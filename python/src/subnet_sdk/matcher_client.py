
"""Async gRPC clients for matcher and validator services."""

from __future__ import annotations

from typing import AsyncIterator, Optional, Sequence, Tuple

from .grpc_transport import (
    SigningConfig,
    SigningInterceptor,
    create_insecure_channel,
    create_secure_channel,
)
from .proto.subnet import matcher_service_pb2_grpc
from .proto.subnet import matcher_service_pb2
from .proto.subnet import service_pb2_grpc
from .proto.subnet import execution_report_pb2
from .proto.subnet import validator_pb2


class MatcherClient:
    """Async client for subnet MatcherService."""

    def __init__(
        self,
        target: str,
        *,
        secure: bool = False,
        signing_config: Optional[SigningConfig] = None,
        channel_options: Optional[Sequence[Tuple[str, str]]] = None,
    ) -> None:
        self._signer = SigningInterceptor(signing_config) if signing_config else None
        if secure:
            channel = create_secure_channel(target, options=channel_options)
        else:
            channel = create_insecure_channel(target, options=channel_options)
        self._channel = channel
        self._stub = matcher_service_pb2_grpc.MatcherServiceStub(self._channel)

    async def close(self) -> None:
        await self._channel.close()

    async def submit_bid(
        self, request: matcher_service_pb2.SubmitBidRequest
    ) -> matcher_service_pb2.SubmitBidResponse:
        metadata = await self._metadata("/subnet.v1.MatcherService/SubmitBid", request)
        return await self._stub.SubmitBid(request, metadata=metadata)

    async def stream_intents(
        self, request: matcher_service_pb2.StreamIntentsRequest
    ) -> AsyncIterator[matcher_service_pb2.MatcherIntentUpdate]:
        metadata = await self._metadata("/subnet.v1.MatcherService/StreamIntents", request)
        call = self._stub.StreamIntents(request, metadata=metadata)
        async for update in call:
            yield update

    async def stream_tasks(
        self, request: matcher_service_pb2.StreamTasksRequest
    ) -> AsyncIterator[matcher_service_pb2.ExecutionTask]:
        metadata = await self._metadata("/subnet.v1.MatcherService/StreamTasks", request)
        call = self._stub.StreamTasks(request, metadata=metadata)
        async for task in call:
            yield task

    async def respond_to_task(
        self, request: matcher_service_pb2.RespondToTaskRequest
    ) -> matcher_service_pb2.RespondToTaskResponse:
        metadata = await self._metadata("/subnet.v1.MatcherService/RespondToTask", request)
        return await self._stub.RespondToTask(request, metadata=metadata)

    async def _metadata(self, method: str, request) -> Optional[Sequence[Tuple[str, str]]]:
        if not self._signer:
            return None
        return await self._signer.build_metadata(method, request)


class ValidatorClient:
    """Async client for subnet ValidatorService."""

    def __init__(
        self,
        target: str,
        *,
        secure: bool = False,
        signing_config: Optional[SigningConfig] = None,
        channel_options: Optional[Sequence[Tuple[str, str]]] = None,
    ) -> None:
        self._signer = SigningInterceptor(signing_config) if signing_config else None
        if secure:
            channel = create_secure_channel(target, options=channel_options)
        else:
            channel = create_insecure_channel(target, options=channel_options)
        self._channel = channel
        self._stub = service_pb2_grpc.ValidatorServiceStub(self._channel)

    async def close(self) -> None:
        await self._channel.close()

    async def submit_execution_report(
        self, request: execution_report_pb2.ExecutionReport
    ) -> service_pb2.Receipt:
        metadata = await self._metadata("/subnet.v1.ValidatorService/SubmitExecutionReport", request)
        return await self._stub.SubmitExecutionReport(request, metadata=metadata)

    async def get_validator_set(
        self, request: service_pb2.GetCheckpointRequest
    ) -> validator_pb2.ValidatorSet:
        metadata = await self._metadata("/subnet.v1.ValidatorService/GetValidatorSet", request)
        return await self._stub.GetValidatorSet(request, metadata=metadata)

    async def _metadata(self, method: str, request) -> Optional[Sequence[Tuple[str, str]]]:
        if not self._signer:
            return None
        return await self._signer.build_metadata(method, request)
