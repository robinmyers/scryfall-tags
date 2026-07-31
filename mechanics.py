"""The rule/tag pass: match a card's oracle tags against the taxonomy's
tag->mechanic lookup to produce Mechanics suggestions with their source tag(s).
"""


def match_mechanics(
    oracle_tags: list[str], tag_lookup: dict[str, str]
) -> dict[str, list[str]]:
    """Match oracle tags against a tag->mechanic lookup.

    Returns Mechanic name -> list of matching source tag(s). Tags not
    present in the lookup are ignored — most of a card's oracle tags
    won't be part of the known Mechanics taxonomy at all.
    """
    matches: dict[str, list[str]] = {}
    for tag in oracle_tags:
        mechanic = tag_lookup.get(tag)
        if mechanic is not None:
            matches.setdefault(mechanic, []).append(tag)
    return matches
