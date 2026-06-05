#!/usr/bin/env bash
# Random-100 SWE-bench Verified runner for a single model.
# Draws a deterministic random 100 (seed=42) from the full Verified-500 and runs
# ONLY those instance ids (via --filter regex). Resumable; prunes empty ENTRIES
# from preds between passes so they get retried; relies on the HARVEST_DIFF_FALLBACK
# patch in mini-swe-agent so LimitsExceeded tasks still yield a non-empty patch.
# Usage: MODEL=grok-4.3-foundry WORKERS=4 EVAL_WORKERS=8 STEPS=150 bash swe_run_rand.sh
set -uo pipefail

MODEL="${MODEL:?set MODEL alias e.g. grok-4.3-foundry}"
WORKERS="${WORKERS:-4}"
EVAL_WORKERS="${EVAL_WORKERS:-8}"
STEPS="${STEPS:-150}"
MAXPASS="${MAXPASS:-3}"
SEED="${SEED:-42}"

BASE=/opt/swebench
RUNROOT=$BASE/runs-randv100
OUT=$RUNROOT/$MODEL
LOG=$OUT.runner.log
PREDS=$OUT/preds.json
EVALIN=$RUNROOT/official-input/$MODEL.json
IDSFILE=$BASE/rand100_ids.json
mkdir -p "$OUT" "$RUNROOT/official-input" "$RUNROOT/official-results"

log(){ echo "[$(date -Iseconds)] $*" | tee -a "$LOG"; }

. $BASE/mini-swe/.venv/bin/activate

# 0) deterministic random-100 id list (seed=42) from full Verified-500
if [ ! -f "$IDSFILE" ]; then
  python3 - "$IDSFILE" "$SEED" <<'PY'
import sys, json, random
from datasets import load_dataset
out, seed = sys.argv[1], int(sys.argv[2])
ds = load_dataset("SWE-bench/SWE-bench_Verified", split="test")
ids = [r["instance_id"] for r in ds]
sample = sorted(random.Random(seed).sample(ids, 100))
json.dump(sample, open(out, "w"))
print("generated", len(sample), "ids")
PY
fi
FILTER=$(python3 - "$IDSFILE" <<'PY'
import sys, json
ids = json.load(open(sys.argv[1]))
print("^(" + "|".join(ids) + ")$")
PY
)
log "filter covers $(python3 -c "import json;print(len(json.load(open('$IDSFILE'))))" ) ids"

# 1) proxy clean restart (load latest multi-region routes)
if [ -f $BASE/proxy/proxy.pid ]; then kill "$(cat $BASE/proxy/proxy.pid)" 2>/dev/null || true; fi
pkill -f azure_foundry_proxy.py 2>/dev/null || true
sleep 2
log "starting proxy"
nohup /usr/bin/python3 $BASE/proxy/azure_foundry_proxy.py > $BASE/proxy/proxy.log 2>&1 &
echo $! > $BASE/proxy/proxy.pid
sleep 4
curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1 && log "proxy healthy" || log "WARN proxy health check failed"

# prune empty ENTRIES from preds (drop entry + rm dir) so mini-extra reruns ONLY them
prune_empty() {
python3 - "$OUT" "$PREDS" <<'PY'
import json,os,sys,shutil
out,preds=sys.argv[1],sys.argv[2]
if not os.path.exists(preds): print("nopreds"); sys.exit(0)
data=json.load(open(preds))
items=data if isinstance(data,dict) else {d.get("instance_id"):d for d in data}
empt=[k for k,v in items.items() if not str((v or {}).get("model_patch","")).strip()]
for k in empt:
    items.pop(k,None)
    p=os.path.join(out,k)
    if os.path.isdir(p): shutil.rmtree(p,ignore_errors=True)
if isinstance(data,dict): json.dump(items,open(preds,"w"),indent=2)
print("pruned_empty=%d"%len(empt))
PY
}

for pass in $(seq 1 $MAXPASS); do
  log "=== AGENT PASS $pass/$MAXPASS model=$MODEL workers=$WORKERS steps=$STEPS (random-100) ==="
  MSWEA_COST_TRACKING=ignore_errors OPENAI_API_KEY=dummy OPENAI_API_BASE=http://127.0.0.1:8000/v1 \
  mini-extra swebench \
    --subset verified --split test --filter "$FILTER" \
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

# re-add any ids still missing from preds as empty placeholders so eval sees all 100
python3 - "$PREDS" "$IDSFILE" "$MODEL" <<'PY'
import json,sys,os
preds,idsf,model=sys.argv[1],sys.argv[2],sys.argv[3]
ids=json.load(open(idsf))
d=json.load(open(preds)) if os.path.exists(preds) else {}
for i in ids:
    if i not in d:
        d[i]={"model_name_or_path":model,"instance_id":i,"model_patch":""}
json.dump(d,open(preds,"w"),indent=2)
print("preds now",len(d))
PY
cp "$PREDS" "$EVALIN"

# 2) official evaluation over the 100 ids
cd $BASE/SWE-bench
. .venv/bin/activate
IDS=$(python3 -c "import json;print(' '.join(json.load(open('$IDSFILE'))))")
log "=== OFFICIAL EVAL model=$MODEL n_ids=$(echo $IDS|wc -w) (random-100) ==="
python -m swebench.harness.run_evaluation \
  --dataset_name SWE-bench/SWE-bench_Verified --split test \
  --predictions_path "$EVALIN" --max_workers "$EVAL_WORKERS" \
  --run_id "randv100_$MODEL" --instance_ids $IDS >> "$LOG" 2>&1
log "official eval exit=$?"
report=$(ls -t $BASE/SWE-bench/*randv100_$MODEL*.json 2>/dev/null | head -1)
[ -n "$report" ] && cp "$report" "$RUNROOT/official-results/$MODEL.report.json" && log "report -> official-results/$MODEL.report.json"
log "=== DONE model=$MODEL (random-100) ==="
echo DONE > "$OUT.status"
