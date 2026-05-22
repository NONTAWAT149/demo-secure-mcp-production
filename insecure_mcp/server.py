"""Insecure FastMCP server that blindly exposes enterprise tools."""

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


# This represents insecure production MCP where the MCP server is only used
# as a transport/tool layer without governance.
mcp = FastMCP("Insecure Production MCP Demo")


@mcp.tool
def read_internal_docs() -> str:
    """Expose confidential data with no policy guardrails."""
    return raw_read_internal_docs()


@mcp.tool
def send_email(to: str, subject: str, body: str) -> str:
    """Forward the email request directly."""
    return raw_send_email(to, subject, body)


@mcp.tool
def delete_records(record_id: str) -> str:
    """Expose record deletion without validation."""
    return raw_delete_records(record_id)


@mcp.tool
def export_customer_data(destination: str) -> str:
    """Expose customer exports without approval or DLP."""
    return raw_export_customer_data(destination)


if __name__ == "__main__":
    mcp.run()
