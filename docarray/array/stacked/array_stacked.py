from contextlib import contextmanager
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    List,
    Sequence,
    Type,
    TypeVar,
    Union,
    overload,
)

from docarray.array.abstract_array import AnyDocumentArray
from docarray.array.array.array import DocumentArray
from docarray.array.stacked.storage import Storage, StorageView
from docarray.base_document import AnyDocument, BaseDocument
from docarray.typing import NdArray
from docarray.typing.tensor.abstract_tensor import AbstractTensor
from docarray.utils.misc import is_tf_available, is_torch_available

if TYPE_CHECKING:
    from pydantic import BaseConfig
    from pydantic.fields import ModelField

    from docarray.proto import DocumentArrayStackedProto

torch_available = is_torch_available()
if torch_available:
    from docarray.typing import TorchTensor
else:
    TorchTensor = None  # type: ignore

tf_available = is_tf_available()
if tf_available:
    from docarray.typing import TensorFlowTensor  # noqa: F401
else:
    TensorFlowTensor = None  # type: ignore

T_doc = TypeVar('T_doc', bound=BaseDocument)
T = TypeVar('T', bound='DocumentArrayStacked')
IndexIterType = Union[slice, Iterable[int], Iterable[bool], None]


class DocumentArrayStacked(AnyDocumentArray[T_doc]):
    """
    DocumentArrayStacked is a container of Documents appropriates to perform
    computation that require batches of data (ex: matrix multiplication, distance
    calculation, deep learning forward pass)

    A DocumentArrayStacked is similar to {class}`~docarray.array.DocumentArray`
    but the field of the Document that are {class}`~docarray.typing.AnyTensor` are
    stacked into a batches of AnyTensor. Like {class}`~docarray.array.DocumentArray`
    you can be precise a Document schema by using the `DocumentArray[MyDocument]`
    syntax where MyDocument is a Document class (i.e. schema).
    This creates a DocumentArray that can only contains Documents of
    the type 'MyDocument'.

    :param docs: a DocumentArray
    :param tensor_type: Class used to wrap the stacked tensors

    """

    document_type: Type[BaseDocument] = AnyDocument
    _storage: Storage

    def __init__(
        self: T,
        docs: Sequence[T_doc],
        tensor_type: Type['AbstractTensor'] = NdArray,
    ):
        self.tensor_type = tensor_type
        self._storage = Storage(
            docs, document_type=self.document_type, tensor_type=self.tensor_type
        )

    def to(self: T, device: str) -> T:
        """Move all tensors of this DocumentArrayStacked to the given device

        :param device: the device to move the data to
        """
        raise NotImplementedError

    def _get_array_attribute(
        self: T,
        field: str,
    ) -> Union[List, 'DocumentArrayStacked', AbstractTensor]:
        """Return all values of the fields from all docs this array contains

        :param field: name of the fields to extract
        :return: Returns a list of the field value for each document
        in the array like container
        """
        raise NotImplementedError

    def _set_array_attribute(
        self: T,
        field: str,
        values: Union[List, T, AbstractTensor],
    ):
        """Set all Documents in this DocumentArray using the passed values

        :param field: name of the fields to extract
        :values: the values to set at the DocumentArray level
        """
        raise NotImplementedError

    @overload
    def __getitem__(self: T, item: int) -> T_doc:
        ...

    @overload
    def __getitem__(self: T, item: IndexIterType) -> T:
        ...

    def __getitem__(self, item):
        if item is None:
            return self  # PyTorch behaviour
        # multiple docs case
        # if isinstance(item, (slice, Iterable)):
        #     item_ = cast(Iterable, item)
        #     return self._get_from_data_and_columns(item_)
        # single doc case
        doc = self.document_type.from_view(StorageView(item, self._storage))
        return doc

    @overload
    def __setitem__(self: T, key: int, value: T_doc):
        ...

    @overload
    def __setitem__(self: T, key: IndexIterType, value: T):
        ...

    def __setitem__(self: T, key: Union[int, IndexIterType], value: Union[T, T_doc]):
        # multiple docs case
        raise NotImplementedError

    @overload
    def __delitem__(self: T, key: int) -> None:
        ...

    @overload
    def __delitem__(self: T, key: IndexIterType) -> None:
        ...

    def __delitem__(self, key) -> None:
        raise NotImplementedError(
            f'{self.__class__.__name__} does not implement '
            f'__del_item__. You are trying to delete an element'
            f'from {self.__class__.__name__} which is not '
            f'designed for this operation. Please `unstack`'
            f' before doing the deletion'
        )

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        return len(self._storage)

    @classmethod
    def from_protobuf(cls: Type[T], pb_msg: 'DocumentArrayStackedProto') -> T:
        """create a Document from a protobuf message"""

        raise NotImplementedError

    def to_protobuf(self) -> 'DocumentArrayStackedProto':
        """Convert DocumentArray into a Protobuf message"""
        raise NotImplementedError

    def unstack(self: T) -> DocumentArray:
        """Convert DocumentArrayStacked into a DocumentArray.

        Note this destroys the arguments and returns a new DocumentArray
        """
        raise NotImplementedError

    @contextmanager
    def unstacked_mode(self):
        """
        Context manager to put the DocumentArrayStacked in unstacked mode and stack it
        when exiting the context manager.
        EXAMPLE USAGE
        .. code-block:: python
            with da.unstacked_mode():
                ...
        """
        raise NotImplementedError

    @classmethod
    def validate(
        cls: Type[T],
        value: Union[T, Iterable[T_doc]],
        field: 'ModelField',
        config: 'BaseConfig',
    ) -> T:
        if isinstance(value, cls):
            return value
        elif isinstance(value, Iterable):
            return cls(DocumentArray(value))
        else:
            raise TypeError(f'Expecting an Iterable of {cls.document_type}')

    def traverse_flat(
        self: 'AnyDocumentArray',
        access_path: str,
    ) -> Union[List[Any], 'TorchTensor', 'NdArray']:
        raise NotImplementedError
