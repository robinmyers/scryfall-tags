# Cube Workshop — Mechanics & Archetypes Taxonomy (v1 draft)

This is a working spec for the classification pipeline: the rule/tag pass targets the Mechanics table, the LLM pass targets the Archetypes table. Both tables are meant to be pasted into the respective prompts as context, not just used as internal docs.

---

## Archetypes

`Type` marks how a card qualifies, since the qualifying logic differs by category:
- **Strategy Shape** — describes overall deck plan, not a synergy package. Usually inferred from a card's overall stats/speed, not one signal.
- **Mechanic-Anchored** — a named mechanic is the core enabler; payoff cards belong even without the mechanic itself.
- **Synergy Package** — a themed set of enablers + payoffs.
- **Kindred** — tribal enablers + payoffs, cross-references the Creature Types field.

| Archetype | Type | Definition | Qualifying Signals |
|---|---|---|---|
| Control | Strategy Shape | Wins via resource/tempo denial into a late-game win condition | Efficient removal, sweepers, counterspells, card draw, high-impact finishers |
| Aggro | Strategy Shape | Wins by pressuring life total fast before opponent stabilizes | Cheap, efficient creatures; direct damage; low curve |
| Combo | Strategy Shape | Wins by assembling a specific card combination for a fast/instant win | Explicit combo pieces, tutors for them, enablers |
| Midrange | Strategy Shape | Flexible value plan — efficient threats/removal, grinds incremental advantage | Solid rate creatures, removal, card advantage, no single dependency |
| Tempo | Strategy Shape | Wins by pairing efficient threats with disruption to stay ahead on board | Bounce, cheap counters, evasive/efficient creatures |
| **Ramp** | Mechanic-Anchored | Accelerates mana **and** the big spells it enables | Cards tagged Mechanic:Ramp or Mechanic:Mana Dork, *plus* high-CMC payoffs costed to be ramped into |
| **Tokens** | Mechanic-Anchored | Generates a wide board **and** rewards having one | Cards tagged Mechanic:Tokens, *plus* anthems/sac outlets/go-wide finishers |
| **+1/+1 Counters** | Mechanic-Anchored | Places counters **and** rewards doing so | Cards tagged Mechanic:+1/+1 Counters, *plus* proliferate/counter-doubling/counter-matters payoffs |
| **Burn** | Mechanic-Anchored | Deals direct damage **and** rewards having dealt it | Cards tagged Mechanic:Burn, *plus* "whenever a source deals damage to a player" payoffs |
| **Blink** | Mechanic-Anchored | Repeated ETB value via exile/return **and** the ETB payoffs it enables | Cards tagged Mechanic:Blink, *plus* strong ETB creatures that don't blink themselves |
| Aristocrats | Synergy Package | Sacrifice-for-value | Sac outlets + death-trigger payoffs |
| Reanimator | Synergy Package | Cheats big creatures in from the graveyard | Discard/self-mill enablers + Reanimate effects + big graveyard targets; Looting/Rummage cards often support this shell |
| Spellslinger | Synergy Package | Rewards casting many noncreature spells | Spell-triggered payoffs + cheap efficient instants/sorceries |
| Artifacts | Synergy Package | Payoffs/support for an artifact-heavy shell | Cost reducers, artifact-matters triggers, treasure/artifact-token synergy |
| Graveyard | Synergy Package | Broader graveyard value beyond pure reanimation | Recursion, self-mill, delirium, flashback-style value; Looting/Rummage cards often support this shell |
| Lands | Synergy Package | Rewards extra land drops/land types | Landfall, land recursion, landcycling, "lands matter" triggers |
| Storm | Synergy Package | Chains cheap spells toward a single explosive turn | Cost reduction/discounts, ritual effects, storm-count payoffs |
| Sneak | Synergy Package | Cheats big creatures into play without casting them | "Put onto the battlefield" cheat effects (Sneak Attack-style, Show and Tell-style); adjacent to Reanimator but not graveyard-based |
| Wheels | Synergy Package | Payoffs around drawing/discarding whole hands | "Each player discards their hand, then draws" effects + hellbent/discard payoffs |
| Proliferate | Synergy Package | Payoffs for adding extra counters of any kind | Proliferate effects + counter-based payoffs across counter types |
| Goblins | Kindred | Goblin tribal package | Goblin creature type + Goblin-tribal payoffs |
| Zombies | Kindred | Zombie tribal package | Zombie creature type + Zombie-tribal payoffs |
| Elves | Kindred | Elf tribal package | Elf creature type + Elf-tribal payoffs |
| Humans | Kindred | Human tribal package | Human creature type + Human-tribal payoffs |
| Cat | Kindred | Cat tribal package | Cat creature type + Cat-tribal payoffs |

---

## Mechanics / Effects

