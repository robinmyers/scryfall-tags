import argparse

from scryfall import fetch_card


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Cube Classification Pipeline — fetch and classify a single Magic card."
    )
    parser.add_argument("card", help="Card name or identifier to look up")
    args = parser.parse_args(argv)

    card = fetch_card(args.card)
    print(f"{card.name} — {card.type_line}")
    print(card.oracle_text)
    tags = ", ".join(card.oracle_tags) if card.oracle_tags else "(none)"
    print(f"Oracle tags: {tags}")


if __name__ == "__main__":
    main()
