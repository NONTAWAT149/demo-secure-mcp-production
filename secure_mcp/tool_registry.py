"""Trusted tool registry used by the secure MCP governance layer."""

TRUSTED_TOOLS = {
    "read_internal_docs": {"risk": "medium", "trusted": True},
    "send_email": {"risk": "high", "trusted": True},
    "delete_records": {"risk": "critical", "trusted": True},
    "export_customer_data": {"risk": "critical", "trusted": True},
}


def validate_tool(tool_name: str) -> dict:
    """Validate that the requested tool is known and trusted."""
    tool_meta = TRUSTED_TOOLS.get(tool_name)
    if tool_meta is None:
        return {
            "allowed": False,
            "trusted": False,
            "risk_level": "critical",
            "reason": f"Unknown or untrusted tool: {tool_name}",
        }

    return {
        "allowed": True,
        "trusted": tool_meta["trusted"],
        "risk_level": tool_meta["risk"],
        "reason": f"Tool {tool_name} found in trusted registry.",
    }
