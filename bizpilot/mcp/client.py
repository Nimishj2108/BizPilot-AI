import os
import sys
import json
import subprocess
from typing import Dict, Any
from bizpilot.security.validator import SecurityValidator

class MCPClient:
    """
    Client interface that runs and interacts with the stdio BizPilot MCP Server.
    Integrates parameters authorization before executing any tool.
    """
    def __init__(self):
        self.process = None

    def connect(self) -> None:
        """Spawns the MCP server subprocess."""
        # Set PYTHONPATH to make sure the server can import the bizpilot modules
        env = os.environ.copy()
        workspace_dir = os.path.abspath(".")
        
        # Append workspace to PYTHONPATH
        if "PYTHONPATH" in env:
            env["PYTHONPATH"] = workspace_dir + os.pathsep + env["PYTHONPATH"]
        else:
            env["PYTHONPATH"] = workspace_dir
            
        self.process = subprocess.Popen(
            [sys.executable, "-m", "bizpilot.mcp.server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
            cwd=workspace_dir
        )

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs validation and calls an MCP server tool.
        """
        # 1. Authorize tool execution first
        is_authorized, reason = SecurityValidator.authorize_tool_execution(name, arguments)
        if not is_authorized:
            return {"error": f"Security Blocked: {reason}"}
            
        # 2. Spawn process if not active
        if not self.process or self.process.poll() is not None:
            self.connect()

        # 3. Create JSON-RPC message
        req = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            },
            "id": 1
        }
        
        try:
            # Send message
            self.process.stdin.write(json.dumps(req) + "\n")
            self.process.stdin.flush()
            
            # Read single line response
            line = self.process.stdout.readline()
            if not line:
                return {"error": "MCP Server disconnected unexpectedly."}
                
            response = json.loads(line)
            
            if "error" in response:
                return {"error": response["error"]["message"]}
                
            result = response.get("result", {})
            content = result.get("content", [])
            if content and content[0].get("type") == "text":
                return json.loads(content[0]["text"])
                
            return {"error": "Unexpected tool execution output format."}
            
        except Exception as e:
            return {"error": f"Failed to execute MCP tool: {str(e)}"}

    def list_tools(self) -> Dict[str, Any]:
        """Queries the server for list of supported tools."""
        if not self.process or self.process.poll() is not None:
            self.connect()
            
        req = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 0
        }
        
        try:
            self.process.stdin.write(json.dumps(req) + "\n")
            self.process.stdin.flush()
            line = self.process.stdout.readline()
            return json.loads(line)
        except Exception as e:
            return {"error": f"Failed to query tools: {str(e)}"}

    def close(self) -> None:
        """Gracefully shuts down the server process."""
        if self.process:
            try:
                self.process.stdin.close()
            except:
                pass
            self.process.terminate()
            self.process.wait()
            self.process = None
