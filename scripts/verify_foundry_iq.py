"""Verify a live Microsoft Foundry IQ connection using local secrets.

Reads ``.streamlit/secrets.toml`` (never committed), performs one real
retrieve call, and prints retrieval diagnostics. The API key is never
printed or logged: only the endpoint hostname, knowledge base name, elapsed
time, and citation count are shown.

Usage:
    python scripts/verify_foundry_iq.py ["custom coaching question"]
"""

from __future__ import annotations

import sys
from pathlib import Path

import toml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.foundry_iq import FoundryIQClient, FoundryIQError, settings_from_mapping

SECRETS_PATH = ROOT / ".streamlit" / "secrets.toml"
DEFAULT_QUESTION = (
    "How should a student structure a teamwork answer for a software "
    "engineering internship?"
)


def main() -> int:
    if not SECRETS_PATH.exists():
        print(f"No secrets file at {SECRETS_PATH}.")
        print("Copy .streamlit/secrets.toml.example and fill in your values.")
        return 1

    secrets = toml.loads(SECRETS_PATH.read_text(encoding="utf-8"))
    settings = settings_from_mapping(secrets.get("foundry_iq"))
    if settings is None:
        print("Foundry IQ secrets are missing or incomplete; cannot verify.")
        print("Required: search_endpoint, knowledge_base_name, api_key.")
        return 1

    question = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUESTION
    print("Connecting to Microsoft Foundry IQ (key not displayed)...")
    try:
        response = FoundryIQClient(settings).retrieve(question)
    except FoundryIQError as exc:
        print(f"FAILED: {exc}")
        return 1

    print("\nLive connection verified.")
    print(f"  Provider:       {response.provider}")
    print(f"  Endpoint host:  {response.endpoint_host}")
    print(f"  Knowledge base: {response.knowledge_base}")
    print(f"  Elapsed:        {response.elapsed_ms} ms")
    print(f"  Citations:      {response.citation_count}")
    for citation in response.citations:
        print(f"    [{citation.citation_id}] {citation.title} -> {citation.source}")
    print(f"\nAnswer preview:\n{response.answer[:400]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
