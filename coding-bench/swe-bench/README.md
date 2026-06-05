# SWE-bench 벤치마크 하네스

Azure VM(`rg-model-benchmark`)의 `/opt/swebench/`에서 가져온 **직접 작성한 실행 코드** 전체 + Docker 없이 돌리는 로컬 proxy 평가입니다. 나중에 다시 돌릴 수 있도록 스크립트 / 프록시 / 패치 / 입력 데이터 / 결과 샘플 / 보존된 실행 산출물을 한곳에 정리했습니다.

SWE-bench Lite와 Verified를 모두 다룹니다. **Lite**는 `swe_run_100.sh`(공식 Docker) 또는 `swe_lite_patch_eval.py`(로컬 proxy)로, **Verified**는 `swe_run.sh`(첫 100) / `swe_run_rand.sh`(무작위 100)로 실행합니다. proxy·patches·data는 양쪽이 공유합니다.

> 결과 파일 형식 설명은 [`RESULTS-FORMAT.md`](./RESULTS-FORMAT.md) 참고.

## 폴더 구성

```
swe-bench/
├─ swe_lite_patch_eval.py            # 로컬 proxy 평가(Docker 불필요). diff 적용 가능 여부만 채점
├─ scripts/                          # VM 러너 (systemd-run으로 detached 실행)
│  ├─ swe_run_100.sh                 # SWE-bench Lite, test 첫 100개
│  ├─ swe_run.sh                     # SWE-bench Verified, test 첫 100개 (slice 0:100)
│  ├─ swe_run_rand.sh                # SWE-bench Verified, 무작위 100개 (seed=42, --filter 정규식)
│  ├─ fill.sh                        # 빈 패치(empty) 채우기 — lite|verified 공용
│  └─ fill_empties.sh               # 빈 패치 채우기 — lite 전용(구버전)
├─ proxy/
│  └─ azure_foundry_proxy.py         # OpenAI 호환 로컬 프록시(127.0.0.1:8000), 멀티리전 라운드로빈
├─ patches/
│  └─ harvest_diff_fallback.snippet.py  # mini-swe-agent에 적용한 harvest 패치(빈 패치 방지)
├─ data/
│  └─ rand100_ids.json               # seed=42 무작위 100개 instance_id (재현용)
├─ sample-results/                   # 결과 파일 실제 샘플
│  ├─ preds.single-entry.json
│  ├─ report.sample.json
│  └─ traj.keys.txt
└─ runs/
   └─ clean-swe-10-v2/               # 보존된 Lite 10개 샘플 실행 결과
```

## 로컬 proxy 평가 — `swe_lite_patch_eval.py`

Docker 없이, 모델이 생성한 unified diff가 gold-patch 대상 파일에 깨끗이 적용되고 기대 파일을 건드리는지를 보는 **proxy 평가**입니다(공식 SWE-bench Docker 채점이 아님). 루트의 공유 `models.local.json`을 사용합니다.

```powershell
python coding-bench\swe-bench\swe_lite_patch_eval.py --models coding-bench\models.local.json --out coding-bench\swe-bench\runs\<name> --count 10
```

보존 산출물: `runs/clean-swe-10-v2/` — 정리된 10개 샘플 실행 결과.

---

# VM 실행 코드 (공식 Docker 평가)

아래는 Azure VM 스냅샷이며, 스크립트 내부에서 `/opt/swebench/...` 절대경로를 사용합니다.

## VM ↔ 모델 매핑

| VM | 모델 alias | Azure 엔드포인트 / 리전 | TPM |
| --- | --- | --- | --- |
| `vm-swebench-eval` | `kimi-k2.6-foundry` | **멀티리전 풀**: eastus2 + eastus + westus3 + swedencentral + koreacentral | **500k (5×100k 라운드로빈)** |
| `vm-swebench-grok` | `grok-4.3-foundry` | eastus2 (`bench-grok-43`) | 500k |
| `vm-swebench-minimax` | `minimax-m2.5-foundry` | eastus (`bench-minimax-m25-eastus`) | 500k |
| `vm-swebench-glm` | `glm-5.1-foundry` | westus3 (`bench-glm-51-westus3`) | 500k |

- 워커 VM 3종은 `vm-swebench-eval` 스냅샷 클론이라 hostname이 모두 `vm-swebench-eval`로 보입니다(정상).
- `proxy/azure_foundry_proxy.py`의 `DEPLOYMENTS`가 alias→배포 라우트입니다. Kimi만 5개 라우트 리스트(라운드로빈, 429 시 다음 엔드포인트 폴오버), 나머지는 단일 엔드포인트. 각 워커 VM은 자기 모델만 사용합니다.

## 외부(stock) 구성 요소 — VM에 설치돼 있으나 직접 작성한 코드 아님

| 항목 | VM 경로 | 버전 |
| --- | --- | --- |
| mini-swe-agent (스캐폴드) | `/opt/swebench/mini-swe/.venv` | 2.3.0 |
| SWE-bench (공식 평가기) | `/opt/swebench/SWE-bench/.venv` | 4.1.0 |
| 에이전트 config | `.../minisweagent/config/benchmarks/swebench.yaml` | mini-swe-agent 2.3.0 기본값 |

