"""gRPC utilities for matcher / validator clients.

Provides:
  * SigningInterceptor: attaches signature metadata to outbound RPC calls.
  * channel_factory: helper for creating aio channels with common options.
"""

from __future__ import annotations

import asyncio
import json
import secrets
import time
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence, Tuple

import grpc
from eth_account import Account
from eth_keys import keys
from google.protobuf.json_format import MessageToDict
from grpc.aio import (  # type: ignore[attr-defined]
    ClientCallDetails,
    UnaryUnaryClientInterceptor,
    UnaryStreamClientInterceptor,
    StreamUnaryClientInterceptor,
    StreamStreamClientInterceptor,
)
from web3 import Web3

# Metadata keys must match the Go implementation under
# subnet/internal/grpc/interceptors/auth.go
_SIGNATURE_KEY = "x-signature"
_SIGNER_ID_KEY = "x-signer-id"
_TIMESTAMP_KEY = "x-timestamp"
_NONCE_KEY = "x-nonce"
_CHAIN_ID_KEY = "x-chain-id"


@dataclass
class SigningConfig:
    """Configuration for metadata signing."""

    private_key_hex: str
    chain_id: str = "subnet-local"


def _now_unix() -> int:
    return int(time.time())


def _generate_nonce() -> str:
    # 16 bytes -> 32 hex chars, plenty for replay protection
    return secrets.token_hex(16)


def _canonical_json(chain_id: str, method: str, timestamp: int, nonce: str, request: Optional[Any]) -> bytes:
    payload: Mapping[str, Any]
    body: Mapping[str, Any]

    if request is None:
        body = {}
    elif hasattr(request, "DESCRIPTOR"):
        # Protobuf message -> deterministic JSON (keep field names)
        body = MessageToDict(request, preserving_proto_field_name=True)
    else:
        body = request if isinstance(request, Mapping) else {"value": request}

    payload = {
        "chain_id": chain_id,
        "method": method,
        "timestamp": timestamp,
        "nonce": nonce,
        "request": body or None,
    }

    # Remove "request" when None to match Go struct tag `omitempty`
    if payload["request"] is None:
        payload = {k: v for k, v in payload.items() if k != "request"}

    return json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")


class _ClientCallDetails(ClientCallDetails):
    """Lightweight wrapper to augment gRPC metadata."""

    def __init__(
        self,
        method: str,
        timeout: Optional[float],
        metadata: Optional[Sequence[Tuple[str, str]]],
        credentials: Optional[grpc.CallCredentials],
        wait_for_ready: Optional[bool],
        compression: Optional[grpc.Compression],
    ) -> None:
        self.method = method
        self.timeout = timeout
        self.metadata = metadata
        self.credentials = credentials
        self.wait_for_ready = wait_for_ready
        self.compression = compression


class SigningInterceptor(
    UnaryUnaryClientInterceptor,
    UnaryStreamClientInterceptor,
    StreamUnaryClientInterceptor,
    StreamStreamClientInterceptor,
):
    """Client interceptor that signs requests and injects metadata."""

    def __init__(self, config: SigningConfig) -> None:
        if len(config.private_key_hex) != 64:
            raise ValueError("private key must be 64 hex characters")

        self._config = config
        self._private_key = keys.PrivateKey(bytes.fromhex(config.private_key_hex))
        self._address = Account.from_key("0x" + config.private_key_hex).address

    async def intercept_unary_unary(self, continuation, client_call_details, request):
        metadata = await self.build_metadata(client_call_details.method, request)
        new_details = self._augment_details(client_call_details, metadata)
        return await continuation(new_details, request)

    async def intercept_unary_stream(self, continuation, client_call_details, request):
        metadata = await self.build_metadata(client_call_details.method, request)
        new_details = self._augment_details(client_call_details, metadata)
        return await continuation(new_details, request)

    async def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        metadata = await self.build_metadata(client_call_details.method, None)
        new_details = self._augment_details(client_call_details, metadata)
        return await continuation(new_details, request_iterator)

    async def intercept_stream_stream(self, continuation, client_call_details, request_iterator):
        metadata = await self.build_metadata(client_call_details.method, None)
        new_details = self._augment_details(client_call_details, metadata)
        return await continuation(new_details, request_iterator)

    def _augment_details(
        self,
        details: ClientCallDetails,
        metadata: Sequence[Tuple[str, str]],
    ) -> ClientCallDetails:
        merged = []
        if details.metadata:
            merged.extend(details.metadata)
        merged.extend(metadata)
        return _ClientCallDetails(
            method=details.method,
            timeout=details.timeout,
            metadata=tuple(merged),
            credentials=details.credentials,
            wait_for_ready=getattr(details, "wait_for_ready", None),
            compression=getattr(details, "compression", None),
        )

    async def build_metadata(
        self,
        method: str,
        request: Optional[Any],
    ) -> Sequence[Tuple[str, str]]:
        timestamp = _now_unix()
        nonce = _generate_nonce()
        canonical = _canonical_json(self._config.chain_id, method, timestamp, nonce, request)
        digest = Web3.keccak(canonical)
        signature = self._private_key.sign_msg_hash(digest).to_bytes().hex()

        return (
            (_SIGNATURE_KEY, signature),
            (_SIGNER_ID_KEY, self._address),
            (_TIMESTAMP_KEY, str(timestamp)),
            (_NONCE_KEY, nonce),
            (_CHAIN_ID_KEY, self._config.chain_id),
        )


def create_secure_channel(
    target: str,
    *,
    root_certificates: Optional[bytes] = None,
    private_key: Optional[bytes] = None,
    certificate_chain: Optional[bytes] = None,
    options: Optional[Iterable[Tuple[str, str]]] = None,
) -> grpc.aio.Channel:
    """Create an aio secure channel with optional custom certificates."""

    creds = grpc.ssl_channel_credentials(
        root_certificates=root_certificates,
        private_key=private_key,
        certificate_chain=certificate_chain,
    )
    return grpc.aio.secure_channel(target, creds, options=options)


def create_insecure_channel(
    target: str,
    *,
    options: Optional[Iterable[Tuple[str, str]]] = None,
) -> grpc.aio.Channel:
    return grpc.aio.insecure_channel(target, options=options)


def intercept_channel(channel: grpc.aio.Channel, *interceptors: grpc.aio.ClientInterceptor) -> grpc.aio.Channel:
    if interceptors:
        return grpc.aio.intercept_channel(channel, *interceptors)
    return channel


async def close_channel(channel: grpc.aio.Channel) -> None:
    await channel.close()
