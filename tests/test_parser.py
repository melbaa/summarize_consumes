import pytest

from melbalabs.summarize_consumes.main import player
from melbalabs.summarize_consumes.main import player_detect
from melbalabs.summarize_consumes.main import death_count
from melbalabs.summarize_consumes.main import pet_detect
from melbalabs.summarize_consumes.main import kt_frostbolt2

from melbalabs.summarize_consumes.main import parse_line
from melbalabs.summarize_consumes.main import create_app
from melbalabs.summarize_consumes.grammar import grammar


@pytest.fixture
def app():
    return create_app(expert_log_unparsed_lines=True)


def test_rage_consumable_line(app):
    lines = """
4/14 13:55:49.949  Jaekta gains 10 Rage from Jaekta 's Berserker Rage Effect.
4/19 21:10:19.076  Dragoon gains 60 Rage from Dragoon 's Great Rage.
4/19 21:10:19.076  Dragoon gains 60 Rage from Dragoon 's Mighty Rage.
4/19 21:10:19.076  Dragoon gains 60 Rage from Dragoon 's Rage.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    for pot in ['Great Rage Potion', 'Mighty Rage Potion', 'Rage Potion']:
        assert player['Dragoon'][pot] == 1

def test_tea_with_sugar_line(app):
    lines = """
4/21 21:01:38.861  Psykhe 's Tea with Sugar heals Psykhe for 1613.
4/21 21:22:41.023  Shumy gains 1209 Mana from Shumy 's Tea with Sugar.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert player['Psykhe']['Tea with Sugar'] == 1
    assert player['Shumy']['Tea with Sugar'] == 0

def test_gains_consumable_line(app):
    lines = """
4/20 20:29:51.707  Rando gains Greater Arcane Elixir (1).
4/14 21:56:51.221  Rando gains Arcane Elixir (1).
4/14 21:56:51.221  Rando gains Health II (1).
10/11 23:37:59.079  Psykhe gains Shadow Protection  (1).
10/11 23:37:59.079  Psykhe gains Shadow Protection (1).
10/11 20:44:17.813  Axe gains Gift of Arthas (1).
10/11 20:44:17.813  Unholy Axe gains Gift of Arthas (1).
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert player['Rando']['Greater Arcane Elixir'] == 1
    assert player['Rando']['Arcane Elixir'] == 1
    assert player['Rando']['Elixir of Fortitude'] == 1
    assert player['Rando']['Increased Stamina'] == 0
    assert player['Psykhe']['Shadow Protection'] == 1
    assert player['Axe']['Gift of Arthas'] == 1
    assert player['Unholy Axe']['Gift of Arthas'] == 0

def test_buff_line(app):
    lines = """
6/16 21:32:19.790  Niviri gains Prayer of Shadow Protection (1).
6/16 21:32:19.790  Ikoretta gains Prayer of Shadow Protection (1).
6/16 21:32:19.859  Samet gains Prayer of Shadow Protection (1).
6/16 21:32:22.078  Charmia gains Prayer of Shadow Protection (1).
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)

    for name in {'Niviri', 'Ikoretta', 'Samet', 'Charmia'}:
        assert name in player_detect

def test_dies_line(app):
    lines = """
4/5 20:11:49.164  Nilia dies.
4/5 20:11:49.653  Blackwing Mage dies.
4/5 20:11:52.882  Blackwing Legionnaire dies.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert death_count['Nilia'] == 1
    assert death_count['Blackwing Mage'] == 0

def test_healpot_line(app):
    lines = """
4/5 20:46:53.177  Macc 's Healing Potion heals Macc for 1628.
4/5 20:57:27.357  Srj 's Healing Potion critically heals Srj for 2173.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert player['Macc']['Healing Potion - Major'] == 1
    assert player['Srj']['Healing Potion - Major'] == 1

