"""Local testing for UI-CUBE deterministic tasks."""

import asyncio
import os

import hud
from hud import Environment
from hud.agents import create_agent
from prompts import SYSTEM_PROMPT
from hud.agents.gemini_cua import GeminiCUAAgent
from hud.agents import OpenAIAgent
from hud.agents import OperatorAgent
import logging

logger = logging.getLogger(__name__)

DEV_URL = os.getenv("HUD_DEV_URL", "http://localhost:8765/mcp")

env = Environment("ui-cube")
env.connect_url(DEV_URL)

# model = "gpt-5.1"
# model = "grok-4-1-fast"
# model = "z-ai/glm-4.5v"
# model = "claude-sonnet-4-5"
# model = "gemini-3-pro-preview"
model = "claude-sonnet-4-5"
max_steps = 30


async def test_sample(task_id: str = "combo-box-tasks--1"):
    """Test a specific deterministic task."""
    print(f"\n=== Test: {task_id} ===")

    task = env("deterministic", task_id=task_id)
    logger.info(f"SYSTEM_MESSAGE: {SYSTEM_PROMPT}")
    async with hud.eval(task) as ctx:
        agent = create_agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            disallowed_tools=["hud-logs", "gemnini_computer"],
        )

        # agent = OperatorAgent.create(
        #     model="computer-use-preview",
        #     system_prompt=SYSTEM_PROMPT,
        #     disallowed_tools=["hud-logs"],
        #     validate_api_key=False,
        # )
        # agent = GeminiCUAAgent.create(
        #     model="gemini-2.5-computer-use-preview-10-2025",
        #     system_prompt=SYSTEM_PROMPT,
        #     disallowed_tools=["hud-logs"],
        #     validate_api_key=False,
        # )
        await agent.run(ctx, max_steps=max_steps)
        print(f"Reward: {ctx.reward}")
        print(f"Success: {ctx.reward == 1.0}")


async def main():
    print("UI-CUBE Local Test")
    print("=" * 40)
    # await test_sample()
    await test_sample("navigation-search-interaction--16")


if __name__ == "__main__":
    asyncio.run(main())
