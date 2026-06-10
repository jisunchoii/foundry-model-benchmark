# SWE-bench Verified benchmark report

## Overview

This report covers the results of 5 Foundry coding models over **all 500 instances** of **SWE-bench Verified**. It used the mini-swe-agent scaffold + the official evaluator (`swebench.harness.run_evaluation`), run on per-model dedicated Azure Ubuntu VMs / Foundry endpoints.

## Experiment setup

| Item | Value |
| --- | --- |
| Dataset | `SWE-bench/SWE-bench_Verified` |
| Split | `test` (all 500) |
| Sample | 500/500 (full set) |
| Repository distribution | Official Verified-500 distribution (django the largest, plus sympy, scikit-learn, sphinx, matplotlib, astropy, xarray, pytest, pylint, requests, seaborn, flask, etc. — 12 repos) |
| Scaffold | `mini-swe-agent` |
| Environment | Docker on Azure Ubuntu VM (per-model dedicated) |
| Step limit | STEPS=150 (raised to 300 for DeepSeek and GLM to converge on hard instances) |
| Temperature | 0 (single attempt, MAXPASS=3 empty-patch prune-retry) |
| Empty-patch prevention | `HARVEST_DIFF_FALLBACK` |
| Scoring | official `swebench.harness.run_evaluation` |

## Results summary (resolved/500, descending)

| Rank | Model | Resolved | Resolved/500 | Unresolved | Empty | Error | 95% CI (Wilson) |
| :---: | --- | ---: | ---: | ---: | ---: | ---: | :---: |
| 1 | **Kimi K2.6 Foundry** | **382** | **76.4%** | 118 | 0 | 0 | [72.5, 79.9] |
| 2 | **DeepSeek-V4-Pro Foundry** | **372** | **74.4%** | 128 | 0 | 0 | [70.4, 78.0] |
| 3 | **MiniMax M2.5 Foundry** | **369** | **73.8%** | 130 | 1 | 0 | [69.8, 77.5] |
| 4 | **Grok 4.3 Foundry** | **337** | **67.4%** | 163 | 0 | 0 | [63.2, 71.4] |
| 5 | **GLM-5.1 Foundry** | **331** | **66.2%** | 111 | 58 | 0 | [61.9, 70.2] |

- **Error = 0 (all models)**: all 500 instances were graded normally by the official evaluator.
- **Empty**: the count of cases that failed to submit a non-empty patch. GLM's 58 and MiniMax's 1 are cases where the model deterministically judged "no fix needed" and submitted an empty patch; **per the user-approval policy, these are counted as unresolved in the denominator of 500**. The other models have empty=0.

## Interpretation

- The ranking over the full 500 is **Kimi K2.6 (76.4%) > DeepSeek-V4-Pro (74.4%) > MiniMax M2.5 (73.8%) > Grok 4.3 (67.4%) > GLM-5.1 (66.2%)**.
- **The top 3 (Kimi · DeepSeek · MiniMax) are a statistical-tie band with heavily overlapping 95% confidence intervals** (76.4 vs 74.4 vs 73.8%). The ranking should be read as a trend only.
- **Grok and GLM form a lower group**, somewhat separated from the top 3 since the CIs barely overlap (Kimi's lower bound 72.5% > Grok's upper bound 71.4%).
- **Sample-expansion effect**: growing from 100 → 500 narrowed the confidence intervals from ±8–9%p → ±4%p, raising confidence in the ranking. Grok (71%), tied in random-100, separated to the lower group at 500.
- **GLM's 58 empty**: GLM deterministically submits empty patches on 58 instances; excluding them, the resolve rate over the remaining 442 is 331/442 = 74.9%, similar to the top group. Following standard convention (resolved/500), we report 66.2%.

## Comparison with published Verified scores

| Model | This Verified-500 | Published Verified (source) | Difference |
| --- | ---: | ---: | ---: |
| Kimi K2.6 | 76.4% | 80.2% (official leaderboard) | −3.8%p |
| DeepSeek-V4-Pro | 74.4% | N/A | — |
| MiniMax M2.5 | 73.8% | 75.8% (self-reported/leaderboard) | −2.0%p |
| Grok 4.3 | 67.4% | N/A | — |
| GLM-5.1 | 66.2% | 77.8% (self-reported, GLM-5) | −11.6%p |

