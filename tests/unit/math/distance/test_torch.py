import numpy as np
import pytest
import torch

from docarray.math.distance.torch import cosine, euclidean, sqeuclidean


@pytest.mark.parametrize(
    'x_mat, y_mat, result',
    (
        (
            torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]),
            torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]),
            np.array(
                [[0.00000000e00, 2.53681537e-02], [2.53681537e-02, 2.22044605e-16]]
            ),
        ),
        (
            torch.tensor([[1.0, 2.0, 3.0]]),
            torch.tensor([[1.0, 2.0, 3.0]]),
            np.array([[1]]),
        ),
        (
            torch.tensor([[0.0, 0.0, 0.0]]),
            torch.tensor([[0.0, 0.0, 0.0]]),
            np.array([[1]]),
        ),
        (
            torch.tensor([[1.0, 2.0, 3.0]]),
            torch.tensor([[19.0, 53.0, 201.0]]),
            np.array([[0.06788693]]),
        ),
    ),
)
def test_cosine(x_mat, y_mat, result):
    assert cosine(x_mat, y_mat).all() == result.all()


@pytest.mark.parametrize(
    'x_mat, y_mat, result',
    (
        (
            torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]),
            torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]),
            np.array([[0, 27], [27, 0]]),
        ),
        (
            torch.tensor([[1.0, 2.0, 3.0]]),
            torch.tensor([[1.0, 2.0, 3.0]]),
            np.array([[0]]),
        ),
        (
            torch.tensor([[0.0, 0.0, 0.0]]),
            torch.tensor([[0.0, 0.0, 0.0]]),
            np.array([[0]]),
        ),
        (
            torch.tensor([[1.0, 2.0, 3.0]]),
            torch.tensor([[19.0, 53.0, 201.0]]),
            np.array([[42129]]),
        ),
    ),
)
def test_sqeuclidean(x_mat, y_mat, result):
    assert sqeuclidean(x_mat, y_mat).all() == result.all()


@pytest.mark.parametrize(
    'x_mat, y_mat, result',
    (
        (
            torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]),
            torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]),
            np.array([[0, 5.19615242], [5.19615242, 0]]),
        ),
        (
            torch.tensor([[1.0, 2.0, 3.0]]),
            torch.tensor([[1.0, 2.0, 3.0]]),
            np.array([[0]]),
        ),
        (
            torch.tensor([[0.0, 0.0, 0.0]]),
            torch.tensor([[0.0, 0.0, 0.0]]),
            np.array([[0]]),
        ),
        (
            torch.tensor([[1.0, 2.0, 3.0]]),
            torch.tensor([[19.0, 53.0, 201.0]]),
            np.array([[205.2535018]]),
        ),
    ),
)
def test_euclidean(x_mat, y_mat, result):
    assert euclidean(x_mat, y_mat).all() == result.all()
