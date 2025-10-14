# Python SDK Examples

以下示例假设本地已启动必要的 matcher、validator、registry 服务，并且 proto 定义保存在 `../pin_protocol`。

## 1. 综合代理示例

`examples/agent_demo.py`

- 运行一个简单的 `Handler`，订阅 matcher 的任务流并将执行结果通过 SDK 自动上报到 validator。
- 配置示例：
  ```python
  config = Config(
      identity=IdentityConfig(subnet_id="subnet-1", agent_id="demo-agent"),
      matcher_addr="localhost:8090",
      validator_addr="localhost:9090",
      registry_addr="http://localhost:8092",
      agent_endpoint="http://localhost:7000",
      capabilities=["demo"],
      intent_types=["demo"],
      private_key="ab" * 32,
  )

  # 具体策略/回调实现可参考 README 中的示例
  sdk.register_bidding_strategy(FixedPriceStrategy())
  sdk.register_callbacks(LifecycleCallbacks())
  ```
- 运行：`python examples/agent_demo.py`

如需参与 matcher 竞价，可实现自定义 `BiddingStrategy` 和 `Callbacks`，SDK 会自动通过 `StreamIntents`→`SubmitBid`→`StreamTasks` 串起完整链路。

## 2. Matcher 流调试

`examples/matcher_stream.py`

- 独立连接 matcher，订阅 `StreamTasks`，打印接收到的 `ExecutionTask`。
- 可用于验证 matcher 推送任务是否正常。

运行：`python examples/matcher_stream.py`

## 3. Validator 提交流程

`examples/validator_submit.py`

- 演示如何使用 `ValidatorClient` 手动提交 gRPC 执行报告。
- 构造了一个 `ExecutionReport` 并调用 `submit_execution_report`，输出 validator 返回的 receipt。

运行：`python examples/validator_submit.py`

> 以上示例仅用于联调说明，实际生产环境应结合真实的 bidding 策略、回调和错误处理。
