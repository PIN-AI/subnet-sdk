# Subnet SDK

Official SDKs for building agents that interact with PinAI Subnets.

## Structure

```
subnet-sdk/
├── proto-src/          # Proto source files (synced from pin_protocol)
├── go/                 # Go SDK
├── python/             # Python SDK
└── scripts/            # Utility scripts
```

## Quick Start

### Go SDK

```bash
cd go
make proto    # Generate proto files (optional, already generated)
make build    # Build SDK
make test     # Run tests
```

### Python SDK

```bash
cd python
pip install -e ".[dev]"  # Install SDK with dev dependencies
make test                # Run tests
```

## Proto Management

Proto source files are maintained in `proto-src/` directory.

### Syncing Proto from pin_protocol

```bash
# From local pin_protocol (development)
./scripts/sync-proto.sh

# From GitHub tag (production)
./scripts/sync-proto.sh v0.1.0

# From GitHub main branch
./scripts/sync-proto.sh main
```

After syncing, regenerate proto for both SDKs:

```bash
cd go && make proto
cd python && make proto
```

## Development Workflow

### 1. Clone Repository

```bash
git clone https://github.com/PIN-AI/subnet-sdk
cd subnet-sdk
```

### 2. Build and Test

```bash
# Go
cd go
make build
make test

# Python
cd python
pip install -e ".[dev]"
make test
```

## Proto Source Strategy

The SDK uses a **proto-in-repo** strategy:

- ✅ Proto source files are committed to `proto-src/`
- ✅ Generated files are also committed (for user convenience)
- ✅ No external dependencies required for build
- ✅ Version control over proto definitions

## License

MIT License
