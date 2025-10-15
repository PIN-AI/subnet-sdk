from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CommitmentRoots(_message.Message):
    __slots__ = ("agent_root", "agent_service_root", "rank_root", "metrics_root", "data_usage_root", "state_root", "event_root", "cross_subnet_root")
    AGENT_ROOT_FIELD_NUMBER: _ClassVar[int]
    AGENT_SERVICE_ROOT_FIELD_NUMBER: _ClassVar[int]
    RANK_ROOT_FIELD_NUMBER: _ClassVar[int]
    METRICS_ROOT_FIELD_NUMBER: _ClassVar[int]
    DATA_USAGE_ROOT_FIELD_NUMBER: _ClassVar[int]
    STATE_ROOT_FIELD_NUMBER: _ClassVar[int]
    EVENT_ROOT_FIELD_NUMBER: _ClassVar[int]
    CROSS_SUBNET_ROOT_FIELD_NUMBER: _ClassVar[int]
    agent_root: bytes
    agent_service_root: bytes
    rank_root: bytes
    metrics_root: bytes
    data_usage_root: bytes
    state_root: bytes
    event_root: bytes
    cross_subnet_root: bytes
    def __init__(self, agent_root: _Optional[bytes] = ..., agent_service_root: _Optional[bytes] = ..., rank_root: _Optional[bytes] = ..., metrics_root: _Optional[bytes] = ..., data_usage_root: _Optional[bytes] = ..., state_root: _Optional[bytes] = ..., event_root: _Optional[bytes] = ..., cross_subnet_root: _Optional[bytes] = ...) -> None: ...

class DACommitment(_message.Message):
    __slots__ = ("kind", "pointer", "size_hint", "segment_hashes", "expiry")
    KIND_FIELD_NUMBER: _ClassVar[int]
    POINTER_FIELD_NUMBER: _ClassVar[int]
    SIZE_HINT_FIELD_NUMBER: _ClassVar[int]
    SEGMENT_HASHES_FIELD_NUMBER: _ClassVar[int]
    EXPIRY_FIELD_NUMBER: _ClassVar[int]
    kind: str
    pointer: str
    size_hint: int
    segment_hashes: _containers.RepeatedScalarFieldContainer[bytes]
    expiry: int
    def __init__(self, kind: _Optional[str] = ..., pointer: _Optional[str] = ..., size_hint: _Optional[int] = ..., segment_hashes: _Optional[_Iterable[bytes]] = ..., expiry: _Optional[int] = ...) -> None: ...

class EpochSlot(_message.Message):
    __slots__ = ("epoch", "slot")
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    SLOT_FIELD_NUMBER: _ClassVar[int]
    epoch: int
    slot: int
    def __init__(self, epoch: _Optional[int] = ..., slot: _Optional[int] = ...) -> None: ...

class CheckpointHeader(_message.Message):
    __slots__ = ("subnet_id", "epoch", "parent_cp_hash", "timestamp", "version", "params_hash", "roots", "da_commitments", "validator_set_id", "stats", "aux_hash", "epoch_slot", "assignments_root", "validation_commitment", "policy_root", "signatures")
    SUBNET_ID_FIELD_NUMBER: _ClassVar[int]
    EPOCH_FIELD_NUMBER: _ClassVar[int]
    PARENT_CP_HASH_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PARAMS_HASH_FIELD_NUMBER: _ClassVar[int]
    ROOTS_FIELD_NUMBER: _ClassVar[int]
    DA_COMMITMENTS_FIELD_NUMBER: _ClassVar[int]
    VALIDATOR_SET_ID_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    AUX_HASH_FIELD_NUMBER: _ClassVar[int]
    EPOCH_SLOT_FIELD_NUMBER: _ClassVar[int]
    ASSIGNMENTS_ROOT_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_COMMITMENT_FIELD_NUMBER: _ClassVar[int]
    POLICY_ROOT_FIELD_NUMBER: _ClassVar[int]
    SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    subnet_id: str
    epoch: int
    parent_cp_hash: bytes
    timestamp: int
    version: int
    params_hash: bytes
    roots: CommitmentRoots
    da_commitments: _containers.RepeatedCompositeFieldContainer[DACommitment]
    validator_set_id: str
    stats: bytes
    aux_hash: bytes
    epoch_slot: EpochSlot
    assignments_root: bytes
    validation_commitment: bytes
    policy_root: bytes
    signatures: CheckpointSignatures
    def __init__(self, subnet_id: _Optional[str] = ..., epoch: _Optional[int] = ..., parent_cp_hash: _Optional[bytes] = ..., timestamp: _Optional[int] = ..., version: _Optional[int] = ..., params_hash: _Optional[bytes] = ..., roots: _Optional[_Union[CommitmentRoots, _Mapping]] = ..., da_commitments: _Optional[_Iterable[_Union[DACommitment, _Mapping]]] = ..., validator_set_id: _Optional[str] = ..., stats: _Optional[bytes] = ..., aux_hash: _Optional[bytes] = ..., epoch_slot: _Optional[_Union[EpochSlot, _Mapping]] = ..., assignments_root: _Optional[bytes] = ..., validation_commitment: _Optional[bytes] = ..., policy_root: _Optional[bytes] = ..., signatures: _Optional[_Union[CheckpointSignatures, _Mapping]] = ...) -> None: ...

class CheckpointSignatures(_message.Message):
    __slots__ = ("ecdsa_signatures", "signers_bitmap", "signature_count", "total_weight")
    ECDSA_SIGNATURES_FIELD_NUMBER: _ClassVar[int]
    SIGNERS_BITMAP_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    ecdsa_signatures: _containers.RepeatedScalarFieldContainer[bytes]
    signers_bitmap: bytes
    signature_count: int
    total_weight: int
    def __init__(self, ecdsa_signatures: _Optional[_Iterable[bytes]] = ..., signers_bitmap: _Optional[bytes] = ..., signature_count: _Optional[int] = ..., total_weight: _Optional[int] = ...) -> None: ...

class Signature(_message.Message):
    __slots__ = ("algo", "der", "pubkey", "msg_hash", "signer_id")
    ALGO_FIELD_NUMBER: _ClassVar[int]
    DER_FIELD_NUMBER: _ClassVar[int]
    PUBKEY_FIELD_NUMBER: _ClassVar[int]
    MSG_HASH_FIELD_NUMBER: _ClassVar[int]
    SIGNER_ID_FIELD_NUMBER: _ClassVar[int]
    algo: str
    der: bytes
    pubkey: bytes
    msg_hash: bytes
    signer_id: str
    def __init__(self, algo: _Optional[str] = ..., der: _Optional[bytes] = ..., pubkey: _Optional[bytes] = ..., msg_hash: _Optional[bytes] = ..., signer_id: _Optional[str] = ...) -> None: ...
