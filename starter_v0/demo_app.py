"""
demo_app.py — Streamlit demo for DAY04 Research Agent
Showcase: live chat + version comparison + run evidence browser
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version

load_lab_env(ROOT)

ARTIFACTS_DIR = ROOT / "artifacts"
RUNS_DIR = ROOT / "runs"
TRANSCRIPTS_DIR = ROOT / "transcripts"

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🔬 Research Agent Demo",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Sidebar gradient */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}
[data-testid="stSidebar"] * {
    color: #e0e0ff !important;
}
[data-testid="stSidebar"] label {
    font-weight: 500;
}

/* Main area */
.main {
    background: #0d1117;
}

/* Hero header */
.hero-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid rgba(99, 179, 237, 0.2);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: "";
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99,179,237,0.08) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 0 0 0.3rem 0;
    background: linear-gradient(135deg, #63b3ed, #9f7aea);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    color: #94a3b8;
    font-size: 1rem;
    margin: 0;
}

/* Chat messages */
.chat-user {
    background: linear-gradient(135deg, #2d3748, #1a202c);
    border-left: 3px solid #63b3ed;
    border-radius: 0 12px 12px 0;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    color: #e2e8f0;
}
.chat-agent {
    background: linear-gradient(135deg, #1a3a5c, #0d2137);
    border-left: 3px solid #9f7aea;
    border-radius: 0 12px 12px 0;
    padding: 0.75rem 1rem;
    margin: 0.5rem 0;
    color: #e2e8f0;
}
.tool-call-badge {
    display: inline-block;
    background: linear-gradient(135deg, #2d1b69, #1a0f3d);
    border: 1px solid rgba(159,122,234,0.4);
    border-radius: 8px;
    padding: 0.3rem 0.7rem;
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
    color: #c4b5fd;
    margin: 0.2rem 0.2rem 0.2rem 0;
}
.status-pass {
    color: #48bb78;
    font-weight: 600;
}
.status-fail {
    color: #fc8181;
    font-weight: 600;
}

/* Version badge */
.version-badge {
    display: inline-block;
    background: linear-gradient(135deg, #0f3460, #1a1a2e);
    border: 1px solid rgba(99,179,237,0.3);
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: #63b3ed;
    margin: 0.1rem;
}

/* Metric card */
.metric-card {
    background: linear-gradient(135deg, #1a202c, #0d1117);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    text-align: center;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: #63b3ed;
    margin-bottom: 0.2rem;
}
.metric-label {
    color: #94a3b8;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Section header */
.section-header {
    font-size: 1.1rem;
    font-weight: 600;
    color: #63b3ed;
    border-bottom: 1px solid rgba(99,179,237,0.2);
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

/* Quick scenario chips */
.scenario-chip {
    background: rgba(99,179,237,0.08);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    color: #e2e8f0;
    cursor: pointer;
    transition: all 0.2s;
}
.scenario-chip:hover {
    background: rgba(99,179,237,0.15);
}

/* Scrollable run list */
.run-item {
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    margin: 0.3rem 0;
    background: rgba(255,255,255,0.02);
    font-size: 0.85rem;
    color: #cbd5e0;
}

/* Progress bar */
.progress-bar-wrap {
    background: rgba(255,255,255,0.05);
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
    margin-top: 0.4rem;
}
.progress-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #48bb78, #63b3ed);
}
</style>
""", unsafe_allow_html=True)

# ─── Helpers ─────────────────────────────────────────────────────────────────

