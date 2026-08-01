"""The rule/tag pass: match a card's oracle tags against the taxonomy's
tag->mechanic lookup to produce Mechanics suggestions with their source tag(s).
"""


def match_mechanics(
    oracle_tags: list[str],
    tag_lookup: dict[str, str],
    tag_ancestors: dict[str, set[str]],
) -> dict[str, list[str]]:
    """Match oracle tags against a tag->mechanic lookup, hierarchy-aware.

    For each of a card's oracle tags, checks the tag itself *and* all of its
    ancestor tags (e.g. "land-ramp" is a child of "ramp") against the lookup.
    A single tag can resolve to more than one mechanic this way — including
    across our own mechanic boundaries in cases where Scryfall's own tag
    ontology is broader than our taxonomy's distinctions (e.g. "reanimate"'s
    own parent tag is "recursion", even though we treat those as separate
    mechanics). That's accepted as informative for the human reviewer rather
    than suppressed.

    Returns Mechanic name -> list of matching source tag(s). Tags with no
    match (directly or via ancestry) are ignored — most of a card's oracle
    tags won't be part of the known Mechanics taxonomy at all.
    """
    matches: dict[str, list[str]] = {}
    for tag in oracle_tags:
        mechanics_matched: set[str] = set()

        mechanic = tag_lookup.get(tag)
        if mechanic is not None:
            mechanics_matched.add(mechanic)

        for ancestor in tag_ancestors.get(tag, ()):
            ancestor_mechanic = tag_lookup.get(ancestor)
            if ancestor_mechanic is not None:
                mechanics_matched.add(ancestor_mechanic)

        for mechanic in mechanics_matched:
            matches.setdefault(mechanic, []).append(tag)

    return matches
