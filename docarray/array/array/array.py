import io
from functools import wraps
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    List,
    MutableSequence,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    overload,
)

from typing_inspect import is_union_type

from docarray.array.abstract_array import AnyDocumentArray
from docarray.array.array.io import IOMixinArray
from docarray.array.array.sequence_indexing_mixin import (
    IndexingSequenceMixin,
    IndexIterType,
)
from docarray.base_document import AnyDocument, BaseDocument
from docarray.typing import NdArray
from pydantic import BaseModel

if TYPE_CHECKING:
    from pydantic import BaseConfig
    from pydantic.fields import ModelField

    from docarray.array.stacked.array_stacked import DocumentArrayStacked
    from docarray.proto import DocumentArrayProto
    from docarray.typing import TorchTensor
    from docarray.typing.tensor.abstract_tensor import AbstractTensor

T = TypeVar('T', bound='DocumentArray')
T_doc = TypeVar('T_doc', bound=BaseDocument)


def _delegate_meth_to_data(meth_name: str) -> Callable:
    """
    create a function that mimic a function call to the data attribute of the
    DocumentArray

    :param meth_name: name of the method
    :return: a method that mimic the meth_name
    """
    func = getattr(list, meth_name)

    @wraps(func)
    def _delegate_meth(self, *args, **kwargs):
        return getattr(self._data, meth_name)(*args, **kwargs)

    return _delegate_meth


