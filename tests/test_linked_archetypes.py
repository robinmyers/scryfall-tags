from linked_archetypes import match_linked_archetypes


def test_single_mechanic_single_archetype():
    suggestions = match_linked_archetypes({"Reanimate": ["reanimate"]})

    assert len(suggestions) == 1
    assert suggestions[0].archetype == "Reanimator"
    assert "Reanimate (reanimate)" in suggestions[0].reasoning


def test_mechanic_linking_to_two_archetypes():
    suggestions = match_linked_archetypes({"Self-mill": ["mill-self"]})

    assert {s.archetype for s in suggestions} == {"Reanimator", "Graveyard"}


def test_two_mechanics_merge_into_one_suggestion_for_shared_archetype():
    suggestions = match_linked_archetypes(
        {"Recursion": ["recursion"], "Self-mill": ["mill-self"]}
    )

    graveyard = [s for s in suggestions if s.archetype == "Graveyard"]
    assert len(graveyard) == 1
    assert "Recursion (recursion)" in graveyard[0].reasoning
    assert "Self-mill (mill-self)" in graveyard[0].reasoning


def test_untrusted_mechanic_produces_nothing():
    # Discard Outlet and Looting both have real linked archetypes in the
    # taxonomy doc, but were excluded from TRUSTED_LINKS after evidence
    # showed they're unreliable (0/4 and 0/3 precision in the T021 sample).
    suggestions = match_linked_archetypes(
        {
            "Discard Outlet": ["discard-outlet"],
            "Looting": ["loot"],
            "Tokens": ["repeatable-token-generator"],
            "Burn": ["burn"],
        }
    )

    assert suggestions == []


def test_no_mechanics_returns_empty():
    assert match_linked_archetypes({}) == []
