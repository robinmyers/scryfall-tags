# EDHREC Signal-Contribution Ablation — Notes

Working notes for the follow-up experiment `docs/production-integration-proposal.md` called for under "Known limitations to carry forward": *"EDHREC weak signal's actual contribution is still unvalidated... worth a follow-up experiment (re-run a subsample with EDHREC disabled, diff the suggestions) before assuming it's pulling its weight in production."* Not a permanent doc — findings here get folded into `production-integration-proposal.md`.

## Method

Added a `--no-edhrec` flag to `main.py` (skips the EDHREC fetch entirely, reuses the existing `edhrec_signal=None` degradation path already built for real EDHREC failures). Re-ran all 32 T021 cards (`docs/t021-verification-notes.md`) through the *current* pipeline — post the Life Loss/`mana-filter` taxonomy fixes and the double-faced-card oracle-text bug fix, none of which the original T021 EDHREC-on runs had — twice each:

1. `uv run python main.py "<card>"` (EDHREC on)
2. `uv run python main.py "<card>" --no-edhrec` (EDHREC off)

All 64 runs completed and logged to `run_log.jsonl` (Rona, Herald of Invasion's "on" run degrades exactly as it did in T021 — EDHREC has no page for that DFC — so its "on" condition ran with `edhrec_signal=None` too, unaffected by the flag; both its runs are effectively "off" and it contributes no signal to this experiment either way).

Archetype suggestions were diffed per card (on-set vs off-set) and scored for recall/precision against the same hand-tag ground truth already transcribed in T021's comparison table (hit ∪ missed columns, stale categories like `Flash` excluded, Dragonlord Atarka excluded — no Archetypes hand-tag at all).

**Caveat**: one run per condition per card. The LLM call is not deterministic, so some of the on/off diff is ordinary sampling noise rather than a real EDHREC effect — this is exactly what the analysis below tries to separate out, using whether each suggestion's own reasoning text cites the EDHREC signal as the discriminator, not just presence/absence of the archetype.

## Aggregate results

- **ON recall**: 57/76 hand-tagged archetype instances (**75%**)
- **OFF recall**: 56/76 (**74%**) — a one-instance difference, within noise
- **ON extras** (suggestions beyond hand-tags): 42
- **OFF extras**: 47 — OFF produced *more* noise than ON, the opposite of what a meaningful EDHREC contribution would predict
- Across all 224 ON-condition archetype suggestions (32 cards), only **3 (1.3%)** explicitly cite EDHREC in their reasoning — even when the signal is present and in-context, the LLM leans on it rarely
- **8 archetypes appeared only in the ON condition** (present with EDHREC, absent without); **12 appeared only in the OFF condition** (absent with EDHREC, present without) — of the 8 ON-only gains, exactly **1** cites EDHREC in its reasoning: **Kavaron Harrier → Artifacts** ("Both the Harrier and the tokens it creates are artifact creatures, feeding into artifact-count or artifact-synergy shells as suggested by the EDHREC artifact-heavy signal list"). This is also the one case where the ON-only gain is a real hand-tag hit (Kavaron Harrier's hand-tags include Artifacts) — the single instance in the whole sample where recall measurably depended on EDHREC.
- The other 7 ON-only gains and all 12 OFF-only gains show no EDHREC citation in their reasoning — textually indistinguishable from ordinary LLM run-to-run variance.

## Per-card diffs (cards with any on/off difference)

| Card | Hand-tags | ON-only | OFF-only | Cited EDHREC? |
|---|---|---|---|---|
| Dark Confidant | Aggro, Control, Midrange | — | Humans | no |
| Emperor of Bones | Graveyard, Midrange, Reanimator | — | Aristocrats | no |
| Dauthi Voidwalker | Control, Graveyard | Aristocrats | Tempo | no |
| Bloodbraid Elf | Aggro, Midrange | — | Aggro | no |
| Wrenn and Six | Lands, Midrange | — | Burn | no |
| Glissa Sunslayer | Midrange | +1/+1 Counters | Zombies | no |
| Abrupt Decay | Control, Midrange | — | Tempo | no |
| Pillage the Bog | Graveyard | — | Control | no |
| Omnath, Locus of Creation | Lands, Ramp | Control | — | no |
| Snapcaster Mage | Combo, Control, Spellslinger, Storm, Tempo | — | Humans | no |
| Faerie Mastermind | Control, Tempo | Midrange | — | no |
| Ledger Shredder | Spellslinger, Tempo | — | Midrange | no |
| Duelist of the Mind | Control, Spellslinger | Spellslinger | Humans, Midrange | no |
| **Kavaron Harrier** | **Aggro, Artifacts, Tokens** | **Artifacts** | — | **yes — and it's a real hit** |
| Moonshadow | Aristocrats, Graveyard, Midrange | +1/+1 Counters | — | no |
| Firebolt | Aggro, Graveyard | Spellslinger | — | no |

18 of 32 cards had zero on/off difference at all — identical archetype sets whether or not EDHREC was in the prompt.

## Findings

### 1. EDHREC's measured contribution on this sample is real but minimal: one hand-tag hit out of 76

Kavaron Harrier → Artifacts is the only case in the whole 32-card sample where an archetype the tool got *right* (matched a hand-tag) both (a) only appeared when EDHREC was in the prompt, and (b) explicitly named EDHREC as the reason in its own output. Every other on/off difference — 7 more ON-only gains, all 12 OFF-only gains — reads as ordinary LLM sampling noise: no citation of the signal, and roughly symmetric churn in both directions (if EDHREC were adding real signal, gains should outweigh losses; here losses outweigh gains).

### 2. The LLM rarely leans on EDHREC even when it's available

3 of 224 ON-condition reasonings (1.3%) mention EDHREC at all. The system prompt (`llm.py`) tells the model to ground its reasoning "in the provided context," which includes EDHREC, but doesn't instruct it to specifically weigh or cite the synergy signal — so most of the time, oracle text + mechanic tags alone appear to carry the classification, EDHREC or not.

### 3. Aggregate recall/precision is a wash

75% vs 74% recall, 42 vs 47 extras — neither number moves enough to argue EDHREC materially improves suggestion quality in aggregate, consistent with finding 1's granular read.

## Recommendation

EDHREC's contribution on this sample is real (one attributable case) but too small to justify treating it as a load-bearing input, especially given: it's an unofficial, unstable API (`DESIGN.md`'s own characterization) that already needed a dedicated graceful-degradation path (T016) for real outages; it adds a full extra network round-trip to the per-card pipeline latency the production-integration proposal already flags as worth profiling; and the LLM demonstrably ignores it 98.7% of the time regardless.

Two reasonable paths, either defensible from this data:
- **Drop EDHREC from the production pipeline.** The measured lift (1/76 hand-tag instances) doesn't clearly clear the bar of "worth the added latency, failure surface, and unofficial-API dependency" for a production card-add flow, versus a spike where it was explicitly being tested.
- **Keep it, but make its use auditable.** If kept, update the system prompt (`llm.py`'s `SYSTEM_PROMPT`) to explicitly instruct the model to name which input (oracle text, mechanic tags, or EDHREC) supports each suggestion — this experiment could only measure EDHREC's contribution by scanning free-text reasoning for incidental citations, which undercounts silent-but-real influence and overcounts nothing at 1.3%. Making citation mandatory would let this same ablation be re-run with a much cleaner signal.

Either way, this resolves the "still unvalidated" status: EDHREC has now been measured, and the honest conclusion is "small, real, but not clearly worth its cost as currently used" rather than "unknown."
