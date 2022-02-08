from typing import Iterator, Union, Iterable, Sequence, MutableSequence

import numpy as np

from ...memory import DocumentArrayInMemory
from .... import Document


class SequenceLikeMixin(MutableSequence[Document]):
    """Implement sequence-like methods"""

    def insert(self, index: int, value: 'Document'):
        """Insert `doc` at `index`.

        :param index: Position of the insertion.
        :param value: The doc needs to be inserted.
        """
        if value.embedding is None:
            value.embedding = np.zeros(self._pqlite.dim, dtype=np.float32)

        self._pqlite.index(DocumentArrayInMemory([value]))
        self._offset2ids.insert_at_offset(index, value.id)

    def append(self, value: 'Document') -> None:
        if value.embedding is None:
            value.embedding = np.zeros((self._pqlite.dim,), dtype=np.float32)
        self._pqlite.index(DocumentArrayInMemory([value]))
        self._offset2ids.extend_doc_ids([value.id])

    def extend(self, values: Iterable['Document']) -> None:
        docs = DocumentArrayInMemory(values)
        for doc in docs:
            if doc.embedding is None:
                doc.embedding = np.zeros(self._pqlite.dim, dtype=np.float32)
        self._pqlite.index(docs)
        self._offset2ids.extend_doc_ids([doc.id for doc in docs])

    def clear(self):
        """Clear the data of :class:`DocumentArray`"""
        self._offset2ids.clear()
        self._pqlite.clear()

    def __del__(self) -> None:
        if not self._persist:
            self._offset2ids.clear()
            self._pqlite.clear()

    def __eq__(self, other):
        """In pqlite backend, data are considered as identical if configs point to the same database source"""
        return (
            type(self) is type(other)
            and type(self._config) is type(other._config)
            and self._config == other._config
        )

    def __len__(self):
        return self._offset2ids.size

    def __iter__(self) -> Iterator['Document']:
        for i in range(len(self)):
            yield self[i]

    def __contains__(self, x: Union[str, 'Document']):
        if isinstance(x, str):
            return self._offset2ids.get_offset_by_id(x) is not None
        elif isinstance(x, Document):
            return self._offset2ids.get_offset_by_id(x.id) is not None
        else:
            return False

    def __bool__(self):
        """To simulate ```l = []; if l: ...```

        :return: returns true if the length of the array is larger than 0
        """
        return len(self) > 0

    def __repr__(self):
        return f'<DocumentArray[PQLite] (length={len(self)}) at {id(self)}>'

    def __add__(self, other: Union['Document', Sequence['Document']]):
        v = type(self)(self)
        v.extend(other)
        return v
