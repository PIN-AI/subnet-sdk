from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AgentStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AGENT_STATUS_UNKNOWN: _ClassVar[AgentStatus]
    AGENT_STATUS_ACTIVE: _ClassVar[AgentStatus]
    AGENT_STATUS_INACTIVE: _ClassVar[AgentStatus]
    AGENT_STATUS_UNHEALTHY: _ClassVar[AgentStatus]
AGENT_STATUS_UNKNOWN: AgentStatus
AGENT_STATUS_ACTIVE: AgentStatus
AGENT_STATUS_INACTIVE: AgentStatus
AGENT_STATUS_UNHEALTHY: AgentStatus

class Agent(_message.Message):
    __slots__ = ("id", "capabilities", "endpoint", "status", "last_seen")
    ID_FIELD_NUMBER: _ClassVar[int]
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_FIELD_NUMBER: _ClassVar[int]
    id: str
    capabilities: _containers.RepeatedScalarFieldContainer[str]
    endpoint: str
    status: AgentStatus
    last_seen: int
    def __init__(self, id: _Optional[str] = ..., capabilities: _Optional[_Iterable[str]] = ..., endpoint: _Optional[str] = ..., status: _Optional[_Union[AgentStatus, str]] = ..., last_seen: _Optional[int] = ...) -> None: ...
