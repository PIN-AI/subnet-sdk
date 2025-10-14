# Subnet SDK API Reference

## Core Interfaces

### 1. Configuration

#### ConfigBuilder (Fluent API)
Builder pattern for creating SDK configuration.

**Go:**
```go
config, err := sdk.NewConfigBuilder().
    WithSubnetID(string).        // Set subnet ID (REQUIRED)
    WithAgentID(string).         // Set agent ID (REQUIRED)
    WithPrivateKey(string).      // Set private key for signing (64 hex chars)
    WithMatcherAddr(string).     // Set matcher address (REQUIRED)
    WithRegistryAddr(string).    // Set registry HTTP base (optional)
    WithAgentEndpoint(string).   // Advertised agent endpoint (required when registry is set)
    WithRegistryHeartbeatInterval(Duration). // Set registry heartbeat interval
    WithValidatorAddr(string).   // Optional fallback validator address
    WithCapabilities(...string). // Set capabilities (REQUIRED, at least 1)
    AddCapability(string).       // Add single capability
    WithTaskTimeout(Duration).   // Set task execution timeout
    WithBidTimeout(Duration).    // Set bid submission timeout
    WithMaxConcurrentTasks(int). // Set max concurrent tasks
    WithBiddingStrategy(strategy string, minPrice, maxPrice uint64).
    WithStakeAmount(uint64).     // Set stake amount
    WithOwner(string).           // Set owner address
    WithTLS(certFile, keyFile string). // Enable TLS
    WithLogLevel(string).        // Set log level
    WithDataDir(string).         // Set data directory
    Build() (*Config, error)
```

**Python:**
```python
config = ConfigBuilder() \
    .with_subnet_id(str) \        # Set subnet ID (REQUIRED)
    .with_agent_id(str) \         # Set agent ID (REQUIRED)
    .with_private_key(str) \      # Set private key (64 hex chars)
    .with_matcher_addr(str) \     # Set matcher address (REQUIRED)
    .with_registry_addr(str) \    # Set registry HTTP base
    .with_agent_endpoint(str) \  # Advertised agent endpoint for registry
    .with_registry_heartbeat_interval(int) \  # Heartbeat seconds
    .with_validator_addr(str) \   # Optional fallback validator address
    .with_capabilities(*str) \    # Set capabilities (REQUIRED)
    .add_capability(str) \        # Add single capability
    .with_task_timeout(int) \     # Timeout in seconds
    .with_bid_timeout(int) \      # Timeout in seconds
    .with_max_concurrent_tasks(int) \
    .with_bidding_strategy(str, min_price: int, max_price: int) \
    .with_stake_amount(int) \
    .with_owner(str) \
    .with_log_level(str) \
    .with_data_dir(str) \
    .build() -> Config
```

### 2. SDK Main Class

#### Initialization
**Go:**
```go
sdk, err := sdk.New(config *Config) (*SDK, error)
```

**Python:**
```python
sdk = SDK(config: Config)
```

#### Core Methods

| Method | Go Signature | Python Signature | Description |
|--------|-------------|------------------|-------------|
| Register Handler | `RegisterHandler(handler Handler)` | `register_handler(handler: Handler)` | Register task execution handler |
| Start | `Start() error` | `async start()` | Start the SDK |
| Stop | `Stop() error` | `async stop()` | Stop the SDK |
| Get Agent ID | `GetAgentID() string` | `get_agent_id() -> str` | Get agent identifier |
| Get Subnet ID | `GetSubnetID() string` | `get_subnet_id() -> str` | Get subnet identifier |
| Get Address | `GetAddress() string` | `get_address() -> Optional[str]` | Get Ethereum address |
| Get Capabilities | `GetCapabilities() []string` | `get_capabilities() -> List[str]` | Get agent capabilities |
| Get Config | `GetConfig() *Config` | `get_config() -> Config` | Get configuration copy |
| Get Metrics | `GetMetrics() *Metrics` | `get_metrics() -> Metrics` | Get metrics instance |
| Execute Task | `ExecuteTask(ctx Context, task *Task) (*Result, error)` | `async execute_task(task: Task) -> Result` | Execute a task |
| Sign | `Sign(data []byte) ([]byte, error)` | `sign(data: bytes) -> Optional[bytes]` | Sign data with private key |
| Discover Validators | `DiscoverValidators(ctx context.Context) ([]ValidatorEndpoint, error)` | `discover_validators() -> List[ValidatorEndpoint]` | Fetch active validators from the registry |
| Submit Execution Report | `SubmitExecutionReport(ctx context.Context, report *ExecutionReport) ([]*ExecutionReceipt, error)` | `submit_execution_report(report: ExecutionReport) -> List[ExecutionReceipt]` | Fan out execution reports to validators and return receipts |

### 3. Handler Interface

The core interface that must be implemented by agents.

**Go:**
```go
type Handler interface {
    Execute(ctx context.Context, task *Task) (*Result, error)
}
```

