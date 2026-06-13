# Deployment Guide

## Streamlit Community Cloud (recommended for submission)

### 1. Push the repository to GitHub

```bash
git push
```

Confirm `main` is up to date and `.streamlit/secrets.toml` is **not** tracked.

### 2. Create the app

1. Sign in at https://share.streamlit.io with your GitHub account.
2. Select **Create app → Deploy a public app from GitHub**.
3. Configure:

   ```text
   Repository: alstondsouza1/ai-interview-coach
   Branch:     main
   Main file:  app.py
   ```

### 3. Add secrets in the dashboard (never in Git)

In the app's **Settings → Secrets**, paste:

```toml
[foundry_iq]
search_endpoint = "https://interview-prep-studio-srch.search.windows.net"
knowledge_base_name = "interview-coaching-kb"
api_version = "2026-05-01-preview"
api_key = "YOUR-REAL-KEY"
```

> Paste the real key **only** into the Streamlit dashboard. Do not commit it and
> do not put it in any tracked file. The local `.streamlit/secrets.toml` stays on
> your machine only.

### 4. Deploy and capture the URL

After the first build completes, copy the public URL (e.g.
`https://<app-name>.streamlit.app`) and add it to:

- `README.md` (Live demo)
- `docs/PROJECT_DESCRIPTION.md`
- `docs/INNOVATION_STUDIO_DESCRIPTION.md`
- The submission portal

## Deployment verification

Check every page on the deployed app:

- Main workspace loads the fictional sample data
- Mock Interview starts and advances through questions
- Grounded Coach returns Foundry IQ citations with the live banner
- Progress creates a local aggregate record
- Judge Demo prepares the fictional workspace

If Foundry IQ is misconfigured on the host, Grounded Coach falls back to the
bundled cited knowledge pack — re-check the dashboard secret if you do not see
the "Live retrieval from Microsoft Foundry IQ" banner.

## Notes & limitations

- Streamlit Community Cloud storage is **ephemeral**: the SQLite progress history
  may reset between restarts. This is acceptable for the demo and preserves the
  aggregate-only privacy model.
- PDF resumes must contain extractable text (no OCR).
- Foundry IQ requests need outbound access to Azure AI Search.
- The current Foundry authentication uses an API key. For production, migrate to
  Microsoft Entra identity and assign the app the Search Index Data Reader role.
