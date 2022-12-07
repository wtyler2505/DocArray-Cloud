from docarray.typing.tensor.embedding.embedding_mixin import EmbeddingMixin
from docarray.typing.tensor.ndarray import NdArray


class NdArrayEmbedding(NdArray, EmbeddingMixin):
    alternative_type = NdArray
