"""Optional Microsoft Foundry IQ retrieval integration."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

from src.models import GroundedCoachingResponse, KnowledgeCitation


class FoundryIQError(RuntimeError):
    """Raised when Foundry IQ cannot return a usable grounded response."""


@dataclass(frozen=True)
class FoundryIQSettings:
    """Configuration for an Azure AI Search knowledge base."""

    search_endpoint: str
    knowledge_base_name: str
    api_key: str
    api_version: str = "2026-05-01-preview"

    @property
    def configured(self) -> bool:
        hostname = (urlparse(self.search_endpoint).hostname or "").casefold()
        return all(
            (
                self.search_endpoint.startswith("https://"),
                hostname.endswith(".search.windows.net"),
                self.knowledge_base_name,
                self.api_key,
                "YOUR-" not in self.search_endpoint,
                not self.api_key.startswith("YOUR-"),
            )
        )


def settings_from_mapping(
    values: Mapping[str, Any] | None,
) -> FoundryIQSettings | None:
    """Build settings from Streamlit secrets or another mapping."""

    if not values:
        return None
    settings = FoundryIQSettings(
        search_endpoint=str(values.get("search_endpoint", "")).rstrip("/"),
        knowledge_base_name=str(values.get("knowledge_base_name", "")),
        api_key=str(values.get("api_key", "")),
        api_version=str(values.get("api_version", "2026-05-01-preview")),
    )
    return settings if settings.configured else None


class FoundryIQClient:
    """Call the Foundry IQ knowledge-base retrieve REST action."""

    def __init__(
        self,
        settings: FoundryIQSettings,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        if not settings.configured:
            raise ValueError("Complete Foundry IQ settings are required.")
        self.settings = settings
        self._opener = opener

    def retrieve(self, query: str) -> GroundedCoachingResponse:
        """Retrieve a synthesized, citation-backed coaching response."""

        clean_query = " ".join(query.split())
        if len(clean_query) < 10:
            raise ValueError("Ask a more specific coaching question.")
        if len(clean_query) > 2_000:
            raise ValueError("Keep the coaching question under 2,000 characters.")

        payload = {
            "messages": [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are a career coach for students and entry-level "
                                "software engineers. Use only retrieved knowledge. "
                                "Give practical guidance, cite supporting references, "
                                "and say when the sources do not establish an answer."
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [{"type": "text", "text": clean_query}],
                },
            ],
            "includeActivity": True,
            "maxOutputDocuments": 8,
            "maxOutputSize": 8_000,
            "retrievalReasoningEffort": {"kind": "low"},
        }
        started = time.perf_counter()
        response_data = self._post_json(payload)
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        answer = _extract_answer(response_data)
        citations = _extract_citations(response_data)
        activity = _extract_activity(response_data)
        if not answer:
            raise FoundryIQError("Foundry IQ returned no coaching content.")
        # Diagnostics only ever expose the endpoint hostname and knowledge base
        # name. The API key is never copied into the response or activity log.
        endpoint_host = urlparse(self.settings.search_endpoint).hostname or ""
        return GroundedCoachingResponse(
            answer=answer,
            citations=citations,
            provider="Microsoft Foundry IQ",
            query=clean_query,
            activity_summary=activity,
            endpoint_host=endpoint_host,
            knowledge_base=self.settings.knowledge_base_name,
            elapsed_ms=elapsed_ms,
        )

    def _post_json(self, payload: dict[str, Any]) -> dict[str, Any]:
        endpoint = (
            f"{self.settings.search_endpoint}/knowledgebases/"
            f"{quote(self.settings.knowledge_base_name, safe='')}/retrieve"
            f"?api-version={quote(self.settings.api_version, safe='')}"
        )
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "api-key": self.settings.api_key,
            },
            method="POST",
        )
        try:
            with self._opener(request, timeout=35) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")[:500]
            raise FoundryIQError(
                f"Foundry IQ returned HTTP {exc.code}: {details}"
            ) from exc
        except (URLError, TimeoutError) as exc:
            raise FoundryIQError(f"Could not reach Foundry IQ: {exc}") from exc
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise FoundryIQError("Foundry IQ returned an unreadable response.") from exc


def _extract_answer(data: dict[str, Any]) -> str:
    for message in data.get("response", []):
        for content in message.get("content", []):
            if content.get("type") == "text" and content.get("text"):
                return str(content["text"]).strip()
    return ""


def _extract_citations(data: dict[str, Any]) -> list[KnowledgeCitation]:
    citations = []
    for reference in data.get("references", []):
        source_data = reference.get("sourceData") or {}
        citation_id = str(reference.get("id", len(citations)))
        title = str(
            source_data.get("title")
            or reference.get("docKey")
            or f"Reference {citation_id}"
        )
        source = str(
            source_data.get("url")
            or source_data.get("source")
            or reference.get("knowledgeSourceName")
            or reference.get("type", "Foundry IQ knowledge source")
        )
        excerpt = str(source_data.get("content") or source_data.get("terms") or "")
        citations.append(
            KnowledgeCitation(
                citation_id=citation_id,
                title=title,
                source=source,
                excerpt=excerpt[:500],
            )
        )
    return citations


def _extract_activity(data: dict[str, Any]) -> list[str]:
    activity = []
    for item in data.get("activity", []):
        activity_type = str(item.get("type", "retrieval"))
        elapsed = item.get("elapsedMs")
        source = item.get("knowledgeSourceName")
        details = activity_type
        if source:
            details += f": {source}"
        if elapsed is not None:
            details += f" ({elapsed} ms)"
        activity.append(details)
    return activity
