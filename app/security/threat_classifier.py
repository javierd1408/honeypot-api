import re

# Common Threat Signatures
SQLI_PATTERN = re.compile(r"(?i)(union\s+select|select\s+.*\s+from|insert\s+into|update\s+.*\s+set|delete\s+from|drop\s+table|'[\s]*OR[\s]*'?[0-9]?'?[\s]*=|--|#)")
PATH_TRAVERSAL_PATTERN = re.compile(r"(?i)(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/|\.\.%2f|%2e%2e%5c|/etc/passwd|/windows/win.ini)")
BOT_SCAN_PATHS = [".env", "wp-admin", "config.php", ".git", "admin", "setup.php"]

class ThreatType:
    SQL_INJECTION = "SQL_INJECTION_ATTEMPT"
    PATH_TRAVERSAL = "PATH_TRAVERSAL_ATTEMPT"
    BOT_SCAN = "BOT_SCAN"
    BRUTE_FORCE = "BRUTE_FORCE"
    UNKNOWN = "UNKNOWN"

def classify_threat(path: str, method: str, payload: str = None) -> str:
    """
    Analyzes the request data to classify the type of threat.
    """
    # 1. Check for Bot Scanning common paths
    for scan_path in BOT_SCAN_PATHS:
        if scan_path in path.lower():
            return ThreatType.BOT_SCAN

    # 2. Check for SQL Injection in payload or path
    target_string = f"{path} {payload}" if payload else path
    if SQLI_PATTERN.search(target_string):
        return ThreatType.SQL_INJECTION

    # 3. Check for Path Traversal
    if PATH_TRAVERSAL_PATTERN.search(target_string):
        return ThreatType.PATH_TRAVERSAL

    # 4. Check for Brute Force (Simple heuristic based on path and method)
    if method == "POST" and ("login" in path.lower() or "auth" in path.lower()):
        return ThreatType.BRUTE_FORCE

    return ThreatType.UNKNOWN
