import json
from typing import Dict, Any, List, Optional

class SharedContext:
    """
    Manages the shared memory and context passed between BizPilot sub-agents.
    """
    def __init__(self, user_query: str = ""):
        self.user_query: str = user_query
        self.input_files: Dict[str, str] = {}  # file_path -> file_content or metadata
        self.parsed_data: Dict[str, Any] = {}  # file_type/name -> structured data (list of dicts, etc.)
        
        # Sub-agent outputs
        self.data_analyst_output: Dict[str, Any] = {}
        self.customer_intelligence_output: Dict[str, Any] = {}
        self.action_planner_output: Dict[str, Any] = {}
        self.report_generator_output: Dict[str, Any] = {}
        
        # General state
        self.tasks: List[Dict[str, Any]] = []
        self.history: List[str] = []
        self.security_warnings: List[str] = []
        self.errors: List[str] = []
        
    def add_history(self, sender: str, message: str) -> None:
        """Log agent activities and thoughts."""
        self.history.append(f"[{sender}] {message}")

    def add_security_warning(self, message: str) -> None:
        """Track security incidents (like blocked injection patterns)."""
        self.security_warnings.append(message)

    def add_error(self, message: str) -> None:
        """Log errors during execution."""
        self.errors.append(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for serialisation."""
        return {
            "user_query": self.user_query,
            "input_files": list(self.input_files.keys()),
            "data_analyst_output": self.data_analyst_output,
            "customer_intelligence_output": self.customer_intelligence_output,
            "action_planner_output": self.action_planner_output,
            "report_generator_output": self.report_generator_output,
            "tasks": self.tasks,
            "history": self.history,
            "security_warnings": self.security_warnings,
            "errors": self.errors
        }

    def __str__(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
