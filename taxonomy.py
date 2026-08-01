"""Parse the taxonomy doc's tables: the Scryfall Oracle Tag Mapping table
(tag slug -> Mechanic name, and Mechanic -> Confidence), the Mechanics /
Effects table (Mechanic -> Linked Archetype), and the Archetypes table.
"""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

TAXONOMY_PATH = Path("docs/mechanics-archetypes-taxonomy.md")

_TABLE_HEADER = "| Mechanic | Candidate Tag(s) | Confidence | Notes |"
_ARCHETYPES_HEADER = "| Archetype | Type | Definition | Qualifying Signals |"
_MECHANICS_EFFECTS_HEADER = (
    "| Mechanic | Definition | Oracle-Text Signal Examples | Linked Archetype |"
)
_SLUG_RE = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`")


@dataclass
class Archetype:
    name: str
    type: str
    definition: str
    qualifying_signals: str


def parse_tag_mechanic_lookup(path: Path = TAXONOMY_PATH) -> dict[str, str]:
    """Build a tag slug -> Mechanic name lookup from the Oracle Tag Mapping table.

    Only rows whose Confidence starts with "Confirmed" contribute tags —
    rows still needing verification (e.g. historically Discard, before it
    was confirmed) are skipped rather than risking a false match pulled
    from surrounding prose in the same cell.
    """
    lines = path.read_text(encoding="utf-8").splitlines()

    start = lines.index(_TABLE_HEADER) + 2  # +2 skips the header and its separator row
    lookup: dict[str, str] = {}
    for line in lines[start:]:
        if not line.strip().startswith("|"):
            break  # table has ended

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        mechanic, candidate_tags, confidence = cells[0], cells[1], cells[2]

        if not confidence.startswith("Confirmed"):
            continue

        for slug in _SLUG_RE.findall(candidate_tags):
            existing = lookup.get(slug)
            if existing is not None and existing != mechanic:
                raise ValueError(
                    f"Tag {slug!r} maps to both {existing!r} and {mechanic!r} "
                    "in the taxonomy doc — resolve the conflict before proceeding."
                )
            lookup[slug] = mechanic

    return lookup


def _table_rows(path: Path, header: str) -> Iterator[list[str]]:
    """Yield stripped cell lists for each row of the table starting at `header`,
    mirroring parse_tag_mechanic_lookup's own row-walking."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = lines.index(header) + 2  # +2 skips the header and its separator row
    for line in lines[start:]:
        if not line.strip().startswith("|"):
            break  # table has ended
        yield [cell.strip() for cell in line.strip().strip("|").split("|")]


def parse_archetypes(path: Path = TAXONOMY_PATH) -> list[Archetype]:
    """Parse the Archetypes table in full, doc order. Strips the '**bold**'
    wrapper some archetype names carry (table markup, not content) — the
    Qualifying Signals text otherwise stays verbatim, inline markdown and all,
    since it's meant to be pasted into the LLM prompt as-is.
    """
    return [
        Archetype(
            name=cells[0].strip("*"),
            type=cells[1],
            definition=cells[2],
            qualifying_signals=cells[3],
        )
        for cells in _table_rows(path, _ARCHETYPES_HEADER)
    ]


def parse_mechanic_linked_archetypes(path: Path = TAXONOMY_PATH) -> dict[str, str]:
    """Mechanic name -> raw Linked Archetype cell ("—" or a comma-list), from
    the Mechanics/Effects table. Keyed by that table's own Mechanic-name
    spelling, which differs from the Oracle Tag Mapping table's for one row
    ("Counter" vs. "Counter (counterspell)") — do not cross-look-up this dict
    by a match_mechanics()-matched mechanic name.
    """
    return {
        cells[0]: cells[3] for cells in _table_rows(path, _MECHANICS_EFFECTS_HEADER)
    }


def parse_mechanic_confidence(path: Path = TAXONOMY_PATH) -> dict[str, str]:
    """Mechanic name -> Confidence label, from the Oracle Tag Mapping table —
    the same table parse_tag_mechanic_lookup draws from, so this is keyed
    identically to match_mechanics()'s output keys.
    """
    return {cells[0]: cells[2] for cells in _table_rows(path, _TABLE_HEADER)}
