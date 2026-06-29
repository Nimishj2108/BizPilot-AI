import os
from typing import List, Dict, Any
from bizpilot.utils.context import SharedContext
from bizpilot.mcp.client import MCPClient
from bizpilot.agents.data_analyst import DataAnalystAgent
from bizpilot.agents.customer_intelligence import CustomerIntelligenceAgent
from bizpilot.agents.action_planner import ActionPlannerAgent
from bizpilot.agents.report_generator import ReportGeneratorAgent
from bizpilot.security.validator import SecurityValidator

class BizPilotOrchestrator:
    """
    Main Orchestrator Agent.
    Coordinates initialization, validations, routing, sub-agent execution,
    and final report compilation.
    """
    def __init__(self):
        self.mcp_client = MCPClient()

    def run_pipeline(self, user_query: str, file_paths: List[str]) -> SharedContext:
        """
        Executes the multi-agent pipeline:
        1. Validates inputs & file paths.
        2. Starts MCP connection.
        3. Invokes Sub-agents in sequence (delegation).
        4. Cleans up MCP client.
        """
        context = SharedContext(user_query=user_query)
        context.add_history("Orchestrator", f"Starting business operations analysis pipeline for query: '{user_query}'")

        # Step 1: Input & Path Validations
        valid_paths = []
        for path in file_paths:
            # Check path injection or format
            is_valid, msg = SecurityValidator.validate_file_path(path)
            if not is_valid:
                context.add_error(msg)
                context.add_history("Orchestrator", f"Aborting pipeline. Input validation failed: {msg}")
                return context
            
            valid_paths.append(path)
            # Store validated files in context
            context.input_files[path] = "Validated and ready."
            
        # Step 2: Establish MCP Connection
        context.add_history("Orchestrator", "Connecting to MCP Server stdio process...")
        try:
            self.mcp_client.connect()
        except Exception as e:
            msg = f"Failed to spawn MCP Server stdio connection: {str(e)}"
            context.add_error(msg)
            context.add_history("Orchestrator", f"Aborting pipeline: {msg}")
            return context

        # Step 3: Multi-agent execution delegation
        try:
            # 1. Customer Intelligence Agent
            ci_agent = CustomerIntelligenceAgent(self.mcp_client)
            ci_agent.run(context)
            
            # Check for critical errors
            if context.errors:
                context.add_history("Orchestrator", "Halting pipeline due to errors in Customer Intelligence execution.")
                return context

            # 2. Data Analyst Agent
            da_agent = DataAnalystAgent(self.mcp_client)
            da_agent.run(context)
            
            if context.errors:
                context.add_history("Orchestrator", "Halting pipeline due to errors in Data Analyst execution.")
                return context

            # 3. Action Planner Agent
            ap_agent = ActionPlannerAgent(self.mcp_client)
            ap_agent.run(context)
            
            if context.errors:
                context.add_history("Orchestrator", "Halting pipeline due to errors in Action Planner execution.")
                return context

            # 4. Report Generator Agent
            rg_agent = ReportGeneratorAgent(self.mcp_client)
            rg_agent.run(context)

        except Exception as e:
            msg = f"Unexpected pipeline execution crash: {str(e)}"
            context.add_error(msg)
            context.add_history("Orchestrator", msg)
        finally:
            # Step 4: Disconnect MCP connection safely
            context.add_history("Orchestrator", "Closing MCP client subprocess streams...")
            self.mcp_client.close()

        context.add_history("Orchestrator", "Multi-agent pipeline completed successfully.")
        return context
