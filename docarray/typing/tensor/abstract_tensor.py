import abc
from abc import ABC
from typing import TYPE_CHECKING, Any, Generic, List, Tuple, Type, TypeVar, Union

from docarray.computation import AbstractComputationalBackend
from docarray.typing.abstract_type import AbstractType

if TYPE_CHECKING:
    from pydantic import BaseConfig
    from pydantic.fields import ModelField

    from docarray.proto import NdArrayProto, NodeProto

T = TypeVar('T', bound='AbstractTensor')
ShapeT = TypeVar('ShapeT')


class _ParametrizedMeta(type):
    """
    This metaclass ensures that instance and subclass checks on parametrized Tensors
    are handled as expected:

    assert issubclass(TorchTensor[128], TorchTensor[128])
    t = parse_obj_as(TorchTensor[128], torch.zeros(128))
    assert isinstance(t, TorchTensor[128])
    etc.

    This special handling is needed because every call to `AbstractTensor.__getitem__`
    creates a new class on the fly.
    We want technically distinct but identical classes to be considered equal.
    """

    def __subclasscheck__(cls, subclass):
        is_tensor = AbstractTensor in subclass.mro()
        same_parents = is_tensor and cls.mro()[1:] == subclass.mro()[1:]

        subclass_target_shape = getattr(subclass, '__docarray_target_shape__', False)
        self_target_shape = getattr(cls, '__docarray_target_shape__', False)
        same_shape = (
            same_parents
            and subclass_target_shape
            and self_target_shape
            and subclass_target_shape == self_target_shape
        )

        if same_shape:
            return True
        return super().__subclasscheck__(subclass)

    def __instancecheck__(cls, instance):
        is_tensor = isinstance(instance, AbstractTensor)
        if is_tensor:  # custom handling
            return any(issubclass(candidate, cls) for candidate in type(instance).mro())
        return super().__instancecheck__(instance)


class AbstractTensor(Generic[ShapeT], AbstractType, ABC):

    __parametrized_meta__: type = _ParametrizedMeta
    _proto_type_name: str
    def _to_node_protobuf(self: T) -> 'NodeProto':
        """Convert itself into a NodeProto protobuf message. This function should
        be called when the Document is nested into another Document that need to be
        converted into a protobuf
        :param field: field in which to store the content in the node proto
        :return: the nested item protobuf message
        """
        from docarray.proto import NodeProto

        nd_proto = self.to_protobuf()
        return NodeProto(ndarray=nd_proto, type=self._proto_type_name)

    @classmethod
    @abc.abstractmethod
    def __docarray_validate_shape__(cls, t: T, shape: Tuple[int]) -> T:
        """Every tensor has to implement this method in order to
        enable syntax of the form AnyTensor[shape].

        It is called when a tensor is assigned to a field of this type.
        i.e. when a tensor is passed to a Document field of type AnyTensor[shape].

        The intended behaviour is as follows:
        - If the shape of `t` is equal to `shape`, return `t`.
        - If the shape of `t` is not equal to `shape`,
            but can be reshaped to `shape`, return `t` reshaped to `shape`.
        - If the shape of `t` is not equal to `shape`
            and cannot be reshaped to `shape`, raise a ValueError.

        :param t: The tensor to validate.
        :param shape: The shape to validate against.
        :return: The validated tensor.
        """
        ...

    @classmethod
    def __docarray_validate_getitem__(cls, item: Any) -> Tuple[int]:
        """This method validates the input to __class_getitem__.

        It is called at "class creation time",
        i.e. when a class is created with syntax of the form AnyTensor[shape].

        The default implementation tries to cast any `item` to a tuple of ints.
        A subclass can override this method to implement custom validation logic.

        The output of this is eventually passed to
        {ref}`AbstractTensor.__validate_shape__` as its `shape` argument.

        Raises `ValueError` if the input `item` does not pass validation.

        :param item: The item to validate, passed to __class_getitem__ (`Tensor[item]`).
        :return: The validated item == the target shape of this tensor.
        """
        if isinstance(item, int):
            item = (item,)
        try:
            item = tuple(item)
        except TypeError:
            raise TypeError(f'{item} is not a valid tensor shape.')
        return item

    @classmethod
    def _docarray_create_parametrized_type(cls: Type[T], shape: Tuple[int]):
        shape_str = ', '.join([str(s) for s in shape])

        class _ParametrizedTensor(
            cls,  # type: ignore
            metaclass=cls.__parametrized_meta__,  # type: ignore
        ):
            __docarray_target_shape__ = shape

            @classmethod
            def validate(
                _cls,
                value: Any,
                field: 'ModelField',
                config: 'BaseConfig',
            ):
                t = super().validate(value, field, config)
                return _cls.__docarray_validate_shape__(
                    t, _cls.__docarray_target_shape__
                )

        _ParametrizedTensor.__name__ = f'{cls.__name__}[{shape_str}]'
        _ParametrizedTensor.__qualname__ = f'{cls.__qualname__}[{shape_str}]'

        return _ParametrizedTensor

    def __class_getitem__(cls, item: Any):
        target_shape = cls.__docarray_validate_getitem__(item)
        return cls._docarray_create_parametrized_type(target_shape)

    @classmethod
    def _docarray_stack(cls: Type[T], seq: Union[List[T], Tuple[T]]) -> T:
        """Stack a sequence of tensors into a single tensor."""
        comp_backend = cls.get_comp_backend()
        # at runtime, 'T' is always the correct input type for .stack()
        # but mypy doesn't know that, so we ignore it here
        return cls._docarray_from_native(comp_backend.stack(seq))  # type: ignore

    @classmethod
    @abc.abstractmethod
    def _docarray_from_native(cls: Type[T], value: Any) -> T:
        """
        Create a DocArray tensor from a tensor that is native to the given framework,
        e.g. from numpy.ndarray or torch.Tensor.
        """
        ...

    @staticmethod
    @abc.abstractmethod
    def get_comp_backend() -> Type[AbstractComputationalBackend]:
        """The computational backend compatible with this tensor type."""
        ...

    def __getitem__(self, item):
        """Get a slice of this tensor."""
        ...

    def __setitem__(self, index, value):
        """Set a slice of this tensor."""
        ...

    def __iter__(self):
        """Iterate over the elements of this tensor."""
        ...

    @abc.abstractmethod
    def to_protobuf(self) -> 'NdArrayProto':
        """Convert DocumentArray into a Protobuf message"""
        ...

    def unwrap(self):
        """Return the native tensor object that this DocArray tensor wraps."""

    @abc.abstractmethod
    def _docarray_to_json_compatible(self):
        """
        Convert tensor into a json compatible object
        :return: a representation of the tensor compatible with orjson
        """
        ...
