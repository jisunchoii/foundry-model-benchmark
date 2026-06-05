#!/usr/bin/env bash
# Resumable SWE-bench Lite first-100 runner for a single model.
# Usage: MODEL=kimi-k2.6-foundry WORKERS=3 EVAL_WORKERS=8 STEPS=40 bash swe_run_100.sh
set -uo pipefail

MODEL="${MODEL:?set MODEL alias e.g. kimi-k2.6-foundry}"
WORKERS="${WORKERS:-4}"
EVAL_WORKERS="${EVAL_WORKERS:-8}"
STEPS="${STEPS:-40}"
SLICE="${SLICE:-0:100}"
MAXPASS="${MAXPASS:-3}"

BASE=/opt/swebench
RUNROOT=$BASE/runs-100
OUT=$RUNROOT/$MODEL
LOG=$OUT.runner.log
PREDS=$OUT/preds.json
EVALIN=$RUNROOT/official-input/$MODEL.json
mkdir -p "$OUT" "$RUNROOT/official-input" "$RUNROOT/official-results"

log(){ echo "[$(date -Iseconds)] $*" | tee -a "$LOG"; }

# 1) proxy up
if ! curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1; then
  log "starting proxy"
  nohup /usr/bin/python3 $BASE/proxy/azure_foundry_proxy.py > $BASE/proxy/proxy.log 2>&1 &
  echo $! > $BASE/proxy/proxy.pid
  sleep 4
fi
curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1 && log "proxy healthy" || log "WARN proxy health check failed"

. $BASE/mini-swe/.venv/bin/activate

# helper: delete output dirs whose preds patch is empty/missing so they get retried
prune_empty() {
python3 - "$OUT" "$PREDS" <<'PY'
import json,os,sys,shutil
out,preds=sys.argv[1],sys.argv[2]
if not os.path.exists(preds):
    print("no preds yet"); sys.exit(0)
data=json.load(open(preds))
# preds.json may be dict keyed by instance_id or list of dicts
items={}
if isinstance(data,dict):
    items=data
elif isinstance(data,list):
    for d in data:
        iid=d.get("instance_id");
        if iid: items[iid]=d
empties=[]
for iid,d in items.items():
    patch=(d or {}).get("model_patch") or (d or {}).get("prediction") or ""
    if not str(patch).strip():
        empties.append(iid)
for iid in empties:
    p=os.path.join(out,iid)
    if os.path.isdir(p):
        shutil.rmtree(p,ignore_errors=True)
print("pruned_empty=%d"%len(empties))
PY
}

for pass in $(seq 1 $MAXPASS); do
  log "=== AGENT PASS $pass/$MAXPASS model=$MODEL workers=$WORKERS steps=$STEPS slice=$SLICE ==="
  MSWEA_COST_TRACKING=ignore_errors OPENAI_API_KEY=dummy OPENAI_API_BASE=http://127.0.0.1:8000/v1 \
  mini-extra swebench \
    --subset lite --split test --slice "$SLICE" \
    --model "openai/$MODEL" \
    --workers "$WORKERS" \
    --output "$OUT" \
    --environment-class docker \
    -c swebench.yaml \
    -c model.model_kwargs.api_base=http://127.0.0.1:8000/v1 \
    -c model.model_kwargs.api_key=dummy \
    -c model.model_kwargs.drop_params=true \
    -c model.model_kwargs.temperature=0 \
    -c agent.step_limit=$STEPS \
    -c model.cost_tracking=ignore_errors >> "$LOG" 2>&1
  log "agent pass $pass exit=$?"
  if [ -f "$PREDS" ]; then
    res=$(prune_empty); log "after pass $pass: $res"
    echo "$res" | grep -q "pruned_empty=0" && { log "no empties left, stop agent passes"; break; }
  fi
done

[ -f "$PREDS" ] && cp "$PREDS" "$EVALIN"

# 2) official evaluation
cd $BASE/SWE-bench
. .venv/bin/activate
IDS=$(python3 - "$EVALIN" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
ids=list(d.keys()) if isinstance(d,dict) else [x.get("instance_id") for x in d]
print(" ".join(i for i in ids if i))
PY
)
log "=== OFFICIAL EVAL model=$MODEL n_ids=$(echo $IDS | wc -w) ==="
python -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Lite --split test \
  --predictions_path "$EVALIN" --max_workers "$EVAL_WORKERS" \
  --run_id "run100_$MODEL" --instance_ids $IDS >> "$LOG" 2>&1
log "official eval exit=$?"

# 3) collect official report json into run dir
report=$(ls -t $BASE/SWE-bench/*run100_$MODEL*.json 2>/dev/null | head -1)
[ -n "$report" ] && cp "$report" "$RUNROOT/official-results/$MODEL.report.json" && log "report -> $RUNROOT/official-results/$MODEL.report.json"
log "=== DONE model=$MODEL ==="
echo DONE > "$OUT.status"
