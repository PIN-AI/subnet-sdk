# Quick Start Guide

Get your first Subnet agent running in 5 minutes!

## Prerequisites

- Go 1.21+ or Python 3.8+
- Access to a Subnet matcher service
- Basic understanding of async programming (for Python)

## Installation

### Go
```bash
go get github.com/PIN-AI/subnet-sdk/go
```

### Python
```bash
pip install subnet-sdk
```

## Minimal Working Agent

### Go Version

Create `agent.go`:

```go
package main

import (
    "context"
    "fmt"
    "log"
    sdk "github.com/PIN-AI/subnet-sdk/go"
)

// Simple handler that echoes input
type EchoHandler struct{}

func (h *EchoHandler) Execute(ctx context.Context, task *sdk.Task) (*sdk.Result, error) {
    log.Printf("Task %s: %s", task.ID, string(task.Data))
    return &sdk.Result{
        Data:    []byte(fmt.Sprintf("Echo: %s", task.Data)),
        Success: true,
    }, nil
}

func main() {
    // ⚠️ IMPORTANT: No default IDs - you MUST set these!
    config, err := sdk.NewConfigBuilder().
        WithSubnetID("quickstart-subnet").  // CHANGE THIS!
        WithAgentID("quickstart-agent-1").  // CHANGE THIS!
        WithMatcherAddr("localhost:8090").
        WithCapabilities("echo").
        Build()

    if err != nil {
        log.Fatal(err)
    }

    agent, err := sdk.New(config)
    if err != nil {
        log.Fatal(err)
    }

    agent.RegisterHandler(&EchoHandler{})

    if err := agent.Start(); err != nil {
        log.Fatal(err)
    }

    log.Printf("Agent running: %s", agent.GetAgentID())
    select {} // Run forever
}
```

Run it:
```bash
go run agent.go
```

### Python Version

Create `agent.py`:

```python
import asyncio
import logging
from subnet_sdk import SDK, ConfigBuilder, Handler, Task, Result

logging.basicConfig(level=logging.INFO)

class EchoHandler(Handler):
    async def execute(self, task: Task) -> Result:
        logging.info(f"Task {task.id}: {task.data}")
        return Result(
            data=f"Echo: {task.data.decode()}".encode(),
            success=True
        )

async def main():
    # ⚠️ IMPORTANT: No default IDs - you MUST set these!
    config = (
        ConfigBuilder()
        .with_subnet_id("quickstart-subnet")  # CHANGE THIS!
        .with_agent_id("quickstart-agent-1")  # CHANGE THIS!
        .with_matcher_addr("localhost:8090")
        .with_capabilities("echo")
        .build()
    )

    agent = SDK(config)
    agent.register_handler(EchoHandler())
    await agent.start()

    logging.info(f"Agent running: {agent.get_agent_id()}")
    await asyncio.Event().wait()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python agent.py
```

## Key Configuration Points

### ⚠️ Critical: No Default IDs

The SDK has **NO default values** for IDs to prevent conflicts:

```go
// ❌ THIS WILL FAIL
config, err := sdk.NewConfigBuilder().Build()
// Error: subnet_id must be configured

// ✅ THIS WORKS
config, err := sdk.NewConfigBuilder().
    WithSubnetID("my-unique-subnet").
    WithAgentID("my-unique-agent").
    WithMatcherAddr("localhost:8090").
    WithCapabilities("compute").
    Build()
```

### Required Fields

| Field | Description | Example |
|-------|------------|---------|
| `subnet_id` | Which subnet to join | `"prod-subnet-1"` |
| `agent_id` | Your unique agent ID | `"compute-agent-42"` |
| `matcher_addr` | Matcher service endpoint | `"matcher.example.com:8090"` |
| `capabilities` | What your agent can do | `["compute", "ml"]` |

## Adding Authentication

To enable signing and authentication:

### Go
```go
config, _ := sdk.NewConfigBuilder().
    WithSubnetID("secure-subnet").
    WithAgentID("secure-agent").
    WithPrivateKey("abc...123").  // 64 hex chars, no 0x
    WithMatcherAddr("localhost:8090").
    WithCapabilities("secure-compute").
    Build()
```

### Python
```python
config = (
    ConfigBuilder()
    .with_subnet_id("secure-subnet")
    .with_agent_id("secure-agent")
    .with_private_key("abc...123")    # 64 hex chars, no 0x prefix
    .with_matcher_addr("localhost:8090")
    .with_capabilities("secure-compute")
    .build()
)
```

## Testing Your Agent

### Manual Task Execution

You can test your handler directly:

