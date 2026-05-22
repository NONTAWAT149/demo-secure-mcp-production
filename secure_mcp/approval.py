"""Human approval simulation for high-risk MCP actions."""

from secure_mcp.dlp import scan_for_sensitive_data


def requires_human_approval(tool_name: str, args: dict) -> bool:
    """Return whether the tool request should go to human review."""
    if tool_name in {"delete_records", "export_customer_data"}:
        return True

    if tool_name == "send_email":
        body = str((args or {}).get("body", ""))
        return scan_for_sensitive_data(body)["contains_sensitive_data"]

    return False


def simulate_human_approval(tool_name: str, args: dict) -> dict:
    """Deny dangerous actions for the demo."""
    if requires_human_approval(tool_name, args):
        return {
            "approved": False,
            "approver": "security_reviewer",
            "reason": "Human reviewer denied high-risk action.",
        }

    return {
        "approved": True,
        "approver": "security_reviewer",
        "reason": "Human reviewer approved low-risk action.",
    }
