# Python SDK Roadmap

本路线图用于跟踪 Python 版 Subnet SDK 尚待补齐的核心能力，按依赖顺序列出实施阶段及关键任务，后续迭代可在此基础上更新。

## Phase 1 · gRPC 基座与签名拦截器
- 生成 matcher、validator 等服务的 Python gRPC stub（proto 源自 `pin_protocol/proto/subnet/*.proto`）。
- 封装统一的 gRPC 连接管理（channel 复用、超时设置、异常转换）。
- 实现私钥签名拦截器：参考 Go 侧 `internal/grpc/interceptors/auth.go`，在 metadata 中附带 `x-signature`、`x-signer-id`、`x-timestamp`、`x-nonce` 等字段。
- 单元测试：覆盖配置校验、签名编码、时间窗口/Nonce 校验等。

## Phase 2 · Matcher 客户端
- 提供 `SubmitBid`、`StreamIntents`、`StreamTasks`、`RespondToTask` 等 RPC 封装。
- 设计事件循环：
  - 拉取 intents 并根据 `BiddingStrategy` 决策是否投标。
  - 接收任务流并触发 `Handler.execute`。
  - 对任务接受/拒绝结果更新状态并调用 `Callbacks`。
- 与 metrics/日志打通，记录投标次数、成功率、任务处理耗时等。
- 增加集成测试或 mock 测试验证投标/任务流链路。

## Phase 3 · Validator 客户端
- 改造执行报告提交流程，调用 `ValidatorService.SubmitExecutionReport`，复用签名拦截器。
- 解析 protobuf 回执，补充重试策略、错误分类与指标统计。
- 预留 `GetValidatorSet`、`GetValidationPolicy` 等查询接口，便于健康检查和调试。
- 补充测试：模拟 validator 返回的成功/失败/超时场景。

## Phase 4 · 生命周期与回调补强
- Registry 注册流程与 matcher/validator 链路统一，必要时迁移到 gRPC。
- 补齐 `Callbacks` 触发点：竞价成功/失败、任务接受/拒绝、执行报告提交成功/失败等。
- 确保 `Metrics` 与 `Callbacks` 协同，不遗漏关键事件。
- 更新日志格式，附带 intent/assignment 等上下文信息。

## Phase 5 · 测试、示例与文档收尾
- 扩展单元测试覆盖率，特别是网络交互的 mock 测试。
- 编写示例脚本，演示 SDK 如何连接 matcher 与 validator（可复用仓库内 mock 服务）。
- 更新 `README.md`、`docs/quick-start.md`、`docs/tutorial.md`，加入 gRPC 版流程说明。
- 设立回归清单，确保“注册 → 竞价 → 执行 → 上报”链路在 PR 中均有验证记录。

> 若计划或依赖发生变化，可直接在本文件更新阶段内容或新增阶段，以保持 roadmap 与实现同步。
