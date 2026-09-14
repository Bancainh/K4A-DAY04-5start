from __future__ import annotations

import json
import sys
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
from tools import load_tool_declarations, to_openai_tools  # noqa: E402
from versioning import artifact_version_dict, build_artifact_version  # noqa: E402


st.set_page_config(
    page_title="IT Helpdesk Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


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
    system_prompt = read_system_prompt(st.session_state.system_prompt_path)
    tools = read_tools(st.session_state.tools_path)
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, st.session_state.history_window),
        {"role": "user", "content": user_text},
    ]

    turn_record: dict[str, Any] = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

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


def render_round(round_record: dict[str, Any]) -> None:
    st.markdown(f"**Round {round_record.get('round')}**")

    assistant_text = round_record.get("assistant_text")
    if assistant_text:
        st.caption("Assistant text before tool execution")
        st.code(assistant_text, language="text")

    tool_calls = round_record.get("tool_calls", [])
    tool_results = round_record.get("tool_results", [])
    if not tool_calls:
        st.info("No tool call in this round.")
        return

    for index, call in enumerate(tool_calls, start=1):
        st.caption(f"Tool call {index}: {call.get('name')}")
        st.code(json_text(call.get("args", {})), language="json")

        if index <= len(tool_results):
            result = tool_results[index - 1]
            result_payload = result.get("result")
            if isinstance(result_payload, dict) and result_payload.get("error"):
                st.error(f"Tool error: {result_payload.get('error')}")
            st.code(json_text(result), language="json")


with st.sidebar:
    st.title("IT Helpdesk Agent")
    st.caption("Chat UI for Day 04 Lab evidence.")

    st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"], key="provider")
    st.text_input("Model override", value="", key="model")
    st.text_input("Artifact label", value="v0", key="version")
    st.text_input("System prompt path", value=str(DEFAULT_SYSTEM_PROMPT), key="system_prompt_path")
    st.text_input("Tools YAML path", value=str(DEFAULT_TOOLS), key="tools_path")
    st.number_input("History window", min_value=0, max_value=20, value=5, key="history_window")
    st.number_input("Max tool rounds", min_value=1, max_value=10, value=4, key="max_tool_rounds")
    st.text_input("Transcript folder", value=str(DEFAULT_TRANSCRIPTS_DIR), key="transcripts_dir")

    if st.button("Start new transcript", use_container_width=True):
        start_new_transcript()

ensure_state()

artifact = st.session_state.artifact

header_left, header_right = st.columns([0.7, 0.3], vertical_alignment="center")
with header_left:
    st.title("IT Helpdesk Agent Chat")
    st.caption("Uses the same model/tool loop as `starter_v0/chat.py`.")
with header_right:
    st.metric("Artifact label", artifact.version)
    st.code(artifact.artifact_version, language="text")

chat_col, trace_col = st.columns([0.62, 0.38], gap="large")

with chat_col:
    st.subheader("Chat")

    if not st.session_state.turns:
        st.info(
            "Ask about VPN, email, SSO, Wi-Fi, printing, asset diagnostics, users, "
            "KB, policy, incident reports, ticket creation, or public device info."
        )

    for turn in st.session_state.turns:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            if turn.get("status") == "provider_error":
                st.error(turn.get("error", "Provider error"))
            else:
                st.write(turn.get("assistant_text") or "")

    prompt = st.chat_input("Type a helpdesk request...")

with trace_col:
    st.subheader("Tool Trace")
    st.caption(f"Transcript: `{st.session_state.transcript_path}`")

    with st.expander("Artifact version and hashes", expanded=True):
        st.code(
            json_text(
                {
                    "artifact_version": artifact.artifact_version,
                    "prompt_hash": artifact.prompt_hash,
                    "tools_hash": artifact.tools_hash,
                }
            ),
            language="json",
        )

    if not st.session_state.turns:
        st.info("Tool calls, args, result/error, round and status will appear here.")

    for turn in reversed(st.session_state.turns):
        title = f"Turn {turn['turn_index']} - {turn.get('status', 'unknown')}"
        with st.expander(title, expanded=turn is st.session_state.turns[-1]):
            st.caption("User request")
            st.code(turn["user"], language="text")

            if turn.get("error"):
                st.error(turn["error"])

            rounds = turn.get("rounds", [])
            if not rounds:
                st.info("No round trace was recorded.")
            for round_record in rounds:
                render_round(round_record)

if prompt:
    with st.spinner("Running model and tools..."):
        append_turn(prompt)
    st.rerun()
