# T021 — End-to-End Verification Notes

Working notes for T021 (see `docs/TASKS.md`). Not a permanent doc — findings here get folded into `mechanics-archetypes-taxonomy.md` and a PRD/DESIGN production-integration addendum; this file may be trimmed or dropped once that's done.

## Sample

All 32 cards where the "Modern Cube Consideration List" Notion database has `My Modern Cube = Mainboard` — confirmed cube inclusions with real hand-tags, queried live via the Notion database directly. Full sample, not a subset. One card (Dragonlord Atarka) has no Archetypes hand-tag at all in the source data (not a pipeline miss — nothing to compare against).

Run via `uv run python main.py "<card>"` for all 32, real Scryfall/EDHREC/Anthropic calls, `claude-sonnet-5`. All 32 runs completed; one EDHREC lookup degraded gracefully (Rona, Herald of Invasion — EDHREC has no page under that name for this DFC).

**Comparison caveat**: the Notion schema predates several of this spike's taxonomy decisions. Its `Mechanics / Effects` options still include `Haste`, `Mayhem`, `Connive`, `Delirium` — all explicitly dropped or folded into `Graveyard Matters` in the current taxonomy doc. Its `Archetypes` options include `Flash`, not one of the current 25 archetypes. Comparisons below exclude these stale categories from hit/miss scoring (the tool structurally cannot produce them) but call out the one case where a stale category appears on a real hand-tagged card.

## Aggregate results

