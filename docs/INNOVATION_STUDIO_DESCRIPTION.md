# Innovation Studio Submission Copy

> Field-by-field copy for the Innovation Studio submission portal. Keep entries
> short; paste each block into its matching field. Placeholders marked
> `<!-- FILL IN -->` require an action only you can complete.

## Project name

Interview Prep Studio

## Challenge / category

Creative Apps

## Tagline (≤ 100 characters)

Explainable, private interview prep with citation-backed Foundry IQ coaching.

## Elevator pitch (2–3 sentences)

Interview Prep Studio turns a resume and job description into a private,
explainable interview-preparation workspace where every skill match, score, and
piece of advice is traceable to its source. Its Grounded Coach uses a Microsoft
Foundry IQ knowledge base to deliver cited guidance, with an explicit per-request
consent boundary so personal data stays local.

## Problem statement

Early-career candidates receive generic advice and opaque match percentages they
cannot interrogate — they can't see which resume line earned a match or where a
recommendation came from, which undermines trust when it matters most.

## What it does (bulleted)

- Evidence-backed role fit: required vs. preferred skills, each match linked to a
  resume excerpt.
- Transparent resume scoring and prioritized edits.
- Timed 10-question mock interview with a visible rubric and readiness trends.
- Grounded Coach: cited coaching from a Foundry IQ knowledge base, with a
  citation trail and retrieval-activity panel; cited local fallback when offline.
- Aggregate-only local progress history with one-click delete.

## How we used Microsoft Foundry IQ

Grounded Coach calls the Foundry IQ knowledge-base retrieve API
(`POST /knowledgebases/interview-coaching-kb/retrieve?api-version=2026-05-01-preview`)
on an Azure AI Search resource, requesting answer synthesis plus activity data,
and renders the synthesized answer with its references. Live connectivity is
verifiable via `scripts/verify_foundry_iq.py`.

## How we used GitHub Copilot

<!-- FILL IN: 2–3 true sentences after completing docs/COPILOT_DEVELOPMENT.md.
     Do not claim Copilot did work it did not. -->

## What makes it innovative

Explainability is built into the architecture: the audit trail (skill → evidence,
score → rubric, advice → citation) is the core feature, and the Microsoft
intelligence layer is integrated behind an explicit privacy boundary rather than
at its expense.

## Tech stack

Python, Streamlit, Microsoft Foundry IQ (Azure AI Search knowledge-base retrieve
API), SQLite, pytest (39 tests), GitHub Copilot.

## Links

- Public repository: https://github.com/alstondsouza1/ai-interview-coach
- Live demo URL: <!-- FILL IN after Streamlit Cloud deploy -->
- Demo video (≤ 3 min): <!-- FILL IN -->
- Screenshots: see `docs/screenshots/`

## Team

<!-- FILL IN: name(s) / role(s) -->
