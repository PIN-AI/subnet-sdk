package agentsdk

import (
	"bytes"
	"context"
	"crypto/ecdsa"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
)

// SDK provides the core agent functionality
type SDK struct {
	config          *Config
	handler         Handler
	biddingStrategy BiddingStrategy
	callbacks       Callbacks
	privateKey      *ecdsa.PrivateKey
	address         string
	metrics         *Metrics
	mu              sync.RWMutex
	running         bool
	httpClient      *http.Client
	registryCancel  context.CancelFunc
	registryWG      sync.WaitGroup
	matcherClient   *MatcherClient
	validatorClient *ValidatorClient
	matcherCancel   context.CancelFunc
	matcherWG       sync.WaitGroup
}

const defaultReportTimeout = 10 * time.Second
const chainAddressMetadataKey = "chain_address"

// Config holds SDK configuration
type Config struct {
	Identity                  *IdentityConfig
	AgentID                   string
	PrivateKey                string
	ChainAddress              string
	MatcherAddr               string
	ValidatorAddr             string
	Capabilities              []string
	MaxConcurrentTasks        int
	TaskTimeout               time.Duration
	BidTimeout                time.Duration
	BiddingStrategy           string
	MinBidPrice               uint64
	MaxBidPrice               uint64
	Owner                     string
	StakeAmount               uint64
	UseTLS                    bool
	CertFile                  string
	KeyFile                   string
	LogLevel                  string
	DataDir                   string
	Timeouts                  *TimeoutConfig
	RegistryAddr              string
	AgentEndpoint             string
	RegistryHeartbeatInterval time.Duration
}

// ValidatorEndpoint contains validator discovery information
type ValidatorEndpoint struct {
	ID       string
	Endpoint string
	Status   string
	LastSeen time.Time
}

// IdentityConfig holds identity information
type IdentityConfig struct {
	SubnetID    string
	ValidatorID string
	MatcherID   string
	AgentID     string
}

// TimeoutConfig holds timeout settings
type TimeoutConfig struct {
	TaskTimeout time.Duration
	BidTimeout  time.Duration
}

// New creates a new SDK instance
func New(config *Config) (*SDK, error) {
	if err := config.Validate(); err != nil {
		return nil, fmt.Errorf("invalid config: %w", err)
	}

	// Apply defaults
	config.applyDefaults()

	var privateKey *ecdsa.PrivateKey
	var address string

	if config.PrivateKey != "" {
		key, err := crypto.HexToECDSA(config.PrivateKey)
		if err != nil {
			return nil, fmt.Errorf("invalid private key: %w", err)
		}
		privateKey = key
		address = crypto.PubkeyToAddress(key.PublicKey).Hex()
	}

	if address != "" && config.ChainAddress != "" && !strings.EqualFold(address, config.ChainAddress) {
		return nil, fmt.Errorf("chain_address does not match derived address from private key")
	}

	if address == "" && config.ChainAddress != "" {
		address = common.HexToAddress(config.ChainAddress).Hex()
	}

	if address != "" {
		config.ChainAddress = address
	}

	return &SDK{
		config:     config,
		privateKey: privateKey,
		address:    address,
		metrics:    NewMetrics(),
		running:    false,
		httpClient: &http.Client{Timeout: 10 * time.Second},
	}, nil
}

// RegisterHandler sets the task handler
func (sdk *SDK) RegisterHandler(handler Handler) {
	sdk.mu.Lock()
	defer sdk.mu.Unlock()
	sdk.handler = handler
}

// RegisterBiddingStrategy sets the bidding strategy
func (sdk *SDK) RegisterBiddingStrategy(strategy BiddingStrategy) {
	sdk.mu.Lock()
	defer sdk.mu.Unlock()
	sdk.biddingStrategy = strategy
}

// RegisterCallbacks sets lifecycle callbacks
func (sdk *SDK) RegisterCallbacks(callbacks Callbacks) {
	sdk.mu.Lock()
	defer sdk.mu.Unlock()
	sdk.callbacks = callbacks
}

