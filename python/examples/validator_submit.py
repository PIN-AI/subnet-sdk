
from __future__ import annotations

import asyncio
import logging

from subnet_sdk import ValidatorClient, SigningConfig
from subnet_sdk.proto.subnet import execution_report_pb2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    client = ValidatorClient(
        target="localhost:9090",
        signing_config=SigningConfig(private_key_hex="aa" * 32),
    )

    report = execution_report_pb2.ExecutionReport(
        report_id="demo-report",
        assignment_id="demo-assignment",
        intent_id="demo-intent",
        agent_id="demo-agent",
        status=execution_report_pb2.ExecutionReport.SUCCESS,
        result_data=b"demo",
        timestamp=0,
    )

    try:
        receipt = await client.submit_execution_report(report)
        logger.info("Validator receipt: %s", receipt)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
