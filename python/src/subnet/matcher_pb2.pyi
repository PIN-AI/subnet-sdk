from subnet import bid_pb2 as _bid_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class IntentBidSnapshot(_message.Message):
    __slots__ = ("intent_id", "bids", "bidding_start_time", "bidding_end_time", "bidding_closed")
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    BIDS_FIELD_NUMBER: _ClassVar[int]
    BIDDING_START_TIME_FIELD_NUMBER: _ClassVar[int]
    BIDDING_END_TIME_FIELD_NUMBER: _ClassVar[int]
    BIDDING_CLOSED_FIELD_NUMBER: _ClassVar[int]
    intent_id: str
    bids: _containers.RepeatedCompositeFieldContainer[_bid_pb2.Bid]
    bidding_start_time: int
    bidding_end_time: int
    bidding_closed: bool
    def __init__(self, intent_id: _Optional[str] = ..., bids: _Optional[_Iterable[_Union[_bid_pb2.Bid, _Mapping]]] = ..., bidding_start_time: _Optional[int] = ..., bidding_end_time: _Optional[int] = ..., bidding_closed: bool = ...) -> None: ...

class MatchingResult(_message.Message):
    __slots__ = ("matcher_id", "intent_id", "winning_bid_id", "winning_agent_id", "runner_up_bid_ids", "matched_at", "matching_reason", "result_hash", "matcher_signature")
    MATCHER_ID_FIELD_NUMBER: _ClassVar[int]
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    WINNING_BID_ID_FIELD_NUMBER: _ClassVar[int]
    WINNING_AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    RUNNER_UP_BID_IDS_FIELD_NUMBER: _ClassVar[int]
    MATCHED_AT_FIELD_NUMBER: _ClassVar[int]
    MATCHING_REASON_FIELD_NUMBER: _ClassVar[int]
    RESULT_HASH_FIELD_NUMBER: _ClassVar[int]
    MATCHER_SIGNATURE_FIELD_NUMBER: _ClassVar[int]
    matcher_id: str
    intent_id: str
    winning_bid_id: str
    winning_agent_id: str
    runner_up_bid_ids: _containers.RepeatedScalarFieldContainer[str]
    matched_at: int
    matching_reason: str
    result_hash: bytes
    matcher_signature: bytes
    def __init__(self, matcher_id: _Optional[str] = ..., intent_id: _Optional[str] = ..., winning_bid_id: _Optional[str] = ..., winning_agent_id: _Optional[str] = ..., runner_up_bid_ids: _Optional[_Iterable[str]] = ..., matched_at: _Optional[int] = ..., matching_reason: _Optional[str] = ..., result_hash: _Optional[bytes] = ..., matcher_signature: _Optional[bytes] = ...) -> None: ...

class SubmitBidRequest(_message.Message):
    __slots__ = ("bid",)
    BID_FIELD_NUMBER: _ClassVar[int]
    bid: _bid_pb2.Bid
    def __init__(self, bid: _Optional[_Union[_bid_pb2.Bid, _Mapping]] = ...) -> None: ...

class SubmitBidResponse(_message.Message):
    __slots__ = ("ack",)
    ACK_FIELD_NUMBER: _ClassVar[int]
    ack: _bid_pb2.BidSubmissionAck
    def __init__(self, ack: _Optional[_Union[_bid_pb2.BidSubmissionAck, _Mapping]] = ...) -> None: ...

class GetIntentSnapshotRequest(_message.Message):
    __slots__ = ("intent_id", "include_closed")
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_CLOSED_FIELD_NUMBER: _ClassVar[int]
    intent_id: str
    include_closed: bool
    def __init__(self, intent_id: _Optional[str] = ..., include_closed: bool = ...) -> None: ...

class GetIntentSnapshotResponse(_message.Message):
    __slots__ = ("snapshot",)
    SNAPSHOT_FIELD_NUMBER: _ClassVar[int]
    snapshot: IntentBidSnapshot
    def __init__(self, snapshot: _Optional[_Union[IntentBidSnapshot, _Mapping]] = ...) -> None: ...

