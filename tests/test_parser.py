import pytest
import io


from melbalabs.summarize_consumes.main import parse_line
from melbalabs.summarize_consumes.main import create_app
from melbalabs.summarize_consumes.main import NAME2ITEMID

from melbalabs.summarize_consumes.grammar import grammar


@pytest.fixture
def app():
    return create_app(expert_log_unparsed_lines=True)




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
        assert app.player['Dragoon'][pot] == 1

def test_tea_with_sugar_line(app):
    lines = """
4/21 21:01:38.861  Psykhe 's Tea with Sugar heals Psykhe for 1613.
4/21 21:01:38.861  Psykhe 's Tea with Sugar critically heals Psykhe for 1613.
4/21 21:22:41.023  Shumy gains 1209 Mana from Shumy 's Tea with Sugar.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert app.player['Psykhe']['Tea with Sugar'] == 2
    assert app.player['Shumy']['Tea with Sugar'] == 0

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
    assert app.player['Rando']['Greater Arcane Elixir'] == 1
    assert app.player['Rando']['Arcane Elixir'] == 1
    assert app.player['Rando']['Elixir of Fortitude'] == 1
    assert app.player['Rando']['Increased Stamina'] == 0
    assert app.player['Psykhe']['Shadow Protection'] == 1
    assert app.player['Axe']['Gift of Arthas'] == 1
    assert app.player['Unholy Axe']['Gift of Arthas'] == 1

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
        assert name in app.player_detect

def test_dies_line(app):
    lines = """
4/5 20:11:49.164  Nilia dies.
4/5 20:11:49.653  Blackwing Mage dies.
4/5 20:11:52.882  Blackwing Legionnaire dies.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert app.death_count['Nilia'] == 1
    assert app.death_count['Blackwing Mage'] == 1

def test_healpot_line(app):
    lines = """
4/5 20:46:53.177  Macc 's Healing Potion heals Macc for 1628.
4/5 20:57:27.357  Srj 's Healing Potion critically heals Srj for 2173.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert app.player['Macc']['Healing Potion - Major'] == 1
    assert app.player['Srj']['Healing Potion - Major'] == 1

def test_manapot_line(app):
    lines = """
4/5 22:42:46.277  Ikoretta gains 1787 Mana from Ikoretta 's Restore Mana.
4/5 22:43:16.765  Smahingbolt gains 1967 Mana from Smahingbolt 's Restore Mana.
4/5 22:50:51.341  Magikal gains 1550 Mana from Magikal 's Restore Mana.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert app.player['Ikoretta']['Mana Potion - Major'] == 1
    assert app.player['Smahingbolt']['Mana Potion - Major'] == 1
    assert app.player['Magikal']['Mana Potion - Major'] == 1

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
    assert app.player['Getterfour']['Demonic Rune'] == 1
    assert app.player['Ionize']['Dark Rune'] == 1
    assert app.player['Badmanaz']['Demonic Rune'] == 1

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
    assert app.player['Hammerlammy']['Consecrated Sharpening Stone'] == 1
    assert app.player['Nethrion']['Consecrated Sharpening Stone'] == 2
    assert app.player['Bruceweed']["Kreeg's Stout Beatdown"] == 3

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
    assert app.player['Faradin']["Advanced Target Dummy"] == 1
    assert app.player['Psykhe']["Powerful Anti-Venom"] == 1
    assert app.player['Doombabe']["Jungle Remedy"] == 2

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
    assert app.player['Getterfour']["Dragonbreath Chili"] == 2
    assert app.player['Srj']["Dragonbreath Chili"] == 1
    assert app.player['Abstractz']["Goblin Sapper Charge"] == 1
    assert match == 8

