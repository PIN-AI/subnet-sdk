from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ValidationPolicy(_message.Message):
    __slots__ = ("policy_id", "version", "effective_epoch", "rules", "metadata")
    class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MODE_UNSPECIFIED: _ClassVar[ValidationPolicy.Mode]
        DETERMINISTIC: _ClassVar[ValidationPolicy.Mode]
        SAMPLED: _ClassVar[ValidationPolicy.Mode]
        EXTERNAL: _ClassVar[ValidationPolicy.Mode]
        MULTI_SOURCE: _ClassVar[ValidationPolicy.Mode]
    MODE_UNSPECIFIED: ValidationPolicy.Mode
    DETERMINISTIC: ValidationPolicy.Mode
    SAMPLED: ValidationPolicy.Mode
    EXTERNAL: ValidationPolicy.Mode
    MULTI_SOURCE: ValidationPolicy.Mode
    class SamplingParams(_message.Message):
        __slots__ = ("sample_rate", "min_validators")
        SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
        MIN_VALIDATORS_FIELD_NUMBER: _ClassVar[int]
        sample_rate: float
        min_validators: int
        def __init__(self, sample_rate: _Optional[float] = ..., min_validators: _Optional[int] = ...) -> None: ...
    class ExecutionLimits(_message.Message):
        __slots__ = ("max_exec_time_ms", "max_memory_mb", "network_allowlist")
        MAX_EXEC_TIME_MS_FIELD_NUMBER: _ClassVar[int]
        MAX_MEMORY_MB_FIELD_NUMBER: _ClassVar[int]
        NETWORK_ALLOWLIST_FIELD_NUMBER: _ClassVar[int]
        max_exec_time_ms: int
        max_memory_mb: int
        network_allowlist: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, max_exec_time_ms: _Optional[int] = ..., max_memory_mb: _Optional[int] = ..., network_allowlist: _Optional[_Iterable[str]] = ...) -> None: ...
    class AntiCheat(_message.Message):
        __slots__ = ("similarity_threshold", "duplicate_submission_window", "blacklist")
        SIMILARITY_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
        DUPLICATE_SUBMISSION_WINDOW_FIELD_NUMBER: _ClassVar[int]
        BLACKLIST_FIELD_NUMBER: _ClassVar[int]
        similarity_threshold: int
        duplicate_submission_window: int
        blacklist: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, similarity_threshold: _Optional[int] = ..., duplicate_submission_window: _Optional[int] = ..., blacklist: _Optional[_Iterable[str]] = ...) -> None: ...
    class Rules(_message.Message):
        __slots__ = ("required_evidence", "validation_mode", "sampling_params", "execution_limits", "anti_cheat")
        REQUIRED_EVIDENCE_FIELD_NUMBER: _ClassVar[int]
        VALIDATION_MODE_FIELD_NUMBER: _ClassVar[int]
        SAMPLING_PARAMS_FIELD_NUMBER: _ClassVar[int]
        EXECUTION_LIMITS_FIELD_NUMBER: _ClassVar[int]
        ANTI_CHEAT_FIELD_NUMBER: _ClassVar[int]
        required_evidence: _containers.RepeatedScalarFieldContainer[str]
        validation_mode: ValidationPolicy.Mode
        sampling_params: ValidationPolicy.SamplingParams
        execution_limits: ValidationPolicy.ExecutionLimits
        anti_cheat: ValidationPolicy.AntiCheat
        def __init__(self, required_evidence: _Optional[_Iterable[str]] = ..., validation_mode: _Optional[_Union[ValidationPolicy.Mode, str]] = ..., sampling_params: _Optional[_Union[ValidationPolicy.SamplingParams, _Mapping]] = ..., execution_limits: _Optional[_Union[ValidationPolicy.ExecutionLimits, _Mapping]] = ..., anti_cheat: _Optional[_Union[ValidationPolicy.AntiCheat, _Mapping]] = ...) -> None: ...
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_EPOCH_FIELD_NUMBER: _ClassVar[int]
    RULES_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    policy_id: str
    version: str
    effective_epoch: int
    rules: ValidationPolicy.Rules
    metadata: bytes
    def __init__(self, policy_id: _Optional[str] = ..., version: _Optional[str] = ..., effective_epoch: _Optional[int] = ..., rules: _Optional[_Union[ValidationPolicy.Rules, _Mapping]] = ..., metadata: _Optional[bytes] = ...) -> None: ...

