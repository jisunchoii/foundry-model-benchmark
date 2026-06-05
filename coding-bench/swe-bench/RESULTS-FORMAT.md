# 결과 파일 형식 (Result file formats)

각 러너는 VM의 `/opt/swebench/` 아래에 run 디렉터리를 만듭니다.
실행 종류별 run root:

| 실행 | run root |
| --- | --- |
| Lite 100 (`swe_run_100.sh`) | `/opt/swebench/runs-100/` |
| Verified 첫 100 (`swe_run.sh`) | `/opt/swebench/runs-verified/` |
| Verified 무작위 100 (`swe_run_rand.sh`) | `/opt/swebench/runs-randv100/` |

## 디렉터리 레이아웃

```
runs-randv100/
├─ <model>/                          # 예: grok-4.3-foundry/
│  ├─ preds.json                     # ← 제출 예측(핵심 산출물)
│  ├─ <instance_id>/                 # instance당 하나, 예: django__django-15268/
│  │  └─ <instance_id>.traj.json     # 에이전트 trajectory (~180KB)
│  └─ ...                            # (100개 instance 디렉터리)
├─ official-input/<model>.json       # 평가기에 넘긴 preds 사본
├─ official-results/<model>.report.json   # ← 공식 채점 결과(핵심 산출물)
├─ <model>.status                    # "DONE" (러너 완료 마커)
├─ <model>.runner.log                # 러너 로그
└─ <model>.runner.status             # systemd 유닛 상태
```

빈 패치 채우기를 돌리면 `<model>.fill.log`, `<model>.fillstatus` (`FILLED`)도 생깁니다.

---

## 1. `preds.json` — 모델 예측 (제출물)

SWE-bench 평가기에 넣는 입력. `instance_id`를 키로 하는 **dict** 또는 객체의 **list** 형태.
각 엔트리 필드:

| 필드 | 의미 |
| --- | --- |
| `model_name_or_path` | 예측을 만든 모델 (예: `openai/kimi-k2.6-foundry`) |
| `instance_id` | SWE-bench instance id (예: `astropy__astropy-14365`) |
| `model_patch` | 모델이 만든 **unified diff**. 평가기가 `/testbed`에 적용해 테스트를 돌림 |

실제 샘플: [`sample-results/preds.single-entry.json`](./sample-results/preds.single-entry.json)

```json
{
  "model_name_or_path": "openai/kimi-k2.6-foundry",
  "instance_id": "astropy__astropy-14365",
  "model_patch": "diff --git a/astropy/io/ascii/qdp.py b/astropy/io/ascii/qdp.py\n--- a/astropy/io/ascii/qdp.py\n+++ b/astropy/io/ascii/qdp.py\n@@ -68,7 +68,7 @@ ...\n-    _line_type_re = re.compile(_type_re)\n+    _line_type_re = re.compile(_type_re, re.IGNORECASE)\n ..."
}
```

> `model_patch`가 빈 문자열(`""`)이면 **empty patch** → 자동으로 unresolved. 0 empty가 목표이며
> harvest 패치 + `fill.sh`가 이를 막습니다.

---

## 2. `<model>.report.json` — 공식 채점 결과

`swebench.harness.run_evaluation`이 생성. 벤치마크의 **최종 점수**입니다.

실제 샘플: [`sample-results/report.sample.json`](./sample-results/report.sample.json) (Kimi Lite-100, 74/100)

| 필드 | 의미 |
| --- | --- |
| `total_instances` | 대상 instance 수 (100) |
| `submitted_instances` | 제출된 예측 수 |
| `completed_instances` | 평가가 끝난 수 |
| `resolved_instances` | **테스트 통과 = 해결한 수 (점수)** |
| `unresolved_instances` | 미해결 수 |
| `empty_patch_instances` | 빈 패치 수 (0이어야 함) |
| `error_instances` | 평가 에러 수 |
| `resolved_ids[]` | 해결한 instance id 목록 |
| `unresolved_ids[]` | 미해결 instance id 목록 |
| `empty_patch_ids[]` | 빈 패치 id 목록 |
| `error_ids[]` | 에러 id 목록 |
| `schema_version` | 리포트 스키마 버전 (2) |

```json
{
  "total_instances": 100,
  "submitted_instances": 100,
  "completed_instances": 100,
  "resolved_instances": 74,
  "unresolved_instances": 26,
  "empty_patch_instances": 0,
  "error_instances": 0,
  "resolved_ids": ["astropy__astropy-12907", "..."],
  "unresolved_ids": ["astropy__astropy-7746", "..."],
  "empty_patch_ids": [],
  "error_ids": [],
  "schema_version": 2
}
```

**점수 = `resolved_instances` / `total_instances`** (예: 74/100 = 74%).

---

## 3. `<instance_id>.traj.json` — 에이전트 trajectory

mini-swe-agent가 instance마다 남기는 전체 상호작용 기록 (디버깅·재현용, ~180KB).

최상위 키: `info`, `messages`, `trajectory_format`, `instance_id`

| 키 | 내용 |
| --- | --- |
| `info.exit_status` | 종료 사유 (`Submitted`, `LimitsExceeded`, `...+HarvestedDiff` 등) |
| `info.submission` | 최종 제출 패치(= preds의 `model_patch` 원본) |
| `info.model_stats` | 토큰/호출 통계 |
| `info.config` | 실행 config 스냅샷 |
| `info.mini_version` | mini-swe-agent 버전 |
| `messages[]` | system/user/assistant/tool 메시지 시퀀스 (에이전트 루프 전체) |
| `instance_id` | instance id |

`messages[0]` = system 프롬프트(`"You are a helpful assistant that can interact with a computer shell..."`).

샘플 키 덤프: [`sample-results/traj.keys.txt`](./sample-results/traj.keys.txt)

---

## 결과 백업 (blob)

최종 trajectory는 tar로 묶어 storage account `<storage-account>` 컨테이너 `swebench-logs`에 업로드합니다:

- Lite: `lite-100/<model>.traj.tar.gz`
- Verified 첫 100: `verified-100/<model>.traj.tar.gz`
- Verified 무작위 100: `verified-randv100/<model>.traj.tar.gz`

> 업로드는 user-delegation SAS + `curl PUT`(`x-ms-blob-type: BlockBlob`, 기대 응답 201).
> 계정이 `allowSharedKeyAccess=false`라 모든 접근은 Entra ID(`--auth-mode login`) 필요.
