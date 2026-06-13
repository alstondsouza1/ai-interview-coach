# Microsoft Foundry IQ Setup

This application supports the Foundry IQ knowledge-base retrieve API exposed
through Azure AI Search.

Official references:

- [Create a knowledge base](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-create-knowledge-base)
- [Query a knowledge base](https://learn.microsoft.com/azure/search/agentic-retrieval-how-to-retrieve)

## 1. Create the Azure AI Search resource

In Microsoft Foundry:

1. Open **Build → Knowledge**.
2. Create or connect an Azure AI Search resource.
3. Use the Free tier if it supports the required features; otherwise use Basic
   and monitor Azure for Students credit usage.

Suggested name:

```text
interview-prep-search
```

## 2. Create the knowledge base

Suggested knowledge base:

```text
interview-coaching-kb
```

Configure:

- Retrieval reasoning effort: `low`
- Output mode: answer synthesis
- Answer instructions: provide concise student interview guidance and cite
  every recommendation

## 3. Add the knowledge content

Upload the Markdown documents from [`knowledge/`](../knowledge/) to the data
source connected to the knowledge base. These files contain summarized,
attributed guidance and no personal resume data.

## 4. Configure local secrets

Copy the example:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Fill in:

```toml
[foundry_iq]
search_endpoint = "https://interview-prep-search.search.windows.net"
knowledge_base_name = "interview-coaching-kb"
api_version = "2026-05-01-preview"
api_key = "YOUR-AZURE-AI-SEARCH-ADMIN-KEY"
```

Never commit `.streamlit/secrets.toml`.

For a production deployment, replace the API key with Microsoft Entra
authentication and assign the app identity the Search Index Data Reader role.
The current API-key path is intended for the hackathon proof of concept.

## 5. Verify

First, confirm the live connection from the command line. This reads
`.streamlit/secrets.toml`, performs one real retrieve call, and prints
diagnostics (endpoint host, knowledge base, elapsed time, citation count).
The API key is never printed or logged:

```bash
python scripts/verify_foundry_iq.py
```

Then open **Grounded Coach**, enable Foundry IQ, accept the consent checkbox,
and ask:

```text
How should a student structure a teamwork answer for a software engineering internship?
```

Verify that:

- Provider is `Microsoft Foundry IQ`
- The answer contains grounded guidance
- Source citations are displayed
- Retrieval activity shows the endpoint host, knowledge base, elapsed time,
  and citation count

## Privacy Boundary

The app sends only the reviewed coaching question. It does not automatically
send the uploaded resume, job description, or interview answers to Foundry IQ.
