"""
Streamlit chat UI — AI Data Analyst Agent (Week 3 — real answer + chart)
=========================================================================
Run with:
    streamlit run frontend/app.py
"""
from __future__ import annotations

import requests
import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AI Data Analyst Agent",
    page_icon="🤖",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

st.markdown("""
<style>
    .main { background-color: #0f0f1a; }
    .block-container { padding-top: 2rem; max-width: 900px; }
    .stChatMessage { border-radius: 12px; }
    h1 { background: linear-gradient(135deg, #6366f1, #a78bfa);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .answer-box {
        background: linear-gradient(135deg, #1e1b4b 0%, #1a1a2e 100%);
        border: 1px solid #4f46e5;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        color: #e2e8f0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .route-badge {
        display: inline-block;
        background: #4f46e5;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("## ⚙️ Settings")
    backend_url = st.text_input("Backend URL", value="http://localhost:8000")
    route_override = st.selectbox(
        "Route override (optional)",
        ["", "sql", "rag", "hybrid"],
        help="Leave blank to let the agent classify automatically.",
    )
    st.markdown("---")
    st.markdown("**Stack**")
    st.markdown("🔀 LangGraph routing")
    st.markdown("🗄️ DuckDB SQL")
    st.markdown("📄 ChromaDB RAG")
    st.markdown("🤖 Groq Llama 3.3")
    st.markdown("📊 Plotly charts")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown("# 🤖 AI Data Analyst Agent")
st.caption("Ask questions about your data — powered by LangGraph, DuckDB, ChromaDB & Groq")
st.divider()

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="answer-box">{msg["content"]}</div>', unsafe_allow_html=True)
            if msg.get("chart"):
                fig = go.Figure(msg["chart"])
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------

if prompt := st.chat_input("Ask a question about your data…"):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                payload = {"question": prompt, "route": route_override}
                resp = requests.post(f"{backend_url}/ask", json=payload, timeout=90)
                resp.raise_for_status()
                data = resp.json()

                # ── Route badge ────────────────────────────────────────────
                route = data.get("route", "?")
                st.markdown(f'<span class="route-badge">📍 {route}</span>', unsafe_allow_html=True)

                # ── Answer ─────────────────────────────────────────────────
                answer = data.get("final_answer", "(no answer)")
                st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

                # ── Chart ──────────────────────────────────────────────────
                chart_data = data.get("chart_data")
                fig_obj = None
                if chart_data and chart_data.get("data"):
                    fig_obj = go.Figure(chart_data)
                    fig_obj.update_layout(
                        height=380,
                        margin=dict(l=40, r=20, t=50, b=60),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(15,15,26,0.5)",
                        font=dict(color="#e2e8f0"),
                    )
                    st.plotly_chart(fig_obj, use_container_width=True)

                # ── Debug expander ─────────────────────────────────────────
                with st.expander("🔍 Full agent state (debug)"):
                    st.json(data)

                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "chart": chart_data if fig_obj else None,
                })

            except requests.exceptions.ConnectionError:
                err = (
                    f"❌ Cannot reach backend at `{backend_url}`.\n\n"
                    "```bash\nuvicorn backend.main:app --reload\n```"
                )
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})

            except requests.exceptions.HTTPError as exc:
                err = f"❌ Backend error {exc.response.status_code}: {exc.response.text}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})

            except Exception as exc:
                err = f"❌ Unexpected error: {exc}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
