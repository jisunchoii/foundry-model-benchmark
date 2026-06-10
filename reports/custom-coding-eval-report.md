# Custom coding eval report

## Purpose

Rather than reproducing a full public benchmark, this compares how reliably the models actually callable from Microsoft Foundry solve small coding tasks.

This evaluation does not replace public benchmarks such as SWE-bench, Aider Polyglot, or LiveCodeBench. It is an internal pilot that looks at per-model stability, latency, and cost trends under the same prompt/grader/repetition conditions.

## Method

| Item | Detail |
| --- | --- |
| Tasks | 10 |
| Repetitions | 5 reps across all models |
| Total calls | 350 (7 models × 10 tasks × 5 reps) |
| Grading | Pass/fail against each task's Python unittest or deterministic validator |
| Result location | Local `coding-bench\custom\runs\repeat-5x-all-models` (DeepSeek under `runs\deepseek-5x`) |

### Task list

| Task | Description |
| --- | --- |
| `py_slugify` | Slug generation handling whitespace/punctuation/underscores |
| `cart_discount` | Quantity, gift-card exclusion, conditional discount/tax calculation |
| `json_patch` | add/replace/remove JSON Patch subset |
| `markdown_toc` | H2/H3 TOC and GitHub-style anchors |
| `log_redaction` | email/token/API key/card masking |
| `interval_merge` | Interval merging |
| `rate_limiter` | per-key fixed-window limiter |
| `sql_builder` | identifier validation + parameterized SELECT |
| `html_accessible_form` | accessible login form |
| `package_stats` | mean/median/percentile implementation |

## 5-rep results

| Model | Passes | Total calls | Pass rate | Avg latency | P50 | P95 | Estimated token cost | Estimated cost per pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek-V4-Pro Foundry | 50 | 50 | 100.0% | 6.24s | 4.410s | 16.323s | $0.073959 | $0.001479 |
| Claude Opus 4.8 ADB | 50 | 50 | 100.0% | 7.90s | 7.657s | 10.225s | $0.551025 | $0.011020 |
| GPT-5.5 Foundry | 50 | 50 | 100.0% | 8.674s | 7.429s | 14.484s | $0.760830 | $0.015217 |
| Grok 4.3 Foundry | 50 | 50 | 100.0% | 18.54s | 19.465s | 28.399s | $0.219525 | $0.004391 |
| GLM-5.1 Foundry | 46 | 50 | 92.0% | 19.959s | 19.997s | 34.116s | $0.261884 | $0.005693 |
| Kimi K2.6 Foundry | 38 | 50 | 76.0% | 25.003s | 20.555s | 46.272s | $0.371297 | $0.009771 |
| MiniMax M2.5 Foundry | 36 | 50 | 72.0% | 10.337s | 9.417s | 15.342s | $0.059045 | $0.001640 |

> Cost = `prompt_tokens × input price + completion_tokens × output price` (per-model $/1M pricing applied). Cost per pass = estimated token cost ÷ number of passes.

## Task stability

| Model | Tasks with concentrated instability/failures |
| --- | --- |
| DeepSeek-V4-Pro Foundry | None |
| Claude Opus 4.8 ADB | None |
| GPT-5.5 Foundry | None |
| Grok 4.3 Foundry | None |
| GLM-5.1 Foundry | `markdown_toc` |
| Kimi K2.6 Foundry | `log_redaction`, `markdown_toc`, `package_stats`, `py_slugify`, `cart_discount` |
| MiniMax M2.5 Foundry | `markdown_toc`, `json_patch`, `rate_limiter`, `sql_builder` |

## Interpretation against public benchmarks

Public coding benchmarks typically use a larger problem set, a different harness, and a different test-time compute policy. The ranking from this custom eval should therefore not be read as a public-leaderboard ranking.

| Comparison | How it differs from this custom eval |
| --- | --- |
| SWE-bench Verified/Lite | An agentic patch benchmark requiring edits across a whole repository that must pass the official tests |
| LiveCodeBench | Algorithm/coding-problem focused |
| Aider Polyglot | Centered on the Aider scaffold and multi-language edit tasks |
| This custom eval | Evaluates small deterministic unit-test tasks via single-response/file generation |

Where this custom eval diverges from public-benchmark expectations:

- Kimi K2.6 and MiniMax M2.5 are reported as strong on public coding benchmarks, but were unstable on output formatting and certain deterministic tasks here.
- Grok 4.3 had limited public numeric coding benchmarks, but was stable here at 50/50.
- Claude Opus 4.8 and GPT-5.5 were the most reliable on small unit-test-style tasks.
- DeepSeek-V4-Pro was flawless at 50/50 (100%) and was **the fastest of all models at 6.24s average latency** (it doesn't bill reasoning tokens separately, so output is lightweight too). That said, some calls showed latency variance (P95 16.3s, 6.6s std-dev).
- GLM-5.1 was generally solid but repeatedly failed on tasks with many fine-grained rules, such as markdown anchors.

## Conclusion

On small code generation/editing tasks, **DeepSeek-V4-Pro, Claude Opus 4.8, GPT-5.5, and Grok 4.3** all top the list at a 100% pass rate, and among them **DeepSeek-V4-Pro is the fastest by average latency**. These results alone, however, should not be used to judge SWE-bench-style repository-patch performance — those are covered in a separate report (over the full set of 500, the order is Kimi > DeepSeek > MiniMax > Grok > GLM — see the [Verified report](./swe-bench-verified-500-report.md)).
