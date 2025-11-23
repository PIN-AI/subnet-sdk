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
    WithChainAddress(string).    // Set on-chain address (optional, derived from private key if not set)
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
    .with_chain_address(str) \    # Set on-chain address (optional)
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
| Register Bidding Strategy | `RegisterBiddingStrategy(strategy BiddingStrategy)` | `register_bidding_strategy(strategy: BiddingStrategy)` | Register custom bidding strategy |
| Register Callbacks | `RegisterCallbacks(callbacks Callbacks)` | `register_callbacks(callbacks: Callbacks)` | Register lifecycle callbacks |
| Start | `Start() error` | `async start()` | Start the SDK |
| Stop | `Stop() error` | `async stop()` | Stop the SDK |
| Get Agent ID | `GetAgentID() string` | `get_agent_id() -> str` | Get agent identifier |
| Get Subnet ID | `GetSubnetID() string` | `get_subnet_id() -> str` | Get subnet identifier |
| Get Address | `GetAddress() string` | `get_address() -> Optional[str]` | Get Ethereum address (derived from private key) |
| Get Chain Address | `GetChainAddress() string` | `get_chain_address() -> Optional[str]` | Get configured on-chain address |
| Get Capabilities | `GetCapabilities() []string` | `get_capabilities() -> List[str]` | Get agent capabilities |
| Get Config | `GetConfig() *Config` | `get_config() -> Config` | Get configuration copy |
| Get Metrics | `GetMetrics() *Metrics` | `get_metrics() -> Metrics` | Get metrics instance |
| Execute Task | `ExecuteTask(ctx Context, task *Task) (*Result, error)` | `async execute_task(task: Task) -> Result` | Execute a task |
| Sign | `Sign(data []byte) ([]byte, error)` | `sign(data: bytes) -> bytes` | Sign data with private key |
| Discover Validators | `DiscoverValidators(ctx context.Context) ([]ValidatorEndpoint, error)` | `async discover_validators() -> List[ValidatorEndpoint]` | Fetch active validators from the registry |
| Submit Execution Report | `SubmitExecutionReport(ctx context.Context, report *ExecutionReport) ([]*ExecutionReceipt, error)` | `async submit_execution_report(report: ExecutionReport) -> List[ExecutionReceipt]` | Fan out execution reports to validators and return receipts |
| Get Execution Report | `GetExecutionReport(ctx context.Context, reportID string) (*ExecutionReport, error)` | - | Retrieve a single execution report by ID (Go only) |
| List Execution Reports | `ListExecutionReports(ctx context.Context, intentID string, limit uint32) ([]*ExecutionReport, error)` | - | List execution reports, optionally filtered by intent ID (Go only) |

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

#### Intent
Represents an intent for bidding.

**Go:**
```go
type Intent struct {
    ID          string    // Intent identifier
    Type        string    // Intent type
    Description string    // Intent description
    CreatedAt   time.Time // When the intent was created
}
```

**Python:**
```python
@dataclass
class Intent:
    id: str              # Intent identifier
    type: str            # Intent type
    description: str     # Intent description
    created_at: datetime # When the intent was created
```

#### Bid
Represents a bid for an intent.

**Go:**
```go
type Bid struct {
    Price    uint64            // Bid price
    Currency string            // Currency (e.g., "PIN")
    Metadata map[string]string // Optional metadata
}
```

**Python:**
```python
@dataclass
class Bid:
    price: int                           # Bid price
    currency: str = "PIN"                # Currency
    metadata: Optional[Dict[str, Any]] = None
```

#### ExecutionReport
Payload sent from agents to validators.

**Go:**
```go
type ExecutionReport struct {
    ReportID     string
    AssignmentID string
    IntentID     string
    AgentID      string
    Status       ExecutionReportStatus  // "success", "failed", "partial"
    ResultData   []byte
    Timestamp    time.Time
    Metadata     map[string]string
}
```

**Python:**
```python
@dataclass
class ExecutionReport:
    report_id: str
    assignment_id: str
    intent_id: str
    agent_id: Optional[str] = None
    status: ExecutionReportStatus = ExecutionReportStatus.SUCCESS
    result_data: Optional[bytes] = None
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, str]] = None
```

#### ExecutionReceipt
Response returned by validators for execution reports.

**Go:**
```go
type ExecutionReceipt struct {
    ReportID    string
    IntentID    string
    ValidatorID string
    Status      string
    ReceivedAt  time.Time
    Message     string
    Endpoint    string
}
```

