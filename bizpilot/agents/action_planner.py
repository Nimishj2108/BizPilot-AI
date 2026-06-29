from typing import Any
from bizpilot.agents.base import BaseAgent
from bizpilot.utils.context import SharedContext
from bizpilot.skills.decision import DecisionSupportSkill
from bizpilot.skills.summary import ExecutiveSummarySkill

class ActionPlannerAgent(BaseAgent):
    """
    Sub-agent focused on decision support and task scheduling based on insights.
    """
    def __init__(self, mcp_client: Any = None):
        super().__init__("Action Planner Agent", mcp_client)
        self.skills = ["Decision Support Skill", "Executive Summary Skill"]

    def run(self, context: SharedContext) -> None:
        self.log(context, "Initiating strategic action plan formulation...")
        
        # 1. Retrieve prior analyses from context
        da_out = context.data_analyst_output
        ci_out = context.customer_intelligence_output
        
        kpis = da_out.get("kpis", {})
        trends = da_out.get("trends", {})
        anomalies = da_out.get("anomalies", [])
        feedback = ci_out.get("feedback_summary", {})
        
        # 2. Identify risks and opportunities using ExecutiveSummarySkill
        risks_opps = ExecutiveSummarySkill.identify_risks_and_opportunities(kpis, feedback, anomalies)
        risks = risks_opps["risks"]
        opportunities = risks_opps["opportunities"]
        
        self.log(context, f"Identified risks: {risks}")
        self.log(context, f"Identified opportunities: {opportunities}")
        
        # 3. Formulate recommendations using DecisionSupportSkill
        recommendations = DecisionSupportSkill.evaluate_and_recommend(risks, opportunities)
        self.log(context, f"Formulated {len(recommendations)} strategic recommendations.")
        
        # 4. Generate persistent tasks for each recommendation via Task Management MCP Tool
        tasks_generated = []
        for rec in recommendations:
            title = f"{rec['action']}: {rec['reason']}"
            priority = rec["priority"]
            assignee = rec["category"]
            
            self.log(context, f"Requesting MCP task creation: '{rec['action']}'")
            res = self.mcp_client.call_tool("create_task", {
                "title": title,
                "priority": priority,
                "assignee": assignee
            })
            
            if "error" in res:
                self.log(context, f"Failed to create task via MCP: {res['error']}")
                context.add_error(res["error"])
            else:
                task = res.get("task", {})
                tasks_generated.append(task)
                self.log(context, f"Successfully created MCP Task ID: {task.get('id')}")
                
        # 5. Populate action planner results in context
        context.action_planner_output = {
            "risks": risks,
            "opportunities": opportunities,
            "recommendations": recommendations,
            "tasks": tasks_generated
        }
        context.tasks.extend(tasks_generated)
        
        self.log(context, "Action planner completed.")
