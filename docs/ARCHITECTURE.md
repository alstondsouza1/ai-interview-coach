# Architecture

## Design Principle

Interview Prep Studio separates personal-data processing from optional cloud
knowledge retrieval.

```text
Personal inputs
  Resume + job description + practice answers
                 |
                 v
       Local deterministic modules
  parsing, matching, scoring, mock interview
                 |
       aggregate scores only
                 v
            Local SQLite

Reviewed coaching question
        + explicit consent
                 |
                 v
      Microsoft Foundry IQ retrieve API
                 |
                 v
       Grounded answer + citations
```

## Trust Controls

- Resume matches show their source evidence.
- Required and preferred qualifications are separated.
- Answer scores show every rubric component.
- Foundry IQ calls require explicit per-question consent.
- Resume and answer text are not persisted.
- SQLite stores aggregate progress only.
- The application has a cited local fallback for offline demos.

## Foundry IQ Integration

`src/foundry_iq.py` calls:

```text
POST /knowledgebases/{knowledge-base}/retrieve
     ?api-version=2026-05-01-preview
```

The request uses low retrieval reasoning effort and asks for activity data and
up to eight grounding documents. The response parser exposes the synthesized
answer, references, and a concise activity summary.
