"""Type definitions for Subnet SDK."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Any, Dict, Optional, Tuple


@dataclass
class Task:
    """Represents a task to execute."""
    id: str
    intent_id: str
    type: str
    data: bytes
    metadata: Dict[str, Any]
    deadline: datetime
    created_at: datetime


@dataclass
class Result:
    """Represents task execution result."""
    data: bytes
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Intent:
    """Represents an intent for bidding."""
    id: str
    type: str
    description: str
    created_at: datetime


@dataclass
class Bid:
    """Represents a bid for an intent."""
    price: int
    currency: str = "PIN"
    metadata: Optional[Dict[str, Any]] = None


class ExecutionReportStatus(str, Enum):
    """Supported execution report statuses."""

    STATUS_UNSPECIFIED = "status_unspecified"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class ExecutionReport:
    """Payload emitted by agents when reporting task execution."""

    report_id: str
    assignment_id: str
    intent_id: str
    agent_id: Optional[str] = None
    status: ExecutionReportStatus = ExecutionReportStatus.SUCCESS
    result_data: Optional[bytes] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, str]] = None


@dataclass
class ExecutionReceipt:
    """Response returned by validators for execution reports."""

    report_id: str
    intent_id: str
    validator_id: str
    status: str
    message: Optional[str] = None
    received_at: Optional[datetime] = None
    endpoint: Optional[str] = None


@dataclass
class ValidatorEndpoint:
    """Validator discovery information from registry service."""

    id: str
    endpoint: str
    status: str
    last_seen: Optional[datetime] = None


class Handler(ABC):
    """Abstract base class for task handlers."""

    @abstractmethod
    async def execute(self, task: Task) -> Result:
        """Execute a task and return result."""
        pass


class BiddingStrategy(ABC):
    """Optional custom bidding strategy."""

    @abstractmethod
    def should_bid(self, intent: Intent) -> bool:
        """Return True if the agent should bid on the given intent."""

    @abstractmethod
    def calculate_bid(self, intent: Intent) -> Bid:
        """Produce a bid for the provided intent."""


class Callbacks(ABC):
    """Lifecycle callbacks emitted by the SDK."""

    async def on_start(self) -> None:  # pragma: no cover - default noop
        pass

    async def on_stop(self) -> None:  # pragma: no cover - default noop
        pass

    async def on_task_accepted(self, task: Task) -> None:  # pragma: no cover
        pass

    async def on_task_rejected(self, task: Task, reason: str) -> None:  # pragma: no cover
        pass

    async def on_task_completed(self, task: Task, result: Result) -> None:  # pragma: no cover
        pass

    async def on_report_submitted(self, report_id: str) -> None:  # pragma: no cover
        pass

    async def on_report_failed(self, report_id: str, error: str) -> None:  # pragma: no cover
        pass

    async def on_error(self, error: BaseException) -> None:  # pragma: no cover
        pass

    async def on_bid_submitted(self, intent_id: str, bid_id: str) -> None:  # pragma: no cover
        pass

    async def on_bid_failed(self, intent_id: str, bid_id: str, reason: str) -> None:  # pragma: no cover
        pass


class Metrics:
    """Metrics tracking for agents."""

    def __init__(self):
        self._tasks_completed = 0
        self._tasks_failed = 0
        self._total_bids = 0
        self._successful_bids = 0
        self._total_earnings = 0
        self._reports_submitted = 0
        self._reports_failed = 0
        self._lock = Lock()

    def record_task_success(self):
        """Record successful task completion."""
        with self._lock:
            self._tasks_completed += 1

    def record_task_failure(self):
        """Record task failure."""
        with self._lock:
            self._tasks_failed += 1

    def record_bid(self, success: bool):
        """Record bid attempt."""
        with self._lock:
            self._total_bids += 1
            if success:
                self._successful_bids += 1

    def add_earnings(self, amount: int):
        """Accumulate earnings."""
        with self._lock:
            self._total_earnings += amount

    def record_report_success(self):
        """Record successful execution report submission."""
        with self._lock:
            self._reports_submitted += 1

    def record_report_failure(self):
        """Record failed execution report submission."""
        with self._lock:
            self._reports_failed += 1

    def get_stats(self) -> Tuple[int, int, int, int]:
        """Get current task and bid statistics."""
        with self._lock:
            return (
                self._tasks_completed,
                self._tasks_failed,
                self._total_bids,
                self._successful_bids,
            )

    def report_counters(self) -> Tuple[int, int]:
        """Return execution report success/failure counters."""
        with self._lock:
            return self._reports_submitted, self._reports_failed

    def total_earnings(self) -> int:
        """Return accumulated earnings."""
        with self._lock:
            return self._total_earnings
