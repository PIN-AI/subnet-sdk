package agentsdk

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"log"
	"time"

	pb "subnet/proto/subnet"
)

// startMatcherStreams starts task and intent streaming
func (sdk *SDK) startMatcherStreams() error {
	if sdk.matcherClient == nil {
		return nil
	}

	ctx, cancel := context.WithCancel(context.Background())
	sdk.matcherCancel = cancel

	// Start task streaming
	sdk.matcherWG.Add(1)
	go sdk.taskStreamLoop(ctx)

	// Start intent streaming if bidding strategy is registered
	if sdk.biddingStrategy != nil {
		sdk.matcherWG.Add(1)
		go sdk.intentStreamLoop(ctx)
	}

	return nil
}

// stopMatcherStreams stops all matcher streams
func (sdk *SDK) stopMatcherStreams() {
	if sdk.matcherCancel != nil {
		sdk.matcherCancel()
		sdk.matcherWG.Wait()
		sdk.matcherCancel = nil
	}
}

// taskStreamLoop handles incoming execution tasks
func (sdk *SDK) taskStreamLoop(ctx context.Context) {
	defer sdk.matcherWG.Done()

	// Read agent ID directly to avoid potential deadlock
	var agentID string
	if sdk.config.Identity != nil {
		agentID = sdk.config.Identity.AgentID
	} else {
		agentID = sdk.config.AgentID
	}

	req := &pb.StreamTasksRequest{
		AgentId: agentID,
	}

	log.Printf("[SDK DEBUG] Starting task stream loop for agent: %s", agentID)

	for {
		select {
		case <-ctx.Done():
			log.Printf("[SDK DEBUG] Task stream loop context done, exiting")
			return
		default:
		}

		log.Printf("[SDK DEBUG] Calling StreamTasks...")
		taskCh, errCh := sdk.matcherClient.StreamTasks(ctx, req)
		log.Printf("[SDK DEBUG] StreamTasks called, waiting for tasks...")

		for {
			select {
			case <-ctx.Done():
				log.Printf("[SDK DEBUG] Task stream context done")
				return
			case task, ok := <-taskCh:
				if !ok {
					// Channel closed, reconnect
					log.Printf("[SDK DEBUG] Task stream channel closed, reconnecting...")
					time.Sleep(5 * time.Second)
					goto reconnect
				}
				log.Printf("[SDK DEBUG] Received task from stream: %s (intent: %s)", task.TaskId, task.IntentId)
				// Handle task in separate goroutine to avoid blocking the stream
				go sdk.handleExecutionTask(ctx, task)
			case err := <-errCh:
				if err != nil {
					log.Printf("[SDK DEBUG] Task stream error: %v", err)
					sdk.fireCallback("OnError", err)
					time.Sleep(5 * time.Second)
					goto reconnect
				}
			}
		}
	reconnect:
	}
}

// intentStreamLoop handles incoming intents for bidding
func (sdk *SDK) intentStreamLoop(ctx context.Context) {
	defer sdk.matcherWG.Done()

	req := &pb.StreamIntentsRequest{
		SubnetId: sdk.GetSubnetID(),
	}

	log.Printf("[SDK DEBUG] Starting intent stream loop for subnet: %s", req.SubnetId)

	for {
		select {
		case <-ctx.Done():
			log.Printf("[SDK DEBUG] Intent stream loop context done, exiting")
			return
		default:
		}

		log.Printf("[SDK DEBUG] Calling StreamIntents...")
		intentCh, errCh := sdk.matcherClient.StreamIntents(ctx, req)
		log.Printf("[SDK DEBUG] StreamIntents called, waiting for updates...")

		for {
			select {
			case <-ctx.Done():
				log.Printf("[SDK DEBUG] Intent stream context done")
				return
			case update, ok := <-intentCh:
				if !ok {
					// Channel closed, reconnect
					log.Printf("[SDK DEBUG] Intent stream channel closed, reconnecting...")
					time.Sleep(5 * time.Second)
					goto reconnect
				}
				log.Printf("[SDK DEBUG] Received intent update: %s, type: %s", update.IntentId, update.UpdateType)
				sdk.handleIntentUpdate(ctx, update)
			case err := <-errCh:
				if err != nil {
					log.Printf("[SDK DEBUG] Intent stream error: %v", err)
					sdk.fireCallback("OnError", err)
					time.Sleep(5 * time.Second)
					goto reconnect
				}
			}
		}
	reconnect:
	}
}

