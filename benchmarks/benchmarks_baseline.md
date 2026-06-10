# Coding benchmark baseline

This file records an initial public-benchmark baseline before running the local evaluations.

The official SWE-bench Verified leaderboard is published at `https://www.swebench.com/` and on the HuggingFace `SWE-bench/SWE-bench_Verified` page.

| Vendor | Model | Foundry ID | SWE Verified | SWE Pro | SWE Multilingual | Terminal |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Anthropic | Claude Opus 4.8 | `claude-opus-4-8` | 88.6 | 69.2 | 84.4 | 74.6 (T-Bench 2.1) |
| OpenAI | GPT-5.5 | `gpt-5.5` | N/A | 58.6 | N/A | 78.2 (T-Bench 2.1) |
| Moonshot AI | Kimi K2.6 | `Kimi-K2.6` | 80.2 † | 58.6 | 76.7 | 66.7 (T-Bench 2.0) |
| Z.AI | GLM-5 | `FW-GLM-5` | 77.8 †* | N/A | 73.3 | 56.2 (T-Bench 2.0) |
| MiniMax | MiniMax M2.5 | `FW-MiniMax-M2.5` | 75.8 †* | 55.4 | 74.1 | 51.7 (T-Bench 2.0) |
| xAI | Grok 4.3 | `grok-4.3` | N/A | N/A | N/A | N/A |

† Value listed on the official SWE-bench Verified leaderboard (Kimi K2.6, GLM-5, MiniMax M2.5).
\* Value flagged as vendor self-reported on the leaderboard. Kimi K2.6 is listed without a self-reported flag.

† SWE Verified values without the † mark (Claude Opus 4.8 88.6, GPT-5.5) are not on the leaderboard and are vendor self-reported or cross-comparison figures. The SWE Pro, SWE Multilingual, and Terminal columns have no official leaderboard, so all of those values are vendor self-reported or cross-comparison figures.

## Sources

- Official leaderboard (dataset + scores): https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified
- Official leaderboard: https://www.swebench.com/
