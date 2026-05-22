"""Streamlit UI for the insecure vs secure production MCP architecture demo."""

from typing import Dict, List

import streamlit as st

from insecure_mcp.agent import insecure_agent
from secure_mcp.agent import secure_agent
from shared.sample_inputs import MALICIOUS_PROMPT, SAFE_PROMPT

st.set_page_config(
    page_title="Insecure vs Secure Production MCP Architecture",
    page_icon="🛡️",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --bg-soft: #f7f4ef;
        --ink: #172033;
        --muted: #5c6478;
        --danger: #c0392b;
        --danger-soft: #fff1ef;
        --safe: #1e7f5c;
        --safe-soft: #eefaf4;
        --warning: #9a6700;
        --warning-soft: #fff8db;
        --card: rgba(255, 255, 255, 0.84);
        --line: rgba(23, 32, 51, 0.12);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(210, 233, 224, 0.65), transparent 32%),
            radial-gradient(circle at top right, rgba(255, 220, 209, 0.62), transparent 28%),
            linear-gradient(180deg, #f9f6f0 0%, #f4efe7 100%);
        color: var(--ink);
    }

    .hero {
        background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(246,238,228,0.88));
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1.4rem 1.5rem;
        box-shadow: 0 20px 45px rgba(52, 43, 26, 0.08);
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.2rem;
    }

    .hero p {
        color: var(--muted);
        margin: 0.45rem 0 0;
        font-size: 1rem;
    }

    .arch-box, .result-box {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1rem 1.1rem;
        margin-bottom: 0.9rem;
    }

    .arch-label {
        font-size: 0.82rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.45rem;
    }

    .arch-flow {
        font-size: 1.08rem;
        font-weight: 600;
        line-height: 1.5;
    }

    .status-card {
        border-radius: 18px;
        padding: 1rem 1.1rem;
        border: 1px solid transparent;
        margin-bottom: 0.8rem;
    }

    .status-danger {
        background: var(--danger-soft);
        border-color: rgba(192, 57, 43, 0.18);
    }

    .status-safe {
        background: var(--safe-soft);
        border-color: rgba(30, 127, 92, 0.18);
    }

    .status-warning {
        background: var(--warning-soft);
        border-color: rgba(154, 103, 0, 0.18);
    }

    .status-title {
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    .mini-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
        gap: 0.8rem;
        margin-top: 0.75rem;
    }

    .metric-chip {
        background: rgba(255,255,255,0.72);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 0.75rem 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _render_architecture(flow: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="arch-box">
            <div class="arch-label">Architecture Diagram</div>
            <div class="arch-flow">{flow}</div>
            <div style="margin-top:0.55rem;color:#5c6478;">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_tool_calls(tool_calls: List[Dict]) -> None:
    st.markdown("**Requested MCP Tool Calls**")
    if not tool_calls:
        st.info("No privileged MCP tool calls were needed.")
        return
    st.json(tool_calls, expanded=True)


def _render_audit_log(audit_log: List[Dict]) -> None:
    st.markdown("**Audit / Security Events**")
    if not audit_log:
        st.info("No audit events were generated for this run.")
        return
    st.json(audit_log, expanded=False)


def _render_status_box(title: str, message: str, style: str) -> None:
    st.markdown(
        f"""
        <div class="status-card {style}">
            <div class="status-title">{title}</div>
            <div>{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero">
        <h1>Insecure vs Secure Production MCP Architecture</h1>
        <p>Demonstrating why production MCP servers need security controls.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Shared Prompt Input")

prompt_col, action_col = st.columns([4, 1])
with prompt_col:
    if "demo_prompt" not in st.session_state:
        st.session_state.demo_prompt = MALICIOUS_PROMPT
    prompt = st.text_area(
        "Use the same prompt across both architectures.",
        key="demo_prompt",
        height=170,
    )
with action_col:
    st.write("")
    st.write("")
    if st.button("Load Malicious", use_container_width=True):
        st.session_state.demo_prompt = MALICIOUS_PROMPT
        st.rerun()
    if st.button("Load Safe", use_container_width=True):
        st.session_state.demo_prompt = SAFE_PROMPT
        st.rerun()

tab_insecure, tab_secure = st.tabs(
    ["Insecure Production MCP", "Secure Production MCP"]
)

with tab_insecure:
    _render_architecture(
        "AI Agent → MCP Server → Enterprise Tools",
        "The MCP layer acts as a transport mechanism only. No policy, DLP, approval, or audit controls are enforced.",
    )
    if st.button("Run Insecure Demo", type="primary", key="run_insecure"):
        st.session_state.insecure_result = insecure_agent(prompt)

    insecure_result = st.session_state.get("insecure_result")
    if insecure_result:
        _render_status_box(
            "Agent Interpretation",
            insecure_result["agent_interpretation"],
            "status-danger" if insecure_result["risk_level"] == "critical" else "status-warning",
        )
        _render_tool_calls(insecure_result["tool_calls"])
        st.error(insecure_result["governance_decision"])
        st.error(insecure_result["final_result"])
        st.markdown(
            f"""
            <div class="mini-grid">
                <div class="metric-chip"><strong>Mode</strong><br>{insecure_result['mode']}</div>
                <div class="metric-chip"><strong>Risk Level</strong><br>{insecure_result['risk_level'].upper()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Run the insecure demo to show how an ungoverned MCP layer can leak data.")

with tab_secure:
    _render_architecture(
        "AI Agent → Secure MCP Governance Layer → Enterprise Tools",
        "The MCP layer enforces authorization, policy, DLP, audit logging, tool validation, approval, and least privilege before execution.",
    )
    if st.button("Run Secure Demo", type="primary", key="run_secure"):
        st.session_state.secure_result = secure_agent(prompt)

    secure_result = st.session_state.get("secure_result")
    if secure_result:
        _render_status_box(
            "Agent Interpretation",
            secure_result["agent_interpretation"],
            "status-safe" if secure_result["risk_level"] != "critical" else "status-warning",
        )
        _render_tool_calls(secure_result["tool_calls"])
        st.success("Secure governance layer is active.")
        st.warning(secure_result["governance_decision"])
        if secure_result.get("dlp_findings"):
            st.markdown("**DLP Findings**")
            st.json(secure_result["dlp_findings"], expanded=True)
        if secure_result["risk_level"] == "critical":
            st.warning(secure_result["final_result"])
        else:
            st.success(secure_result["final_result"])
        _render_audit_log(secure_result["audit_log"])
        st.markdown(
            f"""
            <div class="mini-grid">
                <div class="metric-chip"><strong>Mode</strong><br>{secure_result['mode']}</div>
                <div class="metric-chip"><strong>Risk Level</strong><br>{secure_result['risk_level'].upper()}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Run the secure demo to show the same attack being blocked by MCP governance.")

if st.session_state.get("insecure_result") and st.session_state.get("secure_result"):
    st.markdown("### Side-by-Side Comparison")
    left, right = st.columns(2)
    with left:
        st.markdown("**Insecure Outcome**")
        st.error(st.session_state.insecure_result["final_result"])
    with right:
        st.markdown("**Secure Outcome**")
        st.success(st.session_state.secure_result["final_result"])

st.markdown("### Key Takeaway")
st.info(
    "MCP improves interoperability for Agentic AI tools, but MCP is not security "
    "by default. In production, the MCP layer must be treated as a critical "
    "security boundary and protected with governance controls."
)
