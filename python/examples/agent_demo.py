
import asyncio
import json
import logging
from pathlib import Path
from typing import List

from subnet_sdk import (
    Config,
    ExecutionReport,
    ExecutionReportStatus,
    Handler,
    IdentityConfig,
    Metrics,
    Result,
    SDK,
    Task,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DummyHandler(Handler):
    async def execute(self, task: Task) -> Result:
        logger.info("Executing task %s of type %s", task.id, task.type)
        await asyncio.sleep(0.1)
        return Result(
            data=json.dumps({"processed": True, "task_id": task.id}).encode(),
            success=True,
        )


async def main():
    config = Config(
        identity=IdentityConfig(subnet_id="subnet-1", agent_id="demo-agent"),
        matcher_addr="localhost:8090",
        validator_addr="localhost:9090",
        registry_addr="http://localhost:8092",
        agent_endpoint="http://localhost:7000",
        capabilities=["demo"],
        private_key="" + "ab" * 32,
    )

    sdk = SDK(config)
    sdk.register_handler(DummyHandler())

    await sdk.start()
    logger.info("SDK started; press Ctrl+C to stop")

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Stopping SDK...")
        await sdk.stop()


if __name__ == "__main__":
    asyncio.run(main())