class StreamIntentsRequest(_message.Message):
    __slots__ = ("subnet_id", "intent_types")
    SUBNET_ID_FIELD_NUMBER: _ClassVar[int]
    INTENT_TYPES_FIELD_NUMBER: _ClassVar[int]
    subnet_id: str
    intent_types: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, subnet_id: _Optional[str] = ..., intent_types: _Optional[_Iterable[str]] = ...) -> None: ...

class StreamBidsRequest(_message.Message):
    __slots__ = ("intent_id", "agent_id")
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    intent_id: str
    agent_id: str
    def __init__(self, intent_id: _Optional[str] = ..., agent_id: _Optional[str] = ...) -> None: ...

class MatcherIntentUpdate(_message.Message):
    __slots__ = ("intent_id", "update_type", "timestamp")
    INTENT_ID_FIELD_NUMBER: _ClassVar[int]
    UPDATE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    intent_id: str
    update_type: str
    timestamp: int
    def __init__(self, intent_id: _Optional[str] = ..., update_type: _Optional[str] = ..., timestamp: _Optional[int] = ...) -> None: ...

class BidEvent(_message.Message):
    __slots__ = ("type", "bid", "timestamp")
    class EventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        EVENT_UNSPECIFIED: _ClassVar[BidEvent.EventType]
        EVENT_SUBMITTED: _ClassVar[BidEvent.EventType]
        EVENT_ACCEPTED: _ClassVar[BidEvent.EventType]
        EVENT_REJECTED: _ClassVar[BidEvent.EventType]
        EVENT_WITHDRAWN: _ClassVar[BidEvent.EventType]
    EVENT_UNSPECIFIED: BidEvent.EventType
    EVENT_SUBMITTED: BidEvent.EventType
    EVENT_ACCEPTED: BidEvent.EventType
    EVENT_REJECTED: BidEvent.EventType
    EVENT_WITHDRAWN: BidEvent.EventType
    TYPE_FIELD_NUMBER: _ClassVar[int]
    BID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    type: BidEvent.EventType
    bid: _bid_pb2.Bid
    timestamp: int
    def __init__(self, type: _Optional[_Union[BidEvent.EventType, str]] = ..., bid: _Optional[_Union[_bid_pb2.Bid, _Mapping]] = ..., timestamp: _Optional[int] = ...) -> None: ...

class TaskResponse(_message.Message):
    __slots__ = ("task_id", "agent_id", "accepted", "reason", "timestamp")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    AGENT_ID_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    agent_id: str
    accepted: bool
    reason: str
    timestamp: int
    def __init__(self, task_id: _Optional[str] = ..., agent_id: _Optional[str] = ..., accepted: bool = ..., reason: _Optional[str] = ..., timestamp: _Optional[int] = ...) -> None: ...

class RespondToTaskRequest(_message.Message):
    __slots__ = ("response",)
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    response: TaskResponse
    def __init__(self, response: _Optional[_Union[TaskResponse, _Mapping]] = ...) -> None: ...

class RespondToTaskResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class SubmitBidBatchRequest(_message.Message):
    __slots__ = ("bids", "batch_id", "partial_ok")
    BIDS_FIELD_NUMBER: _ClassVar[int]
    BATCH_ID_FIELD_NUMBER: _ClassVar[int]
    PARTIAL_OK_FIELD_NUMBER: _ClassVar[int]
    bids: _containers.RepeatedCompositeFieldContainer[_bid_pb2.Bid]
    batch_id: str
    partial_ok: bool
    def __init__(self, bids: _Optional[_Iterable[_Union[_bid_pb2.Bid, _Mapping]]] = ..., batch_id: _Optional[str] = ..., partial_ok: bool = ...) -> None: ...

class SubmitBidBatchResponse(_message.Message):
    __slots__ = ("acks", "success", "failed", "msg")
    ACKS_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    acks: _containers.RepeatedCompositeFieldContainer[_bid_pb2.BidSubmissionAck]
    success: int
    failed: int
    msg: str
    def __init__(self, acks: _Optional[_Iterable[_Union[_bid_pb2.BidSubmissionAck, _Mapping]]] = ..., success: _Optional[int] = ..., failed: _Optional[int] = ..., msg: _Optional[str] = ...) -> None: ...
