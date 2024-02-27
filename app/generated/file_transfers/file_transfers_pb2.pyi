from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FileChunk(_message.Message):
    __slots__ = ("length", "filename", "buffer")
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    length: int
    filename: str
    buffer: bytes
    def __init__(self, length: _Optional[int] = ..., filename: _Optional[str] = ..., buffer: _Optional[bytes] = ...) -> None: ...

class TransferResponse(_message.Message):
    __slots__ = ("length", "statusCode", "message")
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    STATUSCODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    length: int
    statusCode: int
    message: str
    def __init__(self, length: _Optional[int] = ..., statusCode: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...
