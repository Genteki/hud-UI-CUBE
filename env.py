"""UI-CUBE Environment using a local Playwright browser."""
import asyncio
import logging
import os
import sys
from datetime import datetime
from typing import Any, TypedDict, cast

# CRITICAL: Register this module as 'env' so imports work correctly
# even when running as __main__
if __name__ == "__main__":
    sys.modules["env"] = sys.modules[__name__]

from hud import Environment
from hud.tools.types import ContentResult
from scenarios import register_scenarios
from tools.browser import router as browser_router

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s | %(name)s | %(message)s",
    force=True,
)
logger = logging.getLogger(__name__)


# Global state
playwright_tool = None
browser_executor = None

# Create Environment instance
env = Environment(name="ui-cube")

class Telemetry(TypedDict):
    provider: str
    status: str
    timestamp: str
    live_url: str | None

@env.resource("telemetry://live")
async def get_telemetry_resource() -> Telemetry:
    return Telemetry(
        provider="local",
        status="running" if playwright_tool else "not_initialized",
        live_url=os.getenv("UI_CUBE_BASE_URL"),
        timestamp=datetime.now().isoformat(),
    )

@env.initialize
async def initialize_environment() -> None:
    """Initialize the UI-CUBE environment."""
    global playwright_tool, browser_executor

    from hud.tools.executors.pyautogui import PyAutoGUIExecutor
    from hud.tools.executors.xdo import XDOExecutor
    from tools.browser import PlaywrightTool, BrowserExecutor
    from tools.computer import register_computer_tools

    try:
        logger.info("Initializing local Playwright tool...")
        playwright_tool = PlaywrightTool(cdp_url=None)
        logger.info("Playwright tool ready (browser launches lazily)")


        executor_type = os.environ.get("COMPUTER_EXECUTOR", "playwright").lower()
        if executor_type == "xdo":
            if not XDOExecutor.is_available():
                logger.warning(
                    "XDOExecutor unavailable; falling back to Playwright executor"
                )
                browser_executor = BrowserExecutor(cast(Any, playwright_tool))
            else:
                browser_executor = XDOExecutor()
        elif executor_type == "pyautogui":
            if not PyAutoGUIExecutor.is_available():
                logger.warning(
                    "PyAutoGUIExecutor unavailable; falling back to Playwright executor"
                )
                browser_executor = BrowserExecutor(cast(Any, playwright_tool))
            else:
                browser_executor = PyAutoGUIExecutor()
        else:
            browser_executor = BrowserExecutor(cast(Any, playwright_tool))

        logger.info("Computer executor selected: %s", browser_executor.__class__.__name__)
        register_computer_tools(env, browser_executor)
        logger.info("Tools registered")

        initial_url = os.getenv("BROWSER_URL")
        if initial_url:
            await playwright_tool.navigate(initial_url)

        logger.info("UI-CUBE environment ready!")

    except Exception as e:
        logger.error("Initialization failed: %s", e)
        import traceback
        logger.error("Traceback: %s", traceback.format_exc())
        raise


@env.tool("navigate_to")
async def tool_navigate(url: str) -> ContentResult:
    """Navigate the browser to a URL."""
    if not playwright_tool:
        return ContentResult(error="No browser available")
    try:
        result = await playwright_tool.navigate(url=url, wait_for_load_state="load")
        success = bool(result.get("success"))
        error = result.get("error") or (None if success else "Navigation failed")
        return ContentResult(output=f"Navigated to {url}" if success else None, error=error)
    except BaseException as e:
        return ContentResult(error=str(e))


@env.tool("wait")
async def tool_wait(seconds: float) -> ContentResult:
    """Wait for a number of seconds."""
    try:
        await asyncio.sleep(min(seconds, 5.0))
        return ContentResult(output=f"Waited {seconds} seconds")
    except BaseException as e:
        return ContentResult(error=str(e))

@env.shutdown
async def shutdown_environment() -> None:
    global playwright_tool, browser_executor

    logger.info("Shutting down UI-CUBE environment...")

    playwright_tool = None
    browser_executor = None


env.include_router(browser_router)

register_scenarios(env)


if __name__ == "__main__":
    env.run(transport="stdio")
