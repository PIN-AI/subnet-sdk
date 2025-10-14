
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from subnet_sdk import MatcherClient, SigningConfig
from subnet_sdk.proto.subnet import matcher_service_pb2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    client = MatcherClient(
        target="localhost:8090",
        signing_config=SigningConfig(private_key_hex="aa" * 32),
    )

    request = matcher_service_pb2.StreamTasksRequest(agent_id="demo-agent")
    try:
        async for task in client.stream_tasks(request):
            logger.info("Task from matcher: %s", task)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
