# DESIGN: Cube Classification Pipeline Spike

## Language & Tooling
- Python, managed with `uv`
- No framework — plain `requests` for Scryfall/EDHREC calls, an LLM client library for the archetype pass
- `ruff` for linting, `mypy` for type checking — matches the core Cube Workshop app's tooling; no full CI or pre-commit hooks for this spike

## Data Layer
- No database. Local file output only: a log (CSV or JSONL) recording each card's inputs and the pipeline's suggestions, for pattern review across the one-at-a-time run history

## Hosting & Deployment
- None — runs locally as a personal CLI tool. No deploy pipeline, no environment beyond the local dev machine

## Authorization
- None — single-user local tool, no accounts or permission levels

## External Integrations & Failure Handling
- **Scryfall API** — no key required; reuse the retry/backoff-with-jitter pattern already built in `verify_oracle_tags.py` for rate limits
- **EDHREC** (unofficial, via `pyedhrec`/`mightstone` or direct `json.edhrec.com` calls) — no key required, but unstable/unofficial. On failure, degrade gracefully: skip the weak-signal input for that card and proceed with Mechanics + oracle text only, rather than failing the whole lookup
- **LLM provider** — API key loaded from an env var or `.env` file, never hardcoded

## Reference Data
`mechanics-archetypes-taxonomy.md` (project root) is the source of truth for the rule/tag pass and the LLM prompt — it contains the full Mechanics/Effects table (with confirmed Scryfall oracle tag mappings) and the Archetypes table (with type/definition/qualifying signals) that steps 3 and 5 below depend on.

## Architecture / Flow
1. User invokes the CLI with a single card identifier
2. Tool fetches Scryfall card data (oracle text, type line, oracle tags)
3. Rule/tag pass matches oracle tags against the Mechanics taxonomy mapping → suggested Mechanics + source tags
4. Tool fetches EDHREC theme/synergy data (best-effort; degrades gracefully on failure)
5. LLM pass assembles the archetype-classification prompt (oracle text + mechanic tags/confidence + EDHREC signal + archetype list + mechanic-affinity heuristics) and returns suggested Archetypes
6. Both suggestion sets print to the terminal for manual comparison against hand-tagging
7. Inputs + suggestions are appended to the local log file

## Testing Approach
Manual, card-by-card verification is the primary test method — that's the point of the spike. `ruff`/`mypy` catch basic code-quality issues; no automated test suite planned given the throwaway nature of this build.

## Decision Log

### Oracle tags require a local bulk-data cache, not a per-card endpoint
Scryfall's `/cards/named` endpoint (used to fetch oracle text/type line) does not include a card's oracle tags — there is no per-card tag lookup endpoint. Oracle tags only exist in a separate, tag-centric "Oracle Tags" bulk data file (`/bulk-data`, ~5.8MB gzipped / ~18MB decompressed as of writing, updated roughly daily), where each record lists which cards (by `oracle_id`) it applies to — the inverse of what's needed.

Decision: download and cache that file locally (`.cache/oracle-tags.jsonl`, gitignored, refreshed if older than 24h), and build an in-memory `oracle_id → [tag slugs]` index from it at lookup time. Rejected alternative: querying `otag:<slug> oracleid:<id>` once per known candidate tag (~40-50 tags from the taxonomy doc) — this would mean dozens of sequential rate-limited API calls per single card lookup, working against the "fast enough for interactive one-at-a-time review" requirement, and still wouldn't surface tags outside the known candidate list.

### EDHREC access: direct `json.edhrec.com` calls, not `pyedhrec`/`mightstone`

DESIGN.md left the EDHREC access method open. Evaluated all three options live: `pyedhrec` is a thin, effectively unmaintained wrapper (5 commits, last activity 2024) whose `get_card_details()` hits a different, smaller endpoint than the one carrying synergy data — using it correctly would mean bypassing its API and calling `requests` directly anyway. `mightstone` is async-first, alpha-quality, and pulls in Pydantic/Beanie (with optional MongoDB persistence) — too heavy for a single synchronous best-effort fetch.

