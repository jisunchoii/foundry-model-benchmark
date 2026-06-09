# SWE-bench Verified 벤치마크 리포트

## 개요

이 리포트는 **SWE-bench Verified**의 **전체 500개 instance**에 대한 5개 Foundry 코딩 모델의 결과입니다. mini-swe-agent 스캐폴드 + 공식 평가기(`swebench.harness.run_evaluation`)를 사용했고, 모델별 전용 Azure Ubuntu VM/Foundry 엔드포인트에서 실행했습니다.



## 실험 구성

| 항목 | 값 |
| --- | --- |
| Dataset | `SWE-bench/SWE-bench_Verified` |
| Split | `test` (전체 500개) |
| Sample | 500/500 (전수) |
| 저장소 분포 | 공식 Verified-500 분포 (django 최다, 그 외 sympy·scikit-learn·sphinx·matplotlib·astropy·xarray·pytest·pylint·requests·seaborn·flask 등 12개 저장소) |
| Scaffold | `mini-swe-agent` |
| Environment | Docker on Azure Ubuntu VM (모델별 전용) |
| Step limit | STEPS=150 (DeepSeek·GLM은 hard instance 수렴을 위해 300으로 상향) |
| Temperature | 0 (단일 시도, MAXPASS=3 빈 패치 prune-retry) |
| 빈 패치 방지 | `HARVEST_DIFF_FALLBACK` |
| Scoring | official `swebench.harness.run_evaluation` |

## 결과 요약 (resolved/500, 내림차순)

| 순위 | 모델 | Resolved | Resolved/500 | Unresolved | Empty | Error | 95% CI (Wilson) |
| :---: | --- | ---: | ---: | ---: | ---: | ---: | :---: |
| 1 | **Kimi K2.6 Foundry** | **382** | **76.4%** | 118 | 0 | 0 | [72.5, 79.9] |
| 2 | **DeepSeek-V4-Pro Foundry** | **372** | **74.4%** | 128 | 0 | 0 | [70.4, 78.0] |
| 3 | **MiniMax M2.5 Foundry** | **369** | **73.8%** | 130 | 1 | 0 | [69.8, 77.5] |
| 4 | **Grok 4.3 Foundry** | **337** | **67.4%** | 163 | 0 | 0 | [63.2, 71.4] |
| 5 | **GLM-5.1 Foundry** | **331** | **66.2%** | 111 | 58 | 0 | [61.9, 70.2] |

- **Error = 0 (전 모델)**: 모든 500개 instance가 공식 평가기에서 정상 채점되었습니다
- **Empty**: non-empty 패치를 제출하지 못한 건수. GLM 58, MiniMax 1은 모델이 결정론적으로 "수정 불필요"로 판단해 빈 패치를 제출한 케이스로, **사용자 승인 정책에 따라 500 분모에서 unresolved로 집계**했습니다. 나머지 모델은 empty=0.

## 해석

- 전체 500개 기준 순위는 **Kimi K2.6(76.4%) > DeepSeek-V4-Pro(74.4%) > MiniMax M2.5(73.8%) > Grok 4.3(67.4%) > GLM-5.1(66.2%)** 입니다.
- **상위 3개(Kimi·DeepSeek·MiniMax)는 95% 신뢰구간이 크게 겹쳐 통계적으로 동률 구간**입니다(76.4 vs 74.4 vs 73.8%). 순위는 경향성으로만 해석해야 합니다.
- **Grok·GLM은 하위 그룹**으로, 상위 3개와는 CI가 거의 겹치지 않아(Kimi 하한 72.5% > Grok 상한 71.4%) 다소 분리됩니다.
- **표본 확대 효과**: 100개 → 500개로 늘리면서 신뢰구간이 ±8~9%p → ±4%p로 좁아져 순위 신뢰도가 높아졌습니다. random-100에서 동률이던 Grok(71%)이 500개에서는 하위로 분리됐습니다.
- **GLM의 58 empty**: GLM은 결정론적으로 빈 패치를 제출하는 instance가 58개로, 이를 제외한 442개 기준 해결률은 331/442=74.9%로 상위 그룹과 유사합니다. 다만 표준 관례(resolved/500)를 따라 66.2%로 보고합니다.

## Published Verified 점수와 비교 

| 모델 | 본 Verified-500 | Published Verified (출처) | 차이 |
| --- | ---: | ---: | ---: |
| Kimi K2.6 | 76.4% | 80.2% (공식 리더보드) | −3.8%p |
| DeepSeek-V4-Pro | 74.4% | N/A | — |
| MiniMax M2.5 | 73.8% | 75.8% (자가보고/리더보드) | −2.0%p |
| Grok 4.3 | 67.4% | N/A | — |
| GLM-5.1 | 66.2% | 77.8% (자가보고, GLM-5) | −11.6%p |

