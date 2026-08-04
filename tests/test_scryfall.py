from scryfall import (
    _extract_oracle_text,
    _extract_power_toughness,
    build_oracle_tag_index,
    build_tag_ancestors,
)


def test_build_oracle_tag_index():
    records = [
        {
            "slug": "burn-any",
            "taggings": [{"oracle_id": "aaa", "weight": "very_strong"}],
        },
        {
            "slug": "spot-removal",
            "taggings": [
                {"oracle_id": "aaa", "weight": "median"},
                {"oracle_id": "bbb", "weight": "median"},
            ],
        },
    ]

    index = build_oracle_tag_index(records)

    assert sorted(index["aaa"]) == ["burn-any", "spot-removal"]
    assert index["bbb"] == ["spot-removal"]


def test_build_tag_ancestors():
    # Mirrors the real hierarchy shape: burn-any has two parent branches
    # (burn-player, itself a child of burn; and removal directly) —
    # covers root/no-parent, direct parent, transitive (grandparent), and
    # multi-parent tags all in one fixture.
    records = [
        {"id": "removal-id", "slug": "removal", "parent_ids": []},
        {"id": "burn-id", "slug": "burn", "parent_ids": []},
        {"id": "bp-id", "slug": "burn-player", "parent_ids": ["burn-id"]},
        {"id": "ba-id", "slug": "burn-any", "parent_ids": ["bp-id", "removal-id"]},
    ]

    ancestors = build_tag_ancestors(records)

    assert ancestors["removal"] == set()
    assert ancestors["burn"] == set()
    assert ancestors["burn-player"] == {"burn"}
    assert ancestors["burn-any"] == {"burn-player", "burn", "removal"}


def test_extract_oracle_text_single_faced():
    data = {"oracle_text": "Deals 3 damage to any target."}

    assert _extract_oracle_text(data) == "Deals 3 damage to any target."


def test_extract_oracle_text_double_faced():
    # Double-faced cards have no top-level oracle_text — Scryfall splits it
    # across card_faces instead (confirmed against the real API for
    # Rona, Herald of Invasion // Rona, Tolarian Obliterator during T021).
    data = {
        "card_faces": [
            {"name": "Front Face", "oracle_text": "Front face text."},
            {"name": "Back Face", "oracle_text": "Back face text."},
        ]
    }

    assert _extract_oracle_text(data) == "Front face text.\n//\nBack face text."


def test_extract_power_toughness_creature():
    data = {"power": "7", "toughness": "7"}

    assert _extract_power_toughness(data) == ("7", "7")


def test_extract_power_toughness_non_creature():
    data = {"oracle_text": "Lightning Bolt deals 3 damage to any target."}

    assert _extract_power_toughness(data) == (None, None)


def test_extract_power_toughness_double_faced():
    # Double-faced creatures have no top-level power/toughness when faces
    # differ (confirmed against the real API for Rona, Herald of Invasion //
    # Rona, Tolarian Obliterator: front face 1/3, back face 5/5) — falls
    # back to the front face, same pattern as _extract_oracle_text.
    data = {
        "card_faces": [
            {"name": "Front Face", "power": "1", "toughness": "3"},
            {"name": "Back Face", "power": "5", "toughness": "5"},
        ]
    }

    assert _extract_power_toughness(data) == ("1", "3")
