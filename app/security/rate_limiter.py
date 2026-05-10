from datetime import datetime, timedelta
from typing import Dict

# Dictionary to store request counts: { "ip_address": {"count": 1, "blocked_until": None} }
_rate_limit_store: Dict[str, Dict] = {}

MAX_REQUESTS = 5
BLOCK_DURATION_HOURS = 1

def is_ip_blocked(ip_address: str) -> bool:
    """
    Checks if an IP is currently blocked.
    """
    record = _rate_limit_store.get(ip_address)
    if not record:
        return False
    
    if record.get("blocked_until"):
        if datetime.now() < record["blocked_until"]:
            return True
        else:
            # Block expired, reset
            _rate_limit_store[ip_address] = {"count": 0, "blocked_until": None}
            return False
    return False

def record_request(ip_address: str) -> bool:
    """
    Records a request for an IP. 
    Returns True if the request should be blocked, False otherwise.
    
    Note: If migrating to Redis, replace this in-memory dictionary with
    Redis INCR and EXPIRE commands.
    """
    if is_ip_blocked(ip_address):
        return True

    record = _rate_limit_store.get(ip_address, {"count": 0, "blocked_until": None})
    record["count"] += 1

    if record["count"] >= MAX_REQUESTS:
        record["blocked_until"] = datetime.now() + timedelta(hours=BLOCK_DURATION_HOURS)
        _rate_limit_store[ip_address] = record
        return True # Just blocked

    _rate_limit_store[ip_address] = record
    return False

def get_blocked_ips():
    """Helper to return currently blocked IPs (mostly for monitoring/debugging)"""
    return [ip for ip, data in _rate_limit_store.items() if data.get("blocked_until") and datetime.now() < data["blocked_until"]]
