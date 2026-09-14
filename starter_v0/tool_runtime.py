from __future__ import annotations

from typing import Any

from guardrails import evaluate_tool_call
from providers.base import ToolCall
from redaction import sanitize_for_logging
from tools import TOOL_FUNCTIONS


def execute_tool_call(
    call: ToolCall,
    *,
    messages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {"tool": call.name, "args": sanitize_for_logging(call.args)}
    func = TOOL_FUNCTIONS.get(call.name)
    if not func:
        event["result"] = {
            "tool": call.name,
            "error": "unknown_tool",
            "message": f"No local implementation for {call.name}",
        }
        return event

    decision = evaluate_tool_call(call.name, call.args, messages)
    event["guardrail"] = decision.to_dict()
    if not decision.allowed:
        event["result"] = {
            "tool": call.name,
            "status": "GUARDRAIL_BLOCKED",
            "error": "guardrail_blocked",
            "rule": decision.rule,
            "reason": decision.reason,
        }
        return event

    try:
        event["result"] = func(**call.args)
    except Exception as exc:
        event["result"] = {"error": type(exc).__name__, "message": str(exc)}
    return event