def test_manapot_line(app):
    lines = """
4/5 22:42:46.277  Ikoretta gains 1787 Mana from Ikoretta 's Restore Mana.
4/5 22:43:16.765  Smahingbolt gains 1967 Mana from Smahingbolt 's Restore Mana.
4/5 22:50:51.341  Magikal gains 1550 Mana from Magikal 's Restore Mana.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert player['Ikoretta']['Mana Potion - Major'] == 1
    assert player['Smahingbolt']['Mana Potion - Major'] == 1
    assert player['Magikal']['Mana Potion - Major'] == 1

def test_manarune_line(app):
    lines = """
4/5 22:56:14.149  Ionize gains 1233 Mana from Ionize 's Dark Rune.
4/5 22:56:14.151  Ionize 's Dark Rune crits Ionize for 1140 Shadow damage.
4/5 20:10:47.164  Getterfour gains 1394 Mana from Getterfour 's Demonic Rune.
4/5 20:10:47.164  Getterfour 's Demonic Rune hits Getterfour for 653 Shadow damage.
4/5 20:10:54.738  Badmanaz gains 1499 Mana from Badmanaz 's Demonic Rune.
4/5 20:10:54.738  Badmanaz 's Demonic Rune hits Badmanaz for 858 Shadow damage. (286 resisted)
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert player['Getterfour']['Demonic Rune'] == 1
    assert player['Ionize']['Dark Rune'] == 1
    assert player['Badmanaz']['Demonic Rune'] == 1

def test_begins_to_cast_line(app):
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
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert player['Hammerlammy']['Consecrated Sharpening Stone'] == 1
    assert player['Nethrion']['Consecrated Sharpening Stone'] == 2
    assert player['Bruceweed']["Kreeg's Stout Beatdown"] == 3

def test_casts_consumable_line(app):
    lines = """
6/28 22:16:50.836  Faradin casts Advanced Target Dummy.
4/14 21:16:25.160  Psykhe casts Strong Anti-Venom on Psykhe.
4/14 21:15:01.099  Psykhe casts Powerful Anti-Venom on Psykhe.
4/13 22:19:00.971  Doombabe casts Cure Ailments on Doombabe.
4/13 22:19:00.971  Doombabe casts Cure Ailments on Doombabe.
4/14 21:04:16.502  Samain casts Cure Ailments on Samain.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert player['Faradin']["Advanced Target Dummy"] == 1
    assert player['Psykhe']["Powerful Anti-Venom"] == 1
    assert player['Doombabe']["Jungle Remedy"] == 2

def test_hits_consumable_line(app):
    lines = """
4/19 20:15:15.532  Getterfour 's Dragonbreath Chili crits Razorgore the Untamed for 521 Fire damage. (173 resisted)
4/19 20:25:16.797  Getterfour 's Dragonbreath Chili hits Razorgore the Untamed for 591 Fire damage.
4/19 20:25:27.034  Srj 's Dragonbreath Chili was resisted by Razorgore the Untamed.
4/19 20:54:19.933  Abstractz 's Goblin Sapper Charge fails. Corrupted Red Whelp is immune.
4/19 20:54:19.933  Abstractz 's Goblin Sapper Charge crits Corrupted Green Whelp for 837 Fire damage.
4/19 20:54:19.933  Abstractz 's Goblin Sapper Charge crits Corrupted Bronze Whelp for 949 Fire damage.
4/19 20:54:19.933  Abstractz 's Goblin Sapper Charge crits Corrupted Green Whelp for 864 Fire damage.
4/19 20:54:19.933  Abstractz 's Goblin Sapper Charge hits Corrupted Bronze Whelp for 717 Fire damage.
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    assert player['Getterfour']["Dragonbreath Chili"] == 2
    assert player['Srj']["Dragonbreath Chili"] == 1
    assert player['Abstractz']["Goblin Sapper Charge"] == 1
    assert match == 8

