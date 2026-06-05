#!/usr/bin/env bash
# Fill empty-patch instances for one model by re-running ONLY the empties at a higher step limit.
# Usage: MODEL=grok-4.3-foundry STEPS=120 WORKERS=4 EVAL_WORKERS=8 bash fill_empties.sh
set -uo pipefail
MODEL="${MODEL:?set MODEL}"
WORKERS="${WORKERS:-4}"
EVAL_WORKERS="${EVAL_WORKERS:-8}"
STEPS="${STEPS:-120}"
SLICE="${SLICE:-0:100}"
ROUNDS="${ROUNDS:-2}"

BASE=/opt/swebench
RUNROOT=$BASE/runs-100
OUT=$RUNROOT/$MODEL
LOG=$OUT.fill.log
PREDS=$OUT/preds.json
EVALIN=$RUNROOT/official-input/$MODEL.json
log(){ echo "[$(date -Iseconds)] $*" | tee -a "$LOG"; }

if ! curl -sf http://127.0.0.1:8000/health >/dev/null 2>&1; then
  nohup /usr/bin/python3 $BASE/proxy/azure_foundry_proxy.py > $BASE/proxy/proxy.log 2>&1 & echo $! > $BASE/proxy/proxy.pid
  sleep 4
fi

. $BASE/mini-swe/.venv/bin/activate

count_empty(){
python3 - "$PREDS" <<'PY'
import json,sys,os
p=sys.argv[1]
if not os.path.exists(p): print(0); raise SystemExit
d=json.load(open(p))
items=d if isinstance(d,dict) else {x.get("instance_id"):x for x in d}
print(sum(1 for v in items.values() if not str((v or {}).get("model_patch","")).strip()))
PY
}

# delete output dirs of empty instances so mini-extra re-runs ONLY them
prune_empty_dirs(){
python3 - "$OUT" "$PREDS" <<'PY'
import json,sys,os,shutil
out,p=sys.argv[1],sys.argv[2]
if not os.path.exists(p): print("nopreds"); raise SystemExit
d=json.load(open(p))
items=d if isinstance(d,dict) else {x.get("instance_id"):x for x in d}
empt=[k for k,v in items.items() if not str((v or {}).get("model_patch","")).strip()]
# also drop the empty entries from preds so mini-extra does not consider them done
for k in empt:
    items.pop(k,None)
    dd=os.path.join(out,k)
    if os.path.isdir(dd): shutil.rmtree(dd,ignore_errors=True)
if isinstance(d,dict):
    json.dump(items,open(p,"w"))
print("removed=%d ids=%s"%(len(empt),",".join(empt)))
PY
}

for r in $(seq 1 $ROUNDS); do
  e=$(count_empty); log "round $r start: empties=$e (steps=$STEPS)"
  [ "$e" = "0" ] && { log "no empties, done"; break; }
  pinfo=$(prune_empty_dirs); log "pruned: $pinfo"
  MSWEA_COST_TRACKING=ignore_errors OPENAI_API_KEY=dummy OPENAI_API_BASE=http://127.0.0.1:8000/v1 \
  mini-extra swebench --subset lite --split test --slice "$SLICE" \
    --model "openai/$MODEL" --workers "$WORKERS" --output "$OUT" --environment-class docker \
    -c swebench.yaml \
    -c model.model_kwargs.api_base=http://127.0.0.1:8000/v1 \
    -c model.model_kwargs.api_key=dummy -c model.model_kwargs.drop_params=true \
    -c model.model_kwargs.temperature=0 -c agent.step_limit=$STEPS \
    -c model.cost_tracking=ignore_errors >> "$LOG" 2>&1
  log "round $r agent exit=$?"
  STEPS=$((STEPS+80))
done

cp "$PREDS" "$EVALIN"
cd $BASE/SWE-bench && . .venv/bin/activate
IDS=$(python3 -c "import json,sys;d=json.load(open('$EVALIN'));print(' '.join(d.keys() if isinstance(d,dict) else [x['instance_id'] for x in d]))")
log "=== OFFICIAL EVAL (fill) model=$MODEL n=$(echo $IDS|wc -w) ==="
python -m swebench.harness.run_evaluation --dataset_name SWE-bench/SWE-bench_Lite --split test \
  --predictions_path "$EVALIN" --max_workers "$EVAL_WORKERS" --run_id "fill_$MODEL" --instance_ids $IDS >> "$LOG" 2>&1
report=$(ls -t $BASE/SWE-bench/*fill_$MODEL*.json 2>/dev/null | head -1)
[ -n "$report" ] && cp "$report" "$RUNROOT/official-results/$MODEL.report.json" && log "report updated"
log "final empties=$(count_empty)"
echo FILLED > "$OUT.fillstatus"
log "=== FILL DONE $MODEL ==="
