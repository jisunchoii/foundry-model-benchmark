# First-pass coding benchmark report

## Model summary

| Model | Passed | Total | Pass rate | Avg latency (s) | Failed tasks |
| --- | ---: | ---: | ---: | ---: | --- |
| claude-opus-4.8-adb | 10 | 10 | 100% | 6.90 | - |
| glm-5.1-foundry | 8 | 10 | 80% | 17.29 | log_redaction, markdown_toc |
| gpt-5.5-foundry | 10 | 10 | 100% | 7.12 | - |
| grok-4.3-foundry | 10 | 10 | 100% | 18.41 | - |
| kimi-k2.6-foundry | 8 | 10 | 80% | 24.63 | json_patch, log_redaction |
| minimax-m2.5-foundry | 6 | 10 | 60% | 26.65 | log_redaction, markdown_toc, rate_limiter, sql_builder |

## Task summary

| Task | Passed models | Failed models |
| --- | --- | --- |
| cart_discount | gpt-5.5-foundry, kimi-k2.6-foundry, grok-4.3-foundry, minimax-m2.5-foundry, glm-5.1-foundry, claude-opus-4.8-adb | - |
| html_accessible_form | gpt-5.5-foundry, kimi-k2.6-foundry, grok-4.3-foundry, minimax-m2.5-foundry, glm-5.1-foundry, claude-opus-4.8-adb | - |
| interval_merge | gpt-5.5-foundry, kimi-k2.6-foundry, grok-4.3-foundry, minimax-m2.5-foundry, glm-5.1-foundry, claude-opus-4.8-adb | - |
| json_patch | gpt-5.5-foundry, grok-4.3-foundry, minimax-m2.5-foundry, glm-5.1-foundry, claude-opus-4.8-adb | kimi-k2.6-foundry |
| log_redaction | gpt-5.5-foundry, grok-4.3-foundry, claude-opus-4.8-adb | kimi-k2.6-foundry, minimax-m2.5-foundry, glm-5.1-foundry |
| markdown_toc | gpt-5.5-foundry, kimi-k2.6-foundry, grok-4.3-foundry, claude-opus-4.8-adb | minimax-m2.5-foundry, glm-5.1-foundry |
| package_stats | gpt-5.5-foundry, kimi-k2.6-foundry, grok-4.3-foundry, minimax-m2.5-foundry, glm-5.1-foundry, claude-opus-4.8-adb | - |
| py_slugify | gpt-5.5-foundry, kimi-k2.6-foundry, grok-4.3-foundry, minimax-m2.5-foundry, glm-5.1-foundry, claude-opus-4.8-adb | - |
| rate_limiter | gpt-5.5-foundry, kimi-k2.6-foundry, grok-4.3-foundry, glm-5.1-foundry, claude-opus-4.8-adb | minimax-m2.5-foundry |
| sql_builder | gpt-5.5-foundry, kimi-k2.6-foundry, grok-4.3-foundry, glm-5.1-foundry, claude-opus-4.8-adb | minimax-m2.5-foundry |

## Deployment notes

- GPT-5.5 GlobalStandard had quota limit 0 in checked regions, so it was deployed successfully as GlobalProvisionedManaged on `<foundry-account-eastus>` with deployment `bench-gpt-55`.
- Grok 4.3 was deployed on `<foundry-account-eastus2>` as `bench-grok-43`.
- GLM-5 was deprecated as of 2026-05-29, so the benchmark used deployed fallback `FW-GLM-5.1` as `bench-glm-51`.
- Existing Kimi K2.6 and MiniMax M2.5 deployments were reused.
- Claude Opus 4.8 used the Databricks serving endpoint `databricks-claude-opus-4-8`.
- No existing model deployments were deleted.