def test_consolidated_line(app):
    lines = """
10/11 20:40:42.226  CONSOLIDATED: PET: 11.10.23 20:40:36&Arzetlam&Deathknight Understudy
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
10/11 20:40:42.226  CONSOLIDATED: PET: 11.10.23 20:40:36&Arzetlam&Deathknight Understudy{LOOT: 24.05.23 21:14:39&Doombabe receives item: |cffffffff|Hitem:6265:0:0:0|h[Soul Shard]|h|rx1.
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    assert app.pet_detect['Khuujhom'] == 'Doombabe'
    assert app.player_detect['Doombabe'] == {'pet: Khuujhom'}

    assert app.pet_detect['Deathknight Understudy'] == 'Arzetlam'
    assert app.player_detect['Arzetlam'] == {'pet: Deathknight Understudy'}
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
4/14 21:49:18.451  Maexxna 's Poison Shock hits Jaekta for 270 Nature damage. (481 resisted) (1176 absorbed)
4/14 21:49:18.451  Maexxna 's Poison Shock hits Jaekta for 270 Nature damage. (1176 absorbed)
4/14 21:49:18.451  Maexxna 's Poison Shock hits Jaekta for 270 Nature damage. (481 resisted)
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    assert match == 4

def test_hits_line2(app):
    lines = """
10/15 20:10:30.145  Jaekta hits Core Hound for 1. (glancing) (11 resisted) (189 absorbed)
10/15 20:10:30.145  Jaekta hits Core Hound for 1. (glancing) (11 resisted)
10/15 20:10:30.145  Jaekta hits Core Hound for 1. (glancing) (189 absorbed)
10/15 20:10:30.145  Jaekta hits Core Hound for 1. (11 resisted) (189 absorbed)
10/15 20:10:30.145  Jaekta hits Core Hound for 1. (189 absorbed)
10/15 20:10:30.145  Jaekta hits Core Hound for 1.
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        if len(line) > 10:
            app.parser.parse(line)
        match += parse_line(app, line)
    assert match == 6


def test_ktfrostbolt(app):
    lines = """
9/28 22:50:37.695  Kel'Thuzad begins to cast Frostbolt.
9/28 22:50:38.406  Mupsi 's Kick crits Kel'Thuzad for 132.
9/28 22:50:24.408  Melevolence 's Pummel was parried by Kel'Thuzad.
9/28 22:50:37.695  Kel'Thuzad begins to cast Frostbolt.
9/28 22:52:56.103  Srj 's Kick hits Kel'Thuzad for 66.
9/28 22:52:27.732  Jaekta 's Pummel hits Kel'Thuzad for 17.
9/28 22:52:51.129  Psykhe 's Shield Bash hits Kel'Thuzad for 33.
10/26 21:41:39.007  Kel'Thuzad 's Frostbolt hits Jaekta for 4379 Frost damage. (3063 absorbed)
10/26 21:41:39.007  Kel'Thuzad 's Frostbolt hits Jaekta for 3000 Frost damage.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    # 2 synthetic newlines
    # ignore the small frostbolt
    assert len(app.kt_frostbolt.log) == 10


def test_kt_frostblast(app):
    lines = """
9/28 22:52:03.404  Bloxie is afflicted by Frost Blast (1).
9/28 22:52:03.404  Dyrachyo is afflicted by Frost Blast (1).
9/28 22:52:03.404  Killanime is afflicted by Frost Blast (1).
9/28 22:52:03.404  Melevolence is afflicted by Frost Blast (1).
9/28 22:52:03.414  Djune is afflicted by Frost Blast (1).
9/28 22:52:04.449  Kel'Thuzad 's Frost Blast is absorbed by Djune.
9/28 22:52:04.449  Kel'Thuzad 's Frost Blast hits Melevolence for 1315 Frost damage.
9/28 22:52:04.449  Kel'Thuzad 's Frost Blast hits Killanime for 1605 Frost damage.
9/28 22:52:04.449  Kel'Thuzad 's Frost Blast hits Dyrachyo for 1546 Frost damage.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert len(app.kt_frostblast.log) == 9

