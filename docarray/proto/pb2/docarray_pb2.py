# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: docarray.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0e\x64ocarray.proto\x12\x08\x64ocarray\x1a\x1cgoogle/protobuf/struct.proto\"A\n\x11\x44\x65nseNdArrayProto\x12\x0e\n\x06\x62uffer\x18\x01 \x01(\x0c\x12\r\n\x05shape\x18\x02 \x03(\r\x12\r\n\x05\x64type\x18\x03 \x01(\t\"g\n\x0cNdArrayProto\x12*\n\x05\x64\x65nse\x18\x01 \x01(\x0b\x32\x1b.docarray.DenseNdArrayProto\x12+\n\nparameters\x18\x02 \x01(\x0b\x32\x17.google.protobuf.Struct\"Z\n\x0cKeyValuePair\x12#\n\x03key\x18\x01 \x01(\x0b\x32\x16.google.protobuf.Value\x12%\n\x05value\x18\x02 \x01(\x0b\x32\x16.google.protobuf.Value\";\n\x10GenericDictValue\x12\'\n\x07\x65ntries\x18\x01 \x03(\x0b\x32\x16.docarray.KeyValuePair\"3\n\x0eListOfAnyProto\x12!\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x13.docarray.NodeProto\"\xc5\x03\n\tNodeProto\x12\x0e\n\x04text\x18\x01 \x01(\tH\x00\x12\x11\n\x07integer\x18\x02 \x01(\x05H\x00\x12\x0f\n\x05\x66loat\x18\x03 \x01(\x01H\x00\x12\x11\n\x07\x62oolean\x18\x04 \x01(\x08H\x00\x12\x0e\n\x04\x62lob\x18\x05 \x01(\x0cH\x00\x12)\n\x07ndarray\x18\x06 \x01(\x0b\x32\x16.docarray.NdArrayProtoH\x00\x12+\n\x08\x64ocument\x18\x07 \x01(\x0b\x32\x17.docarray.DocumentProtoH\x00\x12\x36\n\x0e\x64ocument_array\x18\x08 \x01(\x0b\x32\x1c.docarray.DocumentArrayProtoH\x00\x12(\n\x04list\x18\t \x01(\x0b\x32\x18.docarray.ListOfAnyProtoH\x00\x12\'\n\x03set\x18\n \x01(\x0b\x32\x18.docarray.ListOfAnyProtoH\x00\x12)\n\x05tuple\x18\x0b \x01(\x0b\x32\x18.docarray.ListOfAnyProtoH\x00\x12\'\n\x04\x64ict\x18\x0c \x01(\x0b\x32\x17.google.protobuf.StructH\x00\x12\x0e\n\x04type\x18\r \x01(\tH\x01\x42\t\n\x07\x63ontentB\x0f\n\rdocarray_type\"\x82\x01\n\rDocumentProto\x12/\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32!.docarray.DocumentProto.DataEntry\x1a@\n\tDataEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\"\n\x05value\x18\x02 \x01(\x0b\x32\x13.docarray.NodeProto:\x02\x38\x01\";\n\x12\x44ocumentArrayProto\x12%\n\x04\x64ocs\x18\x01 \x03(\x0b\x32\x17.docarray.DocumentProto\"F\n\x18ListOfDocumentArrayProto\x12*\n\x04\x64\x61ta\x18\x01 \x03(\x0b\x32\x1c.docarray.DocumentArrayProto\"\x90\x05\n\x19\x44ocumentArrayStackedProto\x12N\n\x0etensor_columns\x18\x01 \x03(\x0b\x32\x36.docarray.DocumentArrayStackedProto.TensorColumnsEntry\x12H\n\x0b\x64oc_columns\x18\x02 \x03(\x0b\x32\x33.docarray.DocumentArrayStackedProto.DocColumnsEntry\x12\x46\n\nda_columns\x18\x03 \x03(\x0b\x32\x32.docarray.DocumentArrayStackedProto.DaColumnsEntry\x12H\n\x0b\x61ny_columns\x18\x04 \x03(\x0b\x32\x33.docarray.DocumentArrayStackedProto.AnyColumnsEntry\x1aL\n\x12TensorColumnsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12%\n\x05value\x18\x02 \x01(\x0b\x32\x16.docarray.NdArrayProto:\x02\x38\x01\x1aV\n\x0f\x44ocColumnsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x32\n\x05value\x18\x02 \x01(\x0b\x32#.docarray.DocumentArrayStackedProto:\x02\x38\x01\x1aT\n\x0e\x44\x61\x43olumnsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x31\n\x05value\x18\x02 \x01(\x0b\x32\".docarray.ListOfDocumentArrayProto:\x02\x38\x01\x1aK\n\x0f\x41nyColumnsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\'\n\x05value\x18\x02 \x01(\x0b\x32\x18.docarray.ListOfAnyProto:\x02\x38\x01\x62\x06proto3'
)