**Go:**
```go
// Create a test task
testTask := &sdk.Task{
    ID:       "test-001",
    Type:     "echo",
    Data:     []byte("Hello, World!"),
    Metadata: map[string]string{"priority": "high"},
}

// Execute directly
result, err := agent.ExecuteTask(context.Background(), testTask)
if err != nil {
    log.Printf("Error: %v", err)
} else {
    log.Printf("Result: %s", result.Data)
}
```

**Python:**
```python
from datetime import datetime

# Create a test task
test_task = Task(
    id="test-001",
    intent_id="intent-001",
    type="echo",
    data=b"Hello, World!",
    metadata={"priority": "high"},
    deadline=datetime.now(),
    created_at=datetime.now()
)

# Execute directly
result = await agent.execute_task(test_task)
if result.success:
    print(f"Result: {result.data}")
else:
    print(f"Error: {result.error}")
```

## Monitoring

Add basic monitoring to see what's happening:

### Go
```go
// Check metrics every 10 seconds
go func() {
    for range time.Tick(10 * time.Second) {
        metrics := agent.GetMetrics()
        completed, failed, _, _ := metrics.GetStats()
        log.Printf("Processed: %d success, %d failed", completed, failed)
    }
}()
```

### Python
```python
# Check metrics every 10 seconds
async def monitor():
    while True:
        await asyncio.sleep(10)
        metrics = agent.get_metrics()
        completed, failed, _, _ = metrics.get_stats()
        print(f"Processed: {completed} success, {failed} failed")

asyncio.create_task(monitor())
```

## Environment Variables

For production, use environment variables:

### `.env` file:
```bash
SUBNET_ID=production-subnet
AGENT_ID=prod-agent-001
MATCHER_ADDR=matcher.production.com:8090
PRIVATE_KEY=your_private_key_here
CAPABILITIES=compute,storage,ml
```

### Go:
```go
import "os"

config, _ := sdk.NewConfigBuilder().
    WithSubnetID(os.Getenv("SUBNET_ID")).
    WithAgentID(os.Getenv("AGENT_ID")).
    WithMatcherAddr(os.Getenv("MATCHER_ADDR")).
    WithPrivateKey(os.Getenv("PRIVATE_KEY")).
    WithCapabilities(strings.Split(os.Getenv("CAPABILITIES"), ",")...).
    Build()
```

### Python:
```python
import os
from dotenv import load_dotenv

load_dotenv()

config = (
    ConfigBuilder()
    .with_subnet_id(os.getenv("SUBNET_ID"))
    .with_agent_id(os.getenv("AGENT_ID"))
    .with_matcher_addr(os.getenv("MATCHER_ADDR"))
    .with_private_key(os.getenv("PRIVATE_KEY"))
    .with_capabilities(*os.getenv("CAPABILITIES").split(","))
    .build()
)
```

## Registry & Execution Reports

1. **Agent Registration**
   - Go: Use `WithRegistryAddr(...).WithAgentEndpoint(...)` to enable service registration. The SDK will maintain heartbeats automatically.
   - Python: Use `with_registry_addr(...).with_agent_endpoint(...)`. Registration happens on `start()`, deregistration on `stop()`.

2. **Validator Discovery**
   - Go: Call `sdk.DiscoverValidators(ctx)` to get `[]ValidatorEndpoint`.
   - Python: Call `await sdk.discover_validators()` to get a list of `ValidatorEndpoint` (fields: `id`, `endpoint`, `status`, `last_seen`).

3. **Execution Reports**
   - Go: Create an `ExecutionReport` and call `sdk.SubmitExecutionReport(ctx, report)`.
   - Python: Create an `ExecutionReport` and call `await sdk.submit_execution_report(report)`.
   - The SDK automatically appends `/api/v1/execution-report` to validator endpoints, Base64-encodes result data, and tracks success/failure counts in metrics.

## What's Next?

1. **Implement real processing**: Replace the echo handler with actual task processing
2. **Add error handling**: Handle different error scenarios gracefully
3. **Setup logging**: Implement structured logging for production
4. **Deploy with Docker**: Containerize your agent
5. **Monitor performance**: Track metrics and optimize

## Need Help?

- 📖 Read the full [Tutorial](tutorial.md)
- 📚 Check the [API Reference](api-reference.md)
- 💡 See Examples: [Go](../go/example/) | [Python](../python/examples/)
- 💬 Join our Discord community

## Common Issues

### "subnet_id must be configured"
You forgot to set the subnet ID. There are NO defaults!

### "private key must be 32 bytes"
The private key should be exactly 64 hex characters.

### "at least one capability must be configured"
You must specify what types of tasks your agent can handle.

### Connection refused
Make sure the matcher service is running and accessible.
