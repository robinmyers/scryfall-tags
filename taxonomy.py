"""Parse the taxonomy doc's Scryfall Oracle Tag Mapping table into a
tag slug -> Mechanic name lookup.

The doc has three tables; this parses specifically the "Scryfall Oracle
Tag Mapping" one (Mechanic | Candidate Tag(s) | Confidence | Notes) —
not the "Mechanics / Effects" table (no tag info) or "Archetypes" table
(a different milestone's concern).
"""

import re
from pathlib import Path

TAXONOMY_PATH = Path("docs/mechanics-archetypes-taxonomy.md")

_TABLE_HEADER = "| Mechanic | Candidate Tag(s) | Confidence | Notes |"
_SLUG_RE = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`")


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
