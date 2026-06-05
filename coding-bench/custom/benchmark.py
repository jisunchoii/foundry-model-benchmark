import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


SYSTEM_PROMPT = """You are completing a coding benchmark task.
Return only a JSON object with this exact shape:
{"files":{"relative/path":"complete file content"}}
Do not include markdown fences, explanations, or unchanged files unless needed.
Keep changes minimal and make the provided tests pass."""


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def copy_tree(src, dst):
    if not src.exists():
        return
    for item in src.rglob("*"):
        if item.is_file():
            rel = item.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def collect_files(root):
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            files[rel] = path.read_text(encoding="utf-8")
    return files


def build_prompt(task, workdir):
    files = collect_files(workdir)
    rendered = [task["prompt"].strip(), "", "Current files:"]
    for rel, content in files.items():
        rendered.append(f"\n--- {rel} ---\n{content}")
    rendered.append("\nReturn JSON only.")
    return "\n".join(rendered)


def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(text[start : end + 1])


def safe_write_files(workdir, files):
    for rel, content in files.items():
        path = (workdir / rel).resolve()
        if not str(path).startswith(str(workdir.resolve())):
            raise ValueError(f"Refusing to write outside workdir: {rel}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def az_access_token(scope=None, resource=None):
    az = shutil.which("az") or shutil.which("az.cmd") or r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    command = [az, "account", "get-access-token", "--query", "accessToken", "--output", "tsv"]
    if resource:
        command.extend(["--resource", resource])
    else:
        command.extend(["--scope", scope])
    result = subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.strip()


def http_json(url, headers, payload, timeout):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {body[:2000]}") from exc


def messages(user_prompt):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]


def add_generation_params(payload, model):
    if "temperature" in model:
        payload["temperature"] = model["temperature"]
    if "max_completion_tokens" in model:
        payload["max_completion_tokens"] = model["max_completion_tokens"]
    elif "max_tokens" in model:
        payload["max_tokens"] = model["max_tokens"]


def call_reference(task_dir):
    return {"files": collect_files(task_dir / "reference")}, {}


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
            raise RuntimeError("Missing Azure OpenAI API key environment variable")
        headers["api-key"] = key
    payload = {"messages": messages(user_prompt)}
    add_generation_params(payload, model)
    response = http_json(url, headers, payload, model.get("request_timeout_seconds", 240))
    return extract_json(response["choices"][0]["message"]["content"]), response.get("usage", {})


def call_openai_compatible_chat(model, user_prompt):
    endpoint = (model.get("endpoint") or os.environ.get(model.get("endpoint_env", ""), "")).rstrip("/")
    if not endpoint:
        raise RuntimeError("Missing OpenAI-compatible endpoint")
    url = endpoint
    if not url.endswith("/chat/completions"):
        url = f"{url}/chat/completions"
    headers = {"Content-Type": "application/json"}
    api_key_env = model.get("api_key_env")
    if api_key_env:
        api_key = os.environ.get(api_key_env, "")
        if not api_key:
            raise RuntimeError(f"Missing API key env var {api_key_env}")
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {"model": model.get("model", model["id"]), "messages": messages(user_prompt)}
    add_generation_params(payload, model)
    response = http_json(url, headers, payload, model.get("request_timeout_seconds", 240))
    return extract_json(response["choices"][0]["message"]["content"]), response.get("usage", {})


def call_databricks_chat(model, user_prompt):
    endpoint = model.get("endpoint_url") or os.environ.get(model.get("endpoint_url_env", "ADB_ENDPOINT"), "")
    if not endpoint:
        host = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
        serving_endpoint = os.environ.get("DATABRICKS_SERVING_ENDPOINT", "")
        if host and serving_endpoint:
            endpoint = f"{host}/serving-endpoints/{serving_endpoint}/invocations"
    if not endpoint:
        raise RuntimeError("Missing ADB_ENDPOINT or DATABRICKS_HOST + DATABRICKS_SERVING_ENDPOINT")
    headers = {"Content-Type": "application/json"}
    token_env = model.get("token_env", "ADB_TOKEN")
    token = os.environ.get(token_env) or os.environ.get("DATABRICKS_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["Authorization"] = f"Bearer {az_access_token(resource='2ff814a6-3304-4ab8-85cb-cd0e6f879c1d')}"
    payload = {"messages": messages(user_prompt)}
    add_generation_params(payload, model)
    response = http_json(endpoint, headers, payload, model.get("request_timeout_seconds", 240))
    if "choices" in response:
        return extract_json(response["choices"][0]["message"]["content"]), response.get("usage", {})
    if "predictions" in response and response["predictions"]:
        value = response["predictions"][0]
        content = value.get("content") if isinstance(value, dict) else value
        return extract_json(content), response.get("usage", {})
    raise RuntimeError(f"Unsupported Databricks response shape: {str(response)[:1000]}")


def call_model(model, task_dir, task, user_prompt):
    provider = model["provider"]
    if provider == "reference":
        return call_reference(task_dir)
    if provider == "azure_openai_chat":
        return call_azure_openai_chat(model, user_prompt)
    if provider == "openai_compatible_chat":
        return call_openai_compatible_chat(model, user_prompt)
    if provider == "databricks_chat":
        return call_databricks_chat(model, user_prompt)
    raise ValueError(f"Unsupported provider: {provider}")


def run_command(command, cwd, timeout_seconds):
    started = time.perf_counter()
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        shell=False,
    )
    elapsed = time.perf_counter() - started
    return {
        "exit_code": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
        "elapsed_seconds": round(elapsed, 3),
    }


