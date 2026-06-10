# SWE-bench Lite benchmark report

## What SWE-bench is

SWE-bench is a coding-agent evaluation benchmark whose problems come from **real issues and the actual PRs that resolved them** in real open-source GitHub repositories (django, scikit-learn, astropy, etc.). It deals with real-world bugs rather than artificial function problems, and it is **graded automatically by whether the project's real tests pass** — not by humans.

### Structure of a single task

- **Input**: a snapshot of the repository code at the time the issue was filed + the issue description (GitHub issue text)
- **What the model must do**: explore the codebase, find where to fix, and produce a patch (diff)
- **Grading**: run the project test suite → resolved if the bug-reproduction test (FAIL→PASS) passes and existing tests (PASS→PASS) don't break

> This is not simple code generation but an agentic task requiring exploration → root-cause analysis → minimal fix → regression prevention. So the score is the joint product of the model's standalone ability and the design of the agent scaffold (here, `mini-swe-agent`).

## Lite vs Verified — what's different

Both are subsets carved out of the original SWE-bench (2,294 problems), but **the selection criteria differ.**

| | SWE-bench Lite | SWE-bench Verified |
| --- | --- | --- |
| Count | 300 | 500 |
| Selection method | **Automatic (heuristic) filtering** | **Reviewed one by one by professional developers** (OpenAI collaboration) |
| Purpose | Run cheaply and quickly | Guarantee solvability and fair grading |

- **Lite = lightweight.** The original was too large, so 300 problems easy to handle by automatic rules were selected. The criteria are roughly "bug-fix oriented / few files touched by the gold patch / environment not hard to set up." Since there's no human review, ambiguous or incomplete problems may be mixed in.
- **Verified = quality-assured.** 500 problems where humans checked, one by one, whether the issue description alone is clear enough to solve, whether the grading tests evaluate the answer fairly, and whether the environment works correctly.

⇒ Lite optimizes for **cost/speed**, Verified guarantees **quality/fairness**. The final basis for this work is therefore [Verified](./swe-bench-verified-500-report.md), and this Lite experiment is a pilot/intermediate stage.

> For reference, the Verified score is the fraction of 500 that pass the official tests (e.g., Verified 75.8 ≈ 379/500 resolved).

## Scope of this experiment

This experiment is not the full Lite set (300) but a **pilot of the first 10 from the test split** and an **expansion of that to the first 100**. It should not be compared directly to public leaderboard scores; read it as a small/medium-scale comparison under identical conditions.

## Experiment setup

| Item | Clean-10 pilot | 100-instance expansion |
| --- | --- | --- |
| Dataset | `SWE-bench/SWE-bench_Lite` | `SWE-bench/SWE-bench_Lite` |
| Split | `test` | `test` |
| Sample | First 10 instances | First 100 instances (`slice 0:100`) |
| Scaffold | `mini-swe-agent` | `mini-swe-agent`  |
| Environment | Docker on Azure Ubuntu VM | Docker on Azure Ubuntu VM  |
| Temperature | - | 0 |
| Scoring | official `swebench.harness.run_evaluation` | official `swebench.harness.run_evaluation` |

For the 100-instance expansion, 4 models were run in parallel, distributed across per-model dedicated VMs/endpoints. Each model used a different Azure Foundry endpoint/region, so there was no quota contention.

## Results summary

### 10-instance pilot results

| Model | Submitted | Completed | Resolved | Unresolved | Empty patches | Errors | Resolved / submitted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Kimi K2.6 Foundry | 10 | 10 | 7 | 3 | 0 | 0 | 70.0% |
| GLM-5.1 Foundry | 10 | 10 | 6 | 4 | 0 | 0 | 60.0% |
| Grok 4.3 Foundry | 10 | 10 | 5 | 5 | 0 | 0 | 50.0% |
| MiniMax M2.5 Foundry | 10 | 10 | 5 | 5 | 0 | 0 | 50.0% |

### 100-instance expansion results

| Model | Submitted | Resolved | Resolved/100 | Empty patches | Errors | 95% CI (Wilson) |
| --- | ---: | ---: | ---: | ---: | ---: | :---: |
| **Kimi K2.6 Foundry** | 100 | **74** | **74.0%** | 0 | 0 | [64.6, 81.6] |
| **GLM-5.1 Foundry** | 100 | **68** | **68.0%** | 0 | 0 | [58.3, 76.3] |
| **Grok 4.3 Foundry** | 100 | **64** | **64.0%** | 0 | 0 | [54.2, 72.7] |
| **MiniMax M2.5 Foundry** | 100 | **61** | **61.0%** | 0 | 0 | [51.2, 70.0] |

## Pilot vs 100-instance comparison

| Model | 10-instance (resolved/10) | 100-run (resolved/100) | Note |
| --- | :---: | :---: | --- |
| Kimi K2.6 | 7/10 (70%) | 74/100 (74%) | Pilot #1 → held #1 at 100 |
| GLM-5.1 | 6/10 (60%) | 68/100 (68%) | Slight rise vs 10-sample, held #2 |
| Grok 4.3 | 5/10 (50%) | 64/100 (64%) | Rose relatively sharply as the sample grew |
| MiniMax M2.5 | 5/10 (50%) | 61/100 (61%) | Rose as the sample grew |

## Interpretation

- In the 10-instance pilot, Kimi K2.6 was highest at 7/10, followed by GLM-5.1 at 6/10. Grok 4.3 and MiniMax M2.5 tied at 5/10.
- However, 10 instances is only a 10-sample set and should not be generalized to full SWE-bench Lite or Verified performance.
- In the 100-instance expansion, **Kimi K2.6 was again #1 at 74%**, followed by GLM-5.1 (68%), Grok 4.3 (64%), and MiniMax M2.5 (61%). The pilot leader, Kimi, kept its lead even scaled to 100.
- That said, the 95% confidence intervals **overlap heavily** (e.g., Kimi [64.6, 81.6] vs GLM [58.3, 76.3] vs MiniMax [51.2, 70.0]). At a 100-sample size the band is roughly ±9–10%p, so the differences between models are **not statistically conclusive**. The ranking should be read as a trend only.
- Compared to the 10-instance pilot order (Kimi > GLM > Grok = MiniMax), the top/bottom trend holds, but at 100 the gaps between models narrowed somewhat.

## Artifact paths

The preserved artifacts of the 10-instance pilot (report, summary CSV, official evaluation JSON) are in the local `coding-bench/swe-bench/runs/clean-swe-10-v2/`. The 100-instance expansion was run on per-model dedicated Azure VMs, where each model's predictions (`preds.json`), official evaluation report (`report.json`), and trajectory logs are preserved together.
