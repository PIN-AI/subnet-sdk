# Proto Setup for Subnet SDK

## 现状

SDK 现在拥有自己独立的 proto 生成代码，**不再依赖主 Subnet 项目**。

## 目录结构

```
subnet-sdk/go/
├── proto/
│   └── subnet/          # 从 pin_protocol 生成的 proto
│       ├── agent.pb.go
│       ├── bid.pb.go
│       ├── matcher_service.pb.go
│       ├── ...
│       └── *.pb.go
├── matcher_client.go    # 使用 pb "subnet/proto/subnet"
├── validator_client.go  # 使用 pb "subnet/proto/subnet"
├── streaming.go         # 使用 pb "subnet/proto/subnet"
├── go.mod               # replace subnet => ./
└── Makefile             # proto 生成自动化
```

## go.mod 配置

```go
module github.com/PIN-AI/subnet-sdk/go

require (
    github.com/ethereum/go-ethereum v1.16.4
    google.golang.org/grpc v1.75.0
    google.golang.org/protobuf v1.36.8
    subnet v0.0.0-00010101000000-000000000000  // 用于 proto import
)

// Proto 文件使用 "subnet/proto/subnet" 作为 go_package
// 通过 replace 指向 SDK 自己的 proto 目录
replace subnet => ./
```

**关键点：**
- `subnet v0.0.0` 是虚拟依赖，仅用于满足 proto import 路径
- `replace subnet => ./` 让 `subnet/proto/subnet` 解析为 SDK 自己的 `proto/subnet`
- **不再依赖主 Subnet 项目**

## Proto 生成流程

### 1. 生成 Proto

```bash
make proto
```

这会从 `../../pin_protocol/proto/subnet/*.proto` 生成 Go 代码到 `proto/subnet/`。

### 2. 检查 Proto 同步

```bash
make proto-check
```

检查 SDK 的 proto 是否与 pin_protocol 保持同步。

### 3. 构建 SDK

```bash
make build
```

### 4. 运行测试

```bash
make test
```

## Proto 同步策略

### 何时需要重新生成 Proto？

当 `pin_protocol/proto/subnet/` 中的 proto 文件更新时：

1. **手动同步：**
   ```bash
   cd subnet-sdk/go
   make proto
   git add proto/
   git commit -m "chore: sync proto with pin_protocol"
   ```

2. **验证同步：**
   ```bash
   make proto-check
   ```

### CI/CD 集成

在 `.github/workflows/` 中添加 proto sync 检查：

```yaml
- name: Check Proto Sync
  run: |
    cd go
    make proto-check
```

## Import 路径

SDK 代码中统一使用：

```go
import pb "subnet/proto/subnet"
```

**不要使用：**
- ~~`import pb "github.com/PIN-AI/subnet-sdk/go/proto/subnet"`~~（太长）
- ~~`import pb "../../Subnet/proto/subnet"`~~（依赖主项目）

## 与主 Subnet 项目的关系

### 之前（错误）：

```
SDK → Subnet → proto/subnet/  ❌ 循环依赖
  ↑_____________↓
```

### 现在（正确）：

```
pin_protocol/proto/subnet/
    ↓ make proto          ↓ make proto
SDK/proto/subnet/      Subnet/proto/subnet/
    ↓                       ↓
SDK 代码                  Subnet 代码

完全独立，无依赖 ✓
```

## 发布流程

### 1. 同步 Proto

```bash
cd subnet-sdk/go
make proto
make proto-check
```

### 2. 测试

```bash
make build
make test
```

### 3. 提交并打标签

```bash
git add proto/ go.mod go.sum
git commit -m "chore: sync proto and prepare v0.1.0"
git tag v0.1.0
git push origin main v0.1.0
```

### 4. 主 Subnet 项目更新依赖

```bash
cd ../../Subnet
go get github.com/PIN-AI/subnet-sdk/go@v0.1.0
go mod tidy
```

## 常见问题

### Q: 为什么需要 `replace subnet => ./`？

A: 因为 proto 文件中的 `go_package` 是 `subnet/proto/subnet;pb`，这是为了与主 Subnet 项目的路径兼容。通过 replace，我们让 SDK 的 import 路径也能正确解析。

### Q: SDK 独立后，如何更新 proto？

A:
1. `pin_protocol` 更新 proto 定义
2. SDK 运行 `make proto` 重新生成
3. 主 Subnet 项目也运行 `make proto` 重新生成
4. 各自独立发布

### Q: Proto 版本不同步会怎样？

A: 如果 SDK 和主项目的 proto 版本不同步，可能导致：
- gRPC 调用失败（字段不匹配）
- 数据序列化错误
- 运行时类型错误

建议使用 CI/CD 检查确保同步。

## 总结

✅ SDK 现在完全独立，不依赖主 Subnet 项目
✅ Proto 从权威源（pin_protocol）生成
✅ 使用 `replace subnet => ./` 解决 import 路径
✅ Makefile 自动化 proto 生成和检查
✅ 可以独立发布到独立仓库
