# SWE-bench 토큰 사용 비용 분석

SWE-bench 실행에서 각 instance trajectory(`*.traj.json`)의 `extra.response.usage`에 기록된 **실제 청구 토큰**(API 콜마다 Azure AI Foundry가 반환한 실측값 — 추정/재토크나이즈 아님)을 모델별 단가로 환산한 비용입니다. reasoning 토큰은 API `completion_tokens`에 포함됩니다.

주 데이터셋은 **Verified(전수 500개)**이며, 기준 정확도는 [Verified 리포트](./swe-bench-verified-500-report.md) 참고.

## 단가 (Azure AI Foundry, $/1M tokens)

| 모델 | input | output | 캐시 | 검증 (2026-06) | Foundry 단가 출처 |
| --- | ---: | ---: | ---: | --- | --- |
| kimi-k2.6-foundry | 0.95 | 4.00 | 0.16 | ✅ Azure 일치 | [Kimi](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/kimi/) |
| minimax-m2.5-foundry | 0.30 | 1.20 | input×25% (근사) | ✅ in/out 일치 | 전용 페이지 미게시³ |
| grok-4.3-foundry | 1.25 | 2.50 | 0.20 | ✅ Azure 일치 | [Grok](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/grok/) |
| glm-5.1-foundry | 1.00 | 3.20 | input×25% (근사) | ⚠️ Azure GLM-5 근사(5.1 SKU 미확정) | 전용 페이지 미게시³ |
| deepseek-v4-pro-foundry | 1.74 | 3.48 | n/a² | ✅ Azure Foundry Global Standard | [DeepSeek](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/deepseek/) |

> Microsoft Foundry Models 단가 페이지: [DeepSeek](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/deepseek/) · [Grok (xAI)](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/grok/) · [Kimi (Moonshot)](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/kimi/). MiniMax·GLM은 2026-06 기준 전용 Azure Foundry 단가 페이지가 게시되지 않아(URL 404) 공급사 공식 단가(MiniMax 0.30/1.20, Z.AI GLM 1.00/3.20)를 사용했습니다.
>


비용은 두 가지로 제시합니다.

- **gross** = `prompt×in + completion×out` — 모든 prompt를 input 정가로 청구(캐시 할인 무시). 비용 **상한**.
- **cache-adj** = `(prompt−cached)×in + cached×cache_rate + completion×out` — 캐시 토큰에 캐시 단가 적용. **실청구 근사**.

> 캐시 단가가 공개 안 된 minimax·glm은 `cache_rate = input×25%`로 보수적 근사(실제 캐시 읽기 할인은 보통 input의 10~20%이므로 25%는 비용을 다소 높게 잡음). 건당 비용 = 버킷 총액 / 버킷 instance 수.
>
> ² DeepSeek-V4-Pro 단가는 [Azure AI Foundry Models 가격(DeepSeek)](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/deepseek/) Global Standard 기준 input $1.74 / output $3.48. 단, DeepSeek Foundry 응답이 `cached_tokens`를 보고하지 않아 **cache-adj는 산출 불가**하며 gross만 제시합니다(실제 캐시가 있었다면 gross는 과대 추정).
>
> ³ MiniMax·GLM은 전용 Azure Foundry 단가 페이지가 미게시(2026-06 확인, URL 404)되어 공급사 공식 단가를 적용했습니다 — 단가 검증은 위 표의 "검증" 열 참고.

---

## Verified

### resolved 케이스 (해결한 문제당)

| 모델 | resolved | prompt(M) | cache% | **gross 건당** | **cache-adj 건당** | gross 총액 | cache-adj 총액 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| MiniMax M2.5 | 369 | 299.1 | 96.9% | **$0.254** | **$0.077** | $93.7 | $28.4 |
| Grok 4.3 | 337 | 93.9 | 91.6% | **$0.353** | **$0.085** | $119.0 | $28.7 |
| Kimi K2.6 | 382 | 314.1 | 79.3% | **$0.821** | **$0.306** | $313.7 | $117.1 |
| GLM-5.1 | 331 | 458.0 | 92.7% | **$1.418** | **$0.456** | $469.4 | $151.0 |
| DeepSeek-V4-Pro | 372 | 349.6 | n/a | **$1.670** | — (gross only) | $621.3 | — |

### unresolved/empty 케이스 (참고)

| 모델 | n(traj) | gross 건당 | cache-adj 건당 |
| --- | ---: | ---: | ---: |
| MiniMax M2.5 | 130 | $0.544 | $0.160 |
| Grok 4.3 | 163 | $0.513 | $0.118 |
| Kimi K2.6 | 118 | $1.669 | $0.636 |
| GLM-5.1 | 115¹ | $2.942 | $0.911 |
| DeepSeek-V4-Pro | 128 | $2.780 | — (gross only) |

¹ GLM은 58개 빈 패치 instance에 trajectory가 없어 unresolved 비용에서 제외 — 실 비용은 다소 과소 집계.

### 전체 합계 (resolved + unresolved, 500개)

