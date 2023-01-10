import numpy as np
from pydantic.tools import parse_obj_as, schema_json_of

from docarray.document.io.json import orjson_dumps_and_decode
from docarray.typing import AnyEmbedding


def test_proto_embedding():

    embedding = parse_obj_as(AnyEmbedding, np.zeros((3, 224, 224)))

    embedding._to_node_protobuf()


def test_json_schema():
    schema_json_of(AnyEmbedding)


def test_dump_json():
    tensor = parse_obj_as(AnyEmbedding, np.zeros((3, 224, 224)))
    orjson_dumps_and_decode(tensor)
