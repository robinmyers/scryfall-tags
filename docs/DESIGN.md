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

## Follow-up Notes for Production Integration

Recommendations to carry into the PRD/DESIGN update that proposes how this pipeline integrates into Cube Workshop's card-add workflow (see PRD Success Criteria) — collected here as they come up during the spike, rather than acted on now.

### Extract the taxonomy mapping out of markdown into a dedicated config format
`docs/mechanics-archetypes-taxonomy.md`'s Oracle Tag Mapping table is parsed directly by `taxonomy.py` (T011) via markdown-table parsing. That's fine for the spike — DESIGN.md already names the doc as the source of truth, and a regression test (`tests/test_taxonomy.py`) catches parsing breakage. For the production app, consider extracting this mapping into a dedicated structured format (YAML/JSON/TOML): more robust to parse than regexing markdown table rows, at the cost of splitting the source of truth in two (the human-readable doc and a machine config) unless one is generated from the other. Not worth the added machinery for a throwaway spike; worth reconsidering once this is a permanent part of the production app.
