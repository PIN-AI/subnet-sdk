"""Core SDK implementation for Subnet agents."""

import asyncio
import base64
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse, urlunparse

from aiohttp import ClientError, ClientSession, ClientTimeout
from eth_account import Account
from eth_keys import keys
from web3 import Web3

from .grpc_transport import SigningConfig
from .matcher_client import MatcherClient
from .proto.subnet import matcher_service_pb2, bid_pb2
from .matcher_client import MatcherClient, ValidatorClient
from .proto.subnet import execution_report_pb2, service_pb2, report_pb2, matcher_pb2
from .types import (
    ExecutionReceipt,
    ExecutionReport,
    ExecutionReportStatus,
    Handler,
    Callbacks,
    BiddingStrategy,
    Intent,
    Metrics,
    Result,
    Task,
    ValidatorEndpoint,
)

logger = logging.getLogger(__name__)

DEFAULT_REPORT_TIMEOUT = 10  # seconds
DEFAULT_HEARTBEAT_INTERVAL = 30  # seconds
CHAIN_ADDRESS_METADATA_KEY = "chain_address"


@dataclass
class IdentityConfig:
    """Identity configuration for agents."""

    subnet_id: str
    agent_id: str
    validator_id: Optional[str] = None
    matcher_id: Optional[str] = None


@dataclass
class Config:
    """SDK configuration."""

    # Identity (REQUIRED - no defaults)
    identity: IdentityConfig

    # Network (REQUIRED)
    matcher_addr: str

    # Capabilities (REQUIRED)
    capabilities: List[str] = field(default_factory=list)
    intent_types: List[str] = field(default_factory=list)

    # Authentication
    private_key: Optional[str] = None
    chain_address: Optional[str] = None

    # Optional networking
    validator_addr: Optional[str] = None
    registry_addr: Optional[str] = None
    agent_endpoint: Optional[str] = None
    registry_heartbeat_interval: int = DEFAULT_HEARTBEAT_INTERVAL
    enable_matcher_stream: bool = True

    # Performance
    max_concurrent_tasks: int = 5
    task_timeout: int = 30  # seconds
    bid_timeout: int = 5  # seconds

    # Economics
    bidding_strategy: str = "fixed"
    min_bid_price: int = 100
    max_bid_price: int = 1000
    stake_amount: int = 0
    owner: Optional[str] = None

    # Other
    log_level: str = "INFO"
    data_dir: Optional[str] = None

    def validate(self) -> None:
        """Validate configuration."""
        if not self.identity.subnet_id:
            raise ValueError("subnet_id must be configured")
        if not self.identity.agent_id:
            raise ValueError("agent_id must be configured")

        key = self.private_key or ""
        if key:
            if key.startswith("0x") or key.startswith("0X"):
                key = key[2:]
            if len(key) != 64:
                raise ValueError("private_key must be 32 bytes (64 hex characters)")
            try:
                int(key, 16)
            except ValueError as exc:
                raise ValueError(
                    "private_key must be 32 bytes (64 hex characters)"
                ) from exc
            self.private_key = key

        if self.chain_address:
            addr = self.chain_address
            if not addr.startswith("0x") and not addr.startswith("0X"):
                addr = "0x" + addr
            if not Web3.is_address(addr):
                raise ValueError("chain_address must be a valid Ethereum address")
            self.chain_address = Web3.to_checksum_address(addr)

        if not self.matcher_addr:
            raise ValueError("matcher_addr must be configured")

        if not self.capabilities:
            raise ValueError("at least one capability must be configured")

        if self.registry_addr and not self.agent_endpoint:
            raise ValueError(
                "agent_endpoint must be configured when registry_addr is set"
            )

        if self.registry_heartbeat_interval <= 0:
            self.registry_heartbeat_interval = DEFAULT_HEARTBEAT_INTERVAL


