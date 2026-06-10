# SWE-bench Verified Trajectory analysis (per-model problem-solving style)

## Analysis overview

We parsed the **trajectory logs** (every thought, command, and observation the agent recorded) that each model left while solving **all 500** SWE-bench Verified problems, and quantified each model's **problem-solving style**.

- **Data basis**: all 5 models over the **full 500 of Verified** (same instances, same classifier).
- Command classification (heuristic): `explore` (read/search such as ls/cat/grep/find/sed -n/head/tail), `edit` (file edits such as sed -i/cat >/patch/tee), `test` (reproduce/verify via pytest/tox/python), `other`. The **same regex classifier** is applied to all 5 models.
- One instance = one agent session. steps = number of assistant turns (= number of API calls). Commands are extracted from each turn's `extra.actions[].command`; the failure rate is tallied from the `<returncode>` of tool observations. Thinking volume is the length of the assistant's `reasoning_content`.
- For GLM, the 446 instances that have trajectories (the 58 empty patches have no trajectory directory); the rest are ~500.

## Key-metrics summary

| Metric | Kimi K2.6 | DeepSeek-V4-Pro | MiniMax M2.5 | Grok 4.3 | GLM-5.1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Resolved / 500 | **382** | 372 | 369 | 337 | 331 |
| Avg steps | 50.5 | 48.4 | 54.8 | **33.6** | 65.3 |
| Median steps | 43 | 41 | 46 | **31** | 52 |
| Thinking (reasoning) chars/turn | **503** | 0¹ | 255 | 0 | 320 |
| Share of turns emitting thinking | 100% | 0¹% | 100% | 0% | 63% |
| explore command share | 49.1% | **54.1%** | 46.4% | 53.5% | 49.4% |
| edit command share | **21.2%** | 11.4% | 15.2% | 17.7% | 14.9% |
| test command share | 25.5% | 34.2% | **35.3%** | 26.9% | 35.0% |
| Instances that ran tests | 99.4% | 99.4% | 99.6% | 98.8% | **100%** |
| Commands until first edit | **16.0** | 26.8 | 17.0 | 19.0 | 19.8 |
| Patch lines added (avg) | 40.6 | 9.0 | 60.4 | **6.5** | 266.1² |
| Files modified per patch | 1.26 | 1.19 | 1.24 | **1.07** | 2.09² |
| Command failure rate | 0.13 | 0.11 | 0.10 | 0.12 | **0.09** |

¹ DeepSeek-V4-Pro did not expose `reasoning_content` on this Foundry deployment (this does not mean the model does no internal reasoning — the endpoint simply does not return that field — **unverified**). Grok's 0 reflects the model genuinely not emitting thinking tokens, an action-first trait.
² GLM's average patch-lines-added is an **outlier-sensitive mean**, heavily swayed by a few large-rewrite cases (see the failure signature below).

## Per-model problem-solving style

### Grok 4.3 — "minimal exploration, minimal edits"
- **Overwhelmingly efficient**: shortest at 33.6 average steps (50–65% of the others), with the smallest, most precise patches at **6.5 lines / 1.07 files** on average.
- **Emits no thinking tokens** (reasoning=0). An action-style agent that executes commands immediately.
- **Barely rewrites even on failure**: on failure the patch grows only slightly, 5.4→8.8 lines, and steps 31→38, the most stable. It doesn't waste time/tokens on problems it can't solve, but it also doesn't dig deep.
- Consistent with its cheapest token/cost profile (cache-adj $0.14/resolved).

### Kimi K2.6 — "thinks deeply, edits aggressively"
- Averages **503 chars of thinking per turn** (the most), with CoT output on 100% of turns. **Highest edit share at 21.2%** — as aggressive on edits as on exploration.
- **Gets its hands in fastest**, with 16 commands until the first edit. Resolved **382, #1**.
- **Tries harder when stuck**: on failure cases, steps expand 46→67 and patches 13→129 lines. A persistent style that digs deeper and grows edits when stuck (though not as runaway as MiniMax/GLM).

