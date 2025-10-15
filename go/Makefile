.PHONY: proto proto-check build test clean

# Proto source directory
PROTO_SRC = ../proto-src

# Generate protobuf files from proto-src
proto:
	@echo "Generating protobuf files from $(PROTO_SRC)..."
	@protoc -I $(PROTO_SRC) \
		--go_out=. \
		--go_opt=paths=source_relative \
		--go-grpc_out=. \
		--go-grpc_opt=paths=source_relative \
		$(PROTO_SRC)/subnet/*.proto
	@mkdir -p proto/subnet
	@mv subnet/*.pb.go proto/subnet/ 2>/dev/null || true
	@rmdir subnet 2>/dev/null || true
	@echo "✓ Proto generation complete"

# Check if proto files are in sync with proto-src
proto-check:
	@echo "Checking if proto is in sync with proto-src..."
	@mkdir -p /tmp/proto-check
	@protoc -I $(PROTO_SRC) \
		--go_out=/tmp/proto-check \
		--go_opt=paths=source_relative \
		--go-grpc_out=/tmp/proto-check \
		--go-grpc_opt=paths=source_relative \
		$(PROTO_SRC)/subnet/*.proto 2>/dev/null
	@if diff -r proto/subnet /tmp/proto-check/proto/subnet >/dev/null 2>&1; then \
		echo "✓ Proto in sync"; \
	else \
		echo "❌ Proto out of sync! Run 'make proto'"; \
		rm -rf /tmp/proto-check; \
		exit 1; \
	fi
	@rm -rf /tmp/proto-check

# Build all packages
build:
	@echo "Building SDK..."
	@go build ./...
	@echo "✓ Build complete"

# Run tests
test:
	@echo "Running tests..."
	@go test ./... -v
	@echo "✓ Tests complete"

# Clean generated files
clean:
	@echo "Cleaning..."
	@rm -rf proto/
	@go clean
	@echo "✓ Clean complete"