_DENSENDARRAYPROTO = DESCRIPTOR.message_types_by_name['DenseNdArrayProto']
_NDARRAYPROTO = DESCRIPTOR.message_types_by_name['NdArrayProto']
_KEYVALUEPAIR = DESCRIPTOR.message_types_by_name['KeyValuePair']
_GENERICDICTVALUE = DESCRIPTOR.message_types_by_name['GenericDictValue']
_LISTOFANYPROTO = DESCRIPTOR.message_types_by_name['ListOfAnyProto']
_NODEPROTO = DESCRIPTOR.message_types_by_name['NodeProto']
_DOCUMENTPROTO = DESCRIPTOR.message_types_by_name['DocumentProto']
_DOCUMENTPROTO_DATAENTRY = _DOCUMENTPROTO.nested_types_by_name['DataEntry']
_DOCUMENTARRAYPROTO = DESCRIPTOR.message_types_by_name['DocumentArrayProto']
_LISTOFDOCUMENTARRAYPROTO = DESCRIPTOR.message_types_by_name['ListOfDocumentArrayProto']
_DOCUMENTARRAYSTACKEDPROTO = DESCRIPTOR.message_types_by_name[
    'DocumentArrayStackedProto'
]
_DOCUMENTARRAYSTACKEDPROTO_TENSORCOLUMNSENTRY = (
    _DOCUMENTARRAYSTACKEDPROTO.nested_types_by_name['TensorColumnsEntry']
)
_DOCUMENTARRAYSTACKEDPROTO_DOCCOLUMNSENTRY = (
    _DOCUMENTARRAYSTACKEDPROTO.nested_types_by_name['DocColumnsEntry']
)
_DOCUMENTARRAYSTACKEDPROTO_DACOLUMNSENTRY = (
    _DOCUMENTARRAYSTACKEDPROTO.nested_types_by_name['DaColumnsEntry']
)
_DOCUMENTARRAYSTACKEDPROTO_ANYCOLUMNSENTRY = (
    _DOCUMENTARRAYSTACKEDPROTO.nested_types_by_name['AnyColumnsEntry']
)
DenseNdArrayProto = _reflection.GeneratedProtocolMessageType(
    'DenseNdArrayProto',
    (_message.Message,),
    {
        'DESCRIPTOR': _DENSENDARRAYPROTO,
        '__module__': 'docarray_pb2'
        # @@protoc_insertion_point(class_scope:docarray.DenseNdArrayProto)
    },
)
_sym_db.RegisterMessage(DenseNdArrayProto)

NdArrayProto = _reflection.GeneratedProtocolMessageType(
    'NdArrayProto',
    (_message.Message,),
    {
        'DESCRIPTOR': _NDARRAYPROTO,
        '__module__': 'docarray_pb2'
        # @@protoc_insertion_point(class_scope:docarray.NdArrayProto)
    },
)
_sym_db.RegisterMessage(NdArrayProto)

KeyValuePair = _reflection.GeneratedProtocolMessageType(
    'KeyValuePair',
    (_message.Message,),
    {
        'DESCRIPTOR': _KEYVALUEPAIR,
        '__module__': 'docarray_pb2'
        # @@protoc_insertion_point(class_scope:docarray.KeyValuePair)
    },
)
_sym_db.RegisterMessage(KeyValuePair)

GenericDictValue = _reflection.GeneratedProtocolMessageType(
    'GenericDictValue',
    (_message.Message,),
    {
        'DESCRIPTOR': _GENERICDICTVALUE,
        '__module__': 'docarray_pb2'
        # @@protoc_insertion_point(class_scope:docarray.GenericDictValue)
    },
)
_sym_db.RegisterMessage(GenericDictValue)

