from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RootLayerRef(_message.Message):
    __slots__ = ("height", "root", "proof")
    HEIGHT_FIELD_NUMBER: _ClassVar[int]
    ROOT_FIELD_NUMBER: _ClassVar[int]
    PROOF_FIELD_NUMBER: _ClassVar[int]
    height: int
    root: bytes
    proof: bytes
    def __init__(self, height: _Optional[int] = ..., root: _Optional[bytes] = ..., proof: _Optional[bytes] = ...) -> None: ...

class Report(_message.Message):
    __slots__ = ("intent_id", "root_ref", "executed_at", "received_ts", "agent_id", "agent_endpoint", "env_fingerprint", "result_hash", "result_uri", "proof_exec", "confidence_score", "cost_estimate", "validator_hints", "assignment_id", "result_data", "agent_signature", "agent_pubkey", "agent_nonce")
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    ROOT_REF_FIELD_NUMBER: _ClassVar[int]
    EXECUTED_AT_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_TS_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    ENV_FINGERPRINT_FIELD_NUMBER: _ClassVar[int]
    RESULT_HASH_FIELD_NUMBER: _ClassVar[int]
    RESULT_URI_FIELD_NUMBER: _ClassVar[int]
    PROOF_EXEC_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_SCORE_FIELD_NUMBER: _ClassVar[int]
    COST_ESTIMATE_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_HINTS_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENT_ID_FIELD_NUMBER: _ClassVar[int]
    RESULT_DATA_FIELD_NUMBER: _ClassVar[int]
    AGENT_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    AGENT_PUBKEY_FIELD_NUMBER: _ClassVar[int]
    AGENT_NONCE_FIELD_NUMBER: _ClassVar[int]
    intent_id: str
    root_ref: RootLayerRef
    executed_at: int
    received_ts: int
    agent_id: str
    agent_endpoint: str
    env_fingerprint: bytes
    result_hash: bytes
    result_uri: str
    proof_exec: bytes
    confidence_score: int
    cost_estimate: int
    validator_hints: bytes
    assignment_id: str
    result_data: bytes
    agent_signature: bytes
    agent_pubkey: bytes
    agent_nonce: int
    def __init__(self, intent_id: _Optional[str] = ..., root_ref: _Optional[_Union[RootLayerRef, _Mapping]] = ..., executed_at: _Optional[int] = ..., received_ts: _Optional[int] = ..., agent_id: _Optional[str] = ..., agent_endpoint: _Optional[str] = ..., env_fingerprint: _Optional[bytes] = ..., result_hash: _Optional[bytes] = ..., result_uri: _Optional[str] = ..., proof_exec: _Optional[bytes] = ..., confidence_score: _Optional[int] = ..., cost_estimate: _Optional[int] = ..., validator_hints: _Optional[bytes] = ..., assignment_id: _Optional[str] = ..., result_data: _Optional[bytes] = ..., agent_signature: _Optional[bytes] = ..., agent_pubkey: _Optional[bytes] = ..., agent_nonce: _Optional[int] = ...) -> None: ...

class Receipt(_message.Message):
    __slots__ = ("intent_id", "validator_id", "received_ts", "status", "score_hint", "report_id", "phase")
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_ID_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_TS_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SCORE_HINT_FIELD_NUMBER: _ClassVar[int]
    REPORT_ID_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    intent_id: str
    validator_id: str
    received_ts: int
    status: str
    score_hint: int
    report_id: str
    phase: str
    def __init__(self, intent_id: _Optional[str] = ..., validator_id: _Optional[str] = ..., received_ts: _Optional[int] = ..., status: _Optional[str] = ..., score_hint: _Optional[int] = ..., report_id: _Optional[str] = ..., phase: _Optional[str] = ...) -> None: ...
