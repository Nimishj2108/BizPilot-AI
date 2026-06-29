import os
import re
import logging
from typing import Dict, Any, List, Tuple

# Set up security logger
logger = logging.getLogger("BizPilotSecurity")
logger.setLevel(logging.INFO)
# Clear existing handlers to avoid duplicates
if logger.handlers:
    logger.handlers.clear()
handler = logging.FileHandler("bizpilot_security.log", mode="a", encoding="utf-8")
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class SecurityValidator:
    """
    Handles file path validation, malicious command detection, and safe tool parameter check.
    """
    
    ALLOWED_EXTENSIONS = {".csv", ".json", ".txt", ".md"}
    
    @staticmethod
    def validate_file_path(file_path: str, base_dir: str = ".") -> Tuple[bool, str]:
        """
        Validates if file path is safe:
        1. Checks for path traversal (..)
        2. Verifies allowed extensions (.csv, .json, .txt)
        3. Checks if the file is within base_dir or absolute paths are handled safely.
        """
        try:
            # 1. Traversal check
            norm_path = os.path.normpath(file_path)
            if ".." in norm_path or norm_path.startswith("/") or norm_path.startswith("\\"):
                # If they attempt path traversal or absolute roots, block it (unless it's in the workspace)
                msg = f"Path traversal or absolute path violation detected: '{file_path}'"
                logger.warning(msg)
                return False, msg
            
            # 2. Extension check
            _, ext = os.path.splitext(norm_path.lower())
            if ext not in SecurityValidator.ALLOWED_EXTENSIONS:
                msg = f"Invalid file format: '{ext}'. Please upload CSV, JSON, or TXT."
                logger.warning(msg)
                return False, msg
            
            # 3. Exists check
            if not os.path.exists(file_path):
                msg = f"File not found: '{file_path}'"
                logger.warning(msg)
                return False, msg
                
            return True, "Path is safe and exists."
        except Exception as e:
            msg = f"Error validating path: {str(e)}"
            logger.error(msg)
            return False, msg

    @staticmethod
    def validate_cli_input(cli_string: str) -> Tuple[bool, str]:
        """
        Scans CLI text input for potential command injection patterns.
        """
        # Block command injection meta-characters if the string is used in cmd contexts
        injection_chars = [";", "&", "|", "`", "$", ">", "<", "\n"]
        for char in injection_chars:
            if char in cli_string:
                msg = f"Potentially unsafe characters detected in input string."
                logger.warning(f"Unsafe characters in input: '{cli_string}'")
                return False, msg
        return True, "Input string is safe."

    @staticmethod
    def authorize_tool_execution(tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates parameters before executing MCP tools, checks bounds and logs usage.
        """
        logger.info(f"AUTHORIZATION REQUEST - Tool: {tool_name}, Arguments: {arguments}")
        
        # Specific tool checks
        if tool_name in ["fetch_sales_data", "fetch_customer_feedback", "fetch_product_metrics"]:
            file_path = arguments.get("file_path", "")
            is_valid, reason = SecurityValidator.validate_file_path(file_path)
            if not is_valid:
                logger.warning(f"BLOCKED - Tool: {tool_name}. Reason: {reason}")
                return False, f"Unauthorized file access: {reason}"
                
        elif tool_name == "export_summary":
            output_path = arguments.get("output_path", "")
            # Ensure it outputs locally to safe formats, check for traversal
            is_valid, reason = SecurityValidator.validate_file_path(output_path)
            # Allow creating new file, so path validation is done, but don't strictly require exists for output
            norm_path = os.path.normpath(output_path)
            if ".." in norm_path or norm_path.startswith("/") or norm_path.startswith("\\"):
                logger.warning(f"BLOCKED - Tool: {tool_name}. Reason: Path traversal")
                return False, "Unauthorized file path: Path traversal detected."
            _, ext = os.path.splitext(norm_path.lower())
            if ext not in SecurityValidator.ALLOWED_EXTENSIONS:
                logger.warning(f"BLOCKED - Tool: {tool_name}. Reason: Invalid extension {ext}")
                return False, f"Invalid output file format {ext}."

        elif tool_name == "create_task":
            title = arguments.get("title", "")
            is_valid, reason = SecurityValidator.validate_cli_input(title)
            if not is_valid:
                logger.warning(f"BLOCKED - Tool: {tool_name}. Reason: {reason}")
                return False, f"Unauthorized parameters: {reason}"
                
        logger.info(f"APPROVED - Tool: {tool_name}")
        return True, "Approved."
