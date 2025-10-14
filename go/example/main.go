package main

import (
	"context"
	"fmt"
	"log"
	"time"

	sdk "github.com/pinai/subnet-sdk-go"
)

// ExampleHandler implements the SDK handler interface
type ExampleHandler struct{}

func (h *ExampleHandler) Execute(ctx context.Context, task *sdk.Task) (*sdk.Result, error) {
	log.Printf("Executing task: %s", task.ID)

	// Example: Process the task based on type
	switch task.Type {
	case "compute":
		// Simulate computation
		time.Sleep(2 * time.Second)
		return &sdk.Result{
			Data:    []byte("computation result"),
			Success: true,
		}, nil
	case "storage":
		// Simulate storage operation
		time.Sleep(1 * time.Second)
		return &sdk.Result{
			Data:    []byte("storage result"),
			Success: true,
		}, nil
	default:
		return &sdk.Result{
			Success: false,
			Error:   fmt.Sprintf("unsupported task type: %s", task.Type),
		}, nil
	}
}

func main() {
	// Method 1: Using ConfigBuilder (Recommended)
	config, err := sdk.NewConfigBuilder().
		WithSubnetID("my-subnet-1").
		WithAgentID("my-agent-1").
		WithPrivateKey("0xYOUR_PRIVATE_KEY_HERE").
		WithMatcherAddr("localhost:8090").
		WithCapabilities("compute", "storage", "ml").
		WithTaskTimeout(60 * time.Second).
		WithBidTimeout(10 * time.Second).
		WithMaxConcurrentTasks(10).
		WithBiddingStrategy("dynamic", 50, 500).
		Build()

	if err != nil {
		log.Fatalf("Failed to build config: %v", err)
	}

	// Method 2: Direct configuration
	// config := &sdk.Config{
	// 	Identity: &sdk.IdentityConfig{
	// 		SubnetID: "my-subnet-1",
	// 		AgentID:  "my-agent-1",
	// 	},
	// 	PrivateKey:   "0xYOUR_PRIVATE_KEY_HERE",
	// 	MatcherAddr:  "localhost:8090",
	// 	Capabilities: []string{"compute", "storage", "ml"},
	// 	Timeouts: &sdk.TimeoutConfig{
	// 		TaskTimeout: 60 * time.Second,
	// 		BidTimeout:  10 * time.Second,
	// 	},
	// 	MaxConcurrentTasks: 10,
	// 	BiddingStrategy:    "dynamic",
	// 	MinBidPrice:        50,
	// 	MaxBidPrice:        500,
	// }

	// Create SDK instance
	agent, err := sdk.New(config)
	if err != nil {
		log.Fatalf("Failed to create SDK: %v", err)
	}

	// Register handler
	handler := &ExampleHandler{}
	agent.RegisterHandler(handler)

	// Access configuration via SDK methods
	fmt.Printf("Agent ID: %s\n", agent.GetAgentID())
	fmt.Printf("Subnet ID: %s\n", agent.GetSubnetID())
	fmt.Printf("Agent Address: %s\n", agent.GetAddress())
	fmt.Printf("Capabilities: %v\n", agent.GetCapabilities())

	// Get full config copy (safe to modify)
	configCopy := agent.GetConfig()
	fmt.Printf("Max Concurrent Tasks: %d\n", configCopy.MaxConcurrentTasks)

	// Start the agent
	if err := agent.Start(); err != nil {
		log.Fatalf("Failed to start agent: %v", err)
	}

	log.Println("Agent started successfully")

	// Get metrics periodically
	go func() {
		ticker := time.NewTicker(30 * time.Second)
		defer ticker.Stop()

		for range ticker.C {
			metrics := agent.GetMetrics()
			tasksCompleted, tasksFailed, totalBids, successfulBids := metrics.GetStats()
			fmt.Printf("Metrics - Tasks Completed: %d, Failed: %d, Bids: %d/%d\n",
				tasksCompleted, tasksFailed, successfulBids, totalBids)
		}
	}()

	// Keep running until interrupted
	select {}
}