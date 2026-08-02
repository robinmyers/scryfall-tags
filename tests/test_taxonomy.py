from taxonomy import (
    parse_archetypes,
    parse_mechanic_confidence,
    parse_mechanic_linked_archetypes,
    parse_tag_mechanic_lookup,
)


def test_parse_tag_mechanic_lookup():
    lookup = parse_tag_mechanic_lookup()

    assert lookup["draw"] == "Draw"
    assert lookup["cantrip"] == "Cantrip"
    assert lookup["ramp"] == "Ramp"
    assert lookup["mana-dork"] == "Mana Dork"  # distinct mechanic from Ramp
    assert lookup["discard"] == "Discard"
    assert lookup["gains-pp-counters"] == "+1/+1 Counters"  # multi-tag mechanic
    assert lookup["repeatable-token-generator"] == "Tokens"  # "Confirmed (partial)"
    assert lookup["opponent-loses-life"] == "Life Loss"  # added during T021
    assert lookup["mana-filter"] == "Fixing"  # added during T021

    # discard-outlet must stay scoped to its own row, not bleed into Discard
    assert lookup["discard-outlet"] == "Discard Outlet"


def test_parse_archetypes():
    archetypes = parse_archetypes()
    by_name = {archetype.name: archetype for archetype in archetypes}

    assert len(archetypes) == 25

    control = by_name["Control"]
    assert control.type == "Strategy Shape"
    assert "resource/tempo denial" in control.definition

    # bold-wrapped names ("**Ramp**") must have the markup stripped
    ramp = by_name["Ramp"]
    assert ramp.type == "Mechanic-Anchored"
    assert "*plus*" in ramp.qualifying_signals  # inline markdown kept verbatim


def test_parse_mechanic_linked_archetypes():
    linked = parse_mechanic_linked_archetypes()

    assert linked["Ramp"] == "Ramp"
    assert linked["Looting"] == "Graveyard, Reanimator"
    assert linked["Draw"] == "—"


def test_parse_mechanic_confidence():
    confidence = parse_mechanic_confidence()

    assert confidence["Draw"] == "Confirmed"
    assert confidence["Tokens"] == "Confirmed (partial)"


def test_counter_mechanic_name_differs_between_tables():
    # The Mechanics/Effects table names this row "Counter"; the Oracle Tag
    # Mapping table names it "Counter (counterspell)" — the one known naming
    # mismatch between the two tables. archetype.py's heuristics section is
    # deliberately designed around never cross-looking-up these two dicts by
    # name, so this guards against a future doc edit silently invalidating
    # that assumption.
    linked = parse_mechanic_linked_archetypes()
    confidence = parse_mechanic_confidence()

    assert "Counter" in linked
    assert "Counter" not in confidence
    assert "Counter (counterspell)" in confidence
    assert "Counter (counterspell)" not in linked
