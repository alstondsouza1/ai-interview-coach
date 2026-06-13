"""Tests for Foundry IQ configuration, parsing, and local fallback."""

from __future__ import annotations

import json

import pytest

from src.foundry_iq import FoundryIQClient, FoundryIQError, settings_from_mapping
from src.local_knowledge import retrieve_local_guidance


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


class RawResponse:
    """A response whose body is arbitrary (possibly invalid) bytes."""

    def __init__(self, body: bytes) -> None:
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return self.body


def _configured_settings():
    return settings_from_mapping(
        {
            "search_endpoint": "https://example.search.windows.net",
            "knowledge_base_name": "interview-coaching-kb",
            "api_key": "secret-value",
        }
    )


def test_settings_reject_placeholders() -> None:
    assert (
        settings_from_mapping(
            {
                "search_endpoint": "https://YOUR-SEARCH-SERVICE.search.windows.net",
                "knowledge_base_name": "interview-coaching-kb",
                "api_key": "YOUR-KEY",
            }
        )
        is None
    )


def test_settings_reject_non_azure_search_endpoint() -> None:
    assert (
        settings_from_mapping(
            {
                "search_endpoint": "https://malicious.example.com",
                "knowledge_base_name": "interview-coaching-kb",
                "api_key": "secret-value",
            }
        )
        is None
    )


def test_client_parses_answer_references_and_activity() -> None:
    settings = settings_from_mapping(
        {
            "search_endpoint": "https://example.search.windows.net",
            "knowledge_base_name": "interview-coaching-kb",
            "api_key": "secret-value",
        }
    )
    captured = {}

    def opener(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            {
                "response": [
                    {
                        "role": "assistant",
                        "content": [{"type": "text", "text": "Use STAR [1]."}],
                    }
                ],
                "references": [
                    {
                        "id": "1",
                        "knowledgeSourceName": "career-guidance",
                        "sourceData": {
                            "title": "STAR Method",
                            "url": "https://example.com/star",
                            "content": "Use a specific example.",
                        },
                    }
                ],
                "activity": [
                    {
                        "type": "searchIndex",
                        "knowledgeSourceName": "career-guidance",
                        "elapsedMs": 24,
                    }
                ],
            }
        )

    response = FoundryIQClient(settings, opener=opener).retrieve(
        "How should I answer a teamwork question?"
    )

    assert response.answer == "Use STAR [1]."
    assert response.citations[0].title == "STAR Method"
    assert response.provider == "Microsoft Foundry IQ"
    assert "interview-coaching-kb/retrieve" in captured["url"]
    assert captured["payload"]["retrievalReasoningEffort"] == {"kind": "low"}


def test_client_rejects_short_query() -> None:
    settings = settings_from_mapping(
        {
            "search_endpoint": "https://example.search.windows.net",
            "knowledge_base_name": "kb",
            "api_key": "secret",
        }
    )
    with pytest.raises(ValueError, match="specific"):
        FoundryIQClient(settings).retrieve("help")


def test_client_raises_when_response_has_no_answer() -> None:
    settings = _configured_settings()

    def opener(request, timeout):
        return FakeResponse({"response": [], "references": []})

    with pytest.raises(FoundryIQError, match="no coaching content"):
        FoundryIQClient(settings, opener=opener).retrieve(
            "How should I prepare for a systems design interview?"
        )


def test_client_raises_on_unreadable_json() -> None:
    settings = _configured_settings()

    def opener(request, timeout):
        return RawResponse(b"<html>gateway error</html>")

    with pytest.raises(FoundryIQError, match="unreadable response"):
        FoundryIQClient(settings, opener=opener).retrieve(
            "How should I prepare for a behavioral interview?"
        )


def test_client_surfaces_transport_failure() -> None:
    settings = _configured_settings()

    def opener(request, timeout):
        raise TimeoutError("connection timed out")

    with pytest.raises(FoundryIQError, match="Could not reach Foundry IQ"):
        FoundryIQClient(settings, opener=opener).retrieve(
            "How should I prepare for a coding interview?"
        )


def test_local_knowledge_returns_citations() -> None:
    response = retrieve_local_guidance(
        "How should I structure a behavioral interview answer with STAR?"
    )

    assert response.provider == "Bundled local knowledge"
    assert response.citations
    assert "grounded preparation notes" in response.answer
