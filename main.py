import argparse
import sys

from mechanics import match_mechanics
from scryfall import CardNotFoundError, fetch_card, load_tag_ancestors
from taxonomy import parse_tag_mechanic_lookup


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Cube Classification Pipeline — fetch and classify a single Magic card."
    )
    parser.add_argument("card", help="Card name or identifier to look up")
    args = parser.parse_args(argv)

    try:
        card = fetch_card(args.card)
    except CardNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"{card.name} — {card.type_line}")
    print(card.oracle_text)
    tags = ", ".join(card.oracle_tags) if card.oracle_tags else "(none)"
    print(f"Oracle tags: {tags}")

    tag_lookup = parse_tag_mechanic_lookup()
    tag_ancestors = load_tag_ancestors()
    mechanics = match_mechanics(card.oracle_tags, tag_lookup, tag_ancestors)

    print("Mechanics:")
    if mechanics:
        for mechanic, source_tags in sorted(mechanics.items()):
            print(f"  {mechanic}: {', '.join(sorted(source_tags))}")
    else:
        print("  (none)")


if __name__ == "__main__":
    main()