// Start starts the SDK
func (sdk *SDK) Start() error {
	log.Printf("[SDK DEBUG] Start() called")
	sdk.mu.Lock()
	defer sdk.mu.Unlock()

	log.Printf("[SDK DEBUG] Acquired lock")

	if sdk.running {
		return errors.New("SDK already running")
	}

	if sdk.handler == nil {
		return errors.New("no handler registered")
	}

	log.Printf("[SDK DEBUG] Calling registerWithRegistry()...")
	if err := sdk.registerWithRegistry(); err != nil {
		return fmt.Errorf("registry registration failed: %w", err)
	}
	log.Printf("[SDK DEBUG] registerWithRegistry() completed")

	// Initialize gRPC clients
	log.Printf("[SDK DEBUG] Calling initGRPCClients()...")
	if err := sdk.initGRPCClients(); err != nil {
		return fmt.Errorf("failed to initialize gRPC clients: %w", err)
	}
	log.Printf("[SDK DEBUG] initGRPCClients() completed")

	// Start matcher streams
	log.Printf("[SDK DEBUG] Calling startMatcherStreams()...")
	if err := sdk.startMatcherStreams(); err != nil {
		sdk.closeGRPCClients()
		return fmt.Errorf("failed to start matcher streams: %w", err)
	}
	log.Printf("[SDK DEBUG] startMatcherStreams() completed")

	log.Printf("[SDK DEBUG] Setting sdk.running = true")
	sdk.running = true
	log.Printf("[SDK DEBUG] sdk.running set to true")

	log.Printf("[SDK DEBUG] Calling fireCallback(OnStart)...")
	sdk.fireCallback("OnStart")
	log.Printf("[SDK DEBUG] fireCallback(OnStart) completed")

	// Get agent ID before logging (GetAgentID() acquires a read lock, which would deadlock)
	var agentID string
	if sdk.config.Identity != nil {
		agentID = sdk.config.Identity.AgentID
	} else {
		agentID = sdk.config.AgentID
	}

	log.Printf("[SDK DEBUG] About to log final message and return")
	log.Printf("SDK started with agent ID: %s", agentID)
	log.Printf("[SDK DEBUG] Returning nil from Start()")
	return nil
}

// Stop stops the SDK
func (sdk *SDK) Stop() error {
	sdk.mu.Lock()
	defer sdk.mu.Unlock()

	if !sdk.running {
		return errors.New("SDK not running")
	}

	sdk.running = false
	sdk.stopMatcherStreams()
	sdk.closeGRPCClients()
	sdk.stopRegistry()
	sdk.fireCallback("OnStop")
	log.Printf("SDK stopped")
	return nil
}

// GetAgentID returns the agent ID
func (sdk *SDK) GetAgentID() string {
	sdk.mu.RLock()
	defer sdk.mu.RUnlock()
	if sdk.config.Identity != nil {
		return sdk.config.Identity.AgentID
	}
	return sdk.config.AgentID
}

// GetSubnetID returns the subnet ID
func (sdk *SDK) GetSubnetID() string {
	sdk.mu.RLock()
	defer sdk.mu.RUnlock()
	if sdk.config.Identity != nil {
		return sdk.config.Identity.SubnetID
	}
	return ""
}

// GetAddress returns the agent's blockchain address
func (sdk *SDK) GetAddress() string {
	sdk.mu.RLock()
	defer sdk.mu.RUnlock()
	return sdk.address
}

// GetChainAddress returns the configured on-chain address (alias of GetAddress).
func (sdk *SDK) GetChainAddress() string {
	return sdk.GetAddress()
}

// GetCapabilities returns the agent's capabilities
func (sdk *SDK) GetCapabilities() []string {
	sdk.mu.RLock()
	defer sdk.mu.RUnlock()
	return append([]string{}, sdk.config.Capabilities...)
}

// GetConfig returns a copy of the configuration
func (sdk *SDK) GetConfig() *Config {
	sdk.mu.RLock()
	defer sdk.mu.RUnlock()

	configCopy := *sdk.config
	if sdk.config.Identity != nil {
		identityCopy := *sdk.config.Identity
		configCopy.Identity = &identityCopy
	}
	if sdk.config.Timeouts != nil {
		timeoutsCopy := *sdk.config.Timeouts
		configCopy.Timeouts = &timeoutsCopy
	}
	configCopy.Capabilities = append([]string{}, sdk.config.Capabilities...)

	return &configCopy
}

