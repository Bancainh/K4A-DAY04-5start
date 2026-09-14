from __future__ import annotations

import json
import sys
import time
from html import escape
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st


FRONTEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = FRONTEND_DIR.parent
STARTER_DIR = PROJECT_ROOT / "starter_v0"
ARTIFACTS_DIR = STARTER_DIR / "artifacts"
DEFAULT_SYSTEM_PROMPT = ARTIFACTS_DIR / "system_prompt.md"
DEFAULT_TOOLS = ARTIFACTS_DIR / "tools.yaml"
DEFAULT_TRANSCRIPTS_DIR = STARTER_DIR / "transcripts"

if str(STARTER_DIR) not in sys.path:
    sys.path.insert(0, str(STARTER_DIR))

from chat import (  # noqa: E402
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider  # noqa: E402
from redaction import contains_sensitive_data, sanitize_for_logging  # noqa: E402
from tools import load_tool_declarations, to_openai_tools  # noqa: E402
from versioning import artifact_version_dict, build_artifact_version  # noqa: E402


# ============================================================
#  PAGE CONFIG + CUSTOM CSS
# ============================================================
st.set_page_config(
    page_title="IT Helpdesk Agent",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Force light theme để HTML/CSS hoạt động nhất quán trên mọi máy
st.markdown(
    """
    <style>
      /* ---------- Force light background toàn app ---------- */
      :root, html, body, .stApp, [data-testid="stAppViewContainer"],
      [data-testid="stHeader"], [data-testid="stToolbar"] {
        color-scheme: light !important;
        background-color: #ffffff !important;
        color: #111827 !important;
      }
      section.main, section.main > div, .block-container {
        background: transparent !important;
      }
      section[data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg,#faf5ff 0%, #eef2ff 100%) !important;
      }
      /* ---------- Global ---------- */
      .stApp {
        background: radial-gradient(1200px 600px at 10% -10%, #eef2ff 0%, #ffffff 45%),
                    radial-gradient(900px 500px at 110% 0%, #f5f3ff 0%, #ffffff 55%) !important;
        color: #111827 !important;
      }
      section.main > div { padding-top: 1.2rem; }

      /* Streamlit default text */
      .stApp p, .stApp span, .stApp label, .stApp div,
      .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #111827;
      }
      section[data-testid="stSidebar"] .stApp p,
      section[data-testid="stSidebar"] label,
      section[data-testid="stSidebar"] span,
      section[data-testid="stSidebar"] div { color: #1f2937; }

      /* st.caption mờ -> cho rõ hơn */
      [data-testid="stCaptionContainer"], .stCaption, small {
        color: #6b7280 !important;
      }

      /* st.code / st.info / st.error nền */
      [data-testid="stCodeBlock"], pre, code {
        color: #111827 !important;
      }
      [data-testid="stCodeBlock"] {
        background: #f8fafc !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 10px !important;
        max-width: 100% !important;
      }
      [data-testid="stCodeBlock"] pre {
        white-space: pre !important;
        word-break: normal !important;
        overflow-x: auto !important;
      }
      [data-testid="stCodeBlock"] code {
        color: #1e293b !important;
        white-space: pre !important;
        word-break: normal !important;
      }

      /* Alert boxes */
      [data-testid="stAlert"] {
        border-radius: 12px !important;
      }
      [data-testid="stNotificationContentInfo"] p,
      [data-testid="stNotificationContentError"] p,
      [data-testid="stNotificationContentWarning"] p,
      [data-testid="stNotificationContentSuccess"] p {
        color: #111827 !important;
      }

      /* Expander */
      details, [data-testid="stExpander"] {
        background: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px !important;
      }
      details summary, [data-testid="stExpander"] summary {
        color: #111827 !important;
        font-weight: 600 !important;
      }

      /* Buttons */
      .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
      }
      .stButton > button[kind="primary"] {
        background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
        color: #fff !important;
        border: none !important;
      }

      /* Inputs */
      .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
        background: #ffffff !important;
        color: #111827 !important;
        border-radius: 10px !important;
        border-color: #e5e7eb !important;
      }

      /* Chat input */
      [data-testid="stChatInput"] {
        background: #ffffff !important;
        border-radius: 14px !important;
        border: 1px solid #e5e7eb !important;
      }
      [data-testid="stChatInput"] textarea {
        background: #ffffff !important;
        color: #111827 !important;
      }
      [data-testid="stChatInput"] textarea::placeholder { color: #9ca3af !important; }

      /* ---------- Hero ---------- */
      .hero {
        border-radius: 20px;
        padding: 22px 26px;
        background: linear-gradient(120deg, #4f46e5 0%, #7c3aed 45%, #db2777 100%);
        color: #fff !important;
        box-shadow: 0 14px 40px -12px rgba(79,70,229,.55);
        position: relative;
        overflow: hidden;
      }
      .hero::after{
        content:""; position:absolute; inset:0;
        background: radial-gradient(600px 200px at 90% 10%, rgba(255,255,255,.18), transparent 60%);
        pointer-events:none;
      }
      .hero h1 { margin: 0; font-size: 1.7rem; font-weight: 700; letter-spacing:-.02em; color:#fff !important; }
      .hero p  { margin: 6px 0 0; opacity:.95; font-size: .95rem; color:#fff !important; }
      .hero p code {
        background: rgba(255,255,255,.2) !important;
        color: #fff !important;
        padding: 2px 6px; border-radius: 6px;
      }
      .hero .badges { margin-top: 14px; display:flex; gap:8px; flex-wrap:wrap; }
      .pill {
        display:inline-flex; align-items:center; gap:6px;
        padding: 5px 12px; border-radius: 999px;
        background: rgba(255,255,255,.18);
        border: 1px solid rgba(255,255,255,.35);
        font-size: .8rem; font-weight:600; color:#fff !important;
        backdrop-filter: blur(6px);
      }
      .pill.mono { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }

      /* ---------- Section titles ---------- */
      .section-title {
        display:flex; align-items:center; gap:10px;
        font-weight:700; font-size:1.05rem; color:#1f2937 !important;
        margin: .2rem 0 .8rem;
      }
      .section-title .dot {
        width:10px; height:10px; border-radius:50%;
        background: linear-gradient(135deg,#6366f1,#ec4899);
        box-shadow: 0 0 0 4px rgba(99,102,241,.15);
      }

      /* ---------- Chat bubbles ---------- */
      .bubble-row { display:flex; gap:12px; margin: 14px 0; align-items:flex-start; }
      .bubble-row.user { flex-direction: row-reverse; }
      .avatar {
        width:38px; height:38px; border-radius:50%;
        display:flex; align-items:center; justify-content:center;
        font-size:1.05rem; flex-shrink:0;
        box-shadow: 0 4px 12px rgba(0,0,0,.08);
      }
      .avatar.user { background: linear-gradient(135deg,#6366f1,#8b5cf6); color:#fff !important; }
      .avatar.bot  { background: linear-gradient(135deg,#f59e0b,#ef4444); color:#fff !important; }
      .bubble {
        border-radius:16px; padding:12px 16px; max-width: 85%;
        font-size:.95rem; line-height:1.5;
        box-shadow: 0 4px 16px -8px rgba(0,0,0,.12);
        border:1px solid rgba(0,0,0,.04);
        word-wrap: break-word;
      }
      .bubble.user {
        background: linear-gradient(135deg,#4f46e5,#6366f1);
        color:#fff !important; border-top-right-radius:4px;
      }
      .bubble.user * { color:#fff !important; }
      .bubble.bot {
        background:#ffffff; color:#111827 !important;
        border-top-left-radius:4px;
      }
      .bubble.bot * { color:#111827 !important; }
      .bubble .meta {
        margin-top:8px; font-size:.75rem; opacity:.9;
        display:flex; gap:6px; flex-wrap:wrap;
      }
      .tag {
        padding:2px 8px; border-radius:999px;
        background: rgba(99,102,241,.15); color:#4338ca !important;
        font-weight:600; font-size:.7rem;
      }
      .ts { color:#9ca3af !important; font-size:.72rem; margin: 0 4px; }

      /* ---------- Timeline ---------- */
      .timeline { position:relative; padding-left: 22px; }
      .timeline::before{
        content:""; position:absolute; left:8px; top:6px; bottom:6px;
        width:2px; background: linear-gradient(#c7d2fe,#fbcfe8);
        border-radius:2px;
      }
      .tl-item { position:relative; margin: 14px 0; }
      .tl-item::before{
        content:""; position:absolute; left:-19px; top:6px;
        width:12px; height:12px; border-radius:50%;
        background:#ffffff; border:3px solid #6366f1;
        box-shadow: 0 0 0 3px rgba(99,102,241,.15);
      }
      .tl-item.error::before { border-color:#ef4444; box-shadow: 0 0 0 3px rgba(239,68,68,.15); }
      .tl-item.success::before { border-color:#10b981; box-shadow: 0 0 0 3px rgba(16,185,129,.15); }
      .tl-title { font-weight:700; font-size:.9rem; color:#111827 !important; }
      .tl-sub   { font-size:.78rem; color:#6b7280 !important; margin-top:2px; }

      /* ---------- Tool card ---------- */
      .tool-card {
        background:#ffffff; border:1px solid #e5e7eb; border-radius:14px;
        padding:12px 14px; margin: 10px 0;
        box-shadow: 0 6px 20px -14px rgba(0,0,0,.25);
      }
      .tool-card .head {
        display:flex; align-items:center; gap:8px; margin-bottom:8px;
      }
      .tool-card .name {
        font-family: ui-monospace, Menlo, monospace;
        font-weight:700; color:#4338ca !important; font-size:.88rem;
      }
      .status-badge {
        padding:2px 10px; border-radius:999px; font-size:.7rem; font-weight:700;
        margin-left:auto;
      }
      .status-ok   { background:#dcfce7; color:#166534 !important; }
      .status-err  { background:#fee2e2; color:#991b1b !important; }
      .status-wait { background:#e0e7ff; color:#3730a3 !important; }

      .json-panel {
        background:#f8fafc;
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:12px 14px;
        margin:8px 0 14px;
        max-height:420px;
        overflow:auto;
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size:.78rem;
        line-height:1.48;
        color:#1e293b !important;
        white-space:pre-wrap;
        word-break:break-word;
      }
      .path-panel {
        background:#f8fafc;
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:12px 14px;
        margin:6px 0 16px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size:.78rem;
        line-height:1.45;
        color:#1e293b !important;
        white-space:normal;
        overflow-wrap:anywhere;
      }

      /* ---------- Sidebar ---------- */
      section[data-testid="stSidebar"] {
        background: linear-gradient(180deg,#faf5ff 0%, #eef2ff 100%) !important;
        border-right: 1px solid #e5e7eb;
      }
      section[data-testid="stSidebar"] .block-container { padding-top: 1rem; }
      .side-title {
        font-weight:800; font-size:1.15rem; color:#4c1d95 !important;
        display:flex; align-items:center; gap:8px;
      }
      .side-group {
        margin: 14px 0 6px; font-size:.72rem; font-weight:800;
        color:#7c3aed !important; letter-spacing:.08em; text-transform:uppercase;
      }
      .side-sub { font-size:.78rem; color:#6b7280 !important; margin:-4px 0 8px; }

      /* Card container (st.container border=True) */
      [data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;
        border-color: #e5e7eb !important;
        border-radius: 14px !important;
      }
      [data-testid="stVerticalBlockBorderWrapper"] * { color: #111827; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
#  HELPERS
# ============================================================
def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def render_json_panel(value: Any) -> None:
    st.code(json_text(value), language="json")


def render_text_panel(value: str) -> None:
    st.code(value, language="text")


def parse_assistant_payload(raw_text: str | None) -> dict[str, Any]:
    text = (raw_text or "").strip()
    if not text:
        return {"reply": "", "raw": ""}
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {"reply": text, "raw": text}
    if not isinstance(payload, dict):
        return {"reply": text, "raw": text}
    reply = payload.get("reply")
    if not isinstance(reply, str):
        reply = text
    return {
        "intent": payload.get("intent"),
        "action": payload.get("action"),
        "reply": reply,
        "evidence_ids": payload.get("evidence_ids", []),
        "raw": text,
    }


def stream_words(text: str):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.015)


def make_transcript_id(version: str, provider: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    return "_".join([safe_slug(version), safe_slug(provider), timestamp])


@st.cache_data(show_spinner=False)
def read_system_prompt(path_text: str) -> str:
    return Path(path_text).read_text(encoding="utf-8")


@st.cache_data(show_spinner=False)
def read_tools(path_text: str) -> list[dict[str, Any]]:
    declarations = load_tool_declarations(Path(path_text))
    return to_openai_tools(declarations)


def selected_model() -> str | None:
    value = st.session_state.model.strip()
    return value or None


def current_config() -> dict[str, Any]:
    return {
        "provider": st.session_state.provider,
        "model": st.session_state.model,
        "version": st.session_state.version,
        "system_prompt": st.session_state.system_prompt_path,
        "tools": st.session_state.tools_path,
        "history_window": st.session_state.history_window,
        "max_tool_rounds": st.session_state.max_tool_rounds,
        "transcripts_dir": st.session_state.transcripts_dir,
    }


def start_new_transcript() -> None:
    prompt_path = Path(st.session_state.system_prompt_path)
    tools_path = Path(st.session_state.tools_path)
    artifact = build_artifact_version(st.session_state.version, prompt_path, tools_path)
    transcript_id = make_transcript_id(st.session_state.version, st.session_state.provider)
    transcript_path = Path(st.session_state.transcripts_dir) / f"{transcript_id}.transcript.json"

    st.session_state.artifact = artifact
    st.session_state.transcript_path = transcript_path
    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": st.session_state.provider,
        "model": selected_model(),
        "system_prompt": str(prompt_path),
        "tools": str(tools_path),
        "history_window": st.session_state.history_window,
        "max_tool_rounds": st.session_state.max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    write_transcript(transcript_path, st.session_state.transcript)


def ensure_state() -> None:
    if "active_config" not in st.session_state:
        st.session_state.active_config = current_config()
        start_new_transcript()
        return

    if st.session_state.active_config != current_config():
        st.session_state.active_config = current_config()
        start_new_transcript()


def append_turn(user_text: str) -> None:
    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": now_iso(),
        "user": sanitize_for_logging(user_text),
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    if contains_sensitive_data(user_text):
        assistant_text = json_text(
            {
                "intent": "ticket_creation",
                "action": "refuse",
                "reply": (
                    "I cannot process or store passwords, tokens, API keys, MFA/OTP values, "
                    "or recovery codes. Remove the sensitive value and describe only the technical symptom."
                ),
                "evidence_ids": [],
            }
        )
        turn_record.update(
            {
                "status": "user_input_blocked",
                "assistant_text": assistant_text,
                "ended_at": now_iso(),
            }
        )
        st.session_state.turns.append(turn_record)
        st.session_state.transcript["turns"].append(turn_record)
        write_transcript(st.session_state.transcript_path, st.session_state.transcript)
        return

    system_prompt = read_system_prompt(st.session_state.system_prompt_path)
    tools = read_tools(st.session_state.tools_path)
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, st.session_state.history_window),
        {"role": "user", "content": user_text},
    ]

    try:
        provider = make_provider(st.session_state.provider)
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=tools,
            model=selected_model(),
            max_tool_rounds=st.session_state.max_tool_rounds,
        )
        turn_record.update(result)
        assistant_text = result.get("assistant_text", "")
        st.session_state.history.append({"role": "user", "content": user_text})
        st.session_state.history.append({"role": "assistant", "content": assistant_text})
    except Exception as exc:
        turn_record.update(
            {
                "status": "provider_error",
                "assistant_text": "",
                "error": f"{type(exc).__name__}: {exc}",
            }
        )

    turn_record["ended_at"] = now_iso()
    st.session_state.turns.append(turn_record)
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)


# ============================================================
#  UI HELPERS
# ============================================================
STATUS_COLOR = {
    "ok": "status-ok",
    "completed": "status-ok",
    "error": "status-err",
    "provider_error": "status-err",
    "started": "status-wait",
}

STATUS_ICON = {
    "ok": "✅",
    "completed": "✅",
    "error": "❌",
    "provider_error": "❌",
    "started": "⏳",
}


def status_badge(status: str) -> str:
    cls = STATUS_COLOR.get(status, "status-wait")
    icon = STATUS_ICON.get(status, "•")
    label = status.replace("_", " ").title()
    return f'<span class="status-badge {cls}">{icon} {label}</span>'


def render_tool_call_card(call: dict, result: dict | None, index: int) -> None:
    """Card trực quan cho 1 tool call + result."""
    name = call.get("name", "unknown")
    args = call.get("args", {}) or {}

    result_payload = (result or {}).get("result") if result else None
    is_err = isinstance(result_payload, dict) and result_payload.get("error")
    status = "error" if is_err else ("ok" if result else "wait")

    st.markdown(
        f"""
        <div class="tool-card">
          <div class="head">
            <span class="name">🔧 {index}. {name}</span>
            {status_badge(status)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.caption("📥 Arguments")
        render_json_panel(args)
    with c2:
        if result is None:
            st.caption("📤 Result")
            st.info("Chưa có kết quả.")
        elif is_err:
            st.caption("📤 Error")
            st.error(result_payload.get("error"))
            st.caption("Chi tiết")
            render_json_panel(result)
        else:
            st.caption("📤 Result")
            render_json_panel(result)


def render_round_timeline(round_record: dict) -> None:
    """Timeline cho 1 round trong tool loop."""
    rnd = round_record.get("round", "?")
    tool_calls = round_record.get("tool_calls", []) or []
    tool_results = round_record.get("tool_results", []) or []

    st.markdown(
        f"""
        <div class="tl-item">
          <div class="tl-title">🔁 Round {rnd}</div>
          <div class="tl-sub">{len(tool_calls)} tool call(s)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    assistant_text = round_record.get("assistant_text")
    if assistant_text:
        st.caption("💭 Assistant text trước khi gọi tool")
        render_text_panel(assistant_text)

    if not tool_calls:
        st.info("Round này không có tool call.")
        return

    for i, call in enumerate(tool_calls, start=1):
        result = tool_results[i - 1] if i <= len(tool_results) else None
        render_tool_call_card(call, result, i)


# ============================================================
#  SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<div class="side-title">🛠️ IT Helpdesk Agent</div>', unsafe_allow_html=True)
    st.caption("Day 04 Lab — Model + Tool Loop")

    st.markdown('<div class="side-group">🤖 Model</div>', unsafe_allow_html=True)
    st.selectbox(
        "Provider",
        ["openrouter", "openai", "anthropic", "gemini"],
        key="provider",
        help="Nhà cung cấp LLM.",
    )
    st.text_input(
        "Model override",
        value="",
        key="model",
        placeholder="vd: openai/gpt-4o-mini",
        help="Để trống để dùng model mặc định của provider.",
    )

    st.markdown('<div class="side-group">📦 Artifacts</div>', unsafe_allow_html=True)
    st.text_input("Artifact label", value="v0", key="version")
    st.text_input("System prompt", value=str(DEFAULT_SYSTEM_PROMPT), key="system_prompt_path")
    st.text_input("Tools YAML", value=str(DEFAULT_TOOLS), key="tools_path")

    st.markdown('<div class="side-group">⚙️ Runtime</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        st.number_input("History window", min_value=0, max_value=20, value=5, key="history_window")
    with col_b:
        st.number_input("Max tool rounds", min_value=1, max_value=10, value=4, key="max_tool_rounds")
    st.text_input("Transcript folder", value=str(DEFAULT_TRANSCRIPTS_DIR), key="transcripts_dir")

    st.markdown("---")
    if st.button("✨ Bắt đầu transcript mới", use_container_width=True, type="primary"):
        start_new_transcript()
        st.rerun()


# ============================================================
#  ENSURE STATE
# ============================================================
ensure_state()
artifact = st.session_state.artifact
cfg = current_config()


# ============================================================
#  HERO HEADER
# ============================================================
st.markdown(
    f"""
    <div class="hero">
      <h1>💬 IT Helpdesk Agent Chat</h1>
      <p>Cùng một model/tool loop như <code>starter_v0/chat.py</code> — chỉ khác giao diện.</p>
      <div class="badges">
        <span class="pill">🏷️ {artifact.version}</span>
        <span class="pill">🧠 {cfg['provider']}{' · ' + cfg['model'] if cfg['model'] else ''}</span>
        <span class="pill mono">#{artifact.artifact_version[:12]}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")


# ============================================================
#  MAIN LAYOUT
# ============================================================
chat_col, trace_col = st.columns([0.62, 0.38], gap="large")


# ---------- CHAT COLUMN ----------
with chat_col:
    st.markdown(
        '<div class="section-title"><span class="dot"></span>Chat</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.turns:
        with st.container(border=True):
            st.markdown(
                """
                ### 👋 Xin chào!
                Hỏi mình về **VPN, Email, SSO, Wi-Fi, Printer, Asset diagnostics,
                Users, KB, Policy, Incident reports, Ticket creation**, hoặc
                **Public device info**.
                """
            )
            st.caption("💡 Gợi ý: *“Laptop của tôi không kết nối được VPN, kiểm tra giúp.”*")

    # Lịch sử chat
    for turn in st.session_state.turns:
        # User bubble
        st.markdown(
            f"""
            <div class="bubble-row user">
              <div class="avatar user">🧑</div>
              <div class="bubble user">{turn['user']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Assistant bubble
        if turn.get("status") == "provider_error":
            st.markdown(
                f"""
                <div class="bubble-row">
                  <div class="avatar bot">🤖</div>
                  <div class="bubble bot" style="border-color:#fecaca;">
                    <b style="color:#b91c1c;">Lỗi provider</b><br/>
                    <span style="font-size:.85rem;">{turn.get('error','')}</span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            payload = parse_assistant_payload(turn.get("assistant_text"))
            reply = payload.get("reply", "")
            meta_tags = []
            for key in ("intent", "action"):
                val = payload.get(key)
                if val:
                    meta_tags.append(f'<span class="tag">{key}: {val}</span>')
            ev = payload.get("evidence_ids") or []
            if ev:
                meta_tags.append(f'<span class="tag">evidence: {len(ev)}</span>')

            st.markdown(
                f"""
                <div class="bubble-row">
                  <div class="avatar bot">🤖</div>
                  <div class="bubble bot">
                    <div class="meta">{''.join(meta_tags)}</div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            # Nội dung reply (markdown) — render ngay dưới, canh lề với bubble
            with st.container():
                pad_l, body, _ = st.columns([0.07, 0.85, 0.08])
                with body:
                    if reply:
                        stream_this = st.session_state.get("stream_turn_index") == turn.get("turn_index")
                        if stream_this and reply:
                            st.write_stream(stream_words(reply))
                            st.session_state.stream_turn_index = None
                        else:
                            st.markdown(reply)

                    raw = payload.get("raw")
                    if raw and raw != reply:
                        with st.expander("🧾 Raw JSON response", expanded=False):
                            st.code(raw, language="json")

    # Ô nhập chat
    prompt = st.chat_input("Nhập yêu cầu helpdesk...")


# ---------- TRACE COLUMN ----------
with trace_col:
    st.markdown(
        '<div class="section-title"><span class="dot"></span>Tool Trace</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.caption("📁 Transcript")
        render_text_panel(str(st.session_state.transcript_path))
        st.caption("🔐 Artifact hashes")
        render_json_panel(
            {
                "artifact_version": artifact.artifact_version,
                "prompt_hash": artifact.prompt_hash,
                "tools_hash": artifact.tools_hash,
            }
        )

    if not st.session_state.turns:
        st.info("Tool calls, args, result/error, round và status sẽ hiện ở đây.")

    for turn in reversed(st.session_state.turns):
        status = turn.get("status", "unknown")
        icon = STATUS_ICON.get(status, "•")
        title = f"{icon} Turn {turn['turn_index']} · {status.replace('_',' ').title()}"

        with st.expander(title, expanded=(turn is st.session_state.turns[-1])):
            st.markdown(
                '<div class="tl-item"><div class="tl-title">🧑 User request</div></div>',
                unsafe_allow_html=True,
            )
            render_text_panel(turn["user"])

            if turn.get("error"):
                st.error(turn["error"])

            rounds = turn.get("rounds", []) or []
            if not rounds:
                st.info("Không có round trace nào được ghi.")
            else:
                st.markdown('<div class="timeline">', unsafe_allow_html=True)
                for r in rounds:
                    render_round_timeline(r)
                st.markdown("</div>", unsafe_allow_html=True)


# ============================================================
#  HANDLE PROMPT
# ============================================================
if prompt:
    with st.spinner("🤖 Đang chạy model và tools..."):
        append_turn(prompt)
    st.session_state.stream_turn_index = st.session_state.turns[-1]["turn_index"]
    st.rerun()