Decision: `edhrec.py` calls `https://json.edhrec.com/pages/cards/{slug}.json` directly via `requests`, mirroring `scryfall.py`'s style (including its own reimplementation of the retry/backoff-with-jitter helper, rather than sharing one — matching the precedent `scryfall.py` itself set against `verify_oracle_tags.py`). Slug format: lowercase, spaces→hyphens, apostrophes/commas stripped. One quirk worth flagging: EDHREC's JSON is served as static pre-rendered files behind CloudFront, so a card with no EDHREC page returns **HTTP 403** ("AccessDenied"), not 404 — `edhrec.py` treats 403 (and 404) as not-found.

### LLM provider and model: Anthropic `claude-sonnet-5`

`.env.example` had already guessed Anthropic as the provider (the project runs inside a Claude Code environment) but flagged the specific model as an open question to confirm when building the archetype pass. Confirmed Anthropic, and settled on `claude-sonnet-5` over `claude-opus-5` (the Claude API's general-purpose default) after a cost/fit comparison: per-card cost is a fraction of a cent either way (~2K input tokens for the assembled T017 prompt) so cost wasn't the deciding factor. The task is a grounded classification/extraction job — the full candidate archetype list and mechanic-affinity heuristics are already in the prompt, and the response schema constrains the model to that list — which suits Sonnet-tier models well. `claude-haiku-4-5` was ruled out: since the spike's purpose is judging whether misses trace back to fixable prompt/taxonomy gaps (PRD Success Criteria), using the weakest available model risks conflating "model wasn't sharp enough" with a genuine gap, undermining the diagnostic point of the spike.

Implementation: `llm.py`'s `classify_archetypes()` uses `client.messages.parse(output_format=...)` (structured outputs) rather than free text, with the archetype name constrained by a `Literal` type built at call time from `taxonomy.parse_archetypes()`'s names — this keeps the taxonomy doc as the single source of truth (rather than a second hardcoded archetype list) and structurally prevents the LLM from inventing an archetype outside it. No custom retry/backoff was added for the LLM call — unlike Scryfall/EDHREC, the `anthropic` SDK's own default retry (429/5xx, exponential backoff) already covers this, and DESIGN.md's retry-reuse rule was scoped to Scryfall rate limits specifically.

### T021: end-to-end verification against real hand-tagged cards, plus a DFC bug fix
Ran all 32 cards, added a new **Life Loss** mechanic (`opponent-loses-life`) and `mana-filter` to Fixing based on real misses, and fixed a real bug: `scryfall.py`'s `fetch_card()` returned empty `oracle_text` for double-faced cards (Scryfall puts DFC text under `card_faces[]`, not the top-level field) — this silently starved the Archetype prompt of rules text for any DFC. Fixed via `_extract_oracle_text()`. Full results, including patterns that don't reduce to a taxonomy fix (Strategy Shape archetypes systematically under-recalled; payoff-only archetype membership like Atraxa, Grand Unifier's missed Reanimator/Sneak tags): `docs/t021-verification-notes.md`.

## Follow-up Notes for Production Integration

Recommendations to carry into the PRD/DESIGN update that proposes how this pipeline integrates into Cube Workshop's card-add workflow (see PRD Success Criteria) — collected here as they come up during the spike, rather than acted on now. **That PRD/DESIGN update has now been written: `docs/production-integration-proposal.md`**, informed by T021's actual findings rather than these notes alone.

### Extract the taxonomy mapping out of markdown into a dedicated config format
`docs/mechanics-archetypes-taxonomy.md`'s Oracle Tag Mapping table is parsed directly by `taxonomy.py` (T011) via markdown-table parsing. That's fine for the spike — DESIGN.md already names the doc as the source of truth, and a regression test (`tests/test_taxonomy.py`) catches parsing breakage. For the production app, consider extracting this mapping into a dedicated structured format (YAML/JSON/TOML): more robust to parse than regexing markdown table rows, at the cost of splitting the source of truth in two (the human-readable doc and a machine config) unless one is generated from the other. Not worth the added machinery for a throwaway spike; worth reconsidering once this is a permanent part of the production app.
