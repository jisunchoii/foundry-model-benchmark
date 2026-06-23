# Microsoft Foundry Model Coding Benchmark

A coding-performance evaluation that compares the models callable from Microsoft Foundry under the same harness and conditions. This is not a substitute for public leaderboard scores — it is a **head-to-head metric measured under identical conditions in an Azure environment**.

The evaluation splits into **two tracks** of different character, and **the models covered differ between them.**

| Track | Models evaluated | Strongest candidates | Interpretation |
| --- | --- | --- | --- |
| Custom coding eval | Opus 4.8 · GPT-5.5 · Grok 4.3 · GLM-5.1 · Kimi K2.6 · MiniMax M2.5 · DeepSeek-V4-Pro (7) | DeepSeek-V4-Pro · Claude Opus 4.8 · GPT-5.5 · Grok 4.3 | Four models were the most reliable, at a 100% pass rate, on small deterministic unit-test tasks. |
| SWE-bench Verified | Kimi K2.6 · DeepSeek-V4-Pro · MiniMax M2.5 · Grok 4.3 · GLM-5.1 (5) | Kimi K2.6 · DeepSeek-V4-Pro · MiniMax M2.5 | On real repo patches scored by the official Docker grader, the top 3 are a statistical tie (76/74/74%). |

> **Important — the two evaluations cover different sets of models.**
> - **Claude Opus 4.8 and GPT-5.5 were not run on SWE-bench.** Their repository-patch performance is therefore *not measured*.
> - The models that went through both evaluations are **Grok 4.3 · GLM-5.1 · Kimi K2.6 · MiniMax M2.5 · DeepSeek-V4-Pro (5)**.
> - The SWE-bench ranking should be read as a trend only, since the confidence intervals overlap.

## Conclusion

- Small functional code generation/editing: **DeepSeek-V4-Pro · Claude Opus 4.8 · GPT-5.5 · Grok 4.3** were the most reliable.
- Repository patches (SWE-bench Verified): **Kimi K2.6 · DeepSeek-V4-Pro · MiniMax M2.5** led.
- Looking only at the 5 models that went through both tracks: Grok is strong on custom but lower on SWE; Kimi and MiniMax are strong on SWE but lower on custom; **DeepSeek-V4-Pro ranks near the top on both**. Strengths split by task type, and DeepSeek was consistently strong across both tracks.

## Models by evaluation

| Model | Custom eval | SWE-bench Verified |
| --- | :---: | :---: |
| Claude Opus 4.8 | ✓ | — |
| GPT-5.5 | ✓ | — |
| Grok 4.3 | ✓ | ✓ |
| GLM-5.1 | ✓ | ✓ |
| Kimi K2.6 | ✓ | ✓ |
| MiniMax M2.5 | ✓ | ✓ |
| DeepSeek-V4-Pro | ✓ | ✓ |

## Key results

### Custom coding eval
An internal comparison of 10 small, independent unit-test-style tasks, repeated 5 times across every model (350 runs total).

| Model | Passes over 5 reps | Pass rate | Summary |
| --- | ---: | ---: | --- |
| DeepSeek-V4-Pro Foundry | 50/50 | 100% | 100% pass + 6.24s average latency, the fastest of all models |
| Claude Opus 4.8 ADB | 50/50 | 100% | Among the most reliable and fastest |
| GPT-5.5 Foundry | 50/50 | 100% | Reliable, but PTU-hour cost should be considered |
| Grok 4.3 Foundry | 50/50 | 100% | Good accuracy and cost-efficient, but high latency |
| GLM-5.1 Foundry | 46/50 | 92% | Mostly reliable, but repeated failures on the markdown task |
| Kimi K2.6 Foundry | 38/50 | 76% | JSON/output stability issues surfaced on custom tasks |
| MiniMax M2.5 Foundry | 36/50 | 72% | Cheap, but lower accuracy on small deterministic tasks |

### SWE-bench Verified

Official evaluation results over the full set of 500 human-validated GitHub issues. Claude Opus 4.8 and GPT-5.5 were not run.

