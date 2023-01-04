from typing import Optional, TypeVar

from docarray.document import BaseDocument
from docarray.typing import AnyTensor, Embedding
from docarray.typing.tensor.video.video_tensor import VideoTensor
from docarray.typing.url.video_url import VideoUrl

T = TypeVar('T', bound='Video')


class Video(BaseDocument):
    """
    Document for handling video.
    The Video Document can contain a VideoUrl (`Video.url`), a VideoTensor
    (`Video.tensor`), an AnyTensor ('Video.key_frame_indices), and an Embedding
    (`Video.embedding`).

    EXAMPLE USAGE:

    You can use this Document directly:

    You can extend this Document:

    You can use this Document for composition:

    """

    url: Optional[VideoUrl]
    tensor: Optional[VideoTensor]
    key_frame_indices: Optional[AnyTensor]
    embedding: Optional[Embedding]
