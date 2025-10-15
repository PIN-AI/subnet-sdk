from subnet import report_pb2 as _report_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExecutionReport(_message.Message):
    __slots__ = ("report_id", "assignment_id", "intent_id", "agent_id", "status", "result_data", "evidence", "error", "timestamp", "signature", "root_ref")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_UNSPECIFIED: _ClassVar[ExecutionReport.Status]
        SUCCESS: _ClassVar[ExecutionReport.Status]
        FAILED: _ClassVar[ExecutionReport.Status]
        PARTIAL: _ClassVar[ExecutionReport.Status]
    STATUS_UNSPECIFIED: ExecutionReport.Status
    SUCCESS: ExecutionReport.Status
    FAILED: ExecutionReport.Status
    PARTIAL: ExecutionReport.Status
    REPORT_ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENT_ID_FIELD_NUMBER: _ClassVar[int]
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_DATA_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    ROOT_REF_FIELD_NUMBER: _ClassVar[int]
    report_id: str
    assignment_id: str
    intent_id: str
    agent_id: str
    status: ExecutionReport.Status
    result_data: bytes
    evidence: VerificationEvidence
    error: ErrorInfo
    timestamp: int
    signature: bytes
    root_ref: _report_pb2.RootLayerRef
    def __init__(self, report_id: _Optional[str] = ..., assignment_id: _Optional[str] = ..., intent_id: _Optional[str] = ..., agent_id: _Optional[str] = ..., status: _Optional[_Union[ExecutionReport.Status, str]] = ..., result_data: _Optional[bytes] = ..., evidence: _Optional[_Union[VerificationEvidence, _Mapping]] = ..., error: _Optional[_Union[ErrorInfo, _Mapping]] = ..., timestamp: _Optional[int] = ..., signature: _Optional[bytes] = ..., root_ref: _Optional[_Union[_report_pb2.RootLayerRef, _Mapping]] = ...) -> None: ...

class VerificationEvidence(_message.Message):
    __slots__ = ("env_fingerprint", "inputs_hash", "outputs_hash", "transcript_root", "proof_exec", "resource_usage", "external_refs")
    ENV_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    INPUTS_HASH_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_HASH_FIELD_NUMBER: _ClassVar[int]
    TRANSCRIPT_ROOT_FIELD_NUMBER: _ClassVar[int]
    PROOF_EXEC_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_USAGE_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_REFS_FIELD_NUMBER: _ClassVar[int]
    env_fingerprint: bytes
    inputs_hash: bytes
    outputs_hash: bytes
    transcript_root: bytes
    proof_exec: bytes
    resource_usage: ResourceUsage
    external_refs: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, env_fingerprint: _Optional[bytes] = ..., inputs_hash: _Optional[bytes] = ..., outputs_hash: _Optional[bytes] = ..., transcript_root: _Optional[bytes] = ..., proof_exec: _Optional[bytes] = ..., resource_usage: _Optional[_Union[ResourceUsage, _Mapping]] = ..., external_refs: _Optional[_Iterable[str]] = ...) -> None: ...

class ResourceUsage(_message.Message):
    __slots__ = ("cpu_ms", "memory_mb", "io_ops", "network_bytes")
    CPU_MS_FIELD_NUMBER: _ClassVar[int]
    MEMORY_MB_FIELD_NUMBER: _ClassVar[int]
    IO_OPS_FIELD_NUMBER: _ClassVar[int]
    NETWORK_BYTES_FIELD_NUMBER: _ClassVar[int]
    cpu_ms: int
    memory_mb: int
    io_ops: int
    network_bytes: int
    def __init__(self, cpu_ms: _Optional[int] = ..., memory_mb: _Optional[int] = ..., io_ops: _Optional[int] = ..., network_bytes: _Optional[int] = ...) -> None: ...

class ErrorInfo(_message.Message):
    __slots__ = ("code", "message", "details")
    CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    code: str
    message: str
    details: bytes
    def __init__(self, code: _Optional[str] = ..., message: _Optional[str] = ..., details: _Optional[bytes] = ...) -> None: ...
