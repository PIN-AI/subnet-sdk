"""
Example usage of Subnet SDK for Python.
"""

import asyncio
import logging
from datetime import datetime
from subnet_sdk import SDK, ConfigBuilder, Handler, Task, Result

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExampleHandler(Handler):
    """Example task handler implementation."""

    async def execute(self, task: Task) -> Result:
        """Execute task based on type."""
        logger.info(f"Executing task {task.id} of type {task.type}")

        # Simulate different task types
        if task.type == "compute":
            # Simulate computation
            await asyncio.sleep(2)
            return Result(
                data=b"computation result",
                success=True
            )

        elif task.type == "storage":
            # Simulate storage operation
            await asyncio.sleep(1)
            return Result(
                data=b"storage result",
                success=True
            )

        else:
            return Result(
                data=b"",
                success=False,
                error=f"Unsupported task type: {task.type}"
            )


async def main():
    """Main entry point."""

    # Build configuration
    # IMPORTANT: No default IDs - must be explicitly configured
    config = (
        ConfigBuilder()
        .with_subnet_id("my-subnet-1")      # REQUIRED
        .with_agent_id("my-agent-1")        # REQUIRED
        .with_private_key("a" * 64)          # Example key (64 hex chars, no 0x prefix)
        .with_matcher_addr("localhost:8090") # REQUIRED
        .with_capabilities("compute", "storage")  # REQUIRED
        .with_task_timeout(60)
        .with_max_concurrent_tasks(10)
        .with_bidding_strategy("dynamic", 50, 500)
        .build()
    )

    # Create SDK instance
    sdk = SDK(config)

    # Register handler
    handler = ExampleHandler()
    sdk.register_handler(handler)

    # Start SDK
    await sdk.start()
    logger.info(f"Agent started: {sdk.get_agent_id()}")

    # Example: Execute a task manually
    example_task = Task(
        id="task-123",
        intent_id="intent-456",
        type="compute",
        data=b"example data",
        metadata={"priority": "high"},
        deadline=datetime.now(),
        created_at=datetime.now()
    )

    result = await sdk.execute_task(example_task)
    if result.success:
        logger.info(f"Task completed: {result.data}")
    else:
        logger.error(f"Task failed: {result.error}")

    # Get metrics
    metrics = sdk.get_metrics()
    completed, failed, total_bids, won_bids = metrics.get_stats()
    logger.info(f"Metrics - Tasks: {completed} completed, {failed} failed")
    logger.info(f"Metrics - Bids: {won_bids} won out of {total_bids} total")

    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await sdk.stop()


if __name__ == "__main__":
    asyncio.run(main())