Haste, Mayhem, and Connive are dropped — Haste duplicates Keyword Abilities with no dedicated archetype; Mayhem and Connive are narrow keyword actions rather than functional roles. Curiosity is kept since it isn't tied to a specific named keyword. Looting and Rummage are kept as separate entries — both are forms of card advantage, alongside Draw, Card Advantage, and others.

| Mechanic | Definition | Oracle-Text Signal Examples | Linked Archetype |
|---|---|---|---|
| Draw | Card draw effects | "draw a card," "draw two cards" | — |
| Cantrip | A spell/permanent that draws a card as a bonus to its main effect (self-replacing) | e.g. a removal or combat trick that also says "draw a card" | — |
| Impulsive Draw | Exiles cards from the library with a limited window to play them | "exile the top card of your library. You may play that card until end of turn/this turn" | — |
| Removal | Removes/neutralizes a single opposing permanent | "destroy target," "exile target," "gets -X/-X" | — |
| Sweeper | Removal that hits multiple creatures at once (board wipe) | "destroy all creatures," "each creature gets -X/-X" | — |
| Discard | Forces a player to discard | "discard a card," "each player discards" | — |
| Ramp | Accelerates available mana | "search your library for a land," "add {mana}" | Ramp |
| Mana Dork | A creature that taps for mana (overlaps with Ramp by design) | "{T}: Add {mana}" on a creature | Ramp |
| Counter | Countermagic | "counter target spell" | — |
| Tutor | Searches library for a specific card | "search your library for a card" | — |
| Bounce | Returns a permanent to hand | "return target permanent to its owner's hand" | — |
| Recursion | Returns cards from graveyard to hand (see Reanimate for creature-to-battlefield returns) | "return target card from your graveyard to your hand" | Graveyard |
| Reanimate | Returns a creature (or other permanent) from a graveyard directly to the battlefield | "return target creature card from a graveyard to the battlefield" | Reanimator |
| Tokens | Creates token permanents | "create a/an X/X token" | Tokens |
| Looting | Draw then discard (filtering) | "draw a card, then discard a card" | Graveyard, Reanimator |
| Rummage | Discard then draw (filtering, reverse order from Looting) | "discard a card, then draw a card" | Graveyard, Reanimator |
| Hand Disruption | Targeted discard/reveal-and-choose against opponents | "target opponent reveals their hand, you choose" | — |
| Card Advantage | Net-positive card generation not captured above | 2-for-1 effects, value ETBs | — |
| Drain | Paired life loss/gain | "loses X life and you gain X life" | — |
| Graveyard Hate | Disrupts opponents' graveyards | "exile target card from a graveyard" | — |
| Sac Outlet | Lets you sacrifice your own permanents for value | "sacrifice a creature:" | Aristocrats |
| Evasion | Creatures that are harder to block, via keywords (flying, menace, etc.) or other means | flying/menace/unblockable-style text, either keyword or functional | — |
| Self-mill | Puts your own cards into your graveyard | "put the top X cards of your library into your graveyard" | Reanimator, Graveyard |
| Mill | Puts an opponent's cards into their graveyard | "target player puts the top X cards of their library into their graveyard" | — |
| +1/+1 Counters | Places/uses +1/+1 counters | "put a +1/+1 counter on" | +1/+1 Counters |
| Fixing | Provides mana color fixing | "add one mana of any color" | — |
| Energy | Uses the energy counter mechanic | "get {E}" | — |
| Burn | Deals direct damage | "deals X damage to any target" | Burn |
| Graveyard Matters | Support/payoff for cards or specific card types accumulating in a graveyard (own or any) — covers Delirium, Threshold, Undergrowth, and similar count-based graveyard keywords generally rather than one specific keyword | "delirium," "threshold," card-count/card-type-count graveyard conditions | Graveyard |
| Lifegain | Gains life | "gain X life" | — |
| Pump | Temporary +X/+X stat boost, any source | "gets +X/+X until end of turn" | — |
| Combat Trick | Instant-speed effect used as a combat ambush — stat boosts, fight spells, or granting keywords like indestructible/deathtouch for the turn | instant-speed "+X/+X," "fight," "gains indestructible/deathtouch until end of turn" | — |
| Cost Reduction | Reduces casting cost of spells | "costs {X} less to cast" | — |
| Tax | Increases the cost of opponents' actions | "spells your opponents cast cost {1} more" | — |
| Protection | Grants protection, indestructible, hexproof, or shroud to a permanent — distinct from simply having one of those keywords | "gains protection from," "creatures you control gain hexproof/indestructible" | — |
| Copy | Copies spells or permanents | "copy target spell/creature" | — |
| Tap | Taps opposing permanents / tap-based abilities (kept distinct from Removal) | "tap target permanent," "{T}:" | — |
| Stun | Applies stun counters (kept distinct from Removal) | "stun counter" | — |
| Discard Outlet | Lets you discard cards intentionally for value (no draw) | "discard a card:" | Reanimator |
| Unblockable | Grants unblockable status | "can't be blocked" | — |
| Curiosity | Draw-on-combat-damage effect | "whenever this creature deals combat damage to a player, draw a card" | — |
| Exchange | Swaps permanents/cards between players/zones | "exchange control of" | — |
| Modal | Spell/permanent offering a choice of effects | "choose one —," "choose two —" | — |
| Landcycling | Cycling specifically for a land | "Landcycling {cost}" | Lands |
| -1/-1 Counters | Uses -1/-1 counters as removal/payoff *(niche — currently 1 supporting card; tracked for future growth)* | "-1/-1 counter" | — |

