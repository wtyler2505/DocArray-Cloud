from typing import Generator, Optional

import pytest

from docarray import BaseDocument, DocumentArray
from docarray.documents import Image
from docarray.typing import ImageUrl, NdArray
from docarray.utils.apply import _map_batch, apply, apply_batch
from tests.units.typing.test_bytes import IMAGE_PATHS

N_DOCS = 2


def load_from_doc(d: Image) -> Image:
    if d.url is not None:
        d.tensor = d.url.load()
    return d


@pytest.fixture()
def da():
    da = DocumentArray[Image]([Image(url=IMAGE_PATHS['png']) for _ in range(N_DOCS)])
    return da


@pytest.mark.parametrize('backend', ['thread', 'process'])
def test_apply(da, backend):
    for tensor in da.tensor:
        assert tensor is None

    apply(da=da, func=load_from_doc, backend=backend)

    assert len(da) == N_DOCS
    for tensor in da.tensor:
        assert tensor is not None


def test_apply_multiprocessing_lambda_func_raise_exception(da):
    with pytest.raises(ValueError, match='Multiprocessing does not allow'):
        apply(da=da, func=lambda x: x, backend='process')


def test_apply_multiprocessing_local_func_raise_exception(da):
    def local_func(x):
        return x

    with pytest.raises(ValueError, match='Multiprocessing does not allow'):
        apply(da=da, func=local_func, backend='process')


@pytest.mark.parametrize('backend', ['thread', 'process'])
def test_check_order(backend):
    da = DocumentArray[Image]([Image(id=i) for i in range(N_DOCS)])

    apply(da=da, func=load_from_doc, backend=backend)

    assert len(da) == N_DOCS
    for i, id_1 in enumerate(da.id):
        assert id_1 == str(i)


def load_from_da(da: DocumentArray) -> DocumentArray:
    for doc in da:
        doc.tensor = doc.url.load()
    return da


class MyImage(BaseDocument):
    tensor: Optional[NdArray]
    url: ImageUrl


@pytest.mark.parametrize('n_docs,batch_size', [(10, 5), (10, 8)])
@pytest.mark.parametrize('backend', ['thread', 'process'])
def test_apply_batch(n_docs, batch_size, backend):

    da = DocumentArray[MyImage](
        [MyImage(url=IMAGE_PATHS['png']) for _ in range(n_docs)]
    )
    apply_batch(da=da, func=load_from_da, batch_size=batch_size, backend=backend)

    assert len(da) == n_docs
    for doc in da:
        assert isinstance(doc, MyImage)
        assert doc.url is not None
        assert doc.tensor is not None


def double_da(da: DocumentArray) -> DocumentArray:
    da.extend([MyImage(url=IMAGE_PATHS['png'])])
    return da


@pytest.mark.parametrize('n_docs,batch_size', [(10, 5), (10, 8)])
@pytest.mark.parametrize('backend', ['thread', 'process'])
def test_apply_batch_func_extends_da(n_docs, batch_size, backend):

    da = DocumentArray[MyImage](
        [MyImage(url=IMAGE_PATHS['png']) for _ in range(n_docs)]
    )
    apply_batch(da=da, func=double_da, batch_size=batch_size, backend=backend)

    assert len(da) == n_docs * 2
    for doc in da:
        assert isinstance(doc, MyImage)


#
# def first_doc(da: DocumentArray) -> BaseDocument:
#     return da[0]
#
#
# @pytest.mark.parametrize('n_docs,batch_size', [(10, 5), (10, 8)])
# @pytest.mark.parametrize('backend', ['thread', 'process'])
# def test_apply_batch_func_return_doc(n_docs, batch_size, backend):
#     da = DocumentArray[MyImage](
#         [MyImage(url=IMAGE_PATHS['png']) for _ in range(n_docs)]
#     )
#     apply_batch(da=da, func=first_doc, batch_size=batch_size, backend=backend)
#
#     assert len(da) == math.ceil(n_docs / batch_size)
#     for doc in da:
#         assert isinstance(doc, MyImage)


@pytest.mark.parametrize('n_docs,batch_size', [(10, 5), (10, 8)])
@pytest.mark.parametrize('backend', ['thread', 'process'])
def test_map_batch(n_docs, batch_size, backend):

    da = DocumentArray[MyImage](
        [MyImage(url=IMAGE_PATHS['png']) for _ in range(n_docs)]
    )
    it = _map_batch(da=da, func=load_from_da, batch_size=batch_size, backend=backend)
    assert isinstance(it, Generator)

    for batch in it:
        assert isinstance(batch, DocumentArray[MyImage])
