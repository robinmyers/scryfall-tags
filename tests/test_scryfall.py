from scryfall import build_oracle_tag_index, build_tag_ancestors


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