ListOfAnyProto = _reflection.GeneratedProtocolMessageType(
    'ListOfAnyProto',
    (_message.Message,),
    {
        'DESCRIPTOR': _LISTOFANYPROTO,
        '__module__': 'docarray_pb2'
        # @@protoc_insertion_point(class_scope:docarray.ListOfAnyProto)
    },
)
_sym_db.RegisterMessage(ListOfAnyProto)

NodeProto = _reflection.GeneratedProtocolMessageType(
    'NodeProto',
    (_message.Message,),
    {
        'DESCRIPTOR': _NODEPROTO,
        '__module__': 'docarray_pb2'
        # @@protoc_insertion_point(class_scope:docarray.NodeProto)
    },
)
_sym_db.RegisterMessage(NodeProto)

DocumentProto = _reflection.GeneratedProtocolMessageType(
    'DocumentProto',
    (_message.Message,),
    {
        'DataEntry': _reflection.GeneratedProtocolMessageType(
            'DataEntry',
            (_message.Message,),
            {
                'DESCRIPTOR': _DOCUMENTPROTO_DATAENTRY,
                '__module__': 'docarray_pb2'
                # @@protoc_insertion_point(class_scope:docarray.DocumentProto.DataEntry)
            },
        ),
        'DESCRIPTOR': _DOCUMENTPROTO,
        '__module__': 'docarray_pb2'
        # @@protoc_insertion_point(class_scope:docarray.DocumentProto)
    },
)
_sym_db.RegisterMessage(DocumentProto)
_sym_db.RegisterMessage(DocumentProto.DataEntry)

DocumentArrayProto = _reflection.GeneratedProtocolMessageType(
    'DocumentArrayProto',
    (_message.Message,),
    {
        'DESCRIPTOR': _DOCUMENTARRAYPROTO,
        '__module__': 'docarray_pb2'
        # @@protoc_insertion_point(class_scope:docarray.DocumentArrayProto)
    },
)
_sym_db.RegisterMessage(DocumentArrayProto)

ListOfDocumentArrayProto = _reflection.GeneratedProtocolMessageType(
    'ListOfDocumentArrayProto',
    (_message.Message,),
    {
        'DESCRIPTOR': _LISTOFDOCUMENTARRAYPROTO,
        '__module__': 'docarray_pb2'
        # @@protoc_insertion_point(class_scope:docarray.ListOfDocumentArrayProto)
    },
)
_sym_db.RegisterMessage(ListOfDocumentArrayProto)

DocumentArrayStackedProto = _reflection.GeneratedProtocolMessageType(
    'DocumentArrayStackedProto',
    (_message.Message,),
    {
        'TensorColumnsEntry': _reflection.GeneratedProtocolMessageType(
            'TensorColumnsEntry',
            (_message.Message,),
            {
                'DESCRIPTOR': _DOCUMENTARRAYSTACKEDPROTO_TENSORCOLUMNSENTRY,
                '__module__': 'docarray_pb2'
                # @@protoc_insertion_point(class_scope:docarray.DocumentArrayStackedProto.TensorColumnsEntry)
            },
        ),
        'DocColumnsEntry': _reflection.GeneratedProtocolMessageType(
            'DocColumnsEntry',
            (_message.Message,),
            {
                'DESCRIPTOR': _DOCUMENTARRAYSTACKEDPROTO_DOCCOLUMNSENTRY,
                '__module__': 'docarray_pb2'
                # @@protoc_insertion_point(class_scope:docarray.DocumentArrayStackedProto.DocColumnsEntry)
            },
        ),
        'DaColumnsEntry': _reflection.GeneratedProtocolMessageType(
            'DaColumnsEntry',
            (_message.Message,),
            {
                'DESCRIPTOR': _DOCUMENTARRAYSTACKEDPROTO_DACOLUMNSENTRY,
                '__module__': 'docarray_pb2'
                # @@protoc_insertion_point(class_scope:docarray.DocumentArrayStackedProto.DaColumnsEntry)
            },
        ),
        'AnyColumnsEntry': _reflection.GeneratedProtocolMessageType(
            'AnyColumnsEntry',
            (_message.Message,),
            {
                'DESCRIPTOR': _DOCUMENTARRAYSTACKEDPROTO_ANYCOLUMNSENTRY,
                '__module__': 'docarray_pb2'
                # @@protoc_insertion_point(class_scope:docarray.DocumentArrayStackedProto.AnyColumnsEntry)
            },
        ),
        'DESCRIPTOR': _DOCUMENTARRAYSTACKEDPROTO,
        '__module__': 'docarray_pb2'
        # @@protoc_insertion_point(class_scope:docarray.DocumentArrayStackedProto)
    },
)
_sym_db.RegisterMessage(DocumentArrayStackedProto)
_sym_db.RegisterMessage(DocumentArrayStackedProto.TensorColumnsEntry)
_sym_db.RegisterMessage(DocumentArrayStackedProto.DocColumnsEntry)
_sym_db.RegisterMessage(DocumentArrayStackedProto.DaColumnsEntry)
_sym_db.RegisterMessage(DocumentArrayStackedProto.AnyColumnsEntry)