def load_runs() -> list[dict[str, Any]]:
    runs = []
    if RUNS_DIR.exists():
        for f in sorted(RUNS_DIR.glob("*.json"), reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                data["_filename"] = f.name
                runs.append(data)
            except Exception:
                pass
    return runs

def load_transcripts() -> list[dict[str, Any]]:
    transcripts = []
    if TRANSCRIPTS_DIR.exists():
        for f in sorted(TRANSCRIPTS_DIR.glob("*.transcript.json"), reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                data["_filename"] = f.name
                transcripts.append(data)
            except Exception:
                pass
    return transcripts

def load_version_log() -> list[dict[str, str]]:
    log_path = ARTIFACTS_DIR / "version_log.csv"
    if not log_path.exists():
        return []
    rows = []
    lines = log_path.read_text(encoding="utf-8").splitlines()
    if not lines:
        return []
    headers = [h.strip() for h in lines[0].split(",")]
    for line in lines[1:]:
        if not line.strip():
            continue
        # Handle quoted fields
        import csv, io
        reader = csv.reader(io.StringIO(line))
        vals = next(reader, [])
        if len(vals) == len(headers):
            rows.append(dict(zip(headers, vals)))
    return rows

def format_tool_calls(tool_events: list[dict]) -> str:
    parts = []
    for ev in tool_events:
        name = ev.get("tool", "?")
        args = ev.get("args", {})
        parts.append(f"🔧 **{name}**({', '.join(f'{k}={json.dumps(v, ensure_ascii=False)}' for k,v in args.items())})")
    return "\n\n".join(parts)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Cấu hình")
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "gemini", "anthropic"], index=1)
    version_label = st.text_input("Version label", value="v6")
    st.markdown("---")
    st.markdown("### 🗂️ Navigation")
    page = st.radio("Trang", ["💬 Live Chat", "📊 Version History", "🗃️ Run Evidence", "📋 Scenarios"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### 🔑 Status")
    # Check API key
    import os
    api_key_set = bool(os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("GEMINI_API_KEY"))
    if api_key_set:
        st.success("✅ API Key đã cấu hình")
    else:
        st.error("❌ Chưa có API Key")
    st.markdown(f"**Artifacts locked?**")
    sp_exists = (ARTIFACTS_DIR / "system_prompt.md").exists()
    tools_exists = (ARTIFACTS_DIR / "tools.yaml").exists()
    st.success("✅ system_prompt.md" if sp_exists else "❌ system_prompt.md")
    st.success("✅ tools.yaml" if tools_exists else "❌ tools.yaml")

# ─── Hero Header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🔬 Research Agent — DAY04 G05</div>
    <p class="hero-sub">Tìm tin · Đọc bài báo khoa học · Tra chính sách nội bộ · Xác nhận an toàn trước khi gửi</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# PAGE: LIVE CHAT
# ═══════════════════════════════════════════════════════
if page == "💬 Live Chat":
    col_chat, col_trace, col_info = st.columns([2.5, 1.5, 1])

    with col_info:
        st.markdown('<div class="section-header">⚡ Quick Scenarios</div>', unsafe_allow_html=True)
        scenarios = [
            ("🔍 Tin tức AI", "Có tin tức gì về AI hôm nay không?"),
            ("📰 Đọc bài báo", "Tóm tắt bài viết tại https://openai.com/blog giúp mình."),
            ("🔬 Tìm arXiv", "Tìm các bài báo mới nhất về RLHF trên arXiv."),
            ("👤 Timeline", "Cho tôi xem 5 bài đăng gần đây của Elon Musk."),
            ("📜 Chính sách", "Chính sách nội bộ về data privacy là gì?"),
            ("📤 Gửi an toàn", "Đăng bản tin này lên Telegram giúp tôi."),
            ("🚫 Out of scope", "Đặt vé máy bay Hà Nội - Đà Nẵng giúp tôi."),
        ]
        for icon_label, text in scenarios:
            if st.button(icon_label, key=f"sc_{icon_label}", use_container_width=True):
                if "chat_messages" not in st.session_state:
                    st.session_state.chat_messages = []
                if "pending_input" not in st.session_state:
                    st.session_state.pending_input = ""
                st.session_state.pending_input = text

        st.markdown("---")
        st.markdown('<div class="section-header">🛠️ Tools Available</div>', unsafe_allow_html=True)
        tools_info = [
            ("clarify", "Hỏi lại / Confirm"),
            ("timeline", "Timeline MXH"),
            ("social_search", "Tìm MXH"),
            ("lookup", "Tra cứu web"),
            ("fetch", "Đọc URL"),
            ("format", "Format output"),
            ("send", "Gửi (cần confirm)"),
            ("policy", "Chính sách nội bộ"),
            ("papers", "Bài báo arXiv"),
            ("paper_text", "Nội dung PDF"),
        ]
        for tname, tdesc in tools_info:
            st.markdown(f'<span class="version-badge">{tname}</span>', unsafe_allow_html=True)

    with col_trace:
        st.markdown('<div class="section-header">🔬 Tool Execution Trace</div>', unsafe_allow_html=True)
        last_events = st.session_state.get("last_tool_events", [])
        if not last_events:
            st.info("Chưa có lượt gọi tool nào trong câu hỏi gần nhất hoặc lịch sử trống.")
        else:
            st.markdown(f"Đã gọi **{len(last_events)}** tool(s) ở lượt chạy cuối:")
            for idx, ev in enumerate(last_events):
                name = ev.get("tool", "?")
                args = ev.get("args", {})
                result = ev.get("result", {})
                
                # Check for error
                is_err = False
                err_msg = ""
                if isinstance(result, dict):
                    if "error" in result and result.get("error"):
                        is_err = True
                        err_msg = f"{result.get('error')}: {result.get('message', '')}"
                    elif isinstance(result.get("result"), dict) and result.get("result", {}).get("error"):
                        is_err = True
                        res_err = result.get("result", {})
                        err_msg = f"{res_err.get('error')}: {res_err.get('message', '')}"
                
                status_emoji = "❌" if is_err else "✅"
                
                # Header
                st.markdown(f"**Step {idx+1}:** {status_emoji} `{name}`")
                
                # Container with details
                with st.container():
                    st.caption("📥 Input Arguments")
                    st.json(args)
                    st.caption("📤 Output Result")
                    if is_err:
                        st.error(err_msg)
                    else:
                        st.json(result)
                st.markdown("---")

    with col_chat:
        # Init state
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []  # for LLM context
        if "agent_ready" not in st.session_state:
            st.session_state.agent_ready = False
        if "pending_input" not in st.session_state:
            st.session_state.pending_input = ""
        if "last_tool_events" not in st.session_state:
            st.session_state.last_tool_events = []

        # Display messages
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_messages:
                role = msg["role"]
                content = msg["content"]
                tool_calls = msg.get("tool_calls", [])
                if role == "user":
                    with st.chat_message("user"):
                        st.markdown(content)
                elif role == "assistant":
                    with st.chat_message("assistant", avatar="🤖"):
                        if tool_calls:
                            st.markdown("##### 🛠️ Tool Executions")
                            for tc in tool_calls:
                                name = tc.get("tool", "?")
                                args = tc.get("args", {})
                                result = tc.get("result", {})
                                
                                # Check if error exists in the result
                                is_err = False
                                err_msg = ""
                                if isinstance(result, dict):
                                    if "error" in result and result.get("error"):
                                        is_err = True
                                        err_msg = f"{result.get('error')}: {result.get('message', '')}"
                                    elif isinstance(result.get("result"), dict) and result.get("result", {}).get("error"):
                                        is_err = True
                                        res_err = result.get("result", {})
                                        err_msg = f"{res_err.get('error')}: {res_err.get('message', '')}"
                                
                                status_emoji = "❌" if is_err else "✅"
                                
                                args_preview = ", ".join(f"{k}={json.dumps(v, ensure_ascii=False)}" for k, v in args.items())
                                if len(args_preview) > 60:
                                    args_preview = args_preview[:57] + "..."
                                
                                with st.expander(f"{status_emoji} **{name}**({args_preview})"):
                                    st.markdown("**Arguments:**")
                                    st.json(args)
                                    if is_err:
                                        st.markdown(f"**Error:** :red[{err_msg}]")
                                    else:
                                        st.markdown("**Result:**")
                                        st.json(result)
                            st.markdown("---")
                        if content:
                            st.markdown(content)

        # Input
        pending = st.session_state.get("pending_input", "")
        user_input = st.chat_input("Nhập câu hỏi hoặc lệnh...", key="chat_input")
        if not user_input and pending:
            user_input = pending
            st.session_state.pending_input = ""

        if user_input:
            # Add user message
            st.session_state.chat_messages.append({"role": "user", "content": user_input})

            with st.spinner("🤔 Agent đang xử lý..."):
                try:
                    # Load agent components
                    sp_path = ARTIFACTS_DIR / "system_prompt.md"
                    tools_path = ARTIFACTS_DIR / "tools.yaml"
                    system_prompt = sp_path.read_text(encoding="utf-8")
                    tool_declarations = load_tool_declarations(tools_path)
                    openai_tools = to_openai_tools(tool_declarations)
                    provider = make_provider(provider_name)

                    # Build messages
                    from chat import trim_history, run_model_tool_loop
                    history = st.session_state.chat_history
                    messages = [
                        {"role": "system", "content": system_prompt},
                        *trim_history(history, 5),
                        {"role": "user", "content": user_input},
                    ]

                    result = run_model_tool_loop(
                        provider=provider,
                        messages=messages,
                        tools=openai_tools,
                        model=None,
                        max_tool_rounds=4,
                    )

                    assistant_text = result["assistant_text"]
                    tool_events = result.get("tool_events", [])

                    # Build tool_calls for display
                    display_tools = []
                    for ev in tool_events:
                        display_tools.append({
                            "tool": ev.get("tool", "?"),
                            "args": ev.get("args", {}),
                            "result": ev.get("result", {}),
                        })

                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": assistant_text,
                        "tool_calls": display_tools,
                    })
                    st.session_state.last_tool_events = tool_events

                    # Update history
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_text})

                except Exception as e:
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": f"❌ Lỗi: {type(e).__name__}: {e}",
                        "tool_calls": [],
                    })
                    st.session_state.last_tool_events = []

            st.rerun()

        if st.button("🗑️ Xoá chat", key="clear_chat"):
            st.session_state.chat_messages = []
            st.session_state.chat_history = []
            st.session_state.last_tool_events = []
            st.rerun()