### DeepSeek-V4-Pro — "explores long, edits little"
- **Highest explore share at 54.1%**, and **explores longest before acting, with 26.8 commands until the first edit**. Lowest edit share at 11.4% — a cautious style that makes minimal edits after understanding thoroughly.
- **Most stable failure control**: on failure the patch grows only 7.3→13.9 lines (smallest increase), and file count is nearly unchanged at 1.19→1.20. It doesn't go runaway even when it can't solve — alongside Grok, the most "controlled" failure signature.
- Downside: it had a tendency toward deterministic empty patches ("already fixed"), but achieved empty=0 via re-reasoning. With reasoning not exposed, its thinking style is unverified.

### MiniMax M2.5 — "ultra-precise when right, runaway when wrong"
- **The most pronounced failure signature**: resolved patches average **6.9 lines**, the most precise of the 5, but **unresolved averages 212 lines**, a 30× blowup. When stuck, it mass-rewrites code and flails — runaway over-editing.
- On failure, steps also spike 49→70 and file count 1.07→1.72. With a test share of 35.3% it verifies often, but tends to lose control when it can't find the right place to fix.
- Most efficient when it gets it right (high potential), but weak failure guardrails.

### GLM-5.1 — "verification-driven, but the biggest runaway on failure"
- **35.0% test share + 0.09 command failure rate (lowest) + 100% test execution** — a methodical type that constantly confirms via tests and composes commands most cleanly.
- Emits thinking on only 63% of turns (partial CoT); steps average 65.3 (highest) and median 52 → a long tail that drags out on hard problems.
- **The failure signature flips in the 500-set analysis**: in the earlier Verified-100 (django-biased), GLM's unresolved patches were *smaller*, but over the full 500, resolved is 24.6 lines → **unresolved 961 lines (39×), files 1.4→4.1**, the **most extreme runaway of the 5 models**. The pattern of mass-rewriting many files on hard cases emerged over the full set. (Note: an outlier-sensitive mean, but the direction is clear.)
- The 58 empty patches (deterministic "no fix needed" submissions) are a separate signal — they trim the denominator and hurt the score (see [this report](./swe-bench-verified-500-report.md)).

## Cross-cutting insights

- **Thinking volume ≠ performance**: the gap between Grok (337) and DeepSeek (372) with 0 chars of thinking and Kimi (382) with 503 chars is a matter of style, not thinking volume. **Precision of exploration/editing** drives performance more than CoT volume.
- **Failure patterns split the models into 5 colors**: when stuck, they either ① nearly stop as-is (Grok 5→9, DeepSeek 7→14), ② dig deeper (Kimi 13→129), or ③ go on a mass-rewrite runaway (MiniMax 7→212, **GLM 25→961**). In particular, **the unresolved-patch blowups of GLM and MiniMax are a warning sign not just for automated grading but for code-review cost** — a failed PR touches hundreds of lines across multiple files.
- **Two roads to the top**: #1 Kimi (edit-aggressive) and #2 DeepSeek (exploration-cautious) have opposite styles (16 vs 27 commands until first edit, 21% vs 11% edit share) yet similar performance → **there is no single correct style**.
- **Patch size vs solve rate**: the small patches of resolved cases (Grok 5.4, DeepSeek 7.3, MiniMax 6.9) are not disadvantaged versus larger patches — SWE-bench Verified is largely a structure where a **localized minimal fix** is the answer. Large patches are usually a sign of "still flailing."
- **In common**: every model explores with 16–27 commands before the first edit, runs tests in ~99% of cases, and modifies just 1 file on average when resolved. They follow the mini-swe-agent default workflow (explore → fix → verify) well.

## Caveats

- The command classification is a regex heuristic, so there is a small ± margin (e.g., `python -c` reproduction code is classified as test; `sed -i` is edit and `sed -n` is explore). Applying the **same classifier** to all 5 models keeps the relative comparison consistent.
- The average patch-lines-added (especially for unresolved) is a **mean sensitive to a few large rewrites**. The direction (whether it runs away) is reliable, but absolute values are larger than the median.
- DeepSeek-V4-Pro's reasoning metric of 0 is because **the Foundry endpoint did not return `reasoning_content`**, and does not imply the model lacks internal reasoning (unverified).
- harvest/RateLimit/ServiceUnavailable terminations are infrastructure factors rather than model behavior, and were excluded from the style interpretation.

## Cross-reference

- Accuracy: [swe-bench-verified-500-report.md](./swe-bench-verified-500-report.md)
