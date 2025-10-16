"""
批量投标提交示例

演示如何使用 submit_bid_batch() 一次性提交多个投标。
"""

from __future__ import annotations

import asyncio
import logging
import time

from subnet_sdk import MatcherClient, SigningConfig
from subnet_sdk.proto.subnet import matcher_pb2, bid_pb2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """批量提交投标示例"""

    # 创建matcher客户端
    signing_config = SigningConfig(
        private_key_hex="aa" * 32,  # 测试私钥
        agent_id="test-agent-1",
        subnet_id="0x0000000000000000000000000000000000000000000000000000000000000002"
    )

    client = MatcherClient(
        target="localhost:8090",
        secure=False,
        signing_config=signing_config,
    )

    try:
        # 准备多个投标
        intent_id = "test-intent-" + str(int(time.time()))
        bids = [
            bid_pb2.Bid(
                bid_id=f"bid-{i}",
                intent_id=intent_id,
                agent_id="test-agent-1",
                price=100 + i * 10,  # 不同的价格
                currency="PIN",
            )
            for i in range(1, 6)  # 创建5个投标
        ]

        logger.info("准备提交 %d 个投标到 intent: %s", len(bids), intent_id)
        for i, bid in enumerate(bids, 1):
            logger.info("  投标 %d: bid_id=%s, price=%d", i, bid.bid_id, bid.price)

        # 测试1: partial_ok=True (允许部分成功)
        logger.info("\n=== 测试1: 允许部分失败 (partial_ok=True) ===")
        batch_req = matcher_pb2.SubmitBidBatchRequest(
            bids=bids,
            batch_id=f"batch-{int(time.time())}",
            partial_ok=True,  # 即使部分失败也继续处理
        )

        response = await client.submit_bid_batch(batch_req)

        logger.info("批量提交结果:")
        logger.info("  成功: %d", response.success)
        logger.info("  失败: %d", response.failed)
        logger.info("  消息: %s", response.msg)

        logger.info("\n详细结果:")
        for i, ack in enumerate(response.acks, 1):
            status = "✓ 接受" if ack.accepted else "✗ 拒绝"
            logger.info("  投标 %d: %s - %s", i, status, ack.reason or "无原因")

        # 测试2: partial_ok=False (遇到失败立即停止)
        logger.info("\n=== 测试2: 遇到失败立即停止 (partial_ok=False) ===")

        bids2 = [
            bid_pb2.Bid(
                bid_id=f"bid-strict-{i}",
                intent_id=intent_id + "-strict",
                agent_id="test-agent-1",
                price=200 + i * 20,
                currency="PIN",
            )
            for i in range(1, 4)  # 创建3个投标
        ]

        batch_req2 = matcher_pb2.SubmitBidBatchRequest(
            bids=bids2,
            batch_id=f"batch-strict-{int(time.time())}",
            partial_ok=False,  # 任何失败都停止
        )

        response2 = await client.submit_bid_batch(batch_req2)

        logger.info("批量提交结果:")
        logger.info("  成功: %d", response2.success)
        logger.info("  失败: %d", response2.failed)
        logger.info("  消息: %s", response2.msg)

        logger.info("\n详细结果:")
        for i, ack in enumerate(response2.acks, 1):
            status = "✓ 接受" if ack.accepted else "✗ 拒绝"
            logger.info("  投标 %d: %s - %s", i, status, ack.reason or "无原因")

        logger.info("\n✓ 批量投标测试完成")

    except Exception as e:
        logger.error("批量投标提交失败: %s", e, exc_info=True)
        raise
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
