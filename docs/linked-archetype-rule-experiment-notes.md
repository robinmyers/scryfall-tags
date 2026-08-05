# Mechanic-Linked Archetype Rule — Notes

Working notes for a deterministic rule pass targeting archetype misses the LLM doesn't reliably catch even when the signal is already in the prompt. Started as a Tokens payoff rule (anthems/sac outlets), which failed real-data calibration (docs shows the check inline below); pivoted through a Ramp mana-value rule (also failed calibration) to this: operationalizing the taxonomy doc's own Mechanic→Archetype `Linked Archetype` column as a deterministic rule, since the Mechanics rule pass already computes the underlying mechanic matches. Not a permanent doc — findings here get folded into `production-integration-proposal.md`.

## Method

New `linked_archetypes.py`, `match_linked_archetypes(mechanics)`: for each of a card's already-matched Mechanics that appears in a curated `TRUSTED_LINKS` table, adds the linked Archetype(s) to the suggestion set (merging multiple contributing mechanics into one suggestion per archetype). Wired into `main.py` alongside the existing `payoff.py` stat-rule merge, deduped against the LLM's own suggestions.

**Calibration, checked against the full 32-card T021 sample before writing code**: the taxonomy doc links 14 mechanics to archetypes. Applying all 14 blindly nets 3 true positives against 5 false positives — worse than doing nothing. Broken down per link:
- Clean (0 false positives across all evidence): `Reanimate→Reanimator` (1/1), `Graveyard Matters→Graveyard` (1/1), `Sac Outlet→Aristocrats` (2/2), `Self-mill→Reanimator,Graveyard` (1/1)
- Mixed (1 TP, 1 FP each): `Recursion→Graveyard`, `Ramp→Ramp`
- Bad, excluded: `Discard Outlet→Reanimator` (0/4), `Looting→Reanimator` (0/3), `Tokens→Tokens` (0/1), `Burn→Burn` (0/1), `+1/+1 Counters→+1/+1 Counters` (0/1)

User chose to include the 2 mixed-evidence links alongside the 4 clean ones (6 total in `TRUSTED_LINKS`), accepting the predicted false-positive cost (Wrenn and Six, Manamorphose) in exchange for catching Rona's Ramp miss, which the clean-4-only scope would not.

No fresh baseline run was needed — `run_log.jsonl`'s latest entries already reflected the just-merged `main` state (nothing had run since the Reanimator/Sneak stat-rule PR merged), so the baseline was snapshotted directly from existing log data.

## Result: worked exactly as calibrated

- **All 3 calibration targets flipped to hits**: Bloodghast → Reanimator, Grist, the Hunger Tide → Reanimator, Rona, Herald of Invasion → Ramp.
- **Both predicted false positives materialized exactly as forecast**: Wrenn and Six gained Graveyard (via the Recursion link) and Manamorphose gained Ramp (via the Ramp link) — neither is a hand-tag hit, confirming the calibration pass's prediction precisely rather than just directionally.
- **Aggregate recall improved: 76% (58/76) → 79% (60/76)**, net +2. The rule pass itself contributed a clean +3 (the three calibration hits, no hits lost to the two false positives it added, since those only add extras rather than displace correct suggestions); the remaining -1 is ordinary LLM run-to-run noise between the two independent 32-card passes (confirmed by checking which other gained/lost archetypes aren't reachable via `TRUSTED_LINKS` at all).
- Extras rose 46 → 48, matching the two confirmed false positives.
- 14 of 31 scoreable cards were unchanged.

## Findings

### 1. Calibrating against real data before choosing scope produced a predictable, trustworthy result

This is the clearest case yet of the pattern established across all four experiments in this line: checking real evidence before committing to scope (rather than assuming a taxonomy-doc heuristic is reliable just because it's written down) both prevented shipping something net-negative (the blind full-table version) and made the actual outcome fully predictable — every calibration prediction (3 true positives, 2 false positives) came true exactly, nothing surprising showed up.

### 2. The "mixed evidence" links behaved exactly as their evidence suggested — no better, no worse

Choosing to include `Recursion→Graveyard` and `Ramp→Ramp` despite 50/50 calibration evidence was a real tradeoff, not a free win: it bought the Rona fix but cost exactly the two false positives predicted. Worth remembering if this pattern is extended to other mechanics in the future — mixed-evidence links are a genuine precision/recall tradeoff to make deliberately, not a "probably fine" assumption.

## Recommendation

Keep this rule pass — net positive on real data, with predictable behavior. If the false-positive rate on `Recursion`/`Ramp` becomes a bigger concern as more cards are run (only 2 examples of each currently informed the decision), consider narrowing `TRUSTED_LINKS` back down to the clean 4 — that's a one-line change, not a rearchitecture, since the trust distinction already lives in a single data structure rather than being scattered through logic.