---

## Scryfall Oracle Tag Mapping (draft — needs live verification)

Scryfall's Tagger project has thousands of oracle tags, some very granular (e.g. separate `cost-reducer-self`, `cost-reducer-sorcery`, `cost-reducer-vehicle` rather than one generic tag). This mapping is a starting point pulled from what's confirmed in Scryfall's own docs/search examples plus their kebab-case naming convention — not a verified live query, so treat unconfirmed rows as candidates to check, not facts.

**Confirmed via live testing or direct experience** (not guessed): `draw`, `cantrip`, `impulsive-draw`, `removal`, `sweeper`, `mana-dork`, `ramp`, `counterspell`, `tutor`, `bounce`, `recursion`, `reanimate` (+ `reanimate-<type>` family), `loot`, `rummage`, `hand-disruption`, `card-advantage`, `discard-outlet`, `repeatable-token-generator`, `drain-life`, `hate-graveyard`, `sacrifice-outlet`, `mill-self`, `mill-opponent`, `pp-counters-matter`/`gains-pp-counters`/`gives-pp-counters`, `mana-fix`, `energy-generator`, `combat-trick`, `tax`, `protection`/`gives-protection`/`gives-hexproof`/`gives-indestructible`, `tapper`, `freeze-creature`, `unblockable`/`gives-unblockable`, `exchange-control`, `tutor-land`, `mm-counters-matter`/`gains-mm-counters`/`gives-mm-counters`, `cost-reducer-<type>` (pattern).

One thing still worth a spot-check as more cards get added:
- **Landcycling's tag (`tutor-land`) reads broader than the keyword** and no more precise match turned up after spot-checking. Going with it for now — likely tags any land-tutor effect, not just Landcycling specifically, so keep an eye out for overtagging as the mapping gets used.

All Mechanics entries now have a confirmed or experience-based tag mapping — nothing left unverified in this pass.

Several earlier guesses were confirmed wrong and corrected: `card-draw` -> `draw`; `board-wipe`/`boardwipe` -> `sweeper`; `impulse-draw` -> `impulsive-draw`; `looting` -> `loot` only; `graveyard-hate` -> `hate-graveyard` (order flipped); `self-mill` -> `mill-self` (order flipped); `mill` -> `mill-opponent`; `mana-fixing` -> `mana-fix`; `energy` -> `energy-generator`; `tap-effect` -> `tapper`; `stun`/`counter-fuel-stun` -> `freeze-creature`; `exchange` -> `exchange-control`; `landcycling` -> `tutor-land`; `cost-increaser` dropped (not real).

**Open ambiguity — Discard vs. Discard Outlet:** the real tag `discard-outlet` is defined by Scryfall as "ways to discard your own cards," which matches our **Discard Outlet** mechanic (self-discard for value), not our **Discard** mechanic (forcing an opponent to discard). Don't map `discard-outlet` to the Discard row — it belongs to Discard Outlet. Discard (opponent-facing) still needs its own confirmed tag.

**Tokens has no single matching tag.** `repeatable-token-generator` is the most important one, but it won't catch every token maker (one-shot generators, token-doublers, etc.) — plan on unioning a few tags plus falling back to oracle-text pattern matching for this one specifically, rather than expecting a clean 1:1 tag match.

