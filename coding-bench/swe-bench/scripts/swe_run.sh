#!/usr/bin/env bash
# Resumable SWE-bench runner for a single model, dataset-parameterized (lite|verified).
# Usage: MODEL=kimi-k2.6-foundry SUBSET=verified SLICE=0:100 WORKERS=5 EVAL_WORKERS=8 STEPS=40 bash swe_run.sh
set -uo pipefail

MODEL="${MODEL:?set MODEL alias e.g. kimi-k2.6-foundry}"
SUBSET="${SUBSET:-verified}"            # lite | verified
SLICE="${SLICE:-0:100}"
WORKERS="${WORKERS:-4}"
EVAL_WORKERS="${EVAL_WORKERS:-8}"
STEPS="${STEPS:-40}"
MAXPASS="${MAXPASS:-3}"

# map subset -> official dataset name
case "$SUBSET" in
  lite)     DATASET="SWE-bench/SWE-bench_Lite"; RUNROOT_DEFAULT=/opt/swebench/runs-100 ;;
  verified) DATASET="SWE-bench/SWE-bench_Verified"; RUNROOT_DEFAULT=/opt/swebench/runs-verified ;;
  *) echo "unknown SUBSET=$SUBSET (use lite|verified)"; exit 2 ;;
esac

BASE=/opt/swebench
RUNROOT="${RUNROOT:-$RUNROOT_DEFAULT}"
OUT=$RUNROOT/$MODEL
LOG=$OUT.runner.log
PREDS=$OUT/preds.json
EVALIN=$RUNROOT/official-input/$MODEL.json
RUNID="${RUNID:-${SUBSET}_$(echo "$SLICE" | tr ':' '-')_$MODEL}"
mkdir -p "$OUT" "$RUNROOT/official-input" "$RUNROOT/official-results"

log(){ echo "[$(date -Iseconds)] $*" | tee -a "$LOG"; }

# 1) proxy up (force a clean restart so the latest proxy code / multi-region routes load)
if [ -f $BASE/proxy/proxy.pid ]; then kill "$(cat $BASE/proxy/proxy.pid)" 2>/dev/null || true; fi
pkill -f azure_foundry_proxy.py 2>/dev/null || true
sleep 2
log "starting proxy"
nohup /usr/bin/python3 $BASE/proxy/azure_foundry_proxy.py > $BASE/proxy/proxy.log 2>&1 &
echo $! > $BASE/proxy/proxy.pid
sleep 4
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
items={}
if isinstance(data,dict):
    items=data
elif isinstance(data,list):
    for d in data:
        iid=d.get("instance_id")
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
  log "=== AGENT PASS $pass/$MAXPASS model=$MODEL subset=$SUBSET workers=$WORKERS steps=$STEPS slice=$SLICE ==="
  MSWEA_COST_TRACKING=ignore_errors OPENAI_API_KEY=dummy OPENAI_API_BASE=http://127.0.0.1:8000/v1 \
  mini-extra swebench \
    --subset "$SUBSET" --split test --slice "$SLICE" \
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
log "=== OFFICIAL EVAL model=$MODEL dataset=$DATASET n_ids=$(echo $IDS | wc -w) ==="
python -m swebench.harness.run_evaluation \
  --dataset_name "$DATASET" --split test \
  --predictions_path "$EVALIN" --max_workers "$EVAL_WORKERS" \
  --run_id "$RUNID" --instance_ids $IDS >> "$LOG" 2>&1
log "official eval exit=$?"

# 3) collect official report json into run dir
report=$(ls -t $BASE/SWE-bench/*$RUNID*.json 2>/dev/null | head -1)
[ -n "$report" ] && cp "$report" "$RUNROOT/official-results/$MODEL.report.json" && log "report -> $RUNROOT/official-results/$MODEL.report.json"
log "=== DONE model=$MODEL subset=$SUBSET ==="
echo DONE > "$OUT.status"
