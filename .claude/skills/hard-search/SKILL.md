---
name: hard-search
description: Manually trigger the full market scan (3,800+ stocks, ~15-30 min) on GitHub Actions instead of waiting for the 7am ET scheduled run. Use when the user says "run hard search," "run the full scan/market scan," or wants to see the full scan working right now.
---

Trigger the full market scan workflow on the user's fork and report back — do not run it locally, this is the cloud version that emails the user when done.

IMPORTANT: always pass `--repo BadriPratti/stock-screener` explicitly on every `gh` call in this skill. The local `origin` remote is a fork of `RyanJHamby/stock-screener`, and `gh` auto-resolves to that upstream repo when no `--repo` is given — the user doesn't have workflow-trigger permissions there, so omitting `--repo` targets the wrong (inaccessible) repo.

1. Run `gh workflow run daily_screening_git_storage.yml --repo BadriPratti/stock-screener`.
2. Get the run: `gh run list --repo BadriPratti/stock-screener --workflow daily_screening_git_storage.yml --limit 1` to confirm it queued and grab the run ID/URL.
3. Report the run URL to the user.
4. Tell them: this is the full 3,800+ stock scan, takes 15-30 minutes, and they'll get an email with buy/sell signals and Robinhood trade links when it finishes.
5. Do not poll repeatedly or sleep-loop waiting for it. If the user asks for status later, check with `gh run view <run-id> --repo BadriPratti/stock-screener`.
