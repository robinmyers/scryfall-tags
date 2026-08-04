import pytest
import requests

from edhrec import EdhrecNotFoundError, EdhrecSignal
from llm import ArchetypeClassificationError, ArchetypeSuggestion
from main import main
from scryfall import Card, CardNotFoundError
from taxonomy import Archetype

FAKE_EDHREC_SIGNAL = EdhrecSignal(similar_cards=["Shock"], cardlists=[])


def test_main_runs(monkeypatch, capsys):
    fake_card = Card(
        name="Lightning Bolt",
        oracle_id="4457ed35-7c10-48c8-9776-456485fdf070",
        type_line="Instant",
        oracle_text="Lightning Bolt deals 3 damage to any target.",
        oracle_tags=["burn-any", "spot-removal"],
        mana_value=1.0,
        power=None,
        toughness=None,
    )
    monkeypatch.setattr("main.fetch_card", lambda name: fake_card)
    monkeypatch.setattr("main.parse_tag_mechanic_lookup", dict)
    monkeypatch.setattr("main.load_tag_ancestors", dict)
    monkeypatch.setattr("main.fetch_edhrec_signal", lambda name: FAKE_EDHREC_SIGNAL)
    monkeypatch.setattr("main.classify_archetypes", lambda prompt, archetype_names: [])
    monkeypatch.setattr("main.append_run", lambda **kwargs: None)

    main(["Lightning Bolt"])

    captured = capsys.readouterr()
    assert "Lightning Bolt" in captured.out
    assert "burn-any" in captured.out


def test_main_prints_mechanics(monkeypatch, capsys):
    fake_card = Card(
        name="Lightning Bolt",
        oracle_id="4457ed35-7c10-48c8-9776-456485fdf070",
        type_line="Instant",
        oracle_text="Lightning Bolt deals 3 damage to any target.",
        oracle_tags=["burn-any", "spot-removal"],
        mana_value=1.0,
        power=None,
        toughness=None,
    )
    monkeypatch.setattr("main.fetch_card", lambda name: fake_card)
    monkeypatch.setattr(
        "main.parse_tag_mechanic_lookup",
        lambda: {"burn": "Burn", "removal": "Removal"},
    )
    monkeypatch.setattr(
        "main.load_tag_ancestors",
        lambda: {"burn-any": {"burn", "removal"}, "spot-removal": {"removal"}},
    )
    monkeypatch.setattr("main.fetch_edhrec_signal", lambda name: FAKE_EDHREC_SIGNAL)
    monkeypatch.setattr("main.classify_archetypes", lambda prompt, archetype_names: [])
    monkeypatch.setattr("main.append_run", lambda **kwargs: None)

    main(["Lightning Bolt"])

    captured = capsys.readouterr()
    assert "Mechanics:" in captured.out
    assert "Burn: burn-any" in captured.out
    assert "Removal: burn-any, spot-removal" in captured.out


def test_main_prints_no_mechanics(monkeypatch, capsys):
    fake_card = Card(
        name="Vanilla Bear",
        oracle_id="00000000-0000-0000-0000-000000000000",
        type_line="Creature — Bear",
        oracle_text="",
        oracle_tags=["unrelated-tag"],
        mana_value=2.0,
        power="2",
        toughness="2",
    )
    monkeypatch.setattr("main.fetch_card", lambda name: fake_card)
    monkeypatch.setattr("main.parse_tag_mechanic_lookup", lambda: {"burn": "Burn"})
    monkeypatch.setattr("main.load_tag_ancestors", dict)
    monkeypatch.setattr("main.fetch_edhrec_signal", lambda name: FAKE_EDHREC_SIGNAL)
    monkeypatch.setattr("main.classify_archetypes", lambda prompt, archetype_names: [])
    monkeypatch.setattr("main.append_run", lambda **kwargs: None)

    main(["Vanilla Bear"])

    captured = capsys.readouterr()
    assert "Mechanics:\n  (none)" in captured.out


