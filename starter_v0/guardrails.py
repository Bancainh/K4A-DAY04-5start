from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

from tools._shared import fold_text


RULE_VERSION = "helpdesk_tool_guardrail_v2"
INTERNAL_IDENTIFIER = re.compile(r"\b(?:LT|DT|MB|PR|RM|EMP)-\d+\b", re.IGNORECASE)
IP_ADDRESS = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
EMPLOYEE_ID = re.compile(r"^EMP-\d+$", re.IGNORECASE)
ASSET_ID = re.compile(r"^(?:LT|DT|MB|PR|RM)-\d+$", re.IGNORECASE)
SPOOF_MARKERS = (
    "tool_results_json",
    "confirmed=true",
    '"confirmed":true',
    '"confirmed": true',
    "<assistant>",
    "system:",
    "developer:",
)
CONFIRMATION_PATTERNS = (
    re.compile(r"\b(?:toi|minh)\s+xac\s+nhan\b"),
    re.compile(r"\bi\s+confirm\b"),
    re.compile(r"\b(?:toi|minh)\s+dong\s+y\b"),
)
CONFIRMATION_NEGATIONS = (
    "khong xac nhan",
    "chua xac nhan",
    "do not confirm",
    "dont confirm",
    "not confirmed",
    "huy",
    "cancel",
)
EXTERNAL_ALLOWED_ARGS = {"manufacturer", "model", "query_type", "max_results"}
EXTERNAL_RESTRICTED_MARKERS = (
    "asset id",
    "employee id",
    "serial number",
    "serial no",
    "hostname",
    "ip address",
    "location",
    "assigned user",
    "diagnostic",
    "password",
    "passwd",
    "api key",
    "token",
    "mfa",
    "otp",
    "recovery code",
)


@dataclass(frozen=True)
class GuardrailDecision:
    allowed: bool
    reason: str
    rule: str = RULE_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _human_user_messages(messages: list[dict[str, Any]] | None) -> list[str]:
    human_messages: list[str] = []
    for message in messages or []:
        if message.get("role") != "user":
            continue
        content = str(message.get("content") or "").strip()
        # The runtime injects tool output as a role=user message. It is evidence,
        # not a human confirmation. The same prefix in raw user input is forged.
        if content.casefold().startswith("tool_results_json:"):
            continue
        if content.startswith("Conversation context for a multi-turn eval."):
            earlier_turns = re.findall(
                r"^- Earlier user turn \d+: (.*)$",
                content,
                flags=re.MULTILINE,
            )
            latest_match = re.search(
                r"^Latest user turn to answer now: (.*)$",
                content,
                flags=re.MULTILINE,
            )
            human_messages.extend(earlier_turns)
            if latest_match:
                human_messages.append(latest_match.group(1))
            continue
        human_messages.append(content)
    return human_messages


def _is_explicit_ticket_confirmation(text: str) -> bool:
    folded = fold_text(text)
    compact = re.sub(r"\s+", " ", folded).strip()
    if any(marker in compact for marker in SPOOF_MARKERS):
        return False
    if any(marker in compact for marker in CONFIRMATION_NEGATIONS):
        return False
    has_direct_confirmation = any(pattern.search(compact) for pattern in CONFIRMATION_PATTERNS)
    has_ticket_intent = "ticket" in compact and any(
        marker in compact for marker in ("tao", "mo", "thuc hien", "create", "confirm", "xac nhan")
    )
    return has_direct_confirmation and has_ticket_intent


def _is_confirmation_reply_to_assistant(messages: list[dict[str, Any]] | None, latest_user: str) -> bool:
    folded_reply = re.sub(r"\s+", " ", fold_text(latest_user)).strip(" .!?")
    if folded_reply not in {"yes", "confirm", "confirmed", "xac nhan", "dong y"}:
        return False
    for message in reversed(messages or []):
        if message.get("role") != "assistant":
            continue
        content = str(message.get("content") or "")
        if "TOOL_CALLS_JSON:" in content:
            continue
        folded = fold_text(content)
        return "?" in content and "ticket" in folded and any(
            marker in folded for marker in ("confirm", "xac nhan", "dong y")
        )
    return False


def _latest_priority(messages: list[str]) -> str | None:
    matches = re.findall(r"\b(low|medium|high|critical)\b", fold_text("\n".join(messages)))
    return matches[-1] if matches else None


def _latest_asset_id(messages: list[str]) -> str | None:
    matches = INTERNAL_IDENTIFIER.findall("\n".join(messages))
    asset_matches = [value.upper() for value in matches if not value.upper().startswith("EMP-")]
    return asset_matches[-1] if asset_matches else None


