import pytest

from main import main
from scryfall import Card, CardNotFoundError


def test_main_runs(monkeypatch, capsys):
    fake_card = Card(
        name="Lightning Bolt",
        oracle_id="4457ed35-7c10-48c8-9776-456485fdf070",
        type_line="Instant",
        oracle_text="Lightning Bolt deals 3 damage to any target.",
        oracle_tags=["burn-any", "spot-removal"],
    )
    monkeypatch.setattr("main.fetch_card", lambda name: fake_card)

    main(["Lightning Bolt"])

    captured = capsys.readouterr()
    assert "Lightning Bolt" in captured.out
    assert "burn-any" in captured.out


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
