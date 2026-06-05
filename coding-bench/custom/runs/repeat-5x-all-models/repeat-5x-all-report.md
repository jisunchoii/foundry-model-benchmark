# 5x repeat custom coding eval - all models

## Summary by model

| Model | Passed | Calls | Pass rate | Avg latency | P50 | P95 | Latency stdev | Est. token cost | Est. cost/pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-opus-4.8-adb | 50 | 50 | 100.0% | 7.9s | 7.657s | 10.225s | 1.725s | $0.551025 | $0.011020 |
| gpt-5.5-foundry | 50 | 50 | 100.0% | 8.674s | 7.429s | 14.484s | 3.313s | $0.760830 | $0.015217 |
| grok-4.3-foundry | 50 | 50 | 100.0% | 18.54s | 19.465s | 28.399s | 5.907s | $0.219525 | $0.004391 |
| glm-5.1-foundry | 46 | 50 | 92.0% | 19.959s | 19.997s | 34.116s | 10.871s | $0.261884 | $0.005693 |
| kimi-k2.6-foundry | 38 | 50 | 76.0% | 25.003s | 20.555s | 46.272s | 16.037s | $0.371297 | $0.009771 |
| minimax-m2.5-foundry | 36 | 50 | 72.0% | 10.337s | 9.417s | 15.342s | 3.223s | $0.059045 | $0.001640 |

## Task stability

