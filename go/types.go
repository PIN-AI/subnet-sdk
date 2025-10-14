package agentsdk

import (
	"context"
	"sync/atomic"
	"time"
)

// Task represents a task to be executed by the agent
type Task struct {
	ID        string            // Task identifier
	IntentID  string            // Parent intent ID
	Type      string            // Task type (e.g., "weather", "ml.inference")
	Data      []byte            // Task payload data
	Metadata  map[string]string // Additional metadata
	Deadline  time.Time         // Execution deadline
	CreatedAt time.Time         // Task creation time
}

// Result represents the execution result
type Result struct {
	Data     []byte            // Result data
	Success  bool              // Whether execution was successful
	Error    string            // Error message if failed
	Metadata map[string]string // Result metadata
}

// ExecutionReportStatus represents execution report status values understood by validators
type ExecutionReportStatus string

const (
	ExecutionReportStatusUnspecified ExecutionReportStatus = "status_unspecified"
	ExecutionReportStatusSuccess     ExecutionReportStatus = "success"
	ExecutionReportStatusFailed      ExecutionReportStatus = "failed"
	ExecutionReportStatusPartial     ExecutionReportStatus = "partial"
)

// ExecutionReport models the payload sent from agents to validators
type ExecutionReport struct {
	ReportID     string
	AssignmentID string
	IntentID     string
	AgentID      string
	Status       ExecutionReportStatus
	ResultData   []byte
	Timestamp    time.Time
	Metadata     map[string]string
}

// ExecutionReceipt captures validator acknowledgements for reports
type ExecutionReceipt struct {
	ReportID    string
	IntentID    string
	ValidatorID string
	Status      string
	ReceivedAt  time.Time
	Message     string
	Endpoint    string
}

// Intent represents an intent for bidding
type Intent struct {
	ID          string    // Intent ID
	Type        string    // Intent type
	Description string    // Intent description
	CreatedAt   time.Time // When the intent was created
}

// Bid represents a bid for an intent
//
// IMPORTANT: When implementing bid submission logic (e.g., SubmitBid), ensure that
// the chain address is automatically included in bid metadata by calling:
//
//	bidMetadata := ensureChainAddressMetadata(bid.Metadata, sdk.GetChainAddress())
//
// This ensures consistency with ExecutionReport handling and matches the Python SDK behavior.
// See ensureChainAddressMetadata() in sdk.go for the implementation.
type Bid struct {
	Price    uint64 // Bid price
	Currency string // Currency (e.g., "PIN")
	Metadata map[string]string
}

// AgentInfo contains agent information
type AgentInfo struct {
	AgentID      string   // Agent identifier
	Capabilities []string // Agent capabilities
	Status       string   // Current status
}

// Handler is the interface that agent operators must implement
type Handler interface {
	// Execute handles task execution
	Execute(ctx context.Context, task *Task) (*Result, error)
}

// BiddingStrategy defines custom bidding behavior (optional)
type BiddingStrategy interface {
	// ShouldBid decides whether to bid on an intent
	ShouldBid(intent *Intent) bool
	// CalculateBid calculates the bid price
	CalculateBid(intent *Intent) *Bid
}

// Callbacks for lifecycle events (optional)
type Callbacks interface {
	// OnStart is called when the agent starts
	OnStart() error
	// OnStop is called when the agent stops
	OnStop() error
	// OnTaskAccepted is called when a task is accepted
	OnTaskAccepted(task *Task)
	// OnTaskRejected is called when a task is rejected
	OnTaskRejected(task *Task, reason string)
	// OnTaskCompleted is called after task execution
	OnTaskCompleted(task *Task, result *Result, err error)
	// OnBidSubmitted is called when a bid is submitted
	OnBidSubmitted(intent *Intent, bid *Bid)
	// OnBidWon is called when a bid is won
	OnBidWon(intentID string)
	// OnBidLost is called when a bid is lost
	OnBidLost(intentID string)
	// OnError is called when an error occurs
	OnError(err error)
}

// Metrics represents agent metrics
type Metrics struct {
	TasksCompleted   int64
	TasksFailed      int64
	AverageExecTime  time.Duration
	CurrentTasks     int32
	TotalBids        int64
	SuccessfulBids   int64
	TotalEarnings    uint64
	ReportsSubmitted int64
	ReportsFailed    int64
}

// NewMetrics creates new metrics instance
func NewMetrics() *Metrics {
	return &Metrics{}
}

// RecordTaskSuccess records a successful task
func (m *Metrics) RecordTaskSuccess() {
	atomic.AddInt64(&m.TasksCompleted, 1)
}

// RecordTaskFailure records a failed task
func (m *Metrics) RecordTaskFailure() {
	atomic.AddInt64(&m.TasksFailed, 1)
}

// RecordBid records a bid attempt
func (m *Metrics) RecordBid(success bool) {
	atomic.AddInt64(&m.TotalBids, 1)
	if success {
		atomic.AddInt64(&m.SuccessfulBids, 1)
	}
}

// RecordReportSuccess records a successful execution report submission
func (m *Metrics) RecordReportSuccess() {
	atomic.AddInt64(&m.ReportsSubmitted, 1)
}

// RecordReportFailure records a failed execution report submission attempt
func (m *Metrics) RecordReportFailure() {
	atomic.AddInt64(&m.ReportsFailed, 1)
}

// GetStats returns current metrics
func (m *Metrics) GetStats() (tasksCompleted, tasksFailed, totalBids, successfulBids int64) {
	return atomic.LoadInt64(&m.TasksCompleted),
		atomic.LoadInt64(&m.TasksFailed),
		atomic.LoadInt64(&m.TotalBids),
		atomic.LoadInt64(&m.SuccessfulBids)
}

// Authentication types (temporary until proto is updated)

// AuthRequest represents authentication request
type AuthRequest struct {
	AgentId   string
	Address   string
	PublicKey []byte
	Signature []byte
	Timestamp int64
	Nonce     string
}

// AuthResponse represents authentication response
type AuthResponse struct {
	Success      bool
	Message      string
	SessionToken string
}

// RegisterCapabilitiesRequest represents capability registration
type RegisterCapabilitiesRequest struct {
	AgentId      string
	Capabilities []string
	StakeAmount  uint64
	Owner        string
	Signature    []byte
}

// Marshal marshals the request (mock implementation)
func (r *RegisterCapabilitiesRequest) Marshal() ([]byte, error) {
	// This would use protobuf marshaling in real implementation
	return []byte(r.AgentId), nil
}

// RegisterCapabilitiesResponse represents registration response
type RegisterCapabilitiesResponse struct {
	Success            bool
	Message            string
	GrantedPermissions []string
}
