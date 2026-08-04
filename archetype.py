"""Assemble the archetype-classification prompt from already-computed data:
oracle text, rule-pass mechanic matches + confidence, EDHREC signal, the full
Archetype list, and the Mechanics/Effects table's linked-archetype heuristics.
Pure string assembly — no I/O, no LLM call (that's T018).
"""

from edhrec import EdhrecSignal
from scryfall import Card
from taxonomy import Archetype

SECTION_ORACLE_TEXT = "## Oracle Text"
SECTION_MECHANICS = "## Mechanic Tags & Confidence"
SECTION_EDHREC = "## EDHREC Signal"
SECTION_ARCHETYPES = "## Candidate Archetypes"
SECTION_HEURISTICS = "## Mechanic-Archetype Heuristics"


def _oracle_text_section(card: Card) -> str:
    lines = [
        SECTION_ORACLE_TEXT,
        f"{card.name} — {card.type_line}",
        f"Mana Value: {card.mana_value}",
    ]
    if card.power is not None:
        lines.append(f"Power/Toughness: {card.power}/{card.toughness}")
    lines.append(card.oracle_text)
    return "\n".join(lines)


def _mechanics_section(
    mechanics: dict[str, list[str]], mechanic_confidence: dict[str, str]
) -> str:
    if not mechanics:
        return f"{SECTION_MECHANICS}\n(none)"
    lines = [
        f"- {mechanic} (confidence: {mechanic_confidence[mechanic]}) "
        f"— tags: {', '.join(sorted(source_tags))}"
        for mechanic, source_tags in sorted(mechanics.items())
    ]
    return "\n".join([SECTION_MECHANICS, *lines])


def _edhrec_section(edhrec_signal: EdhrecSignal | None) -> str:
    if edhrec_signal is None:
        return f"{SECTION_EDHREC}\n(unavailable)"

    similar = (
        ", ".join(edhrec_signal.similar_cards)
        if edhrec_signal.similar_cards
        else "(none)"
    )
    lines = [SECTION_EDHREC, f"Similar cards: {similar}", "Synergy card lists:"]
    if edhrec_signal.cardlists:
        lines.extend(
            f"- {cardlist.header}: {', '.join(cardlist.card_names)}"
            for cardlist in edhrec_signal.cardlists
        )
    else:
        lines.append("(none)")
    return "\n".join(lines)


def _archetypes_section(archetypes: list[Archetype]) -> str:
    lines = [
        f"- {archetype.name} [{archetype.type}]: {archetype.definition} "
        f"— Qualifying signals: {archetype.qualifying_signals}"
        for archetype in archetypes
    ]
    return "\n".join([SECTION_ARCHETYPES, *lines])


def _heuristics_section(linked_archetypes: dict[str, str]) -> str:
    lines = [
        f"- {mechanic}: {linked}"
        for mechanic, linked in linked_archetypes.items()
        if linked != "—"
    ]
    if not lines:
        return f"{SECTION_HEURISTICS}\n(none)"
    return "\n".join([SECTION_HEURISTICS, *lines])


def build_archetype_prompt(
    card: Card,
    mechanics: dict[str, list[str]],
    mechanic_confidence: dict[str, str],
    edhrec_signal: EdhrecSignal | None,
    archetypes: list[Archetype],
    linked_archetypes: dict[str, str],
) -> str:
    """Build the five-section archetype-classification prompt, in the exact
    order DESIGN.md's flow step 5 specifies: oracle text, mechanic
    tags/confidence, EDHREC signal, archetype list, mechanic-affinity
    heuristics.
    """
    return "\n\n".join(
        [
            _oracle_text_section(card),
            _mechanics_section(mechanics, mechanic_confidence),
            _edhrec_section(edhrec_signal),
            _archetypes_section(archetypes),
            _heuristics_section(linked_archetypes),
        ]
    )