// GetMetrics returns the current metrics
func (sdk *SDK) GetMetrics() *Metrics {
	return sdk.metrics
}

// ExecuteTask executes a task using the registered handler
func (sdk *SDK) ExecuteTask(ctx context.Context, task *Task) (*Result, error) {
	if !sdk.running {
		return nil, errors.New("SDK not running")
	}

	if sdk.handler == nil {
		return nil, errors.New("no handler registered")
	}

	// Set timeout
	timeout := sdk.config.TaskTimeout
	if timeout == 0 {
		timeout = 30 * time.Second
	}

	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	// Record metrics
	start := time.Now()

	result, err := sdk.handler.Execute(ctx, task)

	duration := time.Since(start)
	if err != nil {
		sdk.metrics.RecordTaskFailure()
	} else {
		sdk.metrics.RecordTaskSuccess()
	}

	log.Printf("Task %s completed in %v", task.ID, duration)
	return result, err
}

// Sign signs data with the private key
func (sdk *SDK) Sign(data []byte) ([]byte, error) {
	if sdk.privateKey == nil {
		return nil, errors.New("no private key configured")
	}

	hash := crypto.Keccak256Hash(data)
	signature, err := crypto.Sign(hash.Bytes(), sdk.privateKey)
	if err != nil {
		return nil, fmt.Errorf("failed to sign: %w", err)
	}

	return signature, nil
}

func (sdk *SDK) registerWithRegistry() error {
	if sdk.config.RegistryAddr == "" {
		return nil
	}

	payload := map[string]interface{}{
		"id":           sdk.GetAgentID(),
		"capabilities": sdk.GetCapabilities(),
		"endpoint":     sdk.config.AgentEndpoint,
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal payload: %w", err)
	}

	req, err := http.NewRequest(http.MethodPost, sdk.registryURL("/agents"), bytes.NewReader(body))
	if err != nil {
		return fmt.Errorf("build request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := sdk.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("register agent: %w", err)
	}
	defer resp.Body.Close()
	if resp.StatusCode >= 300 {
		return fmt.Errorf("register agent: registry returned %s", resp.Status)
	}

	hbCtx, hbCancel := context.WithCancel(context.Background())
	sdk.registryCancel = hbCancel
	sdk.registryWG.Add(1)
	go sdk.heartbeatLoop(hbCtx)

	return nil
}

func (sdk *SDK) heartbeatLoop(ctx context.Context) {
	defer sdk.registryWG.Done()

	interval := sdk.config.RegistryHeartbeatInterval
	if interval <= 0 {
		interval = 30 * time.Second
	}
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			req, err := http.NewRequest(http.MethodPost, sdk.registryURL("/agents/"+sdk.GetAgentID()+"/heartbeat"), nil)
			if err != nil {
				log.Printf("registry heartbeat build error: %v", err)
				continue
			}
			req.Header.Set("Content-Type", "application/json")

			resp, err := sdk.httpClient.Do(req)
			if err != nil {
				log.Printf("registry heartbeat failed: %v", err)
				continue
			}
			resp.Body.Close()
			if resp.StatusCode >= 300 {
				log.Printf("registry heartbeat unexpected status: %s", resp.Status)
			}
		}
	}
}

func (sdk *SDK) stopRegistry() {
	if sdk.registryCancel != nil {
		sdk.registryCancel()
		sdk.registryWG.Wait()
		sdk.registryCancel = nil
	}

	if sdk.config.RegistryAddr != "" {
		req, err := http.NewRequest(http.MethodDelete, sdk.registryURL("/agents/"+sdk.GetAgentID()), nil)
		if err == nil {
			resp, err := sdk.httpClient.Do(req)
			if err != nil {
				log.Printf("failed to unregister agent: %v", err)
			} else {
				resp.Body.Close()
				if resp.StatusCode >= 300 {
					log.Printf("unregister agent returned %s", resp.Status)
				}
			}
		}
	}
}

