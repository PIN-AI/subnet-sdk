# Subnet SDK

Multi-language SDK for building agents that interact with the Subnet protocol.

## 🌟 Features

- **Multi-Language Support**: Go and Python SDKs with consistent APIs
- **Independent Design**: No dependencies on internal Subnet packages
- **Security First**: No default IDs to prevent conflicts
- **Simple Interface**: Clean handler-based architecture
- **Built-in Metrics**: Performance and earnings tracking
- **Thread-Safe**: Safe for concurrent use

## 📦 Languages

### Go SDK

```bash
cd go
go get github.com/pinai/subnet-sdk-go
```

[Go Documentation](go/README.md) | [Go Example](go/example/)

### Python SDK

```bash
pip install subnet-sdk
```

[Python Documentation](python/README.md) | [Python Example](python/example.py)

## 🚀 Quick Start

### Go

```go
import sdk "github.com/pinai/subnet-sdk-go"

config, _ := sdk.NewConfigBuilder().
    WithSubnetID("subnet-1").   // REQUIRED - no defaults
    WithAgentID("agent-1").     // REQUIRED - no defaults
    WithMatcherAddr("localhost:8090").
    WithCapabilities("compute").
    Build()

agent, _ := sdk.New(config)
```

### Python

```python
from subnet_sdk import SDK, ConfigBuilder

config = ConfigBuilder() \
    .with_subnet_id("subnet-1") \     # REQUIRED - no defaults
    .with_agent_id("agent-1") \       # REQUIRED - no defaults
    .with_matcher_addr("localhost:8090") \
    .with_capabilities("compute") \
    .build()

sdk = SDK(config)
```

## ⚠️ Important Configuration Rules

1. **No Default IDs**: SubnetID and AgentID MUST be explicitly configured
   - Prevents identity conflicts in production
   - Forces conscious ID selection
   - No "subnet-1" or "agent-1" defaults

2. **Required Fields** (all languages):
   - `subnet_id` - Identifies the subnet
   - `agent_id` - Unique agent identifier
   - `matcher_addr` - Matcher service endpoint
   - `capabilities` - At least one capability

3. **Private Key Format**:
   - 64 hex characters (32 bytes)
   - Without "0x" prefix in Go
   - With or without "0x" prefix in Python

## 🏗️ Architecture

```
subnet-sdk/
├── go/                    # Go SDK
│   ├── sdk.go            # Core SDK
│   ├── types.go          # Type definitions
│   ├── config_builder.go # Configuration builder
│   └── example/          # Example implementation
├── python/               # Python SDK
│   ├── subnet_sdk/       # Package directory
│   │   ├── sdk.py       # Core SDK
│   │   ├── types.py     # Type definitions
│   │   └── config_builder.py
│   ├── setup.py         # Package setup
│   └── example.py       # Example implementation
├── docs/                # Shared documentation
└── examples/            # Cross-language examples
```

## 🔧 Development

### Building

```bash
# Go
cd go
make build

# Python
cd python
pip install -e .[dev]
```

### Testing

```bash
# Go
cd go
make test

# Python
cd python
pytest
```

## 📖 Documentation

- [Quick Start Guide](docs/quick-start.md) - Get started in 5 minutes
- [Complete Tutorial](docs/tutorial.md) - Step-by-step guide
- [API Reference](docs/api-reference.md) - Complete API documentation
- [Execution Reporting](docs/execution-reporting.md) - How to report results to Validators
- [Go SDK Documentation](go/README.md) - Go-specific details
- [Python SDK Documentation](python/README.md) - Python-specific details

## 🤝 Contributing

1. Keep APIs consistent across languages
2. No default IDs in any language
3. Update all SDKs when adding features
4. Write tests for all new functionality
5. Update documentation

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🔗 Links

- [Subnet Repository](https://github.com/pinai/subnet)
- [Protocol Documentation](https://docs.pinai.io)
- [Discord Community](https://discord.gg/pinai)