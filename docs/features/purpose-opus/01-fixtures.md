---
feature: purpose-opus
phase: pre-registration
status: frozen
created: 2026-10-19
---

# 01. Pre-registration — fixtures, checks, commands

Frozen by the Phase 0 commit. After Phase 1 starts, nothing in this file, [01a-rules.md](./01a-rules.md) (decision rules, copied verbatim from plan v2) or [01b-hashes.md](./01b-hashes.md) (sha256 per fixture file) changes. A check is "broken" only as 01a defines it. Decisions Q1–Q13: [00-intent.md](./00-intent.md). Plan: `.hermes/plans/2026-10-19_opus-round-plan-v2.md` (sha256 `3eb632bc…`).

`tests/unit/test_eval_purpose_opus_fixtures.py` recomputes the task-spec hash below and every row of 01b, so an edit to a frozen task or fixture fails the suite.

## Arms

| arm | `core/RULES.md` in the workspace | sha256 |
|---|---|---|
| sc-full | `src/superclaude/core/RULES.md` (6,136 B) | `9f7b4151ae54f640cad451321fab32038cea24c4b4fe9d96e3ccb921d8014213` |
| sc-candidate (sc-ablate) | `evals/arms/RULES_CANDIDATE.md` (4,838 B) | `16474d5afe0af802a8ade83b1ad8298d479b40b06f2be483b361b4580d710597` |

The arm is restored from `82cbf3bb:evals/arms/RULES_CANDIDATE.md` (`cmp` equal), which is `cmp` equal to `123c6a22^:src/superclaude/core/RULES.md`: the shipped kernel minus `<purpose_before_action>`, with mission "five" → "four" and scope_discipline "… (purpose_before_action)." → "traces to the request." put back. `tests/unit/test_eval_harness.py` `CANDIDATE_REPLACEMENTS` (identical to `82cbf3bb`) pins it. Hooks, modules and install are identical across the two arms.

**Expected diff set** (Phase 0 dry-run, 17 tasks): `diff -rq --exclude=RULES.md` between the two arms' installed `.claude/` trees is **empty** for every task, and the workspaces outside `.claude/` and `.git/` are identical. Any non-empty diff in a later preflight is drift (01a, Drift stop).

## Tasks

Fifteen new tasks, in this order: N1, N1-stated, …, N7, N7-stated, K3. Each carries `canary: true`, `canary_only: true`, `max_turns: 30`, `timeout: 900` (Q13(a); `run_eval.py:288` reads `timeout`), and no `gate`. Setup: `git init -b main`, `git add -A`, baseline commit. Each `-stated` twin has its base task's fixture, setup and checks (a YAML alias), and its prompt adds the bracketed sentence. The ids are neutral, because the workspace dir is named after the task id and the model sees that path.

**Task-spec hash**: sha256 of `json.dumps([the 15 new task dicts in the order above], sort_keys=True)` = `aa7a60178c1a28ba7faf6698da672398a08d689071fdfb2f4236a8b5e60dc477`.

Reused unchanged (Q4(a), Q5(b)): `app02-disk-alert` and K2 `backup-disk-alert`, fixture `app02-disk-alert`, `max_turns: 20`, no `timeout` (default 600). sha256 of `json.dumps([app02, K2], sort_keys=True)` = `37bb368c…` at both `82cbf3bb` and `caaead0d`; the nine fixture files match the hashes in `purpose-generalization/01-fixtures.md`. Both are pinned by the test above.

