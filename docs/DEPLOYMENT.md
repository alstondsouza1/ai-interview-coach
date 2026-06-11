# Deployment Guide

## Streamlit Community Cloud

1. Push the repository to GitHub.
2. Open Streamlit Community Cloud.
3. Create an app from:

```text
Repository: alstondsouza1/ai-interview-coach
Branch: main
Main file: app.py
```

4. In the app's **Secrets** settings, add:

```toml
[foundry_iq]
search_endpoint = "https://interview-prep-search.search.windows.net"
knowledge_base_name = "interview-coaching-kb"
api_version = "2026-05-01-preview"
api_key = "YOUR-REAL-KEY"
```

Do not add `.streamlit/secrets.toml` to Git.

## Deployment Verification

Check every page:

- Main workspace loads fictional sample data
- Mock Interview starts and advances
- Grounded Coach returns Foundry IQ citations
- Progress creates a local aggregate record
- Judge Demo prepares the fictional workspace

Streamlit Community Cloud storage can be ephemeral. For a permanent production
history, replace local SQLite with an approved persistent database while
preserving the aggregate-only privacy model.

## Environment Limitations

- PDF files must contain extractable text.
- Foundry IQ requests need outbound access to Azure AI Search.
- The current Foundry authentication uses a secret API key.
- Production deployments should migrate to Microsoft Entra identity.
