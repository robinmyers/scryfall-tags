# Payoff-Only Archetype Membership: Deterministic Stat Rule — Notes

Working notes for `production-integration-proposal.md`'s payoff-only archetype membership limitation. Two prior prompt-instruction attempts (`docs/stats-prompt-experiment-notes.md`, `docs/payoff-prompt-experiment-notes.md`) both failed — the LLM didn't reliably act on stats-based hints even when explicitly instructed. This experiment tries a different mechanism: a deterministic rule pass, mirroring `mechanics.py`, rather than a third prompt-engineering attempt. Not a permanent doc — findings here get folded into `production-integration-proposal.md`.

## Method

New `payoff.py`, `match_payoff_archetypes(card)`: returns Reanimator + Sneak suggestions when `mana_value >= 6.0` **and** (`power >= 5` or `toughness >= 5`, both required to parse as numbers) — scoped to just these two archetypes since their taxonomy-doc qualifying signals are literally "big creature" (Reanimator: "big graveyard targets"; Sneak: "cheats big creatures into play"), unlike other Mechanic-Anchored payoff patterns which are effect-based, not size-based. Wired into `main.py`: merged into the LLM's own suggestion list after a successful `classify_archetypes()` call, deduped by archetype name so a card the LLM already caught doesn't get a duplicate entry.

Threshold calibrated against the real 32-card T021 sample's logged stats before writing any code: fires on exactly 2 cards — Atraxa, Grand Unifier (mv=7, 7/7, hand-tagged Reanimator+Sneak) and Dragonlord Atarka (mv=7, 8/8, no archetype hand-tag at all) — zero false positives in-sample, and confirmed the joint mana-value+stat condition matters (Moonshadow, mv=1 but 7/7 stats from a counters mechanic, would be a false positive on power/toughness alone).

Baseline note: unlike the prior two experiments, no valid "before" data was already sitting in `run_log.jsonl` (the most recent entries reflected the now-reverted payoff instruction) — had to freshly re-run the 32-card sample under current `main` to get a valid baseline. First attempt at this was accidentally contaminated (the rule pass's code landed in the working tree partway through the background baseline run, since the run executes the live file each iteration rather than a frozen snapshot) — caught it because Atraxa's "baseline" entry already showed the rule pass's telltale reasoning text, redid the baseline cleanly by stashing the implementation, re-running, then restoring it.

## Result: it worked

- **Atraxa, Grand Unifier now correctly gets both Reanimator and Sneak** — the exact case all three experiments in this line have targeted, confirmed via the rule pass's own reasoning text in the log ("Mana value 7.0 and power/toughness 7/7 clear the stat threshold... stat-based payoff heuristic").
- **Reanimator/Sneak recall: 20% (1/5) before → 60% (3/5) after** — both new hits are Atraxa's, both directly attributable to the rule pass (verified by reasoning-text provenance, not just presence/absence).
- **Aggregate recall improved too: 74% (56/76) → 76% (58/76)** — the first of the three payoff-fix attempts to move aggregate recall in the right direction rather than regress it.
- **Dragonlord Atarka** (no archetype hand-tag in the source data, so untestable) also got flagged Reanimator + Sneak by the rule — plausible given it's a comparably huge dragon, can't be scored but not a red flag either.
- Extras rose slightly (42 → 46) — checked each one's reasoning text and confirmed all are ordinary LLM run-to-run noise unrelated to the rule pass (e.g. Kitsa, Otterball Elite gained a spurious Reanimator suggestion from the LLM itself, with mana_value 2.0 — nowhere near the rule's threshold, and its own free-text reasoning, not the canned heuristic string). Same single-run-per-condition caveat as all three prior experiments: some of the 14 other per-card diffs in this run are plain sampling noise between two independent 32-card passes, not effects of this change — confirmed none of them touch Reanimator/Sneak.
- 17 of 31 scoreable cards were unchanged.

## Findings

### 1. Removing the LLM from the loop for this specific narrow judgment worked where asking it twice did not

The core hypothesis behind switching mechanisms was that the LLM's demonstrated unreliability at doing numeric reasoning on its own (both prior experiments) wasn't fixable by asking more clearly — and that held up. A deterministic check reliably catches exactly the case it was built for, with the same architecture pattern (`mechanics.py`-style rule pass) already proven out for Mechanics suggestions.

### 2. The fix is narrow by design, and that's fine

Only 2 of 32 cards clear the threshold. This doesn't touch Bloodghast, Grist, or other Reanimator misses whose membership comes from their own graveyard text rather than size (confirmed not fixable by this mechanism going in, per the earlier stat-distribution check). It's a small, precise fix for a small, precise problem — not a general Reanimator/Sneak recall improvement.

## Recommendation

Keep this rule pass — it's the first of three payoff-fix attempts to actually work, confirmed with clean attribution (not just correlation) via the reasoning-text check. Update `production-integration-proposal.md`'s known-limitation bullet to reflect that payoff-only membership for size-qualified archetypes (Reanimator/Sneak) is now handled, while the broader payoff-recognition gap for non-size-based Mechanic-Anchored archetypes (Ramp/Tokens/+1+1 Counters/Burn/Blink) remains open — those were explicitly out of scope here and would need a different, effect-based mechanism if pursued.
