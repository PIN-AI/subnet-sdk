"""
批量执行报告提交示例

演示如何使用 submit_execution_report_batch() 一次性提交多个执行报告。
"""

from __future__ import annotations

import asyncio
import logging
import time

from subnet_sdk import ValidatorClient, SigningConfig
from subnet_sdk.proto.subnet import service_pb2, execution_report_pb2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """批量提交执行报告示例"""

    # 创建validator客户端
    signing_config = SigningConfig(
        private_key_hex="aa" * 32,  # 测试私钥
        agent_id="test-agent-1",
        subnet_id="0x0000000000000000000000000000000000000000000000000000000000000002"
    )

    client = ValidatorClient(
        target="localhost:9090",
        secure=False,
        signing_config=signing_config,
    )

    try:
        # 准备多个执行报告
        base_time = int(time.time())
        reports = [
            execution_report_pb2.ExecutionReport(
                report_id=f"report-{i}",
                assignment_id=f"assignment-{i}",
                intent_id=f"intent-{i}",
                agent_id="test-agent-1",
                status=execution_report_pb2.ExecutionReport.SUCCESS,
                result_data=f"执行结果 {i}".encode('utf-8'),
                timestamp=base_time + i,
            )
            for i in range(1, 6)  # 创建5个报告
        ]

        logger.info("准备提交 %d 个执行报告", len(reports))
        for i, report in enumerate(reports, 1):
            logger.info("  报告 %d: report_id=%s, intent_id=%s, status=%s",
                       i, report.report_id, report.intent_id,
                       execution_report_pb2.ExecutionReport.Status.Name(report.status))

        # 测试1: partial_ok=True (允许部分成功)
        logger.info("\n=== 测试1: 允许部分失败 (partial_ok=True) ===")
        batch_req = service_pb2.ExecutionReportBatchRequest(
            reports=reports,
            batch_id=f"report-batch-{base_time}",
            partial_ok=True,  # 即使部分失败也继续处理
        )

        response = await client.submit_execution_report_batch(batch_req)

        logger.info("批量提交结果:")
        logger.info("  成功: %d", response.success)
        logger.info("  失败: %d", response.failed)
        logger.info("  消息: %s", response.msg)

        logger.info("\n详细收据:")
        for i, receipt in enumerate(response.receipts, 1):
            logger.info("  报告 %d: status=%s, phase=%s, message=%s",
                       i, receipt.status, receipt.phase, receipt.message or "无消息")

        # 测试2: partial_ok=False (遇到失败立即停止)
        logger.info("\n=== 测试2: 遇到失败立即停止 (partial_ok=False) ===")

        reports2 = [
            execution_report_pb2.ExecutionReport(
                report_id=f"report-strict-{i}",
                assignment_id=f"assignment-strict-{i}",
                intent_id=f"intent-strict-{i}",
                agent_id="test-agent-1",
                status=execution_report_pb2.ExecutionReport.SUCCESS,
                result_data=f"严格模式执行结果 {i}".encode('utf-8'),
                timestamp=base_time + 100 + i,
            )
            for i in range(1, 4)  # 创建3个报告
        ]

        batch_req2 = service_pb2.ExecutionReportBatchRequest(
            reports=reports2,
            batch_id=f"report-batch-strict-{base_time}",
            partial_ok=False,  # 任何失败都停止
        )

        response2 = await client.submit_execution_report_batch(batch_req2)

        logger.info("批量提交结果:")
        logger.info("  成功: %d", response2.success)
        logger.info("  失败: %d", response2.failed)
        logger.info("  消息: %s", response2.msg)

        logger.info("\n详细收据:")
        for i, receipt in enumerate(response2.receipts, 1):
            logger.info("  报告 %d: status=%s, phase=%s, message=%s",
                       i, receipt.status, receipt.phase, receipt.message or "无消息")

        # 测试3: 混合状态（包含成功和失败的报告）
        logger.info("\n=== 测试3: 混合状态报告 ===")

        mixed_reports = [
            execution_report_pb2.ExecutionReport(
                report_id=f"report-mixed-{i}",
                assignment_id=f"assignment-mixed-{i}",
                intent_id=f"intent-mixed-{i}",
                agent_id="test-agent-1",
                status=execution_report_pb2.ExecutionReport.SUCCESS if i % 2 == 0
                       else execution_report_pb2.ExecutionReport.FAILURE,
                result_data=f"混合结果 {i}".encode('utf-8'),
                timestamp=base_time + 200 + i,
            )
            for i in range(1, 5)
        ]

        batch_req3 = service_pb2.ExecutionReportBatchRequest(
            reports=mixed_reports,
            batch_id=f"report-batch-mixed-{base_time}",
            partial_ok=True,
        )

        response3 = await client.submit_execution_report_batch(batch_req3)

        logger.info("批量提交结果:")
        logger.info("  成功: %d", response3.success)
        logger.info("  失败: %d", response3.failed)
        logger.info("  消息: %s", response3.msg)

        logger.info("\n✓ 批量执行报告测试完成")

    except Exception as e:
        logger.error("批量报告提交失败: %s", e, exc_info=True)
        raise
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