if _descriptor._USE_C_DESCRIPTORS == False:

    DESCRIPTOR._options = None
    _DOCUMENTPROTO_DATAENTRY._options = None
    _DOCUMENTPROTO_DATAENTRY._serialized_options = b'8\001'
    _DOCUMENTARRAYSTACKEDPROTO_TENSORCOLUMNSENTRY._options = None
    _DOCUMENTARRAYSTACKEDPROTO_TENSORCOLUMNSENTRY._serialized_options = b'8\001'
    _DOCUMENTARRAYSTACKEDPROTO_DOCCOLUMNSENTRY._options = None
    _DOCUMENTARRAYSTACKEDPROTO_DOCCOLUMNSENTRY._serialized_options = b'8\001'
    _DOCUMENTARRAYSTACKEDPROTO_DACOLUMNSENTRY._options = None
    _DOCUMENTARRAYSTACKEDPROTO_DACOLUMNSENTRY._serialized_options = b'8\001'
    _DOCUMENTARRAYSTACKEDPROTO_ANYCOLUMNSENTRY._options = None
    _DOCUMENTARRAYSTACKEDPROTO_ANYCOLUMNSENTRY._serialized_options = b'8\001'
    _DENSENDARRAYPROTO._serialized_start = 58
    _DENSENDARRAYPROTO._serialized_end = 123
    _NDARRAYPROTO._serialized_start = 125
    _NDARRAYPROTO._serialized_end = 228
    _KEYVALUEPAIR._serialized_start = 230
    _KEYVALUEPAIR._serialized_end = 320
    _GENERICDICTVALUE._serialized_start = 322
    _GENERICDICTVALUE._serialized_end = 381
    _LISTOFANYPROTO._serialized_start = 383
    _LISTOFANYPROTO._serialized_end = 434
    _NODEPROTO._serialized_start = 437
    _NODEPROTO._serialized_end = 890
    _DOCUMENTPROTO._serialized_start = 893
    _DOCUMENTPROTO._serialized_end = 1023
    _DOCUMENTPROTO_DATAENTRY._serialized_start = 959
    _DOCUMENTPROTO_DATAENTRY._serialized_end = 1023
    _DOCUMENTARRAYPROTO._serialized_start = 1025
    _DOCUMENTARRAYPROTO._serialized_end = 1084
    _LISTOFDOCUMENTARRAYPROTO._serialized_start = 1086
    _LISTOFDOCUMENTARRAYPROTO._serialized_end = 1156
    _DOCUMENTARRAYSTACKEDPROTO._serialized_start = 1159
    _DOCUMENTARRAYSTACKEDPROTO._serialized_end = 1815
    _DOCUMENTARRAYSTACKEDPROTO_TENSORCOLUMNSENTRY._serialized_start = 1488
    _DOCUMENTARRAYSTACKEDPROTO_TENSORCOLUMNSENTRY._serialized_end = 1564
    _DOCUMENTARRAYSTACKEDPROTO_DOCCOLUMNSENTRY._serialized_start = 1566
    _DOCUMENTARRAYSTACKEDPROTO_DOCCOLUMNSENTRY._serialized_end = 1652
    _DOCUMENTARRAYSTACKEDPROTO_DACOLUMNSENTRY._serialized_start = 1654
    _DOCUMENTARRAYSTACKEDPROTO_DACOLUMNSENTRY._serialized_end = 1738
    _DOCUMENTARRAYSTACKEDPROTO_ANYCOLUMNSENTRY._serialized_start = 1740
    _DOCUMENTARRAYSTACKEDPROTO_ANYCOLUMNSENTRY._serialized_end = 1815
# @@protoc_insertion_point(module_scope)
