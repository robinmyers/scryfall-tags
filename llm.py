"""LLM archetype-classification client: send the assembled archetype prompt to
Claude and parse the response into suggested Archetypes.

Uses structured outputs (client.messages.parse) rather than free text or
manual JSON parsing, so a successful response is guaranteed schema-valid.
The archetype name is constrained by a Literal type built at call time from
the caller-supplied archetype_names (sourced from taxonomy.parse_archetypes())
rather than hardcoded here, so the LLM cannot suggest an archetype outside the
taxonomy doc's list.
"""

from dataclasses import dataclass
from typing import Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, create_model

load_dotenv()

MODEL = "claude-sonnet-5"
MAX_TOKENS = 4096

SYSTEM_PROMPT = (
    "You are classifying a Magic: The Gathering card into archetypes for a "
    "curated cube, using the oracle text, rule-pass mechanic tags, EDHREC "
    "synergy signal, candidate archetype list, and mechanic-archetype "
    "heuristics provided below. Select every archetype from the candidate "
    "list that meaningfully applies to this card — zero archetypes is a "
    "valid answer for a card that doesn't fit any of them, and more than "
    "one is fine too. Only choose archetypes from the candidate list; never "
    "invent one. For each suggested archetype, give a one-sentence "
    "reasoning grounded in the provided context."
)


class ArchetypeClassificationError(Exception):
    """Raised when the LLM archetype-classification call fails or is refused."""


@dataclass
class ArchetypeSuggestion:
    archetype: str
    reasoning: str


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


def _build_response_model(archetype_names: list[str]) -> type[BaseModel]:
    name_type = Literal[tuple(archetype_names)]  # type: ignore[valid-type]
    suggestion = create_model(
        "ArchetypeSuggestion", archetype=(name_type, ...), reasoning=(str, ...)
    )
    return create_model(
        "ArchetypeSuggestions",
        suggestions=(list[suggestion], ...),  # type: ignore[valid-type]
    )


def classify_archetypes(
    prompt: str, archetype_names: list[str]
) -> list[ArchetypeSuggestion]:
    """Call the LLM with the assembled archetype prompt and parse suggested
    Archetypes from the response. Raises ArchetypeClassificationError on
    refusal, truncation, or API failure."""
    response_model = _build_response_model(archetype_names)

    try:
        response = _client().messages.parse(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            output_format=response_model,
        )
    except anthropic.RateLimitError as exc:
        raise ArchetypeClassificationError(f"Rate limited: {exc}") from exc
    except anthropic.APIConnectionError as exc:
        raise ArchetypeClassificationError(f"Connection error: {exc}") from exc
    except anthropic.APIStatusError as exc:
        raise ArchetypeClassificationError(f"API error: {exc}") from exc

    if response.stop_reason == "refusal":
        raise ArchetypeClassificationError(
            f"LLM declined to classify this card (stop_details: {response.stop_details})"
        )
    if response.stop_reason == "max_tokens":
        raise ArchetypeClassificationError(
            "LLM response was truncated at max_tokens before completing"
        )

    parsed = response.parsed_output
    if parsed is None:
        raise ArchetypeClassificationError(
            f"LLM response did not contain a parseable result (stop_reason: "
            f"{response.stop_reason})"
        )

    return [
        ArchetypeSuggestion(archetype=s.archetype, reasoning=s.reasoning)
        for s in parsed.suggestions  # type: ignore[attr-defined]
    ]
