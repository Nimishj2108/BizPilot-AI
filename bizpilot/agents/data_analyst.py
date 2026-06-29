from typing import Any
from bizpilot.agents.base import BaseAgent
from bizpilot.utils.context import SharedContext
from bizpilot.skills.analytics import BusinessAnalyticsSkill
from bizpilot.security.guardian import SecurityGuardian

class DataAnalystAgent(BaseAgent):
    """
    Sub-agent focused on quantitative business statistics, metrics and anomaly tracking.
    """
    def __init__(self, mcp_client: Any = None):
        super().__init__("Data Analyst Agent", mcp_client)
        self.skills = ["Business Analytics Skill"]

    def run(self, context: SharedContext) -> None:
        self.log(context, "Initiating sales and metrics data analysis...")
        
        sales_file = None
        product_file = None
        
        # Find files in shared context
        for file_path in context.input_files.keys():
            if "sales" in file_path.lower():
                sales_file = file_path
            elif "product" in file_path.lower() or "note" in file_path.lower():
                product_file = file_path
                
        # 1. Fetch sales data via MCP tool
        sales_records = []
        if sales_file:
            self.log(context, f"Requesting sales data from MCP for path: {sales_file}")
            res = self.mcp_client.call_tool("fetch_sales_data", {"file_path": sales_file})
            if "error" in res:
                self.log(context, f"Error fetching sales data: {res['error']}")
                context.add_error(res["error"])
            else:
                sales_records = res.get("data", [])
                self.log(context, f"Successfully loaded {len(sales_records)} sales records.")
        else:
            self.log(context, "No sales CSV file path provided.")
            
        # 2. Fetch product metrics/notes via MCP tool
        product_notes = ""
        if product_file:
            self.log(context, f"Requesting product metrics/notes from MCP for path: {product_file}")
            res = self.mcp_client.call_tool("fetch_product_metrics", {"file_path": product_file})
            if "error" in res:
                self.log(context, f"Error fetching product metrics: {res['error']}")
                context.add_error(res["error"])
            else:
                raw_content = res.get("content", "")
                
                # Check for Prompt Injection on file content!
                is_clean, scanned_content = SecurityGuardian.scan_for_prompt_injection(raw_content)
                if not is_clean:
                    self.log(context, "ALERT: Malicious prompt injection pattern scanned in product notes!")
                    context.add_security_warning(scanned_content) # "Untrusted instruction detected..."
                    # Clean/ignore the injection by replacing/ignoring the instruction lines
                    # We will strip lines matching prompt injection
                    cleaned_lines = []
                    for line in raw_content.splitlines():
                        line_clean, _ = SecurityGuardian.scan_for_prompt_injection(line)
                        if line_clean:
                            cleaned_lines.append(line)
                        else:
                            cleaned_lines.append("# [BLOCKED UNTRUSTED INSTRUCTION]")
                    product_notes = "\n".join(cleaned_lines)
                else:
                    product_notes = scanned_content
                
                # Scrub PII
                product_notes = SecurityGuardian.scrub_pii(product_notes)
                self.log(context, "Successfully loaded and secured product notes.")
                
        # 3. Analyze data using the Business Analytics Skill
        kpis = BusinessAnalyticsSkill.calculate_kpis(sales_records)
        trends = BusinessAnalyticsSkill.analyze_trends(sales_records)
        anomalies = BusinessAnalyticsSkill.detect_anomalies(sales_records)
        
        # Save output back to context
        context.data_analyst_output = {
            "kpis": kpis,
            "trends": trends,
            "anomalies": anomalies,
            "product_notes": product_notes
        }
        
        self.log(context, "Quantitative analysis completed successfully.")