| 모델 | **gross 총액** | **cache-adj 총액** | resolved/500 | cache-adj $/resolved |
| --- | ---: | ---: | ---: | ---: |
| Grok 4.3 | $202.7 | **$48.0** | 337 | $0.142 |
| MiniMax M2.5 | $164.4 | **$49.2** | 369 | $0.133 |
| Kimi K2.6 | $510.7 | **$192.1** | 382 | $0.503 |
| GLM-5.1 | $807.7 | **$255.7** | 331 | $0.773 |
| DeepSeek-V4-Pro | **$977.1** | n/a³ | 372 | $2.627 (gross) |

---



## 핵심 관찰

- **실패가 더 비싸다** — unresolved 케이스가 resolved보다 건당 약 1.4~2.6배 비쌈(step_limit까지 더 많은 콜·컨텍스트 소모). "실패에 더 많은 돈이 든다"는 경향이 Lite-100·Verified-500 양쪽에서 일관.
- **input-bound 워크로드** — completion(출력 diff) 토큰은 prompt 대비 1% 미만. 총비용은 output 단가가 아니라 **input 단가 + 캐시 정책**이 좌우.
- **prompt 캐시 비중 75~97%** — 에이전트 루프가 매 콜마다 커지는 동일 컨텍스트를 재전송. 캐시 할인 적용 시 실청구는 gross의 30~40% 수준 ⇒ 비교는 cache-adj 컬럼이 현실적.
- **품질-비용 균형**:
  - **MiniMax·Grok**가 해결 건당 가장 저렴(Verified-500 $0.13~0.14/resolved). MiniMax는 낮은 input 단가(0.30)+96.9% 캐시, Grok은 적은 총 토큰(prompt 160M, 다른 모델의 1/3~1/5).
  - **Kimi**는 최고 해결률(382/500)이면서 중간 비용($0.50/resolved) — 품질-비용 균형 우수.
  - **GLM**이 가장 비쌈($0.77/resolved): 최다 토큰(789M) + 높은 단가(1.00) + 58 빈 패치로 resolved 분모 작음.
  - **DeepSeek-V4-Pro**는 gross 기준 $2.63/resolved로 표면상 가장 비싸 보이나, 이는 **캐시 할인을 전혀 적용 못 한 gross 상한**(Foundry가 cached_tokens 미보고)이라 타 모델의 cache-adj와 직접 비교는 부적절합니다. 다른 모델도 gross로 보면 $0.25~$2.44이므로 DeepSeek의 실청구는 캐시가 있었다면 더 낮을 수 있습니다.

⇒ **정확도 최우선이면 Kimi, 비용 최우선이면 MiniMax/Grok.** GLM은 정확도 상위권이지만 비용 효율이 가장 낮습니다. DeepSeek는 캐시 보고 부재로 비용 비교가 제한적입니다.

---

## 방법론

- **토큰 출처**: 각 instance `*.traj.json`의 모든 assistant 메시지 `extra.response.usage`에서 `prompt_tokens`, `completion_tokens`, `prompt_tokens_details.cached_tokens`를 합산. Azure Foundry가 콜마다 반환한 실측 청구 토큰(사후 추정/재토크나이즈 아님). 한 instance는 수십 콜로 구성되며 콜별 usage를 모두 합산해 instance 단위로 만듦. 메시지 컨테이너는 `messages`/`trajectory` 키 모두 처리, usage 없는 system/user 메시지는 건너뜀.
- **resolved 판정**: 공식 평가기 `swebench.harness.run_evaluation`가 만든 `<model>.report.json`의 `resolved_ids` 기준으로 resolved/other(unresolved+empty) 버킷 분류.
- **계산식**: gross = `prompt×in + completion×out`; cache-adj = `(prompt−cached)×in + cached×cache_rate + completion×out`. 단가는 위 표(/1M).
- **검증**: ① 버킷 합 = 전체 합(예: Kimi gross $313.7 + $196.9 = $510.7), ② traj 수 = preds 수(GLM 446 = 500−58 empty, MiniMax 499 = 500−1 empty), ③ resolved n = 공식 리포트 `resolved_instances`(예: Kimi 382).

### 한계 / 주의

- **DeepSeek-V4-Pro는 gross만 산출** — 단가는 Azure Foundry Global Standard input $1.74 / output $3.48([출처](https://azure.microsoft.com/en-us/pricing/details/ai-foundry-models/deepseek/))로 확정됐으나, DeepSeek Foundry 응답이 `cached_tokens`를 보고하지 않아 **cache-adj 불가**. gross = $977.1(prompt 550.3M × 1.74 + completion 5.66M × 3.48). 실제 캐시가 있었다면 실청구는 이보다 낮음. (³ 전체합계 표의 n/a 캐시 주석과 동일.)
- **GLM unresolved 과소 집계** — 빈 패치 58개에 traj가 없어 unresolved 비용 일부 누락.
- **캐시 단가 근사** — minimax·glm은 실제 캐시 단가 미공개로 input×25% 근사 → 두 모델 cache-adj는 실청구보다 다소 높게 잡힘.
- **Foundry 실청구 변동** — PTU-시간/계약·지역 단가에 따라 카탈로그 단가와 달라질 수 있음. 단가 확인 시점 2026-06.

## 교차 참조

- Verified 리포트: [swe-bench-verified-500-report.md](./swe-bench-verified-500-report.md)
- SWE-bench Lite 리포트: [swe-bench-lite-report.md](./swe-bench-lite-report.md)
- Published 단가 기준선: [benchmarks_baseline.md](../benchmarks/benchmarks_baseline.md)