`patches/harvest_diff_fallback.snippet.py`만 stock mini-swe-agent의
`minisweagent/run/benchmarks/swebench.py` `process_instance()` `finally` 블록에 직접 추가한 코드입니다.

## 사전 준비 (새 VM에서 재현 시)

1. Ubuntu VM + Docker + Python 3.12.
2. `/opt/swebench/`에 두 개의 venv 구성:
   - `mini-swe/.venv` → `pip install mini-swe-agent==2.3.0`
   - `SWE-bench/.venv` → 공식 `SWE-bench` 4.1.0 설치 (`python -m swebench.harness.run_evaluation` 사용).
3. `mini-swe/.venv`의 `minisweagent/run/benchmarks/swebench.py` `process_instance()` finally에
   `patches/harvest_diff_fallback.snippet.py` 내용을 병합 (빈 패치 방지).
   - **주의**: `_env.execute()`는 문자열이 아니라 **dict** `{"command": "..."}`를 받습니다.
4. VM 시스템 관리 identity에 사용할 Azure Foundry 계정들의 **Cognitive Services User** 역할 부여
   (프록시가 IMDS managed-identity 토큰으로 인증).
5. `scripts/`, `proxy/`, `data/rand100_ids.json`을 `/opt/swebench/`에 배치.

## 실행 방법

모든 장시간 작업은 **반드시** `systemd-run`으로 detached 실행하고, 상태는 짧은 폴링으로 확인합니다.
(레거시 `az vm run-command`로 sleep/blocking 루프를 돌리면 VM 슬롯이 잠겨 다른 명령이 전부 막힙니다.)

### SWE-bench Lite 100

```bash
systemd-run --unit=swebench100 --collect \
  --setenv=MODEL=kimi-k2.6-foundry --setenv=WORKERS=5 \
  --setenv=EVAL_WORKERS=8 --setenv=STEPS=150 \
  bash /opt/swebench/swe_run_100.sh
```

### SWE-bench Verified — 무작위 100 (대표 샘플, 권장)

```bash
systemd-run --unit=swebench-rand --collect \
  --setenv=MODEL=grok-4.3-foundry --setenv=WORKERS=4 \
  --setenv=EVAL_WORKERS=8 --setenv=STEPS=150 --setenv=MAXPASS=3 \
  bash /opt/swebench/swe_run_rand.sh
```

- `data/rand100_ids.json`이 있으면 그대로, 없으면 seed=42로 Verified-500에서 100개를 재추출합니다(결정적).
- `--filter '^(id1|id2|...)$'` 정규식으로 정확히 그 100개만 실행.

### 빈 패치 채우기 (필요 시)

```bash
# Verified
systemd-run --unit=swebench-vfill --collect \
  --setenv=MODEL=glm-5.1-foundry --setenv=SUBSET=verified \
  --setenv=STEPS=200 --setenv=WORKERS=4 --setenv=ROUNDS=2 \
  bash /opt/swebench/fill.sh
```

`fill.sh`는 preds에서 **빈 항목만** 제거 → 해당 instance dir 삭제 → 더 높은 `STEPS`로 재실행 → 재평가합니다.

### 진행 상황 확인 (non-blocking)

```bash
cat /opt/swebench/runs-randv100/<model>.status        # DONE 이면 완료
tail -n 30 /opt/swebench/runs-randv100/<model>.runner.log
```

## 환경 변수 요약

| 변수 | 기본값 | 의미 |
| --- | --- | --- |
| `MODEL` | (필수) | 프록시 alias (`kimi-k2.6-foundry` 등) |
| `WORKERS` | 4 | mini-swe-agent 동시 인스턴스 수 (Kimi는 5 권장 = 엔드포인트당 1) |
| `EVAL_WORKERS` | 8 | 공식 평가기 Docker 병렬 수 |
| `STEPS` | 150 | 에이전트 step_limit (빈 패치 줄이려면 200까지) |
| `MAXPASS` | 3 | 빈 항목 재시도 패스 수 (rand 러너) |
| `SEED` | 42 | 무작위 100 추출 시드 (rand 러너) |
| `SUBSET` | verified | `fill.sh` 대상 데이터셋 (`lite`\|`verified`) |

## 핵심 동작 원리

- **프록시** (`azure_foundry_proxy.py`): mini-swe-agent의 OpenAI Chat Completions 요청을 받아
  Azure Foundry `/openai/deployments/.../chat/completions`로 변환·전달. managed-identity 토큰 자동 갱신,
  429/401 재시도, Kimi는 여러 리전 라운드로빈으로 합산 TPM 확보.
- **harvest 패치**: 에이전트가 step_limit을 초과(`LimitsExceeded`)해도 컨테이너 안 `/testbed`의
  `git diff --cached`를 캡처해 빈 패치를 방지. 단, 에이전트가 실제로 파일을 수정한 경우에만 diff가 잡힙니다
  (전혀 수정 안 한 instance는 여전히 빈 패치 → `STEPS`를 올려 재시도해야 함).
- **0 empty 원칙**: 러너는 마지막에 누락 id를 빈 placeholder로 재삽입해 평가가 100개 전부를 보게 하고,
  `fill.sh`로 빈 항목을 끝까지 채웁니다.
