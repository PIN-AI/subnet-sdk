# Subnet SDK

Official SDKs for building agents on PinAI Subnets. Available in **Go** and **Python**.

## What is an Agent?

An **Agent** is a service provider in the PinAI network. Agents:
- Connect to a Subnet's Matcher service
- Bid on tasks (Intents) they can handle
- Execute tasks and submit results
- Get paid for successful execution

```
Subnet Matcher ──── streams tasks ────→ Your Agent
                                            │
                                            ↓
                                      Execute task
                                            │
                                            ↓
Your Agent ──── submits result ────→ Validator ──→ Verified & Paid
```

---

## Quick Start

### Installation

**Go:**
```bash
go get github.com/PIN-AI/subnet-sdk/go
```

**Python:**
```bash
pip install subnet-sdk
```

### Minimal Agent (Go)

```go
package main

import (
    "context"
    "log"
    sdk "github.com/PIN-AI/subnet-sdk/go"
)

type MyHandler struct{}

func (h *MyHandler) Execute(ctx context.Context, task *sdk.Task) (*sdk.Result, error) {
    // Your business logic here
    return &sdk.Result{Data: []byte("done"), Success: true}, nil
}

func main() {
    config, _ := sdk.NewConfigBuilder().
        WithSubnetID("your-subnet-id").      // Get from subnet operator
        WithAgentID("your-agent-id").        // Your unique ID
        WithMatcherAddr("matcher:8090").     // Matcher address
        WithCapabilities("compute").         // What you can do
        Build()

    agent, _ := sdk.New(config)
    agent.RegisterHandler(&MyHandler{})
    agent.Start()

    select {} // Run forever
}
```

### Minimal Agent (Python)

```python
import asyncio
from subnet_sdk import SDK, ConfigBuilder, Handler, Task, Result

class MyHandler(Handler):
    async def execute(self, task: Task) -> Result:
        # Your business logic here
        return Result(data=b"done", success=True)

async def main():
    config = (
        ConfigBuilder()
        .with_subnet_id("your-subnet-id")    # Get from subnet operator
        .with_agent_id("your-agent-id")      # Your unique ID
        .with_matcher_addr("matcher:8090")   # Matcher address
        .with_capabilities("compute")        # What you can do
        .build()
    )

    agent = SDK(config)
    agent.register_handler(MyHandler())
    await agent.start()
    await asyncio.Event().wait()

asyncio.run(main())
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Quick Start](docs/quick-start.md) | Get your first agent running in 5 minutes |
| [Tutorial](docs/tutorial.md) | Step-by-step guide with examples |
| [API Reference](docs/api-reference.md) | Complete API documentation |
| [Execution Reporting](docs/execution-reporting.md) | How to submit results to validators |

---

## Configuration Reference

| Parameter | Required | Description |
|-----------|----------|-------------|
| `subnet_id` | ✅ | The subnet to join (get from operator) |
| `agent_id` | ✅ | Your unique agent identifier |
| `matcher_addr` | ✅ | Matcher service address (e.g., `host:8090`) |
| `capabilities` | ✅ | What tasks you can handle (e.g., `compute`, `ml`) |
| `private_key` | Optional | 64 hex chars, for signing (required for payments) |

---

## Examples

See working examples:

- **Go**: [`go/example/`](go/example/)
- **Python**: [`python/examples/`](python/examples/)

---

## Need Help?

- Check the [Tutorial](docs/tutorial.md) for detailed walkthrough
- See [Troubleshooting](docs/quick-start.md#common-issues) for common issues
- For subnet setup, see [Subnet Repository](https://github.com/PIN-AI/Subnet)

---

## License

MIT License
