# Cube Classification Pipeline (Spike)

A standalone spike to prove out the Mechanics/Archetype auto-classification pipeline before folding it into Cube Workshop proper. For each card, it runs a rule/tag pass against Scryfall oracle tags to suggest Mechanics, pulls EDHREC theme/synergy data as a weak signal, and runs an LLM pass to suggest Archetypes — printing both suggestion sets for manual comparison against hand-tagging, one card at a time.

## Prerequisites

- Python >= 3.12
- [`uv`](https://docs.astral.sh/uv/)
- Network access to `api.scryfall.com` and EDHREC
- An LLM provider API key (see `.env.example`)

## Setup

```bash
git clone <this-repo>
cd scryfall-tags
uv sync
cp .env.example .env   # then fill in your LLM API key
uv run python main.py <card identifier>
```

## Commands

- Install: `uv sync`
- Run: `uv run python main.py`
- Lint: `uv run ruff check .`
- Type check: `uv run mypy .`
- Test: none — manual card-by-card verification is the test method for this spike
- Migrate: n/a — no database

## Project Structure

- `docs/` — PRD, DESIGN, TASKS, and `mechanics-archetypes-taxonomy.md` (source of truth for the rule pass and LLM prompt)
- `main.py` — CLI entrypoint (to be built out starting T008)
- `verify_oracle_tags.py` — standalone helper that verifies candidate Scryfall oracle tag slugs against the live search API
- `oracle_tag_verification.csv` — output of `verify_oracle_tags.py`
