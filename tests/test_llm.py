from types import SimpleNamespace

import anthropic
import httpx
import pytest

from llm import ArchetypeClassificationError, ArchetypeSuggestion, classify_archetypes

ARCHETYPE_NAMES = ["Burn", "Aggro", "Control"]


class FakeMessages:
    def __init__(self, response=None, exc=None):
        self._response = response
        self._exc = exc

    def parse(self, **kwargs):
        if self._exc is not None:
            raise self._exc
        return self._response


class FakeClient:
    def __init__(self, response=None, exc=None):
        self.messages = FakeMessages(response=response, exc=exc)


def _fake_response(stop_reason="end_turn", suggestions=None, stop_details=None):
    parsed_output = (
        SimpleNamespace(suggestions=suggestions) if suggestions is not None else None
    )
    return SimpleNamespace(
        stop_reason=stop_reason,
        stop_details=stop_details,
        parsed_output=parsed_output,
    )


def test_classify_archetypes_success(monkeypatch):
    suggestions = [
        SimpleNamespace(archetype="Burn", reasoning="Deals direct damage."),
    ]
    fake_client = FakeClient(response=_fake_response(suggestions=suggestions))
    monkeypatch.setattr("llm._client", lambda: fake_client)

    result = classify_archetypes("prompt text", ARCHETYPE_NAMES)

    assert result == [
        ArchetypeSuggestion(archetype="Burn", reasoning="Deals direct damage.")
    ]


def test_classify_archetypes_empty_suggestions(monkeypatch):
    fake_client = FakeClient(response=_fake_response(suggestions=[]))
    monkeypatch.setattr("llm._client", lambda: fake_client)

    result = classify_archetypes("prompt text", ARCHETYPE_NAMES)

    assert result == []


def test_classify_archetypes_refusal(monkeypatch):
    fake_client = FakeClient(
        response=_fake_response(
            stop_reason="refusal", stop_details={"category": "cyber"}
        )
    )
    monkeypatch.setattr("llm._client", lambda: fake_client)

    with pytest.raises(ArchetypeClassificationError, match="declined"):
        classify_archetypes("prompt text", ARCHETYPE_NAMES)


def test_classify_archetypes_truncated(monkeypatch):
    fake_client = FakeClient(response=_fake_response(stop_reason="max_tokens"))
    monkeypatch.setattr("llm._client", lambda: fake_client)

    with pytest.raises(ArchetypeClassificationError, match="truncated"):
        classify_archetypes("prompt text", ARCHETYPE_NAMES)


def test_classify_archetypes_rate_limit_error(monkeypatch):
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    response = httpx.Response(429, request=request)
    exc = anthropic.RateLimitError("rate limited", response=response, body=None)
    fake_client = FakeClient(exc=exc)
    monkeypatch.setattr("llm._client", lambda: fake_client)

    with pytest.raises(ArchetypeClassificationError, match="Rate limited"):
        classify_archetypes("prompt text", ARCHETYPE_NAMES)


def test_classify_archetypes_connection_error(monkeypatch):
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    exc = anthropic.APIConnectionError(request=request)
    fake_client = FakeClient(exc=exc)
    monkeypatch.setattr("llm._client", lambda: fake_client)

    with pytest.raises(ArchetypeClassificationError, match="Connection error"):
        classify_archetypes("prompt text", ARCHETYPE_NAMES)