**Python:**
```python
@dataclass
class ExecutionReceipt:
    report_id: str
    intent_id: str
    validator_id: str
    status: str
    message: Optional[str] = None
    received_at: Optional[datetime] = None
    endpoint: Optional[str] = None
```

#### ValidatorEndpoint
Validator discovery information from registry service.

**Go:**
```go
type ValidatorEndpoint struct {
    ID       string
    Endpoint string
    Status   string
    LastSeen time.Time
}
```

**Python:**
```python
@dataclass
class ValidatorEndpoint:
    id: str
    endpoint: str
    status: str
    last_seen: Optional[datetime] = None
```

### 5. BiddingStrategy Interface

Optional interface for custom bidding behavior.

**Go:**
```go
type BiddingStrategy interface {
    // ShouldBid decides whether to bid on an intent
    ShouldBid(intent *Intent) bool
    // CalculateBid calculates the bid price
    CalculateBid(intent *Intent) *Bid
}
```

**Python:**
```python
class BiddingStrategy(ABC):
    @abstractmethod
    def should_bid(self, intent: Intent) -> bool:
        """Return True if the agent should bid on the given intent."""

    @abstractmethod
    def calculate_bid(self, intent: Intent) -> Bid:
        """Produce a bid for the provided intent."""
```

**Example Implementation:**
```go
type MyBiddingStrategy struct{}

func (s *MyBiddingStrategy) ShouldBid(intent *Intent) bool {
    return intent.Type == "compute"  // Only bid on compute tasks
}

func (s *MyBiddingStrategy) CalculateBid(intent *Intent) *Bid {
    return &Bid{Price: 100, Currency: "PIN"}
}

// Register with SDK
sdk.RegisterBiddingStrategy(&MyBiddingStrategy{})
```

### 6. Callbacks Interface

Optional lifecycle callbacks for monitoring agent events.

**Go:**
```go
type Callbacks interface {
    OnStart() error
    OnStop() error
    OnTaskAccepted(task *Task)
    OnTaskRejected(task *Task, reason string)
    OnTaskCompleted(task *Task, result *Result, err error)
    OnBidSubmitted(intent *Intent, bid *Bid)
    OnBidWon(intentID string)
    OnBidLost(intentID string)
    OnError(err error)
}
```

**Python:**
```python
class Callbacks(ABC):
    async def on_start(self) -> None: pass
    async def on_stop(self) -> None: pass
    async def on_task_accepted(self, task: Task) -> None: pass
    async def on_task_rejected(self, task: Task, reason: str) -> None: pass
    async def on_task_completed(self, task: Task, result: Result) -> None: pass
    async def on_report_submitted(self, report_id: str) -> None: pass
    async def on_report_failed(self, report_id: str, error: str) -> None: pass
    async def on_bid_submitted(self, intent_id: str, bid_id: str) -> None: pass
    async def on_bid_failed(self, intent_id: str, bid_id: str, reason: str) -> None: pass
    async def on_error(self, error: BaseException) -> None: pass
```

**Example Implementation:**
```go
type MyCallbacks struct{}

func (c *MyCallbacks) OnStart() error {
    log.Println("Agent started")
    return nil
}
func (c *MyCallbacks) OnStop() error {
    log.Println("Agent stopped")
    return nil
}
func (c *MyCallbacks) OnTaskAccepted(task *Task) {
    log.Printf("Task accepted: %s", task.ID)
}
func (c *MyCallbacks) OnTaskRejected(task *Task, reason string) {
    log.Printf("Task rejected: %s - %s", task.ID, reason)
}
func (c *MyCallbacks) OnTaskCompleted(task *Task, result *Result, err error) {
    log.Printf("Task completed: %s, success: %v", task.ID, result.Success)
}
func (c *MyCallbacks) OnBidSubmitted(intent *Intent, bid *Bid) {
    log.Printf("Bid submitted for intent: %s", intent.ID)
}
func (c *MyCallbacks) OnBidWon(intentID string) {
    log.Printf("Won bid for intent: %s", intentID)
}
func (c *MyCallbacks) OnBidLost(intentID string) {
    log.Printf("Lost bid for intent: %s", intentID)
}
func (c *MyCallbacks) OnError(err error) {
    log.Printf("Error: %v", err)
}

// Register with SDK
sdk.RegisterCallbacks(&MyCallbacks{})
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

### 7. Configuration Structure

#### Config
Main configuration object.

**Fields:**
| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| identity.subnet_id | string | ✅ | - | Subnet identifier |
| identity.agent_id | string | ✅ | - | Agent identifier |
| private_key | string | ❌ | - | Private key (64 hex) |
| chain_address | string | ❌ | - | On-chain address (derived from private_key if not set) |
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