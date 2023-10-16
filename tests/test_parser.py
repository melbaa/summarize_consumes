from melbalabs.summarize_consumes.main import player
from melbalabs.summarize_consumes.main import player_detect
from melbalabs.summarize_consumes.main import death_count

from melbalabs.summarize_consumes.main import parse_line

def test_rage_consumable_line():
    lines = """
4/14 13:55:49.949  Jaekta gains 10 Rage from Jaekta 's Berserker Rage Effect.
4/19 21:10:19.076  Dragoon gains 60 Rage from Dragoon 's Great Rage.
4/19 21:10:19.076  Dragoon gains 60 Rage from Dragoon 's Mighty Rage.
4/19 21:10:19.076  Dragoon gains 60 Rage from Dragoon 's Rage.
    """
    lines = lines.split('\n')
    for line in lines:
        parse_line(line)
    for pot in ['Great Rage Potion', 'Mighty Rage Potion', 'Rage Potion']:
        assert player['Dragoon'][pot] == 1

def test_tea_with_sugar_line():
    lines = """
4/21 21:01:38.861  Psykhe 's Tea with Sugar heals Psykhe for 1613.
4/21 21:22:41.023  Shumy gains 1209 Mana from Shumy 's Tea with Sugar.
    """
    lines = lines.split('\n')
    for line in lines:
        parse_line(line)
    assert player['Psykhe']['Tea with Sugar'] == 1
    assert player['Shumy']['Tea with Sugar'] == 0

def test_gains_consumable_line():
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
        parse_line(line)
    assert player['Rando']['Greater Arcane Elixir'] == 1
    assert player['Rando']['Arcane Elixir'] == 1
    assert player['Rando']['Elixir of Fortitude'] == 1
    assert player['Rando']['Increased Stamina'] == 0
    assert player['Psykhe']['Shadow Protection'] == 1
    assert player['Axe']['Gift of Arthas'] == 1
    assert player['Unholy Axe']['Gift of Arthas'] == 0

def test_buff_line():
    lines = """
6/16 21:32:19.790  Niviri gains Prayer of Shadow Protection (1).
6/16 21:32:19.790  Ikoretta gains Prayer of Shadow Protection (1).
6/16 21:32:19.859  Samet gains Prayer of Shadow Protection (1).
6/16 21:32:22.078  Charmia gains Prayer of Shadow Protection (1).
    """
    lines = lines.split('\n')
    for line in lines:
        parse_line(line)

    for name in {'Niviri', 'Ikoretta', 'Samet', 'Charmia'}:
        assert name in player_detect

def test_dies_line():
    lines = """
4/5 20:11:49.164  Nilia dies.
4/5 20:11:49.653  Blackwing Mage dies.
4/5 20:11:52.882  Blackwing Legionnaire dies.
    """
    lines = lines.split('\n')
    for line in lines:
        parse_line(line)
    assert death_count['Nilia'] == 1
    assert death_count['Blackwing Mage'] == 0

def test_healpot_line():
    lines = """
4/5 20:46:53.177  Macc 's Healing Potion heals Macc for 1628.
4/5 20:57:27.357  Srj 's Healing Potion critically heals Srj for 2173.
    """
    lines = lines.split('\n')
    for line in lines:
        parse_line(line)
    assert player['Macc']['Healing Potion - Major'] == 1
    assert player['Srj']['Healing Potion - Major'] == 1

def test_manapot_line():
    lines = """
4/5 22:42:46.277  Ikoretta gains 1787 Mana from Ikoretta 's Restore Mana.
4/5 22:43:16.765  Smahingbolt gains 1967 Mana from Smahingbolt 's Restore Mana.
4/5 22:50:51.341  Magikal gains 1550 Mana from Magikal 's Restore Mana.
    """
    lines = lines.split('\n')
    for line in lines:
        parse_line(line)
    assert player['Ikoretta']['Mana Potion - Major'] == 1
    assert player['Smahingbolt']['Mana Potion - Major'] == 1
    assert player['Magikal']['Mana Potion - Major'] == 1

def test_manarune_line():
    lines = """
4/5 22:56:14.149  Ionize gains 1233 Mana from Ionize 's Dark Rune.
4/5 22:56:14.151  Ionize 's Dark Rune crits Ionize for 1140 Shadow damage.
4/5 20:10:47.164  Getterfour gains 1394 Mana from Getterfour 's Demonic Rune.
4/5 20:10:47.164  Getterfour 's Demonic Rune hits Getterfour for 653 Shadow damage.
4/5 20:10:54.738  Badmanaz gains 1499 Mana from Badmanaz 's Demonic Rune.
4/5 20:10:54.738  Badmanaz 's Demonic Rune hits Badmanaz for 858 Shadow damage. (286 resisted)
    """
    lines = lines.split('\n')
    for line in lines:
        parse_line(line)
    assert player['Getterfour']['Demonic Rune'] == 1
    assert player['Ionize']['Dark Rune'] == 1
    assert player['Badmanaz']['Demonic Rune'] == 1

def test_begins_to_cast_line():
    lines = """
10/15 20:25:14.239  Dregoth begins to cast Shadow Bolt.
10/15 20:25:14.437  Smahingbolt begins to cast Multi-Shot.
10/15 20:25:14.437  Churka begins to cast Frostbolt.
4/5 22:33:29.909  Hammerlammy begins to cast Consecrated Weapon.
4/14 20:23:52.580  Nethrion begins to cast Consecrated Weapon.
4/14 20:23:57.766  Nethrion begins to cast Consecrated Weapon.
4/14 20:23:58.871  Repe begins to cast Consecrated Weapon.
4/12 20:11:17.188  Bruceweed begins to cast Kreeg's Stout Beatdown.
4/12 20:11:18.129  Bruceweed is afflicted by Kreeg's Stout Beatdown (1).
4/12 20:16:37.168  Kreeg's Stout Beatdown fades from Bruceweed.
4/12 20:21:32.488  Bruceweed begins to cast Kreeg's Stout Beatdown.
4/12 20:21:33.432  Bruceweed is afflicted by Kreeg's Stout Beatdown (1).
4/12 20:36:33.440  Kreeg's Stout Beatdown fades from Bruceweed.
4/12 21:03:59.459  Bruceweed begins to cast Kreeg's Stout Beatdown.
4/12 21:04:00.483  Bruceweed is afflicted by Kreeg's Stout Beatdown (1).
    """
    lines = lines.split('\n')
    for line in lines:
        parse_line(line)
    assert player['Hammerlammy']['Consecrated Sharpening Stone'] == 1
    assert player['Nethrion']['Consecrated Sharpening Stone'] == 2
    assert player['Bruceweed']["Kreeg's Stout Beatdown"] == 3

def test_casts_consumable_line():
    lines = """
6/28 22:16:50.836  Faradin casts Advanced Target Dummy.
4/14 21:16:25.160  Psykhe casts Strong Anti-Venom on Psykhe.
4/14 21:15:01.099  Psykhe casts Powerful Anti-Venom on Psykhe.
4/13 22:19:00.971  Doombabe casts Cure Ailments on Doombabe.
4/13 22:19:00.971  Doombabe casts Cure Ailments on Doombabe.
4/14 21:04:16.502  Samain casts Cure Ailments on Samain.
    """
    lines = lines.split('\n')
    for line in lines:
        parse_line(line)
    assert player['Faradin']["Advanced Target Dummy"] == 1
    assert player['Psykhe']["Powerful Anti-Venom"] == 1
    assert player['Doombabe']["Jungle Remedy"] == 2
