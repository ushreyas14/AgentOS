"""
app.py
──────
Streamlit frontend for the Multi-Agent Productivity System.
Run: streamlit run app.py
"""

import os
import streamlit as st
from coordinator import plan
from executor import execute, format_results
from store import _init

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgentOS",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Syne:wght@400;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace;
    background-color: #0a0a0f;
    color: #c9d1d9;
}
.stApp { background: #0a0a0f; }
[data-testid="stSidebar"] {
    background: #0d0d14 !important;
    border-right: 1px solid #1e1e2e;
}
[data-testid="stSidebar"] * { font-family: 'JetBrains Mono', monospace !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

.agentos-header {
    font-family: 'Syne', sans-serif;
    font-weight: 800; font-size: 2rem; letter-spacing: -0.02em;
    background: linear-gradient(135deg, #58a6ff 0%, #79c0ff 40%, #a5d6ff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin: 0; padding: 0;
}
.agentos-sub {
    font-size: 0.7rem; color: #484f58;
    letter-spacing: 0.15em; text-transform: uppercase; margin-top: 2px;
}
.chat-wrapper {
    background: #0d0d14; border: 1px solid #1e1e2e;
    border-radius: 8px; padding: 1rem;
    min-height: 420px; max-height: 520px; overflow-y: auto;
}
.msg-user {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 6px 6px 0 6px;
    padding: 10px 14px; margin: 8px 0 8px 60px;
    font-size: 0.82rem; color: #e6edf3;
}
.msg-user::before {
    content: "YOU"; font-size: 0.6rem; color: #484f58;
    display: block; margin-bottom: 4px; letter-spacing: 0.1em;
}
.msg-agent {
    background: #0f1923; border: 1px solid #1a3a5c;
    border-left: 3px solid #58a6ff;
    border-radius: 0 6px 6px 6px;
    padding: 10px 14px; margin: 8px 60px 8px 0;
    font-size: 0.82rem; color: #c9d1d9;
}
.msg-agent::before {
    content: "AGENTOS"; font-size: 0.6rem; color: #58a6ff;
    display: block; margin-bottom: 6px;
    letter-spacing: 0.12em; font-weight: 700;
}
.msg-error {
    background: #1a0a0a; border: 1px solid #5c1a1a;
    border-left: 3px solid #f85149; border-radius: 6px;
    padding: 10px 14px; margin: 8px 0;
    font-size: 0.82rem; color: #ffa198;
}
.msg-system {
    text-align: center; color: #484f58;
    font-size: 0.7rem; margin: 12px 0; letter-spacing: 0.08em;
}
.route-badge {
    display: inline-block; background: #161b22;
    border: 1px solid #21262d; border-radius: 4px;
    padding: 2px 8px; font-size: 0.65rem; color: #8b949e;
    margin: 2px 3px; letter-spacing: 0.05em;
}
.stat-card {
    background: #0d0d14; border: 1px solid #1e1e2e;
    border-radius: 6px; padding: 14px 16px; text-align: center;
}
.stat-num {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem; font-weight: 700; color: #58a6ff; line-height: 1;
}
.stat-label {
    font-size: 0.65rem; color: #484f58;
    text-transform: uppercase; letter-spacing: 0.12em; margin-top: 4px;
}
.panel-item {
    background: #0d0d14; border: 1px solid #1e1e2e;
    border-radius: 4px; padding: 8px 12px; margin: 4px 0;
    font-size: 0.75rem; display: flex; align-items: center; gap: 8px;
}
.panel-item.done { opacity: 0.4; text-decoration: line-through; }
.priority-high   { color: #f85149; font-size: 0.6rem; }
.priority-medium { color: #d29922; font-size: 0.6rem; }
.priority-low    { color: #3fb950; font-size: 0.6rem; }
.tag-badge {
    background: #161b22; border: 1px solid #21262d;
    border-radius: 3px; padding: 1px 6px;
    font-size: 0.6rem; color: #8b949e;
}
.stTextInput > div > div > input {
    background: #0d0d14 !important; border: 1px solid #21262d !important;
    border-radius: 6px !important; color: #e6edf3 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important; padding: 10px 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #58a6ff !important;
    box-shadow: 0 0 0 2px rgba(88,166,255,0.1) !important;
}
.stTextInput > div > div > input::placeholder { color: #484f58 !important; }
.stButton > button {
    background: #161b22 !important; border: 1px solid #21262d !important;
    color: #c9d1d9 !important; font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important; border-radius: 6px !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    border-color: #58a6ff !important; color: #58a6ff !important;
    background: #0f1923 !important;
}
.section-header {
    font-family: 'Syne', sans-serif; font-size: 0.75rem; font-weight: 600;
    letter-spacing: 0.15em; text-transform: uppercase; color: #484f58;
    margin: 16px 0 8px 0; padding-bottom: 6px; border-bottom: 1px solid #1e1e2e;
}
.hint { font-size: 0.65rem; color: #484f58; margin-top: 4px; letter-spacing: 0.04em; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #21262d; border-radius: 2px; }
hr { border-color: #1e1e2e !important; margin: 1rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Init session state ────────────────────────────────────────────────────────
_init()
if "submitted_message" not in st.session_state:
    st.session_state.submitted_message = None
# API key loaded silently — never shown in the UI
def _get_api_key() -> str:
    """Read key from Streamlit secrets (cloud) or env var (local/Cloud Shell)."""
    if "GOOGLE_API_KEY" in st.secrets:
        return st.secrets["GOOGLE_API_KEY"]
    return os.environ.get("GOOGLE_API_KEY", "")


# ── Core pipeline ─────────────────────────────────────────────────────────────
def process_message(message: str):
    """1 API call → plan → execute (0 API calls) → append to chat."""
    st.session_state.chat_history.append({"role": "user", "content": message})

    api_key = _get_api_key()
    if not api_key:
        st.session_state.chat_history.append({
            "role": "error",
            "content": "GOOGLE_API_KEY not found. Run: export GOOGLE_API_KEY='your_key'",
        })
        return

    try:
        actions = plan(message, api_key)
        st.session_state.api_call_count += 1
    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower():
            msg = "Rate limit hit — wait ~30s and try again."
        elif "404" in err:
            msg = "Model not found — verify the model name in coordinator.py."
        elif "API_KEY" in err or "invalid" in err.lower():
            msg = "Invalid API key — check your GOOGLE_API_KEY env variable."
        else:
            msg = f"API error: {err[:150]}"
        st.session_state.chat_history.append({"role": "error", "content": msg})
        return

    if not actions:
        st.session_state.chat_history.append({
            "role": "error",
            "content": "Couldn't understand that. Try rephrasing.",
        })
        return

    results = execute(actions)
    reply   = format_results(results)
    routing = list({a["agent"] for a in actions})
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": reply,
        "routing": routing,
    })


# ── Process pending message BEFORE rendering (buttons + form both land here) ──
if st.session_state.submitted_message:
    msg = st.session_state.submitted_message
    st.session_state.submitted_message = None
    with st.spinner(""):
        process_message(msg)
    st.rerun()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="agentos-header">⬡ AgentOS</p>', unsafe_allow_html=True)
    st.markdown('<p class="agentos-sub">Multi-Agent System v1.0</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Stats
    st.markdown('<p class="section-header">Session Stats</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="stat-card">
            <div class="stat-num">{st.session_state.api_call_count}</div>
            <div class="stat-label">API Calls</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        total = len(st.session_state.tasks) + len(st.session_state.events) + len(st.session_state.notes)
        st.markdown(f"""<div class="stat-card">
            <div class="stat-num">{total}</div>
            <div class="stat-label">Records</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Quick commands — only the 9 tools the agents actually support
    st.markdown('<p class="section-header">Quick Commands</p>', unsafe_allow_html=True)

    quick_cmds = {
        "📋 List tasks":       "Show all my tasks",
        "📅 List reminders":   "Show all my reminders",
        "📝 List notes":       "Show all my notes",
        "📊 Show everything":  "Show all tasks, reminders, and notes",
    }
    for label, cmd in quick_cmds.items():
        if st.button(label, key=f"qbtn_{label}", use_container_width=True):
            st.session_state.submitted_message = cmd
            st.rerun()   # ← trigger processing immediately

    st.markdown("---")

    st.markdown('<p class="section-header">Data</p>', unsafe_allow_html=True)
    if st.button("🗑 Clear all data", use_container_width=True):
        st.session_state.tasks = []
        st.session_state.events = []
        st.session_state.notes = []
        st.session_state.chat_history = []
        st.session_state.api_call_count = 0
        st.rerun()
    if st.button("💬 Clear chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.markdown('<p class="hint" style="text-align:center">1 API call per message<br>Sub-agents: pure Python</p>', unsafe_allow_html=True)


# ── Main layout ───────────────────────────────────────────────────────────────
left_col, right_col = st.columns([3, 2], gap="large")

# ════════════════════════════════════════════════════════════
# LEFT — Chat
# ════════════════════════════════════════════════════════════
with left_col:
    st.markdown('<p class="agentos-header">⬡ AgentOS</p>', unsafe_allow_html=True)
    st.markdown('<p class="agentos-sub">Coordinator · Task · Calendar · Notes</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Chat history
    chat_html = '<div class="chat-wrapper">'
    if not st.session_state.chat_history:
        chat_html += """
        <div class="msg-system">── system initialized ──<br>type a message or use quick commands</div>
        <div style="margin:40px 0;text-align:center;color:#21262d;font-size:0.7rem;letter-spacing:0.1em">
            TRY: "add high priority task finish report, set reminder for 2025-10-01, save note launch plan"
        </div>"""
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f'<div class="msg-user">{msg["content"]}</div>'
            elif msg["role"] == "assistant":
                content = msg["content"].replace("\n", "<br>")
                routing = msg.get("routing", [])
                if routing:
                    badges = "".join(f'<span class="route-badge">{a}</span>' for a in routing)
                    chat_html += f'<div style="margin:4px 0 0;font-size:0.6rem;color:#484f58">routed → {badges}</div>'
                chat_html += f'<div class="msg-agent">{content}</div>'
            elif msg["role"] == "error":
                chat_html += f'<div class="msg-error">⚠ {msg["content"]}</div>'
            elif msg["role"] == "system":
                chat_html += f'<div class="msg-system">── {msg["content"]} ──</div>'
    chat_html += "</div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    # Input form
    st.markdown("<br>", unsafe_allow_html=True)
    with st.form(key="chat_form", clear_on_submit=True):
        input_col, btn_col = st.columns([5, 1])
        with input_col:
            user_input = st.text_input(
                label="input",
                label_visibility="collapsed",
                placeholder='e.g. "Add high priority task fix bug #42"',
            )
        with btn_col:
            submitted = st.form_submit_button("→ Send", use_container_width=True)

    st.markdown('<p class="hint">Multi-step works too: "add task X, set reminder for Y, save note Z"</p>', unsafe_allow_html=True)

    if submitted and user_input.strip():
        st.session_state.submitted_message = user_input.strip()
        st.rerun()


# ════════════════════════════════════════════════════════════
# RIGHT — Live data panels
# ════════════════════════════════════════════════════════════
with right_col:

    # Tasks
    st.markdown('<p class="section-header">📋 Tasks</p>', unsafe_allow_html=True)
    tasks = st.session_state.tasks
    if not tasks:
        st.markdown('<p class="hint" style="margin:8px 0">No tasks yet.</p>', unsafe_allow_html=True)
    else:
        for t in reversed(tasks):
            done_cls = "done" if t["done"] else ""
            p_cls    = f"priority-{t['priority']}"
            icon     = "✓" if t["done"] else "○"
            st.markdown(f"""<div class="panel-item {done_cls}">
                <span style="color:#484f58">{icon}</span>
                <span style="flex:1">#{t['id']} {t['title']}</span>
                <span class="{p_cls}">{t['priority'].upper()}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Reminders
    st.markdown('<p class="section-header">📅 Reminders</p>', unsafe_allow_html=True)
    events = st.session_state.events
    if not events:
        st.markdown('<p class="hint" style="margin:8px 0">No reminders yet.</p>', unsafe_allow_html=True)
    else:
        for e in reversed(events):
            st.markdown(f"""<div class="panel-item">
                <span style="color:#484f58">◷</span>
                <span style="flex:1">#{e['id']} {e['title']}</span>
                <span style="color:#484f58;font-size:0.65rem">{e['date']} {e['time']}</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Notes
    st.markdown('<p class="section-header">📝 Notes</p>', unsafe_allow_html=True)
    notes = st.session_state.notes
    if not notes:
        st.markdown('<p class="hint" style="margin:8px 0">No notes yet.</p>', unsafe_allow_html=True)
    else:
        for n in reversed(notes):
            st.markdown(f"""<div class="panel-item">
                <span style="color:#484f58">◈</span>
                <span style="flex:1">#{n['id']} {n['title']}</span>
                <span class="tag-badge">#{n['tag']}</span>
            </div>""", unsafe_allow_html=True)