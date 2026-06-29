import re
import logging
from typing import Tuple

logger = logging.getLogger("BizPilotSecurity")

class SecurityGuardian:
    """
    Guards against prompt injection and scrubs sensitive PII for data privacy.
    """
    
    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(?:previous|all|above|below)\s+instructions",
        r"(?i)system\s+override",
        r"(?i)delete\s+all\s+(?:data|files|tasks)",
        r"(?i)you\s+must\s+now\s+act\s+as",
        r"(?i)new\s+system\s+prompt",
        r"(?i)reset\s+agent\s+behavior",
        r"(?i)override\s+system\s+rules"
    ]
    
    # PII scrubber patterns
    EMAIL_PATTERN = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    PHONE_PATTERN = r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}"

    @staticmethod
    def scan_for_prompt_injection(content: str) -> Tuple[bool, str]:
        """
        Scans content (e.g. from uploaded files) for prompt injection attempts.
        Returns (is_clean, cleaned_or_message).
        """
        for pattern in SecurityGuardian.INJECTION_PATTERNS:
            if re.search(pattern, content):
                logger.warning("PROMPT INJECTION BLOCKED - Found matching pattern in content.")
                # Return detection response
                return False, "Untrusted instruction detected. Continuing analysis safely."
        return True, content

    @staticmethod
    def scrub_pii(text: str) -> str:
        """
        Scrubs email addresses and phone numbers to ensure data privacy.
        """
        # Scrub emails
        scrubbed = re.sub(SecurityGuardian.EMAIL_PATTERN, "[REDACTED EMAIL]", text)
        # Scrub phone numbers (only if they fit common formats, avoid scrubbing metrics)
        # To avoid scrubbing sales quantities, we'll only scrub phone numbers if they have 7+ digits and formatting
        def phone_replacer(match):
            val = match.group(0)
            # Count digits
            digits = sum(c.isdigit() for c in val)
            if digits >= 7:
                return "[REDACTED PHONE]"
            return val
            
        scrubbed = re.sub(SecurityGuardian.PHONE_PATTERN, phone_replacer, scrubbed)
        return scrubbed
