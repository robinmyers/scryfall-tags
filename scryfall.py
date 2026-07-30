"""Scryfall client: fetch a single card's oracle text, type line, and oracle tags.

Oracle tags aren't part of the card object returned by the named-card
endpoint — they only exist in a separate "Oracle Tags" bulk data file,
keyed by tag rather than by card. This module downloads and caches that
file locally and builds an oracle_id -> [tag slugs] index from it.
"""

import gzip
import json
import random
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

SCRYFALL_NAMED = "https://api.scryfall.com/cards/named"
SCRYFALL_BULK_DATA = "https://api.scryfall.com/bulk-data"
USER_AGENT = "CubeClassificationPipeline/1.0"

MAX_RETRIES = 5
BACKOFF_BASE_SECONDS = 1.0
BACKOFF_MAX_SECONDS = 30.0

ORACLE_TAG_CACHE_PATH = Path(".cache/oracle-tags.jsonl")
ORACLE_TAG_CACHE_MAX_AGE_SECONDS = 24 * 60 * 60


class CardNotFoundError(Exception):
    """Raised when Scryfall has no card matching the given exact name."""


@dataclass
class Card:
    name: str
    oracle_id: str
    type_line: str
    oracle_text: str
    oracle_tags: list[str]


def _sleep_backoff(attempt: int) -> None:
    """Exponential backoff with jitter, capped at BACKOFF_MAX_SECONDS."""
    delay = min(BACKOFF_BASE_SECONDS * (2**attempt), BACKOFF_MAX_SECONDS)
    delay += random.uniform(0, delay * 0.25)
    time.sleep(delay)


def _request_with_retry(
    url: str, params: dict[str, str] | None = None
) -> requests.Response:
    """GET url, retrying on network errors/429/5xx with backoff-with-jitter."""
    attempt = 0
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    while True:
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=30)
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


def fetch_card(name: str) -> Card:
    """Fetch a card's oracle text, type line, and oracle tags by exact name."""
    resp = _request_with_retry(SCRYFALL_NAMED, params={"exact": name})
    if resp.status_code == 404:
        raise CardNotFoundError(f"No card found matching {name!r}")
    resp.raise_for_status()
    data = resp.json()

    tag_index = _load_oracle_tag_index()
    return Card(
        name=data["name"],
        oracle_id=data["oracle_id"],
        type_line=data["type_line"],
        oracle_text=data.get("oracle_text", ""),
        oracle_tags=tag_index.get(data["oracle_id"], []),
    )


def build_oracle_tag_index(
    tag_records: Iterable[dict[str, Any]],
) -> dict[str, list[str]]:
    """Build an oracle_id -> [tag slugs] index from Oracle Tags bulk-data records."""
    index: dict[str, list[str]] = {}
    for record in tag_records:
        slug = record["slug"]
        for tagging in record.get("taggings", []):
            index.setdefault(tagging["oracle_id"], []).append(slug)
    return index


def _load_oracle_tag_index() -> dict[str, list[str]]:
    _ensure_oracle_tag_cache()
    with ORACLE_TAG_CACHE_PATH.open(encoding="utf-8") as f:
        records = [json.loads(line) for line in f]
    return build_oracle_tag_index(records)


def _ensure_oracle_tag_cache() -> None:
    if ORACLE_TAG_CACHE_PATH.exists():
        age_seconds = time.time() - ORACLE_TAG_CACHE_PATH.stat().st_mtime
        if age_seconds < ORACLE_TAG_CACHE_MAX_AGE_SECONDS:
            return

    bulk_data_resp = _request_with_retry(SCRYFALL_BULK_DATA)
    bulk_data_resp.raise_for_status()
    entries = bulk_data_resp.json()["data"]
    oracle_tags_entry = next(e for e in entries if e["type"] == "oracle_tags")

    download_resp = _request_with_retry(oracle_tags_entry["jsonl_download_uri"])
    download_resp.raise_for_status()

    ORACLE_TAG_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ORACLE_TAG_CACHE_PATH.write_bytes(gzip.decompress(download_resp.content))
