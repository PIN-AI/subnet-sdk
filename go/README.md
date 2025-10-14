# Subnet Agent SDK for Go

A standalone Go SDK for building agents that interact with the Subnet protocol. This SDK is completely independent from internal Subnet packages, making it suitable for external developers.

## Features

- **Independent Design**: No dependencies on internal Subnet packages
- **Configuration Management**: Fluent builder API for easy configuration
- **Identity Management**: Support for SubnetID, AgentID, and other identity fields
- **Task Execution**: Simple handler interface for processing tasks
- **Metrics Collection**: Built-in metrics tracking
- **Signature Support**: ECDSA signing capabilities for authentication
- **Thread-Safe**: Safe for concurrent use
- **Metadata Enrichment**: Bids and execution reports automatically carry `metadata["chain_address"]`

## Installation

```bash
go get github.com/PIN-AI/subnet-sdk/go
```

## Quick Start

```go
package main

import (
    "context"
    "log"
    "time"

    sdk "github.com/PIN-AI/subnet-sdk/go"
)

func main() {
    // Create configuration using builder
    config, err := sdk.NewConfigBuilder().
        WithSubnetID("my-subnet-1").      // REQUIRED - no defaults
        WithAgentID("my-agent-1").        // REQUIRED - no defaults
        WithPrivateKey("your-64-hex-chars"). // Required for signing
        WithChainAddress("0xYourAgentAddress"). // Optional when using external signer
        WithMatcherAddr("localhost:8090").   // REQUIRED
        WithCapabilities("compute", "storage"). // REQUIRED (at least one)
        Build()

    if err != nil {
        log.Fatal(err)
    }

    // Create SDK instance
    agent, err := sdk.New(config)
    if err != nil {
        log.Fatal(err)
    }

    // Register handler
    handler := &MyHandler{}
    agent.RegisterHandler(handler)

    // Start agent
    if err := agent.Start(); err != nil {
        log.Fatal(err)
    }

    log.Printf("Agent started: %s", agent.GetAgentID())

    // Keep running
    select {}
}

// Implement the Handler interface
type MyHandler struct{}

func (h *MyHandler) Execute(ctx context.Context, task *sdk.Task) (*sdk.Result, error) {
    // Process task based on type
    log.Printf("Executing task: %s of type %s", task.ID, task.Type)

    // Simulate work
    time.Sleep(time.Second)

    // Return result
    return &sdk.Result{
        Data:    []byte("task completed"),
        Success: true,
    }, nil
}
```

## Configuration

### Using ConfigBuilder (Recommended)

The ConfigBuilder provides a fluent API for configuration:

```go
config, err := sdk.NewConfigBuilder().
    // Identity (REQUIRED - no defaults to prevent conflicts)
    WithSubnetID("subnet-1").
    WithAgentID("agent-1").

    // Authentication
    WithPrivateKey("0x...").               // 64 hex chars without 0x prefix
    WithChainAddress("0x...").             // Optional when using a remote signer

    // Network (REQUIRED)
    WithMatcherAddr("localhost:8090").
    WithRegistryAddr("127.0.0.1:8092").
    WithAgentEndpoint("10.0.0.2:8080").
    WithRegistryHeartbeatInterval(30 * time.Second).
    WithValidatorAddr("localhost:9090").

    // Capabilities (REQUIRED - at least one)
    WithCapabilities("compute", "ml", "storage").

    // Performance
    WithTaskTimeout(60 * time.Second).
    WithBidTimeout(10 * time.Second).
    WithMaxConcurrentTasks(10).

    // Economics
    WithBiddingStrategy("dynamic", 50, 500).
    WithStakeAmount(1000).
    WithOwner("0x...").

    // Security
    WithTLS("cert.pem", "key.pem").

    Build()
```

### Direct Configuration

```go
config := &sdk.Config{
    Identity: &sdk.IdentityConfig{
        SubnetID: "subnet-1",  // REQUIRED
        AgentID:  "agent-1",   // REQUIRED
    },
    PrivateKey:   "your-private-key-hex", // 64 hex chars
    ChainAddress: "0xYourAgentAddress",   // Optional when private key not local
    MatcherAddr:  "localhost:8090",       // REQUIRED
    RegistryAddr: "127.0.0.1:8092",     // Optional (enables discovery)
    AgentEndpoint: "10.0.0.2:8080",     // Required when registry is set
    RegistryHeartbeatInterval: 30 * time.Second,
    ValidatorAddr: "localhost:9090",    // Optional fallback
    Capabilities: []string{"compute"},    // REQUIRED

    // Optional settings with defaults
    MaxConcurrentTasks: 5,
    TaskTimeout:        30 * time.Second,
    BidTimeout:         5 * time.Second,
}
```

## Important Configuration Rules

1. **No Default IDs**: SubnetID and AgentID MUST be explicitly configured. There are NO defaults to prevent identity conflicts in the network.

2. **Private Key Format**: Private keys must be exactly 64 hex characters (32 bytes) WITHOUT the "0x" prefix.

3. **Required Fields**:
   - `SubnetID` - Identifies which subnet this agent belongs to
   - `AgentID` - Unique identifier for this agent
   - `MatcherAddr` - Address of the matcher service
   - `Capabilities` - At least one capability string

4. **Chain Address**: The SDK auto-derives the on-chain address from the private key. If your signer is external (KMS/HSM), set `ChainAddress`/`WithChainAddress` so bids and execution reports include `metadata["chain_address"]` for on-chain verification.

5. **Registry Usage**: When `RegistryAddr` is configured you must also set `AgentEndpoint` (reachable by validators) and keep heartbeat intervals reasonable. The optional `ValidatorAddr` acts as a fallback when discovery fails.

