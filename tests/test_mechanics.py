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
        ["pp-counters-matter", "gains-pp-counters", "ramp"], tag_lookup
    )

    assert sorted(matches["+1/+1 Counters"]) == [
        "gains-pp-counters",
        "pp-counters-matter",
    ]
    assert matches["Ramp"] == ["ramp"]


def test_match_mechanics_ignores_unknown_tags():
    tag_lookup = {"ramp": "Ramp"}

    matches = match_mechanics(["some-unrelated-tag", "ramp"], tag_lookup)

    assert matches == {"Ramp": ["ramp"]}


def test_match_mechanics_empty_input():
    assert match_mechanics([], {"ramp": "Ramp"}) == {}


def test_match_mechanics_with_real_taxonomy():
    tag_lookup = parse_tag_mechanic_lookup()

    matches = match_mechanics(["ramp", "some-unrelated-tag"], tag_lookup)

    assert matches == {"Ramp": ["ramp"]}
