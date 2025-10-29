package agentsdk

import (
	"context"
	"fmt"
	"io"
	"log"

	pb "subnet/proto/subnet"

	"google.golang.org/grpc"
)

// MatcherClient wraps the gRPC MatcherService client with simplified interface
type MatcherClient struct {
	conn   *grpc.ClientConn
	client pb.MatcherServiceClient
}

// NewMatcherClient creates a new matcher client
func NewMatcherClient(target string, signingConfig *SigningConfig, secure bool) (*MatcherClient, error) {
	conn, err := DialOption(target, signingConfig, secure)
	if err != nil {
		return nil, fmt.Errorf("failed to dial matcher: %w", err)
	}

	return &MatcherClient{
		conn:   conn,
		client: pb.NewMatcherServiceClient(conn),
	}, nil
}

// Close closes the connection
func (c *MatcherClient) Close() error {
	if c.conn != nil {
		return c.conn.Close()
	}
	return nil
}

// SubmitBid submits a bid to the matcher
func (c *MatcherClient) SubmitBid(ctx context.Context, req *pb.SubmitBidRequest) (*pb.SubmitBidResponse, error) {
	return c.client.SubmitBid(ctx, req)
}

// SubmitBidBatch submits multiple bids to the matcher in batch
func (c *MatcherClient) SubmitBidBatch(ctx context.Context, req *pb.SubmitBidBatchRequest) (*pb.SubmitBidBatchResponse, error) {
	return c.client.SubmitBidBatch(ctx, req)
}

// StreamIntents streams intents from the matcher
func (c *MatcherClient) StreamIntents(ctx context.Context, req *pb.StreamIntentsRequest) (<-chan *pb.MatcherIntentUpdate, <-chan error) {
	intentCh := make(chan *pb.MatcherIntentUpdate)
	errCh := make(chan error, 1)

	log.Printf("[MatcherClient DEBUG] StreamIntents called with SubnetID: %s", req.SubnetId)

	go func() {
		defer close(intentCh)
		defer close(errCh)

		log.Printf("[MatcherClient DEBUG] Calling gRPC StreamIntents...")
		stream, err := c.client.StreamIntents(ctx, req)
		if err != nil {
			log.Printf("[MatcherClient DEBUG] Failed to start intent stream: %v", err)
			errCh <- fmt.Errorf("failed to start intent stream: %w", err)
			return
		}
		log.Printf("[MatcherClient DEBUG] Intent stream started successfully, entering receive loop...")

		for {
			log.Printf("[MatcherClient DEBUG] Waiting for intent update from stream.Recv()...")
			update, err := stream.Recv()
			if err == io.EOF {
				log.Printf("[MatcherClient DEBUG] Intent stream EOF")
				return
			}
			if err != nil {
				log.Printf("[MatcherClient DEBUG] Intent stream Recv error: %v", err)
				errCh <- fmt.Errorf("intent stream error: %w", err)
				return
			}

			log.Printf("[MatcherClient DEBUG] Received intent update from stream: %s", update.IntentId)
			select {
			case intentCh <- update:
				log.Printf("[MatcherClient DEBUG] Sent intent update to channel")
			case <-ctx.Done():
				log.Printf("[MatcherClient DEBUG] Context done while sending update")
				errCh <- ctx.Err()
				return
			}
		}
	}()

	return intentCh, errCh
}

// StreamTasks streams execution tasks for an agent
func (c *MatcherClient) StreamTasks(ctx context.Context, req *pb.StreamTasksRequest) (<-chan *pb.ExecutionTask, <-chan error) {
	taskCh := make(chan *pb.ExecutionTask)
	errCh := make(chan error, 1)

	log.Printf("[MatcherClient DEBUG] StreamTasks called with AgentID: %s", req.AgentId)

	go func() {
		defer close(taskCh)
		defer close(errCh)

		log.Printf("[MatcherClient DEBUG] Calling gRPC StreamTasks...")
		stream, err := c.client.StreamTasks(ctx, req)
		if err != nil {
			log.Printf("[MatcherClient DEBUG] Failed to start task stream: %v", err)
			errCh <- fmt.Errorf("failed to start task stream: %w", err)
			return
		}

		log.Printf("[MatcherClient DEBUG] Task stream started successfully, entering receive loop...")

		for {
			log.Printf("[MatcherClient DEBUG] Waiting for task from stream.Recv()...")
			task, err := stream.Recv()
			if err == io.EOF {
				log.Printf("[MatcherClient DEBUG] Task stream EOF received")
				return
			}
			if err != nil {
				log.Printf("[MatcherClient DEBUG] Task stream error: %v", err)
				errCh <- fmt.Errorf("task stream error: %w", err)
				return
			}

			log.Printf("[MatcherClient DEBUG] Received task from stream: %s", task.TaskId)
			log.Printf("[MatcherClient DEBUG] Sent task to channel")

			select {
			case taskCh <- task:
				log.Printf("[MatcherClient DEBUG] Task sent to channel successfully")
			case <-ctx.Done():
				log.Printf("[MatcherClient DEBUG] Context done while sending task")
				errCh <- ctx.Err()
				return
			}
		}
	}()

	return taskCh, errCh
}

// RespondToTask sends task acceptance/rejection to matcher
func (c *MatcherClient) RespondToTask(ctx context.Context, req *pb.RespondToTaskRequest) (*pb.RespondToTaskResponse, error) {
	log.Printf("[MatcherClient DEBUG] RespondToTask called for task: %s, accepted: %t", req.Response.TaskId, req.Response.Accepted)
	resp, err := c.client.RespondToTask(ctx, req)
	if err != nil {
		log.Printf("[MatcherClient DEBUG] RespondToTask failed: %v", err)
		return nil, err
	}
	log.Printf("[MatcherClient DEBUG] RespondToTask succeeded")
	return resp, nil
}
