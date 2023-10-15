from melbalabs.summarize_consumes import grammar

from melbalabs.summarize_consumes.main import great_rage
from melbalabs.summarize_consumes.main import player

def test_great_rage():
    lines = """
4/14 13:55:49.949  Jaekta gains 10 Rage from Jaekta 's Berserker Rage Effect.
4/19 21:10:19.076  Dragoon gains 60 Rage from Dragoon 's Great Rage.
4/19 21:10:19.076  Dragoon gains 60 Rage from Dragoon 's Mighty Rage.
4/19 21:10:19.076  Dragoon gains 60 Rage from Dragoon 's Rage.
    """
    lines = lines.split('\n')
    found = 0
    for line in lines:
        res = great_rage(line)
        if res: found += 1
    for pot in ['Great Rage Potion', 'Mighty Rage Potion', 'Rage Potion']:
        assert player['Dragoon'][pot] == 1
    assert found == 3
