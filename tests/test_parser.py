from melbalabs.summarize_consumes import grammar

from melbalabs.summarize_consumes.main import great_rage
from melbalabs.summarize_consumes.main import tea_with_sugar
from melbalabs.summarize_consumes.main import gains_consumable
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

def test_tea_with_sugar():
    lines = """
4/21 21:01:38.861  Psykhe 's Tea with Sugar heals Psykhe for 1613.
4/21 21:22:41.023  Shumy gains 1209 Mana from Shumy 's Tea with Sugar.
    """
    lines = lines.split('\n')
    for line in lines:
        tea_with_sugar(line)
    assert player['Psykhe']['Tea with Sugar'] == 1
    assert player['Shumy']['Tea with Sugar'] == 0

def test_gains_consumable():
    lines = """
4/20 20:29:51.707  Rando gains Greater Arcane Elixir (1).
4/14 21:56:51.221  Rando gains Arcane Elixir (1).
4/14 21:56:51.221  Rando gains Health II (1).
10/11 23:37:59.079  Psykhe gains Shadow Protection  (1).
10/11 23:37:59.079  Psykhe gains Shadow Protection (1).
10/11 20:44:17.813  Axe gains Gift of Arthas (1).
10/11 20:44:17.813  Unholy Axe gains Gift of Arthas (1).
    """
    lines = lines.split('\n')
    for line in lines:
        gains_consumable(line)
    assert player['Rando']['Greater Arcane Elixir'] == 1
    assert player['Rando']['Arcane Elixir'] == 1
    assert player['Rando']['Elixir of Fortitude'] == 1
    assert player['Rando']['Increased Stamina'] == 0
    assert player['Psykhe']['Shadow Protection'] == 1
    assert player['Axe']['Gift of Arthas'] == 1
    assert player['Unholy Axe']['Gift of Arthas'] == 0
