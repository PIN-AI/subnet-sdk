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

	req := &pb.StreamTasksRequest{
		AgentId: sdk.GetAgentID(),
	}

	for {
		select {
		case <-ctx.Done():
			return
		default:
		}

		taskCh, errCh := sdk.matcherClient.StreamTasks(ctx, req)

		for {
			select {
			case <-ctx.Done():
				return
			case task, ok := <-taskCh:
				if !ok {
					// Channel closed, reconnect
					log.Printf("Task stream closed, reconnecting...")
					time.Sleep(5 * time.Second)
					goto reconnect
				}
				sdk.handleExecutionTask(ctx, task)
			case err := <-errCh:
				if err != nil {
					log.Printf("Task stream error: %v", err)
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

	for {
		select {
		case <-ctx.Done():
			return
		default:
		}

		intentCh, errCh := sdk.matcherClient.StreamIntents(ctx, req)

		for {
			select {
			case <-ctx.Done():
				return
			case update, ok := <-intentCh:
				if !ok {
					// Channel closed, reconnect
					log.Printf("Intent stream closed, reconnecting...")
					time.Sleep(5 * time.Second)
					goto reconnect
				}
				sdk.handleIntentUpdate(ctx, update)
			case err := <-errCh:
				if err != nil {
					log.Printf("Intent stream error: %v", err)
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
	if !sdk.running {
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

	// Respond to task (accept)
	response := &pb.RespondToTaskRequest{
		Response: &pb.TaskResponse{
			TaskId:    task.ID,
			AgentId:   sdk.GetAgentID(),
			Accepted:  true,
			Timestamp: time.Now().Unix(),
		},
	}

	if _, err := sdk.matcherClient.RespondToTask(ctx, response); err != nil {
		log.Printf("Failed to respond to task %s: %v", task.ID, err)
		sdk.fireCallback("OnTaskRejected", task, fmt.Sprintf("response failed: %v", err))
		return
	}

	sdk.fireCallback("OnTaskAccepted", task)

	// Execute task
	result, err := sdk.ExecuteTask(ctx, task)
	if err != nil {
		log.Printf("Task %s execution failed: %v", task.ID, err)
	}

	sdk.fireCallback("OnTaskCompleted", task, result, err)

	// Submit execution report
	report := &ExecutionReport{
		ReportID:     generateReportID(),
		AssignmentID: task.ID,
		IntentID:     task.IntentID,
		AgentID:      sdk.GetAgentID(),
		Status:       ExecutionReportStatusSuccess,
		ResultData:   result.Data,
		Timestamp:    time.Now(),
		Metadata: map[string]string{
			"bid_id": taskProto.BidId,
		},
	}

	if !result.Success {
		report.Status = ExecutionReportStatusFailed
		if result.Error != "" {
			report.Metadata["error"] = result.Error
		}
	}

	if _, err := sdk.SubmitExecutionReport(ctx, report); err != nil {
		log.Printf("Failed to submit execution report %s: %v", report.ReportID, err)
	}
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

// generateBidID generates a unique bid ID
func generateBidID() string {
	b := make([]byte, 16)
	rand.Read(b)
	return fmt.Sprintf("bid-%s", hex.EncodeToString(b))
}
