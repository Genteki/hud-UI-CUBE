"""Local testing for UI-CUBE deterministic tasks."""
import asyncio
import os

import hud
from hud import Environment
from hud.agents import OpenAIChatAgent

DEV_URL = os.getenv("HUD_DEV_URL", "http://localhost:8765/mcp")

env = Environment("ui-cube")
env.connect_url(DEV_URL)


async def test_sample(task_id: str = "combo-box-tasks--1"):
    """Test a specific deterministic task."""
    print(f"\n=== Test: {task_id} ===")
    
    task = env("deterministic", task_id=task_id)

    async with hud.eval(task) as ctx:
        agent = OpenAIChatAgent.create(model="gpt-5")
        await agent.run(ctx, max_steps=30)
        print(f"Reward: {ctx.reward}")
        print(f"Success: {ctx.reward == 1.0}")


async def main():
    print("UI-CUBE Local Test")
    print("=" * 40)
    print(f"Container URL: {DEV_URL}")
    print("Make sure the environment server is running (hud dev --port 8765)")

    await test_sample()


if __name__ == "__main__":
    asyncio.run(main())
