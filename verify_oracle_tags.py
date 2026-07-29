"""
Verifies candidate Scryfall oracle tag slugs against the live search API.

For each candidate slug, queries `otag:<slug>` and records whether it
returns results (i.e. the tag exists and is populated) plus the hit count.
Scryfall asks API consumers to keep request rates modest (they recommend
50-100ms between requests) — this script sleeps between calls accordingly.

Run this yourself; it needs network access to api.scryfall.com which this
sandbox doesn't have.

Usage:
    pip install requests
    python verify_oracle_tags.py
"""

import csv
import random
import time

import requests

SCRYFALL_SEARCH = "https://api.scryfall.com/cards/search"
REQUEST_DELAY_SECONDS = 0.1
MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 1.0
BACKOFF_MAX_SECONDS = 30.0

# mechanic name -> list of candidate slugs to check, in priority order.
# Confirmed-correct slugs (from direct experience, not guessing) are marked.
CANDIDATES = {
    "Draw": ["draw"],  # confirmed — "card-draw" was wrong
    "Cantrip": ["cantrip"],
    "Impulsive Draw": ["impulsive-draw"],  # confirmed — "impulse-draw" was wrong
    "Removal": ["removal"],
    "Sweeper": ["sweeper"],  # confirmed — "board-wipe"/"boardwipe" were wrong
    "Discard": ["discard"],  # NOTE: "discard-outlet" is a real tag but its definition
    # ("ways to discard your own cards") matches our
    # Discard Outlet mechanic, not this one — see Discard
    # Outlet entry below. Don't map it here.
    "Ramp": ["ramp"],
    "Mana Dork": ["mana-dork"],  # confirmed correct
    "Counter": ["counterspell"],
    "Tutor": ["tutor"],
    "Bounce": ["bounce"],
    "Recursion": ["recursion"],
    "Reanimate": ["reanimate"],  # confirmed — plural family "reanimate-<type>" also
    # exists (e.g. reanimate-dragon); worth pulling the
    # full tag list to enumerate all reanimate-* tags
    # rather than guessing types one by one
    "Tokens": ["repeatable-token-generator"],  # confirmed as the most important one;
    # no single tag covers all token makers —
    # likely needs a union of several tags
    # plus text-pattern inference as a fallback
    "Looting": ["loot"],  # confirmed — "looting" was wrong
    "Rummage": ["rummage"],
    "Hand Disruption": ["hand-disruption"],  # confirmed
    "Card Advantage": ["card-advantage"],  # confirmed
    "Drain": ["drain-life"],  # confirmed — was "drain"
    "Graveyard Hate": [
        "hate-graveyard"
    ],  # confirmed — order flipped from "graveyard-hate"
    "Sac Outlet": ["sacrifice-outlet"],  # confirmed
    "Evasion": ["evasion"],  # confirmed
    "Self-mill": ["mill-self"],  # confirmed — order flipped from "self-mill"
    "Mill": ["mill-opponent"],  # confirmed — was just "mill"
    "+1/+1 Counters": [
        "pp-counters-matter",
        "gains-pp-counters",
        "gives-pp-counters",
    ],  # confirmed, 3 tags
    "Fixing": ["mana-fix"],  # confirmed — was "mana-fixing"
    "Energy": ["energy-generator"],  # confirmed — was "energy"
    "Burn": ["burn"],  # confirmed
    "Graveyard Matters": [
        "cards-in-graveyard-matter",
        "card-types-in-graveyard-matter",
    ],  # confirmed — replaces the narrower "Delirium" entry; no dedicated Delirium tag exists, these catch Delirium/Threshold/Undergrowth-style effects generally
    "Lifegain": ["lifegain"],  # confirmed
    "Pump": [
        "firebreathing",
        "power-boost-to-all",
        "shade-pump",
    ],  # confirmed, 3 tags —
    # firebreathing = +X/+0 until EOT, power-boost-to-all
    # = anthem-style boost to all creatures, shade-pump =
    # classic +X/+X until EOT. Likely not exhaustive —
    # revisit if more pump variants surface during spot-checking
    "Combat Trick": ["combat-trick"],
    "Cost Reduction": [
        "cost-reducer-self",
        "cost-reducer-sorcery",
        "cost-reducer-vehicle",
        "cost-reducer-saga",
    ],  # confirmed pattern "cost-reducer-<type>" — full type list still needs enumerating
    "Tax": ["tax"],  # confirmed — drop "cost-increaser"
    "Protection": [
        "protection",
        "gives-protection",
        "gives-hexproof",
        "gives-indestructible",
    ],  # confirmed, 4 tags
    "Copy": ["copy"],  # confirmed
    "Tap": ["tapper"],  # confirmed — was "tap-effect"
    "Stun": ["freeze-creature"],  # confirmed — completely different name than guessed
    "Discard Outlet": [
        "discard-outlet"
    ],  # confirmed — "ways to discard your own cards"
    "Unblockable": ["unblockable", "gives-unblockable"],  # confirmed, 2 tags
    "Curiosity": ["curiosity", "curiosity-like"],
    "Exchange": ["exchange-control"],  # confirmed — was "exchange"
    "Modal": ["modal"],  # confirmed
    "Landcycling": ["tutor-land"],  # confirmed by experience, but NOTE: this reads
    # broader than the Landcycling keyword specifically
    # (any land-tutoring effect, not just Landcycling) —
    # worth checking it doesn't overtag non-Landcycling cards
    "-1/-1 Counters": [
        "mm-counters-matter",
        "gains-mm-counters",
        "gives-mm-counters",
    ],  # confirmed, 3 tags
}


