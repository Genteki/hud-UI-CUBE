"""Computer tools registration - kept for compatibility."""
from typing import Any
from tools.browser import set_global_executor

# Keep this function for compatibility with hud-remote-browser pattern
def register_computer_tools(env: Any, browser_executor: Any) -> None:
    """Register computer tools with the environment.
    
    Note: Tools are already registered on the router at module level.
    This function just sets the executor.
    """
    set_global_executor(browser_executor)
