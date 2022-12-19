from typing import Optional

import pytest
import torch

from docarray import Document, DocumentArray, Text
from docarray.typing import TorchTensor

num_docs = 5
num_sub_docs = 2
num_sub_sub_docs = 3


@pytest.fixture
def multi_model_docs():
    class SubSubDoc(Document):
        sub_sub_text: Text
        sub_sub_tensor: TorchTensor[2]

    class SubDoc(Document):
        sub_text: Text
        sub_da: DocumentArray[SubSubDoc]

    class MultiModalDoc(Document):
        mm_text: Text
        mm_tensor: Optional[TorchTensor[3, 2, 2]]
        mm_da: DocumentArray[SubDoc]

    docs = DocumentArray[MultiModalDoc](
        [
            MultiModalDoc(
                mm_text=Text(text=f'hello{i}'),
                mm_da=[
                    SubDoc(
                        sub_text=Text(text=f'sub_{i}_1'),
                        sub_da=DocumentArray[SubSubDoc](
                            [
                                SubSubDoc(
                                    sub_sub_text=Text(text='subsub'),
                                    sub_sub_tensor=torch.zeros(2),
                                )
                                for _ in range(num_sub_sub_docs)
                            ]
                        ),
                    )
                    for _ in range(num_sub_docs)
                ],
            )
            for i in range(num_docs)
        ]
    )

    return docs


@pytest.mark.parametrize(
    'filter_fn',
    [(lambda d: True), None],
)
@pytest.mark.parametrize(
    'traversal_path,len_result',
    [
        ('mm_text', num_docs),  # List of 5 Text
        ('mm_text.text', num_docs),  # List of 5 strings
        ('mm_da', num_docs * num_sub_docs),  # List of 5 * 2 SubDocs
        ('mm_da.sub_text', num_docs * num_sub_docs),  # List of 5 * 2 Text
        (
            'mm_da.sub_da',
            num_docs * num_sub_docs * num_sub_sub_docs,
        ),  # List of 5 * 2 * 3 SubSubDoc
        (
            'mm_da.sub_da.sub_sub_text',
            num_docs * num_sub_docs * num_sub_sub_docs,
        ),  # List of 5 * 2 * 3 Text
    ],
)
def test_traverse_flat(multi_model_docs, traversal_path, len_result, filter_fn):
    doc_req = multi_model_docs
    ds = list(doc_req.traverse_flat(traversal_path))
    assert len(ds) == len_result