def test_consolidated_line(app):
    lines = """
5/4 21:54:18.739  CONSOLIDATED: ZONE_INFO: 04.05.23 21:39:44&Naxxramas&3421{LOOT: 04.05.23 21:51:55&Doombabe receives item: |cffffffff|Hitem:6265:0:0:0|h[Soul Shard]|h|rx1.{PET: 04.05.23 21:51:55&Doombabe&Khuujhom
5/5 14:43:00.154  CONSOLIDATED: LOOT: 05.05.23 14:41:24&Melbaxd receives loot: |cff9d9d9d|Hitem:18223:0:0:0|h[Serrated Petal]|h|rx1.{LOOT: 05.05.23 14:41:26&Melbaxd receives loot: |cffffffff|Hitem:22529:0:0:0|h[Savage Frond]|h|rx4.{LOOT: 05.05.23 14:41:26&Melbaxd receives loot: |cff9d9d9d|Hitem:18224:0:0:0|h[Lasher Root]|h|rx1.{LOOT: 05.05.23 14:41:27&Melbaxd receives loot: |cff9d9d9d|Hitem:18222:0:0:0|h[Thorny Vine]|h|rx1.
5/24 14:24:11.633  CONSOLIDATED: LOOT: 24.05.23 14:21:19&Melbaxd receives loot: |cffffffff|Hitem:2450:0:0:0|h[Briarthorn]|h|rx1.{LOOT: 24.05.23 14:21:19&Melbaxd receives loot: |cffffffff|Hitem:4608:0:0:0|h[Raw Black Truffle]|h|rx1.{LOOT: 24.05.23 14:21:21&Melbaxd receives loot: |cff9d9d9d|Hitem:18223:0:0:0|h[Serrated Petal]|h|rx1.{LOOT: 24.05.23 14:21:21&Melbaxd receives loot: |cffffffff|Hitem:10286:0:0:0|h[Heart of the Wild]|h|rx1.
5/24 14:26:30.002  CONSOLIDATED: LOOT: 24.05.23 14:21:29&Melbaxd receives loot: |cffffffff|Hitem:4608:0:0:0|h[Raw Black Truffle]|h|rx1.{LOOT: 24.05.23 14:21:29&Melbaxd receives loot: |cffffffff|Hitem:13464:0:0:0|h[Golden Sansam]|h|rx1.{LOOT: 24.05.23 14:21:30&Melbaxd receives loot: |cffffffff|Hitem:3821:0:0:0|h[Goldthorn]|h|rx1.{LOOT: 24.05.23 14:21:30&Melbaxd receives loot: |cff9d9d9d|Hitem:18223:0:0:0|h[Serrated Petal]|h|rx1.
5/24 14:56:44.779  CONSOLIDATED: LOOT: 24.05.23 14:53:10&Melbaxd receives loot: |cff9d9d9d|Hitem:18222:0:0:0|h[Thorny Vine]|h|rx1.{LOOT: 24.05.23 14:53:12&Melbaxd receives loot: |cff9d9d9d|Hitem:18223:0:0:0|h[Serrated Petal]|h|rx1.{LOOT: 24.05.23 14:53:12&Melbaxd receives loot: |cffffffff|Hitem:4608:0:0:0|h[Raw Black Truffle]|h|rx1.{LOOT: 24.05.23 14:53:12&Melbaxd receives loot: |cffffffff|Hitem:10286:0:0:0|h[Heart of the Wild]|h|rx1.
5/24 20:08:13.217  CONSOLIDATED: LOOT: 24.05.23 20:01:36&Waken receives item: |cffffffff|Hitem:83004:0:0:0|h[Conjured Mana Orange]|h|rx20.{LOOT: 24.05.23 20:01:37&Waken receives item: |cffffffff|Hitem:83004:0:0:0|h[Conjured Mana Orange]|h|rx20.{LOOT: 24.05.23 20:01:45&Waken receives item: |cffffffff|Hitem:9421:0:0:0|h[Major Healthstone]|h|rx1.{LOOT: 24.05.23 20:02:05&Doombabe receives item: |cffffffff|Hitem:9421:0:0:0|h[Major Healthstone]|h|rx1.{PET: 24.05.23 20:02:15&Doombabe&Khuujhom
5/24 20:42:15.976  CONSOLIDATED: LOOT: 24.05.23 20:36:53&Need Roll - 45 for |cffffffff|Hitem:14047:0:0:0|h[Runecloth]|h|r by Waken{LOOT: 24.05.23 20:36:59&Doombabe receives item: |cffffffff|Hitem:6265:0:0:0|h[Soul Shard]|h|rx1.{PET: 24.05.23 20:36:59&Doombabe&Khuujhom{LOOT: 24.05.23 20:40:31&Psykhe receives item: |cffffffff|Hitem:9421:0:0:0|h[Major Healthstone]|h|rx1.{LOOT: 24.05.23 20:41:22&Smahingbolt receives loot: |cffffffff|Hitem:22708:0:0:0|h[Fate of Ramaladni]|h|rx1.
5/24 21:18:14.223  CONSOLIDATED: LOOT: 24.05.23 21:14:39&Doombabe receives item: |cffffffff|Hitem:6265:0:0:0|h[Soul Shard]|h|rx1.{PET: 24.05.23 21:14:39&Doombabe&Khuujhom
5/24 21:45:15.542  CONSOLIDATED: PET: 24.05.23 21:43:17&Doombabe&Khuujhom{LOOT: 24.05.23 21:43:53&Lod receives loot: |cff1eff00|Hitem:14489:0:0:0|h[Pattern: Frostweave Pants]|h|rx1.{LOOT: 24.05.23 21:43:53&Lod receives loot: |cffffffff|Hitem:15754:0:0:0|h[Pattern: Warbear Woolies]|h|rx1.
5/24 22:06:52.097  CONSOLIDATED: PET: 24.05.23 22:03:04&Doombabe&Khuujhom
5/24 22:41:47.934  CONSOLIDATED: LOOT: 24.05.23 22:40:17&Doombabe receives item: |cffffffff|Hitem:6265:0:0:0|h[Soul Shard]|h|rx1.{PET: 24.05.23 22:40:17&Doombabe&Khuujhom{LOOT: 24.05.23 22:40:36&Waken receives item: |cffffffff|Hitem:21177:0:0:0|h[Symbol of Kings]|h|rx20.{LOOT: 24.05.23 22:40:36&Waken receives item: |cffffffff|Hitem:21177:0:0:0|h[Symbol of Kings]|h|rx20.{LOOT: 24.05.23 22:40:37&Waken receives item: |cffffffff|Hitem:21177:0:0:0|h[Symbol of Kings]|h|rx20.
10/11 20:40:42.226  CONSOLIDATED: PET: 11.10.23 20:40:36&Arzetlam&Deathknight Understudy
10/11 20:40:42.226  CONSOLIDATED: PET: 11.10.23 20:40:36&Arzetlam&Deathknight Understudy{LOOT: 24.05.23 21:14:39&Doombabe receives item: |cffffffff|Hitem:6265:0:0:0|h[Soul Shard]|h|rx1.
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    assert pet_detect['Khuujhom'] == 'Doombabe'
    assert player_detect['Doombabe'] == 'pet: Khuujhom'

    assert pet_detect['Deathknight Understudy'] == 'Arzetlam'
    assert player_detect['Arzetlam'] == 'pet: Deathknight Understudy'
    assert match == 13

def test_combatant_info_line(app):
    lines = """
