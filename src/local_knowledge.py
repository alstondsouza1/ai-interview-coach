"""Local citation-backed coaching fallback for offline demonstrations."""

from __future__ import annotations

import re
import time
from pathlib import Path

from src.models import GroundedCoachingResponse, KnowledgeCitation

KNOWLEDGE_ROOT = Path(__file__).resolve().parent.parent / "knowledge"


def retrieve_local_guidance(query: str, limit: int = 3) -> GroundedCoachingResponse:
    """Retrieve relevant passages from the bundled Markdown knowledge pack."""

    started = time.perf_counter()
    clean_query = " ".join(query.split())
    query_terms = _tokens(clean_query)
    documents = []
    for path in sorted(KNOWLEDGE_ROOT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        metadata, content = _parse_document(text)
        score = len(query_terms & _tokens(content + " " + metadata.get("title", "")))
        documents.append((score, path, metadata, content))

    ranked = sorted(documents, key=lambda item: item[0], reverse=True)
    selected = [item for item in ranked if item[0] > 0][:limit] or ranked[:limit]
    citations = []
    guidance = []
    for index, (_, path, metadata, content) in enumerate(selected, start=1):
        excerpt = _best_paragraph(content, query_terms)
        citations.append(
            KnowledgeCitation(
                citation_id=str(index),
                title=metadata.get("title", path.stem.replace("-", " ").title()),
                source=metadata.get("source", str(path.relative_to(KNOWLEDGE_ROOT.parent))),
                excerpt=excerpt,
            )
        )
        guidance.append(f"[{index}] {excerpt}")

    answer = (
        "Use these grounded preparation notes:\n\n"
        + "\n\n".join(guidance)
        + "\n\nApply the guidance only when it truthfully matches your own experience."
    )
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    return GroundedCoachingResponse(
        answer=answer,
        citations=citations,
        provider="Bundled local knowledge",
        query=clean_query,
        activity_summary=[f"Matched {len(citations)} local knowledge documents."],
        endpoint_host="",
        knowledge_base="knowledge/ (bundled Markdown pack)",
        elapsed_ms=elapsed_ms,
    )


def _parse_document(text: str) -> tuple[dict[str, str], str]:
    metadata: dict[str, str] = {}
    lines = text.splitlines()
    content_start = 0
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                content_start = index + 1
                break
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()
    return metadata, "\n".join(lines[content_start:]).strip()


def _best_paragraph(content: str, query_terms: set[str]) -> str:
    paragraphs = [
        " ".join(paragraph.split())
        for paragraph in re.split(r"\n\s*\n", content)
        if paragraph.strip() and not paragraph.lstrip().startswith("#")
    ]
    if not paragraphs:
        return "No excerpt available."
    return max(paragraphs, key=lambda paragraph: len(query_terms & _tokens(paragraph)))[:700]


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9+#.]{3,}", text.casefold())
        if token not in {"with", "that", "this", "from", "your", "into", "have"}
    }
