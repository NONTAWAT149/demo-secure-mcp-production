"""Secure FastMCP server that applies governance before tool execution."""

from typing import Dict, Optional

try:
    from fastmcp import FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP

from insecure_mcp.tools import (
    delete_records as raw_delete_records,
    export_customer_data as raw_export_customer_data,
    read_internal_docs as raw_read_internal_docs,
    send_email as raw_send_email,
)
from secure_mcp.approval import requires_human_approval, simulate_human_approval
from secure_mcp.audit import log_event
from secure_mcp.dlp import scan_for_sensitive_data
from secure_mcp.policy import DEFAULT_USER_CONTEXT, check_policy
from secure_mcp.tool_registry import validate_tool

mcp = FastMCP("Secure Production MCP Demo")

RAW_TOOL_HANDLERS = {
    "read_internal_docs": raw_read_internal_docs,
    "send_email": raw_send_email,
    "delete_records": raw_delete_records,
    "export_customer_data": raw_export_customer_data,
}


def execute_governed_tool(
    tool_name: str,
    args: Optional[Dict] = None,
    user_context: Optional[Dict] = None,
) -> Dict:
    """Apply governance at the MCP layer before calling the underlying tool."""
    request_args = args or {}
    context = DEFAULT_USER_CONTEXT.copy()
    context.update(user_context or {})

    validation = validate_tool(tool_name)
    log_event(
        event_type="tool_validation",
        tool_name=tool_name,
        decision="allowed" if validation["allowed"] else "blocked",
        reason=validation["reason"],
        risk_level=validation["risk_level"],
        args=request_args,
    )
    if not validation["allowed"]:
        return {
            "status": "blocked",
            "message": f"BLOCKED: {validation['reason']}",
            "validation": validation,
            "policy": None,
            "dlp": None,
            "approval": None,
            "result": None,
        }

    dlp_result = None
    if tool_name == "send_email":
        dlp_result = scan_for_sensitive_data(str(request_args.get("body", "")))
        log_event(
            event_type="dlp_scan",
            tool_name=tool_name,
            decision="allowed",
            reason=(
                "Sensitive content detected."
                if dlp_result["contains_sensitive_data"]
                else "No sensitive content detected."
            ),
            risk_level="high" if dlp_result["contains_sensitive_data"] else "low",
            args={"body": request_args.get("body", "")},
        )

    policy = check_policy(tool_name, request_args, context)
    log_event(
        event_type="policy_check",
        tool_name=tool_name,
        decision="allowed" if policy["allowed"] else "blocked",
        reason=policy["reason"],
        risk_level=policy["risk_level"],
        args=request_args,
    )
    if not policy["allowed"]:
        return {
            "status": "blocked",
            "message": f"BLOCKED: {policy['reason']}",
            "validation": validation,
            "policy": policy,
            "dlp": dlp_result,
            "approval": None,
            "result": None,
        }

    needs_approval = policy.get("approval_required", False) or requires_human_approval(
        tool_name, request_args
    )
    approval_result = None
    if needs_approval:
        log_event(
            event_type="approval_request",
            tool_name=tool_name,
            decision="approval_required",
            reason="High-risk action escalated for human approval.",
            risk_level=policy["risk_level"],
            args=request_args,
        )
        approval_result = simulate_human_approval(tool_name, request_args)
        if not approval_result["approved"]:
            log_event(
                event_type="approval_decision",
                tool_name=tool_name,
                decision="blocked",
                reason=approval_result["reason"],
                risk_level=policy["risk_level"],
                args=request_args,
            )
            return {
                "status": "blocked",
                "message": f"APPROVAL DENIED: {approval_result['reason']}",
                "validation": validation,
                "policy": policy,
                "dlp": dlp_result,
                "approval": approval_result,
                "result": None,
            }

    result = RAW_TOOL_HANDLERS[tool_name](**request_args)
    log_event(
        event_type="tool_execution",
        tool_name=tool_name,
        decision="allowed",
        reason="Request passed governance and tool executed.",
        risk_level=policy["risk_level"],
        args=request_args,
    )
    return {
        "status": "allowed",
        "message": result,
        "validation": validation,
        "policy": policy,
        "dlp": dlp_result,
        "approval": approval_result,
        "result": result,
    }


@mcp.tool
def read_internal_docs() -> str:
    outcome = execute_governed_tool("read_internal_docs")
    return outcome["message"]


@mcp.tool
def send_email(to: str, subject: str, body: str) -> str:
    outcome = execute_governed_tool(
        "send_email",
        {"to": to, "subject": subject, "body": body},
    )
    return outcome["message"]


@mcp.tool
def delete_records(record_id: str) -> str:
    outcome = execute_governed_tool("delete_records", {"record_id": record_id})
    return outcome["message"]


@mcp.tool
def export_customer_data(destination: str) -> str:
    outcome = execute_governed_tool(
        "export_customer_data",
        {"destination": destination},
    )
    return outcome["message"]


if __name__ == "__main__":
    mcp.run()
