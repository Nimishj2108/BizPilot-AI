from typing import Any
from bizpilot.agents.base import BaseAgent
from bizpilot.utils.context import SharedContext

class ReportGeneratorAgent(BaseAgent):
    """
    Sub-agent focused on synthesizing final executive markdown reports.
    """
    def __init__(self, mcp_client: Any = None):
        super().__init__("Report Generator Agent", mcp_client)
        self.skills = ["Executive Summary Skill"]

    def run(self, context: SharedContext) -> None:
        self.log(context, "Initiating final business report generation...")
        
        # 1. Gather all inputs from context
        da_out = context.data_analyst_output
        ci_out = context.customer_intelligence_output
        ap_out = context.action_planner_output
        
        analysis_data = {
            "kpis": da_out.get("kpis", {}),
            "trends": da_out.get("trends", {}),
            "anomalies": da_out.get("anomalies", []),
            "feedback_summary": ci_out.get("feedback_summary", {}),
            "recommendations": ap_out.get("recommendations", []),
            "tasks": ap_out.get("tasks", [])
        }
        
        # 2. Call MCP generate_report tool
        self.log(context, "Requesting report compilation from MCP...")
        res = self.mcp_client.call_tool("generate_report", {"analysis_data": analysis_data})
        
        if "error" in res:
            self.log(context, f"Error generating report: {res['error']}")
            context.add_error(res["error"])
            report_text = ""
        else:
            report_text = res.get("report", "")
            self.log(context, "Report text compiled successfully.")
            
        # 3. Export report summary to disk if output path is requested
        # For simplicity, we can export to a standard report file 'bizpilot_report.md'
        output_path = "bizpilot_report.md"
        self.log(context, f"Requesting report export to disk at path: {output_path}")
        export_res = self.mcp_client.call_tool("export_summary", {
            "report_text": report_text,
            "output_path": output_path
        })
        
        if "error" in export_res:
            self.log(context, f"Failed to export report: {export_res['error']}")
            context.add_error(export_res["error"])
        else:
            self.log(context, f"Successfully exported report to file.")
            
        # Save output in context
        context.report_generator_output = {
            "report_text": report_text,
            "exported_to": output_path
        }
        
        self.log(context, "Report generation process completed.")