| Model | Task | Passed | Total | Pass rate | Avg latency | Failed repeats |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| claude-opus-4.8-adb | cart_discount | 5 | 5 | 100% | 6.95s | - |
| claude-opus-4.8-adb | html_accessible_form | 5 | 5 | 100% | 7.47s | - |
| claude-opus-4.8-adb | interval_merge | 5 | 5 | 100% | 7.21s | - |
| claude-opus-4.8-adb | json_patch | 5 | 5 | 100% | 9.50s | - |
| claude-opus-4.8-adb | log_redaction | 5 | 5 | 100% | 8.90s | - |
| claude-opus-4.8-adb | markdown_toc | 5 | 5 | 100% | 8.76s | - |
| claude-opus-4.8-adb | package_stats | 5 | 5 | 100% | 9.23s | - |
| claude-opus-4.8-adb | py_slugify | 5 | 5 | 100% | 6.44s | - |
| claude-opus-4.8-adb | rate_limiter | 5 | 5 | 100% | 7.25s | - |
| claude-opus-4.8-adb | sql_builder | 5 | 5 | 100% | 7.30s | - |
| glm-5.1-foundry | cart_discount | 5 | 5 | 100% | 14.25s | - |
| glm-5.1-foundry | html_accessible_form | 5 | 5 | 100% | 5.79s | - |
| glm-5.1-foundry | interval_merge | 5 | 5 | 100% | 9.56s | - |
| glm-5.1-foundry | json_patch | 5 | 5 | 100% | 22.82s | - |
| glm-5.1-foundry | log_redaction | 5 | 5 | 100% | 24.05s | - |
| glm-5.1-foundry | markdown_toc | 1 | 5 | 20% | 26.00s | 1, 3, 4, 5 |
| glm-5.1-foundry | package_stats | 5 | 5 | 100% | 22.73s | - |
| glm-5.1-foundry | py_slugify | 5 | 5 | 100% | 31.91s | - |
| glm-5.1-foundry | rate_limiter | 5 | 5 | 100% | 14.84s | - |
| glm-5.1-foundry | sql_builder | 5 | 5 | 100% | 27.63s | - |
| gpt-5.5-foundry | cart_discount | 5 | 5 | 100% | 6.00s | - |
| gpt-5.5-foundry | html_accessible_form | 5 | 5 | 100% | 5.05s | - |
| gpt-5.5-foundry | interval_merge | 5 | 5 | 100% | 5.25s | - |
| gpt-5.5-foundry | json_patch | 5 | 5 | 100% | 13.31s | - |
| gpt-5.5-foundry | log_redaction | 5 | 5 | 100% | 11.84s | - |
| gpt-5.5-foundry | markdown_toc | 5 | 5 | 100% | 12.32s | - |
| gpt-5.5-foundry | package_stats | 5 | 5 | 100% | 7.59s | - |
| gpt-5.5-foundry | py_slugify | 5 | 5 | 100% | 10.94s | - |
| gpt-5.5-foundry | rate_limiter | 5 | 5 | 100% | 7.22s | - |
| gpt-5.5-foundry | sql_builder | 5 | 5 | 100% | 7.21s | - |
| grok-4.3-foundry | cart_discount | 5 | 5 | 100% | 10.17s | - |
| grok-4.3-foundry | html_accessible_form | 5 | 5 | 100% | 9.62s | - |
| grok-4.3-foundry | interval_merge | 5 | 5 | 100% | 14.39s | - |
| grok-4.3-foundry | json_patch | 5 | 5 | 100% | 21.70s | - |
| grok-4.3-foundry | log_redaction | 5 | 5 | 100% | 20.58s | - |
| grok-4.3-foundry | markdown_toc | 5 | 5 | 100% | 30.08s | - |
| grok-4.3-foundry | package_stats | 5 | 5 | 100% | 20.90s | - |
| grok-4.3-foundry | py_slugify | 5 | 5 | 100% | 22.17s | - |
| grok-4.3-foundry | rate_limiter | 5 | 5 | 100% | 17.45s | - |
| grok-4.3-foundry | sql_builder | 5 | 5 | 100% | 18.33s | - |
| kimi-k2.6-foundry | cart_discount | 4 | 5 | 80% | 25.78s | 5 |
| kimi-k2.6-foundry | html_accessible_form | 5 | 5 | 100% | 19.79s | - |
| kimi-k2.6-foundry | interval_merge | 5 | 5 | 100% | 17.46s | - |
| kimi-k2.6-foundry | json_patch | 5 | 5 | 100% | 26.78s | - |
| kimi-k2.6-foundry | log_redaction | 1 | 5 | 20% | 31.57s | 1, 2, 3, 4 |
| kimi-k2.6-foundry | markdown_toc | 2 | 5 | 40% | 32.12s | 1, 4, 5 |
| kimi-k2.6-foundry | package_stats | 3 | 5 | 60% | 39.72s | 3, 5 |
| kimi-k2.6-foundry | py_slugify | 3 | 5 | 60% | 26.79s | 3, 4 |
| kimi-k2.6-foundry | rate_limiter | 5 | 5 | 100% | 12.40s | - |
| kimi-k2.6-foundry | sql_builder | 5 | 5 | 100% | 17.63s | - |
| minimax-m2.5-foundry | cart_discount | 5 | 5 | 100% | 8.81s | - |
| minimax-m2.5-foundry | html_accessible_form | 5 | 5 | 100% | 6.35s | - |
| minimax-m2.5-foundry | interval_merge | 5 | 5 | 100% | 10.04s | - |
| minimax-m2.5-foundry | json_patch | 1 | 5 | 20% | 10.83s | 1, 3, 4, 5 |
| minimax-m2.5-foundry | log_redaction | 5 | 5 | 100% | 10.54s | - |
| minimax-m2.5-foundry | markdown_toc | 0 | 5 | 0% | 9.96s | 1, 2, 3, 4, 5 |
| minimax-m2.5-foundry | package_stats | 5 | 5 | 100% | 12.38s | - |
| minimax-m2.5-foundry | py_slugify | 5 | 5 | 100% | 8.10s | - |
| minimax-m2.5-foundry | rate_limiter | 1 | 5 | 20% | 9.46s | 1, 3, 4, 5 |
| minimax-m2.5-foundry | sql_builder | 4 | 5 | 80% | 16.89s | 2 |

## Pricing notes

계산식·단가·해석은 [`cost-report.md`](./cost-report.md), 원본 수치는 [`cost-estimates.csv`](./cost-estimates.csv) 참고.

- `claude-opus-4.8-adb`: Anthropic public token pricing equivalent; ADB contract may differ.
- `glm-5.1-foundry`: Z.AI/Fireworks official pricing equivalent; Azure Foundry/Fireworks public numeric price not exposed.
- `gpt-5.5-foundry`: OpenAI public API equivalent; Azure run used PTU-hour billing.
- `grok-4.3-foundry`: xAI official public token pricing equivalent.
- `kimi-k2.6-foundry`: Kimi official API pricing equivalent; Azure Foundry public numeric price not exposed.
- `minimax-m2.5-foundry`: MiniMax official API pricing equivalent; Azure Foundry/Fireworks public numeric price not exposed.

## Failures

