PLAN: SPRINT_PLAN_SECTOR.md (planned 2026-09-22; NOT approved; nothing built)

SEC-001..006 (data/cache/scanner layer)  | all PENDING - can start immediately, no file conflicts with anything in flight
SEC-007..010 (UI layer)                  | all PENDING - UNBLOCKED (market-reorg MR-006 is now DONE)
SEC-011 (final verification)             | PENDING (blocked by SEC-006, SEC-010)

Council: Codex + Antigravity both independent, converged on nearly everything (two-tier sector+category taxonomy
specifically to handle "Insurance" the way the user described it; fetch only for shown/tracked stocks, never the
full universe; separate offline backfill; additive-only API changes). One disagreement (per-ticker cache files
vs one consolidated registry) resolved in favor of per-ticker files, matching this repo's existing
data/fundamentals_cache/ convention (2,601 files already working at that scale today).
