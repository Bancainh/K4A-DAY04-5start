from __future__ import annotations

import argparse
import inspect
import json
import subprocess
from pathlib import Path
from typing import Any

from tools import TOOL_FUNCTIONS, load_tool_declarations


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOOLS = ROOT / "artifacts" / "tools.yaml"
SECRET_ENV_NAMES = {
    "OPENROUTER_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
    "TAVILY_API_KEY",
}


def finding(severity: str, check: str, message: str) -> dict[str, str]:
    return {"severity": severity, "check": check, "message": message}


def audit_tool_contracts(path: Path = DEFAULT_TOOLS) -> list[dict[str, str]]:
    declarations = load_tool_declarations(path)
    declared = {item["name"]: item for item in declarations}
    registered = set(TOOL_FUNCTIONS)
    findings: list[dict[str, str]] = []

    missing_implementations = sorted(set(declared) - registered)
    undeclared_implementations = sorted(registered - set(declared))
    if missing_implementations:
        findings.append(finding("error", "registry", f"Declared without implementation: {missing_implementations}"))
    if undeclared_implementations:
        findings.append(finding("error", "registry", f"Registered but not declared: {undeclared_implementations}"))

    for name in sorted(set(declared) & registered):
        schema_properties = set(declared[name].get("parameters", {}).get("properties", {}))
        implementation_parameters = set(inspect.signature(TOOL_FUNCTIONS[name]).parameters)
        if schema_properties != implementation_parameters:
            findings.append(
                finding(
                    "error",
                    "schema_signature",
                    f"{name}: schema={sorted(schema_properties)} implementation={sorted(implementation_parameters)}",
                )
            )

    ticket_description = str(declared.get("create_ticket", {}).get("description", "")).casefold()
    if not any(marker in ticket_description for marker in ("confirm", "xác nhận", "xac nhan")):
        findings.append(
            finding(
                "warning",
                "ticket_declaration",
                "create_ticket description does not state that it is a side-effecting action requiring explicit confirmation.",
            )
        )

    external_description = str(declared.get("search_device_info", {}).get("description", "")).casefold()
    required_external_markers = ("asset id", "employee id", "internal", "nội bộ")
    if not any(marker in external_description for marker in required_external_markers):
        findings.append(
            finding(
                "warning",
                "external_declaration",
                "search_device_info description does not clearly state the internal-data boundary.",
            )
        )
    return findings


def validate_run(path: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    try:
        run = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [finding("error", "run_json", f"{path}: {type(exc).__name__}: {exc}")]

    summary = run.get("summary") or {}
    total = summary.get("total_cases")
    measured = summary.get("measured_cases")
    provider_errors = summary.get("provider_error_cases")
    result_count = len(run.get("results") or [])
    if not isinstance(total, int) or total != result_count:
        findings.append(finding("error", "run_count", f"{path}: total_cases={total}, results={result_count}"))
    if provider_errors != 0:
        findings.append(finding("error", "provider_errors", f"{path}: provider_error_cases={provider_errors}"))
    if measured != total:
        findings.append(finding("error", "measured_cases", f"{path}: measured_cases={measured}, total_cases={total}"))
    for item in run.get("results") or []:
        for event in item.get("tool_results") or []:
            result = event.get("result") or {}
            if result.get("error"):
                findings.append(
                    finding(
                        "review",
                        "tool_result",
                        f"{path}:{item.get('id')}: {event.get('tool')} returned {result.get('error')}",
                    )
                )
    return findings


def audit_tracked_secret_files() -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    try:
        completed = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT.parent,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception as exc:
        return [finding("error", "git_files", f"Unable to inspect tracked files: {type(exc).__name__}: {exc}")]

    tracked = [line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()]
    forbidden = [
        name
        for name in tracked
        if name.endswith("/.env")
        or "/.env." in name and not name.endswith("/.env.example")
        or name.endswith("/tickets")
        or "/tickets/" in name
    ]
    if forbidden:
        findings.append(finding("error", "tracked_sensitive_paths", f"Forbidden tracked paths: {forbidden}"))

    example = ROOT / ".env.example"
    if example.exists():
        for line_number, raw_line in enumerate(example.read_text(encoding="utf-8").splitlines(), start=1):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            name, value = stripped.split("=", 1)
            if name.strip() in SECRET_ENV_NAMES and value.strip():
                findings.append(
                    finding("error", "env_example_secret", f".env.example:{line_number} has a non-empty {name.strip()} value")
                )
    return findings


def print_findings(title: str, findings: list[dict[str, str]]) -> None:
    print(f"\n{title}")
    if not findings:
        print("PASS: no findings")
        return
    for item in findings:
        print(f"{item['severity'].upper():<7} {item['check']}: {item['message']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit helpdesk tool contracts, tracked secrets, and run evidence.")
    parser.add_argument("--tools", type=Path, default=DEFAULT_TOOLS)
    parser.add_argument("--run", action="append", type=Path, default=[], help="Run JSON to validate; repeat as needed.")
    parser.add_argument("--strict-contracts", action="store_true", help="Treat contract warnings as gate failures.")
    args = parser.parse_args()

    contract_findings = audit_tool_contracts(args.tools)
    secret_findings = audit_tracked_secret_files()
    run_findings: list[dict[str, str]] = []
    for path in args.run:
        run_findings.extend(validate_run(path))

    print_findings("Tool contract audit", contract_findings)
    print_findings("Tracked secret/path audit", secret_findings)
    if args.run:
        print_findings("Run evidence audit", run_findings)

    all_findings = [*contract_findings, *secret_findings, *run_findings]
    failing_levels = {"error"}
    if args.strict_contracts:
        failing_levels.add("warning")
    if any(item["severity"] in failing_levels for item in all_findings):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