def check_tag(slug: str) -> dict:
    """Query otag:<slug> and return status + hit count, retrying on 429/5xx
    with exponential backoff (respecting Retry-After when present)."""
    attempt = 0
    while True:
        try:
            resp = requests.get(
                SCRYFALL_SEARCH,
                params={"q": f"otag:{slug}", "unique": "cards"},
                headers={
                    "User-Agent": "CubeWorkshopTaxonomyCheck/1.0",
                    "Accept": "*/*",
                },
                timeout=10,
            )
        except requests.RequestException as exc:
            if attempt >= MAX_RETRIES:
                return {"exists": None, "count": None, "error": str(exc)}
            _sleep_backoff(attempt)
            attempt += 1
            continue

        if resp.status_code == 200:
            data = resp.json()
            return {"exists": True, "count": data.get("total_cards", 0)}
        elif resp.status_code == 404:
            # Scryfall returns 404 with details when a search matches nothing
            return {"exists": False, "count": 0}
        elif resp.status_code == 429 or resp.status_code >= 500:
            if attempt >= MAX_RETRIES:
                return {"exists": None, "count": None, "http_status": resp.status_code}
            retry_after = resp.headers.get("Retry-After")
            if retry_after:
                try:
                    time.sleep(float(retry_after))
                except ValueError:
                    _sleep_backoff(attempt)
            else:
                _sleep_backoff(attempt)
            attempt += 1
            continue
        else:
            return {"exists": None, "count": None, "http_status": resp.status_code}


def _sleep_backoff(attempt: int) -> None:
    """Exponential backoff with jitter, capped at BACKOFF_MAX_SECONDS."""
    delay = min(BACKOFF_BASE_SECONDS * (2**attempt), BACKOFF_MAX_SECONDS)
    delay += random.uniform(0, delay * 0.25)
    time.sleep(delay)


def main():
    rows = []
    for mechanic, slugs in CANDIDATES.items():
        for slug in slugs:
            result = check_tag(slug)
            rows.append(
                {
                    "mechanic": mechanic,
                    "slug": slug,
                    "exists": result.get("exists"),
                    "count": result.get("count"),
                }
            )
            status = (
                "OK"
                if result.get("exists")
                else ("ERR" if result.get("exists") is None else "MISS")
            )
            print(
                f"[{status}] {mechanic:20s} otag:{slug:35s} count={result.get('count')}"
            )
            time.sleep(REQUEST_DELAY_SECONDS)

    with open("oracle_tag_verification.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["mechanic", "slug", "exists", "count"])
        writer.writeheader()
        writer.writerows(rows)

    print("\nWrote oracle_tag_verification.csv")


if __name__ == "__main__":
    main()
