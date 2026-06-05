# 코딩 벤치마크 기준선

이 파일은 로컬 평가를 실행하기 전, 1차 공개 벤치마크 기준선을 기록합니다.

공식 SWE-bench Verified 리더보드는 `https://www.swebench.com/` 및 HuggingFace `SWE-bench/SWE-bench_Verified` 페이지에 게시됩니다.

| 공급사 | 모델 | Foundry ID | SWE Verified | SWE Pro | SWE Multilingual | Terminal |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Anthropic | Claude Opus 4.8 | `claude-opus-4-8` | 88.6 | 69.2 | 84.4 | 74.6 (T-Bench 2.1) |
| OpenAI | GPT-5.5 | `gpt-5.5` | N/A | 58.6 | N/A | 78.2 (T-Bench 2.1) |
| Moonshot AI | Kimi K2.6 | `Kimi-K2.6` | 80.2 † | 58.6 | 76.7 | 66.7 (T-Bench 2.0) |
| Z.AI | GLM-5 | `FW-GLM-5` | 77.8 †* | N/A | 73.3 | 56.2 (T-Bench 2.0) |
| MiniMax | MiniMax M2.5 | `FW-MiniMax-M2.5` | 75.8 †* | 55.4 | 74.1 | 51.7 (T-Bench 2.0) |
| xAI | Grok 4.3 | `grok-4.3` | N/A | N/A | N/A | N/A |

† 공식 SWE-bench Verified 리더보드 등재 값(Kimi K2.6, GLM-5, MiniMax M2.5).
\* 리더보드에서 공급사 자가보고(self-reported)로 표시된 값. Kimi K2.6은 자가보고 표시 없이 등재되어 있습니다.

† 표시가 없는 SWE Verified 값(Claude Opus 4.8 88.6, GPT-5.5)은 리더보드 미등재이며 공급사 자가보고 또는 교차비교 수치입니다. SWE Pro·SWE Multilingual·Terminal 컬럼은 공식 리더보드가 없으므로 전부 공급사 자가보고 또는 교차비교 값입니다.

## 출처

- 공식 리더보드(데이터셋 + 점수): https://huggingface.co/datasets/SWE-bench/SWE-bench_Verified
- 공식 리더보드: https://www.swebench.com/
