from edhrec import (
    EdhrecCardList,
    EdhrecSignal,
    _parse_edhrec_response,
    format_card_slug,
)


def test_format_card_slug_spaces():
    assert format_card_slug("Lightning Bolt") == "lightning-bolt"


def test_format_card_slug_apostrophe():
    assert format_card_slug("Kutzil's Flanker") == "kutzils-flanker"


def test_format_card_slug_comma():
    assert format_card_slug("Urza, Lord Protector") == "urza-lord-protector"


def test_parse_edhrec_response():
    data = {
        "similar": ["Chain Lightning", "Shock"],
        "container": {
            "json_dict": {
                "cardlists": [
                    {
                        "header": "Top Commanders",
                        "tag": "topcommanders",
                        "cardviews": [
                            {"name": "Vivi Ornitier"},
                            {"name": "Krenko, Mob Boss"},
                        ],
                    }
                ]
            }
        },
    }

    signal = _parse_edhrec_response(data)

    assert signal == EdhrecSignal(
        similar_cards=["Chain Lightning", "Shock"],
        cardlists=[
            EdhrecCardList(
                header="Top Commanders",
                tag="topcommanders",
                card_names=["Vivi Ornitier", "Krenko, Mob Boss"],
            )
        ],
    )


def test_parse_edhrec_response_caps_card_names():
    cardviews = [{"name": f"Card {i}"} for i in range(15)]
    data = {
        "similar": [],
        "container": {
            "json_dict": {
                "cardlists": [
                    {"header": "Creatures", "tag": "creatures", "cardviews": cardviews}
                ]
            }
        },
    }

    signal = _parse_edhrec_response(data)

    assert len(signal.cardlists[0].card_names) == 10
