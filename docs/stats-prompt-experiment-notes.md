# Stats-in-Archetype-Prompt Experiment — Notes

Working notes for `production-integration-proposal.md`'s top priority fix: *"add mana value (and power/toughness for creatures) to the Oracle Text section of the prompt"*, motivated by T021's finding that 61% of archetype misses (11 of 18) were Strategy Shape archetypes (Control, Aggro, Combo, Midrange, Tempo) — archetypes the taxonomy doc says are "usually inferred from a card's overall stats/speed, not one signal," but which the prompt had no stats signal for at all. Not a permanent doc — findings here get folded into `production-integration-proposal.md`.

## Method

Added `mana_value: float`, `power: str | None`, `toughness: str | None` to `scryfall.Card` (`_extract_power_toughness()` mirrors the existing DFC-fallback pattern `_extract_oracle_text()` uses). `archetype._oracle_text_section()` now includes a `Mana Value: X` line always, and a `Power/Toughness: X/Y` line when the card is a creature.

Compared against a frozen pre-fix baseline: the latest EDHREC-on suggestions per card already logged in `run_log.jsonl` from the EDHREC ablation run (same 32 T021 cards, same current pipeline, just missing the stats lines) — snapshotted before any code change so the "before" side can't drift. Re-ran all 32 cards once with the stats-augmented prompt (default pipeline, EDHREC on) and diffed against that snapshot, scoring both aggregate recall and a Strategy-Shape-only breakdown against the same hand-tag ground truth used throughout (T021's table).

**Caveat**: one run per condition (same caveat as the EDHREC ablation) — the LLM call isn't deterministic, so part of any diff is ordinary sampling noise, not necessarily the stats fix's effect. With only 39 Strategy Shape hand-tag instances in the sample, a 1-2 instance swing either direction is within plausible noise.

## Result: the fix did not measurably improve Strategy Shape recall

- **Strategy Shape recall: 28/39 before, 28/39 after — zero net change.** Three suggestions were gained that fall in the Strategy Shape category (Dauthi Voidwalker → Tempo, Wight of the Reliquary → Midrange, Moonshadow → Aggro) and zero were lost — but **none of the three gains matched a hand-tag**. All three are extras, not hits. Strategy Shape extras went from 14 to 17.
- **Aggregate recall across all archetypes actually declined slightly: 75% (57/76) before → 72% (55/76) after.** Two real hand-tag hits were lost, both *outside* Strategy Shape: Firebolt lost its Graveyard hit, and Kavaron Harrier lost its Artifacts hit (the one suggestion the EDHREC ablation had found explicitly attributable to the EDHREC signal — see `docs/edhrec-ablation-notes.md` — apparently reshuffled out once stats were added to the same prompt).
- Aggregate extras were flat (42 before, 42 after) — the stats fix didn't add net noise overall, just redistributed it slightly toward Strategy Shape specifically.
- 22 of 31 scoreable cards were completely unchanged.

## Findings

### 1. Bare numbers didn't give the LLM a usable "speed" signal

The hypothesis was that mana value/power/toughness would let the LLM infer curve/speed framing on its own ("this is a cheap efficient threat" vs. "this is a late-game payoff"). In practice, the three Strategy Shape archetypes gained were all wrong, and recall on the targeted archetypes didn't move. Raw stats numbers alone, with no instruction connecting them to the Strategy Shape definitions' "wins via X" framing, don't appear to be enough signal by themselves — consistent with the taxonomy doc's own phrasing that these are "usually inferred... not one signal," i.e. from a synthesis the prompt doesn't currently ask for explicitly.

### 2. Adding context has a real, if small, collateral-regression cost

Two correct suggestions (Firebolt → Graveyard, Kavaron Harrier → Artifacts) were lost, neither Strategy Shape-related — plausibly just prompt-length/attention effects from the added lines, or ordinary sampling noise given the single-run design. Either way, this fix isn't free: it's not "strictly additive" the way it may have seemed on paper.

## Recommendation

This specific, narrow version of the fix (raw stats numbers appended to Oracle Text, no accompanying instruction) doesn't clear the bar the proposal expected — Strategy Shape recall was flat, and aggregate recall went backward by two instances. Two reasonable paths:

- **Pair the stats data with an explicit instruction**, rather than relying on the LLM to connect raw numbers to the Strategy Shape definitions unprompted — e.g. add a line to `llm.py`'s `SYSTEM_PROMPT` (or a note in the Archetypes section) telling the model to weigh mana value/power/toughness specifically when judging Control/Aggro/Combo/Midrange/Tempo. The stats fields themselves (`Card.mana_value/power/toughness`) are cheap infrastructure worth keeping regardless — this would be a small follow-up prompt-language change to re-test the same way, not a rework.
- **Revert to the old prompt language** if a stricter "no aggregate regression" bar is preferred and the instruction-pairing follow-up isn't prioritized soon — the current state trades a small aggregate recall loss for no measured Strategy Shape gain.

Either way, this resolves "worth doing" into a measured result: the fix as originally scoped (numbers only) isn't sufficient on its own.
