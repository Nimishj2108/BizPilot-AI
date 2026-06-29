from typing import Any
from bizpilot.agents.base import BaseAgent
from bizpilot.utils.context import SharedContext
from bizpilot.skills.feedback import CustomerFeedbackSkill
from bizpilot.security.guardian import SecurityGuardian

class CustomerIntelligenceAgent(BaseAgent):
    """
    Sub-agent focused on qualitative customer sentiment, complaints, and feature requests.
    """
    def __init__(self, mcp_client: Any = None):
        super().__init__("Customer Intelligence Agent", mcp_client)
        self.skills = ["Customer Feedback Skill"]

    def run(self, context: SharedContext) -> None:
        self.log(context, "Initiating customer sentiment analysis...")
        
        feedback_file = None
        
        # Find feedback file
        for file_path in context.input_files.keys():
            if "feedback" in file_path.lower() or "comment" in file_path.lower():
                feedback_file = file_path
                
        # 1. Fetch customer feedback via MCP tool
        feedback_records = []
        if feedback_file:
            self.log(context, f"Requesting customer feedback from MCP for path: {feedback_file}")
            res = self.mcp_client.call_tool("fetch_customer_feedback", {"file_path": feedback_file})
            if "error" in res:
                self.log(context, f"Error fetching customer feedback: {res['error']}")
                context.add_error(res["error"])
            else:
                raw_records = res.get("data", [])
                
                # Verify injection and scrub PII on records
                secured_records = []
                for row in raw_records:
                    text_key = None
                    for k in ["Feedback", "Comment", "Text"]:
                        if k in row:
                            text_key = k
                            break
                            
                    if text_key:
                        content = row[text_key]
                        # Scan prompt injection
                        is_clean, scanned = SecurityGuardian.scan_for_prompt_injection(content)
                        if not is_clean:
                            self.log(context, "ALERT: Malicious prompt injection scanned in customer feedback comments!")
                            context.add_security_warning(scanned) # "Untrusted instruction detected..."
                            # Ignore injection and set placeholder
                            secured_content = "[UNTRUSTED INSTRUCTION BLOCK]"
                        else:
                            secured_content = SecurityGuardian.scrub_pii(scanned)
                            
                        secured_row = row.copy()
                        secured_row[text_key] = secured_content
                        secured_records.append(secured_row)
                    else:
                        secured_records.append(row)
                        
                feedback_records = secured_records
                self.log(context, f"Successfully loaded and secured {len(feedback_records)} feedback records.")
        else:
            self.log(context, "No feedback CSV file path provided.")
            
        # 2. Analyze sentiment and topics using CustomerFeedbackSkill
        feedback_summary = CustomerFeedbackSkill.analyze_feedback_batch(feedback_records)
        
        # Save output back to context
        context.customer_intelligence_output = {
            "feedback_summary": feedback_summary
        }
        
        self.log(context, "Customer feedback sentiment analysis completed.")