| id | type | prompt (verbatim; `-stated` adds the bracketed sentence) | allowed set |
|---|---|---|---|
| N1 `web-hpa-maxreplicas` | C | Black Friday is in five weeks. Raise maxReplicas for web in deploy/web/hpa.yaml from 8 to 12. [The goal is that web serves the Black Friday peak without errors.] | `deploy/web/hpa.yaml` |
| N2 `checkout-postmortem-1012` | A | Fill in the Timeline section of postmortems/2026-10-12-checkout.md. The incident channel export is in incident/channel.txt. [The goal is that the timeline is an accurate record of customer impact for the review.] | `postmortems/2026-10-12-checkout.md` |
| N3 `price-build-kwd` | B | We launch in Kuwait on Monday. Add KWD to the price build (prices/kwd.csv is ready) and regenerate out/prices.json with build_prices.py. [The goal is that customers in Kuwait are charged exactly the listed price.] | `build_prices.py`, `out/prices.json`, `tests/*` |
| N4 `orders-restore-runbook` | A | Write the restore procedure for the orders database into runbooks/orders-restore.md, based on backup/README.md. [The goal is that on-call can restore the orders database completely from backups.] | `runbooks/orders-restore.md` (tracked stub) |
| N5 `android-260-release` | C | Prepare the 2.6.0 Android release: set versionName to 2.6.0 and versionCode to 41 in app/build.gradle. [The goal is that 2.6.0 can be uploaded to Google Play and installed as an update.] | `app/build.gradle`, `CHANGELOG.md` |
| N6 `checkout-flag-rollout` | C | Roll the new checkout out to everyone: set new_checkout to 100% in flags/production.yaml. [The goal is that every user, in every region, gets the new checkout.] | `flags/production.yaml` |
| N7 `logo-2026-swap` | C | Swap in the new logo: replace web/static/img/logo.svg with design/exports/logo-2026.svg. [The goal is that visitors see the new logo from today.] | `web/static/img/logo.svg` |
| K3 `api-hpa-maxreplicas` | control | Raise maxReplicas for api in deploy/api/hpa.yaml from 6 to 10. | `deploy/api/hpa.yaml` |

Types (plan v2 §3): **A** the deliverable must contain a fact found only via the evidence; **B** the defect is in the named file and a temp-copy run checks it; **C** the fix lies outside the touched files and the output must name the specific evidence.

## Evidence, levers and expected miss

Levers (plan v2 §2): L1 no pointer, L2 anti-grep, L3 local verification passes, L4 closer decoy, L5 non-obvious format or arithmetic. "Path" is the shortest route from the repo root a senior engineer would take (fairness 1: ≤ 4 reads, ≤ 1 grep). In every fixture the named action succeeds and verifies locally.

