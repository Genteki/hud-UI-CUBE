"""Local testing for UI-CUBE deterministic tasks."""

import asyncio
import logging
import os

import hud
from hud import Environment
from hud.agents import create_agent
from prompts import SYSTEM_PROMPT
from hud.agents.glm_cua import GLMCUA

# Configure logging to show INFO level messages
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

DEV_URL = os.getenv("HUD_DEV_URL", "http://localhost:8765/mcp")

env = Environment("ui-cube")
env.connect_url(DEV_URL)

model = "z-ai/glm-4.5v"
# model = "claude-haiku-4-5"
max_steps = 10
allowed_tools = ["glm_computer"]

async def test_sample(task_id: str = "combo-box-tasks--1"):
    """Test a specific deterministic task."""
    print(f"\n=== Test: {task_id} ===")

    task = env("deterministic", task_id=task_id)
    task.env._agent_include = allowed_tools
    logger.info(f"SYSTEM_MESSAGE: {SYSTEM_PROMPT}")
    async with hud.eval(task) as ctx:
        # agent = create_agent(
        #     model=model,
        #     system_prompt=SYSTEM_PROMPT,
        # )
        agent = GLMCUA.create(
            model=model,
            # system_prompt=SYSTEM_PROMPT,
        )
        await agent.run(ctx, max_steps=max_steps)
        print(f"Reward: {ctx.reward}")
        print(f"Success: {ctx.reward == 1.0}")

async def main():
    print("UI-CUBE Local Test")
    print("=" * 40)
    await test_sample()
    # await test_sample("navigation-search-interaction--16")


if __name__ == "__main__":
    asyncio.run(main())
