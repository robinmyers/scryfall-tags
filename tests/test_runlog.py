import json

from edhrec import EdhrecCardList, EdhrecSignal
from llm import MODEL, ArchetypeSuggestion
from runlog import append_run
from scryfall import Card

FAKE_CARD = Card(
    name="Lightning Bolt",
    oracle_id="4457ed35-7c10-48c8-9776-456485fdf070",
    type_line="Instant",
    oracle_text="Lightning Bolt deals 3 damage to any target.",
    oracle_tags=["burn-any", "spot-removal"],
)


def _read_lines(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_append_run_writes_expected_fields(tmp_path):
    path = tmp_path / "run_log.jsonl"
    edhrec_signal = EdhrecSignal(
        similar_cards=["Shock"],
        cardlists=[
            EdhrecCardList(
                header="Top Commanders", tag="topcommanders", card_names=["Krenko"]
            )
        ],
    )
    suggestions = [ArchetypeSuggestion(archetype="Burn", reasoning="Deals damage.")]

    append_run(
        card_query="lightning bolt",
        card=FAKE_CARD,
        mechanics={"Burn": ["burn-any"]},
        edhrec_signal=edhrec_signal,
        edhrec_error=None,
        archetype_suggestions=suggestions,
        archetype_error=None,
        path=path,
    )

    entries = _read_lines(path)
    assert len(entries) == 1
    entry = entries[0]
    assert entry["card_query"] == "lightning bolt"
    assert entry["card_name"] == "Lightning Bolt"
    assert entry["type_line"] == "Instant"
    assert entry["oracle_text"] == "Lightning Bolt deals 3 damage to any target."
    assert entry["oracle_tags"] == ["burn-any", "spot-removal"]
    assert entry["mechanics"] == {"Burn": ["burn-any"]}
    assert entry["edhrec"] == {
        "status": "ok",
        "error": None,
        "similar_cards": ["Shock"],
        "cardlists": [
            {
                "header": "Top Commanders",
                "tag": "topcommanders",
                "card_names": ["Krenko"],
            }
        ],
    }
    assert entry["archetypes"] == {
        "model": MODEL,
        "status": "ok",
        "error": None,
        "suggestions": [{"archetype": "Burn", "reasoning": "Deals damage."}],
    }
    assert "timestamp" in entry


def test_append_run_appends_not_overwrites(tmp_path):
    path = tmp_path / "run_log.jsonl"

    for _ in range(2):
        append_run(
            card_query="lightning bolt",
            card=FAKE_CARD,
            mechanics={},
            edhrec_signal=None,
            edhrec_error="not found",
            archetype_suggestions=None,
            archetype_error="unavailable",
            path=path,
        )

    entries = _read_lines(path)
    assert len(entries) == 2


def test_append_run_edhrec_skipped(tmp_path):
    path = tmp_path / "run_log.jsonl"

    append_run(
        card_query="lightning bolt",
        card=FAKE_CARD,
        mechanics={},
        edhrec_signal=None,
        edhrec_error="No EDHREC page found",
        archetype_suggestions=[],
        archetype_error=None,
        path=path,
    )

    entry = _read_lines(path)[0]
    assert entry["edhrec"] == {
        "status": "skipped",
        "error": "No EDHREC page found",
        "similar_cards": None,
        "cardlists": None,
    }


def test_append_run_archetypes_skipped(tmp_path):
    path = tmp_path / "run_log.jsonl"

    append_run(
        card_query="lightning bolt",
        card=FAKE_CARD,
        mechanics={},
        edhrec_signal=None,
        edhrec_error=None,
        archetype_suggestions=None,
        archetype_error="Rate limited",
        path=path,
    )

    entry = _read_lines(path)[0]
    assert entry["archetypes"] == {
        "model": MODEL,
        "status": "skipped",
        "error": "Rate limited",
        "suggestions": None,
    }


def test_append_run_archetypes_empty_is_ok_not_skipped(tmp_path):
    path = tmp_path / "run_log.jsonl"

    append_run(
        card_query="vanilla bear",
        card=FAKE_CARD,
        mechanics={},
        edhrec_signal=None,
        edhrec_error=None,
        archetype_suggestions=[],
        archetype_error=None,
        path=path,
    )

    entry = _read_lines(path)[0]
    assert entry["archetypes"] == {
        "model": MODEL,
        "status": "ok",
        "error": None,
        "suggestions": [],
    }
