# Interview Prep Studio — Final Project Description

> Paste this into the submission form's long-description field. Every claim here
> is true of the current repository; do not add unverified statements.

## One-line summary

Interview Prep Studio turns a resume and job description into an explainable,
private interview-preparation workspace, with optional citation-backed coaching
grounded in a Microsoft Foundry IQ knowledge base.

## The problem

Students and early-career engineers get generic interview advice and opaque
"match scores" they cannot question. They rarely know *why* a tool says they are
a 72% fit, *which* resume line earned a skill match, or *where* a piece of advice
came from. That erodes trust exactly when a candidate needs confidence.

## The solution

Interview Prep Studio is a local-first Streamlit application built around one
principle: **every recommendation is traceable to its source.**

- **Evidence-backed role fit** — separates required vs. preferred qualifications
  and links every matched skill to the exact resume excerpt that produced it.
- **Resume Lab** — transparent readiness score from visible writing signals
  (sections, quantified bullets, action verbs) with prioritized edits.
- **Practice Room & timed Mock Interview** — a balanced 10-question interview
  (4 technical / 3 behavioral / 3 situational), one question at a time, with a
  countdown and a fully visible scoring rubric.
- **Grounded Coach** — connects to a **Microsoft Foundry IQ** knowledge base
  through Azure AI Search and returns cited guidance, showing the citation trail
  and retrieval activity (endpoint host, knowledge base, elapsed time, citation
  count). It falls back to a bundled cited knowledge pack when offline.
- **Progress analytics** — stores aggregate scores only in local SQLite, with a
  one-click delete-all-history privacy control.

## How it uses Microsoft Foundry IQ

The Grounded Coach calls the Foundry IQ knowledge-base retrieve API:

```text
POST /knowledgebases/interview-coaching-kb/retrieve?api-version=2026-05-01-preview
```

against the `interview-prep-studio-srch` Azure AI Search resource. It requests
answer synthesis with low retrieval reasoning effort and activity data, then
renders the synthesized answer alongside its references. A live connection is
verifiable with `python scripts/verify_foundry_iq.py`, which prints diagnostics
without ever displaying the API key.

## Privacy by design

- Resume parsing, skill matching, and answer scoring are deterministic and run
  entirely locally — no cloud call and no hidden model decides the score.
- SQLite stores aggregate metrics only; resume, job, and answer text are never
  persisted.
- Foundry IQ is opt-in and consent-gated per request, and receives only the
  reviewed coaching question — never the resume or answers.
- Secrets live in gitignored Streamlit secrets; a credential scanner
  (`scripts/check_public_repo.py`) guards the public repo.

## What makes it different

It is an "explainable by construction" coach: the audit trail (skill → resume
evidence, score → rubric component, advice → citation) is the product, not an
afterthought. The Microsoft intelligence layer is added *with* a privacy
boundary rather than at the cost of one.

## Tech stack

Python · Streamlit · Microsoft Foundry IQ (Azure AI Search knowledge-base
retrieve API) · SQLite · standard-library `urllib` (no heavy SDKs) · pytest
(39 tests) · built with GitHub Copilot (see `docs/COPILOT_DEVELOPMENT.md`).

## Links

- Repository: https://github.com/alstondsouza1/ai-interview-coach
- Live deployment: _<!-- FILL IN after Streamlit Cloud deploy -->_
- Demo video: _<!-- FILL IN -->_