def test_main_prints_edhrec_signal(monkeypatch, capsys):
    fake_card = Card(
        name="Lightning Bolt",
        oracle_id="4457ed35-7c10-48c8-9776-456485fdf070",
        type_line="Instant",
        oracle_text="Lightning Bolt deals 3 damage to any target.",
        oracle_tags=[],
        mana_value=1.0,
        power=None,
        toughness=None,
    )
    monkeypatch.setattr("main.fetch_card", lambda name: fake_card)
    monkeypatch.setattr("main.parse_tag_mechanic_lookup", dict)
    monkeypatch.setattr("main.load_tag_ancestors", dict)
    monkeypatch.setattr("main.fetch_edhrec_signal", lambda name: FAKE_EDHREC_SIGNAL)
    monkeypatch.setattr("main.classify_archetypes", lambda prompt, archetype_names: [])
    monkeypatch.setattr("main.append_run", lambda **kwargs: None)

    main(["Lightning Bolt"])

    captured = capsys.readouterr()
    assert "EDHREC similar cards: Shock" in captured.out
    assert "EDHREC synergy card lists:\n  (none)" in captured.out


def test_main_degrades_on_edhrec_not_found(monkeypatch, capsys):
    fake_card = Card(
        name="Lightning Bolt",
        oracle_id="4457ed35-7c10-48c8-9776-456485fdf070",
        type_line="Instant",
        oracle_text="Lightning Bolt deals 3 damage to any target.",
        oracle_tags=["burn-any", "spot-removal"],
        mana_value=1.0,
        power=None,
        toughness=None,
    )
    monkeypatch.setattr("main.fetch_card", lambda name: fake_card)
    monkeypatch.setattr(
        "main.parse_tag_mechanic_lookup",
        lambda: {"burn": "Burn", "removal": "Removal"},
    )
    monkeypatch.setattr(
        "main.load_tag_ancestors",
        lambda: {"burn-any": {"burn", "removal"}, "spot-removal": {"removal"}},
    )

    def raise_not_found(name):
        raise EdhrecNotFoundError(f"No EDHREC page found for {name!r}")

    monkeypatch.setattr("main.fetch_edhrec_signal", raise_not_found)
    monkeypatch.setattr("main.classify_archetypes", lambda prompt, archetype_names: [])
    monkeypatch.setattr("main.append_run", lambda **kwargs: None)

    main(["Lightning Bolt"])

    captured = capsys.readouterr()
    assert "Mechanics:" in captured.out
    assert "Burn: burn-any" in captured.out
    assert "EDHREC: (skipped)" in captured.out
    assert "EDHREC: unavailable" in captured.err


def test_main_no_edhrec_flag_skips_fetch(monkeypatch, capsys):
    fake_card = Card(
        name="Lightning Bolt",
        oracle_id="4457ed35-7c10-48c8-9776-456485fdf070",
        type_line="Instant",
        oracle_text="Lightning Bolt deals 3 damage to any target.",
        oracle_tags=["burn-any", "spot-removal"],
        mana_value=1.0,
        power=None,
        toughness=None,
    )
    monkeypatch.setattr("main.fetch_card", lambda name: fake_card)
    monkeypatch.setattr(
        "main.parse_tag_mechanic_lookup",
        lambda: {"burn": "Burn", "removal": "Removal"},
    )
    monkeypatch.setattr(
        "main.load_tag_ancestors",
        lambda: {"burn-any": {"burn", "removal"}, "spot-removal": {"removal"}},
    )

    def fail_if_called(name):
        raise AssertionError(
            "fetch_edhrec_signal should not be called with --no-edhrec"
        )

    monkeypatch.setattr("main.fetch_edhrec_signal", fail_if_called)
    monkeypatch.setattr("main.classify_archetypes", lambda prompt, archetype_names: [])
    monkeypatch.setattr("main.append_run", lambda **kwargs: None)

    main(["Lightning Bolt", "--no-edhrec"])

    captured = capsys.readouterr()
    assert "EDHREC: (skipped)" in captured.out
    assert "EDHREC: unavailable" not in captured.err