func (sdk *SDK) registryURL(path string) string {
	base := strings.TrimSuffix(sdk.config.RegistryAddr, "/")
	if base == "" {
		return path
	}
	if !strings.HasPrefix(base, "http://") && !strings.HasPrefix(base, "https://") {
		base = "http://" + base
	}
	if !strings.HasPrefix(path, "/") {
		path = "/" + path
	}
	return base + path
}

// DiscoverValidators fetches active validator endpoints from the registry
func (sdk *SDK) DiscoverValidators(ctx context.Context) ([]ValidatorEndpoint, error) {
	if sdk.config.RegistryAddr == "" {
		return nil, errors.New("registry_addr not configured")
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, sdk.registryURL("/validators"), nil)
	if err != nil {
		return nil, fmt.Errorf("build request: %w", err)
	}

	resp, err := sdk.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("fetch validators: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 300 {
		return nil, fmt.Errorf("fetch validators: registry returned %s", resp.Status)
	}

	var payload struct {
		Validators []struct {
			ID       string `json:"id"`
			Endpoint string `json:"endpoint"`
			Status   string `json:"status"`
			LastSeen int64  `json:"last_seen"`
		} `json:"validators"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&payload); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}

	validators := make([]ValidatorEndpoint, 0, len(payload.Validators))
	for _, v := range payload.Validators {
		validators = append(validators, ValidatorEndpoint{
			ID:       v.ID,
			Endpoint: v.Endpoint,
			Status:   v.Status,
			LastSeen: time.Unix(v.LastSeen, 0),
		})
	}

	return validators, nil
}

// SubmitExecutionReport sends the execution report to all discovered validators
func (sdk *SDK) SubmitExecutionReport(ctx context.Context, report *ExecutionReport) ([]*ExecutionReceipt, error) {
	if report == nil {
		return nil, errors.New("execution report is required")
	}

	reportID := strings.TrimSpace(report.ReportID)
	if reportID == "" {
		return nil, errors.New("report_id is required")
	}

	assignmentID := strings.TrimSpace(report.AssignmentID)
	if assignmentID == "" {
		return nil, errors.New("assignment_id is required")
	}

	intentID := strings.TrimSpace(report.IntentID)
	if intentID == "" {
		return nil, errors.New("intent_id is required")
	}

	agentID := strings.TrimSpace(report.AgentID)
	if agentID == "" {
		agentID = sdk.GetAgentID()
	}
	if agentID == "" {
		return nil, errors.New("agent_id is required")
	}

	status := report.Status
	if status == "" {
		status = ExecutionReportStatusSuccess
	}
	if !isValidExecutionStatus(status) {
		return nil, fmt.Errorf("invalid status: %s", status)
	}

	timestamp := report.Timestamp
	if timestamp.IsZero() {
		timestamp = time.Now()
	}

	endpoints, endpointErrs := sdk.validatorReportEndpoints(ctx)
	if len(endpoints) == 0 {
		if len(endpointErrs) == 0 {
			return nil, errors.New("no validator endpoints available")
		}
		return nil, errors.Join(endpointErrs...)
	}

	encodedResult := ""
	if len(report.ResultData) > 0 {
		encodedResult = base64.StdEncoding.EncodeToString(report.ResultData)
	}

	metadata := ensureChainAddressMetadata(report.Metadata, sdk.GetChainAddress())
	report.Metadata = metadata

	payload := executionReportRequest{
		ReportID:     reportID,
		AssignmentID: assignmentID,
		IntentID:     intentID,
		AgentID:      agentID,
		Status:       string(status),
		ResultData:   encodedResult,
		Timestamp:    timestamp.Unix(),
		Metadata:     metadata,
	}

	var (
		receipts   []*ExecutionReceipt
		submitErrs []error
	)

	for _, endpoint := range endpoints {
		receipt, err := sdk.postExecutionReport(ctx, endpoint, payload)
		if err != nil {
			submitErrs = append(submitErrs, fmt.Errorf("%s: %w", endpoint, err))
			sdk.metrics.RecordReportFailure()
			continue
		}

		receipt.Endpoint = endpoint
		receipts = append(receipts, receipt)
		sdk.metrics.RecordReportSuccess()
	}

	if len(receipts) == 0 {
		if len(submitErrs) == 0 {
			return nil, errors.New("validator submissions returned no receipts")
		}
		return nil, errors.Join(submitErrs...)
	}

	if len(submitErrs) > 0 {
		return receipts, errors.Join(submitErrs...)
	}

	return receipts, nil
}

type executionReportRequest struct {
	ReportID     string            `json:"report_id"`
	AssignmentID string            `json:"assignment_id"`
	IntentID     string            `json:"intent_id"`
	AgentID      string            `json:"agent_id"`
	Status       string            `json:"status,omitempty"`
	ResultData   string            `json:"result_data,omitempty"`
	Timestamp    int64             `json:"timestamp"`
	Metadata     map[string]string `json:"metadata,omitempty"`
}

func isValidExecutionStatus(status ExecutionReportStatus) bool {
	switch status {
	case ExecutionReportStatusUnspecified,
		ExecutionReportStatusSuccess,
		ExecutionReportStatusFailed,
		ExecutionReportStatusPartial:
		return true
	default:
		return false
	}
}

// ensureChainAddressMetadata ensures that the chain address is included in metadata.
// This function is used to automatically inject the agent's on-chain address into
// execution reports and bid submissions.
//
// Usage:
//   - For execution reports: called in SubmitExecutionReport() (line 504)
//   - For bid submissions: MUST be called when implementing SubmitBid()
//
// Example for future bid implementation:
//
//	bidMetadata := ensureChainAddressMetadata(bid.Metadata, sdk.GetChainAddress())
//	// ... then use bidMetadata in the bid request
//
// This ensures consistency across all metadata-bearing requests and matches
// the Python SDK's behavior (see Python SDK's _ensure_chain_metadata).
func ensureChainAddressMetadata(src map[string]string, addr string) map[string]string {
	if src == nil && addr == "" {
		return nil
	}

	var metadata map[string]string
	if src != nil {
		metadata = cloneStringMap(src)
	} else {
		metadata = make(map[string]string)
	}

	if addr != "" {
		normalized := common.HexToAddress(addr).Hex()
		if _, ok := metadata[chainAddressMetadataKey]; !ok {
			metadata[chainAddressMetadataKey] = normalized
		}
	}

	return metadata
}

func cloneStringMap(src map[string]string) map[string]string {
	clone := make(map[string]string, len(src)+1)
	for k, v := range src {
		clone[k] = v
	}
	return clone
}

func (sdk *SDK) validatorReportEndpoints(ctx context.Context) ([]string, []error) {
	seen := make(map[string]struct{})
	var (
		endpoints []string
		errs      []error
	)

	addEndpoint := func(raw string) {
		urlStr, err := buildExecutionReportURL(raw)
		if err != nil {
			errs = append(errs, fmt.Errorf("%s: %w", raw, err))
			return
		}
		if urlStr == "" {
			return
		}
		if _, exists := seen[urlStr]; exists {
			return
		}
		seen[urlStr] = struct{}{}
		endpoints = append(endpoints, urlStr)
	}

	if sdk.config.RegistryAddr != "" {
		validators, err := sdk.DiscoverValidators(ctx)
		if err != nil {
			errs = append(errs, fmt.Errorf("discover validators: %w", err))
		} else {
			for _, validator := range validators {
				addEndpoint(validator.Endpoint)
			}
		}
	}

	if sdk.config.ValidatorAddr != "" {
		addEndpoint(sdk.config.ValidatorAddr)
	}

	if len(endpoints) > 1 {
		sort.Strings(endpoints)
	}

	return endpoints, errs
}

func buildExecutionReportURL(endpoint string) (string, error) {
	trimmed := strings.TrimSpace(endpoint)
	if trimmed == "" {
		return "", nil
	}
	if !strings.HasPrefix(trimmed, "http://") && !strings.HasPrefix(trimmed, "https://") {
		trimmed = "http://" + trimmed
	}

	parsed, err := url.Parse(trimmed)
	if err != nil {
		return "", err
	}

	path := strings.TrimSuffix(parsed.Path, "/")
	if path == "" || path == "/" {
		parsed.Path = "/api/v1/execution-report"
	} else if strings.HasSuffix(path, "/api/v1/execution-report") {
		parsed.Path = path
	} else {
		parsed.Path = path + "/api/v1/execution-report"
	}

	return parsed.String(), nil
}

func (sdk *SDK) postExecutionReport(parentCtx context.Context, endpoint string, payload executionReportRequest) (*ExecutionReceipt, error) {
	body, err := json.Marshal(payload)
	if err != nil {
		return nil, fmt.Errorf("marshal payload: %w", err)
	}

	timeout := defaultReportTimeout
	if deadline, ok := parentCtx.Deadline(); ok {
		remaining := time.Until(deadline)
		if remaining > 0 && remaining < timeout {
			timeout = remaining
		}
		if remaining <= 0 {
			return nil, context.DeadlineExceeded
		}
	}

	reqCtx, cancel := context.WithTimeout(parentCtx, timeout)
	defer cancel()

	req, err := http.NewRequestWithContext(reqCtx, http.MethodPost, endpoint, bytes.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("build request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	resp, err := sdk.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("submit report: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= http.StatusMultipleChoices {
		msg, _ := io.ReadAll(io.LimitReader(resp.Body, 1024))
		msgText := strings.TrimSpace(string(msg))
		if msgText != "" {
			return nil, fmt.Errorf("validator returned %s: %s", resp.Status, msgText)
		}
		return nil, fmt.Errorf("validator returned %s", resp.Status)
	}

	var reply struct {
		ReportID    string `json:"report_id"`
		IntentID    string `json:"intent_id"`
		ValidatorID string `json:"validator_id"`
		Status      string `json:"status"`
		ReceivedTs  int64  `json:"received_ts"`
		Message     string `json:"message"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&reply); err != nil {
		return nil, fmt.Errorf("decode response: %w", err)
	}

	receipt := &ExecutionReceipt{
		ReportID:    reply.ReportID,
		IntentID:    reply.IntentID,
		ValidatorID: reply.ValidatorID,
		Status:      reply.Status,
		Message:     reply.Message,
	}
	if reply.ReceivedTs > 0 {
		receipt.ReceivedAt = time.Unix(reply.ReceivedTs, 0).UTC()
	}

	return receipt, nil
}

