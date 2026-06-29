from typing import List, Any
from bizpilot.utils.context import SharedContext

class BaseAgent:
    """
    Base class for all BizPilot specialized agents.
    Provides common references to MCP client and shared context.
    """
    def __init__(self, name: str, mcp_client: Any = None):
        self.name: str = name
        self.mcp_client: Any = mcp_client
        self.skills: List[str] = []

    def log(self, context: SharedContext, message: str) -> None:
        """Helper to log agent activity to context history."""
        context.add_history(self.name, message)

    def run(self, context: SharedContext) -> None:
        """
        Execute the agent's specific responsibilities.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement the run method.")
