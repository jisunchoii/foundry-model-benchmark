# 모델 코딩 벤치마크 요약

## 결론

이번 평가에서 의사결정에 가장 유용한 결과는 두 축으로 나눠 봐야 합니다.

| 평가 축 | 가장 강한 후보 | 해석 |
| --- | --- | --- |
| Custom coding eval | Claude Opus 4.8, GPT-5.5, Grok 4.3 | 작은 deterministic unit-test 과제에서는 세 모델이 가장 안정적이었습니다. |
| SWE-bench Lite 100-instance | Kimi K2.6, GLM-5.1 | 실제 repo patch + official Docker evaluator 기준에서는 Kimi(74%)와 GLM(68%)이 앞섰습니다. |

**최종 판단:** 범용 coding assistant/작은 함수형 과제는 Claude Opus 4.8·GPT-5.5·Grok 4.3이 강하고, SWE-bench식 repository patch 작업은 100개 샘플 기준 Kimi K2.6과 GLM-5.1이 더 좋았습니다. SWE-bench Verified 전체(500개) 실행은 현재 진행 중이며, 완료 시 본 리포트를 갱신합니다.

## 핵심 결과

### Custom coding eval

| 모델 | 5회 반복 통과 | 통과율 | 요약 |
| --- | ---: | ---: | --- |
| Claude Opus 4.8 ADB | 50/50 | 100% | 가장 안정적이고 빠른 축 |
| GPT-5.5 Foundry | 50/50 | 100% | 안정적이나 PTU-hour 비용 고려 필요 |
| Grok 4.3 Foundry | 50/50 | 100% | 정확도는 좋고 비용 효율적이나 latency 높음 |
| GLM-5.1 Foundry | 46/50 | 92% | 대부분 안정적이나 markdown task 반복 실패 |
| Kimi K2.6 Foundry | 38/50 | 76% | JSON/output 안정성 이슈가 custom task에서 나타남 |
| MiniMax M2.5 Foundry | 36/50 | 72% | 저렴하지만 작은 deterministic task 정확도는 낮음 |

### SWE-bench Lite 100-instance

| 모델 | Submitted | Resolved | Resolved/100 | Empty patches | Errors | 95% CI (Wilson) |
| --- | ---: | ---: | ---: | ---: | ---: | :---: |
| Kimi K2.6 Foundry | 100 | 74 | 74.0% | 0 | 0 | [64.6, 81.6] |
| GLM-5.1 Foundry | 100 | 68 | 68.0% | 0 | 0 | [58.3, 76.3] |
| Grok 4.3 Foundry | 100 | 64 | 64.0% | 0 | 0 | [54.2, 72.7] |
| MiniMax M2.5 Foundry | 100 | 61 | 61.0% | 0 | 0 | [51.2, 70.0] |

이 SWE-bench 결과는 Verified leaderboard 점수가 아니라 **SWE-bench Lite 첫 100개 instance**에 대한 동일 조건 실행입니다. 전 모델 submitted 100/100, empty patch 0, evaluator error 0입니다. 95% 신뢰구간이 서로 크게 겹치므로 순위는 경향성으로만 해석해야 합니다.

### SWE-bench Verified (진행 중)

500개 human-validated task 전체에 대한 official SWE-bench Verified 실행이 진행 중입니다. 결과가 나오면 아래 표를 채우고 본 리포트의 결론을 갱신합니다.

| 모델 | Submitted | Resolved | Resolved/500 | Empty patches | Errors |
| --- | ---: | ---: | ---: | ---: | ---: |
| Kimi K2.6 Foundry | _진행 중_ | _진행 중_ | _진행 중_ | _진행 중_ | _진행 중_ |
| GLM-5.1 Foundry | _진행 중_ | _진행 중_ | _진행 중_ | _진행 중_ | _진행 중_ |
| Grok 4.3 Foundry | _진행 중_ | _진행 중_ | _진행 중_ | _진행 중_ | _진행 중_ |
| MiniMax M2.5 Foundry | _진행 중_ | _진행 중_ | _진행 중_ | _진행 중_ | _진행 중_ |

## 공개 벤치마크와의 관계


| 항목 | 의미 |
| --- | --- |
| SWE-bench Verified | human-validated 500개 GitHub issue 중 official test를 통과한 비율 (전체 실행 진행 중) |
| 이번 SWE Lite run | SWE-bench Lite 첫 100개 instance에 대한 직접 실행 결과 |
| custom coding eval | 작고 독립적인 unit-test형 과제 10개를 5회 반복한 내부 비교 |

따라서 이번 custom eval과 SWE-bench Lite 100-instance 실행은 공개 Verified 점수의 대체물이 아니라, **우리 환경에서 같은 하네스와 같은 task로 비교한 실측 보조 지표**입니다. Verified 전체(500개) 실행 결과는 별도로 추가됩니다.

## 권장 사용 기준

| 목적 | 추천 |
| --- | --- |
| 작은 코드 생성/수정, deterministic unit test | Claude Opus 4.8, GPT-5.5, Grok 4.3 |
| repository patch/SWE-bench식 task | Kimi K2.6, GLM-5.1 우선 검토 |
| 비용 민감한 반복 실행 | Grok 4.3, MiniMax M2.5 후보 유지 |
| 공개 leaderboard와의 정합성 확인 | SWE-bench Verified 전체 또는 더 큰 Lite subset 추가 실행 필요 |

## 상세 리포트

| 리포트 | 경로 |
| --- | --- |
| Custom coding eval 상세 | `C:\Users\jisunchoi\projects\foundry-model-coding-benchmark\reports\custom-coding-eval-report.md` |
| SWE-bench Lite 100-instance 상세 | `C:\Users\jisunchoi\projects\foundry-model-coding-benchmark\reports\swe-bench-lite-100-report.md` |
| Clean SWE-bench Lite 10개 파일럿 | `C:\Users\jisunchoi\projects\foundry-model-coding-benchmark\reports\swe-bench-lite-clean-report.md` |
| Troubleshooting 기록 | `C:\Users\jisunchoi\projects\foundry-model-coding-benchmark\reports\troubleshooting-log.md` |
| 공개 benchmark 기준표 | `C:\Users\jisunchoi\projects\foundry-model-coding-benchmark\benchmarks\benchmarks_baseline.md` |

