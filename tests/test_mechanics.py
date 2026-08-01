from mechanics import match_mechanics
from taxonomy import parse_tag_mechanic_lookup


def test_match_mechanics_aggregates_multiple_tags():
    tag_lookup = {
        "pp-counters-matter": "+1/+1 Counters",
        "gains-pp-counters": "+1/+1 Counters",
        "gives-pp-counters": "+1/+1 Counters",
        "ramp": "Ramp",
    }

    matches = match_mechanics(
        ["pp-counters-matter", "gains-pp-counters", "ramp"], tag_lookup, {}
    )

    assert sorted(matches["+1/+1 Counters"]) == [
        "gains-pp-counters",
        "pp-counters-matter",
    ]
    assert matches["Ramp"] == ["ramp"]


def test_match_mechanics_ignores_unknown_tags():
    tag_lookup = {"ramp": "Ramp"}

    matches = match_mechanics(["some-unrelated-tag", "ramp"], tag_lookup, {})

    assert matches == {"Ramp": ["ramp"]}


def test_match_mechanics_empty_input():
    assert match_mechanics([], {"ramp": "Ramp"}, {}) == {}


def test_match_mechanics_with_real_taxonomy():
    tag_lookup = parse_tag_mechanic_lookup()

    matches = match_mechanics(["ramp", "some-unrelated-tag"], tag_lookup, {})

    assert matches == {"Ramp": ["ramp"]}


def test_match_mechanics_via_ancestor():
    tag_lookup = {"ramp": "Ramp"}
    tag_ancestors = {"land-ramp": {"ramp"}}

    matches = match_mechanics(["land-ramp"], tag_lookup, tag_ancestors)

    assert matches == {"Ramp": ["land-ramp"]}


def test_match_mechanics_via_ancestor_matches_multiple_mechanics():
    # Mirrors burn-any's real ancestry, which spans both the Burn and
    # Removal branches in Scryfall's own tag hierarchy.
    tag_lookup = {"burn": "Burn", "removal": "Removal"}
    tag_ancestors = {"burn-any": {"burn", "burn-player", "removal", "removal-creature"}}

    matches = match_mechanics(["burn-any"], tag_lookup, tag_ancestors)

    assert matches == {"Burn": ["burn-any"], "Removal": ["burn-any"]}


def test_match_mechanics_tag_with_no_ancestors_behaves_like_before():
    tag_lookup = {"counterspell": "Counter (counterspell)"}

    matches = match_mechanics(["counterspell"], tag_lookup, {})

    assert matches == {"Counter (counterspell)": ["counterspell"]}
