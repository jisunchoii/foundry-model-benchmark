# SWE-bench Lite 벤치마크 리포트

## SWE-bench란

SWE-bench는 실제 GitHub 오픈소스 저장소(django, scikit-learn, astropy 등)의 **진짜 이슈와 그걸 해결한 실제 PR**에서 문제를 만든 코딩 에이전트 평가 벤치마크입니다. 인위적 함수 문제가 아니라 현실 버그를 다루고, 사람이 채점하지 않고 **해당 프로젝트의 실제 테스트 통과 여부로 자동 채점**합니다.

### 한 문제(task)의 구조

- **입력**: 이슈 발생 시점의 저장소 코드 스냅샷 + 이슈 설명(GitHub issue 텍스트)
- **모델이 할 일**: 코드베이스를 탐색해 수정 위치를 찾고 패치(diff) 생성
- **채점**: 프로젝트 테스트 스위트 실행 -> 버그 재현 테스트(FAIL->PASS)가 통과하고 기존 테스트(PASS->PASS)가 안 깨지면 resolved

> 단순 코드 생성이 아니라 탐색 -> 원인 파악 -> 최소 수정 -> 회귀 방지까지 요구하는 에이전트형 과제입니다. 그래서 점수는 모델 단독 능력 + 에이전트 스캐폴드(여기서는 `mini-swe-agent`) 설계의 합작입니다.

## SWE-bench Verified와 이번 실험의 차이

SWE-bench Verified 점수는 human-validated 500개 GitHub issue task 중 모델/에이전트 시스템이 repository를 수정해 official test를 통과한 비율입니다. 예를 들어 Verified 75.8은 약 379/500 task resolved를 의미합니다.

이번 실험은 Verified 전체가 아니라 **SWE-bench Lite test split의 첫 10개 instance 파일럿**과 이를 **첫 100개 instance로 확장한 실험**입니다. Public leaderboard 점수와 직접 비교하면 안 되고, 동일 조건의 소규모/중규모 비교로 해석해야 합니다.

## 실험 구성

| 항목 | Clean-10 파일럿 | 100-instance 확장 실험 |
| --- | --- | --- |
| Dataset | `SWE-bench/SWE-bench_Lite` | `SWE-bench/SWE-bench_Lite` |
| Split | `test` | `test` |
| Sample | 첫 10개 instance | 첫 100개 instance (`slice 0:100`) |
| Scaffold | `mini-swe-agent` | `mini-swe-agent` (Clean-10과 동일 invocation) |
| Environment | Docker on Azure Ubuntu VM | Docker on Azure Ubuntu VM (모델별 전용 VM) |
| Temperature | - | 0 |
| Scoring | official `swebench.harness.run_evaluation`, `resolved_ids` | official `swebench.harness.run_evaluation` |

100-instance 확장 실험에서는 4개 모델을 모델별 전용 VM/엔드포인트에 분산해 병렬 실행했습니다. 각 모델은 서로 다른 Azure Foundry 엔드포인트/리전을 사용해 쿼터 경합이 없습니다(Grok/MiniMax/GLM 각 500k TPM, Kimi 100k TPM).

## 결과 요약

### Clean-10 파일럿 결과

| 모델 | Submitted | Completed | Resolved | Unresolved | Empty patches | Errors | Resolved / submitted |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Kimi K2.6 Foundry | 10 | 10 | 7 | 3 | 0 | 0 | 70.0% |
| GLM-5.1 Foundry | 10 | 10 | 6 | 4 | 0 | 0 | 60.0% |
| Grok 4.3 Foundry | 10 | 10 | 5 | 5 | 0 | 0 | 50.0% |
| MiniMax M2.5 Foundry | 10 | 10 | 5 | 5 | 0 | 0 | 50.0% |

### 100-instance 확장 결과

