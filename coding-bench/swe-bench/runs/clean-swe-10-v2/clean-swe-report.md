# Clean SWE-bench Lite Docker eval

Run date: 2026-06-03

Dataset: `SWE-bench/SWE-bench_Lite`  
Split: `test`  
Sample: first 10 test instances used throughout this evaluation thread  
Scaffold: `mini-swe-agent` + Docker environment  
Scoring: official `swebench.harness.run_evaluation`, `resolved_ids`

## Meaning of SWE-bench Verified vs this run

SWE-bench Verified scores are the percentage of 500 human-validated GitHub issue tasks that a model/agent system resolves by modifying the repository and passing the official tests. For example, 75.8 means about 379 of 500 Verified tasks were resolved. The score reflects the full system: model, agent scaffold, tools, step limits, retry/rollout policy, and evaluator.

This run is not SWE-bench Verified. It is a small pilot on the first 10 `SWE-bench_Lite` test instances. It should be interpreted as a same-harness comparison for these 10 tasks, not as a public leaderboard-equivalent Verified score.

## Prerequisites completed

- Increased effective Fireworks quota by splitting regions:
  - MiniMax M2.5: eastus, `<foundry-account-eastus>/bench-minimax-m25-eastus`, DataZoneStandard 500k TPM.
  - GLM-5.1: westus3, `<foundry-account-westus3>/bench-glm-51-westus3`, DataZoneStandard 500k TPM.
- Added model-specific proxy routing for Kimi, Grok, MiniMax, and GLM.
- Added proxy retry handling for Azure 429 throttles and 401 token-refresh cases.
- Added neutral proxy aliases for Kimi/Grok to avoid LiteLLM provider auto-detection.
- Raised agent step limit to 120 and used trajectory diff recovery where needed to prevent empty submissions.
- Restarted the VM to clear a stuck Azure RunCommand/CustomScript lock; disk artifacts were preserved.

## Final result

| Model | Submitted | Completed | Resolved | Unresolved | Empty patches | Errors | Resolved / submitted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Kimi K2.6 Foundry | 10 | 10 | 7 | 3 | 0 | 0 | 70.0% |
| GLM-5.1 Foundry | 10 | 10 | 6 | 4 | 0 | 0 | 60.0% |
| Grok 4.3 Foundry | 10 | 10 | 5 | 5 | 0 | 0 | 50.0% |
| MiniMax M2.5 Foundry | 10 | 10 | 5 | 5 | 0 | 0 | 50.0% |

All four models produced non-empty predictions for all 10 instances. The official Docker evaluator reported zero patch-empty cases and zero infrastructure/evaluation errors.

## Resolved IDs

| Model | Resolved IDs |
| --- | --- |
| Kimi K2.6 Foundry | `astropy__astropy-12907`, `astropy__astropy-14365`, `astropy__astropy-14995`, `astropy__astropy-6938`, `django__django-10914`, `django__django-10924`, `django__django-11001` |
| GLM-5.1 Foundry | `astropy__astropy-12907`, `astropy__astropy-14365`, `astropy__astropy-14995`, `django__django-10914`, `django__django-10924`, `django__django-11001` |
| Grok 4.3 Foundry | `astropy__astropy-12907`, `astropy__astropy-14995`, `astropy__astropy-6938`, `django__django-10914`, `django__django-11001` |
| MiniMax M2.5 Foundry | `astropy__astropy-12907`, `astropy__astropy-14182`, `astropy__astropy-14995`, `django__django-10914`, `django__django-11001` |

## Interpretation

This clean run supersedes the earlier SWE-bench sections in the main report. The main report now keeps this single clean SWE-bench result for execution comparison.
