package agentsdk

import (
	"context"
	"fmt"

	pb "subnet/proto/subnet"
	"google.golang.org/grpc"
)

// ValidatorClient wraps the gRPC ValidatorService client
type ValidatorClient struct {
	conn   *grpc.ClientConn
	client pb.ValidatorServiceClient
}

// NewValidatorClient creates a new validator client
func NewValidatorClient(target string, signingConfig *SigningConfig, secure bool) (*ValidatorClient, error) {
	conn, err := DialOption(target, signingConfig, secure)
	if err != nil {
		return nil, fmt.Errorf("failed to dial validator: %w", err)
	}

	return &ValidatorClient{
		conn:   conn,
		client: pb.NewValidatorServiceClient(conn),
	}, nil
}

// Close closes the connection
func (c *ValidatorClient) Close() error {
	if c.conn != nil {
		return c.conn.Close()
	}
	return nil
}

// SubmitExecutionReport submits an execution report to the validator
func (c *ValidatorClient) SubmitExecutionReport(ctx context.Context, req *pb.ExecutionReport) (*pb.Receipt, error) {
	return c.client.SubmitExecutionReport(ctx, req)
}

// SubmitExecutionReportBatch submits multiple execution reports to the validator in batch
func (c *ValidatorClient) SubmitExecutionReportBatch(ctx context.Context, req *pb.ExecutionReportBatchRequest) (*pb.ExecutionReportBatchResponse, error) {
	return c.client.SubmitExecutionReportBatch(ctx, req)
}

// GetValidatorSet retrieves the validator set
func (c *ValidatorClient) GetValidatorSet(ctx context.Context, req *pb.GetCheckpointRequest) (*pb.ValidatorSet, error) {
	return c.client.GetValidatorSet(ctx, req)
}