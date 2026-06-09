# Microsoft Foundry 모델 코딩 벤치마크

Microsoft Foundry 에서 호출 가능한 모델들을 동일한 하네스·조건으로 비교한 코딩 성능 평가입니다. 공개 leaderboard 점수의 대체물이 아니라, **Azure 환경에서 같은 조건으로 측정한 실측 비교 지표**입니다.

평가는 성격이 다른 **두 축**으로 나뉘며, **대상 모델이 서로 다릅니다.**

- **Custom coding eval** (7개 모델) — 작고 독립적인 unit-test형 과제로 본 안정성·latency·비용 경향.
- **SWE-bench** (Verified-500 5개 모델) — 실제 GitHub repo 이슈를 패치하고 공식 테스트 통과로 채점하는 에이전트형 과제.

| 모델 | Custom eval | SWE-bench |
| --- | :---: | :---: |
| Claude Opus 4.8 | ✓ | 미실행 |
| GPT-5.5 | ✓ | 미실행 |
| Grok 4.3 | ✓ | ✓ |
| GLM-5.1 | ✓ | ✓ |
| Kimi K2.6 | ✓ | ✓ |
| MiniMax M2.5 | ✓ | ✓ |
| DeepSeek-V4-Pro | ✓ | ✓ |

## 결론

- 작은 함수형 코드 생성/수정은 **DeepSeek-V4-Pro·Claude Opus 4.8·GPT-5.5·Grok 4.3**이 강하고
- Repository patch형(SWE-bench Verified)은 **Kimi K2.6·DeepSeek-V4-Pro·MiniMax M2.5**가 강합니다. 
- 두 축을 모두 거친 5개 모델 중 **DeepSeek-V4-Pro만 양쪽 상위권**입니다.

> Claude Opus 4.8·GPT-5.5는 SWE-bench를 실행하지 않아 repository patch 성능이 *측정되지 않았습니다*. SWE-bench 순위는 신뢰구간이 겹쳐 경향성으로만 해석해야 합니다.

수치·해석·권장 사용 기준은 **[종합 리포트](reports/model-coding-benchmark-report.md)**를 참고하세요.

## 리포트

| 리포트 | 내용 |
| --- | --- |
| [종합 요약](reports/model-coding-benchmark-report.md) | 두 평가 축 결과 통합 + 용도별 모델 추천  |
| [Custom coding eval](reports/custom-coding-eval-report.md) | 작은 deterministic task 10개 × 5회 반복 (7개 모델) |
| [SWE-bench Verified-500](reports/swe-bench-verified-500-report.md) | Verified 전수 500개 — 가장 신뢰도 높은 기준 (5개 모델) |
| [SWE-bench Lite](reports/swe-bench-lite-report.md) | 중간 단계 100개 표본 결과 |
| [SWE-bench Trajectory 분석](reports/swe-bench-trajectory-analysis-500.md) | 모델별 에이전트 행동 경향성 |
| [SWE-bench 비용 분석](reports/swe-bench-cost-analysis.md) | 실측 토큰 기반 비용 경향 |
| [공개 benchmark 기준표](benchmarks/benchmarks_baseline.md) | published 점수·단가 기준선 |

## 디렉토리 구성

| 디렉토리 | 내용 |
| --- | ---|
| `reports/` | 위 리포트 원문. |
| `benchmarks/` | 공개 벤치마크 기준표. |
| `coding-bench/` | 평가 하네스와 task. `custom/`(커스텀 코딩 평가), `swe-bench/`(SWE-bench Lite/Verified)로 나뉨. |
| `research/` | 벤치마크 리서치에 사용한 원본/참고 자료. |
