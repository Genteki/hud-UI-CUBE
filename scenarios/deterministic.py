"""Deterministic benchmark scenarios loaded from deterministic_bench.json."""
import json
import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

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
    
    def _localize_url(url: str) -> str:
        base = os.getenv("UI_CUBE_BASE_URL", "http://localhost:3000")
        if not url or not base:
            return url
        try:
            src = urlparse(url)
            dst = urlparse(base)
            return urlunparse(
                (dst.scheme or src.scheme, dst.netloc, src.path, src.params, src.query, src.fragment)
            )
        except Exception:
            return url

    @env.scenario("deterministic")
    async def deterministic_scenario(task_id: str):
        """Run a deterministic benchmark task by ID.
        
        Args:
            task_id: The task ID (e.g., 'combo-box-tasks--1')
        """
        import env as env_module
        
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

        # Localize the URL
        if web_url:
            web_url = _localize_url(web_url)

        # Get the playwright tool
        tool = env_module.playwright_tool
        if not tool:
            logger.warning("No playwright tool; cannot run task %s", task_id)
            yield 0.0
            return

        # Navigate to the task URL BEFORE yielding prompt (so screenshots work)
        if web_url:
            logger.info("Navigating to task URL: %s", web_url)
            await tool.navigate(web_url)  # type: ignore[misc]

        # Take initial screenshot to capture the starting state
        initial_screenshot = None
        try:
            initial_screenshot = await tool.screenshot()  # type: ignore[misc]
            logger.info("Captured initial screenshot for task: %s", task_id)
        except Exception as e:
            logger.warning("Failed to capture initial screenshot: %s", e)

        # Build and yield prompt
        parts = [ques]
        if ux_hint:
            parts.append(f"\nHint: {ux_hint}")
        if web_url:
            parts.append(f"\nURL: {web_url}")
        prompt = "\n".join([ques])

        # Yield prompt with initial screenshot as setup output
        # The screenshot will be available to the agent via ctx.setup_output
        if initial_screenshot:
            _ = yield {"prompt": prompt, "screenshot": initial_screenshot}
        else:
            _ = yield prompt

        # ===== VERIFICATION PHASE =====
        # Re-fetch tool in case state changed
        tool = env_module.playwright_tool
        
        try:
            if tool and tool.page:
                html = await tool.page.content()  # type: ignore[union-attr]
                success = ">code#1</" in html
                yield 1.0 if success else 0.0
            else:
                logger.warning("No browser page available for verification")
                yield 0.0
        except Exception as exc:
            logger.error("Verification failed for %s: %s", task_id, exc)
            yield 0.0
