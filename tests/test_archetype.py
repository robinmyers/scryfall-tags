from archetype import (
    SECTION_ARCHETYPES,
    SECTION_EDHREC,
    SECTION_HEURISTICS,
    SECTION_MECHANICS,
    SECTION_ORACLE_TEXT,
    build_archetype_prompt,
)
from edhrec import EdhrecCardList, EdhrecSignal
from scryfall import Card
from taxonomy import (
    Archetype,
    parse_archetypes,
    parse_mechanic_confidence,
    parse_mechanic_linked_archetypes,
)

FAKE_CARD = Card(
    name="Lightning Bolt",
    oracle_id="4457ed35-7c10-48c8-9776-456485fdf070",
    type_line="Instant",
    oracle_text="Lightning Bolt deals 3 damage to any target.",
    oracle_tags=["burn-any"],
)

FAKE_ARCHETYPES = [
    Archetype(
        name="Burn",
        type="Mechanic-Anchored",
        definition="Deals direct damage and rewards having dealt it",
        qualifying_signals="Cards tagged Mechanic:Burn",
    ),
    Archetype(
        name="Control",
        type="Strategy Shape",
        definition="Wins via resource/tempo denial",
        qualifying_signals="Efficient removal, sweepers, counterspells",
    ),
]


def _build(**overrides):
    kwargs = {
        "card": FAKE_CARD,
        "mechanics": {},
        "mechanic_confidence": {},
        "edhrec_signal": None,
        "archetypes": [],
        "linked_archetypes": {},
        **overrides,
    }
    return build_archetype_prompt(**kwargs)


def test_section_order():
    prompt = _build(
        mechanics={"Burn": ["burn-any"]},
        mechanic_confidence={"Burn": "Confirmed"},
        edhrec_signal=EdhrecSignal(similar_cards=["Shock"], cardlists=[]),
        archetypes=FAKE_ARCHETYPES,
        linked_archetypes={"Burn": "Burn"},
    )

    assert (
        prompt.index(SECTION_ORACLE_TEXT)
        < prompt.index(SECTION_MECHANICS)
        < prompt.index(SECTION_EDHREC)
        < prompt.index(SECTION_ARCHETYPES)
        < prompt.index(SECTION_HEURISTICS)
    )


def test_oracle_text_section_contents():
    prompt = _build()

    assert "Lightning Bolt — Instant" in prompt
    assert "Lightning Bolt deals 3 damage to any target." in prompt


def test_mechanics_section_empty():
    prompt = _build()

    assert f"{SECTION_MECHANICS}\n(none)" in prompt


def test_mechanics_section_shows_confidence_and_tags():
    prompt = _build(
        mechanics={"Burn": ["burn-any"]}, mechanic_confidence={"Burn": "Confirmed"}
    )

    assert "- Burn (confidence: Confirmed) — tags: burn-any" in prompt


def test_edhrec_section_unavailable_when_none():
    prompt = _build(edhrec_signal=None)

    assert f"{SECTION_EDHREC}\n(unavailable)" in prompt


def test_edhrec_section_present():
    signal = EdhrecSignal(
        similar_cards=["Shock"],
        cardlists=[
            EdhrecCardList(
                header="Top Commanders", tag="topcommanders", card_names=["Krenko"]
            )
        ],
    )

    prompt = _build(edhrec_signal=signal)

    assert "Similar cards: Shock" in prompt
    assert "- Top Commanders: Krenko" in prompt


def test_archetypes_section_lists_all_entries_unfiltered_in_order():
    prompt = _build(archetypes=FAKE_ARCHETYPES)

    burn_idx = prompt.index("- Burn [Mechanic-Anchored]")
    control_idx = prompt.index("- Control [Strategy Shape]")
    assert burn_idx < control_idx
    assert "Cards tagged Mechanic:Burn" in prompt


def test_heuristics_section_filters_out_em_dash():
    prompt = _build(linked_archetypes={"Ramp": "Ramp", "Draw": "—"})

    assert "- Ramp: Ramp" in prompt
    assert "Draw" not in prompt.split(SECTION_HEURISTICS)[1]


def test_heuristics_section_all_em_dash_shows_none():
    prompt = _build(linked_archetypes={"Draw": "—", "Counter": "—"})

    assert f"{SECTION_HEURISTICS}\n(none)" in prompt


def test_build_archetype_prompt_with_real_taxonomy_data():
    prompt = build_archetype_prompt(
        card=FAKE_CARD,
        mechanics={"Burn": ["burn-any"]},
        mechanic_confidence=parse_mechanic_confidence(),
        edhrec_signal=None,
        archetypes=parse_archetypes(),
        linked_archetypes=parse_mechanic_linked_archetypes(),
    )

    for section in (
        SECTION_ORACLE_TEXT,
        SECTION_MECHANICS,
        SECTION_EDHREC,
        SECTION_ARCHETYPES,
        SECTION_HEURISTICS,
    ):
        assert section in prompt
