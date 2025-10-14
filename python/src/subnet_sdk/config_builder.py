"""
Configuration builder for Subnet SDK.
"""

from typing import Optional

from .sdk import Config, IdentityConfig


class ConfigBuilder:
    """Fluent API for building SDK configuration."""

    def __init__(self):
        """Initialize builder with minimal defaults."""
        self._config = Config(
            identity=IdentityConfig(subnet_id="", agent_id=""),
            matcher_addr="",
            capabilities=[],
            intent_types=[],
        )

    def with_subnet_id(self, subnet_id: str) -> "ConfigBuilder":
        """Set subnet ID (REQUIRED)."""
        self._config.identity.subnet_id = subnet_id
        return self

    def with_agent_id(self, agent_id: str) -> "ConfigBuilder":
        """Set agent ID (REQUIRED)."""
        self._config.identity.agent_id = agent_id
        return self

    def with_private_key(self, private_key: str) -> "ConfigBuilder":
        """Set private key for signing."""
        self._config.private_key = private_key
        return self

    def with_chain_address(self, chain_address: str) -> "ConfigBuilder":
        """Set chain address when using an external signer."""
        self._config.chain_address = chain_address
        return self

    def with_matcher_addr(self, addr: str) -> "ConfigBuilder":
        """Set matcher address (REQUIRED)."""
        self._config.matcher_addr = addr
        return self

    def with_validator_addr(self, addr: str) -> "ConfigBuilder":
        """Set validator address."""
        self._config.validator_addr = addr
        return self

    def with_capabilities(self, *capabilities: str) -> "ConfigBuilder":
        """Set agent capabilities (REQUIRED - at least one)."""
        self._config.capabilities = list(capabilities)
        return self

    def with_intent_types(self, *intent_types: str) -> "ConfigBuilder":
        """Set matcher intent types filter for bidding."""
        self._config.intent_types = list(intent_types)
        return self

    def add_capability(self, capability: str) -> "ConfigBuilder":
        """Add a single capability."""
        self._config.capabilities.append(capability)
        return self

    def with_registry_addr(self, addr: str) -> "ConfigBuilder":
        """Set registry service address."""
        self._config.registry_addr = addr
        return self

    def with_agent_endpoint(self, endpoint: str) -> "ConfigBuilder":
        """Set externally reachable agent endpoint (required for registry)."""
        self._config.agent_endpoint = endpoint
        return self

    def with_registry_heartbeat_interval(self, interval: int) -> "ConfigBuilder":
        """Set registry heartbeat interval in seconds."""
        self._config.registry_heartbeat_interval = interval
        return self

    def with_task_timeout(self, timeout: int) -> "ConfigBuilder":
        """Set task timeout in seconds."""
        self._config.task_timeout = timeout
        return self

    def with_bid_timeout(self, timeout: int) -> "ConfigBuilder":
        """Set bid timeout in seconds."""
        self._config.bid_timeout = timeout
        return self

    def with_max_concurrent_tasks(self, max_tasks: int) -> "ConfigBuilder":
        """Set maximum concurrent tasks."""
        self._config.max_concurrent_tasks = max_tasks
        return self

    def with_bidding_strategy(
        self,
        strategy: str,
        min_price: int,
        max_price: int
    ) -> "ConfigBuilder":
        """Set bidding strategy and price range."""
        self._config.bidding_strategy = strategy
        self._config.min_bid_price = min_price
        self._config.max_bid_price = max_price
        return self

    def with_stake_amount(self, amount: int) -> "ConfigBuilder":
        """Set stake amount."""
        self._config.stake_amount = amount
        return self

    def with_owner(self, owner: str) -> "ConfigBuilder":
        """Set owner address."""
        self._config.owner = owner
        return self

    def with_log_level(self, level: str) -> "ConfigBuilder":
        """Set logging level."""
        self._config.log_level = level
        return self

    def with_data_dir(self, dir: str) -> "ConfigBuilder":
        """Set data directory."""
        self._config.data_dir = dir
        return self

    def build(self) -> Config:
        """Build and validate configuration."""
        self._config.validate()
        return self._config
