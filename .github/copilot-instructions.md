# Interview Prep Studio Copilot Instructions

- Keep resume parsing, evidence matching, and answer scoring deterministic.
- Do not add external AI calls outside the optional Foundry IQ module.
- Never log or persist resume text, job descriptions, or interview answers.
- Store secrets only in `.streamlit/secrets.toml`, which is gitignored.
- Reuse data classes from `src/models.py`.
- Add focused pytest coverage for new domain behavior.
- Keep Streamlit pages thin; move testable logic into `src/`.
- Preserve the explicit consent step before any Foundry IQ request.
- Use fictional data in tests, screenshots, and demos.