**Python:**
```python
class Handler(ABC):
    @abstractmethod
    async def execute(self, task: Task) -> Result:
        pass
```

### 4. Data Types

#### Task
Represents a task to be executed.

**Go:**
```go
type Task struct {
    ID        string            // Task identifier
    IntentID  string            // Parent intent ID
    Type      string            // Task type (e.g., "compute", "ml.inference")
    Data      []byte            // Task payload data
    Metadata  map[string]string // Additional metadata
    Deadline  time.Time         // Execution deadline
    CreatedAt time.Time         // Task creation time
}
```

**Python:**
```python
@dataclass
class Task:
    id: str                      # Task identifier
    intent_id: str               # Parent intent ID
    type: str                    # Task type
    data: bytes                  # Task payload data
    metadata: Dict[str, Any]     # Additional metadata
    deadline: datetime           # Execution deadline
    created_at: datetime         # Task creation time
```

#### Result
Represents task execution result.

**Go:**
```go
type Result struct {
    Data     []byte            // Result data
    Success  bool              // Whether execution was successful
    Error    string            // Error message if failed
    Metadata map[string]string // Result metadata
}
```

**Python:**
```python
@dataclass
class Result:
    data: bytes                     # Result data
    success: bool                   # Whether execution was successful
    error: Optional[str] = None     # Error message if failed
    metadata: Optional[Dict[str, Any]] = None
```

#### Metrics
Performance and statistics tracking.

**Go:**
```go
type Metrics struct {
    // Internal fields
}

// Methods
func (m *Metrics) RecordTaskSuccess()
func (m *Metrics) RecordTaskFailure()
func (m *Metrics) RecordBid(success bool)
func (m *Metrics) RecordReportSuccess()
func (m *Metrics) RecordReportFailure()
func (m *Metrics) GetStats() (tasksCompleted, tasksFailed, totalBids, successfulBids int64)
```

**Python:**
```python
class Metrics:
    def record_task_success(self)
    def record_task_failure(self)
    def record_bid(self, success: bool)
    def record_report_success(self)
    def record_report_failure(self)
    def get_stats(self) -> Tuple[int, int, int, int]
    # Returns: (tasks_completed, tasks_failed, total_bids, successful_bids)
```

### 5. Configuration Structure

#### Config
Main configuration object.

**Fields:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| identity.subnet_id | string | ✅ | - | Subnet identifier |
| identity.agent_id | string | ✅ | - | Agent identifier |
| private_key | string | ❌ | - | Private key (64 hex) |
| matcher_addr | string | ✅ | - | Matcher address |
| registry_addr | string | ❌ | - | Registry HTTP base for discovery |
| agent_endpoint | string | ❌ | - | Public URL advertised to the registry |
| registry_heartbeat_interval | Duration/int | ❌ | 30s | Registry heartbeat cadence |
| validator_addr | string | ❌ | - | Optional fallback validator address |
| capabilities | []string | ✅ | - | Agent capabilities |
| max_concurrent_tasks | int | ❌ | 5 | Max parallel tasks |
| task_timeout | Duration/int | ❌ | 30s | Task timeout |
| bid_timeout | Duration/int | ❌ | 5s | Bid timeout |
| bidding_strategy | string | ❌ | "fixed" | Bidding strategy |
| min_bid_price | uint64/int | ❌ | 100 | Minimum bid price |
| max_bid_price | uint64/int | ❌ | 1000 | Maximum bid price |
| stake_amount | uint64/int | ❌ | 0 | Stake amount |
| owner | string | ❌ | - | Owner address |
| log_level | string | ❌ | "INFO" | Logging level |
| data_dir | string | ❌ | - | Data directory |

## Error Handling

### Go Errors
```go
// Configuration errors
errors.New("subnet_id must be configured")
errors.New("agent_id must be configured")
errors.New("matcher_addr must be configured")
errors.New("at least one capability must be configured")
errors.New("private key must be 32 bytes (64 hex characters)")

// Runtime errors
errors.New("SDK already running")
errors.New("SDK not running")
errors.New("no handler registered")
```

### Python Exceptions
```python
# Configuration errors
ValueError("subnet_id must be configured")
ValueError("agent_id must be configured")
ValueError("matcher_addr must be configured")
ValueError("at least one capability must be configured")
ValueError("private_key must be 32 bytes (64 hex characters)")

# Runtime errors
RuntimeError("SDK already running")
RuntimeError("SDK not running")
RuntimeError("No handler registered")
```

## Thread Safety

- **Go SDK**: All public methods are thread-safe
- **Python SDK**: Uses asyncio locks for thread safety

## Best Practices

1. **Always validate configuration** before creating SDK instance
2. **Never hardcode private keys** - use environment variables or secure storage
3. **Implement proper error handling** in your Handler
4. **Use context/timeout** for task execution
5. **Monitor metrics** regularly for performance tracking
6. **Clean shutdown** - always call Stop() when terminating