# ═══════════════════════════════════════════════════════
# PAGE: VERSION HISTORY
# ═══════════════════════════════════════════════════════
elif page == "📊 Version History":
    st.markdown('<div class="section-header">📈 Lịch sử tối ưu — Accuracy qua từng version</div>', unsafe_allow_html=True)

    rows = load_version_log()

    if rows:
        # Accuracy chart
        versions = []
        accuracies_after = []
        for row in rows:
            versions.append(row.get("version", "?"))
            try:
                accuracies_after.append(float(row.get("metric_after", 0)))
            except ValueError:
                accuracies_after.append(0.0)

        # Bar chart using st.bar_chart via pandas
        import pandas as pd
        chart_df = pd.DataFrame({
            "Version": versions,
            "Accuracy": accuracies_after,
        }).set_index("Version")
        st.bar_chart(chart_df, color="#63b3ed", height=250)

        # Metrics row
        cols = st.columns(min(len(rows), 6))
        for i, row in enumerate(rows):
            col = cols[i % len(cols)]
            with col:
                try:
                    pct = f"{float(row.get('metric_after', 0)):.0%}"
                except ValueError:
                    pct = row.get('metric_after', '?')
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{pct}</div>
                    <div class="metric-label">{row.get('version','?')}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="section-header">📋 Chi tiết từng version</div>', unsafe_allow_html=True)
        for row in rows:
            with st.expander(f"**{row.get('version','?')}** — {row.get('reason','')}", expanded=False):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"**Changed:** `{row.get('changed_artifact','')}`")
                    st.markdown(f"**Before:** `{row.get('metric_before','')}`")
                    st.markdown(f"**After:** `{row.get('metric_after','')}`")
                with c2:
                    st.markdown(f"**Hypothesis:**\n> {row.get('hypothesis','')}")
                with c3:
                    run_file = row.get("run_file", "")
                    if run_file:
                        run_path = ROOT / run_file
                        if run_path.exists():
                            st.markdown(f"**Run file:** `{run_file}`")
                            st.markdown(f"**Artifact version:** `{row.get('artifact_version','')}`")
                    st.markdown(f"**Prompt hash:** `{row.get('prompt_hash','')}`")
                    st.markdown(f"**Tools hash:** `{row.get('tools_hash','')}`")
    else:
        st.info("Chưa có dữ liệu trong version_log.csv")