// Validate validates the configuration
func (c *Config) Validate() error {
	// Identity IDs are critical - must be configured
	if c.Identity != nil {
		if c.Identity.SubnetID == "" {
			return errors.New("subnet_id must be configured")
		}
		if c.Identity.AgentID == "" {
			return errors.New("agent_id must be configured")
		}
	} else if c.AgentID == "" {
		return errors.New("agent_id must be configured")
	}

	// Validate private key if provided
	if c.PrivateKey != "" {
		if len(c.PrivateKey) != 64 {
			return errors.New("private key must be 32 bytes (64 hex characters)")
		}
		if _, err := hex.DecodeString(c.PrivateKey); err != nil {
			return errors.New("private key must be valid hex")
		}
	}

	if addr := strings.TrimSpace(c.ChainAddress); addr != "" {
		if !common.IsHexAddress(addr) {
			return errors.New("chain_address must be a valid ethereum address")
		}
		c.ChainAddress = common.HexToAddress(addr).Hex()
	}

	// Validate capabilities
	if len(c.Capabilities) == 0 {
		return errors.New("at least one capability must be configured")
	}

	// Validate matcher address
	if c.MatcherAddr == "" {
		return errors.New("matcher_addr must be configured")
	}

	if c.RegistryAddr != "" && c.AgentEndpoint == "" {
		return errors.New("agent_endpoint must be configured when registry_addr is set")
	}

	return nil
}

