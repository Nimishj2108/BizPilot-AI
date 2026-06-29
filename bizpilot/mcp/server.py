import sys
import os
import json
import csv
import uuid
from typing import Dict, Any, List

# Load tasks database helper
TASKS_FILE = "tasks_db.json"

def read_tasks_db() -> List[Dict[str, Any]]:
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def write_tasks_db(tasks: List[Dict[str, Any]]) -> None:
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)

# Tool Implementation Functions
def fetch_sales_data(file_path: str) -> Dict[str, Any]:
    """Reads sales data from a CSV file."""
    if not os.path.exists(file_path):
        return {"error": f"Sales file not found at: {file_path}"}
    
    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return {"data": rows}

def fetch_customer_feedback(file_path: str) -> Dict[str, Any]:
    """Reads customer feedback data from a CSV file."""
    if not os.path.exists(file_path):
        return {"error": f"Feedback file not found at: {file_path}"}
    
    rows = []
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return {"data": rows}

def fetch_product_metrics(file_path: str) -> Dict[str, Any]:
    """Reads product notes and metrics from a TXT file."""
    if not os.path.exists(file_path):
        return {"error": f"Product notes file not found at: {file_path}"}
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"content": content}

def generate_report(analysis_data: Dict[str, Any], format_type: str = "markdown") -> Dict[str, Any]:
    """Generates structured analysis reports."""
    # We will build a beautiful report based on the provided data dict
    kpis = analysis_data.get("kpis", {})
    trends = analysis_data.get("trends", {})
    feedback = analysis_data.get("feedback_summary", {})
    anomalies = analysis_data.get("anomalies", [])
    recs = analysis_data.get("recommendations", [])
    
    report_lines = []
    report_lines.append("# BizPilot AI - Startup Operations Analysis & Exec Report")
    report_lines.append("")
    report_lines.append("## Executive KPI Summary")
    report_lines.append(f"- **Total Revenue**: ${kpis.get('total_revenue', 0.0):,.2f}")
    report_lines.append(f"- **Successful Revenue**: ${kpis.get('successful_revenue', 0.0):,.2f}")
    report_lines.append(f"- **Total Sales Attempts**: {kpis.get('total_transactions', 0)}")
    report_lines.append(f"- **Average Order Value (AOV)**: ${kpis.get('average_order_value', 0.0):,.2f}")
    report_lines.append(f"- **Customer Satisfaction**: {feedback.get('satisfaction_score_pct', 0.0)}%")
    report_lines.append("")
    
    report_lines.append("## Performance & Sales Trends")
    report_lines.append(f"- **Sales Trend Direction**: {trends.get('trend', 'Stable')}")
    report_lines.append(f"- **Half-over-Half sales growth**: {trends.get('pct_change_half_over_half', 0.0)}%")
    report_lines.append("")
    
    report_lines.append("## Customer Sentiment & Topic Analysis")
    sent = feedback.get("sentiment_summary", {})
    report_lines.append(f"- **Positive comments**: {sent.get('Positive', 0)}")
    report_lines.append(f"- **Neutral comments**: {sent.get('Neutral', 0)}")
    report_lines.append(f"- **Negative comments (Complaints)**: {sent.get('Negative', 0)}")
    report_lines.append("")
    report_lines.append("### Sentiment Topics breakdown:")
    for topic, count in feedback.get("topic_summary", {}).items():
         report_lines.append(f"- **{topic}**: {count} mentions")
    report_lines.append("")
    
    if anomalies:
        report_lines.append("## Anomalies & System Alerts")
        for anomaly in anomalies:
            report_lines.append(f"- **{anomaly.get('type')}**: {anomaly.get('description')} (Order ID: {anomaly.get('order_id')})")
        report_lines.append("")
        
    report_lines.append("## Prioritized Strategic Recommendations")
    for i, rec in enumerate(recs, 1):
        report_lines.append(f"{i}. **{rec.get('action')}** (Priority: **{rec.get('priority')}**)")
        report_lines.append(f"   - *Why*: {rec.get('reason')}")
        report_lines.append(f"   - *Impact*: {rec.get('impact')} | *Effort*: {rec.get('effort')} | *Owner*: {rec.get('category')}")
    report_lines.append("")
    
    report_lines.append("## Action Execution Plan (Generated Tasks)")
    tasks = analysis_data.get("tasks", [])
    if tasks:
        for task in tasks:
            report_lines.append(f"- [ ] **{task.get('title')}** [Priority: {task.get('priority')}] - Assignee: {task.get('assignee')}")
    else:
        report_lines.append("No active tasks generated.")
        
    report_text = "\n".join(report_lines)
    return {"report": report_text}

