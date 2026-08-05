"""Deterministic rule pass for mechanic-linked archetype membership: cards
whose already-matched Mechanics carry a taxonomy-confirmed link to an
Archetype the LLM pass doesn't reliably act on. Mirrors payoff.py's shape —
a code-computed match, not an LLM judgment.

TRUSTED_LINKS is a deliberately curated subset of the taxonomy doc's full
Mechanic->Linked Archetype table (taxonomy.parse_mechanic_linked_archetypes()),
not the whole table. Checked every linked mechanic against the 32-card T021
sample before picking this subset (see docs/linked-archetype-rule-experiment-notes.md):
blindly applying the full table nets more false positives than true
positives (e.g. Discard Outlet/Looting -> Reanimator fire on generic
card-selection tools with no real reanimator angle). These 6 are the ones
with supporting evidence in that sample.
"""

from collections import defaultdict

from llm import ArchetypeSuggestion

TRUSTED_LINKS: dict[str, list[str]] = {
    "Reanimate": ["Reanimator"],
    "Graveyard Matters": ["Graveyard"],
    "Sac Outlet": ["Aristocrats"],
    "Self-mill": ["Reanimator", "Graveyard"],
    "Recursion": ["Graveyard"],
    "Ramp": ["Ramp"],
}


def match_linked_archetypes(
    mechanics: dict[str, list[str]],
) -> list[ArchetypeSuggestion]:
    """Return Archetype suggestions for mechanics already matched by the
    rule/tag pass that carry a trusted link to an archetype. A card can
    reach the same archetype via more than one mechanic (e.g. Recursion
    and Self-mill both link to Graveyard) — those merge into a single
    suggestion whose reasoning cites every contributing mechanic."""
    sources_by_archetype: dict[str, list[str]] = defaultdict(list)
    for mechanic, source_tags in mechanics.items():
        for archetype in TRUSTED_LINKS.get(mechanic, []):
            tags = ", ".join(sorted(source_tags))
            sources_by_archetype[archetype].append(f"{mechanic} ({tags})")

    return [
        ArchetypeSuggestion(
            archetype=archetype,
            reasoning=(
                f"Matches {', '.join(sources)}, which the taxonomy links to "
                f"{archetype} (mechanic-archetype heuristic)."
            ),
        )
        for archetype, sources in sources_by_archetype.items()
    ]