// applyDefaults applies default values to the configuration
func (c *Config) applyDefaults() {
	if c.MaxConcurrentTasks == 0 {
		c.MaxConcurrentTasks = 5
	}
	if c.TaskTimeout == 0 {
		c.TaskTimeout = 30 * time.Second
	}
	if c.BidTimeout == 0 {
		c.BidTimeout = 5 * time.Second
	}
	if c.BiddingStrategy == "" {
		c.BiddingStrategy = "fixed"
	}
	if c.MinBidPrice == 0 {
		c.MinBidPrice = 100
	}
	if c.MaxBidPrice == 0 {
		c.MaxBidPrice = 1000
	}

	// Sync timeout values
	if c.Timeouts != nil {
		if c.Timeouts.TaskTimeout > 0 {
			c.TaskTimeout = c.Timeouts.TaskTimeout
		}
		if c.Timeouts.BidTimeout > 0 {
			c.BidTimeout = c.Timeouts.BidTimeout
		}
	}
	if c.RegistryHeartbeatInterval == 0 {
		c.RegistryHeartbeatInterval = 30 * time.Second
	}
}

// initGRPCClients initializes gRPC clients for matcher and validator
func (sdk *SDK) initGRPCClients() error {
	var signingConfig *SigningConfig
	if sdk.privateKey != nil {
		signingConfig = &SigningConfig{
			PrivateKey: sdk.privateKey,
			Address:    sdk.address,
			ChainID:    sdk.GetSubnetID(),
		}
	}

	// Initialize matcher client
	if sdk.config.MatcherAddr != "" {
		client, err := NewMatcherClient(sdk.config.MatcherAddr, signingConfig, sdk.config.UseTLS)
		if err != nil {
			return fmt.Errorf("failed to create matcher client: %w", err)
		}
		sdk.matcherClient = client
	}

	// Initialize validator client
	if sdk.config.ValidatorAddr != "" {
		client, err := NewValidatorClient(sdk.config.ValidatorAddr, signingConfig, sdk.config.UseTLS)
		if err != nil {
			if sdk.matcherClient != nil {
				sdk.matcherClient.Close()
			}
			return fmt.Errorf("failed to create validator client: %w", err)
		}
		sdk.validatorClient = client
	}

	return nil
}

