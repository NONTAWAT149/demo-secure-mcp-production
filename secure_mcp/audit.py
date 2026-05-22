"""In-memory audit logging for the secure MCP demo."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

_AUDIT_LOG: List[Dict] = []

_SENSITIVE_MARKERS = (
    "confidential",
    "customer data",
    "internal strategy",
    "acquisition",
    "budget",
    "@",
)


def _mask_value(value) -> str:
    if isinstance(value, str):
        lowered = value.lower()
        if any(marker in lowered for marker in _SENSITIVE_MARKERS) or len(value) > 80:
            return "[REDACTED]"
        return value
    return str(value)


def _summarize_args(args: Optional[Dict]) -> str:
    if not args:
        return "{}"

    masked = {key: _mask_value(value) for key, value in args.items()}
    return str(masked)


def log_event(
    event_type,
    tool_name,
    decision,
    reason,
    risk_level,
    args=None,
):
    """Append a masked audit event."""
    _AUDIT_LOG.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "event_type": event_type,
            "tool_name": tool_name,
            "decision": decision,
            "reason": reason,
            "risk_level": risk_level,
            "args_summary": _summarize_args(args),
        }
    )


def get_audit_log():
    """Return a copy of the in-memory audit log."""
    return list(_AUDIT_LOG)


def clear_audit_log():
    """Reset the in-memory audit log."""
    _AUDIT_LOG.clear()
