import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from datasets import load_dataset


SYSTEM_PROMPT = """You are solving a SWE-bench Lite issue.
Return only JSON with this exact shape:
{"patch":"<unified git diff patch>"}
The patch must be a unified diff relative to the repository root.
Do not include markdown fences or explanations."""


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def az_access_token(scope=None, resource=None):
    az = shutil.which("az") or shutil.which("az.cmd") or r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    command = [az, "account", "get-access-token", "--query", "accessToken", "--output", "tsv"]
    if resource:
        command.extend(["--resource", resource])
    else:
        command.extend(["--scope", scope])
    result = subprocess.run(command, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def http_json(url, headers, payload, timeout):
    data = json.dumps(payload).encode("utf-8")
    waits = [20, 45, 90, 120]
    for attempt in range(len(waits) + 1):
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 429 and attempt < len(waits):
                retry_after = exc.headers.get("Retry-After")
                try:
                    wait = int(retry_after) if retry_after else waits[attempt]
                except ValueError:
                    wait = waits[attempt]
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {exc.code} from {url}: {body[:2000]}") from exc


def add_generation_params(payload, model):
    if "temperature" in model:
        payload["temperature"] = model["temperature"]
    if "max_completion_tokens" in model:
        payload["max_completion_tokens"] = max(model["max_completion_tokens"], 8192)
    elif "max_tokens" in model:
        payload["max_tokens"] = max(model["max_tokens"], 8192)


def messages(user_prompt):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
        if fenced:
            text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            obj, _ = json.JSONDecoder().raw_decode(text)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            pass
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        diff_block = re.search(r"```(?:diff|patch)?\s*(diff --git .*?|--- a/.*?)```", text, re.DOTALL)
        if diff_block:
            return {"patch": diff_block.group(1).strip() + "\n"}
        diff_start = text.find("diff --git ")
        if diff_start == -1:
            diff_start = text.find("--- a/")
        if diff_start != -1:
            return {"patch": text[diff_start:].strip() + "\n"}
        raise


def call_azure_openai_chat(model, user_prompt):
    endpoint = (model.get("endpoint") or os.environ.get(model.get("endpoint_env", ""), "")).rstrip("/")
    if not endpoint:
        raise RuntimeError("Missing Azure OpenAI endpoint")
    deployment = model["deployment"]
    api_version = model.get("api_version", "2025-04-01-preview")
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"
    headers = {"Content-Type": "application/json"}
    if model.get("auth") == "aad":
        headers["Authorization"] = f"Bearer {az_access_token('https://cognitiveservices.azure.com/.default')}"
    else:
        key = os.environ.get(model.get("api_key_env", "AZURE_OPENAI_API_KEY"), "")
        if not key:
            raise RuntimeError("Missing Azure OpenAI API key")
        headers["api-key"] = key
    payload = {"messages": messages(user_prompt)}
    add_generation_params(payload, model)
    response = http_json(url, headers, payload, model.get("request_timeout_seconds", 360))
    content = response["choices"][0]["message"]["content"]
    return extract_json(content), response.get("usage", {})


def call_databricks_chat(model, user_prompt):
    endpoint = model.get("endpoint_url") or os.environ.get(model.get("endpoint_url_env", "ADB_ENDPOINT"), "")
    if not endpoint:
        host = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
        serving_endpoint = os.environ.get("DATABRICKS_SERVING_ENDPOINT", "")
        if host and serving_endpoint:
            endpoint = f"{host}/serving-endpoints/{serving_endpoint}/invocations"
    if not endpoint:
        raise RuntimeError("Missing Databricks endpoint")
    headers = {"Content-Type": "application/json"}
    token = os.environ.get(model.get("token_env", "ADB_TOKEN")) or os.environ.get("DATABRICKS_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["Authorization"] = f"Bearer {az_access_token(resource='2ff814a6-3304-4ab8-85cb-cd0e6f879c1d')}"
    payload = {"messages": messages(user_prompt)}
    add_generation_params(payload, model)
    response = http_json(endpoint, headers, payload, model.get("request_timeout_seconds", 360))
    if "choices" in response:
        content = response["choices"][0]["message"]["content"]
        return extract_json(content), response.get("usage", {})
    if "predictions" in response and response["predictions"]:
        value = response["predictions"][0]
        content = value.get("content") if isinstance(value, dict) else value
        return extract_json(content), response.get("usage", {})
    raise RuntimeError(f"Unsupported Databricks response shape: {str(response)[:1000]}")


def call_model(model, user_prompt):
    if model["provider"] == "azure_openai_chat":
        return call_azure_openai_chat(model, user_prompt)
    if model["provider"] == "databricks_chat":
        return call_databricks_chat(model, user_prompt)
    raise ValueError(f"Unsupported provider for SWE eval: {model['provider']}")


def patch_paths(patch):
    paths = []
    for line in patch.splitlines():
        match = re.match(r"^diff --git a/(.+?) b/(.+)$", line)
        if match:
            paths.append(match.group(2))
            continue
        match = re.match(r"^\+\+\+ b/(.+)$", line)
        if match:
            paths.append(match.group(1))
    return sorted(set(paths))


def raw_github_url(repo, commit, path):
    return f"https://raw.githubusercontent.com/{repo}/{commit}/{path}"


def fetch_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": "copilot-cli-benchmark"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8", errors="replace")


def prepare_instance_files(instance, root):
    files = patch_paths(instance["patch"])
    for path in files:
        text = fetch_text(raw_github_url(instance["repo"], instance["base_commit"], path))
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8", newline="")
    return files


def build_prompt(instance, file_contents):
    parts = [
        f"Repository: {instance['repo']}",
        f"Instance: {instance['instance_id']}",
        "",
        "Issue:",
        instance["problem_statement"],
        "",
        "Relevant files from the base commit:",
    ]
    for path, content in file_contents.items():
        if len(content) > 60000:
            content = content[:60000] + "\n\n# [TRUNCATED]\n"
        parts.append(f"\n--- {path} ---\n{content}")
    parts.append("\nReturn only JSON with a unified diff patch.")
    return "\n".join(parts)


def run_git_apply_check(workdir, patch):
    patch_path = workdir / "candidate.patch"
    patch_path.write_text(patch, encoding="utf-8", newline="")
    result = subprocess.run(
        ["git", "apply", "--check", "--recount", str(patch_path)],
        cwd=str(workdir),
        text=True,
        capture_output=True,
        timeout=60,
    )
    return {
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout": result.stdout[-2000:],
        "stderr": result.stderr[-2000:],
    }


def evaluate_one(model, instance, out_dir):
    started = time.perf_counter()
    error = None
    usage = {}
    response = None
    with tempfile.TemporaryDirectory(prefix=f"swe-{instance['instance_id']}-") as tmp:
        workdir = Path(tmp)
        expected_files = prepare_instance_files(instance, workdir)
        file_contents = {path: (workdir / path).read_text(encoding="utf-8", errors="replace") for path in expected_files}
        prompt = build_prompt(instance, file_contents)
        try:
            response, usage = call_model(model, prompt)
            patch = response.get("patch", "")
            if not isinstance(patch, str) or not patch.strip():
                raise ValueError("Response JSON must include non-empty patch string")
            generated_files = patch_paths(patch)
            apply_result = run_git_apply_check(workdir, patch)
        except Exception as exc:
            error = str(exc)
            patch = ""
            generated_files = []
            apply_result = {"ok": False, "exit_code": -1, "stdout": "", "stderr": ""}
    artifact = out_dir / "artifacts" / model["id"] / instance["instance_id"]
    artifact.mkdir(parents=True, exist_ok=True)
    if response is not None:
        (artifact / "response.json").write_text(json.dumps(response, indent=2), encoding="utf-8")
    if patch:
        (artifact / "candidate.patch").write_text(patch, encoding="utf-8", newline="")
    expected_set = set(expected_files)
    generated_set = set(generated_files)
    exact_file_match = generated_set == expected_set
    touches_expected = bool(generated_set & expected_set)
    latency = time.perf_counter() - started
    return {
        "model_id": model["id"],
        "instance_id": instance["instance_id"],
        "repo": instance["repo"],
        "expected_files": expected_files,
        "generated_files": generated_files,
        "patch_applies": apply_result["ok"],
        "exact_file_match": exact_file_match,
        "touches_expected_file": touches_expected,
        "proxy_pass": apply_result["ok"] and touches_expected,
        "error": error,
        "apply_result": apply_result,
        "usage": usage,
        "latency_seconds": round(latency, 3),
    }


def write_report(rows, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "results.jsonl").open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    fields = [
        "model_id",
        "instance_id",
        "repo",
        "patch_applies",
        "touches_expected_file",
        "exact_file_match",
        "proxy_pass",
        "latency_seconds",
        "error",
    ]
    with (out_dir / "summary.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})
    by_model = {}
    for row in rows:
        by_model.setdefault(row["model_id"], []).append(row)
    lines = [
        "# SWE-bench Lite patch-generation proxy eval",
        "",
        "This is not official SWE-bench Docker scoring. Docker was unavailable, so this run evaluates whether each model can generate a unified diff that applies cleanly to the gold-patch target files and touches the expected file.",
        "",
        "## Summary by model",
        "",
        "| Model | Proxy pass | Applies | Touches expected | Exact file match | Calls | Avg latency |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model_id, items in sorted(by_model.items()):
        total = len(items)
        proxy = sum(1 for item in items if item["proxy_pass"])
        applies = sum(1 for item in items if item["patch_applies"])
        touches = sum(1 for item in items if item["touches_expected_file"])
        exact = sum(1 for item in items if item["exact_file_match"])
        avg = sum(item["latency_seconds"] for item in items) / total
        lines.append(f"| {model_id} | {proxy}/{total} | {applies}/{total} | {touches}/{total} | {exact}/{total} | {total} | {avg:.2f}s |")
    lines += [
        "",
        "## Instance results",
        "",
        "| Model | Instance | Repo | Applies | Touches expected | Exact file match | Error |",
        "| --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        err = (row.get("error") or "").replace("|", "\\|")
        if len(err) > 160:
            err = err[:160] + "..."
        lines.append(
            f"| {row['model_id']} | {row['instance_id']} | {row['repo']} | {row['patch_applies']} | {row['touches_expected_file']} | {row['exact_file_match']} | {err or '-'} |"
        )
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", default="models.local.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--model", action="append")
    args = parser.parse_args()

    models = [model for model in read_json(args.models) if model["provider"] in {"azure_openai_chat", "databricks_chat"}]
    if args.model:
        selected = set(args.model)
        models = [model for model in models if model["id"] in selected]
    if not models:
        raise SystemExit("No runnable models selected")

    ds = load_dataset("SWE-bench/SWE-bench_Lite", split="test")
    instances = [dict(ds[i]) for i in range(args.count)]
    out_dir = Path(args.out)
    rows = []
    for model in models:
        for instance in instances:
            row = evaluate_one(model, instance, out_dir)
            rows.append(row)
            status = "PASS" if row["proxy_pass"] else "FAIL"
            print(f"{status} {model['id']} {instance['instance_id']} applies={row['patch_applies']} touches={row['touches_expected_file']} {row['latency_seconds']}s", flush=True)
    write_report(rows, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
