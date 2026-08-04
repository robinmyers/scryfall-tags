# Payoff-Only Archetype Membership Prompt Experiment — Notes

Working notes for `production-integration-proposal.md`'s "Known limitations to carry forward" bullet on payoff-only archetype membership: cards like Atraxa, Grand Unifier that qualify for an archetype purely as a payoff for what *other* cards do to them (big reanimation targets, Sneak Attack payoffs), with zero textual self-signal. T021's finding 6 proposed the fix directly: "explicitly telling the LLM to consider whether a card is a plausible payoff... even without direct textual signal, keyed off high mana value / strong stats." Not a permanent doc — findings here get folded into `production-integration-proposal.md`.

## Method

Added one sentence to `llm.py`'s `SYSTEM_PROMPT`: for Mechanic-Anchored and Synergy Package archetypes, a card can qualify purely as a payoff based on mana value/power/toughness (now in the prompt since the prior stats experiment) even with no textual signal for the archetype's core mechanic, pointing at the qualifying-signals language already in the Candidate Archetypes section (e.g. Reanimator's "big graveyard targets," Sneak's cheat-into-play definition).

Before the change, checked which cards in the 32-card T021 sample currently miss a payoff-relevant archetype (Ramp, Tokens, +1/+1 Counters, Burn, Blink, Reanimator, Sneak) under the current (post-stats-fix) pipeline: **Bloodghast (Reanimator), Grist, the Hunger Tide (Reanimator), Atraxa, Grand Unifier (Reanimator + Sneak), Rona, Herald of Invasion (Ramp)** — 5 miss instances across 4 cards. Atraxa is the clean test case the finding was based on (mana_value 7.0, power/toughness 7/7); Bloodghast/Grist are cheap creatures (mana_value 2.0/3.0) where the "high mana value" framing may not even apply — flagged as a caveat going in, not assumed to be fixable by this change.

Snapshotted the pre-fix baseline (latest EDHREC-on suggestion per card, already in `run_log.jsonl` from the stats-prompt experiment) before touching code, then re-ran all 32 cards once with the new instruction and diffed against that snapshot — same methodology as the prior two experiments.

**Caveat**: single run per condition, same LLM non-determinism caveat as both prior experiments.

## Result: none of the 4 targeted misses were fixed, and aggregate recall regressed again

- **All 5 targeted miss instances remained misses.** Atraxa still missed both Reanimator and Sneak — the exact case the fix was built around. Bloodghast, Grist, and Rona also stayed missed.
- **Payoff-relevant-archetype recall was flat: 3/8 before, 3/8 after.** But extras within that same category rose from 11 to 15 — the instruction made the model more willing to guess Reanimator/Sneak-type archetypes in general (Kitsa, Otterball Elite and Duelist of the Mind both newly gained Reanimator), just not correctly on the cards it was actually meant to help.
- **Aggregate recall across all archetypes declined again: 72% (55/76) before → 70% (53/76) after**, from 4 lost hits (Marionette Apprentice/Artifacts, Kitsa/Tempo, Rona/Control, Duelist of the Mind/Spellslinger) partially offset by 2 gained hits (Kavaron Harrier/Artifacts, Firebolt/Graveyard) unrelated to payoff reasoning.
- 17 of 31 scoreable cards were unchanged.

## Findings

### 1. The instruction didn't move the targeted cards at all

Zero of 5 targeted miss instances flipped. Atraxa's reasoning (not shown in full here, but checked directly in `run_log.jsonl`) still classified purely off its own oracle text, ignoring the new payoff-consideration guidance even with mana value/power/toughness both present in-context and the instruction pointing directly at Reanimator/Sneak's qualifying signals. This suggests the gap isn't primarily an information-availability or even instruction-clarity problem — the model may need either much stronger/more directive language, a worked example, or this kind of "could this card be a payoff for X" reasoning may just not be reliable to elicit via a system-prompt instruction added on top of an already-large prompt.

### 2. A cross-experiment pattern is emerging: added instructions increase noise in their own target category without fixing the target

This is the **second consecutive prompt-engineering experiment** (after `docs/stats-prompt-experiment-notes.md`) that shows the same shape: the specific metric the change targeted stayed flat, extras/noise rose specifically within the targeted category, and aggregate recall took a small hit from unrelated collateral changes elsewhere in the card's suggestion set. Two data points isn't proof of a general rule, but it's consistent enough to be worth naming: incrementally layering more instructions onto this system prompt may have diminishing or even net-negative returns, rather than being a reliably additive way to close specific gaps.

## Recommendation

Don't keep iterating on system-prompt instructions as the default lever for this kind of gap — two attempts (stats framing, payoff framing) both failed to move their target metric while adding collateral noise. Reasonable next steps, not mutually exclusive:

- **Treat payoff-only membership as a genuine, currently-unsolved limitation** rather than something a prompt tweak resolves — keep the known-limitation framing in `production-integration-proposal.md`, now backed by a real negative result instead of an untested hypothesis.
- **If revisited, use a stronger elicitation mechanism than a system-prompt sentence** — e.g. a worked few-shot example directly in the prompt (show Atraxa's oracle text + stats and the correct Reanimator/Sneak reasoning as a demonstration), or a structured two-pass approach (first classify off text alone, then a second pass specifically asking "which of these unselected archetypes could this card be a payoff for, based on cost/stats?").
- **Consider reverting this specific instruction** given it added noise (extras 11→15 in the targeted category) without any offsetting benefit — it's not clearly net-positive to keep as-is.
