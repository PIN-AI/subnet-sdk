from subnet import checkpoint_pb2 as _checkpoint_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Validator(_message.Message):
    __slots__ = ("id", "pubkey", "weight", "endpoint")
    ID_FIELD_NUMBER: _ClassVar[int]
    PUBKEY_FIELD_NUMBER: _ClassVar[int]
    WEIGHT_FIELD_NUMBER: _ClassVar[int]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    id: str
    pubkey: bytes
    weight: int
    endpoint: str
    def __init__(self, id: _Optional[str] = ..., pubkey: _Optional[bytes] = ..., weight: _Optional[int] = ..., endpoint: _Optional[str] = ...) -> None: ...

class ValidatorSet(_message.Message):
    __slots__ = ("validators", "min_validators", "threshold_num", "threshold_denom", "effective_epoch")
    VALIDATORS_FIELD_NUMBER: _ClassVar[int]
    MIN_VALIDATORS_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_NUM_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_DENOM_FIELD_NUMBER: _ClassVar[int]
    EFFECTIVE_EPOCH_FIELD_NUMBER: _ClassVar[int]
    validators: _containers.RepeatedCompositeFieldContainer[Validator]
    min_validators: int
    threshold_num: int
    threshold_denom: int
    effective_epoch: int
    def __init__(self, validators: _Optional[_Iterable[_Union[Validator, _Mapping]]] = ..., min_validators: _Optional[int] = ..., threshold_num: _Optional[int] = ..., threshold_denom: _Optional[int] = ..., effective_epoch: _Optional[int] = ...) -> None: ...

class SignatureSubmission(_message.Message):
    __slots__ = ("cp_hash", "signature", "signer_id", "bit")
    CP_HASH_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    SIGNER_ID_FIELD_NUMBER: _ClassVar[int]
    BIT_FIELD_NUMBER: _ClassVar[int]
    cp_hash: bytes
    signature: _checkpoint_pb2.Signature
    signer_id: str
    bit: int
    def __init__(self, cp_hash: _Optional[bytes] = ..., signature: _Optional[_Union[_checkpoint_pb2.Signature, _Mapping]] = ..., signer_id: _Optional[str] = ..., bit: _Optional[int] = ...) -> None: ...