| 모델 | Submitted | Resolved | Resolved/100 | Empty patches | Errors | 95% CI (Wilson) |
| --- | ---: | ---: | ---: | ---: | ---: | :---: |
| **Kimi K2.6 Foundry** | 100 | **74** | **74.0%** | 0 | 0 | [64.6, 81.6] |
| **GLM-5.1 Foundry** | 100 | **68** | **68.0%** | 0 | 0 | [58.3, 76.3] |
| **Grok 4.3 Foundry** | 100 | **64** | **64.0%** | 0 | 0 | [54.2, 72.7] |
| **MiniMax M2.5 Foundry** | 100 | **61** | **61.0%** | 0 | 0 | [51.2, 70.0] |

## 파일럿 대비 100-instance 비교

| 모델 | Clean-10 (resolved/10) | 100-run (resolved/100) | 비고 |
| --- | :---: | :---: | --- |
| Kimi K2.6 | 7/10 (70%) | 74/100 (74%) | 파일럿 1위 -> 100개에서도 1위 유지 |
| GLM-5.1 | 6/10 (60%) | 68/100 (68%) | 10개 표본 대비 소폭 상승, 2위 유지 |
| Grok 4.3 | 5/10 (50%) | 64/100 (64%) | 표본 확대 시 상대적으로 크게 상승 |
| MiniMax M2.5 | 5/10 (50%) | 61/100 (61%) | 표본 확대 시 상승 |

## 해석

- Clean-10 파일럿에서는 Kimi K2.6이 7/10으로 가장 높고, GLM-5.1이 6/10으로 뒤를 이었습니다. Grok 4.3과 MiniMax M2.5는 5/10으로 동률입니다.
- 단, Clean-10은 10개 샘플이므로 전체 SWE-bench Lite나 Verified 성능으로 일반화하면 안 됩니다.
- 100-instance 확장 실험에서도 **Kimi K2.6가 74%로 1위**, 이어 GLM-5.1(68%), Grok 4.3(64%), MiniMax M2.5(61%) 순입니다. 파일럿 1위였던 Kimi가 100개로 확장해도 선두를 유지했습니다.
- 다만 95% 신뢰구간이 서로 **크게 겹칩니다**(예: Kimi [64.6, 81.6] vs GLM [58.3, 76.3] vs MiniMax [51.2, 70.0]). 100개 표본에서는 +/- 약 9~10%p 폭이라, 모델 간 차이는 **통계적으로 확정적이지 않습니다**. 순위는 경향성으로만 해석해야 합니다.
- 10개 파일럿 순위(Kimi > GLM > Grok = MiniMax)와 비교하면 상위/하위 경향은 유지되되, 100개에서는 모델 간 격차가 다소 좁아졌습니다.

## 산출물 경로

### Clean-10 파일럿

| 항목 | 경로 |
| --- | --- |
| Clean run 리포트 | `C:\Users\jisunchoi\projects\foundry-model-coding-benchmark\coding-bench\swe-bench\runs\clean-swe-10-v2\clean-swe-report.md` |
| Clean run 요약 CSV | `C:\Users\jisunchoi\projects\foundry-model-coding-benchmark\coding-bench\swe-bench\runs\clean-swe-10-v2\clean-swe-summary.csv` |
| Official reports JSON | `C:\Users\jisunchoi\projects\foundry-model-coding-benchmark\coding-bench\swe-bench\runs\clean-swe-10-v2\official-reports.json` |

### 100-instance 확장 실험 (VM)

| 항목 | 경로 |
| --- | --- |
| 모델별 예측 | `/opt/swebench/runs-100/<model>/preds.json` |
| 공식 평가 리포트 | `/opt/swebench/runs-100/official-results/<model>.report.json` |
| Trajectory 로그 (blob) | `<storage-account>` / `swebench-logs` / `lite-100/<model>.traj.tar.gz` |

---

_최종본: Clean-10 파일럿과 100-instance 확장 실험 통합본._

