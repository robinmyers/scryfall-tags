import argparse
import sys

import requests

from archetype import build_archetype_prompt
from edhrec import EdhrecNotFoundError, fetch_edhrec_signal
from llm import ArchetypeClassificationError, classify_archetypes
from mechanics import match_mechanics
from payoff import match_payoff_archetypes
from runlog import append_run
from scryfall import CardNotFoundError, fetch_card, load_tag_ancestors
from taxonomy import (
    parse_archetypes,
    parse_mechanic_confidence,
    parse_mechanic_linked_archetypes,
    parse_tag_mechanic_lookup,
)

# EDHREC returns 16 cardlists per card, several capped at 50 cards (e.g. Creatures,
# Lands) that are useful as full data but too noisy to print for manual verification.
# Only these carry a meaningful synergy signal worth showing in the terminal.
EDHREC_PRINT_TAGS = {"topcommanders", "topcards", "gamechangers"}


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Cube Classification Pipeline — fetch and classify a single Magic card."
    )
    parser.add_argument("card", help="Card name or identifier to look up")
    parser.add_argument(
        "--no-edhrec",
        action="store_true",
        help="Skip the EDHREC fetch and run the Archetype pass without the "
        "weak signal (for ablation testing)",
    )
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

    if args.no_edhrec:
        edhrec_signal = None
        edhrec_error = "disabled via --no-edhrec flag"
    else:
        try:
            edhrec_signal = fetch_edhrec_signal(card.name)
            edhrec_error = None
        except (EdhrecNotFoundError, requests.RequestException) as exc:
            edhrec_error = str(exc)
            print(
                f"EDHREC: unavailable ({edhrec_error}) — skipping weak signal",
                file=sys.stderr,
            )
            edhrec_signal = None

    if edhrec_signal is None:
        print("EDHREC: (skipped)")
    else:
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

    mechanic_confidence = parse_mechanic_confidence()
    archetypes = parse_archetypes()
    linked_archetypes = parse_mechanic_linked_archetypes()
    prompt = build_archetype_prompt(
        card,
        mechanics,
        mechanic_confidence,
        edhrec_signal,
        archetypes,
        linked_archetypes,
    )

    try:
        suggestions = classify_archetypes(prompt, [a.name for a in archetypes])
        already_suggested = {s.archetype for s in suggestions}
        suggestions += [
            s
            for s in match_payoff_archetypes(card)
            if s.archetype not in already_suggested
        ]
        archetype_error = None
    except ArchetypeClassificationError as exc:
        archetype_error = str(exc)
        print(
            f"Archetypes: unavailable ({archetype_error}) — skipping LLM classification",
            file=sys.stderr,
        )
        suggestions = None

    print("Archetypes:")
    if suggestions is None:
        print("  (skipped)")
    elif suggestions:
        for suggestion in suggestions:
            print(f"  {suggestion.archetype}: {suggestion.reasoning}")
    else:
        print("  (none)")

    append_run(
        card_query=args.card,
        card=card,
        mechanics=mechanics,
        edhrec_signal=edhrec_signal,
        edhrec_error=edhrec_error,
        archetype_suggestions=suggestions,
        archetype_error=archetype_error,
    )


if __name__ == "__main__":
    main()
