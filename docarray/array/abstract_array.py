import random
from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    Generic,
    Iterable,
    List,
    MutableSequence,
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

import numpy as np

from docarray.base_doc import BaseDoc
from docarray.display.document_array_summary import DocArraySummary
from docarray.typing.abstract_type import AbstractType
from docarray.utils._internal._typing import change_cls_name

if TYPE_CHECKING:
    from docarray.proto import DocArrayProto, NodeProto
    from docarray.typing.tensor.abstract_tensor import AbstractTensor

T = TypeVar('T', bound='AnyDocArray')
T_doc = TypeVar('T_doc', bound=BaseDoc)
IndexIterType = Union[slice, Iterable[int], Iterable[bool], None]


class AnyDocArray(Sequence[T_doc], Generic[T_doc], AbstractType):
    document_type: Type[BaseDoc]
    __typed_da__: Dict[Type['AnyDocArray'], Dict[Type[BaseDoc], Type]] = {}

    def __repr__(self):
        return f'<{self.__class__.__name__} (length={len(self)})>'

    @classmethod
    def __class_getitem__(cls, item: Union[Type[BaseDoc], TypeVar, str]):
        if not isinstance(item, type):
            return Generic.__class_getitem__.__func__(cls, item)  # type: ignore
            # this do nothing that checking that item is valid type var or str
        if not issubclass(item, BaseDoc):
            raise ValueError(
                f'{cls.__name__}[item] item should be a Document not a {item} '
            )

        if cls not in cls.__typed_da__:
            cls.__typed_da__[cls] = {}

        if item not in cls.__typed_da__[cls]:
            # Promote to global scope so multiprocessing can pickle it
            global _DocArrayTyped

            class _DocArrayTyped(cls):  # type: ignore
                document_type: Type[BaseDoc] = cast(Type[BaseDoc], item)

            for field in _DocArrayTyped.document_type.__fields__.keys():

                def _property_generator(val: str):
                    def _getter(self):
                        return self._get_data_column(val)

                    def _setter(self, value):
                        self._set_data_column(val, value)

                    # need docstring for the property
                    return property(fget=_getter, fset=_setter)

                setattr(_DocArrayTyped, field, _property_generator(field))
                # this generates property on the fly based on the schema of the item

            # The global scope and qualname need to refer to this class a unique name.
            # Otherwise, creating another _DocArrayTyped will overwrite this one.
            change_cls_name(
                _DocArrayTyped, f'{cls.__name__}[{item.__name__}]', globals()
            )

            cls.__typed_da__[cls][item] = _DocArrayTyped

        return cls.__typed_da__[cls][item]

    @overload
    def __getitem__(self: T, item: int) -> T_doc:
        ...

    @overload
    def __getitem__(self: T, item: IndexIterType) -> T:
        ...

    @abstractmethod
    def __getitem__(self, item: Union[int, IndexIterType]) -> Union[T_doc, T]:
        ...

    def __getattr__(self, item: str):
        # Needs to be explicitly defined here for the purpose to disable PyCharm's complaints
        # about not detected properties: https://youtrack.jetbrains.com/issue/PY-47991
        return super().__getattribute__(item)

    @abstractmethod
    def _get_data_column(
        self: T,
        field: str,
    ) -> Union[MutableSequence, T, 'AbstractTensor']:
        """Return all values of the fields from all docs this array contains

        :param field: name of the fields to extract
        :return: Returns a list of the field value for each document
        in the array like container
        """
        ...

    @abstractmethod
    def _set_data_column(
        self: T,
        field: str,
        values: Union[List, T, 'AbstractTensor'],
    ):
        """Set all Documents in this DocArray using the passed values

        :param field: name of the fields to extract
        :values: the values to set at the DocArray level
        """
        ...

    @classmethod
    @abstractmethod
    def from_protobuf(cls: Type[T], pb_msg: 'DocArrayProto') -> T:
        """create a Document from a protobuf message"""
        ...

    @abstractmethod
    def to_protobuf(self) -> 'DocArrayProto':
        """Convert DocArray into a Protobuf message"""
        ...

    def _to_node_protobuf(self) -> 'NodeProto':
        """Convert a DocArray into a NodeProto protobuf message.
         This function should be called when a DocArray
        is nested into another Document that need to be converted into a protobuf

        :return: the nested item protobuf message
        """
        from docarray.proto import NodeProto

        return NodeProto(document_array=self.to_protobuf())

    @abstractmethod
    def traverse_flat(
        self: 'AnyDocArray',
        access_path: str,
    ) -> Union[List[Any], 'AbstractTensor']:
        """
        Return a List of the accessed objects when applying the `access_path`. If this
        results in a nested list or list of DocArrays, the list will be flattened
        on the first level. The access path is a string that consists of attribute
        names, concatenated and "__"-separated. It describes the path from the first
        level to an arbitrary one, e.g. 'content__image__url'.

        :param access_path: a string that represents the access path ("__"-separated).
        :return: list of the accessed objects, flattened if nested.

        EXAMPLE USAGE
        .. code-block:: python
            from docarray import BaseDoc, DocArray, Text


            class Author(BaseDoc):
                name: str


            class Book(BaseDoc):
                author: Author
                content: Text


            da = DocArray[Book](
                Book(author=Author(name='Jenny'), content=Text(text=f'book_{i}'))
                for i in range(10)  # noqa: E501
            )

            books = da.traverse_flat(access_path='content')  # list of 10 Text objs

            authors = da.traverse_flat(access_path='author__name')  # list of 10 strings

        If the resulting list is a nested list, it will be flattened:

        EXAMPLE USAGE
        .. code-block:: python
            from docarray import BaseDoc, DocArray


            class Chapter(BaseDoc):
                content: str


            class Book(BaseDoc):
                chapters: DocArray[Chapter]


            da = DocArray[Book](
                Book(
                    chapters=DocArray[Chapter]([Chapter(content='some_content') for _ in range(3)])
                )
                for _ in range(10)
            )

            chapters = da.traverse_flat(access_path='chapters')  # list of 30 strings

        If your DocArray is in stacked mode, and you want to access a field of
        type AnyTensor, the stacked tensor will be returned instead of a list:

        EXAMPLE USAGE
        .. code-block:: python
            class Image(BaseDoc):
                tensor: TorchTensor[3, 224, 224]


            batch = DocArray[Image](
                [
                    Image(
                        tensor=torch.zeros(3, 224, 224),
                    )
                    for _ in range(2)
                ]
            )

            batch_stacked = batch.stack()
            tensors = batch_stacked.traverse_flat(
                access_path='tensor'
            )  # tensor of shape (2, 3, 224, 224)

        """
        ...

    @staticmethod
    def _traverse(node: Any, access_path: str):
        if access_path:
            curr_attr, _, path_attrs = access_path.partition('__')

            from docarray.array import DocArray

            if isinstance(node, (DocArray, list)):
                for n in node:
                    x = getattr(n, curr_attr)
                    yield from AnyDocArray._traverse(x, path_attrs)
            else:
                x = getattr(node, curr_attr)
                yield from AnyDocArray._traverse(x, path_attrs)
        else:
            yield node

    @staticmethod
    def _flatten_one_level(sequence: List[Any]) -> List[Any]:
        from docarray import DocArray

        if len(sequence) == 0 or not isinstance(sequence[0], (list, DocArray)):
            return sequence
        else:
            return [item for sublist in sequence for item in sublist]

    def summary(self):
        """
        Print a summary of this DocArray object and a summary of the schema of its
        Document type.
        """
        DocArraySummary(self).summary()

    def _batch(
        self: T,
        batch_size: int,
        shuffle: bool = False,
        show_progress: bool = False,
    ) -> Generator[T, None, None]:
        """
        Creates a `Generator` that yields `DocArray` of size `batch_size`.
        Note, that the last batch might be smaller than `batch_size`.

        :param batch_size: Size of each generated batch.
        :param shuffle: If set, shuffle the Documents before dividing into minibatches.
        :param show_progress: if set, show a progress bar when batching documents.
        :yield: a Generator of `DocArray`, each in the length of `batch_size`
        """
        from rich.progress import track

        if not (isinstance(batch_size, int) and batch_size > 0):
            raise ValueError(
                f'`batch_size` should be a positive integer, received: {batch_size}'
            )

        N = len(self)
        indices = list(range(N))
        n_batches = int(np.ceil(N / batch_size))

        if shuffle:
            random.shuffle(indices)

        for i in track(
            range(n_batches),
            description='Batching documents',
            disable=not show_progress,
        ):
            yield self[indices[i * batch_size : (i + 1) * batch_size]]