class DocumentArray(
    BaseModel, IndexingSequenceMixin[T_doc], IOMixinArray, AnyDocumentArray[T_doc]
):
    """
     DocumentArray is a container of Documents.

    A DocumentArray is a list of Documents of any schema. However, many
    DocumentArray features are only available if these Documents are
    homogeneous and follow the same schema. To precise this schema you can use
    the `DocumentArray[MyDocument]` syntax where MyDocument is a Document class
    (i.e. schema). This creates a DocumentArray that can only contains Documents of
    the type 'MyDocument'.

    ---

    ```python
    from docarray import BaseDocument, DocumentArray
    from docarray.typing import NdArray, ImageUrl
    from typing import Optional


    class Image(BaseDocument):
        tensor: Optional[NdArray[100]]
        url: ImageUrl


    da = DocumentArray[Image](
        Image(url='http://url.com/foo.png') for _ in range(10)
    )  # noqa: E510
    ```

    ---


    If your DocumentArray is homogeneous (i.e. follows the same schema), you can access
    fields at the DocumentArray level (for example `da.tensor` or `da.url`).
    You can also set fields, with `da.tensor = np.random.random([10, 100])`:

        print(da.url)
        # [ImageUrl('http://url.com/foo.png', host_type='domain'), ...]
        import numpy as np

        da.tensor = np.random.random([10, 100])
        print(da.tensor)
        # [NdArray([0.11299577, 0.47206767, 0.481723  , 0.34754724, 0.15016037,
        #          0.88861321, 0.88317666, 0.93845579, 0.60486676, ... ]), ...]

    You can index into a DocumentArray like a numpy array or torch tensor:


        da[0]  # index by position
        da[0:5:2]  # index by slice
        da[[0, 2, 3]]  # index by list of indices
        da[True, False, True, True, ...]  # index by boolean mask

    You can delete items from a DocumentArray like a Python List

        del da[0]  # remove first element from DocumentArray
        del da[0:5]  # remove elements for 0 to 5 from DocumentArray

    :param docs: iterable of Document

    """

    document_type: Type[BaseDocument] = AnyDocument
    data: List[T_doc]
    __fields_set__ = set(['document_type', 'data'])

    def __init__(
        self,
        docs: Optional[Iterable[T_doc]] = None,
    ):
        self.data: List[T_doc] = list(self._validate_docs(docs)) if docs else []

    @classmethod
    def construct(
        cls: Type[T],
        docs: Sequence[T_doc],
    ) -> T:
        """
        Create a DocumentArray without validation any data. The data must come from a
        trusted source
        :param docs: a Sequence (list) of Document with the same schema
        :return:
        """
        da = cls.__new__(cls)
        da.data = docs if isinstance(docs, list) else list(docs)
        return da

    def _validate_docs(self, docs: Iterable[T_doc]) -> Iterable[T_doc]:
        """
        Validate if an Iterable of Document are compatible with this DocumentArray
        """
        for doc in docs:
            yield self._validate_one_doc(doc)

    def _validate_one_doc(self, doc: T_doc) -> T_doc:
        """Validate if a Document is compatible with this DocumentArray"""
        if not issubclass(self.__fields__['document_type'].default, AnyDocument) and not isinstance(
            doc, self.__fields__['document_type'].default
        ):
            raise ValueError(f'{doc} is not a {self.document_type}')
        return doc

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)

    def __bytes__(self) -> bytes:
        with io.BytesIO() as bf:
            self._write_bytes(bf=bf)
            return bf.getvalue()

    def append(self, doc: T_doc):
        """
        Append a Document to the DocumentArray. The Document must be from the same class
        as the document_type of this DocumentArray otherwise it will fail.
        :param doc: A Document
        """
        self.data.append(self._validate_one_doc(doc))

    def extend(self, docs: Iterable[T_doc]):
        """
        Extend a DocumentArray with an Iterable of Document. The Documents must be from
        the same class as the document_type of this DocumentArray otherwise it will
        fail.
        :param docs: Iterable of Documents
        """
        self.data.extend(self._validate_docs(docs))

    def insert(self, i: int, doc: T_doc):
        """
        Insert a Document to the DocumentArray. The Document must be from the same
        class as the document_type of this DocumentArray otherwise it will fail.
        :param i: index to insert
        :param doc: A Document
        """
        self.data.insert(i, self._validate_one_doc(doc))

    pop = _delegate_meth_to_data('pop')
    remove = _delegate_meth_to_data('remove')
    reverse = _delegate_meth_to_data('reverse')
    sort = _delegate_meth_to_data('sort')

    def _get_data_column(
        self: T,
        field: str,
    ) -> Union[MutableSequence, T, 'TorchTensor', 'NdArray']:
        """Return all values of the fields from all docs this array contains

        :param field: name of the fields to extract
        :return: Returns a list of the field value for each document
        in the array like container
        """
        field_type = self.__class__.document_type._get_field_type(field)

        if (
            not is_union_type(field_type)
            and isinstance(field_type, type)
            and issubclass(field_type, BaseDocument)
        ):
            # calling __class_getitem__ ourselves is a hack otherwise mypy complain
            # most likely a bug in mypy though
            # bug reported here https://github.com/python/mypy/issues/14111
            return DocumentArray.__class_getitem__(field_type)(
                (getattr(doc, field) for doc in self),
            )
        else:
            return [getattr(doc, field) for doc in self]

    def _set_data_column(
        self: T,
        field: str,
        values: Union[List, T, 'AbstractTensor'],
    ):
        """Set all Documents in this DocumentArray using the passed values

        :param field: name of the fields to set
        :values: the values to set at the DocumentArray level
        """
        ...

        for doc, value in zip(self, values):
            setattr(doc, field, value)

    def stack(
        self,
        tensor_type: Type['AbstractTensor'] = NdArray,
    ) -> 'DocumentArrayStacked':
        """
        Convert the DocumentArray into a DocumentArrayStacked. `Self` cannot be used
        afterwards
        :param tensor_type: Tensor Class used to wrap the stacked tensors. This is useful
        if the BaseDocument has some undefined tensor type like AnyTensor or Union of NdArray and TorchTensor
        :return: A DocumentArrayStacked of the same document type as self
        """
        from docarray.array.stacked.array_stacked import DocumentArrayStacked

        return DocumentArrayStacked.__class_getitem__(self.document_type)(
            self, tensor_type=tensor_type
        )

    @classmethod
    def validate(
        cls: Type[T],
        value: Union[T, Iterable[BaseDocument]],
        field: 'ModelField',
        config: 'BaseConfig',
    ):
        from docarray.array.stacked.array_stacked import DocumentArrayStacked

        if isinstance(value, (cls, DocumentArrayStacked)):
            return value
        elif isinstance(value, Iterable):
            return cls(value)
        else:
            raise TypeError(f'Expecting an Iterable of {cls.document_type}')

    def traverse_flat(
        self: 'DocumentArray',
        access_path: str,
    ) -> List[Any]:
        nodes = list(AnyDocumentArray._traverse(node=self, access_path=access_path))
        flattened = AnyDocumentArray._flatten_one_level(nodes)

        return flattened

    @classmethod
    def from_protobuf(cls: Type[T], pb_msg: 'DocumentArrayProto') -> T:
        """create a Document from a protobuf message
        :param pb_msg: The protobuf message from where to construct the DocumentArray
        """
        return super().from_protobuf(pb_msg)

    @overload
    def __getitem__(self, item: int) -> T_doc:
        ...

    @overload
    def __getitem__(self: T, item: IndexIterType) -> T:
        ...

    def __getitem__(self, item):
        return super().__getitem__(item)

    def __getattr__(self, item: str):
        return self.__getattribute__(item)
