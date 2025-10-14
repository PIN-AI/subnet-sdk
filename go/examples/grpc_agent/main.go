package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	sdk "github.com/pinai/subnet-sdk-go"
)

// ExampleHandler implements task execution
type ExampleHandler struct{}

func (h *ExampleHandler) Execute(ctx context.Context, task *sdk.Task) (*sdk.Result, error) {
	log.Printf("Executing task: %s (type: %s)", task.ID, task.Type)

	// Simulate work
	time.Sleep(time.Second)

	return &sdk.Result{
		Data:    []byte(fmt.Sprintf("Task %s completed", task.ID)),
		Success: true,
		Metadata: map[string]string{
			"processed_at": time.Now().Format(time.RFC3339),
		},
	}, nil
}

// ExampleBiddingStrategy implements simple bidding logic
type ExampleBiddingStrategy struct {
	minPrice uint64
	maxPrice uint64
}

func (s *ExampleBiddingStrategy) ShouldBid(intent *sdk.Intent) bool {
	// Bid on all intents for demo purposes
	log.Printf("Evaluating intent: %s (type: %s)", intent.ID, intent.Type)
	return true
}

func (s *ExampleBiddingStrategy) CalculateBid(intent *sdk.Intent) *sdk.Bid {
	// Simple pricing based on intent age
	age := time.Since(intent.CreatedAt)
	price := s.minPrice
	if age > 10*time.Second {
		price = s.maxPrice
	}

	log.Printf("Calculated bid for intent %s: %d", intent.ID, price)

	return &sdk.Bid{
		Price:    price,
		Currency: "PIN",
		Metadata: map[string]string{
			"strategy": "time-based",
		},
	}
}

// ExampleCallbacks implements lifecycle callbacks
type ExampleCallbacks struct{}

func (c *ExampleCallbacks) OnStart() error {
	log.Println("✓ Agent started")
	return nil
}

func (c *ExampleCallbacks) OnStop() error {
	log.Println("✓ Agent stopped")
	return nil
}

func (c *ExampleCallbacks) OnTaskAccepted(task *sdk.Task) {
	log.Printf("✓ Task accepted: %s", task.ID)
}

func (c *ExampleCallbacks) OnTaskRejected(task *sdk.Task, reason string) {
	log.Printf("✗ Task rejected: %s (reason: %s)", task.ID, reason)
}

func (c *ExampleCallbacks) OnTaskCompleted(task *sdk.Task, result *sdk.Result, err error) {
	if err != nil {
		log.Printf("✗ Task %s failed: %v", task.ID, err)
	} else if result.Success {
		log.Printf("✓ Task %s completed successfully", task.ID)
	} else {
		log.Printf("✗ Task %s failed: %s", task.ID, result.Error)
	}
}

func (c *ExampleCallbacks) OnBidSubmitted(intent *sdk.Intent, bid *sdk.Bid) {
	log.Printf("✓ Bid submitted for intent %s: price=%d %s", intent.ID, bid.Price, bid.Currency)
}

func (c *ExampleCallbacks) OnBidWon(intentID string) {
	log.Printf("✓ Bid won for intent: %s", intentID)
}

func (c *ExampleCallbacks) OnBidLost(intentID string) {
	log.Printf("✗ Bid lost for intent: %s", intentID)
}

func (c *ExampleCallbacks) OnError(err error) {
	log.Printf("✗ Error: %v", err)
}

func main() {
	log.SetFlags(log.LstdFlags | log.Lmicroseconds)

	// Build configuration with gRPC enabled
	config, err := sdk.NewConfigBuilder().
		WithSubnetID("subnet-1").
		WithAgentID("grpc-agent-1").
		WithPrivateKey("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef").
		WithMatcherAddr("localhost:8090").          // gRPC matcher
		WithValidatorAddr("localhost:9090").        // gRPC validator
		WithRegistryAddr("http://localhost:8092").  // HTTP registry
		WithAgentEndpoint("http://localhost:7000"). // Agent HTTP endpoint
		WithCapabilities("compute", "ml", "storage").
		WithTaskTimeout(60 * time.Second).
		WithBidTimeout(5 * time.Second).
		WithMaxConcurrentTasks(10).
		WithBiddingStrategy("dynamic", 100, 1000).
		Build()

	if err != nil {
		log.Fatalf("Failed to build config: %v", err)
	}

	// Create SDK
	agent, err := sdk.New(config)
	if err != nil {
		log.Fatalf("Failed to create SDK: %v", err)
	}

	// Register components
	agent.RegisterHandler(&ExampleHandler{})
	agent.RegisterBiddingStrategy(&ExampleBiddingStrategy{
		minPrice: 100,
		maxPrice: 1000,
	})
	agent.RegisterCallbacks(&ExampleCallbacks{})

	log.Printf("Agent Info:")
	log.Printf("  Agent ID: %s", agent.GetAgentID())
	log.Printf("  Subnet ID: %s", agent.GetSubnetID())
	log.Printf("  Chain Address: %s", agent.GetChainAddress())
	log.Printf("  Capabilities: %v", agent.GetCapabilities())

	// Start agent
	if err := agent.Start(); err != nil {
		log.Fatalf("Failed to start agent: %v", err)
	}

	log.Println("Agent running. Press Ctrl+C to stop...")

	// Start metrics reporter
	go func() {
		ticker := time.NewTicker(30 * time.Second)
		defer ticker.Stop()

		for range ticker.C {
			metrics := agent.GetMetrics()
			tasksCompleted, tasksFailed, totalBids, successfulBids := metrics.GetStats()
			log.Printf("Metrics: Tasks(✓%d/✗%d) Bids(✓%d/%d total)",
				tasksCompleted, tasksFailed, successfulBids, totalBids)
		}
	}()

	// Wait for interrupt
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	log.Println("Shutting down...")
	if err := agent.Stop(); err != nil {
		log.Printf("Error stopping agent: %v", err)
	}

	log.Println("Agent stopped gracefully")
}