# QA and Security Checks

Run these commands from `starter_v0/` with the repository virtual environment.

```powershell
$env:PYTHONUTF8='1'
.\.venv\Scripts\python.exe -m unittest discover -s qa -v
.\.venv\Scripts\python.exe -m qa.security_gate
```

Validate a live run before citing its metrics:

```powershell
.\.venv\Scripts\python.exe -m qa.security_gate --run artifacts\evidence\security\<run-file>.json
```

The gate checks declaration/registry/signature consistency, tracked secret paths,
placeholder-only `.env.example` values, provider errors, measured-case counts, and
tool errors that require manual review. Warnings identify work for another artifact
owner; `--strict-contracts` turns those warnings into a failing exit code.

The runtime guardrail is implemented in `guardrails.py` and is called through
`tool_runtime.py` immediately before tool execution. `redaction.py` sanitizes logged
arguments and transcript content; the interactive chat blocks credential-like input
before calling the model provider.