def test_kt_shadowfissure(app):
    lines = """
10/19 22:27:40.741  Kel'Thuzad casts Shadow Fissure.
10/19 22:27:43.799  Shadow Fissure 's Void Blast hits Shumy for 103074 Shadow damage. (34357 resisted)
10/19 22:28:01.739  Kel'Thuzad casts Shadow Fissure.
10/19 22:28:21.892  Kel'Thuzad casts Shadow Fissure.
10/19 22:28:38.946  Kel'Thuzad casts Shadow Fissure.
10/19 22:28:42.004  Shadow Fissure 's Void Blast hits Windfurytotm for 127456 Shadow damage.
10/19 22:28:42.004  Shadow Fissure 's Void Blast hits Everglow for 102705 Shadow damage.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert len(app.kt_shadowfissure.log) == 7


def test_huhuran(app):
    lines = """
10/6 21:05:31.480  Princess Huhuran gains Frenzy (1).
10/6 21:05:32.460  Princess Huhuran 's Frenzy is removed.
10/6 21:05:32.460  Berserkss casts Tranquilizing Shot on Princess Huhuran.
10/6 21:05:50.787  Princess Huhuran gains Frenzy (1).
10/6 21:05:53.500  Princess Huhuran 's Frenzy is removed.
10/6 21:05:53.500  Chan casts Tranquilizing Shot on Princess Huhuran.
10/6 21:05:53.772  Hrin casts Tranquilizing Shot on Princess Huhuran.
10/6 21:06:05.304  Princess Huhuran gains Frenzy (1).
10/6 21:06:06.412  Princess Huhuran 's Frenzy is removed.
10/6 21:06:06.412  Berserkss casts Tranquilizing Shot on Princess Huhuran.
10/6 21:06:08.239  Srj casts Death by Peasant.
10/6 21:06:08.242  Princess Huhuran gains Berserk (1).
10/6 21:06:09.376  Rhudaur casts Death by Peasant.
10/6 21:06:09.376  Jaekta casts Death by Peasant.
10/6 21:06:10.027  Psykhe casts Death by Peasant.
10/6 21:06:14.089  Killanime casts Death by Peasant.
10/6 21:06:16.497  Iniri casts Death by Peasant.
4/13 21:11:02.121  Princess Huhuran dies.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert len(app.huhuran.log) == 18

def test_beamchain(app):
    lines = """
9/8 23:07:23.048  Eye of C'Thun 's Eye Beam was resisted by Getterfour.
9/8 23:07:23.048  Eye of C'Thun 's Eye Beam was resisted by Getterfour.
9/8 23:21:11.776  Eye of C'Thun 's Eye Beam is absorbed by Shendelzare.
9/8 23:23:32.892  Eye of C'Thun 's Eye Beam hits Killanime for 2918 Nature damage.

9/20 22:38:44.757  Sir Zeliek 's Holy Wrath was resisted by Charmia.
9/20 22:38:44.757  Sir Zeliek 's Holy Wrath was resisted by Charmia.
9/20 22:51:04.622  Sir Zeliek 's Holy Wrath is absorbed by Exeggute.
9/20 22:51:04.622  Sir Zeliek 's Holy Wrath is absorbed by Exeggute.
9/20 22:51:04.622  Sir Zeliek 's Holy Wrath is absorbed by Exeggute.
9/20 22:51:04.622  Sir Zeliek 's Holy Wrath is absorbed by Exeggute.
9/20 23:06:17.787  Sir Zeliek 's Holy Wrath hits Obbi for 477 Holy damage.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert len(app.cthun_chain.log) == 4
    assert len(app.fourhm_chain.log) == 7

    output = io.StringIO()
    app.cthun_chain.print(output)
    app.fourhm_chain.print(output)
    assert output.getvalue() == "\n\nC'Thun Chain Log (2+)\n\n   9/8 23:07:23.048  Eye of C'Thun 's Eye Beam was resisted by Getterfour.\n   9/8 23:07:23.048  Eye of C'Thun 's Eye Beam was resisted by Getterfour.\n\n\n4HM Zeliek Chain Log (4+)\n\n   9/20 22:51:04.622  Sir Zeliek 's Holy Wrath is absorbed by Exeggute.\n   9/20 22:51:04.622  Sir Zeliek 's Holy Wrath is absorbed by Exeggute.\n   9/20 22:51:04.622  Sir Zeliek 's Holy Wrath is absorbed by Exeggute.\n   9/20 22:51:04.622  Sir Zeliek 's Holy Wrath is absorbed by Exeggute.\n"


def test_suffers_line(app):
    lines = """
