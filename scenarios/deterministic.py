"""Deterministic benchmark scenarios loaded from deterministic_bench.json."""
import json
import logging
from pathlib import Path
from typing import Any

from setup.navigate import navigate_to_url

logger = logging.getLogger(__name__)

# Local copy of the dataset (added under data/)
TASKS_FILE = Path(__file__).parent.parent / "data" / "deterministic_bench.json"


def register_deterministic_scenarios(env: Any) -> None:
    """Register each deterministic task as an env scenario."""
    try:
        tasks = json.loads(TASKS_FILE.read_text())
    except Exception as exc:
        logger.error("Failed to load deterministic tasks from %s: %s", TASKS_FILE, exc)
        return

    logger.info("Loading %d deterministic tasks", len(tasks))

    for task in tasks:
        task_id = task.get("id")
        ques = task.get("ques", "")
        ux_hint = task.get("ux_hint", "")
        web_url = task.get("web", "")

        if not task_id:
            continue

        @env.scenario(task_id)
        async def _scenario(ques=ques, ux_hint=ux_hint, web_url=web_url):
            from env import persistent_ctx

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