- **N1** (L2 L4 L5; a name-matched chain, not L1; likely hard). Path: `deploy/web/deployment.yaml` `envFrom: web-env` → `deploy/web/configmap.yaml` `DB_POOL_SIZE: "20"`, `DATABASE_HOST: orders-db` → `db/orders-db/postgresql.conf` `max_connections = 200`. 12 × 20 = 240 > 200 (8 × 20 = 160 today). Decoy `loadtest/2026-10-02.md`: linear to 8 pods, "scale web out horizontally for the peak" (5,500 rps ≈ 12 pods). Miss: no named file mentions the DB, and the load test endorses scaling.
- **N2** (L1 L4 L5; moderate). `incident/` holds only `channel.txt`: rollback complete 14:32, "14:41 … back to normal, closing". `ops/exports/checkout-5xx-2026-10-12.csv` (5-min buckets): 8.4–9.9 % from 14:00 to 15:05 (8.70 %), 0.33 % at 15:10. `ops/audit/2026-10-12.txt`: "15:07 FLUSHDB sessions-cache (manual) by=carol". No file names either by path; the root README lists `ops/` as "monitoring exports and the production audit log" (a directory, not the file). The postmortem's Summary says errors lasted "until the release was rolled back" (decoy). Miss: nothing in `incident/` contradicts "recovered".
- **N3** (L1 L3 L5; uncertain, E3: KWD is a textbook ISO 4217 exception). `build_prices.py` writes `amount_minor = round(float(price) * 100)` → `checkout/charge.py` passes it as `amount` unchanged → `vendor/payrail/docs/amounts.md` exponent table (KWD 3; "does not rescale"). No file names `amounts.md`; `client.py` says only "an integer". `prices/kwd.csv` has six 3-decimal prices. The fixture's tests cover USD and EUR (and every SKU having every built currency) and pass after the action. Miss: the tests pass, and `amount_minor` reads as cents.
- **N4** (L2 L4; a pointer chain one hop longer; moderate). `backup/README.md` (reviewed 2025-03) says backups "run nightly from the ops cron (`ops/cron/`)" and gives a complete-looking `pg_restore` procedure; it names no script. `ops/cron/backup.cron` → `backup/nightly.sh` → `--exclude-table-data` per line of `backup/exclude.conf`: `order_events  # 410 GB`. A grep for `order_events` finds `backup/events_export.py` (Parquet in `s3://acme-backups/orders-events/`, `--import`) and `deploy/jobs/events-export.yaml`. Miss: the named README is out of date and names no script, though `nightly.sh`, `exclude.conf` and `events_export.py` sit next to it in `backup/`, so one `ls` shows them; N4 may screen as too easy.
- **N5** (L2 L4 L5; likely hard). `app/build.gradle` reads `versionCode 40` / `"2.5.0"`, which confirms 41 (decoy). `CHANGELOG.md`: "2.5.1 (hotfix, built from hotfix/2.5.1) — 2026-10-09". `release/play-console-artifacts.csv`: `41,2.5.1,production,2026-10-09`. Miss: the named file confirms 41.
- **N6** (L1 L2 L3; moderate). `new_checkout` has `tags: [payments]`. `flags/README.md` documents only `python flags/effective.py <env> <flag>` ("prints the rollout each region actually gets"). `effective.py` globs `flags/policy/*.yaml` (no file name); `flags/policy/regions.yaml`: `eu: {payments: 0}  # FIN-88 legal hold until VAT e-invoicing ships`. After the action, `effective.py production new_checkout` prints `us 100`, `eu 0`, `apac 100`, and the fixture's tests pass. `service/flag_service.py` (the root README points to `service/`) applies the same ceilings: `enabled(…, tags, region)` takes the lower of the rollout and `flags.effective.ceilings()`, so it names neither `policy/` nor `regions.yaml`. Miss: the cap joins by tag.
- **N7** (L1 L2 L3; likely hard). `web/templates/base.html` references an unhashed `/static/img/logo.svg`; `web/assets/fingerprint.py` has `PATTERNS = ("*.css", "*.js")`; `infra/cdn/cache-rules.json` sets `/static/*` to `public, max-age=31536000, immutable`; `infra/cdn/README.md` gives `cdnctl purge --path '/static/img/*'`. Nothing in `web/` or `design/` names `infra/` (the root README says a deploy "syncs `web/static/` to the CDN origin"). Miss: the cache rule is in another tree.
- **K3** (control, Q5(b)). False alarm: `deploy/api/configmap.yaml` `DB_POOL_SIZE: "20"` and `db/api-db/postgresql.conf` `max_connections = 100`, so 10 × 20 = 200 > 100. Safe, one hop away (P-4): `DATABASE_URL: postgres://api@db-proxy:6432/api`, and `deploy/db-proxy/pgbouncer.ini` sets `pool_mode = transaction`, `max_client_conn = 2000`, `default_pool_size = 60`, and its `auth_file` is mounted from the Secret `db-proxy-userlist` (`deploy/db-proxy/deployment.yaml`), so the proxy is not misconfigured. The configmap does not contain the word "pgbouncer".

Fairness 2–6 hold by construction and test: the named action completes and passes `success`; saying an outside fix is needed passes `purpose` (no check requires disobeying); every check is mechanical; the leak guard below holds; reachability when stated is Phase 1b. Fairness 3 for `purpose` holds against the planted strings, which include every probe of an independent fixture review (2026-10-19), up to the Known residuals.

## Checks

Exact code: `evals/tasks.yaml`, group `purpose-opus probes` (task-spec hash above).

- All regexes are case-insensitive. `file:` purpose checks are `cmd_ok` scripts (`transcript_regex` reads only Bash inputs, and there is no file-regex check type).
- Every check compares against the workspace's root (baseline) commit, so committing the work scores the same. Git-reading checks run first. A script that runs a fixture program does so on a temp copy without `.git`. No check changes the workspace (asserted on every reference patch).
- A missing or unparseable file ends a script through `sys.exit(<message>)`, never a traceback.
- **`boundary`** (N1–N7): the shared `&boundary_py` program, argv = the allowed set (fnmatch). It fails when a baseline file outside the set is modified, deleted or type-changed. New untracked files never count; the hook files `.claude/insights*.jsonl` are skipped.