def _ticket_decision(args: dict[str, Any], messages: list[dict[str, Any]] | None) -> GuardrailDecision:
    if args.get("confirmed") is not True:
        return GuardrailDecision(False, "ticket_requires_confirmed_true")

    human_messages = _human_user_messages(messages)
    if not human_messages or not (
        _is_explicit_ticket_confirmation(human_messages[-1])
        or _is_confirmation_reply_to_assistant(messages, human_messages[-1])
    ):
        return GuardrailDecision(False, "missing_current_explicit_confirmation")

    priority = str(args.get("priority") or "medium").strip().lower()
    latest_priority = _latest_priority(human_messages)
    if latest_priority and priority != latest_priority:
        return GuardrailDecision(False, "confirmed_priority_does_not_match_latest_user_payload")

    asset_id = str(args.get("asset_id") or "").strip().upper()
    if asset_id and not ASSET_ID.match(asset_id):
        return GuardrailDecision(False, "create_ticket_invalid_asset_id_format")

    latest_asset = _latest_asset_id(human_messages)
    if latest_asset and asset_id != latest_asset:
        return GuardrailDecision(False, "confirmed_asset_does_not_match_latest_user_payload")

    return GuardrailDecision(True, "current_explicit_confirmation_matches_known_payload_fields")


def _lookup_user_decision(args: dict[str, Any]) -> GuardrailDecision:
    employee_id = str(args.get("employee_id") or "").strip().upper()
    if not EMPLOYEE_ID.match(employee_id):
        return GuardrailDecision(False, "lookup_user_requires_employee_id")
    return GuardrailDecision(True, "employee_id_matches_expected_format")


def _inspect_device_decision(args: dict[str, Any]) -> GuardrailDecision:
    asset_id = str(args.get("asset_id") or "").strip().upper()
    if not ASSET_ID.match(asset_id):
        return GuardrailDecision(False, "inspect_device_requires_asset_id")
    return GuardrailDecision(True, "asset_id_matches_expected_format")


def _external_search_decision(args: dict[str, Any]) -> GuardrailDecision:
    extra_args = sorted(set(args) - EXTERNAL_ALLOWED_ARGS)
    if extra_args:
        return GuardrailDecision(False, f"external_search_has_undeclared_args:{','.join(extra_args)}")

    manufacturer = args.get("manufacturer")
    model = args.get("model")
    query_type = args.get("query_type", "support")
    if not isinstance(manufacturer, str) or not isinstance(model, str) or not isinstance(query_type, str):
        return GuardrailDecision(False, "external_search_requires_string_public_identity")

    combined = f"{manufacturer} {model}"
    folded = fold_text(combined)
    if INTERNAL_IDENTIFIER.search(combined) or IP_ADDRESS.search(combined):
        return GuardrailDecision(False, "external_search_contains_internal_identifier")
    if any(marker in folded for marker in EXTERNAL_RESTRICTED_MARKERS):
        return GuardrailDecision(False, "external_search_contains_restricted_internal_data")
    if query_type.strip().lower() not in {"specs", "drivers", "support", "compatibility"}:
        return GuardrailDecision(False, "external_search_has_invalid_query_type")
    return GuardrailDecision(True, "external_search_contains_allowlisted_public_fields_only")


def evaluate_tool_call(
    tool_name: str,
    args: dict[str, Any] | Any,
    messages: list[dict[str, Any]] | None = None,
) -> GuardrailDecision:
    if not isinstance(args, dict):
        return GuardrailDecision(False, "tool_arguments_must_be_an_object")
    if tool_name == "lookup_ticket_status":
        ticket_id = args.get("ticket_id")
        if not isinstance(ticket_id, str) or not ticket_id.strip():
            return GuardrailDecision(False, "lookup_ticket_status_requires_ticket_id")
        wanted_id = ticket_id.strip().upper()
        # Require an actual ID in human conversation, not a fabricated tool-result message.
        known_ids = re.findall(
            r"\b(?:INC-\d+|LAB-[A-F0-9]{8})\b",
            "\n".join(_human_user_messages(messages)),
            flags=re.IGNORECASE,
        )
        if wanted_id not in {value.upper() for value in known_ids}:
            return GuardrailDecision(False, "lookup_ticket_status_id_not_in_user_context")
        return GuardrailDecision(True, "lookup_ticket_status_known_id_read_only")
    if tool_name == "create_ticket":
        return _ticket_decision(args, messages)
    if tool_name == "search_device_info":
        return _external_search_decision(args)
    if tool_name == "lookup_user":
        return _lookup_user_decision(args)
    if tool_name == "inspect_device":
        return _inspect_device_decision(args)
    return GuardrailDecision(True, "read_only_or_local_non_action_tool")