def test_main_degrades_on_edhrec_network_error(monkeypatch, capsys):
    fake_card = Card(
        name="Lightning Bolt",
        oracle_id="4457ed35-7c10-48c8-9776-456485fdf070",
        type_line="Instant",
        oracle_text="Lightning Bolt deals 3 damage to any target.",
        oracle_tags=["burn-any", "spot-removal"],
        mana_value=1.0,
        power=None,
        toughness=None,
    )
    monkeypatch.setattr("main.fetch_card", lambda name: fake_card)
    monkeypatch.setattr(
        "main.parse_tag_mechanic_lookup",
        lambda: {"burn": "Burn", "removal": "Removal"},
    )
    monkeypatch.setattr(
        "main.load_tag_ancestors",
        lambda: {"burn-any": {"burn", "removal"}, "spot-removal": {"removal"}},
    )

    def raise_connection_error(name):
        raise requests.exceptions.ConnectionError("connection refused")

    monkeypatch.setattr("main.fetch_edhrec_signal", raise_connection_error)
    monkeypatch.setattr("main.classify_archetypes", lambda prompt, archetype_names: [])
    monkeypatch.setattr("main.append_run", lambda **kwargs: None)

    main(["Lightning Bolt"])

    captured = capsys.readouterr()
    assert "Mechanics:" in captured.out
    assert "Burn: burn-any" in captured.out
    assert "EDHREC: (skipped)" in captured.out
    assert "EDHREC: unavailable" in captured.err


def _patch_common(monkeypatch, fake_card):
    monkeypatch.setattr("main.fetch_card", lambda name: fake_card)
    monkeypatch.setattr("main.parse_tag_mechanic_lookup", lambda: {"burn-any": "Burn"})
    monkeypatch.setattr("main.load_tag_ancestors", dict)
    monkeypatch.setattr("main.fetch_edhrec_signal", lambda name: FAKE_EDHREC_SIGNAL)
    monkeypatch.setattr("main.parse_mechanic_confidence", lambda: {"Burn": "Confirmed"})
    monkeypatch.setattr(
        "main.parse_archetypes",
        lambda: [
            Archetype(
                name="Burn",
                type="Mechanic-Anchored",
                definition="Deals direct damage",
                qualifying_signals="Cards tagged Mechanic:Burn",
            )
        ],
    )
    monkeypatch.setattr(
        "main.parse_mechanic_linked_archetypes", lambda: {"Burn": "Burn"}
    )


def test_main_prints_archetype_suggestions(monkeypatch, capsys):
    fake_card = Card(
        name="Lightning Bolt",
        oracle_id="4457ed35-7c10-48c8-9776-456485fdf070",
        type_line="Instant",
        oracle_text="Lightning Bolt deals 3 damage to any target.",
        oracle_tags=["burn-any"],
        mana_value=1.0,
        power=None,
        toughness=None,
    )
    _patch_common(monkeypatch, fake_card)
    monkeypatch.setattr(
        "main.classify_archetypes",
        lambda prompt, archetype_names: [
            ArchetypeSuggestion(archetype="Burn", reasoning="Deals direct damage.")
        ],
    )
    monkeypatch.setattr("main.append_run", lambda **kwargs: None)

    main(["Lightning Bolt"])

    captured = capsys.readouterr()
    assert "Archetypes:" in captured.out
    assert "  Burn: Deals direct damage." in captured.out


