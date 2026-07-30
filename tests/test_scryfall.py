from scryfall import build_oracle_tag_index


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
