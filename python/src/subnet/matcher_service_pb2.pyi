from subnet import bid_pb2 as _bid_pb2
from subnet import matcher_pb2 as _matcher_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StreamTasksRequest(_message.Message):
    __slots__ = ("agent_id",)
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    def __init__(self, agent_id: _Optional[str] = ...) -> None: ...

class ExecutionTask(_message.Message):
    __slots__ = ("task_id", "intent_id", "agent_id", "bid_id", "created_at", "deadline", "intent_data", "intent_type")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    BID_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    DEADLINE_FIELD_NUMBER: _ClassVar[int]
    INTENT_DATA_FIELD_NUMBER: _ClassVar[int]
    INTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    intent_id: str
    agent_id: str
    bid_id: str
    created_at: int
    deadline: int
    intent_data: bytes
    intent_type: str
    def __init__(self, task_id: _Optional[str] = ..., intent_id: _Optional[str] = ..., agent_id: _Optional[str] = ..., bid_id: _Optional[str] = ..., created_at: _Optional[int] = ..., deadline: _Optional[int] = ..., intent_data: _Optional[bytes] = ..., intent_type: _Optional[str] = ...) -> None: ...