- **Mechanics**: 63 hand-tagged mechanic instances across the sample (after excluding stale categories) → tool recalled 53 (**84%**). Tool produced 101 mechanic tags total, 48 beyond the hand-tags (not necessarily wrong — see Precision note below).
- **Archetypes**: 76 hand-tagged archetype instances (excluding the one stale `Flash` tag) → tool recalled 58 (**76%**). Tool produced 101 archetype suggestions total, 43 beyond the hand-tags.
- **23/32 cards** had zero mechanics misses (full recall); **18/32** had zero archetype misses.
- **Only 3/32 cards had *zero* overlap** with hand-tags on either dimension (Marionette Apprentice on mechanics; Pillage the Bog and Atraxa, Grand Unifier on archetypes) — the other 29 cards got at least partial credit, which is the more realistic bar for a suggest-and-confirm workflow per PRD Success Criteria ("confirming/correcting a suggestion is faster than tagging from scratch").
- **Precision note**: "extra" suggestions (tool produced, hand-tag didn't have) are lower-stakes than misses in a suggest-and-confirm UI — a human unchecks a wrong suggestion; a missed one has to be added from scratch. Recall is the more actionable number here, but a high extras rate would still slow down confirmation, so it's not free to ignore.

## Per-card comparison

| Card | Mechanics: hit | Mechanics: missed | Mechanics: extra | Archetypes: hit | Archetypes: missed | Archetypes: extra |
|---|---|---|---|---|---|---|
| Marionette Apprentice | — | Drain, Tokens | +1/+1 Counters | Aristocrats, Artifacts | — | +1/+1 Counters, Tokens |
| Bloodghast | Recursion | — | Reanimate | Aggro, Graveyard, Lands | Reanimator | Aristocrats |
| Deep-Cavern Bat | Hand Disruption | — | Evasion, Lifegain, Removal | Control, Midrange, Tempo | — | — |
| Dark Confidant | Card Advantage | Draw | — | Aggro, Control, Midrange | — | — |
| Emperor of Bones | Graveyard Hate, Recursion | — | +1/+1 Counters, Reanimate | Graveyard, Reanimator | Midrange | +1/+1 Counters |
| Dauthi Voidwalker | Evasion, Graveyard Hate | Card Advantage | — | Control, Graveyard | — | Tempo |
| Blood Artist | Drain | — | Lifegain | Aristocrats | — | — |
| Jadar, Ghoulcaller of Nephalia | Tokens | — | — | Aristocrats | — | Tokens, Zombies |
| Bloodbraid Elf | — | — | Card Advantage | Aggro, Midrange | — | — |
| Wrenn and Six | Recursion, Removal | — | Burn, Card Advantage, Discard Outlet | Lands, Midrange | — | Burn, Graveyard |
| Dragonlord Atarka | Burn, Removal | — | Evasion | — | — (no hand-tag) | Control, Midrange, Ramp |
| Manamorphose | Card Advantage, Draw, Ramp | Fixing | Cantrip | Spellslinger, Storm | Midrange | — |
| Migloz, Maze Crusher | Evasion | — | Removal | Midrange | Aggro | Control |
| Wight of the Reliquary | Ramp, Sac Outlet, Tutor | +1/+1 Counters | Graveyard Matters, Landcycling | Aristocrats, Graveyard, Lands | — | Midrange, Ramp |
| Grist, the Hunger Tide | Removal, Sac Outlet, Self-mill, Tokens | — | Graveyard Matters | Aristocrats, Graveyard, Midrange | Reanimator | Tokens |
| Glissa Sunslayer | Card Advantage, Draw, Removal | — | Curiosity, Modal | Midrange | — | +1/+1 Counters, Control, Elves |
| Abrupt Decay | Removal | — | — | Control, Midrange | — | — |
| Pillage the Bog | Card Advantage | Draw | — | — | Graveyard | Lands, Midrange |
| Atraxa, Grand Unifier | Card Advantage | Draw | Evasion, Lifegain | — | Reanimator, Sneak (+stale: Flash) | Control, Midrange, Ramp |
| Omnath, Locus of Creation | Burn, Card Advantage, Draw, Lifegain, Ramp | — | Cantrip, Removal, Sweeper | Lands, Ramp | — | Burn, Midrange |
| Snapcaster Mage | Recursion | — | — | Control, Spellslinger | Combo, Storm, Tempo | Graveyard, Humans |
| Malcolm, Alluring Scoundrel | Card Advantage, Evasion, Looting | — | Discard Outlet, Draw, Recursion | Tempo | Control, Spellslinger | Graveyard, Reanimator |
| Faerie Mastermind | Card Advantage, Draw | — | Evasion, Tax | Control, Tempo | — | Midrange |
| Ledger Shredder | +1/+1 Counters, Looting | — | Card Advantage, Discard Outlet, Draw, Evasion, Tax | Spellslinger, Tempo | — | +1/+1 Counters, Graveyard |
| Kitsa, Otterball Elite | Copy, Looting | — | Card Advantage, Discard Outlet, Draw | Spellslinger, Tempo | Combo | Graveyard |
| Rona, Herald of Invasion | Looting | Recursion | Card Advantage, Discard Outlet, Draw, Hand Disruption, Ramp | Control, Graveyard, Ramp | Tempo | Humans, Reanimator, Wheels |
| Phantasmal Image | Copy | — | — | Tempo | Control | Midrange |
| Duelist of the Mind | Looting | — | Card Advantage, Discard Outlet, Draw, Evasion | Spellslinger | Control | Humans, Midrange, Tempo |
| Bloodchief's Thirst | Removal | — | — | Control, Midrange | — | — |
| Kavaron Harrier | Tokens | Sac Outlet | — | Aggro, Artifacts, Tokens | — | — |
| Moonshadow | -1/-1 Counters | — | Evasion | Aristocrats, Graveyard | Midrange | +1/+1 Counters |
| Firebolt | Burn, Removal | — | — | Aggro, Graveyard | — | Burn |

## Resolutions applied

Three findings below were confirmed with the user and fixed as part of closing out T021:

- **Finding 1 (Drain/Life Loss)**: rather than broadening Drain, added a new **Life Loss** mechanic (`opponent-loses-life`, 907 cards) to `mechanics-archetypes-taxonomy.md`, kept distinct from Drain (paired loss/gain) and Burn (damage-based). Marionette Apprentice now correctly matches `Life Loss: opponent-loses-life`. Regression test added to `tests/test_taxonomy.py`.
- **Finding 2 (Fixing/mana-filter)**: `mana-filter` confirmed as a clean, mostly-additive addition (132 cards, only 6 overlapping with `mana-fix`) — added to Fixing's candidate tags. Manamorphose now correctly matches `Fixing: mana-filter`.
- **Finding 4 (DFC oracle-text bug)**: fixed in `scryfall.py` — `_extract_oracle_text()` now falls back to concatenating `card_faces[].oracle_text` when the top-level field is absent. Verified against Rona, Herald of Invasion: full oracle text now prints for both faces, and the Archetype prompt now has real text to work with (previously blank). Re-ran Rona post-fix — still misses the "Tempo" hand-tag, but that's now a genuine LLM judgment call rather than a data-completeness artifact, so left as an open pattern (see finding 5/6) rather than something to fix further here. Unit tests added to `tests/test_scryfall.py`.

Findings 3, 5, 6, and 7 below are informational — no code/taxonomy change, either because they confirm an already-known/scoped-out gap (3), or because they're patterns to carry into the production-integration addendum rather than spike-time fixes (5, 6, 7).

## Findings, by cause

### 1. Real, fixable tag-mapping gap: Drain should probably include `opponent-loses-life` — RESOLVED, see above

**Marionette Apprentice** ("...each opponent loses 1 life" — no paired gain clause) is hand-tagged Drain but the tool found nothing, because our taxonomy's Drain mapping is `drain-life` only (369 live cards). Checked the oracle-tags cache directly: `opponent-loses-life` is a separate, much larger tag (907 cards) with no parent/child relationship to `drain-life` — hierarchy-aware matching (T013) can't bridge it on its own.

**Open question for you**: the taxonomy's Drain definition is "Paired life loss/gain" ("loses X life and you gain X life"). Marionette Apprentice has no gain clause — pure opponent life loss. Does your mental model of "Drain" include pure life-loss effects, or should Marionette Apprentice's hand-tag actually be something else? If Drain should broaden, add `opponent-loses-life` to its candidate tags.

### 2. Real, fixable tag-mapping gap: Fixing may be missing `mana-filter` — RESOLVED, see above

**Manamorphose** ("Add two mana in any combination of colors") is hand-tagged Fixing but the tool found nothing — its actual oracle tag is `mana-filter`, not `mana-fix` (our only mapped tag). Spot-checked `mana-filter`'s population directly (Signets, filter lands — squarely fixing-flavored, minimal overlap with `mana-fix`) and added it to Fixing's candidates.

### 3. Confirmed (not new): Tokens' known text-fallback gap

Marionette Apprentice's Fabricate-1 token (conditional ETB choice, not a repeatable generator) is missed by design — this is the exact gap `mechanics-archetypes-taxonomy.md` already documents ("Tokens has no single matching tag... plan on unioning a few tags plus falling back to oracle-text pattern matching") and PRD explicitly scoped out of this spike ("Tokens' text-fallback logic" is a named Non-Goal). Confirms the known gap manifests in practice; doesn't call for new action here.

### 4. Real code bug found: double-faced card oracle text is silently dropped — RESOLVED, see above

**Rona, Herald of Invasion** printed with *no oracle text at all* — confirmed by querying Scryfall directly: DFCs have no top-level `oracle_text` field; the actual text lives in `card_faces[0].oracle_text` / `card_faces[1].oracle_text`. `scryfall.py`'s `fetch_card()` read `data.get("oracle_text", "")`, which silently returned an empty string for every double-faced card. Oracle tags still worked (keyed by `oracle_id`, unaffected), but the terminal's printed oracle text was blank for any DFC, and the Archetype-classification prompt (T017) was missing the card's rules text entirely for DFCs. Fixed via `_extract_oracle_text()` — falls back to joining both faces' text with `"\n//\n"` when the top-level field is absent. Modern-legal cubes lean on DFCs often enough that this was worth fixing now rather than filing as a follow-up.

### 5. Systematic pattern: Strategy Shape archetypes are the weakest category

**11 of 18 archetype miss instances (61%) are Strategy Shape archetypes** (Control, Aggro, Combo, Midrange, Tempo) — Control/Midrange/Tempo each missed 3 times, Combo/Aggro repeatedly too. The taxonomy doc's own `Type` definition says Strategy Shape archetypes are "usually inferred from a card's overall stats/speed, not one signal" — but the T017 prompt never surfaces mana value, power/toughness, or any curve/speed framing; it's built entirely from oracle text + mechanic tags + EDHREC + heuristics, none of which encode "this is a cheap efficient threat" or "this is a late-game payoff" directly.

This reads as a genuine **prompt issue** (PRD's own miss-cause vocabulary) with a clear, actionable fix direction: add mana value (and maybe power/toughness for creatures) to the Oracle Text section of the assembled prompt, so the LLM has an explicit signal for the "stats/speed" basis these five archetypes are supposed to be judged on. This is the single highest-leverage finding from the whole sample — worth prioritizing in the addendum.

### 6. Genuine payoff-recognition gap: Atraxa, Grand Unifier missed Reanimator and Sneak

Atraxa's own oracle text has zero graveyard or cheat-into-play language — it's purely a big, powerful creature that *other* cards care about putting into play cheaply. The taxonomy's own Reanimator qualifying signals explicitly include "big graveyard targets," and Sneak's definition is "cheats big creatures into play" — Atraxa structurally *is* the target these archetypes describe, but nothing in its own text signals that. This is a real limitation of feeding the LLM only the card's own text/tags: recognizing "this card is a good payoff for archetype X" sometimes requires reasoning about the card's cost/stats relative to the format, not just parsing its text. Worth naming in the addendum as a known limitation rather than something fixable by a prompt tweak alone — possibly addressed by explicitly telling the LLM to consider whether a card is a plausible *payoff* for Mechanic-Anchored/Synergy-Package archetypes even without direct textual signal, keyed off high mana value / strong stats.

### 7. Likely hand-tagging looseness, not pipeline misses (flagging for your review, not assuming)

A cluster of misses look more like the hand-tag being broader than the taxonomy's stated definitions than like tool gaps — surfacing for your judgment rather than deciding myself:

- **Draw ×3** (Dark Confidant, Pillage the Bog, Atraxa): none of these literally "draw" — all use reveal/impulse-style effects (Scryfall tags: `life-for-cards`, `impulse`, `repeatable-impulse`), which the taxonomy correctly routes to Card Advantage instead (and the tool did tag Card Advantage correctly on all three). Is "look at top card(s), put one in hand" meant to count as Draw in your tagging, or is Card Advantage-only the more accurate read?
- **+1/+1 Counters** (Wight of the Reliquary): "gets +1/+1 for each creature in graveyard" is a static Lhurgoyf-style bonus, not an actual counter — no counter-related oracle tag on the card.
- **Card Advantage** (Dauthi Voidwalker): steal-and-cast-for-free is arguably a 2-for-1 (defensible either way), but no Scryfall oracle tag supports it.
- **Sac Outlet** (Kavaron Harrier): the card sacrifices its *own* token at end of combat as a drawback/cost, not a player-facing value engine — no sac-outlet oracle tag present.
- **Pillage the Bog → Graveyard**: the card has no graveyard interaction in its text at all (pure card selection scaling with lands controlled) — possibly tagged Graveyard based on its black-green color identity rather than actual function?

## Recommended next steps

1. Confirm with you: Drain/`opponent-loses-life` (finding 1), Fixing/`mana-filter` (finding 2), and the hand-tagging-looseness cluster (finding 7) — your call on each.
2. Fix the DFC oracle-text bug in `scryfall.py` (finding 4) — pending your go-ahead on scope.
3. Update `mechanics-archetypes-taxonomy.md` for whichever of findings 1/2 you confirm.
4. Prioritize the Strategy Shape / mana-value prompt gap (finding 5) as the headline recommendation in the PRD/DESIGN production-integration addendum — it's the largest, most generalizable, most actionable finding from the sample.
5. Write the addendum, folding in DESIGN.md's existing "Follow-up Notes for Production Integration" section plus everything above.
