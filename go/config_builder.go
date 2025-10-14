package agentsdk

import (
	"fmt"
	"time"
)

// ConfigBuilder provides a fluent interface for building SDK configuration
type ConfigBuilder struct {
	config *Config
}

// NewConfigBuilder creates a new configuration builder
func NewConfigBuilder() *ConfigBuilder {
	return &ConfigBuilder{
		config: &Config{
			Identity: &IdentityConfig{},
			Timeouts: &TimeoutConfig{
				TaskTimeout: 30 * time.Second,
				BidTimeout:  5 * time.Second,
			},
			MaxConcurrentTasks:        5,
			Capabilities:              []string{},
			RegistryHeartbeatInterval: 30 * time.Second,
		},
	}
}

// WithSubnetID sets the subnet ID
func (b *ConfigBuilder) WithSubnetID(subnetID string) *ConfigBuilder {
	if b.config.Identity == nil {
		b.config.Identity = &IdentityConfig{}
	}
	b.config.Identity.SubnetID = subnetID
	return b
}

// WithAgentID sets the agent ID
func (b *ConfigBuilder) WithAgentID(agentID string) *ConfigBuilder {
	b.config.AgentID = agentID
	if b.config.Identity == nil {
		b.config.Identity = &IdentityConfig{}
	}
	b.config.Identity.AgentID = agentID
	return b
}

// WithPrivateKey sets the private key for signing
func (b *ConfigBuilder) WithPrivateKey(privateKey string) *ConfigBuilder {
	b.config.PrivateKey = privateKey
	return b
}

// WithChainAddress sets the on-chain address used for metadata enrichment.
func (b *ConfigBuilder) WithChainAddress(addr string) *ConfigBuilder {
	b.config.ChainAddress = addr
	return b
}

// WithMatcherAddr sets the matcher address
func (b *ConfigBuilder) WithMatcherAddr(addr string) *ConfigBuilder {
	b.config.MatcherAddr = addr
	return b
}

// WithValidatorAddr sets the validator address
func (b *ConfigBuilder) WithValidatorAddr(addr string) *ConfigBuilder {
	b.config.ValidatorAddr = addr
	return b
}

// WithRegistryAddr sets the registry service address
func (b *ConfigBuilder) WithRegistryAddr(addr string) *ConfigBuilder {
	b.config.RegistryAddr = addr
	return b
}

// WithAgentEndpoint sets the agent's reachable endpoint for callbacks
func (b *ConfigBuilder) WithAgentEndpoint(endpoint string) *ConfigBuilder {
	b.config.AgentEndpoint = endpoint
	return b
}

// WithCapabilities sets the agent capabilities
func (b *ConfigBuilder) WithCapabilities(capabilities ...string) *ConfigBuilder {
	b.config.Capabilities = capabilities
	return b
}

// AddCapability adds a single capability
func (b *ConfigBuilder) AddCapability(capability string) *ConfigBuilder {
	b.config.Capabilities = append(b.config.Capabilities, capability)
	return b
}

// WithTaskTimeout sets the task execution timeout
func (b *ConfigBuilder) WithTaskTimeout(timeout time.Duration) *ConfigBuilder {
	if b.config.Timeouts == nil {
		b.config.Timeouts = &TimeoutConfig{}
	}
	b.config.Timeouts.TaskTimeout = timeout
	b.config.TaskTimeout = timeout
	return b
}

// WithBidTimeout sets the bid submission timeout
func (b *ConfigBuilder) WithBidTimeout(timeout time.Duration) *ConfigBuilder {
	if b.config.Timeouts == nil {
		b.config.Timeouts = &TimeoutConfig{}
	}
	b.config.Timeouts.BidTimeout = timeout
	b.config.BidTimeout = timeout
	return b
}

// WithMaxConcurrentTasks sets the maximum concurrent tasks
func (b *ConfigBuilder) WithMaxConcurrentTasks(max int) *ConfigBuilder {
	b.config.MaxConcurrentTasks = max
	return b
}

// WithBiddingStrategy sets the bidding strategy and price range
func (b *ConfigBuilder) WithBiddingStrategy(strategy string, minPrice, maxPrice uint64) *ConfigBuilder {
	b.config.BiddingStrategy = strategy
	b.config.MinBidPrice = minPrice
	b.config.MaxBidPrice = maxPrice
	return b
}

// WithOwner sets the owner address for registration
func (b *ConfigBuilder) WithOwner(owner string) *ConfigBuilder {
	b.config.Owner = owner
	return b
}

// WithStakeAmount sets the stake amount for permissions
func (b *ConfigBuilder) WithStakeAmount(amount uint64) *ConfigBuilder {
	b.config.StakeAmount = amount
	return b
}

// WithRegistryHeartbeatInterval sets the heartbeat interval sent to the registry
func (b *ConfigBuilder) WithRegistryHeartbeatInterval(interval time.Duration) *ConfigBuilder {
	b.config.RegistryHeartbeatInterval = interval
	return b
}

// WithTLS enables TLS with the provided certificates
func (b *ConfigBuilder) WithTLS(certFile, keyFile string) *ConfigBuilder {
	b.config.UseTLS = true
	b.config.CertFile = certFile
	b.config.KeyFile = keyFile
	return b
}

// WithLogLevel sets the logging level
func (b *ConfigBuilder) WithLogLevel(level string) *ConfigBuilder {
	b.config.LogLevel = level
	return b
}

// WithDataDir sets the data directory
func (b *ConfigBuilder) WithDataDir(dir string) *ConfigBuilder {
	b.config.DataDir = dir
	return b
}

// Build validates and returns the configuration
func (b *ConfigBuilder) Build() (*Config, error) {
	// Apply defaults
	b.config.applyDefaults()

	// Validate configuration
	if err := b.config.Validate(); err != nil {
		return nil, fmt.Errorf("invalid configuration: %w", err)
	}

	return b.config, nil
}

// MustBuild builds the configuration and panics if invalid
func (b *ConfigBuilder) MustBuild() *Config {
	config, err := b.Build()
	if err != nil {
		panic(err)
	}
	return config
}

// DefaultConfig returns a minimal default configuration
// Users must still set: SubnetID, AgentID, PrivateKey, MatcherAddr, and Capabilities
func DefaultConfig() *Config {
	return &Config{
		Identity: &IdentityConfig{},
		Timeouts: &TimeoutConfig{
			TaskTimeout: 30 * time.Second,
			BidTimeout:  5 * time.Second,
		},
		MaxConcurrentTasks:        5,
		TaskTimeout:               30 * time.Second,
		BidTimeout:                5 * time.Second,
		BiddingStrategy:           "fixed",
		MinBidPrice:               100,
		MaxBidPrice:               1000,
		RegistryHeartbeatInterval: 30 * time.Second,
	}
}