6. **Validation**: Configuration is validated at SDK creation time with detailed error messages.

## API Reference

### SDK Methods

```go
// Create new SDK instance
func New(config *Config) (*SDK, error)

// Register task handler
func (sdk *SDK) RegisterHandler(handler Handler)

// Start/stop the SDK
func (sdk *SDK) Start() error
func (sdk *SDK) Stop() error

// Get configuration and identity
func (sdk *SDK) GetAgentID() string
func (sdk *SDK) GetSubnetID() string
func (sdk *SDK) GetAddress() string      // Ethereum address from private key or config
func (sdk *SDK) GetChainAddress() string // Alias for GetAddress
func (sdk *SDK) GetCapabilities() []string
func (sdk *SDK) GetConfig() *Config    // Returns a safe copy

// Get metrics
func (sdk *SDK) GetMetrics() *Metrics

// Execute a task directly
func (sdk *SDK) ExecuteTask(ctx context.Context, task *Task) (*Result, error)

// Sign data with private key
func (sdk *SDK) Sign(data []byte) ([]byte, error)

// Discover registry-managed validators
func (sdk *SDK) DiscoverValidators(ctx context.Context) ([]ValidatorEndpoint, error)

// Submit execution reports to all validators
func (sdk *SDK) SubmitExecutionReport(ctx context.Context, report *ExecutionReport) ([]*ExecutionReceipt, error)
```

### Handler Interface

Your agent must implement this interface:

```go
type Handler interface {
    Execute(ctx context.Context, task *Task) (*Result, error)
}
```

### Core Data Types

```go
// Task represents work to be executed
type Task struct {
    ID        string            // Task identifier
    IntentID  string            // Parent intent ID
    Type      string            // Task type (e.g., "compute", "ml.inference")
    Data      []byte            // Task payload data
    Metadata  map[string]string // Additional metadata
    Deadline  time.Time         // Execution deadline
    CreatedAt time.Time         // Task creation time
}

// Result represents execution output
type Result struct {
    Data     []byte            // Result data
    Success  bool              // Whether execution was successful
    Error    string            // Error message if failed
    Metadata map[string]string // Result metadata
}

// Intent represents a task request for bidding
type Intent struct {
    ID          string
    Type        string
    Description string
    CreatedAt   time.Time
}

// Bid represents an agent's bid
type Bid struct {
    Price    uint64
    Currency string // e.g., "PIN"
}
```

## Metrics

The SDK automatically tracks performance metrics:

```go
metrics := agent.GetMetrics()

// Get statistics
completed, failed, totalBids, wonBids := metrics.GetStats()

fmt.Printf("Tasks: %d completed, %d failed\n", completed, failed)
fmt.Printf("Bids: %d won out of %d total\n", wonBids, totalBids)

// Metrics are updated automatically:
// - Task completion/failure
// - Bid submission/success
// - Execution times
```

## Chain Address Metadata

The SDK automatically injects the agent's on-chain address into all metadata-bearing requests:

### Execution Reports

When you call `SubmitExecutionReport()`, the SDK automatically adds `metadata["chain_address"]` with the normalized Ethereum address:

```go
report := &sdk.ExecutionReport{
    ReportID:     "report-123",
    AssignmentID: "task-456",
    IntentID:     "intent-789",
    AgentID:      agent.GetAgentID(),
    Status:       sdk.ExecutionReportStatusSuccess,
    ResultData:   resultBytes,
    Metadata:     map[string]string{"custom": "value"},
}

// The SDK automatically enriches metadata with chain_address
receipts, err := agent.SubmitExecutionReport(ctx, report)
// report.Metadata now contains: {"custom": "value", "chain_address": "0x..."}
```

### Bid Submissions (Future Implementation)

When bid submission logic is implemented, it MUST use the same pattern:

```go
// Example for future SubmitBid implementation:
bidMetadata := ensureChainAddressMetadata(bid.Metadata, sdk.GetChainAddress())
// Use bidMetadata in the bid request
```

See the documentation in `types.go` (Bid struct) and `sdk.go` (ensureChainAddressMetadata function) for implementation details.

### Why Chain Address Matters

- **On-chain verification**: Validators can verify that execution reports come from registered agents
- **Economic tracking**: Rewards and penalties are tied to the chain address
- **Consistency**: Python and Go SDKs follow the same metadata enrichment pattern

## Complete Example

See the [example](example/) directory for a working example that demonstrates:
- Configuration using ConfigBuilder
- Handler implementation
- Metrics collection
- Graceful shutdown

## Error Handling

The SDK provides detailed error messages:

```go
// Configuration errors
config, err := sdk.NewConfigBuilder().Build()
// Error: "subnet_id must be configured"

// Invalid private key
config, err := sdk.NewConfigBuilder().
    WithPrivateKey("invalid").
    Build()
// Error: "private key must be 32 bytes (64 hex characters)"

// Runtime errors
err := agent.Start()
if err != nil {
    // "SDK already running"
    // "no handler registered"
}
```

## Thread Safety

The SDK is fully thread-safe. All public methods can be called concurrently from multiple goroutines. Configuration is immutable after creation.

## Security Considerations

1. **Private Key Storage**: Never hardcode private keys. Use environment variables or secure key management.
2. **TLS Support**: Enable TLS for production deployments.
3. **Input Validation**: The SDK validates all configuration inputs.

## Development Tips

1. Always configure SubnetID and AgentID explicitly - there are no defaults
2. Use the ConfigBuilder for cleaner code
3. Implement proper error handling in your Handler
4. Monitor metrics to track agent performance
5. Use context for proper timeout handling

## License

See the main Subnet repository for license information.