class VerificationRecord(_message.Message):
    __slots__ = ("record_id", "intent_id", "agent_id", "report_id", "policy_id", "validator_id", "verdict", "confidence", "reason", "evidence_checked", "sampling_info", "external_attestation", "timestamp", "validator_signature")
    class Verdict(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        VERDICT_UNSPECIFIED: _ClassVar[VerificationRecord.Verdict]
        PASS: _ClassVar[VerificationRecord.Verdict]
        FAIL: _ClassVar[VerificationRecord.Verdict]
        SKIP: _ClassVar[VerificationRecord.Verdict]
    VERDICT_UNSPECIFIED: VerificationRecord.Verdict
    PASS: VerificationRecord.Verdict
    FAIL: VerificationRecord.Verdict
    SKIP: VerificationRecord.Verdict
    class SamplingInfo(_message.Message):
        __slots__ = ("is_sampled", "sample_seed")
        IS_SAMPLED_FIELD_NUMBER: _ClassVar[int]
        SAMPLE_SEED_FIELD_NUMBER: _ClassVar[int]
        is_sampled: bool
        sample_seed: str
        def __init__(self, is_sampled: bool = ..., sample_seed: _Optional[str] = ...) -> None: ...
    class ExternalAttestation(_message.Message):
        __slots__ = ("provider", "reference", "signature")
        PROVIDER_FIELD_NUMBER: _ClassVar[int]
        REFERENCE_FIELD_NUMBER: _ClassVar[int]
        SIGNATURE_FIELD_NUMBER: _ClassVar[int]
        provider: str
        reference: str
        signature: bytes
        def __init__(self, provider: _Optional[str] = ..., reference: _Optional[str] = ..., signature: _Optional[bytes] = ...) -> None: ...
    RECORD_ID_FIELD_NUMBER: _ClassVar[int]
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    REPORT_ID_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_ID_FIELD_NUMBER: _ClassVar[int]
    VERDICT_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    EVIDENCE_CHECKED_FIELD_NUMBER: _ClassVar[int]
    SAMPLING_INFO_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_ATTESTATION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    record_id: str
    intent_id: str
    agent_id: str
    report_id: str
    policy_id: str
    validator_id: str
    verdict: VerificationRecord.Verdict
    confidence: float
    reason: str
    evidence_checked: _containers.RepeatedScalarFieldContainer[str]
    sampling_info: VerificationRecord.SamplingInfo
    external_attestation: VerificationRecord.ExternalAttestation
    timestamp: int
    validator_signature: bytes
    def __init__(self, record_id: _Optional[str] = ..., intent_id: _Optional[str] = ..., agent_id: _Optional[str] = ..., report_id: _Optional[str] = ..., policy_id: _Optional[str] = ..., validator_id: _Optional[str] = ..., verdict: _Optional[_Union[VerificationRecord.Verdict, str]] = ..., confidence: _Optional[float] = ..., reason: _Optional[str] = ..., evidence_checked: _Optional[_Iterable[str]] = ..., sampling_info: _Optional[_Union[VerificationRecord.SamplingInfo, _Mapping]] = ..., external_attestation: _Optional[_Union[VerificationRecord.ExternalAttestation, _Mapping]] = ..., timestamp: _Optional[int] = ..., validator_signature: _Optional[bytes] = ...) -> None: ...

class PolicyQuery(_message.Message):
    __slots__ = ("subnet_id", "intent_type", "epoch")
    SUBNET_ID_FIELD_NUMBER: _ClassVar[int]
    INTENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    subnet_id: str
    intent_type: str
    epoch: int
    def __init__(self, subnet_id: _Optional[str] = ..., intent_type: _Optional[str] = ..., epoch: _Optional[int] = ...) -> None: ...

class VerificationQuery(_message.Message):
    __slots__ = ("intent_id", "agent_id", "limit")
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    intent_id: str
    agent_id: str
    limit: int
    def __init__(self, intent_id: _Optional[str] = ..., agent_id: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...
