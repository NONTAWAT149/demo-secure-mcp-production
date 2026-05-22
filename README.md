# Insecure vs Secure Production MCP Architecture

This demo shows how to secure production MCP-based Agentic AI systems.

## Demo purpose

MCP is not inherently secure.
MCP standardizes how Agentic AI systems discover and use tools.
As MCP becomes useful in production AI, the MCP server or gateway becomes a critical security boundary.

This demo contrasts:

- Insecure Production MCP: the MCP layer blindly forwards tool requests.
- Secure Production MCP: the MCP layer enforces governance controls before tools execute.

Everything in this project is simulated:

- No real LLM API
- No real email
- No real database
- No external systems

## Key lesson

MCP improves interoperability for Agentic AI tools, but MCP is not security by default.
In production, the MCP layer must be treated as a critical security boundary and protected with governance controls.

## Run

```bash
uv sync
uv run streamlit run app.py
```

Use a Python 3 environment. The demo is intentionally simple, but it expects a modern Python runtime compatible with Streamlit and FastMCP.

Optional MCP server entrypoints:

```bash
uv run python insecure_mcp/server.py
uv run python secure_mcp/server.py
```

## Demo script

1. Show insecure production MCP.
2. Paste the malicious prompt.
3. Run the attack.
4. Show the fake data leak.
5. Explain that MCP blindly forwarded the tool request.
6. Show secure production MCP.
7. Run the same prompt.
8. Show policy, DLP, approval, and trust checks blocking the action.
9. Show the audit log.
10. Conclude: "As MCP adoption grows, securing the MCP governance layer is essential for production Agentic AI."