# ═══════════════════════════════════════════════════════
# PAGE: RUN EVIDENCE
# ═══════════════════════════════════════════════════════
elif page == "🗃️ Run Evidence":
    st.markdown('<div class="section-header">🗃️ Run JSON Evidence Browser</div>', unsafe_allow_html=True)

    tab_runs, tab_transcripts = st.tabs(["📁 Eval Runs", "💬 Chat Transcripts"])

    with tab_runs:
        runs = load_runs()
        if not runs:
            st.info("Chưa có run file nào trong thư mục `runs/`")
        else:
            col_list, col_detail = st.columns([1, 2])
            with col_list:
                run_names = [r["_filename"] for r in runs]
                selected_run_name = st.radio("Chọn run file:", run_names, label_visibility="collapsed")

            with col_detail:
                selected_run = next((r for r in runs if r["_filename"] == selected_run_name), None)
                if selected_run:
                    summary = selected_run.get("summary", {})
                    artifact_version = selected_run.get("artifact_version", "?")

                    st.markdown(f"**Artifact version:** `{artifact_version}`")
                    # Metrics
                    m_cols = st.columns(4)
                    metrics = [
                        ("case_accuracy", "Case Acc"),
                        ("tool_routing_accuracy", "Routing"),
                        ("argument_accuracy", "Args"),
                        ("multiturn_accuracy", "Multi-turn"),
                    ]
                    for i, (key, label) in enumerate(metrics):
                        with m_cols[i]:
                            val = summary.get(key, "?")
                            color = "#48bb78" if val == 1.0 else "#ecc94b" if isinstance(val, float) and val >= 0.8 else "#fc8181"
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-value" style="color:{color}; font-size:1.5rem;">{val if isinstance(val, str) else f"{val:.0%}"}</div>
                                <div class="metric-label">{label}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    st.markdown("---")
                    # Case results
                    results = selected_run.get("results", [])
                    for case in results:
                        cid = case.get("id", "?")
                        passed = case.get("result", {}).get("passed", False)
                        failures = case.get("result", {}).get("failures", [])
                        actual_calls = case.get("result", {}).get("actual_tool_calls", [])
                        status_label = "PASS ✅" if passed else "FAIL ❌"
                        with st.expander(f"{status_label} {cid}", expanded=not passed):
                            if actual_calls:
                                st.markdown("**Actual calls:**")
                                for call in actual_calls:
                                    name = call.get("name", "?")
                                    args = call.get("args", {})
                                    st.code(f"{name}({json.dumps(args, ensure_ascii=False, indent=2)})", language="json")
                            if failures:
                                st.markdown("**Failures:**")
                                for f in failures:
                                    st.markdown(f"- {f}")

    with tab_transcripts:
        transcripts = load_transcripts()
        if not transcripts:
            st.info("Chưa có transcript nào trong thư mục `transcripts/`")
        else:
            col_list2, col_detail2 = st.columns([1, 2])
            with col_list2:
                tr_names = [t["_filename"] for t in transcripts]
                selected_tr_name = st.radio("Chọn transcript:", tr_names, label_visibility="collapsed")
            with col_detail2:
                selected_tr = next((t for t in transcripts if t["_filename"] == selected_tr_name), None)
                if selected_tr:
                    st.markdown(f"**Artifact:** `{selected_tr.get('artifact_version','?')}`")
                    st.markdown(f"**Provider:** `{selected_tr.get('provider','?')}`")
                    for turn in selected_tr.get("turns", []):
                        user_text = turn.get("user", "")
                        agent_text = turn.get("assistant_text", "")
                        tool_events = turn.get("tool_events", [])
                        st.markdown(f"👤 **You:** {user_text}")
                        if tool_events:
                            for ev in tool_events:
                                name = ev.get("tool", "?")
                                args = ev.get("args", {})
                                st.markdown(f'<span class="tool-call-badge">🔧 {name}({json.dumps(args, ensure_ascii=False)})</span>', unsafe_allow_html=True)
                        st.markdown(f"🤖 **Agent:** {agent_text}")
                        st.markdown("---")

