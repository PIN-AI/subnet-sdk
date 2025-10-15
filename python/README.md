# Subnet SDK for Python

Python SDK for building agents that interact with the Subnet protocol.

Bids and execution reports automatically include `metadata["chain_address"]` when a chain address is configured or derived from the private key, enabling on-chain verification by matchers and validators.

## Installation

```bash
pip install subnet-sdk
```

Or from source:

```bash
cd python
pip install -e .
```

## Quick Start

```python
import asyncio
from subnet_sdk import SDK, ConfigBuilder, Handler, Task, Result

class MyHandler(Handler):
    async def execute(self, task: Task) -> Result:
        # Process task
        print(f"Processing task: {task.id}")

        # Return result
        return Result(
            data=b"task completed",
            success=True
        )

async def main():
    # Configure SDK (NO default IDs - must be explicit)
    config = (
        ConfigBuilder()
        .with_subnet_id("my-subnet-1")      # REQUIRED
        .with_agent_id("my-agent-1")        # REQUIRED
        .with_private_key("" + "a" * 64)    # 64 hex chars, no 0x prefix
        .with_chain_address("0xYourAgentAddress")  # Optional when signer is external
        .with_matcher_addr("localhost:8090") # REQUIRED
        .with_capabilities("compute", "ml")  # REQUIRED
        .build()
    )

    # Create and start SDK
    sdk = SDK(config)
    sdk.register_handler(MyHandler())
    await sdk.start()

    print(f"Agent started: {sdk.get_agent_id()}")

    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Using ConfigBuilder (Recommended)

```python
config = (
    ConfigBuilder()
    # Identity (REQUIRED - no defaults)
    .with_subnet_id("subnet-1")
    .with_agent_id("agent-1")

    # Authentication
    .with_private_key("...")    # 64 hex chars, no 0x prefix
    .with_chain_address("0x...") # Optional when key is held elsewhere

    # Network (REQUIRED)
    .with_matcher_addr("localhost:8090")
    .with_validator_addr("localhost:9090")

    # Capabilities (REQUIRED)
    .with_capabilities("compute", "storage")
    .with_intent_types("compute")

    # Performance
    .with_task_timeout(60)  # seconds
    .with_max_concurrent_tasks(10)

    # Economics
    .with_bidding_strategy("dynamic", 50, 500)

    .build()
)
```

### Direct Configuration

```python
from subnet_sdk import Config, IdentityConfig

config = Config(
    identity=IdentityConfig(
        subnet_id="subnet-1",  # REQUIRED
        agent_id="agent-1"     # REQUIRED
    ),
    private_key="...",         # 64 hex chars, no 0x prefix
    chain_address="0x...",      # Optional when private key not local
    matcher_addr="localhost:8090",  # REQUIRED
    capabilities=["compute"],  # REQUIRED
    task_timeout=30,
    max_concurrent_tasks=5
)
```

## Important Configuration Rules

1. **No Default IDs**: SubnetID and AgentID MUST be configured explicitly
2. **Private Key Format**: Exactly 64 hexadecimal characters (no `0x` prefix)
3. **Required Fields**: subnet_id, agent_id, matcher_addr, capabilities
4. **Chain Address**: The SDK derives the on-chain address from the private key. If you sign elsewhere, set `chain_address`/`with_chain_address` so bids and reports carry `metadata["chain_address"]` for on-chain checks.

## API Reference

### SDK Class

```python
# Create SDK
sdk = SDK(config)

# Register handler
sdk.register_handler(handler)
sdk.register_bidding_strategy(strategy)
sdk.register_callbacks(callbacks)

# Start/stop
await sdk.start()
await sdk.stop()

# Get configuration
sdk.get_agent_id()
sdk.get_subnet_id()
sdk.get_chain_address()  # Ethereum address used in metadata
sdk.get_capabilities()

# Execute task
result = await sdk.execute_task(task)

# Sign data
signature = sdk.sign(data)

# Get metrics
metrics = sdk.get_metrics()
```

### Handler Interface

```python
class Handler(ABC):
    @abstractmethod
    async def execute(self, task: Task) -> Result:
        pass
```

### Data Types

```python
@dataclass
class Task:
    id: str
    intent_id: str
    type: str
    data: bytes
    metadata: Dict[str, Any]
    deadline: datetime
    created_at: datetime

@dataclass
class Result:
    data: bytes
    success: bool
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
```

## Batch Operations

The SDK supports batch operations for improved performance when submitting multiple bids or execution reports:

### Batch Bid Submission

```python
from subnet_sdk import MatcherClient, SigningConfig
from subnet_sdk.proto.subnet import matcher_pb2, bid_pb2

# Create matcher client
signing_config = SigningConfig(
    private_key="your_64_hex_char_key",
    agent_id="agent-1",
    subnet_id="subnet-1"
)

matcher_client = MatcherClient(
    target="localhost:8090",
    secure=False,
    signing_config=signing_config
)

# Prepare multiple bids
bids = [
    bid_pb2.Bid(
        bid_id="bid-1",
        intent_id="intent-123",
        agent_id="agent-1",
        price=100,
    ),
    bid_pb2.Bid(
        bid_id="bid-2",
        intent_id="intent-123",
        agent_id="agent-1",
        price=150,
    ),
]