def test_main_prints_no_archetype_suggestions(monkeypatch, capsys):
    fake_card = Card(
        name="Vanilla Bear",
        oracle_id="00000000-0000-0000-0000-000000000000",
        type_line="Creature — Bear",
        oracle_text="",
        oracle_tags=[],
        mana_value=2.0,
        power="2",
        toughness="2",
    )
    _patch_common(monkeypatch, fake_card)
    monkeypatch.setattr("main.classify_archetypes", lambda prompt, archetype_names: [])
    monkeypatch.setattr("main.append_run", lambda **kwargs: None)

    main(["Vanilla Bear"])

    captured = capsys.readouterr()
    assert "Archetypes:\n  (none)" in captured.out


def test_main_merges_payoff_archetype_suggestions(monkeypatch, capsys):
    fake_card = Card(
        name="Big Beater",
        oracle_id="00000000-0000-0000-0000-000000000001",
        type_line="Creature — Giant",
        oracle_text="",
        oracle_tags=[],
        mana_value=7.0,
        power="7",
        toughness="7",
    )
    _patch_common(monkeypatch, fake_card)
    monkeypatch.setattr(
        "main.classify_archetypes",
        lambda prompt, archetype_names: [
            ArchetypeSuggestion(archetype="Burn", reasoning="Deals direct damage.")
        ],
    )
    monkeypatch.setattr("main.append_run", lambda **kwargs: None)

    main(["Big Beater"])

    captured = capsys.readouterr()
    assert "  Burn: Deals direct damage." in captured.out
    assert "  Reanimator:" in captured.out
    assert "  Sneak:" in captured.out


def test_main_payoff_merge_does_not_duplicate_llm_suggestion(monkeypatch, capsys):
    fake_card = Card(
        name="Big Beater",
        oracle_id="00000000-0000-0000-0000-000000000001",
        type_line="Creature — Giant",
        oracle_text="",
        oracle_tags=[],
        mana_value=7.0,
        power="7",
        toughness="7",
    )
    _patch_common(monkeypatch, fake_card)
    monkeypatch.setattr(
        "main.classify_archetypes",
        lambda prompt, archetype_names: [
            ArchetypeSuggestion(
                archetype="Reanimator", reasoning="Already caught it via text."
            )
        ],
    )
    monkeypatch.setattr("main.append_run", lambda **kwargs: None)

    main(["Big Beater"])

    captured = capsys.readouterr()
    assert captured.out.count("Reanimator:") == 1
    assert "  Reanimator: Already caught it via text." in captured.out
    assert "  Sneak:" in captured.out


def test_main_degrades_on_archetype_classification_error(monkeypatch, capsys):
    fake_card = Card(
        name="Lightning Bolt",
        oracle_id="4457ed35-7c10-48c8-9776-456485fdf070",
        type_line="Instant",
        oracle_text="Lightning Bolt deals 3 damage to any target.",
        oracle_tags=["burn-any"],
        mana_value=1.0,
        power=None,
        toughness=None,
    )
    _patch_common(monkeypatch, fake_card)

    def raise_classification_error(prompt, archetype_names):
        raise ArchetypeClassificationError("API error: overloaded")

    monkeypatch.setattr("main.classify_archetypes", raise_classification_error)
    monkeypatch.setattr("main.append_run", lambda **kwargs: None)

    main(["Lightning Bolt"])

    captured = capsys.readouterr()
    assert "Mechanics:" in captured.out
    assert "EDHREC similar cards:" in captured.out
    assert "Archetypes:\n  (skipped)" in captured.out
    assert "Archetypes: unavailable" in captured.err


def test_main_not_found(monkeypatch, capsys):
    def raise_not_found(name):
        raise CardNotFoundError(f"No card found matching {name!r}")

    monkeypatch.setattr("main.fetch_card", raise_not_found)

    with pytest.raises(SystemExit) as exc_info:
        main(["Not A Real Card Xyz123"])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "No card found matching" in captured.err


def test_dependencies_importable():
    import anthropic
    import dotenv
    import requests

    assert requests and anthropic and dotenv
