from typing import Iterable, Type

from docarray.array.abstract_array import AbstractDocumentArray
from docarray.array.mixins import GetAttributeArrayMixin, ProtoArrayMixin
from docarray.document import AnyDocument, BaseDocument, BaseNode
from docarray.document.abstract_document import AbstractDocument


class DocumentArray(
    list,
    ProtoArrayMixin,
    GetAttributeArrayMixin,
    AbstractDocumentArray,
    BaseNode,
):
    """
    a _GenericDocumentArray is a list-like container of Document of the same schema

    :param docs: iterable of Document
    """

    document_type: Type[BaseDocument] = AnyDocument

    def __init__(self, docs: Iterable[AbstractDocument]):
        super().__init__(doc_ for doc_ in docs)

    def __class_getitem__(cls, item: Type[BaseDocument]):
        if not issubclass(item, BaseDocument):
            raise ValueError(
                f'DocumentArray[item] item should be a Document not a {item} '
            )

        class _DocumenArrayTyped(DocumentArray):
            document_type = item

        for field in _DocumenArrayTyped.document_type.__fields__.keys():

            def _proprety_generator(val: str):
                return property(lambda self: self._get_documents_attribute(val))

            setattr(_DocumenArrayTyped, field, _proprety_generator(field))

        _DocumenArrayTyped.__name__ = f'DocumentArray{item.__name__}'

        return _DocumenArrayTyped
