from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FileTransfer(_message.Message):
    __slots__ = ("fileInfo", "buffer")
    FILEINFO_FIELD_NUMBER: _ClassVar[int]
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    fileInfo: FileInfo
    buffer: Chunk
    def __init__(self, fileInfo: _Optional[_Union[FileInfo, _Mapping]] = ..., buffer: _Optional[_Union[Chunk, _Mapping]] = ...) -> None: ...

class Chunk(_message.Message):
    __slots__ = ("buffer",)
    BUFFER_FIELD_NUMBER: _ClassVar[int]
    buffer: bytes
    def __init__(self, buffer: _Optional[bytes] = ...) -> None: ...

class FileInfo(_message.Message):
    __slots__ = ("totalLength", "filename")
    TOTALLENGTH_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    totalLength: int
    filename: str
    def __init__(self, totalLength: _Optional[int] = ..., filename: _Optional[str] = ...) -> None: ...

class TransferResponse(_message.Message):
    __slots__ = ("length", "statusCode", "message")
    LENGTH_FIELD_NUMBER: _ClassVar[int]
    STATUSCODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    length: int
    statusCode: int
    message: str
    def __init__(self, length: _Optional[int] = ..., statusCode: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...