# Submit batch
batch_req = matcher_pb2.SubmitBidBatchRequest(
    bids=bids,
    batch_id="batch-123",
    partial_ok=True,  # Continue on partial failures
)

try:
    response = await matcher_client.submit_bid_batch(batch_req)
    print(f"Batch results: {response.success} succeeded, {response.failed} failed")

    for i, ack in enumerate(response.acks):
        print(f"Bid {i}: accepted={ack.accepted}, reason={ack.reason}")
finally:
    await matcher_client.close()
```

### Batch Execution Report Submission

```python
from subnet_sdk import ValidatorClient, SigningConfig
from subnet_sdk.proto.subnet import service_pb2, execution_report_pb2
import time

# Create validator client
validator_client = ValidatorClient(
    target="localhost:9090",
    secure=False,
    signing_config=signing_config
)

# Prepare multiple reports
reports = [
    execution_report_pb2.ExecutionReport(
        report_id="report-1",
        assignment_id="assignment-1",
        intent_id="intent-123",
        agent_id="agent-1",
        status=execution_report_pb2.ExecutionReport.SUCCESS,
        timestamp=int(time.time()),
    ),
    execution_report_pb2.ExecutionReport(
        report_id="report-2",
        assignment_id="assignment-2",
        intent_id="intent-456",
        agent_id="agent-1",
        status=execution_report_pb2.ExecutionReport.SUCCESS,
        timestamp=int(time.time()),
    ),
]

# Submit batch
batch_req = service_pb2.ExecutionReportBatchRequest(
    reports=reports,
    batch_id="batch-456",
    partial_ok=False,  # Stop on first failure
)

try:
    response = await validator_client.submit_execution_report_batch(batch_req)
    print(f"Batch results: {response.success} succeeded, {response.failed} failed")

    for i, receipt in enumerate(response.receipts):
        print(f"Report {i}: status={receipt.status}, phase={receipt.phase}")
finally:
    await validator_client.close()
```

### Batch Operation Benefits

- **Performance**: Reduced network overhead and connection management
- **Atomicity**: Optional partial success handling with `partial_ok` flag
- **Efficiency**: Single RPC call for multiple operations
- **Idempotency**: Use `batch_id` to prevent duplicate submissions

### Batch Error Handling

```python
# Stop on first failure (partial_ok = False)
batch_req = matcher_pb2.SubmitBidBatchRequest(
    bids=bids,
    batch_id="batch-123",
    partial_ok=False,
)
# If any bid fails, remaining bids are rejected

# Continue on failures (partial_ok = True)
batch_req = matcher_pb2.SubmitBidBatchRequest(
    bids=bids,
    batch_id="batch-123",
    partial_ok=True,
)
# All bids are processed, check individual acks for results
```

## Complete Example

See [example.py](example.py) for a complete working example.

## Testing

```bash
# Install dev dependencies
pip install -e .[dev]

# Run tests
pytest

# With coverage
pytest --cov=subnet_sdk
```

## 注册与执行报告

1. **注册与心跳**
   - 启用注册: 在配置中同时设置 `registry_addr` 与 `agent_endpoint`。
   - 启动后 SDK 会调用 `POST /agents` 注册自身，并按 `registry_heartbeat_interval` (默认 30 秒) 调用 `POST /agents/{id}/heartbeat`。
   - 停止时会调用 `DELETE /agents/{id}` 注销；建议在调试脚本中等待 `sdk.stop()` 完成。

2. **发现验证节点**
   - `SDK.discover_validators()` 会请求 `GET /validators` 并返回 `ValidatorEndpoint` 列表。
   - 若配置了 `validator_addr` 则会在注册发现失败时用作兜底。

3. **提交执行报告**
   - 使用 `ExecutionReport` 填写 `report_id`、`assignment_id`、`intent_id`、`status` (默认 success)、`result_data` (bytes) 与 `metadata`。
   - 调用 `await sdk.submit_execution_report(report)`；SDK 会生成 `/api/v1/execution-report` URL 并广播到所有验证节点。
   - 返回值是 `ExecutionReceipt` 列表，包含 `validator_id`、`status`、`message` 及时间戳；可结合 `metrics.report_counters()` 统计成功/失败次数。

## Development

```bash
# Format code
black subnet_sdk/

# Lint
flake8 subnet_sdk/

# Type checking
mypy subnet_sdk/
```
### Bidding Strategy & Callbacks

```python
from subnet_sdk import BiddingStrategy, Callbacks, Bid, Intent

class FixedPriceStrategy(BiddingStrategy):
    def should_bid(self, intent: Intent) -> bool:
        return intent.type == "compute"

    def calculate_bid(self, intent: Intent) -> Bid:
        return Bid(price=100, currency="PIN")

class LifecycleCallbacks(Callbacks):
    async def on_bid_submitted(self, intent_id: str, bid_id: str) -> None:
        print(f"bid {bid_id} submitted for intent {intent_id}")

    async def on_task_completed(self, task: Task, result: Result) -> None:
        print(f"task {task.id} finished: {result.success}")

sdk.register_bidding_strategy(FixedPriceStrategy())
sdk.register_callbacks(LifecycleCallbacks())
```

启用投标策略后，SDK 会自动订阅 matcher 的 `StreamIntents`，依据策略提交 `SubmitBid`，并通过回调上报竞标结果、任务处理与执行报告状态。
