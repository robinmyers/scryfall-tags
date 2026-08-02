"""Append each run's inputs and suggestions to a local JSONL log, for pattern
review across cards. One JSON object per line — see docs/TASKS.md's T020
entry for the documented schema. Pure file I/O: takes already-computed data,
does no fetching/parsing itself.
"""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from edhrec import EdhrecSignal
from llm import MODEL, ArchetypeSuggestion
from scryfall import Card

LOG_PATH = Path("run_log.jsonl")


def _edhrec_entry(
    edhrec_signal: EdhrecSignal | None, edhrec_error: str | None
) -> dict[str, Any]:
    if edhrec_signal is None:
        return {
            "status": "skipped",
            "error": edhrec_error,
            "similar_cards": None,
            "cardlists": None,
        }
    return {"status": "ok", "error": None, **asdict(edhrec_signal)}


def _archetypes_entry(
    suggestions: list[ArchetypeSuggestion] | None, archetype_error: str | None
) -> dict[str, Any]:
    if suggestions is None:
        return {
            "model": MODEL,
            "status": "skipped",
            "error": archetype_error,
            "suggestions": None,
        }
    return {
        "model": MODEL,
        "status": "ok",
        "error": None,
        "suggestions": [asdict(s) for s in suggestions],
    }


def append_run(
    card_query: str,
    card: Card,
    mechanics: dict[str, list[str]],
    edhrec_signal: EdhrecSignal | None,
    edhrec_error: str | None,
    archetype_suggestions: list[ArchetypeSuggestion] | None,
    archetype_error: str | None,
    path: Path = LOG_PATH,
) -> None:
    """Append one JSONL entry recording this run's inputs and suggestions."""
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "card_query": card_query,
        "card_name": card.name,
        "type_line": card.type_line,
        "oracle_text": card.oracle_text,
        "oracle_tags": card.oracle_tags,
        "mechanics": mechanics,
        "edhrec": _edhrec_entry(edhrec_signal, edhrec_error),
        "archetypes": _archetypes_entry(archetype_suggestions, archetype_error),
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
