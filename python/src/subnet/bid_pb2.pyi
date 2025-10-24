from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class BidStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BID_STATUS_UNSPECIFIED: _ClassVar[BidStatus]
    BID_STATUS_SUBMITTED: _ClassVar[BidStatus]
    BID_STATUS_ACCEPTED: _ClassVar[BidStatus]
    BID_STATUS_REJECTED: _ClassVar[BidStatus]
    BID_STATUS_WINNER: _ClassVar[BidStatus]
    BID_STATUS_RUNNER_UP: _ClassVar[BidStatus]
BID_STATUS_UNSPECIFIED: BidStatus
BID_STATUS_SUBMITTED: BidStatus
BID_STATUS_ACCEPTED: BidStatus
BID_STATUS_REJECTED: BidStatus
BID_STATUS_WINNER: BidStatus
BID_STATUS_RUNNER_UP: BidStatus

class Bid(_message.Message):
    __slots__ = ("bid_id", "intent_id", "agent_id", "price", "token", "settle_chain", "submitted_at", "nonce", "signature", "status", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    BID_ID_FIELD_NUMBER: _ClassVar[int]
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    SETTLE_CHAIN_FIELD_NUMBER: _ClassVar[int]
    SUBMITTED_AT_FIELD_NUMBER: _ClassVar[int]
    NONCE_FIELD_NUMBER: _ClassVar[int]
    SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    bid_id: str
    intent_id: str
    agent_id: str
    price: int
    token: str
    settle_chain: str
    submitted_at: int
    nonce: str
    signature: bytes
    status: BidStatus
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, bid_id: _Optional[str] = ..., intent_id: _Optional[str] = ..., agent_id: _Optional[str] = ..., price: _Optional[int] = ..., token: _Optional[str] = ..., settle_chain: _Optional[str] = ..., submitted_at: _Optional[int] = ..., nonce: _Optional[str] = ..., signature: _Optional[bytes] = ..., status: _Optional[_Union[BidStatus, str]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class BidSubmissionAck(_message.Message):
    __slots__ = ("bid_id", "accepted", "reason", "status", "recorded_at")
    BID_ID_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RECORDED_AT_FIELD_NUMBER: _ClassVar[int]
    bid_id: str
    accepted: bool
    reason: str
    status: BidStatus
    recorded_at: int
    def __init__(self, bid_id: _Optional[str] = ..., accepted: bool = ..., reason: _Optional[str] = ..., status: _Optional[_Union[BidStatus, str]] = ..., recorded_at: _Optional[int] = ...) -> None: ...
