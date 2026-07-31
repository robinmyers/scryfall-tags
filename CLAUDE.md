# CLAUDE.md

## What This Project Is

A standalone spike to prove out the Mechanics/Archetype auto-classification pipeline — running a rule/tag pass against Scryfall oracle tags and an LLM archetype pass against real Modern Cube cards — before folding it into Cube Workshop's card-add UI.

## Key Documents

- Product requirements: `docs/PRD.md`
- Technical design: `docs/DESIGN.md`
- Task backlog: `docs/TASKS.md`
- Taxonomy reference (source of truth for the rule pass and LLM prompt): `docs/mechanics-archetypes-taxonomy.md`

Always read relevant docs before starting work. If a task touches the data model, read DESIGN.md first. If scope is unclear, read PRD.md. If a task touches Mechanics/Archetype matching logic or the LLM prompt, read `mechanics-archetypes-taxonomy.md` first.

## Current Focus

<!-- Update this before every session. -->
**T012 · Match a card's oracle tags against the lookup → Mechanics suggestions + source tag(s)**

## Commands

- Install: `uv sync`
- Run: `uv run python main.py "<card name>"` (e.g. `uv run python main.py "Lightning Bolt"`; entrypoint will evolve further as T012+ build out the pipeline). First run downloads/caches `.cache/oracle-tags.jsonl` (~18MB, refreshed every 24h)
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Type check: `uv run mypy .`
- Test: `uv run pytest` — five smoke/unit tests (entrypoint runs with a mocked Scryfall fetch; not-found card exits 1 with a clean message; core dependencies import cleanly; oracle-tag index builder is unit-tested against a fixture; taxonomy doc's tag→mechanic table is regression-tested against the real doc — no test hits the live network); DESIGN.md's manual card-by-card verification remains the actual correctness check for Mechanics/Archetype suggestions, not this suite
- Migrate: n/a — no database
- No pre-commit hooks — DESIGN.md explicitly scopes this spike without them

## Branching

- `main` is always deployable — never commit directly
- One branch per task: `feature/T001-scaffold`, `feature/T002-tooling`, etc.
- PR required to merge — use it as a checkpoint even on a solo project
- Branch from `main`, merge back to `main` via PR
- CI must pass before merging — GitHub-enforced via branch protection on `main` (required status check: `ci`), not just a stated convention. Repo is public (required to enable branch protection on the free plan)
- **Never merge a PR without being asked.** Open it, confirm CI passes, then stop and let the user review — do not run `gh pr merge` unprompted.

## Behavioral Principles

### 1. Think Before Coding
**Don't assume. Don't hide confusion. Surface tradeoffs.**
Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First
**Minimum code that solves the problem. Nothing speculative.**
- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.
Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes
**Touch only what you must. Clean up only your own mess.**
When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.
The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution
**Define success criteria. Loop until verified.**
Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"
For multi-step tasks, state a brief plan:
```javascript
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

## Definition of Done

Before marking any task complete, run in order:

1. Lint command — must return no errors
2. Type check command — must return no errors
3. Test command — `uv run pytest` must pass; for pipeline stages, also manually run the affected stage against a real card and compare output to hand-tagging judgment (classification-suggestion correctness isn't covered by the automated suite)
4. If a new pipeline stage was added (Scryfall fetch, EDHREC fetch, LLM call): run it against a real card identifier as a smoke test
5. Manually verify acceptance criteria in TASKS.md
6. DESIGN.md decision log updated if a significant choice was made
7. README.md updated if setup or usage changed

## Hard Rules

DESIGN.md has no section literally titled "Hard Rules." The list below is derived from constraints stated throughout DESIGN.md — flagged as inferred, not copied verbatim. Consider formalizing a real Hard Rules section in DESIGN.md (see decision log).

1. No database — local file log (CSV/JSONL) only, for run history.
2. No UI, no persistence beyond the local log — CLI only.
3. One card at a time only — no batch/bulk processing.
4. LLM API key loaded from an env var or `.env` file — never hardcoded.
5. EDHREC lookups are best-effort: on failure, skip the weak-signal input and proceed with Mechanics + oracle text only, rather than failing the whole run.
6. Reuse the existing retry/backoff-with-jitter pattern from `verify_oracle_tags.py` for Scryfall rate limits.
7. No deploy pipeline, no hosting — runs locally only, personal tool.
8. `mechanics-archetypes-taxonomy.md` is the source of truth for both the rule/tag pass and the LLM prompt.

## Decision Protocol

If a task requires a significant architectural choice not covered in DESIGN.md:

1. Write a short proposal — what, why, tradeoffs
2. Flag for review before proceeding
3. Log the final decision in DESIGN.md decision log

Do not make significant decisions silently.

## Session Startup Checklist

1. Read this file
2. Read the Current Focus section
3. Read the referenced task in TASKS.md
4. Read any docs flagged as relevant
5. If frontend task: check docs/mocks/ and ask for screenshots (not expected for this project — CLI-only, no UI)
6. Confirm understanding of the goal before writing any code
