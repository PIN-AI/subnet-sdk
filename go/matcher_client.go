package agentsdk

import (
	"context"
	"fmt"
	"io"

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

// StreamIntents streams intents from the matcher
func (c *MatcherClient) StreamIntents(ctx context.Context, req *pb.StreamIntentsRequest) (<-chan *pb.MatcherIntentUpdate, <-chan error) {
	intentCh := make(chan *pb.MatcherIntentUpdate)
	errCh := make(chan error, 1)

	go func() {
		defer close(intentCh)
		defer close(errCh)

		stream, err := c.client.StreamIntents(ctx, req)
		if err != nil {
			errCh <- fmt.Errorf("failed to start intent stream: %w", err)
			return
		}

		for {
			update, err := stream.Recv()
			if err == io.EOF {
				return
			}
			if err != nil {
				errCh <- fmt.Errorf("intent stream error: %w", err)
				return
			}

			select {
			case intentCh <- update:
			case <-ctx.Done():
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

	go func() {
		defer close(taskCh)
		defer close(errCh)

		stream, err := c.client.StreamTasks(ctx, req)
		if err != nil {
			errCh <- fmt.Errorf("failed to start task stream: %w", err)
			return
		}

		for {
			task, err := stream.Recv()
			if err == io.EOF {
				return
			}
			if err != nil {
				errCh <- fmt.Errorf("task stream error: %w", err)
				return
			}

			select {
			case taskCh <- task:
			case <-ctx.Done():
				errCh <- ctx.Err()
				return
			}
		}
	}()

	return taskCh, errCh
}

// RespondToTask sends task acceptance/rejection to matcher
func (c *MatcherClient) RespondToTask(ctx context.Context, req *pb.RespondToTaskRequest) (*pb.RespondToTaskResponse, error) {
	return c.client.RespondToTask(ctx, req)
}
