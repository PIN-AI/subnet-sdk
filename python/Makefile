.PHONY: proto proto-check clean test install dev

# Proto source directory
PROTO_SRC = ../proto-src

# 生成 proto 文件
proto:
	@echo "Generating proto files from $(PROTO_SRC)..."
	@python -m grpc_tools.protoc \
		-I$(PROTO_SRC) \
		--python_out=src \
		--grpc_python_out=src \
		--pyi_out=src \
		$(PROTO_SRC)/subnet/*.proto
	@echo "Moving proto files to correct location..."
	@mkdir -p src/subnet_sdk/proto/subnet
	@mv src/subnet/*_pb2*.py src/subnet_sdk/proto/subnet/ 2>/dev/null || true
	@rmdir src/subnet 2>/dev/null || true
	@echo "Fixing proto imports..."
	@find src/subnet_sdk/proto/subnet -name "*_pb2*.py" -exec sed -i '' \
		's/from subnet import/from subnet_sdk.proto.subnet import/g' {} \;
	@echo "✓ Proto generation complete"

# 检查 proto 是否正确
proto-check:
	@echo "Checking proto imports..."
	@cd src && python -c "\
		from subnet_sdk.proto.subnet import agent_pb2; \
		from subnet_sdk.proto.subnet import matcher_service_pb2; \
		from subnet_sdk.proto.subnet import service_pb2; \
		print('✓ Proto imports OK')" || \
		(echo "❌ Proto imports failed. Run 'make proto'" && exit 1)

# 清理生成的文件和缓存
clean:
	@echo "Cleaning generated files and cache..."
	@rm -rf src/subnet_sdk/proto/subnet/*.py
	@rm -rf src/subnet_sdk/proto/subnet/*.pyi
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf build/ dist/ *.egg-info 2>/dev/null || true
	@echo "✓ Clean complete"

# 安装依赖
install:
	@pip install -e .

# 安装开发依赖
dev:
	@pip install -e ".[dev]"

# 运行测试
test:
	@pytest tests/ -v
