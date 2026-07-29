# PRD: Cube Classification Pipeline Spike

## Problem & Vision
A standalone spike to prove out the Mechanics/Archetype auto-classification pipeline before folding it into Cube Workshop proper. Run the rule/tag pass (Scryfall oracle tags, per the verified mapping doc) and the LLM archetype pass against real cards from the Modern Cube Consideration List, see how well the suggestions hold up, and use what's learned to refine the taxonomy spec — filling gaps like Discard's still-unconfirmed tag, deciding how multi-tag mechanics union, and validating the EDHREC weak-signal idea — before it becomes a production feature in the card-add UI.

## Target Users
The sole builder/maintainer of Cube Workshop and curator of the Modern Cube. The problem it solves: manually assigning Mechanics and Archetype tags to every card in a large cube is slow and inconsistent, and there's a need for confidence — before building it into the production app — that an automated suggest-and-confirm pipeline actually produces good enough suggestions to be worth the UI/engineering investment.

## Happy Path
The user runs the CLI script one card at a time (not in batch, since manual comparison is the point). For each card: the tool fetches Scryfall data (oracle text, type line, oracle tags), runs the rule/tag pass to produce Mechanics suggestions, fetches EDHREC theme/synergy data as a weak signal, then runs the LLM pass (fed oracle text, mechanic tags + confidence, EDHREC signal, the archetype list, and mechanic-affinity heuristics) to produce Archetype suggestions. The user compares both sets of suggestions against what they'd have tagged by hand, and the patterns observed across cards feed back into refining the taxonomy doc, the tag mapping, and the prompt itself.

## Success Criteria
- Across a meaningful sample of cards run one at a time, Mechanics and Archetype suggestions match hand-tagging often enough that confirming/correcting a suggestion is faster than tagging from scratch
- Where suggestions miss, the misses are traceable to fixable causes (tag mapping gap, prompt issue) rather than fundamental flaws in the approach
- Spike concludes with an updated taxonomy/tag-mapping spec reflecting what was learned
- Spike concludes with a PRD/DESIGN update (or addendum) proposing how the classification pipeline integrates into Cube Workshop's card-add workflow

## Assumptions
- Scryfall oracle tags provide sufficient signal for reliable Mechanics classification for most cards
- LLM archetype classification, given the assembled context, is accurate enough to support a human-in-the-loop confirm/correct workflow
- The EDHREC weak signal meaningfully improves archetype suggestion quality — this is unvalidated going in and is one of the things the spike is meant to test, not a given
- One-card-at-a-time review pace is acceptable for reaching a representative sample within the spike's scope

## Functional Requirements
- Accept a single card identifier as input and fetch its Scryfall data (oracle text, type line, oracle tags)
- Run the rule/tag pass: match the card's Scryfall oracle tags against the Mechanics taxonomy mapping, output suggested Mechanics with their source tag(s)
- Fetch EDHREC theme/synergy data for the card as a weak signal input
- Run the LLM pass: construct the archetype-classification prompt (oracle text + mechanic tags/confidence + EDHREC signal + archetype list + mechanic-affinity heuristics), call the LLM, and parse suggested Archetypes
- Display both Mechanics and Archetype suggestions in the terminal for manual comparison against the user's own tagging judgment
- Record each run's inputs and suggestions to a local log for later pattern review across cards

## Non-Functional Requirements
- Handles Scryfall/EDHREC API rate limits gracefully (reuse the retry/backoff pattern already built for the tag verification script)
- Fast enough turnaround per card to support an interactive, one-at-a-time review loop
- Runs locally as a personal tool — no deployment, scaling, or availability requirements

## Non-Goals
- Any UI, database, or persistence layer beyond simple local output/logging
- Batch or bulk processing — one card at a time only
- Integration into the actual Cube Workshop app — that's an output of the spike (a proposed PRD/DESIGN update), not something built during it
- Fully resolving all open tag ambiguities (e.g. Discard's still-unconfirmed tag, Tokens' text-fallback logic) before the spike starts — surfacing these gaps is part of the spike's purpose
- Any accuracy/confidence scoring system beyond passing through what the rule pass and LLM already produce
