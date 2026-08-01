import argparse
import sys

from edhrec import fetch_edhrec_signal
from mechanics import match_mechanics
from scryfall import CardNotFoundError, fetch_card, load_tag_ancestors
from taxonomy import parse_tag_mechanic_lookup

# EDHREC returns 16 cardlists per card, several capped at 50 cards (e.g. Creatures,
# Lands) that are useful as full data but too noisy to print for manual verification.
# Only these carry a meaningful synergy signal worth showing in the terminal.
EDHREC_PRINT_TAGS = {"topcommanders", "topcards", "gamechangers"}


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

    edhrec_signal = fetch_edhrec_signal(card.name)
    similar = (
        ", ".join(edhrec_signal.similar_cards)
        if edhrec_signal.similar_cards
        else "(none)"
    )
    print(f"EDHREC similar cards: {similar}")
    print("EDHREC synergy card lists:")
    shown_cardlists = [
        cardlist
        for cardlist in edhrec_signal.cardlists
        if cardlist.tag in EDHREC_PRINT_TAGS
    ]
    if shown_cardlists:
        for cardlist in shown_cardlists:
            print(f"  {cardlist.header}: {', '.join(cardlist.card_names)}")
    else:
        print("  (none)")


if __name__ == "__main__":
    main()
