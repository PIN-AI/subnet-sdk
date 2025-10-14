import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from eth_account import Account
from web3 import Web3
from eth_keys import keys

from subnet_sdk.grpc_transport import SigningConfig, SigningInterceptor
from subnet_sdk.matcher_client import MatcherClient

from subnet_sdk import (
    Config,
    ConfigBuilder,
    ExecutionReport,
    ExecutionReportStatus,
    IdentityConfig,
    SDK,
)


def _base_config(**overrides) -> Config:
    config = Config(
        identity=IdentityConfig(subnet_id="subnet-1", agent_id="agent-1"),
        matcher_addr="matcher:8090",
        capabilities=["compute"],
        **overrides,
    )
    config.validate()
    return config


def test_config_private_key_normalization():
    raw_key = "0x" + "ab" * 32
    config = _base_config(private_key=raw_key)

    assert config.private_key == "ab" * 32


def test_config_chain_address_normalization():
    config = _base_config(chain_address="0xABC1230000000000000000000000000000000000")

    assert config.chain_address == Web3.to_checksum_address(
        "0xABC1230000000000000000000000000000000000"
    )


def test_sign_keccak_parity():
    key = "11" * 32
    config = _base_config(private_key=key)
    sdk = SDK(config)

    payload = b"sign-me"
    signature = sdk.sign(payload)

    expected = (
        keys.PrivateKey(bytes.fromhex(key))
        .sign_msg_hash(Web3.keccak(payload))
        .to_bytes()
    )
    assert signature == expected


def test_build_execution_report_url_normalizes_host():
    sdk = SDK(_base_config())

    url = sdk._build_execution_report_url("validator:8080")
    assert url == "http://validator:8080/api/v1/execution-report"


def test_build_execution_report_url_preserves_path():
    sdk = SDK(_base_config())

    url = sdk._build_execution_report_url("https://validator:8080/custom")
    assert url == "https://validator:8080/custom/api/v1/execution-report"


def test_registry_url_normalizes_scheme():
    config = _base_config(registry_addr="registry:9000", agent_endpoint="agent:7000")
    sdk = SDK(config)

    assert sdk._registry_url("/agents") == "http://registry:9000/agents"


def test_submit_execution_report_requires_endpoints():
    sdk = SDK(_base_config())
    report = ExecutionReport(
        report_id="report-1",
        assignment_id="assignment-1",
        intent_id="intent-1",
        status=ExecutionReportStatus.SUCCESS,
        timestamp=datetime.now(timezone.utc),
    )

    with pytest.raises(RuntimeError, match="no validator endpoints available"):
        asyncio.run(sdk.submit_execution_report(report))


def test_signing_interceptor_metadata_contains_expected_fields():
    config = SigningConfig(private_key_hex="aa" * 32, chain_id="subnet-test")
    interceptor = SigningInterceptor(config)

    metadata = asyncio.run(
        interceptor.build_metadata("/test.Service/Method", {"foo": "bar"})
    )
    md = dict(metadata)

    assert md["x-signer-id"].startswith("0x")
    assert md["x-chain-id"] == "subnet-test"
    assert len(md["x-signature"]) == 130  # 65 bytes hex encoded
    assert md["x-nonce"]


def test_matcher_client_can_be_created_and_closed():
    async def _run():
        client = MatcherClient(
            "localhost:50051",
            signing_config=SigningConfig(private_key_hex="bb" * 32),
        )
        await client.close()

    asyncio.run(_run())


def test_ensure_chain_metadata_includes_chain_address():
    key = "22" * 32
    config = _base_config(private_key=key)
    sdk = SDK(config)

    metadata = sdk._ensure_chain_metadata({})
    assert metadata["chain_address"] == sdk.get_chain_address()


def test_chain_address_mismatch_raises():
    key = "33" * 32
    mismatched = "0x4444444444444444444444444444444444444444"
    config = _base_config(private_key=key, chain_address=mismatched)

    with pytest.raises(ValueError, match="chain_address does not match"):  # noqa: PT012
        SDK(config)