def export_summary(report_text: str, output_path: str) -> Dict[str, Any]:
    """Exports report summary to file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        return {"success": True, "message": f"Successfully exported report to '{output_path}'"}
    except Exception as e:
        return {"error": f"Failed to write file: {str(e)}"}

def create_task(title: str, priority: str = "Medium", assignee: str = "Engineering") -> Dict[str, Any]:
    """Creates a new operational task in the persistent DB."""
    tasks = read_tasks_db()
    task_id = str(uuid.uuid4())[:8]
    new_task = {
        "id": task_id,
        "title": title,
        "priority": priority,
        "assignee": assignee,
        "status": "Todo"
    }
    tasks.append(new_task)
    write_tasks_db(tasks)
    return {"task": new_task}

def update_task_status(task_id: str, status: str) -> Dict[str, Any]:
    """Updates status of a task by ID."""
    tasks = read_tasks_db()
    found = False
    for task in tasks:
        if task["id"] == task_id:
            task["status"] = status
            found = True
            break
            
    if found:
        write_tasks_db(tasks)
        return {"success": True, "message": f"Task {task_id} updated to status '{status}'"}
    return {"error": f"Task with ID {task_id} not found."}


# List of tools to return to MCP clients
MCP_TOOLS = [
    {
        "name": "fetch_sales_data",
        "description": "Load and parse a sales transaction CSV dataset.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Local path to the sales CSV file."}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "fetch_customer_feedback",
        "description": "Load and parse customer comments from a CSV dataset.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Local path to the customer feedback CSV file."}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "fetch_product_metrics",
        "description": "Read product notes and performance metrics from text files.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Local path to the product notes TXT file."}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "generate_report",
        "description": "Compile analytical findings into a structured markdown report.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "analysis_data": {"type": "object", "description": "Aggregated dictionary containing KPIs, trends, and feedback analysis."}
            },
            "required": ["analysis_data"]
        }
    },
    {
        "name": "export_summary",
        "description": "Save generated markdown summaries to disk.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "report_text": {"type": "string", "description": "Raw markdown text of the report."},
                "output_path": {"type": "string", "description": "Output file path."}
            },
            "required": ["report_text", "output_path"]
        }
    },
    {
        "name": "create_task",
        "description": "Create an operational execution task in the task database.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task summary description."},
                "priority": {"type": "string", "description": "High, Medium, or Low priority.", "default": "Medium"},
                "assignee": {"type": "string", "description": "Assigned team (e.g. Engineering, support, etc.)", "default": "Engineering"}
            },
            "required": ["title"]
        }
    },
    {
        "name": "update_task_status",
        "description": "Update execution status of an active task.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Unique identifier of the task."},
                "status": {"type": "string", "description": "Todo, In Progress, or Done."}
            },
            "required": ["task_id", "status"]
        }
    }
]

def handle_rpc_request(request: Dict[str, Any]) -> Dict[str, Any]:
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})
    
    # Standard MCP/JSON-RPC response skeleton
    response = {
        "jsonrpc": "2.0",
        "id": req_id
    }
    
    try:
        if method == "tools/list":
            response["result"] = {"tools": MCP_TOOLS}
            
        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            
            # Dispatch
            if tool_name == "fetch_sales_data":
                res = fetch_sales_data(args.get("file_path"))
            elif tool_name == "fetch_customer_feedback":
                res = fetch_customer_feedback(args.get("file_path"))
            elif tool_name == "fetch_product_metrics":
                res = fetch_product_metrics(args.get("file_path"))
            elif tool_name == "generate_report":
                res = generate_report(args.get("analysis_data"))
            elif tool_name == "export_summary":
                res = export_summary(args.get("report_text"), args.get("output_path"))
            elif tool_name == "create_task":
                res = create_task(args.get("title"), args.get("priority", "Medium"), args.get("assignee", "Engineering"))
            elif tool_name == "update_task_status":
                res = update_task_status(args.get("task_id"), args.get("status"))
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
            response["result"] = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(res)
                    }
                ]
            }
        else:
            response["error"] = {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
    except Exception as e:
        response["error"] = {
            "code": -32603,
            "message": f"Internal execution error: {str(e)}"
        }
        
    return response

def start_server():
    """Main execution loop for stdio MCP Server."""
    sys.stderr.write("BizPilot MCP Server running on stdio...\n")
    sys.stderr.flush()
    
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            if not line.strip():
                continue
                
            request = json.loads(line)
            response = handle_rpc_request(request)
            
            # Print response JSON strictly on a single line to stdout
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except KeyboardInterrupt:
            break
        except Exception as e:
            sys.stderr.write(f"Server loop error: {str(e)}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    start_server()
