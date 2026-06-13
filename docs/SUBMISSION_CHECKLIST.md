# Hackathon Submission Checklist

Microsoft Agents League Hackathon 2026 — **Creative Apps** track.

Legend: `[x]` done & verified · `[ ]` still required · **(you)** only the author
can complete this (screenshot, recording, account action, or form entry).

## Challenge Requirements

- [ ] Project linked to **Creative Apps** in the submission portal **(you)**
- [x] Foundry IQ resource created and connected — live verified via
      `scripts/verify_foundry_iq.py`
- [x] Knowledge base populated with attributed content — live retrieve returned
      grounded answer + citations
- [x] Live Grounded Coach response includes citations
- [ ] Real GitHub Copilot usage documented — fill `docs/COPILOT_DEVELOPMENT.md`
      Entry 1 & 2 after a genuine session **(you)**
- [ ] Copilot screenshots added without confidential information **(you)**

## Security

- [x] `.streamlit/secrets.toml` is not tracked (gitignored)
- [x] No API keys, tokens, passwords, or connection strings in Git history —
      scanned full history for the key and any committed secrets file: none
- [ ] GitHub push protection enabled (repo Settings → Code security) **(you)**
- [x] Sample data is fictional (`sample_data/`)
- [x] `python scripts/check_public_repo.py` passes

## Product Quality

- [x] `pytest -q` passes (39 tests)
- [x] All Streamlit pages open — app boots, `/_stcore/health` returns 200, all
      four pages import cleanly
- [ ] Mobile layout reviewed **(you)**
- [ ] Keyboard navigation reviewed **(you)**
- [x] Foundry fallback tested (unit tests cover missing secrets, bad key, error)
- [x] Progress history can be deleted (`delete_all_history` wired into Progress)

## Submission Assets

- [x] Public repository URL — https://github.com/alstondsouza1/ai-interview-coach
- [ ] Live deployment URL — deploy per `docs/DEPLOYMENT.md` **(you)**
- [ ] Three-minute demo video — record per `docs/DEMO_SCRIPT.md` **(you)**
- [ ] Architecture screenshot **(you)**
- [ ] Foundry IQ knowledge-base screenshot **(you)**
- [ ] Foundry citation screenshot **(you)**
- [ ] GitHub Copilot usage screenshots **(you)**
- [ ] Project description and challenge selection — paste
      `docs/PROJECT_DESCRIPTION.md` / `docs/INNOVATION_STUDIO_DESCRIPTION.md`
      into the form **(you)**

## What only you can do (everything technical is complete)

1. Take the 6 screenshots listed in `docs/screenshots/README.md`.
2. Run a real GitHub Copilot session and complete `docs/COPILOT_DEVELOPMENT.md`.
3. Deploy to Streamlit Community Cloud and add the secret in its dashboard.
4. Record the 3-minute demo video.
5. Enable GitHub push protection.
6. Paste the prepared descriptions into the submission portal and select the
   Creative Apps challenge.