| Rank | Model | Resolved/500 | Empty | Error | 95% CI (Wilson) | gross $/resolved |
| :---: | --- | ---: | ---: | ---: | :---: | ---: |
| 1 | **Kimi K2.6 Foundry** | **76.4%** | 0 | 0 | [72.5, 79.9] | $1.34 |
| 2 | **DeepSeek-V4-Pro Foundry** | **74.4%** | 0 | 0 | [70.4, 78.0] | $2.63 |
| 3 | **MiniMax M2.5 Foundry** | **73.8%** | 1 | 0 | [69.8, 77.5] | $0.45 |
| 4 | **Grok 4.3 Foundry** | **67.4%** | 0 | 0 | [63.2, 71.4] | $0.60 |
| 5 | **GLM-5.1 Foundry** | **66.2%** | 58 | 0 | [61.9, 70.2] | $3.76 |

- The top 3 (Kimi · DeepSeek · MiniMax) have heavily overlapping confidence intervals, making them a **statistical tie**. Grok and GLM form a lower group whose CIs are nearly separate from the top group.
- **gross $/resolved** = (prompt tokens × input price + completion tokens × output price) ÷ resolved count — an upper bound that applies no cache discount, and the one common basis computed the same way for all 5 models.

## Recommended use

| Goal | Recommendation | Rationale |
| --- | --- | --- |
| Small code generation/editing, deterministic unit tests | DeepSeek-V4-Pro, Claude Opus 4.8, GPT-5.5, Grok 4.3 | 100% pass rate on custom eval |
| Repository patches / SWE-bench-style tasks | Kimi K2.6, DeepSeek-V4-Pro, MiniMax M2.5 | Top tied group on Verified |
| Cost-sensitive, repeated repo-patch runs | MiniMax M2.5, Grok 4.3 | Lowest cost per resolved on Verified ($0.13–0.14, cache-adj) |
| A single model reliable on both task types | DeepSeek-V4-Pro | 100% on custom + top tied group on Verified; consistently strong across both tracks |

## Next step: model ensembles

The conclusion of this benchmark is that "strengths split by task type — there is no single do-it-all model." Given that, instead of picking one model you can **run several candidates and select the best patch**. A follow-up that validates this as a PoC is [foundry-coding-ensemble](https://github.com/bskim/foundry-coding-ensemble/blob/main/README.md).

- Each model runs its own agent loop independently to produce a candidate patch, and an aggregator selects the best one.
- Aggregation strategies: ① execution-based selection (automatic evaluation via build · test · typecheck) ② cost-aware routing (try the cheapest candidate first). The per-model pass rates and gross $/resolved measured in this repository feed that selection/routing logic.
- On the curated dataset (disc10), execution-based selection achieved a 100% pass rate (not a number that generalizes — it validates the feasibility of the selection mechanism as a PoC).

## Relationship to public benchmarks

| Item | Meaning |
| --- | --- |
| SWE-bench Verified | The fraction of the 500 human-validated GitHub issues that pass the official tests. All 5 models were run on the full set in this work. |
| This SWE run | Foundry MaaS + mini-swe-agent (minimal scaffold) + single attempt at temp=0. Scores run 2–4%p below published leaderboard numbers, which is a good reproduction once the sample/scaffold/attempt differences are accounted for. |
| Custom coding eval | An internal comparison of 10 small, independent unit-test-style tasks repeated 5 times. Not a substitute for public benchmarks. |

## Detailed reports

| Report | Contents |
| --- | --- |
| [Custom coding eval](reports/custom-coding-eval-report.md) | 10 small deterministic tasks × 5 reps (7 models) |
| [SWE-bench Verified](reports/swe-bench-verified-500-report.md) | Full set of 500 Verified — the most reliable basis (5 models) |
| [SWE-bench Lite](reports/swe-bench-lite-report.md) | Intermediate 100-sample results |
| [SWE-bench Trajectory analysis](reports/swe-bench-trajectory-analysis-500.md) | Per-model agent-behavior trends |
| [Public benchmark baseline](benchmarks/benchmarks_baseline.md) | Published scores and unit-price baseline |

## Directory layout

| Directory | Contents |
| --- | ---|
| `reports/` | Source text of the reports above. |
| `benchmarks/` | Public benchmark baseline. |
| `research/` | Original/reference material used in the benchmark research. |

> The evaluation harness, tasks, and raw artifacts (`coding-bench/`), along with the token-cost analysis, are kept local-only and are not included in this repository.
