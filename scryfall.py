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
    mana_value: float
    power: str | None
    toughness: str | None


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


def _extract_oracle_text(data: dict[str, Any]) -> str:
    """Return the card's oracle text. Double-faced cards have no top-level
    oracle_text — Scryfall splits it across card_faces instead."""
    oracle_text = data.get("oracle_text")
    if oracle_text:
        return oracle_text
    faces = data.get("card_faces", [])
    return "\n//\n".join(face.get("oracle_text", "") for face in faces)


def _extract_power_toughness(data: dict[str, Any]) -> tuple[str | None, str | None]:
    """Return the card's (power, toughness). Non-creatures have neither.
    Double-faced cards have no top-level power/toughness when faces differ —
    Scryfall splits it across card_faces instead; falls back to the front
    face, same pattern as _extract_oracle_text."""
    power = data.get("power")
    toughness = data.get("toughness")
    if power is not None or toughness is not None:
        return power, toughness
    faces = data.get("card_faces", [])
    if faces:
        return faces[0].get("power"), faces[0].get("toughness")
    return None, None


def fetch_card(name: str) -> Card:
    """Fetch a card's oracle text, type line, oracle tags, mana value, and
    power/toughness by exact name."""
    resp = _request_with_retry(SCRYFALL_NAMED, params={"exact": name})
    if resp.status_code == 404:
        raise CardNotFoundError(f"No card found matching {name!r}")
    resp.raise_for_status()
    data = resp.json()

    tag_index = _load_oracle_tag_index()
    power, toughness = _extract_power_toughness(data)
    return Card(
        name=data["name"],
        oracle_id=data["oracle_id"],
        type_line=data["type_line"],
        oracle_text=_extract_oracle_text(data),
        oracle_tags=tag_index.get(data["oracle_id"], []),
        mana_value=data["cmc"],
        power=power,
        toughness=toughness,
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


def build_tag_ancestors(
    tag_records: Iterable[dict[str, Any]],
) -> dict[str, set[str]]:
    """Build a tag slug -> set of all transitive ancestor slugs from Oracle Tags
    bulk-data records, using each record's parent_ids. Handles tags with multiple
    parent branches (e.g. reanimate-creature, whose parents span both the
    reanimate and recursion branches)."""
    records = list(tag_records)
    slug_by_id = {r["id"]: r["slug"] for r in records}
    parent_ids_by_id = {r["id"]: r.get("parent_ids", []) for r in records}

    cache: dict[str, set[str]] = {}

    def ancestors_of(tag_id: str) -> set[str]:
        if tag_id in cache:
            return cache[tag_id]
        cache[tag_id] = set()  # seed before recursing, guards against cycles
        result: set[str] = set()
        for parent_id in parent_ids_by_id.get(tag_id, []):
            parent_slug = slug_by_id.get(parent_id)
            if parent_slug is None:
                continue
            result.add(parent_slug)
            result |= ancestors_of(parent_id)
        cache[tag_id] = result
        return result

    return {slug: ancestors_of(tag_id) for tag_id, slug in slug_by_id.items()}


def _load_oracle_tag_records() -> list[dict[str, Any]]:
    _ensure_oracle_tag_cache()
    with ORACLE_TAG_CACHE_PATH.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def _load_oracle_tag_index() -> dict[str, list[str]]:
    return build_oracle_tag_index(_load_oracle_tag_records())


def load_tag_ancestors() -> dict[str, set[str]]:
    """Public: tag slug -> set of all ancestor tag slugs, for hierarchy-aware matching."""
    return build_tag_ancestors(_load_oracle_tag_records())


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