| Group | Repeat | Model | Task | Error | Exit |
| --- | ---: | --- | --- | --- | ---: |
| repeat-5x-remaining | 1 | kimi-k2.6-foundry | log_redaction | Expecting value: line 1 column 1 (char 0) | -1 |
| repeat-5x-remaining | 1 | kimi-k2.6-foundry | markdown_toc | Expecting value: line 1 column 1 (char 0) | -1 |
| repeat-5x-remaining | 1 | minimax-m2.5-foundry | json_patch |  | 1 |
| repeat-5x-remaining | 1 | minimax-m2.5-foundry | markdown_toc |  | 1 |
| repeat-5x-remaining | 1 | minimax-m2.5-foundry | rate_limiter |  | 1 |
| repeat-5x-remaining | 1 | glm-5.1-foundry | markdown_toc |  | 1 |
| repeat-5x-remaining | 2 | kimi-k2.6-foundry | log_redaction | Expecting value: line 1 column 1 (char 0) | -1 |
| repeat-5x-remaining | 2 | minimax-m2.5-foundry | markdown_toc |  | 1 |
| repeat-5x-remaining | 2 | minimax-m2.5-foundry | sql_builder |  | 1 |
| repeat-5x-remaining | 3 | kimi-k2.6-foundry | log_redaction | Expecting value: line 1 column 1 (char 0) | -1 |
| repeat-5x-remaining | 3 | kimi-k2.6-foundry | package_stats | Expecting value: line 1 column 1 (char 0) | -1 |
| repeat-5x-remaining | 3 | kimi-k2.6-foundry | py_slugify | HTTP 400 from https://<foundry-account-eastus2>.cognitiveservices.azure.com/openai/deployments/Kimi-K2.6-1/chat/completions?api-version=2025-04-01-preview: {"id":"b4b5518bee0345c385d847204dc3e258","model":"Kimi-K2.6","choices":[{"index":0,"message":{"role":"assistant","content":""},"finish_reason":"content_filter","content_filter_results":{"error":{"code":"content_filter","message":"ResponsibleAI result indicated block action."}}}],"usage":{"prompt_tokens":317,"completion_tokens":779,"total_tokens":1096},"created":1780377244,"object":"chat.completion","prompt_filter_results":null} | -1 |
| repeat-5x-remaining | 3 | minimax-m2.5-foundry | json_patch |  | 1 |
| repeat-5x-remaining | 3 | minimax-m2.5-foundry | markdown_toc |  | 1 |
| repeat-5x-remaining | 3 | minimax-m2.5-foundry | rate_limiter |  | 1 |
| repeat-5x-remaining | 3 | glm-5.1-foundry | markdown_toc |  | 1 |
| repeat-5x-remaining | 4 | kimi-k2.6-foundry | log_redaction | Expecting value: line 1 column 1 (char 0) | -1 |
| repeat-5x-remaining | 4 | kimi-k2.6-foundry | markdown_toc | Expecting value: line 1 column 1 (char 0) | -1 |
| repeat-5x-remaining | 4 | kimi-k2.6-foundry | py_slugify | Expecting value: line 1 column 1 (char 0) | -1 |
| repeat-5x-remaining | 4 | minimax-m2.5-foundry | json_patch |  | 1 |
| repeat-5x-remaining | 4 | minimax-m2.5-foundry | markdown_toc |  | 1 |
| repeat-5x-remaining | 4 | minimax-m2.5-foundry | rate_limiter |  | 1 |
| repeat-5x-remaining | 4 | glm-5.1-foundry | markdown_toc |  | 1 |
| repeat-5x-remaining | 5 | kimi-k2.6-foundry | cart_discount | Expecting value: line 1 column 1 (char 0) | -1 |
| repeat-5x-remaining | 5 | kimi-k2.6-foundry | markdown_toc | Expecting value: line 1 column 1 (char 0) | -1 |
| repeat-5x-remaining | 5 | kimi-k2.6-foundry | package_stats | Expecting value: line 1 column 1 (char 0) | -1 |
| repeat-5x-remaining | 5 | minimax-m2.5-foundry | json_patch |  | 1 |
| repeat-5x-remaining | 5 | minimax-m2.5-foundry | markdown_toc |  | 1 |
| repeat-5x-remaining | 5 | minimax-m2.5-foundry | rate_limiter |  | 1 |
| repeat-5x-remaining | 5 | glm-5.1-foundry | markdown_toc |  | 1 |