def run_one(model, task_dir, run_root):
    task = read_json(task_dir / "task.json")
    with tempfile.TemporaryDirectory(prefix=f"{task['id']}-") as tmp:
        workdir = Path(tmp)
        copy_tree(task_dir / "starter", workdir)
        user_prompt = build_prompt(task, workdir)
        started = time.perf_counter()
        error = None
        usage = {}
        response = None
        try:
            response, usage = call_model(model, task_dir, task, user_prompt)
            if "files" not in response or not isinstance(response["files"], dict):
                raise ValueError("Model response must contain a files object")
            safe_write_files(workdir, response["files"])
            command_result = run_command(task["command"], workdir, task.get("timeout_seconds", 30))
        except Exception as exc:
            error = str(exc)
            command_result = {"exit_code": -1, "stdout": "", "stderr": "", "elapsed_seconds": 0}
        total_elapsed = time.perf_counter() - started
        artifact_dir = run_root / "artifacts" / model["id"] / task["id"]
        artifact_dir.mkdir(parents=True, exist_ok=True)
        if response is not None:
            (artifact_dir / "response.json").write_text(json.dumps(response, indent=2), encoding="utf-8")
        result = {
            "model_id": model["id"],
            "task_id": task["id"],
            "passed": command_result["exit_code"] == 0 and error is None,
            "error": error,
            "usage": usage,
            "latency_seconds": round(total_elapsed, 3),
            "command": task["command"],
            "command_result": command_result,
        }
        return result


def write_outputs(results, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "results.jsonl").open("w", encoding="utf-8") as fh:
        for result in results:
            fh.write(json.dumps(result, ensure_ascii=False) + "\n")
    with (out_dir / "summary.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["model_id", "task_id", "passed", "latency_seconds", "exit_code", "error"],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "model_id": result["model_id"],
                    "task_id": result["task_id"],
                    "passed": result["passed"],
                    "latency_seconds": result["latency_seconds"],
                    "exit_code": result["command_result"]["exit_code"],
                    "error": result["error"] or "",
                }
            )
    by_model = {}
    for result in results:
        by_model.setdefault(result["model_id"], []).append(result)
    lines = ["# Benchmark summary", "", "| Model | Passed | Total | Pass rate | Avg latency sec |", "| --- | ---: | ---: | ---: | ---: |"]
    for model_id, model_results in sorted(by_model.items()):
        passed = sum(1 for r in model_results if r["passed"])
        total = len(model_results)
        avg_latency = sum(r["latency_seconds"] for r in model_results) / total if total else 0
        lines.append(f"| {model_id} | {passed} | {total} | {passed / total:.1%} | {avg_latency:.2f} |")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", default="models.example.json")
    parser.add_argument("--tasks", default="tasks")
    parser.add_argument("--out", required=True)
    parser.add_argument("--model", action="append", help="Run only selected model id; can be repeated.")
    parser.add_argument("--task", action="append", help="Run only selected task id; can be repeated.")
    args = parser.parse_args()

    models = read_json(args.models)
    if args.model:
        selected = set(args.model)
        models = [m for m in models if m["id"] in selected]
    if not models:
        raise SystemExit("No models selected")

    task_dirs = [p for p in sorted(Path(args.tasks).iterdir()) if (p / "task.json").exists()]
    if args.task:
        selected_tasks = set(args.task)
        task_dirs = [p for p in task_dirs if read_json(p / "task.json")["id"] in selected_tasks]
    if not task_dirs:
        raise SystemExit("No tasks selected")

    out_dir = Path(args.out)
    results = []
    for model in models:
        for task_dir in task_dirs:
            result = run_one(model, task_dir, out_dir)
            results.append(result)
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status} {model['id']} {result['task_id']} {result['latency_seconds']}s", flush=True)
    write_outputs(results, out_dir)
    failed = [r for r in results if not r["passed"]]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