10/20 20:04:05.389  Anubisath Sentinel suffers 60 Nature damage from Jaekta 's Potent Venom.
10/20 20:04:05.389  Anubisath Sentinel suffers 287 Shadow damage from Rossol 's Shadow Word: Pain.
10/20 20:04:05.389  Anubisath Sentinel suffers 260 Shadow damage from Dregoth 's Corruption.

4/19 20:50:05.344  Echetawa suffers 90 Fire damage from Death Talon Hatcher 's Growing Flames. (40 absorbed)
4/19 20:50:07.253  Alotofdamage suffers 30 Fire damage from Death Talon Hatcher 's Growing Flames. (100 absorbed)
4/19 20:50:07.267  Axehole suffers 44 Fire damage from Death Talon Hatcher 's Growing Flames. (73 absorbed)

10/20 20:04:30.879  Ridea suffers 15 Fire damage from Ridea 's Fireball. (5 resisted)
10/20 20:06:25.658  Shrimpshark suffers 89 Fire damage from Shrimpshark 's Ignite. (89 resisted)
10/20 20:06:36.007  Ridea suffers 15 Fire damage from Ridea 's Fireball. (5 resisted)
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    assert match == 9


def test_nef_corrupted_healing(app):
    lines = """
10/14 22:02:40.403  Psykhe absorbs Jarnp 's Corrupted Healing.
10/14 22:02:41.443  Psykhe absorbs Jarnp 's Corrupted Healing.
10/14 22:02:42.457  Psykhe suffers 315 Shadow damage from Jarnp 's Corrupted Healing.
10/14 22:02:43.366  Psykhe suffers 315 Shadow damage from Jarnp 's Corrupted Healing.
5/6 22:14:32.515  Arzetlam 's Corrupted Healing is absorbed by Jaekta.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert len(app.nef_corrupted_healing.log) == 5

def test_gluth(app):
    lines = """

9/21 22:59:44.495  Gluth 's Decimate hits Mikkasa for 5266.
9/21 22:59:44.495  Gluth 's Decimate hits Psykhe for 6887.
9/21 22:59:44.495  Gluth 's Decimate hits Shumy for 5358.

9/21 22:59:52.517  Hrin casts Tranquilizing Shot on Gluth.
9/21 23:00:03.082  Smahingbolt casts Tranquilizing Shot on Gluth.
9/21 23:00:03.673  Berserkss casts Tranquilizing Shot on Gluth.
9/21 23:00:12.698  Hrin casts Tranquilizing Shot on Gluth.
9/21 23:00:22.440  Yis casts Tranquilizing Shot on Gluth.

9/21 22:58:39.978  Gluth gains Frenzy (1).

9/21 23:00:42.334  Gluth 's Frenzy is removed.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert len(app.gluth.log) == 10

def test_consumable_report(app):
    app.player['Psykhe']['Flask of the Titans'] = 3
    app.player['Psykhe']['Elixir of the Mongoose'] = 3
    app.player['Psykhe']['Rage of Ages (ROIDS)'] = 3

    output = io.StringIO()
    app.pricedb.data[NAME2ITEMID['Flask of the Titans']] = 3000000
    app.pricedb.data[NAME2ITEMID['Elixir of the Mongoose']] = 30000
    app.pricedb.data[NAME2ITEMID['Scorpok Pincer']] = 1
    app.pricedb.data[NAME2ITEMID['Blasted Boar Lung']] = 2
    app.pricedb.data[NAME2ITEMID['Snickerfang Jowl']] = 3
    app.print_consumables.print(output)
    assert output.getvalue() == 'Psykhe deaths:0\n   Elixir of the Mongoose 3   (9g)\n   Flask of the Titans 3   (900g)\n   Rage of Ages (ROIDS) 3   (42c)\n\n   total spent: 909g 42c\n'


