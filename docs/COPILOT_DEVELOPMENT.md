# GitHub Copilot Development Journal

The Creative Apps challenge requires meaningful GitHub Copilot usage. This
file records truthful evidence from work completed with GitHub Copilot in
VS Code or the Copilot CLI.

> Integrity note: do not claim that AI assistance from other tools was
> GitHub Copilot. Fill in the entries below only after you personally use
> Copilot. GitHub Copilot has a free tier (monthly completions and chat
> messages at no cost), so a short, genuine session is enough.

## How to complete this in ~5 minutes

1. Open this repository in **VS Code** with the **GitHub Copilot** extension
   signed in.
2. Run the two short tasks below in **Copilot Chat** (they are real, useful
   tasks on this codebase).
3. Take a screenshot of each Copilot Chat exchange and save them to
   `docs/screenshots/` as `copilot-chat.png` and `copilot-suggestion.png`.
4. Paste your real prompt and a short note on what you accepted or changed
   into each entry below, then check the boxes.

## Evidence Checklist

- [ ] Screenshot of Copilot Chat helping with a feature (`docs/screenshots/copilot-chat.png`)
- [ ] Screenshot of an accepted or modified code suggestion (`docs/screenshots/copilot-suggestion.png`)
- [ ] At least two real prompts recorded below
- [ ] Explanation of what was accepted, changed, or rejected
- [ ] Commit hash(es) for any work that used Copilot

---

## Entry 1 — Explain and index the history schema

**Date:** _<!-- FILL IN: YYYY-MM-DD -->_
**Feature:** Local progress history (`src/history_store.py`)
**Copilot surface:** VS Code Chat
**Model, if shown:** _<!-- FILL IN -->_

**Prompt used**

```text
Open src/history_store.py. Explain the mock_sessions table schema and
suggest an index that would speed up the "ORDER BY created_at DESC" query
in list_mock_sessions.
```

**How Copilot helped**

_<!-- FILL IN: summarize the explanation / suggestion Copilot gave -->_

**What I changed**

_<!-- FILL IN: what you accepted, modified, or rejected and why -->_

**Verification**

```
.venv/bin/python -m pytest -q
```

**Evidence**

- Screenshot: `docs/screenshots/copilot-chat.png`
- Commit: _<!-- FILL IN: short commit hash -->_

---

## Entry 2 — Harden Foundry IQ error handling

**Date:** _<!-- FILL IN: YYYY-MM-DD -->_
**Feature:** Foundry IQ client (`src/foundry_iq.py`)
**Copilot surface:** VS Code Chat / inline completion
**Model, if shown:** _<!-- FILL IN -->_

**Prompt used**

```text
In src/foundry_iq.py, what happens if the Foundry IQ endpoint returns a
non-JSON body or an empty response? Suggest a test in
tests/test_foundry_iq.py that covers that case.
```

**How Copilot helped**

_<!-- FILL IN: summarize the suggestion -->_

**What I changed**

_<!-- FILL IN: what you accepted, modified, or rejected and why -->_

**Verification**

```
.venv/bin/python -m pytest tests/test_foundry_iq.py -q
```

**Evidence**

- Screenshot: `docs/screenshots/copilot-suggestion.png`
- Commit: _<!-- FILL IN: short commit hash -->_

---

## Suggested follow-up Copilot tasks (optional)

Use Copilot for any of these if you want more evidence:

1. Reviewing keyboard accessibility on the Mock Interview page.
2. Improving empty-state wording on the Progress page.
3. Adding a docstring or type hint Copilot proposes for a helper function.

Record only what you actually do.
