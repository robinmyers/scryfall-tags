"""Deterministic stat-based rule pass for payoff-only archetype membership:
cards that qualify for Reanimator/Sneak purely by being a plausible big
target for what other cards do to them, with no textual self-signal.
Mirrors mechanics.py's shape — a code-computed match, not an LLM judgment.
"""

from llm import ArchetypeSuggestion
from scryfall import Card

PAYOFF_ARCHETYPES = ["Reanimator", "Sneak"]
MANA_VALUE_THRESHOLD = 6.0
STAT_THRESHOLD = 5


def _parse_stat(value: str | None) -> float | None:
    """Power/toughness are strings and can be non-numeric ("*", "1+*").
    Returns None for anything that doesn't parse as a plain number."""
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _meets_stat_threshold(card: Card) -> bool:
    if card.mana_value < MANA_VALUE_THRESHOLD:
        return False
    power = _parse_stat(card.power)
    toughness = _parse_stat(card.toughness)
    return (power is not None and power >= STAT_THRESHOLD) or (
        toughness is not None and toughness >= STAT_THRESHOLD
    )


def match_payoff_archetypes(card: Card) -> list[ArchetypeSuggestion]:
    """Return Reanimator/Sneak suggestions for cards whose mana value and
    power/toughness clear the stat threshold for a plausible big-creature
    payoff target — even with no textual signal for the archetype's own
    core mechanic. Empty for non-creatures or cards below the threshold."""
    if not _meets_stat_threshold(card):
        return []

    return [
        ArchetypeSuggestion(
            archetype=archetype,
            reasoning=(
                f"Mana value {card.mana_value} and power/toughness "
                f"{card.power}/{card.toughness} clear the stat threshold for "
                f"a plausible {archetype} target, even without direct "
                "textual signal (stat-based payoff heuristic)."
            ),
        )
        for archetype in PAYOFF_ARCHETYPES
    ]
