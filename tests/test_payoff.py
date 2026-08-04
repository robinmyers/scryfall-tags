from payoff import match_payoff_archetypes
from scryfall import Card

BASE_KWARGS = {
    "name": "Test Card",
    "oracle_id": "00000000-0000-0000-0000-000000000000",
    "type_line": "Creature — Test",
    "oracle_text": "",
    "oracle_tags": [],
}


def _card(mana_value, power, toughness):
    return Card(mana_value=mana_value, power=power, toughness=toughness, **BASE_KWARGS)


def test_meets_both_thresholds_returns_both_archetypes():
    card = _card(mana_value=7.0, power="7", toughness="7")

    suggestions = match_payoff_archetypes(card)

    assert {s.archetype for s in suggestions} == {"Reanimator", "Sneak"}
    assert all("stat-based payoff heuristic" in s.reasoning for s in suggestions)


def test_below_mana_value_threshold_returns_empty():
    card = _card(mana_value=5.0, power="7", toughness="7")

    assert match_payoff_archetypes(card) == []


def test_below_stat_threshold_returns_empty():
    card = _card(mana_value=7.0, power="2", toughness="2")

    assert match_payoff_archetypes(card) == []


def test_non_creature_returns_empty():
    card = _card(mana_value=7.0, power=None, toughness=None)

    assert match_payoff_archetypes(card) == []


def test_unparseable_power_falls_back_to_toughness():
    card = _card(mana_value=7.0, power="*", toughness="7")

    assert {s.archetype for s in match_payoff_archetypes(card)} == {
        "Reanimator",
        "Sneak",
    }


def test_unparseable_power_and_low_toughness_returns_empty():
    card = _card(mana_value=7.0, power="*", toughness="2")

    assert match_payoff_archetypes(card) == []


def test_exact_threshold_boundary_meets():
    card = _card(mana_value=6.0, power="5", toughness="1")

    assert {s.archetype for s in match_payoff_archetypes(card)} == {
        "Reanimator",
        "Sneak",
    }
