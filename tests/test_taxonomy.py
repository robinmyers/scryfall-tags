from taxonomy import parse_tag_mechanic_lookup


def test_parse_tag_mechanic_lookup():
    lookup = parse_tag_mechanic_lookup()

    assert lookup["draw"] == "Draw"
    assert lookup["cantrip"] == "Cantrip"
    assert lookup["ramp"] == "Ramp"
    assert lookup["mana-dork"] == "Mana Dork"  # distinct mechanic from Ramp
    assert lookup["discard"] == "Discard"
    assert lookup["gains-pp-counters"] == "+1/+1 Counters"  # multi-tag mechanic
    assert lookup["repeatable-token-generator"] == "Tokens"  # "Confirmed (partial)"

    # discard-outlet must stay scoped to its own row, not bleed into Discard
    assert lookup["discard-outlet"] == "Discard Outlet"
