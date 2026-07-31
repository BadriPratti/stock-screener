---
name: soft-search
description: Manually trigger the quick 100-stock test scan on GitHub Actions instead of waiting for the ~12pm ET scheduled run. Use when the user says "run soft search," "run easy search," "run the quick/test scan," or wants a fast sanity check that the pipeline works.
---

Trigger the midday quick-scan workflow on the user's fork and report back — do not run it locally unless the user specifically asks for a local run (e.g. to test unpushed local changes), since this cloud version is what actually emails the user.

IMPORTANT: always pass `--repo BadriPratti/stock-screener` explicitly on every `gh` call in this skill. The local `origin` remote is a fork of `RyanJHamby/stock-screener`, and `gh` auto-resolves to that upstream repo when no `--repo` is given — the user doesn't have workflow-trigger permissions there, so omitting `--repo` targets the wrong (inaccessible) repo.

1. Run `gh workflow run midday_quick_scan.yml --repo BadriPratti/stock-screener`.
2. Get the run: `gh run list --repo BadriPratti/stock-screener --workflow midday_quick_scan.yml --limit 1` to confirm it queued and grab the run ID/URL.
3. Report the run URL to the user.
4. Tell them: this scans 100 stocks, usually finishes in a few minutes, and they'll get an email when it's done.
5. Worth mentioning if relevant: this always scans the same static first-100 tickers (an alphabetical slice of the universe), not a rotating sample — it's more of a pipeline health check than a second independent signal source.
6. Do not poll repeatedly or sleep-loop waiting for it. If the user asks for status later, check with `gh run view <run-id> --repo BadriPratti/stock-screener`.
