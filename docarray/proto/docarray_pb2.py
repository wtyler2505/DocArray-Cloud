# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: docarray.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0e\x64ocarray.proto\x12\x08\x64ocarray\x1a\x1cgoogle/protobuf/struct.proto\"A\n\x11\x44\x65nseNdArrayProto\x12\x0e\n\x06\x62uffer\x18\x01 \x01(\x0c\x12\r\n\x05shape\x18\x02 \x03(\r\x12\r\n\x05\x64type\x18\x03 \x01(\t\"\xb6\x01\n\x0cNdArrayProto\x12,\n\x05\x64\x65nse\x18\x01 \x01(\x0b\x32\x1b.docarray.DenseNdArrayProtoH\x00\x12.\n\x06sparse\x18\x02 \x01(\x0b\x32\x1c.docarray.SparseNdArrayProtoH\x00\x12\x10\n\x08\x63ls_name\x18\x03 \x01(\t\x12+\n\nparameters\x18\x04 \x01(\x0b\x32\x17.google.protobuf.StructB\t\n\x07\x63ontent\"~\n\x12SparseNdArrayProto\x12,\n\x07indices\x18\x01 \x01(\x0b\x32\x1b.docarray.DenseNdArrayProto\x12+\n\x06values\x18\x02 \x01(\x0b\x32\x1b.docarray.DenseNdArrayProto\x12\r\n\x05shape\x18\x03 \x03(\r\"V\n\x0fNamedScoreProto\x12\r\n\x05value\x18\x01 \x01(\x02\x12\x0f\n\x07op_name\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\x12\x0e\n\x06ref_id\x18\x04 \x01(\t\"\xed\x05\n\rDocumentProto\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0e\n\x04\x62lob\x18\x02 \x01(\x0cH\x00\x12(\n\x06tensor\x18\x03 \x01(\x0b\x32\x16.docarray.NdArrayProtoH\x00\x12\x0e\n\x04text\x18\x04 \x01(\tH\x00\x12\x13\n\x0bgranularity\x18\x05 \x01(\r\x12\x11\n\tadjacency\x18\x06 \x01(\r\x12\x11\n\tparent_id\x18\x07 \x01(\t\x12\x0e\n\x06weight\x18\x08 \x01(\x02\x12\x0b\n\x03uri\x18\t \x01(\t\x12\x10\n\x08modality\x18\n \x01(\t\x12\x11\n\tmime_type\x18\x0b \x01(\t\x12\x0e\n\x06offset\x18\x0c \x01(\x02\x12\x10\n\x08location\x18\r \x03(\x02\x12\'\n\x06\x63hunks\x18\x0e \x03(\x0b\x32\x17.docarray.DocumentProto\x12(\n\x07matches\x18\x0f \x03(\x0b\x32\x17.docarray.DocumentProto\x12)\n\tembedding\x18\x10 \x01(\x0b\x32\x16.docarray.NdArrayProto\x12%\n\x04tags\x18\x11 \x01(\x0b\x32\x17.google.protobuf.Struct\x12\x33\n\x06scores\x18\x12 \x03(\x0b\x32#.docarray.DocumentProto.ScoresEntry\x12=\n\x0b\x65valuations\x18\x13 \x03(\x0b\x32(.docarray.DocumentProto.EvaluationsEntry\x12*\n\t_metadata\x18\x14 \x01(\x0b\x32\x17.google.protobuf.Struct\x1aH\n\x0bScoresEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12(\n\x05value\x18\x02 \x01(\x0b\x32\x19.docarray.NamedScoreProto:\x02\x38\x01\x1aM\n\x10\x45valuationsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12(\n\x05value\x18\x02 \x01(\x0b\x32\x19.docarray.NamedScoreProto:\x02\x38\x01\x42\t\n\x07\x63ontent\";\n\x12\x44ocumentArrayProto\x12%\n\x04\x64ocs\x18\x01 \x03(\x0b\x32\x17.docarray.DocumentProtob\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'docarray_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _DOCUMENTPROTO_SCORESENTRY._options = None
  _DOCUMENTPROTO_SCORESENTRY._serialized_options = b'8\001'
  _DOCUMENTPROTO_EVALUATIONSENTRY._options = None
  _DOCUMENTPROTO_EVALUATIONSENTRY._serialized_options = b'8\001'
  _DENSENDARRAYPROTO._serialized_start=58
  _DENSENDARRAYPROTO._serialized_end=123
  _NDARRAYPROTO._serialized_start=126
  _NDARRAYPROTO._serialized_end=308
  _SPARSENDARRAYPROTO._serialized_start=310
  _SPARSENDARRAYPROTO._serialized_end=436
  _NAMEDSCOREPROTO._serialized_start=438
  _NAMEDSCOREPROTO._serialized_end=524
  _DOCUMENTPROTO._serialized_start=527
  _DOCUMENTPROTO._serialized_end=1276
  _DOCUMENTPROTO_SCORESENTRY._serialized_start=1114
  _DOCUMENTPROTO_SCORESENTRY._serialized_end=1186
  _DOCUMENTPROTO_EVALUATIONSENTRY._serialized_start=1188
  _DOCUMENTPROTO_EVALUATIONSENTRY._serialized_end=1265
  _DOCUMENTARRAYPROTO._serialized_start=1278
  _DOCUMENTARRAYPROTO._serialized_end=1337
# @@protoc_insertion_point(module_scope)
