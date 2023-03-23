import logging
from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    Generator,
    Generic,
    List,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import numpy as np
import weaviate

import docarray
from docarray import BaseDocument, DocumentArray
from docarray.doc_index.abstract_doc_index import BaseDocumentIndex, _FindResultBatched
from docarray.utils.find import _FindResult

TSchema = TypeVar('TSchema', bound=BaseDocument)
T = TypeVar('T', bound='WeaviateDocumentIndex')


DEFAULT_BATCH_CONFIG = {
    "batch_size": 20,
    "dynamic": False,
    "timeout_retries": 3,
    "num_workers": 1,
}

# TODO: add more types and figure out how to handle text vs string type
# see https://weaviate.io/developers/weaviate/configuration/datatypes
WEAVIATE_PY_VEC_TYPES = [list, np.ndarray]
WEAVIATE_PY_TYPES = [bool, int, float, str, docarray.typing.ID]

# "id" and "_id" are reserved names in weaviate so we need to use a different
# name for the id column in a BaseDocument
DOCUMENTID = "docarrayid"


class WeaviateDocumentIndex(BaseDocumentIndex, Generic[TSchema]):
    def __init__(self, db_config=None, **kwargs) -> None:
        self.embedding_column = None
        self.properties = None
        super().__init__(db_config=db_config, **kwargs)
        self._db_config = cast(WeaviateDocumentIndex.DBConfig, self._db_config)
        self._client = weaviate.Client(self._db_config.host)
        self._configure_client()
        self._validate_columns()
        self._set_embedding_column()
        self._set_properties()
        self._create_schema()

    def _set_properties(self) -> None:
        field_overwrites = {"id": DOCUMENTID}

        self.properties = [
            field_overwrites.get(k, k)
            for k, v in self._column_infos.items()
            if v.config.get('is_embedding', False) is False
        ]

    def _validate_columns(self) -> None:
        # must have at most one column with property is_embedding=True
        # and that column must be of type WEAVIATE_PY_VEC_TYPES
        # TODO: update when https://github.com/weaviate/weaviate/issues/2424
        # is implemented
        num_embedding_columns = 0

        for column_name, column_info in self._column_infos.items():
            if column_info.config.get('is_embedding', False):
                num_embedding_columns += 1
                if column_info.db_type not in WEAVIATE_PY_VEC_TYPES:
                    raise ValueError(
                        f'Column {column_name} is marked as embedding but is not of type {WEAVIATE_PY_VEC_TYPES}'
                    )

        if num_embedding_columns > 1:
            raise ValueError(
                f'Only one column can be marked as embedding but found {num_embedding_columns} columns marked as embedding'
            )

    def _set_embedding_column(self) -> None:
        for column_name, column_info in self._column_infos.items():
            if column_info.config.get('is_embedding', False):
                self.embedding_column = column_name
                break

    def _configure_client(self) -> None:
        self._client.batch.configure(**self._db_config.batch_config)

    def _create_schema(self) -> None:
        schema = {}

        properties = []
        column_infos = self._column_infos

        for column_name, column_info in column_infos.items():
            # in weaviate, we do not create a property for the doc's embeddings
            if column_name == self.embedding_column:
                continue
            prop = {
                "name": column_name
                if column_name != 'id'
                else DOCUMENTID,  # in weaviate, id and _id is a reserved keyword
                "dataType": column_info.config["dataType"],
            }
            properties.append(prop)

        # TODO: What is the best way to specify other config that is part of schema?
        # e.g. invertedIndexConfig, shardingConfig, moduleConfig, vectorIndexConfig
        #       and configure replication
        # we will update base on user feedback
        schema["properties"] = properties
        schema["class"] = self._db_config.index_name

        # TODO: Use exists() instead of contains() when available
        #       see https://github.com/weaviate/weaviate-python-client/issues/232
        if self._client.schema.contains(schema):
            logging.warning(
                f"Found index {self._db_config.index_name} with schema {schema}. Will reuse existing schema."
            )
        else:
            self._client.schema.create_class(schema)

    @dataclass
    class DBConfig(BaseDocumentIndex.DBConfig):
        host: str = 'http://weaviate:8080'
        index_name: str = 'Document'
        batch_config: Dict[str, Any] = field(
            default_factory=lambda: DEFAULT_BATCH_CONFIG
        )

    @dataclass
    class RuntimeConfig(BaseDocumentIndex.RuntimeConfig):
        default_column_config: Dict[Type, Dict[str, Any]] = field(
            default_factory=lambda: {
                np.ndarray: {
                    'dataType': ['number[]'],
                },
                docarray.typing.ID: {'dataType': ['string']},
                bool: {'dataType': ['boolean']},
                int: {'dataType': ['int']},
                float: {'dataType': ['number']},
                str: {'dataType': ['text']},
                # `None` is not a Type, but we allow it here anyway
                None: {},  # type: ignore
            }
        )

    def _del_items(self, doc_ids: Sequence[str]):
        has_matches = True

        operands = [
            {"path": [DOCUMENTID], "operator": "Equal", "valueString": doc_id}
            for doc_id in doc_ids
        ]
        where_filter = {
            "operator": "Or",
            "operands": operands,
        }

        # do a loop because there is a limit to how many objects can be deleted at
        # in a single query
        # see: https://weaviate.io/developers/weaviate/api/rest/batch#maximum-number-of-deletes-per-query
        while has_matches:
            results = self._client.batch.delete_objects(
                class_name=self._db_config.index_name,
                where=where_filter,
            )

            has_matches = results["results"]["matches"]

    def _filter(
        self, filter_query: Any, limit: int
    ) -> Union[DocumentArray, List[Dict]]:
        results = (
            self._client.query.get(self._db_config.index_name, self.properties)
            .with_additional("vector")
            .with_where(filter_query)
            .with_limit(limit)
            .do()
        )

        docs = results["data"]["Get"][self._db_config.index_name]

        return [self._parse_weaviate_result(doc) for doc in docs]

    def _filter_batched(
        self, filter_queries: Any, limit: int
    ) -> Union[List[DocumentArray], List[List[Dict]]]:
        qs = [
            self._client.query.get(self._db_config.index_name, self.properties)
            .with_additional("vector")
            .with_where(filter_query)
            .with_limit(limit)
            .with_alias(f'query_{i}')
            for i, filter_query in enumerate(filter_queries)
        ]

        batched_results = self._client.query.multi_get(qs).do()

        return [
            [self._parse_weaviate_result(doc) for doc in batched_result]
            for batched_result in batched_results["data"]["Get"].values()
        ]

    def _find(
        self,
        query: np.ndarray,
        search_field: str,
        limit: int,
        score_name: Literal["certainty", "distance"] = "certainty",
        score_threshold: Optional[float] = None,
    ) -> _FindResult:
        index_name = self._db_config.index_name
        if search_field:
            logging.warning(
                'Argument search_field is not supported for WeaviateDocumentIndex. Ignoring.'
            )
        near_vector = {
            "vector": query,
        }
        if score_threshold:
            near_vector[score_name] = score_threshold

        results = (
            self._client.query.get(index_name, self.properties)
            .with_near_vector(
                near_vector,
            )
            .with_limit(limit)
            .with_additional([score_name, "vector"])
            .do()
        )

        return self._format_response(results["data"]["Get"][index_name], score_name)

    def _format_response(
        self, results, score_name
    ) -> Tuple[List[DocumentArray], List[float]]:
        """
        Format the response from Weaviate into a Tuple of DocumentArray and scores
        """
        da_class = DocumentArray.__class_getitem__(
            cast(Type[BaseDocument], self._schema)
        )

        documents = []
        scores = []

        for result in results:
            score = result["_additional"][score_name]
            scores.append(score)

            document = self._parse_weaviate_result(result)
            documents.append(self._schema.from_view(document))

        return da_class(documents), scores

    def _find_batched(
        self,
        queries: Sequence[np.ndarray],
        search_field: str,
        limit: int,
        score_name: Literal["certainty", "distance"] = "certainty",
        score_threshold: Optional[float] = None,
    ) -> _FindResultBatched:

        if search_field != '':
            logging.warning(
                'Argument search_field is not supported for WeaviateDocumentIndex. Ignoring.'
            )

        qs = []
        for i, query in enumerate(queries):
            near_vector = {"vector": query}

            if score_threshold:
                near_vector[score_name] = score_threshold

            q = (
                self._client.query.get(self._db_config.index_name, self.properties)
                .with_near_vector(near_vector)
                .with_limit(limit)
                .with_additional([score_name, "vector"])
                .with_alias(f'query_{i}')
            )

            qs.append(q)

        results = self._client.query.multi_get(qs).do()

        docs_and_scores = [
            self._format_response(result, score_name)
            for result in results["data"]["Get"].values()
        ]

        docs, scores = zip(*docs_and_scores)
        return list(docs), list(scores)

    def _get_items(self, doc_ids: Sequence[str]) -> List[Dict]:
        # TODO: warn when doc_ids > QUERY_MAXIMUM_RESULTS after
        #       https://github.com/weaviate/weaviate/issues/2792
        #       is implemented
        operands = [
            {"path": [DOCUMENTID], "operator": "Equal", "valueString": doc_id}
            for doc_id in doc_ids
        ]
        where_filter = {
            "operator": "Or",
            "operands": operands,
        }

        results = (
            self._client.query.get(self._db_config.index_name, self.properties)
            .with_where(where_filter)
            .with_additional("vector")
            .do()
        )

        docs = [
            self._parse_weaviate_result(doc)
            for doc in results["data"]["Get"][self._db_config.index_name]
        ]

        return docs

    def _rewrite_documentid(self, document: Dict):
        doc = document.copy()

        # rewrite the id to DOCUMENTID
        document_id = doc.pop('id')
        doc[DOCUMENTID] = document_id

        return doc

    def _parse_weaviate_result(self, result: Dict) -> Dict:
        """
        Parse the result from weaviate to a format that is compatible with the schema
        that was used to initialize weaviate with.
        """
        # rewrite the DOCUMENTID to id
        result = result.copy()
        result['id'] = result.pop(DOCUMENTID)

        # take the vector from the _additional field
        additional_fields = result.pop('_additional')
        result[self.embedding_column] = additional_fields['vector']

        return result

    def _index(self, column_to_data: Dict[str, Generator[Any, None, None]]):
        docs = self._transpose_col_value_dict(column_to_data)
        index_name = self._db_config.index_name

        with self._client.batch as batch:
            for doc in docs:
                parsed_doc = self._rewrite_documentid(doc)
                vector = parsed_doc.pop(self.embedding_column)

                batch.add_data_object(
                    uuid=weaviate.util.generate_uuid5(parsed_doc, index_name),
                    data_object=parsed_doc,
                    class_name=index_name,
                    vector=vector,
                )

    def _text_search(self, query: str, search_field: str, limit: int) -> _FindResult:
        index_name = self._db_config.index_name
        bm25 = {"query": query, "properties": [search_field]}

        results = (
            self._client.query.get(index_name, self.properties)
            .with_bm25(bm25)
            .with_limit(limit)
            .with_additional(["score", "vector"])
            .do()
        )

        return self._format_response(results["data"]["Get"][index_name], "score")

    def _text_search_batched(
        self, queries: Sequence[str], search_field: str, limit: int
    ) -> _FindResultBatched:
        qs = []
        for i, query in enumerate(queries):
            bm25 = {"query": query, "properties": [search_field]}

            q = (
                self._client.query.get(self._db_config.index_name, self.properties)
                .with_bm25(bm25)
                .with_limit(limit)
                .with_additional(["score", "vector"])
                .with_alias(f'query_{i}')
            )

            qs.append(q)

        results = self._client.query.multi_get(qs).do()

        docs_and_scores = [
            self._format_response(result, "score")
            for result in results["data"]["Get"].values()
        ]

        docs, scores = zip(*docs_and_scores)
        return list(docs), list(scores)

    def execute_query(self, query: Any, *args, **kwargs) -> Any:
        return super().execute_query(query, *args, **kwargs)

    def num_docs(self) -> int:
        index_name = self._db_config.index_name
        result = self._client.query.aggregate(index_name).with_meta_count().do()
        # TODO: decorator to check for errors
        total_docs = result["data"]["Aggregate"][index_name][0]["meta"]["count"]

        return total_docs

    def python_type_to_db_type(self, python_type: Type) -> Any:
        """Map python type to database type."""
        for allowed_type in WEAVIATE_PY_VEC_TYPES:
            if issubclass(python_type, allowed_type):
                return np.ndarray

        if python_type in WEAVIATE_PY_TYPES:
            return python_type

        raise ValueError(f'Unsupported column type for {type(self)}: {python_type}')

    def build_query(self) -> BaseDocumentIndex.QueryBuilder:
        return self.QueryBuilder(self)

    class QueryBuilder(BaseDocumentIndex.QueryBuilder):
        def __init__(self, document_index):
            self._query = document_index._client.query.get(
                document_index._db_config.index_name, document_index.properties
            )

        def build(self) -> Any:
            return self._query.do()

        def _overwrite_id(self, where_filter):
            """
            Overwrite the id field in the where filter to DOCUMENTID
            if the "id" field is present in the path
            """
            for key, value in where_filter.items():
                if key == "path" and value == ["id"]:
                    where_filter[key] = [DOCUMENTID]
                elif isinstance(value, dict):
                    self._overwrite_id(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._overwrite_id(item)

        def find(
            self,
            query,
            score_name: Literal["certainty", "distance"] = "certainty",
            score_threshold: Optional[float] = None,
        ) -> Any:
            near_vector = {
                "vector": query,
            }
            if score_threshold:
                near_vector[score_name] = score_threshold

            self._query = self._query.with_near_vector(near_vector)
            return self

        def find_batched(self, *args, **kwargs) -> Any:
            pass

        def filter(self, where_filter) -> Any:
            where_filter = where_filter.copy()
            self._overwrite_id(where_filter)
            self._query = self._query.with_where(where_filter)
            return self

        def filter_batched(self, *args, **kwargs) -> Any:
            pass

        def text_search(self, *args, **kwargs) -> Any:
            pass

        def text_search_batched(self, *args, **kwargs) -> Any:
            pass

        # the methods below need to be implemented by subclasses
        # If, in your subclass, one of these is not usable in a query builder, but
        # can be called directly on the DocumentIndex, use `_raise_not_composable`.
        # If the method is not supported _at all_, use `_raise_not_supported`.
        # find = abstractmethod(lambda *args, **kwargs: ...)
        # filter = abstractmethod(lambda *args, **kwargs: ...)
        # text_search = abstractmethod(lambda *args, **kwargs: ...)
        # find_batched = abstractmethod(lambda *args, **kwargs: ...)
        # filter_batched = abstractmethod(lambda *args, **kwargs: ...)
        # text_search_batched = abstractmethod(lambda *args, **kwargs: ...)
