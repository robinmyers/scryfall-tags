"""EDHREC client: fetch a card's theme/synergy data as a best-effort weak signal.

EDHREC has no official API. Its per-card JSON is served as static,
pre-rendered files behind CloudFront — a missing card surfaces as a 403
"AccessDenied" rather than a 404.
"""

import random
import time
from dataclasses import dataclass
from typing import Any

import requests

EDHREC_CARD_URL = "https://json.edhrec.com/pages/cards/{slug}.json"
USER_AGENT = "CubeClassificationPipeline/1.0"

MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 1.0
BACKOFF_MAX_SECONDS = 30.0

CARDLIST_MAX_CARDS = 10


class EdhrecNotFoundError(Exception):
    """Raised when EDHREC has no page for the given card."""


@dataclass
class EdhrecCardList:
    header: str
    tag: str
    card_names: list[str]


@dataclass
class EdhrecSignal:
    similar_cards: list[str]
    cardlists: list[EdhrecCardList]


def _sleep_backoff(attempt: int) -> None:
    """Exponential backoff with jitter, capped at BACKOFF_MAX_SECONDS."""
    delay = min(BACKOFF_BASE_SECONDS * (2**attempt), BACKOFF_MAX_SECONDS)
    delay += random.uniform(0, delay * 0.25)
    time.sleep(delay)


def _request_with_retry(url: str) -> requests.Response:
    """GET url, retrying on network errors/429/5xx with backoff-with-jitter."""
    attempt = 0
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    while True:
        try:
            resp = requests.get(url, headers=headers, timeout=30)
        except requests.RequestException:
            if attempt >= MAX_RETRIES:
                raise
            _sleep_backoff(attempt)
            attempt += 1
            continue

        if resp.status_code == 429 or resp.status_code >= 500:
            if attempt >= MAX_RETRIES:
                return resp
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

        return resp


def format_card_slug(name: str) -> str:
    """Convert a card name to EDHREC's slug format."""
    slug = name.lower().replace(" ", "-")
    slug = slug.replace("'", "").replace(",", "")
    return slug


def _parse_edhrec_response(data: dict[str, Any]) -> EdhrecSignal:
    similar_cards = list(data.get("similar", []))

    cardlists = []
    for entry in data.get("container", {}).get("json_dict", {}).get("cardlists", []):
        card_names = [
            cardview["name"]
            for cardview in entry.get("cardviews", [])[:CARDLIST_MAX_CARDS]
        ]
        cardlists.append(
            EdhrecCardList(
                header=entry["header"], tag=entry["tag"], card_names=card_names
            )
        )

    return EdhrecSignal(similar_cards=similar_cards, cardlists=cardlists)


def fetch_edhrec_signal(name: str) -> EdhrecSignal:
    """Fetch a card's EDHREC theme/synergy data by name."""
    slug = format_card_slug(name)
    url = EDHREC_CARD_URL.format(slug=slug)
    resp = _request_with_retry(url)
    if resp.status_code in (403, 404):
        raise EdhrecNotFoundError(f"No EDHREC page found for {name!r}")
    resp.raise_for_status()
    return _parse_edhrec_response(resp.json())