> **Comparison caveats**:
> - **Minimal scaffold**: mini-swe-agent is simpler than the sophisticated agent scaffolds used for top leaderboard submissions.
> - **Single attempt, temp=0**: one attempt, no best-of-N or multi-rollout.
> - **Foundry MaaS**: Azure Foundry managed endpoints.
> - **Why GLM's gap is large**: the published 77.8% is a self-reported figure for `GLM-5` (the higher SKU), while this experiment uses Foundry's `GLM-5.1` deployment. GLM also has 58 deterministic empty patches (included in the denominator) that drag the score down by about 12%p. Excluding the empty patches, it is 74.9%, shrinking the gap to −2.9%p.
> - Kimi and MiniMax, at −2 to −4%p, **reproduce the published figures well** once the above condition differences are accounted for.

## Token usage cost (full 500 run)

We converted each model's **actually-billed tokens** over the full 500 run (summed from traj `extra.response.usage`) to cost using Azure Foundry pricing. This workload is overwhelmingly input-bound (completion tokens < 1.5% of prompt), with a very high prompt-cache share of 79–97%.

- **gross**: bills all prompt tokens at the input list price (ignores cache discount → upper bound).
- **cache-adj**: applies the cache price to cached tokens (kimi $0.16, grok $0.20, glm $0.286 (Fireworks actual); minimax conservatively approximated at 25% of input) → **closer to actual billing**.

| Model | input/output ($/1M) | prompt(M) | cache% | **gross total** | **gross /resolved** | **cache-adj total** | **cache-adj /resolved** |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MiniMax M2.5 | 0.30 / 1.20 | 526.2 | 97.3% | $164.4 | $0.445 | **$49.2** | **$0.133** |
| Grok 4.3 | 1.25 / 2.50 | 160.0 | 92.1% | $202.7 | $0.601 | **$48.0** | **$0.142** |
| Kimi K2.6 | 0.95 / 4.00 | 512.2 | 78.7% | $510.7 | $1.337 | **$192.1** | **$0.503** |
| GLM-5.1 | 1.54 / 4.84 | 788.8 | 93.3% | $1243.3 | $3.756 | **$320.5** | **$0.968** |
| DeepSeek-V4-Pro | 1.74 / 3.48 | 550.3 | n/a¹ | $977.1 | $2.627 | — ¹ | — ¹ |

¹ The DeepSeek Foundry response format doesn't populate `prompt_tokens_details.cached_tokens`, so the cache rate tallies as 0 (which may not mean cache was actually unused) → **cache-adj cannot be computed; gross only**. Pricing is per [Azure AI Foundry pricing (DeepSeek)](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/deepseek/), Global Standard, input $1.74 / output $3.48. gross = prompt 550.3M × 1.74 + completion 5.66M × 3.48 = $977.1.

### Cost key observations

- **MiniMax and Grok are cheapest per resolved** ($0.13–0.14, cache-adj). MiniMax thanks to a low input price (0.30) + 97% cache; Grok thanks to few total tokens (prompt 160M, 1/3 of the others).
- **GLM is most expensive per resolved** ($0.97): the most tokens (789M prompt) + a high price (input 1.54 / output 4.84, Fireworks Data Zone) + a small resolved denominator due to 58 empty patches.
- **Kimi** is mid-upper cost ($0.50/resolved) but has the **highest resolve rate**, giving it a good quality-cost balance.
- Output tokens are under 1% of prompt — total cost is driven by **input price + cache policy**.

## Artifact paths

Each model's predictions (`preds.500.json`), official evaluation report (`official-results/<model>.report.500.json`), and trajectory logs are preserved at `/opt/swebench/runs-verified/<model>/` on each model's dedicated VM.

Trajectory archives (Blob `swebench-logs/`):

| Model | Blob path |
| --- | --- |
| Kimi K2.6 | `verified-500/kimi-k2.6-foundry.traj.tar.gz` |
| DeepSeek-V4-Pro | `verified-500/deepseek-v4-pro-foundry.traj.tar.gz` |
| MiniMax M2.5 | `verified-500/minimax-m2.5-foundry.traj.tar.gz` |
| Grok 4.3 | `verified-500/grok-4.3-foundry.traj.tar.gz` |
| GLM-5.1 | `verified-500/glm-5.1-foundry.traj.tar.gz` |

## Cross-reference

- SWE-bench Lite results: [swe-bench-lite-report.md](./swe-bench-lite-report.md)
- Trajectory analysis (full 500): [swe-bench-trajectory-analysis-500.md](./swe-bench-trajectory-analysis-500.md)
- Published baseline: [benchmarks_baseline.md](../benchmarks/benchmarks_baseline.md)