| Mechanic | Candidate Tag(s) | Confidence | Notes |
|---|---|---|---|
| Draw | `draw` | Confirmed | — |
| Cantrip | `cantrip` | Confirmed | — |
| Impulsive Draw | `impulsive-draw` | Confirmed | — |
| Removal | `removal`, `creature-removal` | Confirmed | May need to union sub-tags (artifact/enchantment/planeswalker removal) |
| Sweeper | `sweeper` | Confirmed | — |
| Discard | *(unconfirmed — do not use `discard-outlet`, see note above)* | Needs verification | — |
| Ramp | `ramp` | Confirmed | — |
| Mana Dork | `mana-dork` | Confirmed | — |
| Counter (counterspell) | `counterspell` | Confirmed | Scryfall disambiguates from +1/+1 counters this way — good, avoids collision |
| Tutor | `tutor` | Confirmed | — |
| Bounce | `bounce` | Confirmed | — |
| Recursion | `recursion` | Confirmed | May be split further by target type |
| Reanimate | `reanimate`, `reanimate-<type>` family | Confirmed | Pull the full tag list to enumerate all `reanimate-*` variants rather than guessing types one by one |
| Tokens | `repeatable-token-generator` (+ others, + text fallback) | Confirmed (partial) | No single umbrella tag — see note above |
| Looting | `loot` | Confirmed | — |
| Rummage | `rummage` | Confirmed | — |
| Hand Disruption | `hand-disruption` | Confirmed | — |
| Card Advantage | `card-advantage` | Confirmed | — |
| Drain | `drain-life` | Confirmed | — |
| Graveyard Hate | `hate-graveyard` | Confirmed | Order flipped from initial guess |
| Sac Outlet | `sacrifice-outlet` | Confirmed | — |
| Evasion | `evasion` | Confirmed | — |
| Self-mill | `mill-self` | Confirmed | Order flipped from initial guess |
| Mill | `mill-opponent` | Confirmed | — |
| +1/+1 Counters | `pp-counters-matter`, `gains-pp-counters`, `gives-pp-counters` | Confirmed | 3 tags — `gives-pp-counters` is also used for Pump, see note below |
| Fixing | `mana-fix` | Confirmed | — |
| Energy | `energy-generator` | Confirmed | — |
| Burn | `burn` | Confirmed | — |
| Graveyard Matters | `cards-in-graveyard-matter`, `card-types-in-graveyard-matter` | Confirmed | Replaces the narrower Delirium-specific tag guess — no dedicated Delirium tag exists; these catch Delirium/Threshold/Undergrowth-style effects broadly |
| Lifegain | `lifegain` | Confirmed | — |
| Pump | `firebreathing`, `power-boost-to-all`, `shade-pump` | Confirmed | firebreathing = +X/+0 until EOT; power-boost-to-all = anthem-style boost to all creatures; shade-pump = classic +X/+X until EOT. Possibly not exhaustive |
| Combat Trick | `combat-trick` | Confirmed | — |
| Cost Reduction | `cost-reducer-creature`, `cost-reducer-noncreature` | Confirmed | Simplified from the granular per-type family (self/sorcery/vehicle/saga), which only caught a fraction of cards (e.g. `cost-reducer-vehicle` matched just 1) |
| Tax | `tax` | Confirmed | `cost-increaser` dropped, not a real tag |
| Protection | `protection`, `gives-protection`, `gives-hexproof`, `gives-indestructible` | Confirmed | 4 tags |
| Copy | `copy` | Confirmed | — |
| Tap | `tapper` | Confirmed | — |
| Stun | `freeze-creature` | Confirmed | Completely different name than originally guessed |
| Discard Outlet | `discard-outlet` | Confirmed | "Ways to discard your own cards" — see note above, this is the one, not Discard |
| Unblockable | `unblockable`, `gives-unblockable` | Confirmed | 2 tags |
| Curiosity | `curiosity`, `curiosity-like` | Confirmed | — |
| Exchange | `exchange-control` | Confirmed | — |
| Modal | `modal` | Confirmed | — |
| Landcycling | `tutor-land` | Confirmed | No more consistent tag found after spot-checking landcyclers — going with this, continue spot-checking as more cards are added |
| -1/-1 Counters | `mm-counters-matter`, `gains-mm-counters`, `gives-mm-counters` | Confirmed | 3 tags

Kindred archetypes (Goblins, Zombies, Elves, Humans, Cat) don't need oracle-tag mapping at all — creature type is a native Scryfall field (`t:goblin`), so tribal enablers/payoffs are better sourced from type line + a smaller set of tribal-payoff oracle tags than from otag matching alone.

---

## Status

Naming and scope decisions are settled as of this draft: kept as "Protection" (grants protection/indestructible/hexproof/shroud, distinct from the literal keyword), Combat Trick scoped broader than Pump, and Recursion (graveyard-to-hand) split from Reanimate (graveyard-to-battlefield for creatures).

The Scryfall oracle tag mapping for every Mechanics entry is now verified against live data (all tags returned nonzero card counts on the latest run) — see the Mechanics/Effects mapping table above. Remaining implementation work: build the union logic for multi-tag mechanics (Protection, ±1/±1 Counters, Pump, Unblockable, Cost Reduction, Curiosity, Reanimate) so a card gets the mechanic once even if it matches multiple constituent tags, and decide how to handle cards with no matching tag at all (text-pattern fallback, especially for Tokens given `repeatable-token-generator` alone won't catch one-shot token makers).
