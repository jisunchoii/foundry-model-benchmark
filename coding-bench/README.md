# Coding bench 하네스

비싼 공개 벤치마크를 돌리기 전에 Foundry와 외부 엔드포인트를 비교하기 위한, 작고 재현 가능한 코딩 평가 하네스입니다. 평가는 성격이 다른 두 종류로 나뉩니다.

| 디렉터리 | 평가 | 무엇을 측정하나 |
| --- | --- | --- |
| [`custom/`](./custom/) | Custom coding eval | 작은 deterministic 단위테스트 과제(10개)를 격리 실행해 모델별 안정성·latency 비교. |
| [`swe-bench/`](./swe-bench/) | SWE-bench (Lite / Verified) | 실제 repo 이슈에 대한 patch 생성. VM 공식 Docker 평가 + 로컬 proxy 평가. 자세한 내용은 [`swe-bench/README.md`](./swe-bench/README.md). |

`models.example.json` / `models.local.json` 은 두 평가가 공유하는 모델 설정입니다. `models.example.json`을 `models.local.json`으로 복사한 뒤 배포별 값을 채웁니다. **비밀 값(secret)은 넣지 마세요.** API 키·엔드포인트 토큰은 환경 변수로 전달합니다.

지원하는 provider:

- `reference`: 로컬 하네스 검증을 위해 `reference/` 파일을 복사합니다.
- `azure_openai_chat`: Azure OpenAI 배포의 chat completions.
- `openai_compatible_chat`: 일반적인 OpenAI 호환 `/chat/completions` 엔드포인트.
- `databricks_chat`: Azure Databricks 모델 서빙 엔드포인트 또는 기타 ADB 방식의 OpenAI 호환 호출 엔드포인트.

---

## `custom/` — Custom coding eval

10개의 작은 코딩 task(`custom/tasks/`)를 격리된 임시 작업 디렉터리에서 실행합니다. 모델은 스타터 파일과 테스트를 받고, 변경된 파일을 담은 JSON을 반환하며, 하네스가 task 명령을 실행합니다. 명령이 종료 코드 0으로 끝나면 통과입니다.

### 빠른 검증 (dry-run)

```powershell
python custom\benchmark.py --models models.example.json --tasks custom\tasks --out custom\runs\dry-run --model dry-run-reference
```

`dry-run-reference` 모델은 각 task의 참조(reference) 솔루션을 복사하여 하네스·task 파일·채점 명령·출력 리포트가 제대로 동작하는지 검증합니다.

### 기대하는 모델 응답 형식

```json
{
  "files": {
    "solution.py": "complete file content"
  }
}
```

### 출력

각 실행은 `custom/runs/<name>/` 아래에 다음을 기록합니다:

- `results.jsonl`: 모델/task별 결과 1건씩.
- `summary.csv`: 압축된 지표.
- `summary.md`: 사람이 읽기 좋은 표.

### 보존된 실행 산출물

- `custom/runs/first-pass/` — 1차 커스텀 코딩 평가.
- `custom/runs/repeat-5x-all-models/` — 전체 모델 5회 반복(총 300회) 요약.

---

## `swe-bench/` — SWE-bench

실제 GitHub 저장소 이슈에 대한 patch 생성 평가. Lite와 Verified를 모두 다룹니다.

- **공식 Docker 평가**(Azure VM): `swe-bench/scripts/`의 러너로 실행. Lite 100 / Verified 첫 100 / Verified 무작위 100.
- **로컬 proxy 평가**(Docker 불필요): `swe-bench/swe_lite_patch_eval.py`. diff 적용 가능 여부만 빠르게 본다.

실행 방법·VM↔모델 매핑·결과 파일 형식은 [`swe-bench/README.md`](./swe-bench/README.md)와 [`swe-bench/RESULTS-FORMAT.md`](./swe-bench/RESULTS-FORMAT.md)를 참고하세요.
