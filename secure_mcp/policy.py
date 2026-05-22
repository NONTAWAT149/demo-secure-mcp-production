"""Policy engine for the secure MCP governance layer."""

from typing import Dict, Optional

DEFAULT_USER_CONTEXT = {
    "user_id": "demo_user",
    "role": "analyst",
    "approved_tools": ["read_internal_docs", "send_email"],
}


def check_policy(
    tool_name: str,
    args: Dict,
    user_context: Optional[Dict] = None,
) -> Dict:
    """Apply a small set of deterministic security rules."""
    context = DEFAULT_USER_CONTEXT.copy()
    context.update(user_context or {})
    matched_rules = []
    tool_args = args or {}

    if tool_name not in {
        "read_internal_docs",
        "send_email",
        "delete_records",
        "export_customer_data",
    }:
        matched_rules.append("unknown_tool_block")
        return {
            "allowed": False,
            "reason": "Tool is not approved by policy.",
            "risk_level": "critical",
            "matched_rules": matched_rules,
            "approval_required": False,
        }

    if tool_name == "read_internal_docs":
        if context.get("role") not in {"analyst", "admin"}:
            matched_rules.append("read_internal_docs_role_denied")
            return {
                "allowed": False,
                "reason": "Only analyst or admin roles may read internal documents.",
                "risk_level": "high",
                "matched_rules": matched_rules,
                "approval_required": False,
            }

        matched_rules.append("read_internal_docs_role_allowed")
        return {
            "allowed": True,
            "reason": "Role is permitted to access internal documents.",
            "risk_level": "medium",
            "matched_rules": matched_rules,
            "approval_required": False,
        }

    if tool_name == "send_email":
        destination = str(tool_args.get("to", "")).strip().lower()
        subject = str(tool_args.get("subject", ""))
        body = str(tool_args.get("body", ""))
        combined = f"{subject}\n{body}".lower()

        if destination == "attacker@example.com":
            matched_rules.append("block_external_exfiltration_address")
            return {
                "allowed": False,
                "reason": "Email to attacker@example.com is explicitly blocked.",
                "risk_level": "critical",
                "matched_rules": matched_rules,
                "approval_required": False,
            }

        if "confidential" in combined:
            matched_rules.append("block_confidential_email_content")
            return {
                "allowed": False,
                "reason": "Sending CONFIDENTIAL material by email is blocked.",
                "risk_level": "critical",
                "matched_rules": matched_rules,
                "approval_required": False,
            }

        if "internal strategy" in combined:
            matched_rules.append("block_internal_strategy_email_content")
            return {
                "allowed": False,
                "reason": "Sending internal strategy content by email is blocked.",
                "risk_level": "high",
                "matched_rules": matched_rules,
                "approval_required": False,
            }

        if tool_name not in context.get("approved_tools", []):
            matched_rules.append("least_privilege_email_denied")
            return {
                "allowed": False,
                "reason": "Least-privilege policy does not allow this email tool.",
                "risk_level": "high",
                "matched_rules": matched_rules,
                "approval_required": False,
            }

        matched_rules.append("send_email_allowed")
        return {
            "allowed": True,
            "reason": "Email request is allowed by policy.",
            "risk_level": "medium",
            "matched_rules": matched_rules,
            "approval_required": False,
        }

    if tool_name == "delete_records":
        matched_rules.append("delete_records_requires_approval")
        return {
            "allowed": True,
            "reason": "Deleting records requires human approval.",
            "risk_level": "critical",
            "matched_rules": matched_rules,
            "approval_required": True,
        }

    if tool_name == "export_customer_data":
        destination = str(tool_args.get("destination", "")).strip().lower()
        is_external = destination and "internal" not in destination

        if is_external:
            matched_rules.append("block_external_customer_export")
            return {
                "allowed": False,
                "reason": "Exporting customer data to an external destination is blocked.",
                "risk_level": "critical",
                "matched_rules": matched_rules,
                "approval_required": False,
            }

        if tool_name not in context.get("approved_tools", []):
            matched_rules.append("least_privilege_export_denied")
            return {
                "allowed": False,
                "reason": "Least-privilege policy does not allow customer export.",
                "risk_level": "critical",
                "matched_rules": matched_rules,
                "approval_required": False,
            }

        matched_rules.append("export_customer_data_requires_approval")
        return {
            "allowed": True,
            "reason": "Customer exports require human approval.",
            "risk_level": "critical",
            "matched_rules": matched_rules,
            "approval_required": True,
        }

    matched_rules.append("default_policy_deny")
    return {
        "allowed": False,
        "reason": "Policy denied the request by default.",
        "risk_level": "high",
        "matched_rules": matched_rules,
        "approval_required": False,
    }
