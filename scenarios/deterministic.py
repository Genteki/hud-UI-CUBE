"""Deterministic benchmark scenarios loaded from deterministic_bench.json."""
import json
import logging
from pathlib import Path
from typing import Any

from setup.navigate import navigate_to_url

logger = logging.getLogger(__name__)

# Local copy of the dataset (added under data/)
TASKS_FILE = Path(__file__).parent.parent / "data" / "deterministic_bench.json"

# Load all tasks once at module level
try:
    _ALL_TASKS = json.loads(TASKS_FILE.read_text())
    _TASKS_BY_ID = {task["id"]: task for task in _ALL_TASKS if task.get("id")}
    logger.info("Loaded %d deterministic tasks", len(_TASKS_BY_ID))
except Exception as exc:
    logger.error("Failed to load deterministic tasks from %s: %s", TASKS_FILE, exc)
    _TASKS_BY_ID = {}


def register_deterministic_scenarios(env: Any) -> None:
    """Register a single parameterized scenario for all deterministic tasks."""
    
    @env.scenario("deterministic")
    async def deterministic_scenario(task_id: str):
        """Run a deterministic benchmark task by ID.
        
        Args:
            task_id: The task ID (e.g., 'combo-box-tasks--1')
        """
        from env import persistent_ctx

        # Look up the task
        task = _TASKS_BY_ID.get(task_id)
        if not task:
            logger.error("Task not found: %s", task_id)
            logger.error("Available tasks: %s", list(_TASKS_BY_ID.keys())[:10])
            yield 0.0
            return

        ques = task.get("ques", "")
        ux_hint = task.get("ux_hint", "")
        web_url = task.get("web", "")

        tool = persistent_ctx.playwright_tool if persistent_ctx else None
        if not tool:
            logger.warning("No playwright tool; cannot run task %s", task_id)
            yield 0.0
            return

        # Navigate to the task URL
        if web_url:
            await navigate_to_url(tool, web_url)

        # Build prompt
        parts = [ques]
        if ux_hint:
            parts.append(f"\nHint: {ux_hint}")
        if web_url:
            parts.append(f"\nURL: {web_url}")
        prompt = "\n".join(parts)

        _ = yield prompt

        # Verification: check for UI-CUBE success marker in DOM
        try:
            if tool.page:
                html = await tool.page.content()
                success = ">code#1</" in html
                yield 1.0 if success else 0.0
            else:
                yield 0.0
        except Exception as exc:
            logger.error("Verification failed for %s: %s", task_id, exc)
            yield 0.0
    
    # Also register individual task IDs for backward compatibility
    for task_id in _TASKS_BY_ID.keys():
        @env.scenario(task_id)
        async def _compat_scenario(task_id=task_id):
            """Backward compatibility wrapper."""
            async for result in deterministic_scenario(task_id):
                yield result
