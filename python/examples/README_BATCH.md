# 批量操作测试指南

本目录包含批量操作功能的测试示例。

## 测试脚本

### 1. 批量投标提交 (`batch_bid_submit.py`)

测试一次性提交多个投标到Matcher。

**功能测试：**
- ✅ 提交多个投标（5个）
- ✅ `partial_ok=True` 模式（允许部分失败）
- ✅ `partial_ok=False` 模式（遇到失败立即停止）
- ✅ 查看每个投标的接受/拒绝状态

### 2. 批量执行报告提交 (`batch_report_submit.py`)

测试一次性提交多个执行报告到Validator。

**功能测试：**
- ✅ 提交多个报告（5个）
- ✅ `partial_ok=True` 模式
- ✅ `partial_ok=False` 模式
- ✅ 混合状态报告（成功+失败）
- ✅ 查看每个报告的收据

## 运行前准备

### 1. 确保Subnet服务正在运行

```bash
# 启动Matcher（终端1）
cd /Users/ty/pinai/protocol/Subnet
./bin/matcher --config config/matcher-config.yaml

# 启动Validator（终端2）
./bin/validator --config config/validator-config.yaml
```

或使用一键启动脚本：

```bash
cd /Users/ty/pinai/protocol/Subnet
./start-subnet.sh
```

### 2. 安装Python SDK

```bash
cd /Users/ty/pinai/protocol/subnet-sdk/python
pip install -e .
```

## 运行测试

### 方式一：单独运行测试

```bash
cd /Users/ty/pinai/protocol/subnet-sdk/python

# 测试批量投标
PYTHONPATH=src python examples/batch_bid_submit.py

# 测试批量执行报告
PYTHONPATH=src python examples/batch_report_submit.py
```

### 方式二：使用测试脚本（推荐）

```bash
cd /Users/ty/pinai/protocol/subnet-sdk/python
./test-batch-ops.sh
```

## 预期输出

### 批量投标测试输出示例

```
INFO:__main__:准备提交 5 个投标到 intent: test-intent-1729123456
INFO:__main__:  投标 1: bid_id=bid-1, price=110
INFO:__main__:  投标 2: bid_id=bid-2, price=120
INFO:__main__:  投标 3: bid_id=bid-3, price=130
INFO:__main__:  投标 4: bid_id=bid-4, price=140
INFO:__main__:  投标 5: bid_id=bid-5, price=150

INFO:__main__:=== 测试1: 允许部分失败 (partial_ok=True) ===
INFO:__main__:批量提交结果:
INFO:__main__:  成功: 5
INFO:__main__:  失败: 0
INFO:__main__:  消息: Batch processed successfully

INFO:__main__:详细结果:
INFO:__main__:  投标 1: ✓ 接受 - 无原因
INFO:__main__:  投标 2: ✓ 接受 - 无原因
INFO:__main__:  投标 3: ✓ 接受 - 无原因
INFO:__main__:  投标 4: ✓ 接受 - 无原因
INFO:__main__:  投标 5: ✓ 接受 - 无原因

INFO:__main__:✓ 批量投标测试完成
```

### 批量执行报告测试输出示例

```
INFO:__main__:准备提交 5 个执行报告
INFO:__main__:  报告 1: report_id=report-1, intent_id=intent-1, status=SUCCESS
INFO:__main__:  报告 2: report_id=report-2, intent_id=intent-2, status=SUCCESS
INFO:__main__:  报告 3: report_id=report-3, intent_id=intent-3, status=SUCCESS
INFO:__main__:  报告 4: report_id=report-4, intent_id=intent-4, status=SUCCESS
INFO:__main__:  报告 5: report_id=report-5, intent_id=intent-5, status=SUCCESS

INFO:__main__:=== 测试1: 允许部分失败 (partial_ok=True) ===
INFO:__main__:批量提交结果:
INFO:__main__:  成功: 5
INFO:__main__:  失败: 0
INFO:__main__:  消息: Batch processed successfully

INFO:__main__:详细收据:
INFO:__main__:  报告 1: status=accepted, phase=validated, message=无消息
INFO:__main__:  报告 2: status=accepted, phase=validated, message=无消息
INFO:__main__:  报告 3: status=accepted, phase=validated, message=无消息
INFO:__main__:  报告 4: status=accepted, phase=validated, message=无消息
INFO:__main__:  报告 5: status=accepted, phase=validated, message=无消息

INFO:__main__:✓ 批量执行报告测试完成
```

## 常见问题排查

### 1. 连接失败

**错误：** `grpc._channel._InactiveRpcError: Connection refused`

**解决：**
```bash
# 检查Matcher/Validator是否运行
ps aux | grep -E 'matcher|validator'

# 检查端口
lsof -i :8090  # Matcher
lsof -i :9090  # Validator

# 启动服务
cd /Users/ty/pinai/protocol/Subnet
./start-subnet.sh
```

### 2. 导入错误

**错误：** `ModuleNotFoundError: No module named 'subnet_sdk'`

**解决：**
```bash
# 确保使用PYTHONPATH
PYTHONPATH=src python examples/batch_bid_submit.py

# 或安装SDK
pip install -e .
```

### 3. Proto导入错误

**错误：** `ImportError: cannot import name 'matcher_pb2'`

**解决：**
```bash
# 重新生成proto文件
cd /Users/ty/pinai/protocol/subnet-sdk/python
make proto
```

## 自定义测试

### 修改投标数量

编辑 `batch_bid_submit.py`:

```python
# 将这行修改为你想要的数量
for i in range(1, 11)  # 创建10个投标
```

### 修改Matcher/Validator地址

```python
client = MatcherClient(
    target="your-matcher-host:8090",  # 修改这里
    # ...
)
```

### 测试不同的失败场景

```python
# 故意创建无效投标来测试错误处理
bids = [
    bid_pb2.Bid(
        bid_id="",  # 空ID，可能导致失败
        intent_id=intent_id,
        # ...
    )
]
```

## 性能测试

要测试大批量操作的性能：

```python
# 创建1000个投标
bids = [
    bid_pb2.Bid(
        bid_id=f"bid-{i}",
        intent_id=intent_id,
        agent_id="test-agent-1",
        price=100 + i,
        currency="PIN",
    )
    for i in range(1, 1001)  # 1000个投标
]

import time
start = time.time()
response = await client.submit_bid_batch(batch_req)
elapsed = time.time() - start

logger.info("提交1000个投标耗时: %.2f秒", elapsed)
logger.info("平均每个投标: %.2f毫秒", elapsed * 1000 / 1000)
```

## 相关文档

- [Python SDK README](../README.md)
- [批量操作文档](../README.md#batch-operations)
- [Go SDK批量操作](../../go/README.md#batch-operations)
