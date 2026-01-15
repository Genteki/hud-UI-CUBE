"""Computer tools registration."""
from typing import Any

from hud.tools.computer import (
    AnthropicComputerTool,
    OpenAIComputerTool,
    HudComputerTool,
    GeminiComputerTool,
    QwenComputerTool,
)
from tools.browser import router

# Create tool instances at module level with None executor
# The executor will be set during initialization
_tools = [
    AnthropicComputerTool(executor=None),
    OpenAIComputerTool(executor=None),
    HudComputerTool(executor=None),
    GeminiComputerTool(executor=None),
    QwenComputerTool(executor=None),
]

# Register tools on the browser router at module level
for tool in _tools:
    router.add_tool(tool)


def register_computer_tools(env: Any, browser_executor: Any) -> None:
    """Set the executor for all computer tools."""
    for tool in _tools:
        tool.executor = browser_executor