10/11 20:03:02.614  COMBATANT_INFO: 11.10.23 20:02:40&Loyola&PALADIN&Human&2&nil&Cold Embrace&Member&7&nil&nil&nil&nil&nil&nil&nil&21387:2584:0:0&18404:0:0:0&21391:0:0:0&3428:0:0:0&16958:0:0:0&19137:0:0:0&21390:2584:0:0&21388:1887:0:0&21618:1885:0:0&21623:2564:0:0&60006:0:0:0&19382:0:0:0&nil
10/11 20:03:02.614  COMBATANT_INFO: 11.10.23 20:02:40&Druindy&DRUID&Tauren&3&nil&Cold Embrace&Marauder&4&nil&nil&nil&nil&nil&nil&nil&22490:2591:0:0&23036:0:0:0&22491:0:0:0&51904:0:0:0&65021:928:0:0&21582:0:0:0&19385:2591:0:0&19437:911:0:0&21604:2566:0:0&22493:2617:0:0&19382:0:0:0&19140:0:0:0&nil
10/11 20:03:02.614  COMBATANT_INFO: 11.10.23 20:02:40&Loyola&PALADIN&Human&2&nil&Cold Embrace&Member&7&nil&nil&nil&nil&nil&nil&nil&21387:2584:0:0&18404:0:0:0&21391:0:0:0&3428:0:0:0&16958:0:0:0&19137:0:0:0&21390:2584:0:0&21388:1887:0:0&21618:1885:0:0&21623:2564:0:0&60006:0:0:0&19382:0:0:0&nil
10/11 20:03:02.614  COMBATANT_INFO: 11.10.23 20:02:40&Druindy&DRUID&Tauren&3&nil&Cold Embrace&Marauder&4&nil&nil&nil&nil&nil&nil&nil&22490:2591:0:0&23036:0:0:0&22491:0:0:0&51904:0:0:0&65021:928:0:0&21582:0:0:0&19385:2591:0:0&19437:911:0:0&21604:2566:0:0&22493:2617:0:0&19382:0:0:0&19140:0:0:0&nil
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    assert match == 4