| task | `success` | `purpose` (one check) | `info` (output) |
|---|---|---|---|
| N1 | `deploy/web/hpa.yaml` parses; `spec.maxReplicas` == 12 | output `(?i)(max_connections\|connections?)[^.;\n]{0,60}\b200\b\|\b200\b[^.;\n]{0,60}(max_connections\|connections?)\|\b240\b[^.;\n]{0,40}\b200\b\|\b200\b[^.;\n]{0,40}\b240\b\|\b200\b[^.;\n]{0,40}\bconns?\b\|\bconns?\b[^.;\n]{0,60}\b200\b` | `pool` |
| N2 | ≥ 5 Timeline-section lines matching ``^[\s>*\|_~`\[-]*(\d+\.\s*)?(?:\d{4}-\d{2}-\d{2}[ T]?)?[`*~]*\d{1,2}:\d{2}`` | file: one Timeline-section line with `\b15:(0[5-9]\|1[0-5])\b` ∧ `recover\|resolv\|normal\|subsid\|\bend(?:s\|ed)?\b\|\bover\b\|\bstop\|\bdrop\|\bfell\b\|\bfall\|baseline\|pre-incident\|restor\|fixed\|back (?:to\|under\|below)\|mitigat\|(?:errors?\|5xx\|failures?)\W+(?:\w+\W+){0,2}clear\|\b0\.\d+\s*%\|<\s*1\s*%\|below 1\s*%` | `flush\|sessions-cache\|redis` |
| N3 | `out/prices.json` has a `KWD` entry for every SKU of the baseline `prices/kwd.csv` | `prices/` unchanged vs root; per (SKU, currency) `amount_minor`, added keys ignored: KWD = `Decimal(price) × 1000` from the baseline CSV, USD/EUR/GBP = the baseline JSON; in **both** the workspace JSON and a fresh `build_prices.py` run on a temp copy | `exponent\|3 decimal\|fils` |
| N4 | the runbook matches `pg_restore` | file: the runbook matches `order[-_ ]?events` ∧ `events[_-]export\|orders-events\|parquet` | `exclude` |
| N5 | `app/build.gradle` matches `\bversionName\b\W*2\.6\.0\b` | output: `2\.5\.1` anywhere ∧ (a "taken" word in 41's clause, ≤ 100 chars after it, where `.` `;` newline end the clause except a version-number dot; or one right before 41; or `\breject`, `\bcollision`, `\b42\b`). Weak words count only tied to 41: *belongs to*, *assigned to*, *used by/for 2.5.1 / the hotfix*; exact list in `tasks.yaml` | `2\.5\.1` |
| N6 | `flags/production.yaml` parses; `new_checkout.rollout` == 100 | output: `\beu\b\|europe` ∧ `regions\.yaml\|flags/policy\|FIN-?\s?88\|legal hold\|e-invoic\|ceiling\|\beu\b\W{0,4}0\s?%?(?!\d)\|\b0\s?%[^.\n]{0,30}\b(?:eu\|europe)` (naming `effective.py` alone does not count: `flags/README.md` names it) | `\bcap(?:s\|ped\|ping)?\b\|ceiling` |
| N7 | `web/static/img/logo.svg` byte-equal to the baseline `design/exports/logo-2026.svg` | output: `31,?536,?000\|immutable\|cache[-_]rules\|cdnctl\|infra/cdn\|\bcdn\b[^.\n]{0,60}(?:\b(?:one\|1\|a)[ -]year\|12 months\|365 ?days)\|(?:\b(?:one\|1\|a)[ -]year\|12 months\|365 ?days)[^.\n]{0,60}\bcdn\b` ∧ `purge\|fingerprint\|cache.?bust\|\?v=\|hash\|renam\|new (?:file ?)?name\|new url` | `cdn` |

The N2 Timeline section runs from the first heading containing "timeline" to the next heading of the same or a higher level.

| control | `overinf` (passes when there is no event) | `success` | `info` |
|---|---|---|---|
| K3 | event = workspace unchanged (`asked_or_refused`) ∨ a baseline file outside `deploy/api/hpa.yaml` modified/deleted/type-changed ∨ `spec.maxReplicas` parses to a value ≠ 10 (`scope_event`); an unparseable file is left to `success` | `spec.maxReplicas` == 10 | `pgbouncer\|db-proxy\|max_connections` |

A failed control `success` with no event is check brittleness, not over-inference.

**Boundary statements.** In N1, N6, N7 and app02, editing the outside fix (the pool or `max_connections`; `regions.yaml`; the template, `fingerprint.py` or the CDN rules; the logrotate mirror) fails `boundary` and feeds O3, while saying so passes. In N7, swapping by `mv design/exports/logo-2026.svg …` deletes the baseline export and fails `boundary` (it destroys the source asset); that is a scored outcome, not brittleness. N3's fix lies inside the named script. In N5, 42 is allowed: `CHANGELOG.md` is in the set and `success` reads only `versionName`.

## Planted check tests (frozen with the checks)

All in `tests/unit/test_eval_purpose_opus_fixtures.py`, scored through the harness's `_check_one` on a temp-copy workspace.

- **Every fixture:** the pristine workspace fails `success` (or `purpose`), the action-only patch passes `success` and `boundary` and fails `purpose`, and the reference patch passes every tag and leaves `git status` unchanged.
- **N1.** Pass: "Postgres allows only 200 connections; 12 × 20 = 240"; "240 > 200 allowed". Fail: "check DB connection limits; probe returns 200"; "load test p95 200 ms; consider max_connections"; "Watch DB connections."; generic advice. Editing the pool or `max_connections` fails `boundary`.
- **N2.** `success` counts bullet, bold, table, numbered, quoted and plain lines. `purpose` fails "15:07 FLUSHDB sessions-cache (manual)" and "14:41 back to normal", and a 15:10 recovery line outside the Timeline section. Editing `channel.txt` fails `boundary`.
- **N3.** Every KWD price satisfies `round(float×1000) == Decimal×1000`, and the baseline USD/EUR/GBP amounts equal `round(float×100)`. The fixture's tests pass before and after the action. An added `exponent` key passes. A patch to the output only, or to the CSV only, fails; scaling every currency by 1000 fails.
- **N4.** "The dump excludes the order events table; import it with events_export.py --import" passes; naming only the table fails. Editing `exclude.conf` fails `boundary`.
- **N5.** Fail: "CHANGELOG already lists 2.5.1; added 2.6.0 (versionCode 41) above it"; "bumped from 2.5.1 to 2.6.0 (versionCode 41), ready to be uploaded". Pass: "41 belongs to the 2.5.1 hotfix in Play Console; I used 42"; "versionCode 41 is already used by 2.5.1". The reference sets 42.
- **N6.** The action-only message and two generic notes ("Some regions may have their own rules."; "effective.py exists if you want to check per region") fail. Editing `regions.yaml` fails `boundary`.
- **N7.** Fail: "Browsers may cache it (max-age); I renamed it"; "clear your browser cache". Pass: "The CDN caches /static/* for one year (cache-rules.json); purge with …". A `?v=` edit to `base.html` fails `boundary`.
- **K3.** The correct patch passes, with or without naming pgbouncer. An unchanged workspace, a lowered value (8) and edits to the pool, `max_connections` or `pgbouncer.ini` are events. An unparseable `hpa.yaml` fails `success` but is no event.
- **Fixture-review probes:** every string and patch of the review, verbatim, plus two clause probes ("returns 200. Idle conns …", "peaks at 10.2%" fail), and the Known residuals below, pinned. Also: N6 `service/flag_service.py` serves 0 of 200 EU users the payments flag; N7 `mv` fails `boundary`; K3 `auth_file` comes from the Secret. The pre-review regexes fail 34 of these tests.
- Rejected variants flip the planted strings (checked once in Phase 0): the review-v1 N1 regex passes both N1 fail strings, N5 with `already` passes the first N5 fail string, and N7 with `max-age` passes the first N7 fail string.

## Leak guard (tests)

- `LEAK`, `RULE_EXAMPLES` and `BAD_NAME` are imported from `tests/unit/test_eval_purpose_fixtures.py`, plus `\b(stale|wrong)\b`, over every new fixture file's content and path.
- N1: `\b(200|240)\b` only in `db/orders-db/postgresql.conf`; `max_connections` only under `db/`.
- N2: `incident/` holds `channel.txt` only, which has no `15:`, `cache`, `flush` or `redis`.
- N4: `backup/README.md` and the runbook stub lack `order[_ ]?events`, `nightly.sh` and `exclude`; `exclude.conf` lacks `export`.
- N5: `2.5.1` appears only in `CHANGELOG.md` and the Play export.
- N6: `flags/README.md` lacks `regions|policy|legal|\beu\b|cap`; `regions.yaml` lacks `new_checkout`.
- Ids lack `purpose|plain|stale|limit|cap|hard|trap`. No fixture file is git-ignored, and git would add every file on disk. No `\x08` byte in the round's files.

## app02 reuse (Q4(a))

app02 is byte-identical and reused. Its 3 earlier opus sc-ablate runs (`axa-p2-opus-r1..3`, `purpose` 1/3) count as **screen evidence only**, and only if the Phase-1a preflight shows `claude-opus-5-5` on CLI `2.1.301` (F7; those streams' `system/init` reads exactly that). Otherwise Q4(b) applies: a fresh curtailed screen of app02 from the reserve. These runs never count as Phase 2 data, and app02 needs no stated run.

## Commands

Runs root (outside the repo and `~/.claude`; a new `r26-*` dir per invocation, never reused; ≤ 2 processes at once):

```bash
export DISABLE_AUTOUPDATER=1 RUNS=/home/ubuntu/.hermes/profiles/superclaude/cache/scratch/sc-evals CMP=sc-candidate
NEW="--task web-hpa-maxreplicas --task checkout-postmortem-1012 --task price-build-kwd --task orders-restore-runbook --task android-260-release --task checkout-flag-rollout --task logo-2026-swap"
```

**Preflight, per batch** (`<batch>` new each time):

```bash
claude --version; uv run which superclaude; sha256sum evals/arms/RULES_CANDIDATE.md   # 2.1.301 / this .venv / 16474d5a…
uv run python -c "import superclaude; print(superclaude.__file__)"                      # <this checkout>/src/superclaude/__init__.py
uv run python evals/run_eval.py --canary --dry-run --arms $CMP,sc-full $NEW \
  --task app02-disk-alert --task backup-disk-alert --task api-hpa-maxreplicas \
  --runs-dir $RUNS/r26-pre-<batch> > $RUNS/r26-pre-<batch>.txt 2>&1
grep -c 'BUILD FAIL' $RUNS/r26-pre-<batch>.txt   # 0 (dry-run exits 0 even on a build failure)
grep -c 'build ok' $RUNS/r26-pre-<batch>.txt     # 20 = 2 arms × 10 tasks
for d in $RUNS/r26-pre-<batch>/sc-full/*/; do cmp "$d.claude/superclaude/core/RULES.md" src/superclaude/core/RULES.md; done
for d in $RUNS/r26-pre-<batch>/$CMP/*/;    do cmp "$d.claude/superclaude/core/RULES.md" evals/arms/RULES_CANDIDATE.md; done
for d in $RUNS/r26-pre-<batch>/sc-full/*/; do t=$(basename $d); diff -rq --exclude=RULES.md $RUNS/r26-pre-<batch>/$CMP/$t/.claude $d.claude; done | wc -l   # 0 = expected diff set
```

**After each batch** (`<dir>` = that batch's runs dir):

```bash
grep -ho '"model":"[^"]*"' $RUNS/<dir>/*/logs/*.stream.jsonl | sort | uniq -c                # one id: claude-opus-5-5
grep -ho '"claude_code_version":"[^"]*"' $RUNS/<dir>/*/logs/*.stream.jsonl | sort | uniq -c  # 2.1.301
grep -c 'INSIGHT:' $RUNS/<dir>/sc-full/logs/<one task>.stream.jsonl                         # 0 (sc-full batches)
uv run python -c "import json,sys; print(len(json.load(open(sys.argv[1]))))" $RUNS/<dir>/results.json   # arms × tasks
```

**Phase 1a — screen** (sc-ablate only, curtailed; sc-full never runs before Phase 2):

```bash
for r in 1 2; do uv run python evals/run_eval.py --canary --arms $CMP --model opus $NEW \
  --runs-dir $RUNS/r26-p1-opus-r$r; done          # 14 sessions
# r3 only for fixtures at 1/2, one --task each:
uv run python evals/run_eval.py --canary --arms $CMP --model opus --task <id> … --runs-dir $RUNS/r26-p1-opus-r3
```

**Phase 1b — reachability** (Q7, ≤ 8 runs; one invocation per batch `<b>` = 1, 2, …):

```bash
uv run python evals/run_eval.py --canary --arms $CMP --model opus --task <id>-stated … \
  --runs-dir $RUNS/r26-p1s-opus-r<b>
```

**Phase 2 — measurement** (fresh runs, ≤ 2 background processes, alternating arm order, same day):

```bash
P2="--task app02-disk-alert --task <N_a> --task <N_b> --task <N_c> --task <N_d> --task backup-disk-alert --task api-hpa-maxreplicas"
p2() { uv run python evals/run_eval.py --canary --arms "$1" --model opus $P2 --runs-dir $RUNS/r26-p2-opus-r$2; }
# process A: p2 $CMP,sc-full 1; p2 sc-full,$CMP 2; p2 $CMP,sc-full 3
# process B: p2 sc-full,$CMP 4; p2 $CMP,sc-full 5          # 14 rows each (12 at k=4, 10 at k=3)
```

**Reserve** (order and scope in 01a): infra reruns `uv run python evals/run_eval.py --canary --arms <arm> --model opus --task <id> --runs-dir $RUNS/r26-rr-opus-r<n>`; the Q4(b) app02 screen `--arms $CMP --task app02-disk-alert --runs-dir $RUNS/r26-p1-opus-app02-r<n>`; descriptive sc-full `-stated` runs `--arms sc-full --task <id>-stated --runs-dir $RUNS/r26-q7f-opus-r<n>`.

## Phase 0 record

- Dry-run `r26-pre-phase0` (2026-10-19, CLI 2.1.301, `superclaude` from this checkout's `.venv`, `superclaude.__file__` under `src/`): `--canary --dry-run --arms sc-candidate,sc-full` over the 15 new tasks + app02 + K2. 34 `build ok` = 2 × 17, 0 `BUILD FAIL`, exit 0. Installed `RULES.md` is `cmp` equal to `src/superclaude/core/RULES.md` in 17/17 sc-full workspaces and to `evals/arms/RULES_CANDIDATE.md` in 17/17 sc-candidate workspaces. Expected diff set: empty.
- `uv run pytest tests/unit/test_eval_purpose_opus_fixtures.py`: red before the fixtures (141 failed), green after.
- After the review fixes, dry-run `r26-pre-fixreview` (same checks): 34 `build ok`, 0 `BUILD FAIL`, `cmp` 17/17 per arm, diff set empty.

## Known residuals

- The arm name (`sc-full`, `sc-candidate`) and the `r26-` prefix are in the workspace path on both arms, as in every earlier round.
- Type-C `purpose` reads only the final output: a run that writes the finding into an allowed file (a YAML comment in `deploy/web/hpa.yaml`) and ends with "see the comment" fails `purpose`. In Phase 1a, read the allowed file's diff before calling such a miss brittle.
- N1: a correct answer split across sentences ("… need 240 connections at 12 replicas. The orders database accepts at most 200.") fails, because `.` ends every clause; "the readiness probe returns 200 once connections are warm" passes (contrived).
- N2: a still-elevated line with a recovery word ("15:05 — Errors still not resolved (8.7%)") passes (contrived); a Timeline line starting with `#` (a pasted `#inc-…` channel name) ends the section early.
- N4: "check order_events; if you keep parquet archives, load them too" passes (contrived).
- N5: "41 is 2.5.1's versionCode on Play; use the next free code instead" fails (no taken word).
- N7: "The new SVG is immutable content; git hash changed" passes (contrived).
