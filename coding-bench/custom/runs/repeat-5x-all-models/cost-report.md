# 5x repeat custom coding eval — 비용 리포트

`repeat-5x-all-summary.csv`의 토큰 usage에 모델별 공개 단가를 적용한 비용 추정입니다. 원본 수치는 [`cost-estimates.csv`](./cost-estimates.csv)에 컬럼으로 들어 있습니다.

> ⚠️ 추정치입니다. 각 모델 **공급사 공개 단가**를 적용한 값이며 실제 Azure Foundry/Databricks 청구와 다릅니다(예: gpt-5.5는 실제로 PTU-hour 과금, 일부 Foundry 모델은 공개 단가 미노출). 모델 간 **상대 비교용 proxy**로만 해석하세요.

## 계산식

```
estimated_token_cost_usd
  = prompt_tokens / 1e6 * input_usd_per_mtok
  + estimated_billed_output_tokens / 1e6 * output_usd_per_mtok

estimated_cost_per_pass_usd = estimated_token_cost_usd / passed
```

- 토큰 수는 호출별 모델 API 응답의 `usage`에서 집계합니다(50콜 = 10 task × 5회 반복).
- `estimated_billed_output_tokens`는 **grok만** `visible_completion_tokens`와 다릅니다. reasoning(사고) 토큰이 응답 텍스트엔 안 보여도 과금되므로 `completion_tokens_details.reasoning_tokens`까지 합산합니다(9,700 → 79,075). 나머지 모델은 visible과 동일합니다.

## 단가 (per-MTok, USD)

| 모델 | input $/MTok | output $/MTok | 출처 |
| --- | ---: | ---: | --- |
| claude-opus-4.8-adb | 5.0 | 25.0 | Anthropic 공개 단가 (ADB 계약은 다를 수 있음) |
| gpt-5.5-foundry | 5.0 | 30.0 | OpenAI 공개 API (실제 Azure는 PTU-hour 과금) |
| grok-4.3-foundry | 1.25 | 2.5 | xAI 공식 공개 단가 |
| glm-5.1-foundry | 1.4 | 4.4 | Z.AI/Fireworks 공식 단가 |
| kimi-k2.6-foundry | 0.95 | 4.0 | Kimi 공식 API 단가 |
| minimax-m2.5-foundry | 0.3 | 1.2 | MiniMax 공식 API 단가 |

## 결과

| 모델 | Passed | Calls | Prompt tok | Billed output tok | Est. token cost | Est. cost/pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-opus-4.8-adb | 50 | 50 | 29,390 | 16,163 | $0.551025 | $0.011020 |
| gpt-5.5-foundry | 50 | 50 | 17,940 | 22,371 | $0.760830 | $0.015217 |
| grok-4.3-foundry | 50 | 50 | 17,470 | 79,075 | $0.219525 | $0.004391 |
| glm-5.1-foundry | 46 | 50 | 17,490 | 53,954 | $0.261884 | $0.005693 |
| kimi-k2.6-foundry | 38 | 50 | 14,174 | 89,458 | $0.371297 | $0.009771 |
| minimax-m2.5-foundry | 36 | 50 | 18,410 | 44,602 | $0.059045 | $0.001640 |

## 해석

- **cost/pass**(통과 1건당 추정 비용)가 비용 효율의 핵심 지표입니다. 통과율이 낮으면 같은 토큰을 써도 통과당 비용이 올라갑니다.
- **minimax-m2.5**가 통과당 $0.0016으로 가장 저렴하지만 통과율이 72%로 가장 낮습니다 — 싼 대신 재시도 부담이 큽니다.
- **gpt-5.5**는 통과율 100%지만 output 단가($30/MTok)가 높아 통과당 $0.0152로 가장 비쌉니다.
- **grok-4.3**는 통과율 100%이면서 통과당 $0.0044로, 안정성과 비용 효율을 함께 보면 균형이 좋습니다(단, reasoning 토큰 과금으로 billed output이 visible의 8배).
- 단, 이건 토큰 비용만 본 것입니다. 실제 청구에는 PTU/VM 시간·스토리지가 더해지므로 절대 금액이 아니라 **모델 간 경향**으로만 보세요.