def test_hits_line(app):
    lines = """
9/28 22:52:56.103  Srj 's Kick hits Kel'Thuzad for 66.
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    assert match == 1



def test_ktfrostbolt(app):
    kt_frostbolt2.log = []
    lines = """
9/28 22:50:37.695  Kel'Thuzad begins to cast Frostbolt.
9/28 22:50:38.406  Mupsi 's Kick crits Kel'Thuzad for 132.
9/28 22:50:24.408  Melevolence 's Pummel was parried by Kel'Thuzad.
9/28 22:50:37.695  Kel'Thuzad begins to cast Frostbolt.
9/28 22:52:56.103  Srj 's Kick hits Kel'Thuzad for 66.
9/28 22:52:27.732  Jaekta 's Pummel hits Kel'Thuzad for 17.
9/28 22:52:51.129  Psykhe 's Shield Bash hits Kel'Thuzad for 33.
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    # 2 synthetic newlines and all other lines
    assert len(kt_frostbolt2.log) == 9


def test_lark_whitespace():
    lines = """a .
a  .
a.
"""
    from lark import Lark
    parser = Lark(r"""

start: A_SPACE " " DOT
    | A " " DOT
    | A DOT

A_SPACE: /\w+ /
A: /\w+/
DOT: "."
%import common.WS
%ignore WS
""")
    lines = lines.splitlines(keepends=True)
    res1 = parser.parse(lines[0])
    assert res1.children[0] == 'a'
    assert res1.children[1] == '.'

    res2 = parser.parse(lines[1])
    assert res2.children[0] == 'a '
    assert res2.children[1] == '.'

    res3 = parser.parse(lines[2])
    assert res3.children[0] == 'a'
    assert res3.children[1] == '.'


@pytest.mark.skip('not using basic lexer; grammar too ambiguous for it')
def test_lark_basic_lexer():
    from lark import Lark

    lines = """4/21 21:01:38.861  Psykhe 's Tea with Sugar heals Psykhe for 1613.
"""
    lines = lines.splitlines(keepends=True)
    lark = Lark(grammar, parser=None, lexer='basic')
    # All tokens: print([t.name for t in self.lark.parser.lexer.tokens])
    for token in lark.lex(lines[0]):
        pass

def test_lark_contextual_lexer(app):
    lines = """4/21 21:01:38.861  Psykhe 's Tea with Sugar heals Psykhe for 1613.
"""
    lines = lines.splitlines(keepends=True)
    assert len(app.parser.parser.parser.parser.parse_table.states)