def test_rejuv_pot(app):
    lines = """
4/14 21:05:17.903  Sebben gains 1676 Mana from Sebben 's Rejuvenation Potion.
4/14 21:05:17.903  Sebben 's Rejuvenation Potion heals Sebben for 1480.
4/14 22:19:20.209  Sebben gains 1558 Mana from Sebben 's Rejuvenation Potion.
4/14 22:19:20.209  Sebben 's Rejuvenation Potion heals Sebben for 1584.
4/14 22:19:22.130  Arzetlam gains 1568 Mana from Arzetlam 's Rejuvenation Potion.
4/14 22:19:22.130  Arzetlam 's Rejuvenation Potion heals Arzetlam for 1482.
4/14 23:19:29.030  Sebben gains 1548 Mana from Sebben 's Rejuvenation Potion.
4/14 23:19:29.030  Sebben 's Rejuvenation Potion heals Sebben for 1497.
4/14 23:19:29.030  Psykhe 's Rejuvenation Potion heals Psykhe for 497.
    """
    lines = lines.splitlines(keepends=True)
    for line in lines:
        parse_line(app, line)
    assert app.player['Sebben']['Rejuvenation Potion - Major'] == 3
    assert app.player['Arzetlam']['Rejuvenation Potion - Major'] == 1
    assert app.player['Psykhe']['Rejuvenation Potion - Major'] == 0
    assert app.player['Psykhe']['Rejuvenation Potion - Minor'] == 1

def test_fades_line(app):
    lines = """
10/28 20:00:57.846  Weakened Soul fades from Bananaheal.
10/28 20:01:41.041  Spirit of Zandalar fades from Shrimpshark.
10/28 20:01:53.689  Stun fades from Everglow.
10/28 20:02:03.456  Rallying Cry of the Dragonslayer fades from Mangokiwi.
10/28 20:02:05.192  Arcane Intellect fades from Teldelar.
10/28 20:02:05.192  Arcane Intellect fades from Daenshoo.
10/28 20:02:13.806  Mark of the Wild fades from Charmia.
10/28 20:02:13.961  Mark of the Wild fades from Psykhe.
10/28 20:02:13.961  Mark of the Wild fades from Jaekta.
10/28 20:02:32.827  Rallying Cry of the Dragonslayer fades from Sunor.
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    assert match == 10


def test_slain_line(app):
    lines = """
10/28 20:12:40.079  Blackwing Mage is slain by Gorkagoth!
10/28 20:12:41.886  Blackwing Mage is slain by Charmia!
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    assert match == 2

def test_creates_line(app):
    lines = """
10/29 19:44:43.785  Tovenares creates Conjured Sparkling Water.
10/29 19:44:54.085  Tovenares creates Mana Ruby.
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    assert match == 2

def test_is_killed_line(app):
    lines = """
4/28 14:28:45.871  Gurubashi Bat Rider is killed by Unstable Concoction.
4/28 15:04:48.311  Lenato is killed by Divine Intervention.
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    assert match == 2

def test_gains_energy_line(app):
    lines = """
10/29 19:44:41.898  Syjlas gains 12 Energy from Syjlas 's Quel'dorei Meditation.
10/29 19:44:42.941  Syjlas gains 12 Energy from Syjlas 's Quel'dorei Meditation.
10/29 19:44:43.965  Syjlas gains 12 Energy from Syjlas 's Quel'dorei Meditation.
10/29 19:44:44.933  Syjlas gains 12 Energy from Syjlas 's Quel'dorei Meditation.
10/29 19:44:45.926  Syjlas gains 12 Energy from Syjlas 's Quel'dorei Meditation.
    """
    lines = lines.splitlines(keepends=True)
    match = 0
    for line in lines:
        match += parse_line(app, line)
    assert match == 5


