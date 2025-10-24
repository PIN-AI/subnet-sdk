from subnet import execution_report_pb2 as _execution_report_pb2
from subnet import validation_pb2 as _validation_pb2
from subnet import checkpoint_pb2 as _checkpoint_pb2
from subnet import validator_pb2 as _validator_pb2
from subnet import report_pb2 as _report_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Ack(_message.Message):
    __slots__ = ("ok", "msg")
    OK_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    ok: bool
    msg: str
    def __init__(self, ok: bool = ..., msg: _Optional[str] = ...) -> None: ...

class GetCheckpointRequest(_message.Message):
    __slots__ = ("subnet_id", "epoch", "cp_hash")
    SUBNET_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    CP_HASH_FIELD_NUMBER: _ClassVar[int]
    subnet_id: str
    epoch: int
    cp_hash: bytes
    def __init__(self, subnet_id: _Optional[str] = ..., epoch: _Optional[int] = ..., cp_hash: _Optional[bytes] = ...) -> None: ...

class GetValidationPolicyRequest(_message.Message):
    __slots__ = ("intent_type",)
    INTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    intent_type: str
    def __init__(self, intent_type: _Optional[str] = ...) -> None: ...

class GetVerificationRecordsRequest(_message.Message):
    __slots__ = ("intent_id", "agent_id", "limit")
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    intent_id: str
    agent_id: str
    limit: int
    def __init__(self, intent_id: _Optional[str] = ..., agent_id: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class GetValidatorMetricsRequest(_message.Message):
    __slots__ = ("validator_id",)
    VALIDATOR_ID_FIELD_NUMBER: _ClassVar[int]
    validator_id: str
    def __init__(self, validator_id: _Optional[str] = ...) -> None: ...

class DoubleSignQuery(_message.Message):
    __slots__ = ("validator_id", "epoch", "limit")
    VALIDATOR_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    validator_id: str
    epoch: int
    limit: int
    def __init__(self, validator_id: _Optional[str] = ..., epoch: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class DoubleSignEvidence(_message.Message):
    __slots__ = ("validator_id", "epoch", "evidence")
    VALIDATOR_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_FIELD_NUMBER: _ClassVar[int]
    validator_id: str
    epoch: int
    evidence: bytes
    def __init__(self, validator_id: _Optional[str] = ..., epoch: _Optional[int] = ..., evidence: _Optional[bytes] = ...) -> None: ...

class ValidatorMetrics(_message.Message):
    __slots__ = ("validator_id", "reports_verified", "checkpoints_signed", "uptime_percentage", "last_active")
    VALIDATOR_ID_FIELD_NUMBER: _ClassVar[int]
    REPORTS_VERIFIED_FIELD_NUMBER: _ClassVar[int]
    CHECKPOINTS_SIGNED_FIELD_NUMBER: _ClassVar[int]
    UPTIME_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    LAST_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    validator_id: str
    reports_verified: int
    checkpoints_signed: int
    uptime_percentage: float
    last_active: int
    def __init__(self, validator_id: _Optional[str] = ..., reports_verified: _Optional[int] = ..., checkpoints_signed: _Optional[int] = ..., uptime_percentage: _Optional[float] = ..., last_active: _Optional[int] = ...) -> None: ...

class ExecutionReportBatchRequest(_message.Message):
    __slots__ = ("reports", "batch_id", "partial_ok")
    REPORTS_FIELD_NUMBER: _ClassVar[int]
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_OK_FIELD_NUMBER: _ClassVar[int]
    reports: _containers.RepeatedCompositeFieldContainer[_execution_report_pb2.ExecutionReport]
    batch_id: str
    partial_ok: bool
    def __init__(self, reports: _Optional[_Iterable[_Union[_execution_report_pb2.ExecutionReport, _Mapping]]] = ..., batch_id: _Optional[str] = ..., partial_ok: bool = ...) -> None: ...

class ExecutionReportBatchResponse(_message.Message):
    __slots__ = ("receipts", "success", "failed", "msg")
    RECEIPTS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    receipts: _containers.RepeatedCompositeFieldContainer[_report_pb2.Receipt]
    success: int
    failed: int
    msg: str
    def __init__(self, receipts: _Optional[_Iterable[_Union[_report_pb2.Receipt, _Mapping]]] = ..., success: _Optional[int] = ..., failed: _Optional[int] = ..., msg: _Optional[str] = ...) -> None: ...
