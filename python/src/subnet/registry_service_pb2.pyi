from subnet import agent_pb2 as _agent_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RegisterAgentRequest(_message.Message):
    __slots__ = ("agent",)
    AGENT_FIELD_NUMBER: _ClassVar[int]
    agent: _agent_pb2.Agent
    def __init__(self, agent: _Optional[_Union[_agent_pb2.Agent, _Mapping]] = ...) -> None: ...

class RegisterAgentResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class UnregisterAgentRequest(_message.Message):
    __slots__ = ("agent_id",)
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    def __init__(self, agent_id: _Optional[str] = ...) -> None: ...

class UnregisterAgentResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class DiscoverAgentsRequest(_message.Message):
    __slots__ = ("capabilities",)
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    capabilities: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, capabilities: _Optional[_Iterable[str]] = ...) -> None: ...

class DiscoverAgentsResponse(_message.Message):
    __slots__ = ("agents",)
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    agents: _containers.RepeatedCompositeFieldContainer[_agent_pb2.Agent]
    def __init__(self, agents: _Optional[_Iterable[_Union[_agent_pb2.Agent, _Mapping]]] = ...) -> None: ...

class HeartbeatRequest(_message.Message):
    __slots__ = ("agent_id", "status")
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    status: _agent_pb2.AgentStatus
    def __init__(self, agent_id: _Optional[str] = ..., status: _Optional[_Union[_agent_pb2.AgentStatus, str]] = ...) -> None: ...

class HeartbeatResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class GetAgentRequest(_message.Message):
    __slots__ = ("agent_id",)
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    agent_id: str
    def __init__(self, agent_id: _Optional[str] = ...) -> None: ...

class GetAgentResponse(_message.Message):
    __slots__ = ("agent",)
    AGENT_FIELD_NUMBER: _ClassVar[int]
    agent: _agent_pb2.Agent
    def __init__(self, agent: _Optional[_Union[_agent_pb2.Agent, _Mapping]] = ...) -> None: ...

class ListAgentsRequest(_message.Message):
    __slots__ = ("capabilities", "status")
    CAPABILITIES_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    capabilities: _containers.RepeatedScalarFieldContainer[str]
    status: _agent_pb2.AgentStatus
    def __init__(self, capabilities: _Optional[_Iterable[str]] = ..., status: _Optional[_Union[_agent_pb2.AgentStatus, str]] = ...) -> None: ...

class ListAgentsResponse(_message.Message):
    __slots__ = ("agents", "total")
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    agents: _containers.RepeatedCompositeFieldContainer[_agent_pb2.Agent]
    total: int
    def __init__(self, agents: _Optional[_Iterable[_Union[_agent_pb2.Agent, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...
