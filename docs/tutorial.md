# Subnet SDK Tutorial

A step-by-step guide to building your first Subnet agent.

## Table of Contents
1. [Installation](#installation)
2. [Basic Agent](#basic-agent)
3. [Task Processing](#task-processing)
4. [Advanced Features](#advanced-features)
5. [Production Deployment](#production-deployment)

## Installation

### Go
```bash
go get github.com/pinai/subnet-sdk-go
```

### Python
```bash
pip install subnet-sdk
```

## Basic Agent

### Step 1: Create Configuration

The first and most important step is configuration. **There are NO default IDs** - you must explicitly set subnet_id and agent_id.

**Go:**
```go
package main

import (
    "log"
    sdk "github.com/pinai/subnet-sdk-go"
)

func main() {
    // Build configuration - ALL IDs must be explicit
    config, err := sdk.NewConfigBuilder().
        WithSubnetID("tutorial-subnet").    // REQUIRED: Choose unique subnet ID
        WithAgentID("tutorial-agent-001").  // REQUIRED: Choose unique agent ID
        WithMatcherAddr("localhost:8090").  // REQUIRED: Matcher service
        WithCapabilities("compute").         // REQUIRED: At least one capability
        Build()

    if err != nil {
        log.Fatal("Config error:", err)
    }
}
```

**Python:**
```python
from subnet_sdk import ConfigBuilder

# Build configuration - ALL IDs must be explicit
config = (
    ConfigBuilder()
    .with_subnet_id("tutorial-subnet")      # REQUIRED: Choose unique subnet ID
    .with_agent_id("tutorial-agent-001")    # REQUIRED: Choose unique agent ID
    .with_matcher_addr("localhost:8090")    # REQUIRED: Matcher service
    .with_capabilities("compute")            # REQUIRED: At least one capability
    .build()
)
```

### Step 2: Implement Handler

The handler is where your task processing logic lives.

**Go:**
```go
type TutorialHandler struct{}

func (h *TutorialHandler) Execute(ctx context.Context, task *sdk.Task) (*sdk.Result, error) {
    log.Printf("Processing task %s of type %s", task.ID, task.Type)

    // Process based on task type
    switch task.Type {
    case "compute":
        result := h.processCompute(task.Data)
        return &sdk.Result{
            Data:    result,
            Success: true,
        }, nil
    default:
        return &sdk.Result{
            Success: false,
            Error:   "unsupported task type",
        }, nil
    }
}

func (h *TutorialHandler) processCompute(data []byte) []byte {
    // Your computation logic here
    return []byte("computed result")
}
```

**Python:**
```python
from subnet_sdk import Handler, Task, Result
import logging

class TutorialHandler(Handler):
    async def execute(self, task: Task) -> Result:
        logging.info(f"Processing task {task.id} of type {task.type}")

        # Process based on task type
        if task.type == "compute":
            result = await self.process_compute(task.data)
            return Result(data=result, success=True)
        else:
            return Result(
                data=b"",
                success=False,
                error="unsupported task type"
            )

    async def process_compute(self, data: bytes) -> bytes:
        # Your computation logic here
        return b"computed result"
```

### Step 3: Create and Start Agent

**Go:**
```go
func main() {
    // ... configuration from Step 1 ...

    // Create SDK instance
    agent, err := sdk.New(config)
    if err != nil {
        log.Fatal("SDK creation error:", err)
    }

    // Register handler
    handler := &TutorialHandler{}
    agent.RegisterHandler(handler)

    // Start agent
    if err := agent.Start(); err != nil {
        log.Fatal("Start error:", err)
    }

    log.Printf("Agent %s started in subnet %s",
        agent.GetAgentID(),
        agent.GetSubnetID())

    // Keep running
    select {}
}
```

**Python:**
```python
import asyncio

async def main():
    # ... configuration from Step 1 ...

    # Create SDK instance
    agent = SDK(config)

    # Register handler
    handler = TutorialHandler()
    agent.register_handler(handler)

    # Start agent
    await agent.start()

    print(f"Agent {agent.get_agent_id()} started in subnet {agent.get_subnet_id()}")

    # Keep running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
```

## Task Processing

### Understanding Task Types

Tasks come with different types that indicate what processing is needed:

```
compute       - General computation
ml.inference  - Machine learning inference
data.process  - Data processing
storage.write - Storage operations
```

### Processing Pipeline

```go
// Go Example: Multi-step processing
func (h *Handler) Execute(ctx context.Context, task *sdk.Task) (*sdk.Result, error) {
    // 1. Validate input
    if err := h.validateInput(task); err != nil {
        return &sdk.Result{Success: false, Error: err.Error()}, nil
    }

    // 2. Process with timeout
    resultCh := make(chan []byte)
    errCh := make(chan error)

    go func() {
        result, err := h.process(task)
        if err != nil {
            errCh <- err
        } else {
            resultCh <- result
        }
    }()

    select {
    case result := <-resultCh:
        return &sdk.Result{Data: result, Success: true}, nil
    case err := <-errCh:
        return &sdk.Result{Success: false, Error: err.Error()}, nil
    case <-ctx.Done():
        return &sdk.Result{Success: false, Error: "timeout"}, nil
    }
}
```

```python
# Python Example: Multi-step processing
async def execute(self, task: Task) -> Result:
    # 1. Validate input
    if not self.validate_input(task):
        return Result(success=False, error="Invalid input")

    # 2. Process with timeout
    try:
        result = await asyncio.wait_for(
            self.process(task),
            timeout=30  # 30 seconds timeout
        )
        return Result(data=result, success=True)
    except asyncio.TimeoutError:
        return Result(success=False, error="Processing timeout")
    except Exception as e:
        return Result(success=False, error=str(e))
```

## Advanced Features

### 1. Authentication with Private Key

**Go:**
```go
config, _ := sdk.NewConfigBuilder().
    WithSubnetID("prod-subnet").
    WithAgentID("prod-agent").
    WithPrivateKey("abcd...1234").  // 64 hex characters
    WithMatcherAddr("matcher.example.com:8090").
    WithCapabilities("compute", "ml").
    WithRegistryAddr("registry:9000").
    WithAgentEndpoint("agent:8080").
    Build()

// Sign data
signature, err := agent.Sign([]byte("data to sign"))
```

**Python:**
```python
config = (
    ConfigBuilder()
    .with_subnet_id("prod-subnet")
    .with_agent_id("prod-agent")
    .with_private_key("abcd...1234")    # 64 hex characters, no 0x prefix
    .with_matcher_addr("matcher.example.com:8090")
    .with_capabilities("compute", "ml")
    .with_registry_addr("registry:9000")
    .with_agent_endpoint("agent:8080")
    .build()
)

# Sign data
signature = agent.sign(b"data to sign")
```

### 2. Metrics Monitoring

**Go:**
```go
// Periodic metrics reporting
go func() {
    ticker := time.NewTicker(60 * time.Second)
    defer ticker.Stop()

    for range ticker.C {
        metrics := agent.GetMetrics()
        completed, failed, totalBids, wonBids := metrics.GetStats()

        log.Printf("Stats - Tasks: %d/%d, Bids: %d/%d",
            completed, completed+failed,
            wonBids, totalBids)
    }
}()
```

**Python:**
```python
# Periodic metrics reporting
async def monitor_metrics(agent):
    while True:
        await asyncio.sleep(60)  # Every minute

        metrics = agent.get_metrics()
        completed, failed, total_bids, won_bids = metrics.get_stats()

        print(f"Stats - Tasks: {completed}/{completed+failed}, "
              f"Bids: {won_bids}/{total_bids}")

# Start monitoring
asyncio.create_task(monitor_metrics(agent))

## 提交执行报告

**Go:**
```go
report := &agentsdk.ExecutionReport{
    ReportID:     "report-123",
    AssignmentID: "assign-123",
    IntentID:     "intent-123",
    Status:       agentsdk.ExecutionReportStatusSuccess,
    ResultData:   []byte("..."),
}

receipts, err := agent.SubmitExecutionReport(ctx, report)
if err != nil {
    log.Fatal(err)
}

for _, receipt := range receipts {
    log.Printf("validator %s: %s", receipt.ValidatorID, receipt.Status)
}
```

**Python:**
```python
report = ExecutionReport(
    report_id="report-123",
    assignment_id="assign-123",
    intent_id="intent-123",
    result_data=b"...",
)

receipts = await sdk.submit_execution_report(report)
for receipt in receipts:
    print(receipt.validator_id, receipt.status)
```
```

### 3. Dynamic Capability Management

```go
// Go: Get current capabilities
capabilities := agent.GetCapabilities()

// Check if we support a task type
func canHandle(taskType string, capabilities []string) bool {
    for _, cap := range capabilities {
        if strings.HasPrefix(taskType, cap) {
            return true
        }
    }
    return false
}
```

```python
# Python: Get current capabilities
capabilities = agent.get_capabilities()

# Check if we support a task type
def can_handle(task_type: str, capabilities: list) -> bool:
    return any(task_type.startswith(cap) for cap in capabilities)
```

### 4. Graceful Shutdown

**Go:**
```go
// Setup signal handling
sigCh := make(chan os.Signal, 1)
signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)

go func() {
    <-sigCh
    log.Println("Shutting down...")

    // Stop agent
    if err := agent.Stop(); err != nil {
        log.Printf("Stop error: %v", err)
    }

    os.Exit(0)
}()
```

**Python:**
```python
# Setup signal handling
import signal

def signal_handler(signum, frame):
    print("Shutting down...")
    asyncio.create_task(agent.stop())
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

## Production Deployment

### 1. Environment Configuration

Never hardcode sensitive values. Use environment variables:

**Go:**
```go
import "os"

config, _ := sdk.NewConfigBuilder().
    WithSubnetID(os.Getenv("SUBNET_ID")).
    WithAgentID(os.Getenv("AGENT_ID")).
    WithPrivateKey(os.Getenv("PRIVATE_KEY")).
    WithMatcherAddr(os.Getenv("MATCHER_ADDR")).
    WithCapabilities(strings.Split(os.Getenv("CAPABILITIES"), ",")...).
    Build()
```

**Python:**
```python
import os

config = (
    ConfigBuilder()
    .with_subnet_id(os.getenv("SUBNET_ID"))
    .with_agent_id(os.getenv("AGENT_ID"))
    .with_private_key(os.getenv("PRIVATE_KEY"))
    .with_matcher_addr(os.getenv("MATCHER_ADDR"))
    .with_capabilities(*os.getenv("CAPABILITIES").split(","))
    .build()
)
```

### 2. Docker Deployment

```dockerfile
# Go Dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o agent .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
COPY --from=builder /app/agent /agent
CMD ["/agent"]
```

```dockerfile
# Python Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "agent.py"]
```

### 3. Health Monitoring

Implement health checks for your agent:

```go
// Go: Health endpoint
http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
    metrics := agent.GetMetrics()
    completed, failed, _, _ := metrics.GetStats()

    status := map[string]interface{}{
        "status": "healthy",
        "agent_id": agent.GetAgentID(),
        "tasks_completed": completed,
        "tasks_failed": failed,
    }

    json.NewEncoder(w).Encode(status)
})

go http.ListenAndServe(":8080", nil)
```

```python
# Python: Health endpoint with aiohttp
from aiohttp import web

async def health_check(request):
    metrics = agent.get_metrics()
    completed, failed, _, _ = metrics.get_stats()

    return web.json_response({
        "status": "healthy",
        "agent_id": agent.get_agent_id(),
        "tasks_completed": completed,
        "tasks_failed": failed
    })

app = web.Application()
app.router.add_get('/health', health_check)
runner = web.AppRunner(app)
await runner.setup()
site = web.TCPSite(runner, '0.0.0.0', 8080)
await site.start()
```

### 4. Logging Best Practices

**Go:**
```go
import (
    "github.com/sirupsen/logrus"
)

log := logrus.New()
log.SetLevel(logrus.InfoLevel)
log.SetFormatter(&logrus.JSONFormatter{})

// Structured logging
log.WithFields(logrus.Fields{
    "agent_id": agent.GetAgentID(),
    "task_id": task.ID,
    "type": task.Type,
}).Info("Processing task")
```

**Python:**
```python
import logging
import json

# Configure JSON logging
class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "agent_id": agent.get_agent_id()
        }
        return json.dumps(log_obj)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

## Common Patterns

### 1. Retry Logic

```go
// Go: Retry with exponential backoff
func retryTask(task *sdk.Task, maxRetries int) (*sdk.Result, error) {
    var lastErr error
    for i := 0; i < maxRetries; i++ {
        result, err := processTask(task)
        if err == nil {
            return result, nil
        }
        lastErr = err
        time.Sleep(time.Duration(math.Pow(2, float64(i))) * time.Second)
    }
    return nil, lastErr
}
```

```python
# Python: Retry with exponential backoff
async def retry_task(task: Task, max_retries: int = 3) -> Result:
    last_error = None
    for i in range(max_retries):
        try:
            return await process_task(task)
        except Exception as e:
            last_error = e
            await asyncio.sleep(2 ** i)

    return Result(success=False, error=str(last_error))
```

### 2. Rate Limiting

```go
// Go: Simple rate limiter
type RateLimiter struct {
    rate   int
    tokens chan struct{}
}

func NewRateLimiter(rate int) *RateLimiter {
    rl := &RateLimiter{
        rate:   rate,
        tokens: make(chan struct{}, rate),
    }

    // Refill tokens
    go func() {
        ticker := time.NewTicker(time.Second / time.Duration(rate))
        for range ticker.C {
            select {
            case rl.tokens <- struct{}{}:
            default:
            }
        }
    }()

    return rl
}

func (rl *RateLimiter) Wait() {
    <-rl.tokens
}
```

## Troubleshooting

### Common Issues

1. **"subnet_id must be configured"**
   - Solution: Explicitly set subnet_id in configuration
   - There are NO defaults for IDs

2. **"private key must be 32 bytes (64 hex characters)"**
   - Solution: Ensure key is exactly 64 hex characters
   - Remove "0x" prefix in Go, optional in Python

3. **"SDK already running"**
   - Solution: Check if Start() was called multiple times
   - Ensure proper shutdown before restart

4. **Task execution timeout**
   - Solution: Increase task_timeout in configuration
   - Optimize processing logic
   - Use goroutines/asyncio for parallel processing

## Next Steps

1. Explore the [API Reference](api-reference.md)
2. Check [Example Implementations](../examples/)
3. Read about [Security Best Practices](security.md)
4. Join the community on Discord
