from typing import Dict, Optional, Union

import pytest

from docarray.typing import NdArray, TorchTensor
from docarray.typing.tensor.abstract_tensor import AbstractTensor
from docarray.utils._typing import is_tensor_union, is_type_tensor


@pytest.mark.parametrize(
    'type_, is_tensor',
    [
        (int, False),
        (TorchTensor, True),
        (NdArray, True),
        (AbstractTensor, True),
        (Optional[TorchTensor], False),
        (Union[TorchTensor, NdArray], False),
        (None, False),
        (Dict, False),
    ],
)
def test_is_type_tensor(type_, is_tensor):
    assert is_type_tensor(type_) == is_tensor


@pytest.mark.parametrize(
    'type_, is_union_tensor',
    [
        (int, False),
        (TorchTensor, False),
        (Optional[TorchTensor], True),
        (Optional[NdArray], True),
        (Union[NdArray, TorchTensor], True),
        (Union[NdArray, TorchTensor, AbstractTensor], True),
        (Union[NdArray, TorchTensor, Optional[TorchTensor]], True),
        (Union[NdArray, TorchTensor, None], True),
    ],
)
def test_is_union_type_tensor(type_, is_union_tensor):
    assert is_tensor_union(type_) == is_union_tensor
