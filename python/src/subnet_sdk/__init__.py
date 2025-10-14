"""
Subnet SDK for Python

A Python SDK for building agents that interact with the Subnet protocol.
"""

from .sdk import SDK, Config, IdentityConfig
from .types import (
    Task,
    Result,
    Intent,
    Bid,
    Handler,
    BiddingStrategy,
    Callbacks,
    Metrics,
    ExecutionReport,
    ExecutionReceipt,
    ExecutionReportStatus,
    ValidatorEndpoint,
)
from .config_builder import ConfigBuilder
from .grpc_transport import (
    SigningConfig,
    SigningInterceptor,
    create_insecure_channel,
    create_secure_channel,
    close_channel,
)
from .matcher_client import MatcherClient, ValidatorClient

__version__ = "0.1.0"

__all__ = [
    "SDK",
    "Config",
    "IdentityConfig",
    "ConfigBuilder",
    "SigningConfig",
    "SigningInterceptor",
    "create_insecure_channel",
    "create_secure_channel",
    "close_channel",
    "MatcherClient",
    "ValidatorClient",
    "Task",
    "Result",
    "Intent",
    "Bid",
    "Handler",
    "BiddingStrategy",
    "Callbacks",
    "Metrics",
    "ExecutionReport",
    "ExecutionReceipt",
    "ExecutionReportStatus",
    "ValidatorEndpoint",
]