// closeGRPCClients closes all gRPC client connections
func (sdk *SDK) closeGRPCClients() {
	if sdk.matcherClient != nil {
		sdk.matcherClient.Close()
		sdk.matcherClient = nil
	}
	if sdk.validatorClient != nil {
		sdk.validatorClient.Close()
		sdk.validatorClient = nil
	}
}

// fireCallback safely invokes a callback if registered
func (sdk *SDK) fireCallback(name string, args ...interface{}) {
	if sdk.callbacks == nil {
		return
	}

	defer func() {
		if r := recover(); r != nil {
			log.Printf("Callback %s panicked: %v", name, r)
		}
	}()

	switch name {
	case "OnStart":
		if err := sdk.callbacks.OnStart(); err != nil {
			log.Printf("OnStart callback error: %v", err)
		}
	case "OnStop":
		if err := sdk.callbacks.OnStop(); err != nil {
			log.Printf("OnStop callback error: %v", err)
		}
	case "OnTaskAccepted":
		if len(args) > 0 {
			if task, ok := args[0].(*Task); ok {
				sdk.callbacks.OnTaskAccepted(task)
			}
		}
	case "OnTaskRejected":
		if len(args) > 1 {
			if task, ok := args[0].(*Task); ok {
				if reason, ok := args[1].(string); ok {
					sdk.callbacks.OnTaskRejected(task, reason)
				}
			}
		}
	case "OnTaskCompleted":
		if len(args) > 2 {
			if task, ok := args[0].(*Task); ok {
				if result, ok := args[1].(*Result); ok {
					var err error
					if len(args) > 2 {
						if e, ok := args[2].(error); ok {
							err = e
						}
					}
					sdk.callbacks.OnTaskCompleted(task, result, err)
				}
			}
		}
	case "OnBidSubmitted":
		if len(args) > 1 {
			if intent, ok := args[0].(*Intent); ok {
				if bid, ok := args[1].(*Bid); ok {
					sdk.callbacks.OnBidSubmitted(intent, bid)
				}
			}
		}
	case "OnBidWon":
		if len(args) > 0 {
			if intentID, ok := args[0].(string); ok {
				sdk.callbacks.OnBidWon(intentID)
			}
		}
	case "OnBidLost":
		if len(args) > 0 {
			if intentID, ok := args[0].(string); ok {
				sdk.callbacks.OnBidLost(intentID)
			}
		}
	case "OnError":
		if len(args) > 0 {
			if err, ok := args[0].(error); ok {
				sdk.callbacks.OnError(err)
			}
		}
	}
}
