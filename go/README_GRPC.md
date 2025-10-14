# Go SDK gRPC Support

The Go SDK now includes full gRPC support, matching the Python SDK functionality.

## New Features

### 1. gRPC Clients

- **MatcherClient**: Connects to matcher service for bidding and task streaming
- **ValidatorClient**: Submits execution reports via gRPC
- **SigningInterceptor**: Automatically signs all gRPC requests with agent's private key

### 2. Streaming Support

#### Task Streaming
Agents automatically receive execution tasks via gRPC server-side streaming:

```go
// Automatically enabled when matcher address is configured
config := sdk.NewConfigBuilder().
    WithMatcherAddr("localhost:8090").  // gRPC endpoint
    Build()

// SDK handles streaming internally
agent.Start()  // Starts task stream automatically
```

#### Intent Streaming & Auto-Bidding
Register a bidding strategy to participate in intent auctions:

```go
type MyStrategy struct{}

func (s *MyStrategy) ShouldBid(intent *sdk.Intent) bool {
    // Your bidding logic
    return intent.Type == "ml.inference"
}

func (s *MyStrategy) CalculateBid(intent *sdk.Intent) *sdk.Bid {
    return &sdk.Bid{
        Price:    500,
        Currency: "PIN",
    }
}

agent.RegisterBiddingStrategy(&MyStrategy{})
agent.Start()  // Starts intent stream and submits bids automatically
```

### 3. Lifecycle Callbacks

Monitor agent lifecycle events:

```go
type MyCallbacks struct{}

func (c *MyCallbacks) OnStart() error {
    log.Println("Agent started")
    return nil
}

func (c *MyCallbacks) OnTaskAccepted(task *sdk.Task) {
    log.Printf("Task accepted: %s", task.ID)
}

func (c *MyCallbacks) OnBidSubmitted(intent *sdk.Intent, bid *sdk.Bid) {
    log.Printf("Bid submitted: %d %s", bid.Price, bid.Currency)
}

func (c *MyCallbacks) OnError(err error) {
    log.Printf("Error: %v", err)
}

agent.RegisterCallbacks(&MyCallbacks{})
```

### 4. Automatic Metadata Injection

Chain addresses are automatically included in bids and execution reports:

```go
config := sdk.NewConfigBuilder().
    WithPrivateKey("your-private-key").  // Address derived automatically
    Build()

// All bids include metadata["chain_address"] = "0x..."
// All reports include metadata["chain_address"] = "0x..."
```

## Architecture

### gRPC Transport Layer

```
grpc_transport.go
├── SigningConfig       - Authentication configuration
├── SigningInterceptor  - Client-side interceptor
├── UnaryInterceptor()  - Signs unary RPC calls
├── StreamInterceptor() - Signs streaming RPC calls
└── DialOption()        - Creates configured gRPC connection
```

### Client Wrappers

```
matcher_client.go
├── MatcherClient
│   ├── SubmitBid()      - Submit bid for intent
│   ├── StreamIntents()  - Receive intent updates
│   ├── StreamTasks()    - Receive execution tasks
│   └── RespondToTask()  - Accept/reject task

validator_client.go
└── ValidatorClient
    ├── SubmitExecutionReport() - Submit report via gRPC
    └── GetValidatorSet()       - Query validator set
```

### Streaming Logic

```
streaming.go
├── startMatcherStreams()   - Initialize streams
├── taskStreamLoop()        - Handle task stream
├── intentStreamLoop()      - Handle intent stream
├── handleExecutionTask()   - Process incoming task
└── handleIntentUpdate()    - Process intent & bid
```

## Configuration

### gRPC Endpoints

```go
config := sdk.NewConfigBuilder().
    // gRPC matcher service
    WithMatcherAddr("localhost:8090").

    // gRPC validator service (optional - falls back to HTTP)
    WithValidatorAddr("localhost:9090").

    // HTTP registry service
    WithRegistryAddr("http://localhost:8092").

    Build()
```

### TLS/SSL Support

```go
config.UseTLS = true  // Enable TLS for gRPC connections
```

## Protocol Buffers

The SDK uses the protobuf definitions from `/Subnet/proto/subnet/`:

- `matcher_service.proto` - Matcher gRPC service
- `service.proto` - Validator gRPC service
- `execution_report.proto` - Execution report messages
- `bid.proto` - Bid messages
- `matcher.proto` - Intent and task messages

Generated Go files are located in `/Subnet/proto/subnet/*.pb.go`

## Signing Protocol

All gRPC requests are signed using the same protocol as Python SDK:

1. **Canonical JSON** - Deterministic JSON serialization
2. **Keccak256 Hash** - Ethereum-compatible hashing
3. **ECDSA Signature** - secp256k1 signature
4. **Metadata Headers** - Signature in gRPC metadata

Headers:
- `x-signature`: hex-encoded signature
- `x-signer-id`: agent's address
- `x-timestamp`: unix timestamp
- `x-nonce`: random nonce
- `x-chain-id`: subnet ID

## Example Usage

See `example/grpc_example.go` for a complete example demonstrating:

- gRPC task streaming
- Intent streaming with auto-bidding
- Lifecycle callbacks
- Metrics reporting
- Graceful shutdown

Run it:
```bash
cd example
go run grpc_example.go
```

## Migration from HTTP-only

### Before (HTTP-only):
```go
config := sdk.NewConfigBuilder().
    WithMatcherAddr("http://localhost:8090").
    Build()

agent.Start()  // Manual polling required
```

### After (gRPC):
```go
config := sdk.NewConfigBuilder().
    WithMatcherAddr("localhost:8090").  // Remove http:// for gRPC
    Build()

agent.Start()  // Automatic streaming
```

## Comparison with Python SDK

| Feature | Python SDK | Go SDK | Status |
|---------|-----------|--------|--------|
| gRPC Clients | ✅ | ✅ | Complete |
| Task Streaming | ✅ | ✅ | Complete |
| Intent Streaming | ✅ | ✅ | Complete |
| Auto-Bidding | ✅ | ✅ | Complete |
| Signing Interceptor | ✅ | ✅ | Complete |
| Callbacks | ✅ | ✅ | Complete |
| Metadata Injection | ✅ | ✅ | Complete |
| HTTP Fallback | ✅ | ✅ | Complete |
| Stream Reconnection | ✅ | ✅ | Complete |

## Troubleshooting

### Import Path Issues

Make sure the protobuf import path matches your project structure:

```go
pb "github.com/pinai/protocol/Subnet/proto/subnet"
```

Update if your repo structure is different.

### gRPC Connection Issues

Enable gRPC logging:
```go
import "google.golang.org/grpc/grpclog"
grpclog.SetLoggerV2(grpclog.NewLoggerV2(os.Stdout, os.Stderr, os.Stderr))
```

### Stream Reconnection

Streams automatically reconnect with 5-second backoff on errors. Monitor logs:
```
Task stream closed, reconnecting...
Intent stream closed, reconnecting...
```

## Dependencies

```go
require (
    google.golang.org/grpc v1.59.0
    google.golang.org/protobuf v1.31.0
    github.com/ethereum/go-ethereum v1.13.0
)
```

Install:
```bash
go mod tidy
```