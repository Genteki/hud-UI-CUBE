"""
Context server for UI-CUBE environment (persistent across hot-reloads).
"""

import asyncio
import logging
import multiprocessing
from datetime import datetime
from typing import Any, Dict, Optional

from hud.server.context import run_context_server

logger = logging.getLogger(__name__)


class UICubeContext:
    """Context that holds remote browser state across reloads."""

    def __init__(self):
        self.browser_provider = None
        self.is_initialized = False
        self.provider_config: Optional[Dict[str, Any]] = None
        self.launch_options: Optional[Dict[str, Any]] = None
        self._startup_complete = False
        self.playwright_tool = None
        self._telemetry: Optional[Dict[str, Any]] = None

        logger.info("[UICubeContext] Created new context")

    def startup(self):
        if self._startup_complete:
            logger.info("[UICubeContext] Startup already complete, skipping")
            return
        self._startup_complete = True
        logger.info("[UICubeContext] Startup complete")

    def get_browser_provider(self):
        return self.browser_provider

    def set_browser_provider(self, provider) -> None:
        self.browser_provider = provider
        if provider:
            self.provider_name = provider.__class__.__name__.replace("Provider", "").lower()
            logger.info(f"[UICubeContext] Set browser provider: {self.provider_name}")

    def get_cdp_url(self) -> Optional[str]:
        return self._telemetry.get("cdp_url") if self._telemetry else None

    def get_is_initialized(self) -> bool:
        return self.is_initialized

    def set_initialized(self, value: bool) -> None:
        self.is_initialized = value
        logger.info(f"[UICubeContext] Initialization status: {value}")

    def get_provider_config(self) -> Optional[Dict[str, Any]]:
        return self.provider_config

    def set_provider_config(self, config: Dict[str, Any]) -> None:
        self.provider_config = config
        logger.info("[UICubeContext] Set provider config")

    def get_launch_options(self) -> Optional[Dict[str, Any]]:
        return self.launch_options

    def set_launch_options(self, options: Dict[str, Any]) -> None:
        self.launch_options = options
        logger.info("[UICubeContext] Set launch options")

    def get_playwright_tool(self):
        return self.playwright_tool

    def set_playwright_tool(self, tool) -> None:
        self.playwright_tool = tool
        logger.info("[UICubeContext] Set playwright tool")

    def set_telemetry(self, telemetry: Dict[str, Any]) -> None:
        self._telemetry = telemetry
        logger.info(f"[UICubeContext] Set telemetry: {telemetry}")

    def get_state_summary(self) -> Dict[str, Any]:
        return {
            "is_initialized": self.is_initialized,
            "startup_complete": self._startup_complete,
            "provider_name": self._telemetry.get("provider") if self._telemetry else None,
            "has_cdp_url": self.get_cdp_url() is not None,
            "has_browser_provider": self.browser_provider is not None,
            "has_playwright_tool": self.playwright_tool is not None,
        }

    def get_telemetry(self) -> Dict[str, Any]:
        if self._telemetry:
            return self._telemetry
        return {
            "provider": "unknown",
            "status": "not_initialized",
            "live_url": None,
            "cdp_url": None,
            "instance_id": None,
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    multiprocessing.set_start_method("fork", force=True)
    ctx = UICubeContext()
    ctx.startup()
    logger.info("[Context] Starting UI-CUBE context server")
    logger.info("[Context] Initial state: %s", ctx.get_state_summary())
    asyncio.run(run_context_server(ctx, "/tmp/hud_ui_cube_ctx.sock"))
