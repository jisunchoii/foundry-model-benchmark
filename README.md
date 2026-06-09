# Microsoft Foundry 모델 코딩 벤치마크

Microsoft Foundry 에서 호출 가능한 모델들을 동일한 하네스·조건으로 비교한 코딩 성능 평가입니다. 공개 leaderboard 점수의 대체물이 아니라, **Azure 환경에서 같은 조건으로 측정한 실측 비교 지표**입니다.

평가는 성격이 다른 **두 축**으로 나뉘며, **대상 모델이 서로 다릅니다.**

| 평가 축 | 대상 모델 | 가장 강한 후보 | 해석 |
| --- | --- | --- | --- |
| Custom coding eval | Opus 4.8 · GPT-5.5 · Grok 4.3 · GLM-5.1 · Kimi K2.6 · MiniMax M2.5 · DeepSeek-V4-Pro (7개) | DeepSeek-V4-Pro<br>Claude Opus 4.8<br>GPT-5.5<br>Grok 4.3 | 작은 deterministic unit-test 과제에서 네 모델이 통과율 100%로 가장 안정적. |
| SWE-bench Verified | Kimi K2.6 · DeepSeek-V4-Pro · MiniMax M2.5 · Grok 4.3 · GLM-5.1 (5개) | Kimi K2.6<br>DeepSeek-V4-Pro<br>MiniMax M2.5 | 실제 repo patch + 공식 Docker 채점에서 상위 3개가 통계적 동률(76/74/74%). |

> **중요 — 두 평가의 대상 모델 구성이 다릅니다.**
> - **Claude Opus 4.8·GPT-5.5는 SWE-bench를 실행하지 않았습니다.** 따라서 두 모델의 repository patch 성능은 *측정된 바 없음* 입니다.
> - 두 평가 모두 거친 모델은 **Grok 4.3·GLM-5.1·Kimi K2.6·MiniMax M2.5·DeepSeek-V4-Pro 5개**입니다.
> - SWE-bench 순위는 신뢰구간이 겹쳐 경향성으로만 해석해야 합니다.

## 결론

- 작은 함수형 코드 생성/수정에서는 **DeepSeek-V4-Pro·Claude Opus 4.8·GPT-5.5·Grok 4.3**이 가장 안정적이었고, repository patch형(SWE-bench Verified, 대상 5개)에서는 **Kimi K2.6·DeepSeek-V4-Pro·MiniMax M2.5**가 상위 동률 그룹입니다.
- 두 축을 모두 거친 5개 모델만 보면, Grok은 custom에서 강하지만 SWE에서는 하위, Kimi·MiniMax는 SWE에서 강하지만 custom에서는 하위, **DeepSeek-V4-Pro는 양쪽 모두 상위권**으로 — 과제 유형에 따라 강점이 갈리는 가운데 DeepSeek가 두 축에서 일관되게 강했습니다.

## 평가별 대상 모델

| 모델 | Custom eval | SWE-bench Verified |
| --- | :---: | :---: |
| Claude Opus 4.8 | ✓ | — |
| GPT-5.5 | ✓ | — |
| Grok 4.3 | ✓ | ✓ |
| GLM-5.1 | ✓ | ✓ |
| Kimi K2.6 | ✓ | ✓ |
| MiniMax M2.5 | ✓ | ✓ |
| DeepSeek-V4-Pro | ✓ | ✓ |

## 핵심 결과

### Custom coding eval 
작고 독립적인 unit-test형 과제 10개를 전체 모델 5회 반복(총 350회)한 내부 비교입니다.

| 모델 | 5회 반복 통과 | 통과율 | 요약 |
| --- | ---: | ---: | --- |
| DeepSeek-V4-Pro Foundry | 50/50 | 100% | 100% 통과 + 평균 지연 6.24s로 전 모델 중 가장 빠름 |
| Claude Opus 4.8 ADB | 50/50 | 100% | 가장 안정적이고 빠른 축 |
| GPT-5.5 Foundry | 50/50 | 100% | 안정적이나 PTU-hour 비용 고려 필요 |
| Grok 4.3 Foundry | 50/50 | 100% | 정확도는 좋고 비용 효율적이나 latency 높음 |
| GLM-5.1 Foundry | 46/50 | 92% | 대부분 안정적이나 markdown task 반복 실패 |
| Kimi K2.6 Foundry | 38/50 | 76% | JSON/output 안정성 이슈가 custom task에서 나타남 |
| MiniMax M2.5 Foundry | 36/50 | 72% | 저렴하지만 작은 deterministic task 정확도는 낮음 |

