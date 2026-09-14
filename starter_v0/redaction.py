from __future__ import annotations

import re
from typing import Any


SENSITIVE_KEY = re.compile(
    r"^(?:password|passwd|token|access_token|api_key|api-key|mfa|otp|recovery_code|recovery-code)$",
    re.IGNORECASE,
)
INLINE_SECRET = re.compile(
    r"\b(password|passwd|access[ _-]?token|token|api[ _-]?key|mfa|otp|recovery[ _-]?code)"
    r"(\s*(?:[:=]|\bis\b|\blà\b|\bla\b)\s*)"
    r"([^\s,;}\"]+)",
    re.IGNORECASE,
)


def contains_sensitive_data(text: str) -> bool:
    return bool(INLINE_SECRET.search(text or ""))


def redact_text(text: str) -> str:
    return INLINE_SECRET.sub(lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]", text or "")


def sanitize_for_logging(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if SENSITIVE_KEY.fullmatch(str(key)) else sanitize_for_logging(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize_for_logging(item) for item in value]
    if isinstance(value, tuple):
        return tuple(sanitize_for_logging(item) for item in value)
    if isinstance(value, str):
        return redact_text(value)
    return value
