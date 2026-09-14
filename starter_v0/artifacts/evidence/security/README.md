# Security evidence index

All evidence here uses fictional lab inputs. No API key is stored in these files.

| File | Purpose |
|---|---|
| `qa-security-final_B_adversarial_openai_20260914T184856684663.json` | Final fixed 12-case adversarial run after runtime guardrail and log redaction |
| `qa-security-final-analysis.csv` | Flat per-case view of the final adversarial run |
| `qa-security-guardrail-v2_B_extension_openai_20260914T184526236026.json` | Positive regression run for policy, confirmed ticket, and public web search paths |
| `qa-security-guardrail-v2-extension-analysis.csv` | Flat per-case view of the extension run |
| `chat-smoke/*.transcript.json` | Credential-like input blocked locally and redacted before provider execution |

The final adversarial metric remains an agent-decision score, not a containment
score. A case can fail because the model selected a dangerous tool even when the
runtime guardrail prevented the side effect. Review both `result` and `tool_results`.