# ═══════════════════════════════════════════════════════
# PAGE: SCENARIOS
# ═══════════════════════════════════════════════════════
elif page == "📋 Scenarios":
    st.markdown('<div class="section-header">🎬 Demo Scenarios & Checklist</div>', unsafe_allow_html=True)

    scenarios_data = [
        {
            "id": "S1",
            "title": "Research thường — Tìm tin tức AI hôm nay",
            "input": "Có tin tức gì nổi bật về AI hôm nay không?",
            "expected_tool": "lookup(query='AI', topic='news', timeframe='day')",
            "story": "Từ v0 → v1: Agent bắt đầu map đúng 'hôm nay' → timeframe='day'.",
            "versions": ["v0 (FAIL: default week)", "v1 (PASS: day)"],
        },
        {
            "id": "S2",
            "title": "Thiếu thông tin — Đọc URL chưa cung cấp",
            "input": "Tóm tắt bài viết này cho tôi. [Turn 2] https://openai.com/blog",
            "expected_tool": "clarify(response_type='text') → fetch(url=...)",
            "story": "Từ v0 → v2: Agent học cách nhận ra thiếu URL và hỏi lại thay vì guess.",
            "versions": ["v0 (FAIL: guess URL)", "v2 (PASS: clarify)"],
        },
        {
            "id": "S3",
            "title": "Confirmation Boundary — Gửi tin nhắn",
            "input": "Đăng bản tin này lên Telegram giúp tôi.",
            "expected_tool": "clarify(response_type='yes_no') KHÔNG gọi send ngay",
            "story": "Từ v3 → v5: Agent học ranh giới xác nhận. Phân biệt 'hỏi text' vs 'hỏi yes/no'.",
            "versions": ["v3 (FAIL: response_type='text')", "v5 (PASS: yes_no)"],
        },
        {
            "id": "S4",
            "title": "Multi-turn Switch — Bỏ Twitter sang Web",
            "input": "Tìm tweet của Sam Altman. [Turn 2] Thôi bỏ Twitter, tìm web thay đi.",
            "expected_tool": "CHỈ gọi lookup, KHÔNG gọi thêm timeline",
            "story": "Từ v3 → v6: Agent học 'tool switching' — khi user nói bỏ, là bỏ hẳn.",
            "versions": ["v0 (FAIL: gọi cả 2 tools)", "v3 (PASS: chỉ lookup)"],
        },
        {
            "id": "S5",
            "title": "Contextual Tool — Social Search vs Papers",
            "input": "Tìm top 5 thảo luận nổi bật về AI safety trên mạng xã hội.",
            "expected_tool": "social_search(search_type='Top') KHÔNG dùng papers",
            "story": "v6: Prompt dạy phân biệt 'bài viết MXH' ≠ 'bài báo khoa học'.",
            "versions": ["v5 (FAIL: gọi papers)", "v6 (PASS: social_search)"],
        },
    ]

    for sc in scenarios_data:
        with st.expander(f"**{sc['id']}** — {sc['title']}", expanded=True):
            cols = st.columns([2, 2, 1])
            with cols[0]:
                st.markdown("**🗣️ User input:**")
                st.info(sc["input"])
                st.markdown("**✅ Expected tool trace:**")
                st.code(sc["expected_tool"], language="python")
            with cols[1]:
                st.markdown("**📖 Version story:**")
                st.markdown(sc["story"])
                st.markdown("**📊 Versions:**")
                for v in sc["versions"]:
                    color = "#48bb78" if "PASS" in v else "#fc8181"
                    st.markdown(f"<span style='color:{color}'>{'✅' if 'PASS' in v else '❌'} {v}</span>", unsafe_allow_html=True)
            with cols[2]:
                # Try button
                simple_input = sc["input"].split("[Turn")[0].strip()
                if st.button(f"▶️ Thử ngay", key=f"try_{sc['id']}"):
                    st.session_state.pending_input = simple_input
                    # Redirect hint
                    st.markdown("👈 Chuyển sang **Live Chat** để xem kết quả!")

    st.markdown("---")
    st.markdown('<div class="section-header">✅ Pre-Demo Checklist</div>', unsafe_allow_html=True)
    checklist = [
        ("🔑 API key và quota đã kiểm tra", api_key_set),
        ("📁 artifacts/system_prompt.md đã lock (không sửa nữa)", sp_exists),
        ("📁 artifacts/tools.yaml đã lock", tools_exists),
        ("📋 version_log.csv đầy đủ v0→v6", len(load_version_log()) >= 3),
        ("📁 Run JSON evidence tồn tại", len(load_runs()) > 0),
        ("💬 Transcript live chat tồn tại", len(load_transcripts()) > 0),
        ("🔒 Secrets không lộ trong screenshot", True),
        ("🌐 Demo URL (local) có thể mở được", True),
    ]
    for label, status in checklist:
        icon = "✅" if status else "⚠️"
        color = "#48bb78" if status else "#ecc94b"
        st.markdown(f"<span style='color:{color}'>{icon}</span> {label}", unsafe_allow_html=True)