> **비교 주의사항**:
> - **미니멀 스캐폴드**: mini-swe-agent는 리더보드 상위 제출에 쓰이는 정교한 에이전트 스캐폴드보다 단순합니다.
> - **단일 시도, temp=0**: best-of-N·다중 롤아웃 없이 1회 시도.
> - **Foundry MaaS**: Azure Foundry 매니지드 엔드포인트.
> - **GLM 갭이 큰 이유**: published 77.8%는 `GLM-5`(상위 SKU) 자가보고이고 본 실험은 Foundry의 `GLM-5.1` 배포입니다. 또한 GLM은 58개의 결정론적 빈 패치(분모에 포함)가 점수를 약 12%p 끌어내립니다. 빈 패치 제외 시 74.9%로 갭이 −2.9%p로 줄어듭니다.
> - Kimi·MiniMax는 −2~4%p로 위 조건 차이를 감안하면 published 수치를 **양호하게 재현**합니다.



## 토큰 사용 비용 (전체 500개 실행)

모델별 전체 500개 실행의 **실제 청구 토큰**(traj `extra.response.usage` 합산)을 Azure Foundry 단가로 환산했습니다. 이 워크로드는 압도적으로 input-bound(완성 토큰 < prompt의 1.5%)이며, prompt 캐시 비중이 79~97%로 매우 높습니다.

- **gross**: 모든 prompt 토큰을 input 정가로 청구 (캐시 할인 무시 → 상한).
- **cache-adj**: cached 토큰에 캐시 단가 적용 (kimi $0.16, grok $0.20; minimax·glm은 input의 25%로 보수적 근사) → **실청구에 가까운 값**.

| 모델 | input/output ($/1M) | prompt(M) | cache% | **gross 총액** | **gross /resolved** | **cache-adj 총액** | **cache-adj /resolved** |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MiniMax M2.5 | 0.30 / 1.20 | 526.2 | 97.3% | $164.4 | $0.445 | **$49.2** | **$0.133** |
| Grok 4.3 | 1.25 / 2.50 | 160.0 | 92.1% | $202.7 | $0.601 | **$48.0** | **$0.142** |
| Kimi K2.6 | 0.95 / 4.00 | 512.2 | 78.7% | $510.7 | $1.337 | **$192.1** | **$0.503** |
| GLM-5.1 | 1.00 / 3.20 | 788.8 | 93.3% | $807.7 | $2.440 | **$255.7** | **$0.773** |
| DeepSeek-V4-Pro | 1.74 / 3.48 | 550.3 | n/a¹ | $977.1 | $2.627 | — ¹ | — ¹ |

¹ DeepSeek Foundry 응답 형식은 `prompt_tokens_details.cached_tokens`를 채우지 않아 캐시율이 0으로 집계됩니다(실제 캐시 미사용이 아닐 수 있음) → **cache-adj 산출 불가, gross만 제시**. 단가는 [Azure AI Foundry 가격(DeepSeek)](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/deepseek/) Global Standard input $1.74 / output $3.48 기준. gross = prompt 550.3M × 1.74 + completion 5.66M × 3.48 = $977.1.

### 비용 핵심 관찰

- **MiniMax·Grok가 해결 건당 가장 저렴**($0.13~0.14, cache-adj). MiniMax는 낮은 input 단가(0.30) + 97% 캐시, Grok은 적은 총 토큰(prompt 160M, 다른 모델의 1/3) 덕분.
- **GLM이 해결 건당 가장 비쌈**($0.77). 가장 많은 토큰(789M prompt) + 높은 단가(1.00) + 58 빈 패치로 분모(resolved) 작음.
- **Kimi**는 중상위 비용($0.50/resolved)이지만 **최고 해결률**이라 품질-비용 균형이 좋습니다.
- output 토큰은 prompt의 1% 미만 — 총비용은 **input 단가 + 캐시 정책**이 좌우합니다.


## 산출물 경로

모델별 예측(`preds.500.json`)·공식 평가 리포트(`official-results/<model>.report.500.json`)·trajectory 로그는 각 모델 전용 VM의 `/opt/swebench/runs-verified/<model>/`에 보존되어 있습니다.

Trajectory 아카이브(Blob `swebench-logs/`):

| 모델 | Blob 경로 |
| --- | --- |
| Kimi K2.6 | `verified-500/kimi-k2.6-foundry.traj.tar.gz` |
| DeepSeek-V4-Pro | `verified-500/deepseek-v4-pro-foundry.traj.tar.gz` |
| MiniMax M2.5 | `verified-500/minimax-m2.5-foundry.traj.tar.gz` |
| Grok 4.3 | `verified-500/grok-4.3-foundry.traj.tar.gz` |
| GLM-5.1 | `verified-500/glm-5.1-foundry.traj.tar.gz` |

## 교차 참조

- **토큰 비용 상세 분석**: [swe-bench-cost-analysis.md](./swe-bench-cost-analysis.md)
- SWE-bench Lite 결과: [swe-bench-lite-report.md](./swe-bench-lite-report.md)
- Trajectory 분석(500 전수): [swe-bench-trajectory-analysis-500.md](./swe-bench-trajectory-analysis-500.md)
- Published 기준선: [benchmarks_baseline.md](../benchmarks/benchmarks_baseline.md)