// handleExecutionTask processes an execution task
func (sdk *SDK) handleExecutionTask(ctx context.Context, taskProto *pb.ExecutionTask) {
	log.Printf("[SDK DEBUG] handleExecutionTask called for task: %s", taskProto.TaskId)

	if !sdk.running {
		log.Printf("[SDK DEBUG] SDK not running, skipping task")
		return
	}

	task := &Task{
		ID:        taskProto.TaskId,
		IntentID:  taskProto.IntentId,
		Type:      taskProto.IntentType,
		Data:      taskProto.IntentData,
		Metadata:  map[string]string{"bid_id": taskProto.BidId},
		Deadline:  time.Unix(taskProto.Deadline, 0),
		CreatedAt: time.Unix(taskProto.CreatedAt, 0),
	}

	log.Printf("[SDK DEBUG] Task created, starting execution...")

	// Call OnTaskAccepted callback (no need to respond to matcher like validator_test_agent)
	log.Printf("[SDK DEBUG] Calling OnTaskAccepted callback")
	sdk.fireCallback("OnTaskAccepted", task)

	// Execute task
	log.Printf("[SDK DEBUG] Executing task...")
	result, err := sdk.ExecuteTask(ctx, task)
	if err != nil {
		log.Printf("[SDK DEBUG] Task %s execution failed: %v", task.ID, err)
	} else {
		log.Printf("[SDK DEBUG] Task %s executed successfully", task.ID)
	}

	log.Printf("[SDK DEBUG] Calling OnTaskCompleted callback")
	sdk.fireCallback("OnTaskCompleted", task, result, err)

	// Submit execution report via gRPC
	log.Printf("[SDK DEBUG] Submitting execution report...")

	if sdk.validatorClient == nil {
		log.Printf("[SDK DEBUG] No validator client configured, skipping execution report submission")
		return
	}

	reportID := generateReportID()
	status := pb.ExecutionReport_SUCCESS
	if !result.Success {
		status = pb.ExecutionReport_FAILED
	}

	// Prepare error info if task failed
	var errorInfo *pb.ErrorInfo
	if !result.Success && result.Error != "" {
		errorInfo = &pb.ErrorInfo{
			Code:    "EXECUTION_FAILED",
			Message: result.Error,
		}
	}

	reportProto := &pb.ExecutionReport{
		ReportId:     reportID,
		AssignmentId: task.ID,
		IntentId:     task.IntentID,
		AgentId:      sdk.GetChainAddress(), // Use chain address for RootLayer compatibility
		Status:       status,
		ResultData:   result.Data,
		Timestamp:    time.Now().Unix(),
		Evidence:     nil,       // Optional: verification evidence
		Error:        errorInfo, // Optional: error details
		Signature:    []byte{},  // TODO: Sign the report
	}

	receipt, err := sdk.validatorClient.SubmitExecutionReport(ctx, reportProto)
	if err != nil {
		log.Printf("[SDK DEBUG] Failed to submit execution report %s: %v", reportID, err)
		return
	}

	log.Printf("[SDK DEBUG] Execution report %s submitted successfully", reportID)
	log.Printf("[SDK DEBUG] Receipt: ReportID=%s, Status=%s, Phase=%s", receipt.ReportId, receipt.Status, receipt.Phase)
}

// handleIntentUpdate processes an intent update for bidding
func (sdk *SDK) handleIntentUpdate(ctx context.Context, update *pb.MatcherIntentUpdate) {
	if sdk.biddingStrategy == nil {
		return
	}

	intent := &Intent{
		ID:          update.IntentId,
		Type:        update.UpdateType,
		Description: "",
		CreatedAt:   time.Unix(update.Timestamp, 0),
	}

	// Check if we should bid
	if !sdk.biddingStrategy.ShouldBid(intent) {
		return
	}

	// Calculate bid
	bid := sdk.biddingStrategy.CalculateBid(intent)
	if bid == nil {
		return
	}

	// Ensure chain address in metadata
	metadata := ensureChainAddressMetadata(bid.Metadata, sdk.GetChainAddress())

	// Generate nonce
	nonce := make([]byte, 16)
	rand.Read(nonce)

	// Create bid request
	bidProto := &pb.Bid{
		BidId:       generateBidID(),
		IntentId:    intent.ID,
		AgentId:     sdk.GetAgentID(),
		Price:       bid.Price,
		Token:       bid.Currency,
		SubmittedAt: time.Now().Unix(),
		Nonce:       hex.EncodeToString(nonce),
		Metadata:    metadata,
	}

	req := &pb.SubmitBidRequest{
		Bid: bidProto,
	}

	// Submit bid
	resp, err := sdk.matcherClient.SubmitBid(ctx, req)
	if err != nil {
		log.Printf("Failed to submit bid for intent %s: %v", intent.ID, err)
		sdk.fireCallback("OnError", fmt.Errorf("bid submission failed: %w", err))
		sdk.metrics.RecordBid(false)
		return
	}

	accepted := resp.Ack != nil && resp.Ack.Accepted
	sdk.metrics.RecordBid(accepted)

	if accepted {
		sdk.fireCallback("OnBidSubmitted", intent, bid)
		log.Printf("Bid submitted for intent %s: %s", intent.ID, bidProto.BidId)
	} else {
		reason := "rejected"
		if resp.Ack != nil {
			reason = resp.Ack.Reason
		}
		log.Printf("Bid rejected for intent %s: %s", intent.ID, reason)
	}
}

// generateReportID generates a unique report ID
func generateReportID() string {
	b := make([]byte, 16)
	rand.Read(b)
	return fmt.Sprintf("report-%s", hex.EncodeToString(b))
}

// generateBidID generates a unique bid ID in format 0x + 64 hex characters (32 bytes)
func generateBidID() string {
	b := make([]byte, 32)
	rand.Read(b)
	return fmt.Sprintf("0x%s", hex.EncodeToString(b))
}