### SWE-bench Verified 

human-validated 500개 GitHub issue 전수에 대한 공식 평가 결과입니다. Claude Opus 4.8·GPT-5.5는 미실행.

| 순위 | 모델 | Resolved/500 | Empty | Error | 95% CI (Wilson) | gross $/resolved |
| :---: | --- | ---: | ---: | ---: | :---: | ---: |
| 1 | **Kimi K2.6 Foundry** | **76.4%** | 0 | 0 | [72.5, 79.9] | $1.34 |
| 2 | **DeepSeek-V4-Pro Foundry** | **74.4%** | 0 | 0 | [70.4, 78.0] | $2.63 |
| 3 | **MiniMax M2.5 Foundry** | **73.8%** | 1 | 0 | [69.8, 77.5] | $0.45 |
| 4 | **Grok 4.3 Foundry** | **67.4%** | 0 | 0 | [63.2, 71.4] | $0.60 |
| 5 | **GLM-5.1 Foundry** | **66.2%** | 58 | 0 | [61.9, 70.2] | $3.76 |

- 상위 3개(Kimi·DeepSeek·MiniMax)는 신뢰구간이 크게 겹쳐 **통계적 동률**입니다. Grok·GLM은 상위 그룹과 CI가 거의 분리되는 하위 그룹입니다.
- **gross $/resolved** = (prompt 토큰 × input 단가 + completion 토큰 × output 단가) ÷ resolved 수 — 캐시 할인을 적용하지 않은 비용 상한이며, 5개 모델 모두 동일 방식으로 산출되는 공통 기준입니다.



## 권장 사용 기준

| 목적 | 추천 | 근거 |
| --- | --- | --- |
| 작은 코드 생성/수정, deterministic unit test | DeepSeek-V4-Pro<br>Claude Opus 4.8<br>GPT-5.5<br>Grok 4.3 | Custom eval 통과율 100% |
| repository patch / SWE-bench식 task | Kimi K2.6<br>DeepSeek-V4-Pro<br>MiniMax M2.5 | Verified 상위 동률 그룹 |
| 비용 민감한 repo patch 반복 실행 | MiniMax M2.5<br>Grok 4.3 | Verified 해결 건당 비용 최저($0.13~0.14, cache-adj) |
| 두 과제 유형 모두 안정적인 단일 후보 | DeepSeek-V4-Pro | custom 100% + Verified 상위 동률, 두 축 모두 거쳐 일관되게 강함 |

## 공개 벤치마크와의 관계

| 항목 | 의미 |
| --- | --- |
| SWE-bench Verified | human-validated 500개 GitHub issue 중 official test 통과 비율. 본 작업에서 5개 모델 전수 실행 완료. |
| 이번 SWE 실행 | Foundry MaaS + mini-swe-agent(미니멀 스캐폴드) + 단일 시도 temp=0. published 리더보드 수치보다 2~4%p 낮으나 표본·스캐폴드·시도 차이를 감안하면 양호한 재현. |
| custom coding eval | 작고 독립적인 unit-test형 과제 10개를 5회 반복한 내부 비교. 공개 벤치마크 대체물 아님. |

## 상세 리포트

| 리포트 | 내용 |
| --- | --- |
| [Custom coding eval](reports/custom-coding-eval-report.md) | 작은 deterministic task 10개 × 5회 반복 (7개 모델) |
| [SWE-bench Verified](reports/swe-bench-verified-500-report.md) | Verified 전수 500개 — 가장 신뢰도 높은 기준 (5개 모델) |
| [SWE-bench Lite](reports/swe-bench-lite-report.md) | 중간 단계 100개 표본 결과 |
| [SWE-bench Trajectory 분석](reports/swe-bench-trajectory-analysis-500.md) | 모델별 에이전트 행동 경향성 |
| [공개 benchmark 기준표](benchmarks/benchmarks_baseline.md) | published 점수·단가 기준선 |

## 디렉토리 구성

| 디렉토리 | 내용 |
| --- | ---|
| `reports/` | 위 상세 리포트 원문. |
| `benchmarks/` | 공개 벤치마크 기준표. |
| `research/` | 벤치마크 리서치에 사용한 원본/참고 자료. |

> 평가 하네스·task·원시 산출물(`coding-bench/`)과 토큰 비용 분석은 로컬 전용으로 보관하며 이 저장소에는 포함되지 않습니다.
