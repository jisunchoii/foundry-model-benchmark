# Custom coding eval report

## 목적

공개 benchmark 전체 재현이 아니라, Azure Foundry/ADB에서 실제로 호출 가능한 모델들이 작은 coding task를 얼마나 안정적으로 해결하는지 비교했습니다.

이 평가는 SWE-bench, Aider Polyglot, LiveCodeBench와 같은 공개 benchmark를 대체하지 않습니다. 대신 같은 prompt/채점기/반복 조건에서 모델별 안정성, latency, 비용 경향을 보는 내부 파일럿입니다.

## 평가 방식

| 항목 | 내용 |
| --- | --- |
| Task 수 | 10개 |
| 반복 | 전체 모델 5회 반복 |
| 총 호출 | 300회 |
| 채점 | 각 task의 Python unittest 또는 deterministic validator 통과 여부 |
| 결과 위치 | `coding-bench\custom\runs\repeat-5x-all-models` |

### Task 목록

| Task | 내용 |
| --- | --- |
| `py_slugify` | 공백/구두점/underscore 처리 slug 생성 |
| `cart_discount` | 수량, gift card 제외, 조건부 할인/세금 계산 |
| `json_patch` | add/replace/remove JSON Patch subset |
| `markdown_toc` | H2/H3 TOC 및 GitHub-style anchor |
| `log_redaction` | email/token/API key/card masking |
| `interval_merge` | interval 병합 |
| `rate_limiter` | per-key fixed-window limiter |
| `sql_builder` | identifier validation + parameterized SELECT |
| `html_accessible_form` | accessible login form |
| `package_stats` | mean/median/percentile 구현 |

## 5회 반복 결과

| 모델 | 통과 | 전체 호출 | 통과율 | 평균 지연시간 | P50 | P95 | 추정 token 비용 | 통과 1건당 추정 비용 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 4.8 ADB | 50 | 50 | 100.0% | 7.90s | 7.657s | 10.225s | $0.551025 | $0.011020 |
| GPT-5.5 Foundry | 50 | 50 | 100.0% | 8.674s | 7.429s | 14.484s | $0.760830 | $0.015217 |
| Grok 4.3 Foundry | 50 | 50 | 100.0% | 18.54s | 19.465s | 28.399s | $0.219525 | $0.004391 |
| GLM-5.1 Foundry | 46 | 50 | 92.0% | 19.959s | 19.997s | 34.116s | $0.261884 | $0.005693 |
| Kimi K2.6 Foundry | 38 | 50 | 76.0% | 25.003s | 20.555s | 46.272s | $0.371297 | $0.009771 |
| MiniMax M2.5 Foundry | 36 | 50 | 72.0% | 10.337s | 9.417s | 15.342s | $0.059045 | $0.001640 |

## Task 안정성

| 모델 | 불안정/실패 집중 task |
| --- | --- |
| Claude Opus 4.8 ADB | 없음 |
| GPT-5.5 Foundry | 없음 |
| Grok 4.3 Foundry | 없음 |
| GLM-5.1 Foundry | `markdown_toc` |
| Kimi K2.6 Foundry | `log_redaction`, `markdown_toc`, `package_stats`, `py_slugify`, `cart_discount` |
| MiniMax M2.5 Foundry | `markdown_toc`, `json_patch`, `rate_limiter`, `sql_builder` |

## 공개 benchmark 대비 해석

공개 coding benchmark는 보통 더 큰 문제셋, 다른 harness, 다른 test-time compute 정책을 사용합니다. 따라서 이번 custom eval의 순위를 공개 leaderboard 순위로 해석하면 안 됩니다.

| 비교 대상 | 이번 custom eval과의 차이 |
| --- | --- |
| SWE-bench Verified/Lite | repository 전체를 수정하고 official test를 통과해야 하는 agentic patch benchmark |
| LiveCodeBench | 알고리즘/코딩 문제 중심 |
| Aider Polyglot | Aider scaffold와 multi-language edit task 중심 |
| 이번 custom eval | 작은 deterministic unit-test task를 단일 응답/파일 생성 방식으로 평가 |

이번 custom eval이 공개 benchmark 기대와 다른 지점:

- Kimi K2.6과 MiniMax M2.5는 공개 coding benchmark에서 강하게 보고되지만, 이번 custom eval에서는 출력 형식/특정 deterministic task에서 불안정했습니다.
- Grok 4.3은 공개 numeric coding benchmark가 부족했지만, 이번 custom eval에서는 50/50으로 안정적이었습니다.
- Claude Opus 4.8과 GPT-5.5는 작은 unit-test형 task에서는 가장 안정적이었습니다.
- GLM-5.1은 전반적으로 준수했지만 markdown anchor처럼 세부 규칙이 많은 task에서 반복 실패했습니다.

## 결론

작은 코드 생성/수정 task에서는 Claude Opus 4.8, GPT-5.5, Grok 4.3이 최상위입니다. 다만 이 결과만으로 SWE-bench식 repository patch 성능을 판단하면 안 되며, SWE-bench 결과는 별도 리포트에서 봐야 합니다.

## 원본 산출물

| 항목 | 경로 |
| --- | --- |
| 5회 반복 리포트 | `C:\Users\jisunchoi\projects\foundry-model-coding-benchmark\coding-bench\custom\runs\repeat-5x-all-models\repeat-5x-all-report.md` |
| 5회 반복 요약 CSV | `C:\Users\jisunchoi\projects\foundry-model-coding-benchmark\coding-bench\custom\runs\repeat-5x-all-models\repeat-5x-all-summary.csv` |
| 5회 반복 실패 CSV | `C:\Users\jisunchoi\projects\foundry-model-coding-benchmark\coding-bench\custom\runs\repeat-5x-all-models\repeat-5x-all-failures.csv` |
| 1차 실행 결과 | `C:\Users\jisunchoi\projects\foundry-model-coding-benchmark\coding-bench\custom\runs\first-pass` |