class SDK:
    """Main SDK class for Subnet agents."""

    def __init__(self, config: Config):
        config.validate()
        self.config = config
        self.handler: Optional[Handler] = None
        self.metrics = Metrics()
        self._running = False
        self._account = None
        self._address = None
        self._session: Optional[ClientSession] = None
        self._registry_task: Optional[asyncio.Task] = None
        self._registry_stop: Optional[asyncio.Event] = None
        self._matcher_client: Optional[MatcherClient] = None
        self._matcher_task: Optional[asyncio.Task] = None
        self._intent_task: Optional[asyncio.Task] = None
        self._validator_client: Optional[ValidatorClient] = None
        self._callbacks: Optional[Callbacks] = None
        self._bidding_strategy: Optional[BiddingStrategy] = None

        if config.private_key:
            self._setup_auth()

        if self._address and config.chain_address:
            if Web3.to_checksum_address(self._address) != Web3.to_checksum_address(
                config.chain_address
            ):
                raise ValueError(
                    "chain_address does not match derived address from private_key"
                )
        elif config.chain_address and not self._address:
            self._address = Web3.to_checksum_address(config.chain_address)
        elif self._address:
            self.config.chain_address = self._address

        logging.basicConfig(level=getattr(logging, config.log_level, logging.INFO))
        logger.info("SDK initialized with agent_id: %s", self.get_agent_id())

    def _setup_auth(self) -> None:
        try:
            key_hex = self.config.private_key or ""
            if not key_hex:
                return
            self._account = Account.from_key("0x" + key_hex)
            self._address = self._account.address
            logger.info("Authentication setup with address: %s", self._address)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to setup authentication: %s", exc)
            raise ValueError(f"Invalid private key: {exc}") from exc

    def register_handler(self, handler: Handler) -> None:
        self.handler = handler
        logger.info("Handler registered")

    async def start(self) -> None:
        if self._running:
            raise RuntimeError("SDK already running")
        if not self.handler:
            raise RuntimeError("No handler registered")

        await self._ensure_session()
        try:
            await self._register_with_registry()
        except Exception:
            await self._close_session()
            raise

        await self._ensure_validator_client()
        self._running = True
        await self._start_matcher()
        await self._fire_callback("on_start")
        logger.info("SDK started: %s", self.get_agent_id())

    async def stop(self) -> None:
        if not self._running:
            raise RuntimeError("SDK not running")

        self._running = False
        await self._stop_matcher()
        await self._stop_registry()
        await self._close_validator_client()
        await self._close_session()
        await self._fire_callback("on_stop")
        logger.info("SDK stopped")

    def get_agent_id(self) -> str:
        return self.config.identity.agent_id

    def get_chain_address(self) -> Optional[str]:
        if self._address:
            return Web3.to_checksum_address(self._address)
        if self.config.chain_address:
            return Web3.to_checksum_address(self.config.chain_address)
        return None

    def _ensure_chain_metadata(
        self, metadata: Optional[Dict[str, Any]]
    ) -> Dict[str, str]:
        result: Dict[str, str] = {}
        if metadata:
            result = {str(k): str(v) for k, v in metadata.items()}

        address = self.get_chain_address()
        if address:
            result.setdefault(CHAIN_ADDRESS_METADATA_KEY, address)

        return result

    def get_subnet_id(self) -> str:
        return self.config.identity.subnet_id

    def get_address(self) -> Optional[str]:
        return self._address

    def get_capabilities(self) -> List[str]:
        return list(self.config.capabilities)

    def get_metrics(self) -> Metrics:
        return self.metrics

    def register_callbacks(self, callbacks: Callbacks) -> None:
        self._callbacks = callbacks

    def register_bidding_strategy(self, strategy: BiddingStrategy) -> None:
        self._bidding_strategy = strategy

    async def execute_task(self, task: Task) -> Result:
        if not self._running:
            raise RuntimeError("SDK not running")
        if not self.handler:
            raise RuntimeError("No handler registered")

        try:
            result = await asyncio.wait_for(
                self.handler.execute(task), timeout=self.config.task_timeout
            )
            if result.success:
                self.metrics.record_task_success()
            else:
                self.metrics.record_task_failure()
            await self._fire_callback("on_task_completed", task, result)
            return result
        except asyncio.TimeoutError:
            self.metrics.record_task_failure()
            error = asyncio.TimeoutError("task execution timeout")
            await self._fire_callback("on_error", error)
            return Result(data=b"", success=False, error=str(error))
        except Exception as exc:  # pragma: no cover - passthrough to caller
            self.metrics.record_task_failure()
            logger.error("Task execution failed: %s", exc)
            await self._fire_callback("on_error", exc)
            return Result(data=b"", success=False, error=str(exc))

    def sign(self, data: bytes) -> bytes:
        if not self._account:
            raise RuntimeError("No private key configured")
        try:
            digest = Web3.keccak(data)
            priv_key = keys.PrivateKey(bytes.fromhex(self.config.private_key))
            signature = priv_key.sign_msg_hash(digest)
            return signature.to_bytes()
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Failed to sign data: %s", exc)
            raise RuntimeError(f"Failed to sign data: {exc}") from exc

    async def discover_validators(self) -> List[ValidatorEndpoint]:
        if not self.config.registry_addr:
            raise RuntimeError("registry_addr not configured")

        session = await self._ensure_session()
        url = self._registry_url("/validators")

        try:
            async with session.get(url) as response:
                if response.status >= 300:
                    payload = await response.text()
                    raise RuntimeError(
                        f"fetch validators: registry returned {response.status}: {payload}"
                    )
                data = await response.json()
        except ClientError as exc:
            raise RuntimeError(f"fetch validators: {exc}") from exc

        validators: List[ValidatorEndpoint] = []
        for raw in data.get("validators", []):
            last_seen = raw.get("last_seen")
            last_seen_dt = (
                datetime.fromtimestamp(last_seen, tz=timezone.utc)
                if isinstance(last_seen, (int, float)) and last_seen > 0
                else None
            )
            validators.append(
                ValidatorEndpoint(
                    id=raw.get("id", ""),
                    endpoint=raw.get("endpoint", ""),
                    status=raw.get("status", "unknown"),
                    last_seen=last_seen_dt,
                )
            )
        return validators

    async def submit_execution_report(
        self, report: ExecutionReport, *, timeout: Optional[float] = None
    ) -> List[ExecutionReceipt]:
        if report is None:
            raise ValueError("execution report is required")

        report_id = (report.report_id or "").strip()
        if not report_id:
            raise ValueError("report_id is required")

        assignment_id = (report.assignment_id or "").strip()
        if not assignment_id:
            raise ValueError("assignment_id is required")

        intent_id = (report.intent_id or "").strip()
        if not intent_id:
            raise ValueError("intent_id is required")

        agent_id = (report.agent_id or "").strip() or self.get_agent_id()
        if not agent_id:
            raise ValueError("agent_id is required")

        status = report.status or ExecutionReportStatus.SUCCESS
        if isinstance(status, str):
            try:
                status = ExecutionReportStatus(status)
            except ValueError as exc:
                raise ValueError(f"invalid status: {status}") from exc

        report.metadata = self._ensure_chain_metadata(report.metadata)

        await self._ensure_validator_client()
        if self._validator_client is not None:
            return await self._submit_report_grpc(report, status)

        # Fallback HTTP path when validator gRPC endpoint未配置
        return await self._submit_report_http(report, agent_id, status, timeout)

    async def _register_with_registry(self) -> None:
        if not self.config.registry_addr:
            return

        session = await self._ensure_session()
        url = self._registry_url("/agents")
        payload = {
            "id": self.get_agent_id(),
            "capabilities": self.get_capabilities(),
            "endpoint": self.config.agent_endpoint,
        }

        try:
            async with session.post(url, json=payload) as response:
                if response.status >= 300:
                    body = await response.text()
                    raise RuntimeError(
                        f"registry registration failed: {response.status}: {body.strip()}"
                    )
        except ClientError as exc:
            raise RuntimeError(f"registry registration failed: {exc}") from exc

        self._registry_stop = asyncio.Event()
        self._registry_task = asyncio.create_task(self._heartbeat_loop())

    async def _stop_registry(self) -> None:
        if self._registry_stop is not None:
            self._registry_stop.set()

        if self._registry_task is not None:
            self._registry_task.cancel()
            try:
                await self._registry_task
            except asyncio.CancelledError:
                pass
            self._registry_task = None

        if self.config.registry_addr:
            session = await self._ensure_session()
            url = self._registry_url(f"/agents/{self.get_agent_id()}")
            try:
                async with session.delete(url) as response:
                    if response.status >= 300:
                        body = await response.text()
                        logger.warning(
                            "failed to unregister agent: %s %s",
                            response.status,
                            body.strip(),
                        )
            except (
                ClientError
            ) as exc:  # pragma: no cover - network failures are runtime specific
                logger.warning("failed to unregister agent: %s", exc)

        self._registry_stop = None

    async def _ensure_validator_client(self) -> None:
        if self._validator_client is not None:
            return
        target = self.config.validator_addr
        if not target:
            return

        signing_config = None
        if self.config.private_key:
            signing_config = SigningConfig(
                private_key_hex=self.config.private_key,
                chain_id=self.config.identity.subnet_id or "subnet",
            )

        self._validator_client = ValidatorClient(
            target,
            signing_config=signing_config,
        )

    async def _close_validator_client(self) -> None:
        if self._validator_client is not None:
            await self._validator_client.close()
            self._validator_client = None

    async def _start_matcher(self) -> None:
        if not self.config.enable_matcher_stream:
            return
        if not self.config.matcher_addr:
            return
        if self._matcher_client is not None:
            return

        signing_config = None
        if self.config.private_key:
            signing_config = SigningConfig(
                private_key_hex=self.config.private_key,
                chain_id=self.config.identity.subnet_id or "subnet",
            )

        self._matcher_client = MatcherClient(
            self.config.matcher_addr,
            signing_config=signing_config,
        )
        request = matcher_service_pb2.StreamTasksRequest(agent_id=self.get_agent_id())
        self._matcher_task = asyncio.create_task(self._task_stream_loop(request))

        if self._bidding_strategy and self._intent_task is None:
            intent_request = matcher_pb2.StreamIntentsRequest(
                subnet_id=self.config.identity.subnet_id,
                intent_types=self.config.intent_types,
            )
            self._intent_task = asyncio.create_task(
                self._intent_stream_loop(intent_request)
            )

    async def _stop_matcher(self) -> None:
        if self._matcher_task is not None:
            self._matcher_task.cancel()
            try:
                await self._matcher_task
            except asyncio.CancelledError:
                pass
            self._matcher_task = None

        if self._intent_task is not None:
            self._intent_task.cancel()
            try:
                await self._intent_task
            except asyncio.CancelledError:
                pass
            self._intent_task = None

        if self._matcher_client is not None:
            await self._matcher_client.close()
            self._matcher_client = None

    async def _task_stream_loop(
        self, request: matcher_service_pb2.StreamTasksRequest
    ) -> None:
        assert self._matcher_client is not None
        logger.debug("Starting task stream loop for agent_id=%s", request.agent_id)
        try:
            logger.debug("Calling matcher_client.stream_tasks()...")
            async for task_proto in self._matcher_client.stream_tasks(request):
                await self._handle_execution_task(task_proto)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover - runtime network failure
            logger.error("Matcher task stream ended: %s", exc)
            await self._fire_callback("on_error", exc)

    async def _intent_stream_loop(
        self, request: matcher_pb2.StreamIntentsRequest
    ) -> None:
        assert self._matcher_client is not None
        logger.debug("Starting intent stream loop for subnet_id=%s intent_types=%s",
                    request.subnet_id, request.intent_types)
        try:
            logger.debug("Calling matcher_client.stream_intents()...")
            async for update in self._matcher_client.stream_intents(request):
                await self._handle_intent_update(update)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover - runtime network failure
            logger.error("Matcher intent stream ended: %s", exc)
            await self._fire_callback("on_error", exc)

    async def _handle_intent_update(
        self, update: matcher_pb2.MatcherIntentUpdate
    ) -> None:
        if not self._bidding_strategy or self._matcher_client is None:
            return

        created_at = (
            datetime.fromtimestamp(update.timestamp, tz=timezone.utc)
            if update.timestamp
            else datetime.now(timezone.utc)
        )
        intent = Intent(
            id=update.intent_id,
            type=update.update_type or "unknown",
            description="",
            created_at=created_at,
        )

        try:
            if not self._bidding_strategy.should_bid(intent):
                return

            bid_info = self._bidding_strategy.calculate_bid(intent)
        except Exception as exc:  # pragma: no cover - user strategy errors
            logger.exception(
                "Bidding strategy failed for intent %s: %s", intent.id, exc
            )
            await self._fire_callback("on_error", exc)
            return

        # Generate 32-byte (64 hex chars) bid ID for RootLayer compatibility
        bid_id = "0x" + uuid.uuid4().hex + uuid.uuid4().hex
        bid_metadata = self._ensure_chain_metadata(getattr(bid_info, "metadata", None))

        bid_pb = bid_pb2.Bid(
            bid_id=bid_id,
            intent_id=intent.id,
            agent_id=self.get_agent_id(),
            price=bid_info.price,
            token=bid_info.currency,
            submitted_at=int(time.time()),
            nonce=uuid.uuid4().hex,
            metadata=bid_metadata,
        )

        request = matcher_pb2.SubmitBidRequest(bid=bid_pb)
        try:
            response = await self._matcher_client.submit_bid(request)
            ack = response.ack if response is not None else None
            accepted = ack.accepted if ack is not None else True
            reason = ack.reason if ack is not None else ""
        except Exception as exc:  # pragma: no cover
            self.metrics.record_bid(False)
            await self._fire_callback("on_bid_failed", intent.id, bid_id, str(exc))
            logger.warning("SubmitBid failed for intent %s: %s", intent.id, exc)
            return

        self.metrics.record_bid(accepted)
        if accepted:
            await self._fire_callback("on_bid_submitted", intent.id, bid_id)
        else:
            await self._fire_callback(
                "on_bid_failed",
                intent.id,
                bid_id,
                reason or "matcher rejected",
            )

    async def _handle_execution_task(
        self, task_proto: matcher_service_pb2.ExecutionTask
    ) -> None:
        if not self._running:
            return
        if not self.handler:
            logger.warning(
                "Received task %s but no handler is registered", task_proto.task_id
            )
            return
        if self._matcher_client is None:
            return

        created_at = (
            datetime.fromtimestamp(task_proto.created_at, tz=timezone.utc)
            if task_proto.created_at
            else datetime.now(timezone.utc)
        )
        deadline = (
            datetime.fromtimestamp(task_proto.deadline, tz=timezone.utc)
            if task_proto.deadline
            else created_at
        )

        task = Task(
            id=task_proto.task_id,
            intent_id=task_proto.intent_id,
            type=task_proto.intent_type,
            data=task_proto.intent_data,
            metadata={"bid_id": task_proto.bid_id},
            deadline=deadline,
            created_at=created_at,
        )

        response = matcher_pb2.RespondToTaskRequest(
            response=matcher_pb2.TaskResponse(
                task_id=task.id,
                agent_id=self.get_agent_id(),
                accepted=True,
                timestamp=int(time.time()),
            )
        )

        try:
            await self._matcher_client.respond_to_task(response)
        except Exception as exc:  # pragma: no cover
            logger.warning(
                "Failed to acknowledge task %s with matcher: %s",
                task.id,
                exc,
            )
            await self._fire_callback("on_task_rejected", task, str(exc))
            return

        await self._fire_callback("on_task_accepted", task)

        result = await self.execute_task(task)

        report = ExecutionReport(
            report_id=str(uuid.uuid4()),
            assignment_id=task_proto.task_id,
            intent_id=task_proto.intent_id,
            agent_id=self.get_agent_id(),
            status=(
                ExecutionReportStatus.SUCCESS
                if result.success
                else ExecutionReportStatus.FAILED
            ),
            result_data=result.data if result.data else b"",
            metadata={"bid_id": task_proto.bid_id},
        )

        if result.error and report.metadata is not None:
            report.metadata["error"] = result.error
        if result.metadata:
            report.metadata.update({str(k): str(v) for k, v in result.metadata.items()})

        try:
            await self.submit_execution_report(report)
        except Exception as exc:  # pragma: no cover
            logger.error(
                "Failed to submit execution report %s: %s",
                report.report_id,
                exc,
            )

    async def _submit_report_grpc(
        self, report: ExecutionReport, status: ExecutionReportStatus
    ) -> List[ExecutionReceipt]:
        assert self._validator_client is not None
        report.metadata = self._ensure_chain_metadata(report.metadata)
        proto_request = self._build_execution_report_proto(report, status)

        try:
            receipt_pb = await self._validator_client.submit_execution_report(
                proto_request
            )
        except Exception as exc:  # pragma: no cover - network/runtime failure
            self.metrics.record_report_failure()
            await self._fire_callback("on_report_failed", report.report_id, str(exc))
            raise RuntimeError(f"validator submission failed: {exc}") from exc

        self.metrics.record_report_success()
        receipt = self._convert_receipt_proto(receipt_pb, self.config.validator_addr)
        await self._fire_callback("on_report_submitted", report.report_id)
        return [receipt]

    async def _submit_report_http(
        self,
        report: ExecutionReport,
        agent_id: str,
        status: ExecutionReportStatus,
        timeout: Optional[float],
    ) -> List[ExecutionReceipt]:
        timestamp = report.timestamp or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        metadata = self._ensure_chain_metadata(report.metadata)
        report.metadata = metadata

        payload: Dict[str, Any] = {
            "report_id": report.report_id,
            "assignment_id": report.assignment_id,
            "intent_id": report.intent_id,
            "agent_id": agent_id,
            "status": status.value,
            "timestamp": int(timestamp.timestamp()),
        }
        if metadata:
            payload["metadata"] = metadata
        if report.result_data:
            payload["result_data"] = base64.b64encode(report.result_data).decode()

        endpoints, endpoint_errors = await self._validator_report_endpoints()
        if not endpoints:
            if endpoint_errors:
                combined = "; ".join(str(err) for err in endpoint_errors)
                await self._fire_callback(
                    "on_report_failed", report.report_id, combined
                )
                raise RuntimeError(f"no validator endpoints available: {combined}")
            await self._fire_callback(
                "on_report_failed", report.report_id, "no validator endpoints available"
            )
            raise RuntimeError("no validator endpoints available")

        receipts: List[ExecutionReceipt] = []
        submit_errors: List[str] = []

        for endpoint in endpoints:
            try:
                receipt = await self._post_execution_report(endpoint, payload, timeout)
                self.metrics.record_report_success()
                receipt.endpoint = endpoint
                receipts.append(receipt)
            except Exception as exc:  # pragma: no cover
                self.metrics.record_report_failure()
                logger.warning(
                    "execution report submission failed for %s: %s", endpoint, exc
                )
                submit_errors.append(f"{endpoint}: {exc}")

        if not receipts:
            message = (
                submit_errors[0]
                if submit_errors
                else "validator submissions returned no receipts"
            )
            await self._fire_callback("on_report_failed", report.report_id, message)
            raise RuntimeError(message)

        if submit_errors:
            logger.warning(
                "execution report partially successful: %s", "; ".join(submit_errors)
            )

        await self._fire_callback("on_report_submitted", report.report_id)
        return receipts

    def _build_execution_report_proto(
        self, report: ExecutionReport, status: ExecutionReportStatus
    ) -> execution_report_pb2.ExecutionReport:
        timestamp = report.timestamp or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        status_map = {
            ExecutionReportStatus.STATUS_UNSPECIFIED: execution_report_pb2.ExecutionReport.STATUS_UNSPECIFIED,
            ExecutionReportStatus.SUCCESS: execution_report_pb2.ExecutionReport.SUCCESS,
            ExecutionReportStatus.FAILED: execution_report_pb2.ExecutionReport.FAILED,
            ExecutionReportStatus.PARTIAL: execution_report_pb2.ExecutionReport.PARTIAL,
        }

        return execution_report_pb2.ExecutionReport(
            report_id=report.report_id,
            assignment_id=report.assignment_id,
            intent_id=report.intent_id,
            agent_id=report.agent_id or self.get_agent_id(),
            status=status_map.get(status, execution_report_pb2.ExecutionReport.SUCCESS),
            result_data=report.result_data or b"",
            timestamp=int(timestamp.timestamp()),
        )

    def _convert_receipt_proto(
        self, receipt: report_pb2.Receipt, endpoint: Optional[str]
    ) -> ExecutionReceipt:
        received_at = (
            datetime.fromtimestamp(receipt.received_ts, tz=timezone.utc)
            if receipt.received_ts
            else None
        )
        return ExecutionReceipt(
            report_id=receipt.report_id or "",
            intent_id=receipt.intent_id or "",
            validator_id=receipt.validator_id or "",
            status=receipt.status or "",
            message=receipt.phase or None,
            received_at=received_at,
            endpoint=endpoint,
        )

    async def _fire_callback(self, method: str, *args) -> None:
        if not self._callbacks:
            return
        callback = getattr(self._callbacks, method, None)
        if callback is None:
            return
        try:
            result = callback(*args)
            if asyncio.iscoroutine(result):
                await result
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Callback %s failed: %s", method, exc)

    async def _heartbeat_loop(self) -> None:
        assert self._registry_stop is not None
        interval = max(
            self.config.registry_heartbeat_interval, DEFAULT_HEARTBEAT_INTERVAL
        )

        try:
            while not self._registry_stop.is_set():
                try:
                    await asyncio.wait_for(self._registry_stop.wait(), timeout=interval)
                    break
                except asyncio.TimeoutError:
                    await self._send_heartbeat()
        except asyncio.CancelledError:
            return

    async def _send_heartbeat(self) -> None:
        if not self.config.registry_addr:
            return

        session = await self._ensure_session()
        url = self._registry_url(f"/agents/{self.get_agent_id()}/heartbeat")
        try:
            async with session.post(url) as response:
                if response.status >= 300:
                    body = await response.text()
                    logger.warning(
                        "registry heartbeat unexpected status %s: %s",
                        response.status,
                        body.strip(),
                    )
        except ClientError as exc:  # pragma: no cover
            logger.warning("registry heartbeat failed: %s", exc)

    async def _post_execution_report(
        self, endpoint: str, payload: Dict[str, Any], timeout: Optional[float]
    ) -> ExecutionReceipt:
        session = await self._ensure_session()
        request_timeout = timeout if timeout and timeout > 0 else DEFAULT_REPORT_TIMEOUT
        try:
            async with session.post(
                endpoint,
                json=payload,
                timeout=ClientTimeout(total=request_timeout),
            ) as response:
                if response.status >= 300:
                    body = await response.text()
                    raise RuntimeError(
                        f"validator returned {response.status}: {body.strip()}"
                    )
                data = await response.json()
        except asyncio.TimeoutError as exc:
            raise RuntimeError("execution report request timed out") from exc
        except ClientError as exc:
            raise RuntimeError(f"submit report: {exc}") from exc

        receipt = ExecutionReceipt(
            report_id=data.get("report_id", ""),
            intent_id=data.get("intent_id", ""),
            validator_id=data.get("validator_id", ""),
            status=data.get("status", ""),
            message=data.get("message"),
        )
        received_ts = data.get("received_ts")
        if isinstance(received_ts, (int, float)) and received_ts > 0:
            receipt.received_at = datetime.fromtimestamp(received_ts, tz=timezone.utc)
        return receipt

    async def _validator_report_endpoints(self) -> Tuple[List[str], List[Exception]]:
        endpoints: List[str] = []
        errors: List[Exception] = []
        seen = set()

        def add_endpoint(raw: str) -> None:
            try:
                url = self._build_execution_report_url(raw)
            except Exception as exc:  # pragma: no cover - defensive
                errors.append(exc)
                return
            if not url or url in seen:
                return
            seen.add(url)
            endpoints.append(url)

        if self.config.registry_addr:
            try:
                validators = await self.discover_validators()
                for validator in validators:
                    add_endpoint(validator.endpoint)
            except (
                Exception
            ) as exc:  # pragma: no cover - network failures are runtime specific
                errors.append(exc)

        if self.config.validator_addr:
            add_endpoint(self.config.validator_addr)

        if len(endpoints) > 1:
            endpoints.sort()

        return endpoints, errors

    def _build_execution_report_url(self, endpoint: str) -> str:
        trimmed = (endpoint or "").strip()
        if not trimmed:
            return ""
        if not trimmed.startswith("http://") and not trimmed.startswith("https://"):
            trimmed = "http://" + trimmed

        parsed = urlparse(trimmed)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"invalid validator endpoint: {endpoint}")

        path = parsed.path.rstrip("/")
        if not path or path == "/":
            path = "/api/v1/execution-report"
        elif path.endswith("/api/v1/execution-report"):
            path = path
        else:
            path = f"{path}/api/v1/execution-report"

        rebuilt = parsed._replace(path=path, params="", query="", fragment="")
        return urlunparse(rebuilt)

    def _registry_url(self, path: str) -> str:
        base = (self.config.registry_addr or "").rstrip("/")
        if not base:
            return path
        if not base.startswith("http://") and not base.startswith("https://"):
            base = "http://" + base
        if not path.startswith("/"):
            path = "/" + path
        return base + path

    async def _ensure_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = ClientSession(timeout=ClientTimeout(total=None))
        return self._session

    async def _close_session(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None
