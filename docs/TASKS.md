# TASKS

Status key: `[ ]` not started · `[~]` in progress · `[x]` complete · `[-]` deferred

## Milestone 1: Project Foundation — COMPLETE

Goal: Working skeleton with CI pipeline running and all checks passing

> Note: `pyproject.toml`, `uv.lock`, and a `main.py` stub already exist in this repo. T001 still needs to confirm/extend this scaffolding rather than starting from nothing. T005 is n/a — DESIGN.md specifies no database for this spike; confirm no migration step is needed rather than silently skipping it.
>
> Note: the `robinmyers/scryfall-tags` GitHub repo was switched from private to public so that branch protection (required status checks) could be enabled — GitHub only allows required status checks on private repos with a paid plan. Verified the protection actually blocks merging: a throwaway PR with a deliberate lint failure showed `mergeStateStatus: BLOCKED`, then was closed without merging.

- [x] T001 · Scaffold project structure and install dependencies — S *(merged via local `git merge feature/T001-scaffold` — no remote yet, so this stood in for a PR)*
- [x] T002 · Configure linter, formatter, and type checker — S *(ruff for lint+format, mypy non-strict per DESIGN.md tooling; merged via local `git merge feature/T002-tooling`)*
- [x] T003 · Set up GitHub Actions CI pipeline (lint → type check → test on every PR to main) — S *(created private GitHub remote `robinmyers/scryfall-tags` since Actions needed one; added `pytest` + one placeholder smoke test ahead of T007 so the "test" stage has something real to run; merged via an actual GitHub PR — the local-merge stand-in from T001/T002 ends here. Follow-up: branch protection requiring the `ci` check now enforces this on GitHub — see note below.)*
- [-] T004 · Create local deploy script triggered by git hook — S *(deferred — no deployment target for this local-only CLI spike per DESIGN.md; nothing to trigger a deploy script into)*
- [-] T005 · Set up database and run initial migration — M *(deferred — no database per DESIGN.md; confirmed n/a, not silently skipped)*
- [-] T006 · Implement health check endpoint — S *(deferred — no HTTP server/hosting in this CLI-only spike per DESIGN.md; nothing for an endpoint to attach to)*
- [x] T007 · Smoke tests confirming project setup — S *(added `test_dependencies_importable` alongside the existing entrypoint test — confirms `requests`/`anthropic`/`dotenv` installed correctly; no `.env`-loading test since no code calls it yet)*

## Milestone 2: Scryfall Card Fetch

Goal: Given a single card identifier, reliably fetch its Scryfall data. Depends on Milestone 1.

- [x] T008 · CLI entrypoint accepts a single card identifier — S *(argparse, one required positional `card` arg; `main(argv=None)` so tests can pass an explicit arg list instead of depending on real `sys.argv`; placeholder output only — T009 replaces it with the actual Scryfall fetch)*
- [x] T009 · Scryfall client: fetch card by identifier (oracle text, type line, oracle tags) — M *(bigger than typical M: discovered oracle tags aren't on the card object at all — required downloading/caching the ~18MB "Oracle Tags" bulk-data file and building an oracle_id→tags index; see DESIGN.md Decision Log. Retry/backoff pattern reimplemented in `scryfall.py`, same shape as `verify_oracle_tags.py`'s. CardNotFoundError is raised but intentionally left uncaught — that's T010's job.)*
  - Acceptance criteria: reuses the retry/backoff-with-jitter pattern already built in `verify_oracle_tags.py` for rate limits
  - Validation note: manual smoke test against a real card identifier (network call to api.scryfall.com — not automatable in CI) — verified against "Lightning Bolt": real oracle text, type line, and 5 real oracle tags all returned correctly; cache confirmed working (second run ~0.3s, no re-download)
- [x] T010 · Handle not-found / ambiguous card identifier — S · depends on T009 *(caught CardNotFoundError in main.py: clean "Error: ..." message to stderr, exit 1, no traceback. No "ambiguous" case exists by construction — exact-name lookup is deterministic (match or 404), never fuzzy, so there's nothing else to handle there.)*
  - Acceptance criteria: use Scryfall's exact-name lookup only; fail clearly with a readable error if the card isn't found — no silent fuzzy-match fallback

## Milestone 3: Rule/Tag Pass (Mechanics)

Goal: Produce Mechanics suggestions from a card's oracle tags. Depends on Milestone 2.

- [ ] T011 · Parse `mechanics-archetypes-taxonomy.md`'s mapping table into a tag→mechanic lookup — M
  - Acceptance criteria: output includes all currently-confirmed mappings (e.g. draw, cantrip, ramp) as a fixture/regression check against the current taxonomy doc
- [ ] T012 · Match a card's oracle tags against the lookup → Mechanics suggestions + source tag(s) — S · depends on T009, T011
- [ ] T013 · Print Mechanics suggestions to terminal — S · depends on T012

## Milestone 4: EDHREC Weak Signal

Goal: Add EDHREC theme/synergy data as a best-effort weak signal. Depends on Milestone 3.

- [ ] T014 · EDHREC client: fetch theme/synergy data for a card — M
  - Acceptance criteria: DESIGN.md leaves the approach open (`pyedhrec`, `mightstone`, or direct `json.edhrec.com` calls) — record which was chosen and why
- [ ] T015 · Graceful degradation on EDHREC failure — S · depends on T014
  - Acceptance criteria: on failure, skip the weak-signal input and proceed with Mechanics + oracle text only, rather than failing the whole run
  - Validation note: simulate/force a failure (e.g. bad URL or mocked timeout) and confirm the run still completes end-to-end

## Milestone 5: LLM Archetype Pass

Goal: Produce Archetype suggestions from the assembled context. Depends on Milestone 3 and Milestone 4.

- [ ] T016 · Assemble the archetype-classification prompt (oracle text + mechanic tags/confidence + EDHREC signal + archetype list + mechanic-affinity heuristics) — M
  - Acceptance criteria: define the required input sections and their order explicitly — two implementations could otherwise structure this very differently
- [ ] T017 · Call the LLM and parse the response into suggested Archetypes — M · depends on T016
  - Acceptance criteria: define the expected response shape (structured list vs. free text) and how parse failures are handled
  - Validation note: smoke test end-to-end against a real card
- [ ] T018 · Print Archetype suggestions to terminal — S · depends on T017

## Milestone 6: Run Logging

Goal: Record every run for pattern review across cards. Depends on Milestone 3 and Milestone 5.

- [ ] T019 · Append each run's inputs + suggestions to a local log file — M
  - Acceptance criteria: pick CSV or JSONL (DESIGN.md leaves this open) and document the schema
  - Validation note: run twice, confirm the log appends rather than overwrites
- [ ] T020 · End-to-end manual verification across a sample of cards — S · depends on all prior tasks
  - Acceptance criteria: maps directly to PRD Success Criteria — suggestions compared against hand-tagging across a meaningful sample; misses traced to fixable causes (tag mapping gap, prompt issue) where possible

## Deferred

Derived from PRD Non-Goals and DESIGN.md out-of-scope:

- [-] Any UI, database, or persistence layer beyond simple local output/logging
- [-] Batch or bulk processing — one card at a time only
- [-] Integration into the actual Cube Workshop app — that's an output of the spike (a proposed PRD/DESIGN update), not something built during it
- [-] Fully resolving all open tag ambiguities (e.g. Discard's still-unconfirmed tag, Tokens' text-fallback logic) before the spike starts
- [-] Any accuracy/confidence scoring system beyond passing through what the rule pass and LLM already produce
