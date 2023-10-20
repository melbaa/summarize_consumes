import argparse
import collections
import datetime
import io
import os
import re
import sys
import time
import webbrowser
import functools
import logging
from datetime import datetime as dt

import zipfile


import requests
import humanize
import lark


from melbalabs.summarize_consumes import grammar


LarkError = lark.LarkError

class App:
    pass


@functools.cache
def create_parser(grammar: str, debug):
    return lark.Lark(
        grammar,
        parser='lalr',
        debug=debug,
        # ambiguity='explicit',  # not in lalr
        strict=True,
    )


def create_app(expert_log_unparsed_lines):

    app = App()

    lark_debug = False
    if expert_log_unparsed_lines:
        lark.logger.setLevel(logging.DEBUG)
        lark_debug = True

    app.parser = create_parser(grammar=grammar.grammar, debug=lark_debug)


    if expert_log_unparsed_lines:
        app.unparsed_logger = UnparsedLogger(filename='unparsed.txt')
    else:
        app.unparsed_logger = NullLogger(filename='unparsed.txt')


    # player - consumable - count
    app.player = collections.defaultdict(lambda: collections.defaultdict(int))

    # player - consumable - unix_timestamp
    app.last_hit_cache = collections.defaultdict(lambda: collections.defaultdict(float))

    app.hits_consumable = HitsConsumable(player=app.player, last_hit_cache=app.last_hit_cache)
    app.kt_frostblast = KTFrostblast()
    app.kt_frostbolt = KTFrostbolt()
    app.kt_shadowfissure = KTShadowfissure()

    return app



def parse_ts2unixtime(timestamp):
    month, day, hour, minute, sec, ms = timestamp.children
    month = int(month)
    day = int(day)
    hour = int(hour)
    minute = int(minute)
    sec = int(sec)
    ms = int(ms)
    timestamp = dt(year=current_year, month=month, day=day, hour=hour, minute=minute, second=sec, tzinfo=datetime.timezone.utc)
    unixtime = timestamp.timestamp()  # seconds
    return unixtime


class HitsConsumable:


    COOLDOWNS = {
        'Dragonbreath Chili': 10 * 60,
        'Goblin Sapper Charge': 5 * 60,
    }

    def __init__(self, player, last_hit_cache):
        self.player = player
        self.last_hit_cache = last_hit_cache

    def update(self, name, consumable, timestamp):
        cooldown = self.COOLDOWNS[consumable]
        unixtime =  parse_ts2unixtime(timestamp)
        delta = unixtime - self.last_hit_cache[name][consumable]
        if delta >= cooldown:
            self.player[name][consumable] += 1
            self.last_hit_cache[name][consumable] = unixtime
        elif delta < 0:
            # probably a new year, will ignore for now
            raise RuntimeError('fixme')




RENAME_CONSUMABLE = {
    'Supreme Power': 'Flask of Supreme Power',
    'Distilled Wisdom': 'Flask of Distilled Wisdom',
    'Rage of Ages': 'Rage of Ages (ROIDS)',
    'Health II': 'Elixir of Fortitude',
    'Fury of the Bogling': 'Bogling Root',
    'Elixir of the Sages': '??? Elixir of the Sages ???',
    'Shadow Power': 'Elixir of Shadow Power',
    'Greater Firepower': 'Elixir of Greater Firepower',
    'Fire Power': 'Elixir of Firepower',
    'Greater Agility': 'Elixir of Greater Agility',
    'Spirit of the Boar': 'Lung Juice Cocktail',
    'Greater Armor': 'Elixir of Superior Defense',
    'Mana Regeneration': 'Mana Regeneration (food or mageblood)',
    'Free Action': 'Free Action Potion',
    'Frost Power': 'Elixir of Frost Power',
    'Nature Protection ': 'Nature Protection',
    'Shadow Protection ': 'Shadow Protection',
    'Holy Protection ': 'Holy Protection',
    '100 energy': 'Thistle Tea',
    'Sharpen Weapon - Critical': 'Elemental Sharpening Stone',
    'Consecrated Weapon': 'Consecrated Sharpening Stone',
    'Sharpen Blade V': 'Dense Sharpening Stone',
    'Enhance Blunt Weapon V': 'Dense Weighstone',
    'Cure Ailments': 'Jungle Remedy',
    'Stoneshield': '??? Lesser Stoneshield Potion ???',
    'Restoration': 'Restorative Potion',
    'Enlarge': 'Elixir of Giant Growth',
    'Greater Intellect': 'Elixir of Greater Intellect',
    'Infallible Mind': 'Infallible Mind (Cerebral Cortex Compound)',
    'Crystal Protection': 'Crystal Protection (Crystal Basilisk Spine)',
}


MELEE_INTERRUPT_SPELLS = {
    'Kick',
    'Pummel',
    'Shield Bash',
}


BEGINS_TO_CAST_CONSUMABLE = {
    "Brilliant Mana Oil",
    "Lesser Mana Oil",
    "Brilliant Wizard Oil",
    "Blessed Wizard Oil",
    "Wizard Oil",
    "Frost Oil",
    "Shadow Oil",
    "Dense Dynamite",
    "Solid Dynamite",
    "Sharpen Weapon - Critical",
    "Consecrated Weapon",
    "Iron Grenade",
    "Thorium Grenade",
    "Kreeg's Stout Beatdown",
    "Fire-toasted Bun",
    "Sharpen Blade V",
    "Enhance Blunt Weapon V",
    "Crystal Force",
}

CASTS_CONSUMABLE = {
    "Powerful Anti-Venom",
    "Strong Anti-Venom",
    "Cure Ailments",
    "Advanced Target Dummy",
}



def healpot_lookup(amount):
    # bigger ranges for rounding errors
    if 1049 <= amount <= 1751:
        return 'Healing Potion - Major'
    if 699 <= amount <= 901:
        return 'Healing Potion - Superior'
    if 454 <= amount <= 586:
        return 'Healing Potion - Greater'
    if 139 <= amount <= 181:
        return 'Healing Potion - Lesser'
    if 69 <= amount <= 91:
        return 'Healing Potion - Minor'
    return 'Healing Potion - unknown'




class NefCorruptedHealing:

    """
10/14 22:02:40.403  Psykhe absorbs Jarnp 's Corrupted Healing.
10/14 22:02:41.443  Psykhe absorbs Jarnp 's Corrupted Healing.
10/14 22:02:42.457  Psykhe suffers 315 Shadow damage from Jarnp 's Corrupted Healing.
10/14 22:02:43.366  Psykhe suffers 315 Shadow damage from Jarnp 's Corrupted Healing.
5/6 22:14:32.515  Arzetlam 's Corrupted Healing is absorbed by Jaekta.
    """
    def __init__(self):
        logname = 'Nefarian Priest Corrupted Healing'
        needles = [
            r"(\w+) absorbs (\w+) 's Corrupted Healing.",
            r"(\w+) suffers \d+ Shadow damage from (\w+) 's Corrupted Healing.",
            r"(\w+) 's Corrupted Healing is absorbed by (\w+).",
        ]
        self.parser = LogParser(logname, needles)

    def parse(self, line):
        return self.parser.parse(line)

    def print(self, output):
        return self.parser.print(output)




class Huhuran:
    def __init__(self):
        self.log = []
        self.found_huhuran = 0

    def print(self, output):
        if not self.found_huhuran: return
        if not self.log: return

        print("\n\nPrincess Huhuran Log", file=output)
        for line in self.log:
            print('  ', line, end='', file=output)

    def parse(self, line):
        if 'Death by Peasant' in line:
            self.log.append(line)
            return 1
        if 'Princess Huhuran dies' in line:
            self.log.append(line)
            self.found_huhuran = 1
            return 1
        if 'Princess Huhuran gains Frenzy' in line:
            self.log.append(line)
            self.found_huhuran = 1
            return 1
        if "Princess Huhuran 's Frenzy is removed." in line:
            self.log.append(line)
            self.found_huhuran = 1
            return 1
        if 'casts Tranquilizing Shot on Princess Huhuran' in line:
            self.log.append(line)
            self.found_huhuran = 1
            return 1
        if 'Princess Huhuran gains Berserk (1).' in line:
            self.log.append(line)
            self.found_huhuran = 1
            return 1
        if not self.found_huhuran and 'Princess Huhuran' in line:
            self.found_huhuran = 1
            return 1

class Gluth:
    def __init__(self):
        self.log = []
        self.boss_found = 0

    def print(self, output):
        if not self.boss_found: return
        if not self.log: return

        print("\n\nGluth Log", file=output)
        for line in self.log:
            print('  ', line, end='', file=output)

    def parse(self, line):
        """
9/21 22:59:43.807  Jaekta is afflicted by Mortal Wound (2).
9/21 22:59:53.950  Jaekta is afflicted by Mortal Wound (3).
9/21 23:00:03.947  Jaekta is afflicted by Mortal Wound (4).
9/21 23:00:13.870  Jaekta is afflicted by Mortal Wound (5).
9/21 23:00:24.074  Jaekta is afflicted by Mortal Wound (6).
9/21 23:00:34.043  Jaekta is afflicted by Mortal Wound (7).

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
        log_needles = [
            'Gluth dies',
            'Gluth gains Frenzy',
            "Gluth 's Frenzy is removed.",
            'casts Tranquilizing Shot on Gluth',
            "Gluth 's Decimate hits",
        ]
        for needle in log_needles:
            if needle in line:
                self.log.append(line)
                self.boss_found = 1
                return 1
        if not self.boss_found and 'Gluth' in line:
            self.boss_found = 1
            return 1




class BeamChain:
    def __init__(self, logname, beamname, chainsize):
        self.log = []
        self.last_ts = 0
        self.logname = logname
        self.beamname = beamname
        self.chainsize = chainsize  # report chains bigger than this

    def print(self, output):
        if not self.log: return

        do_once = False

        batch = []
        for line in self.log:
            if line == '\n':
                if len(batch) > self.chainsize:
                    if not do_once:
                        print(f"\n\n{self.logname}", file=output)
                        do_once = True
                    for batch_line in batch:
                        print('  ', batch_line, end='', file=output)
                batch = []
                batch.append(line)
            else:
                batch.append(line)

        if len(batch) > self.chainsize:
            for batch_line in batch:
                print('  ', batch_line, end='', file=output)



    def parse(self, line):
        """
9/8 23:23:30.876  Eye of C'Thun begins to cast Eye Beam.
9/8 23:23:32.892  Eye of C'Thun 's Eye Beam hits Killanime for 2918 Nature damage.
9/8 23:21:11.776  Eye of C'Thun 's Eye Beam is absorbed by Shendelzare.
9/8 23:07:23.048  Eye of C'Thun 's Eye Beam was resisted by Getterfour.

9/20 23:06:17.787  Sir Zeliek 's Holy Wrath hits Obbi for 477 Holy damage.
9/20 22:51:04.622  Sir Zeliek 's Holy Wrath is absorbed by Exeggute.
9/20 22:38:44.757  Sir Zeliek 's Holy Wrath was resisted by Charmia.
        """
        beamname = self.beamname
        if beamname in line:
            needle = rf"(\d+)/(\d+) (\d+):(\d+):(\d+).(\d+)  {beamname} "
            match = re.search(needle, line)
            cooldown = 2
            if match:
                groups = match.groups()
                month, day, hour, minute, sec, ms = int(groups[0]), int(groups[1]), int(groups[2]), int(groups[3]), int(groups[4]), int(groups[5])
                timestamp = dt(year=current_year, month=month, day=day, hour=hour, minute=minute, second=sec, tzinfo=datetime.timezone.utc)
                unixtime = timestamp.timestamp()
                delta = unixtime - self.last_ts
                if delta >= cooldown:
                    self.log.append('\n')
                    self.last_ts = unixtime
                self.log.append(line)
                return 1


class LogParser:
    # simple slow parser for individual lines with no context

    def __init__(self, logname, needles):
        self.log = []
        self.logname = logname
        self.needles = needles

    def parse(self, line):
        for needle in self.needles:
            match = re.search(needle, line)
            if match:
                self.log.append(line)
                return 1

    def print(self, output):
        if not self.log: return

        print(f"\n\n{self.logname}", file=output)
        for line in self.log:
            print('  ', line, end='', file=output)




def print_collected_log(section_name, log_list, output):
    if not log_list: return
    print(f"\n\n{section_name}", file=output)
    for line in log_list:
        print('  ', line, end='', file=output)
    return



class KTFrostbolt:
    def __init__(self):
        self.logname = 'KT Frostbolt Log'
        self.log = []
    def begins_to_cast(self, line):
        self.log.append('\n')
        self.log.append(line)
    def interrupt(self, line):
        self.log.append(line)
    def parry(self, line):
        line = "*** honorable mention *** " + line
        self.log.append(line)
    def print(self, output):
        print_collected_log(self.logname, self.log, output)

class KTFrostblast:
    def __init__(self):
        self.logname = 'KT Frost Blast Log'
        self.log = []
    def add(self, line):
        self.log.append(line)
    def print(self, output):
        print_collected_log(self.logname, self.log, output)

class KTShadowfissure:
    def __init__(self):
        self.logname = 'KT Shadow Fissure Log'
        self.log = []
    def add(self, line):
        self.log.append(line)
    def print(self, output):
        print_collected_log(self.logname, self.log, output)



class Techinfo:
    def __init__(self):
        self.time_start = time.time()
        self.logsize = 0
        self.linecount = 0
        self.skiplinecount = 0

    def get_file_size(self, filename):
        self.logsize = os.path.getsize(filename)

    def get_line_count(self, count):
        self.linecount = count

    def get_skipped_line_count(self, count):
        self.skiplinecount = count

    def print(self, output):
        time_end = time.time()
        time_delta = time_end - self.time_start
        print("\n\nTech", file=output)
        print('  ', f'log size {humanize.naturalsize(self.logsize)}', file=output)
        print('  ', f'log lines {self.linecount}', file=output)
        print('  ', f'skipped log lines {self.skiplinecount} ({(self.skiplinecount / self.linecount) * 100:.2f}%)', file=output)
        print('  ', f'processed in {time_delta:.2f} seconds. {self.linecount / time_delta:.2f} log lines/sec', file=output)



class UnparsedLogger:
    def __init__(self, filename):
        self.filename = filename
        self.buffer = io.StringIO()

    def log(self, line):
        print(line, end='', file=self.buffer)

    def flush(self):
        with open(self.filename, 'wb') as f:
            f.write(self.buffer.getvalue().encode('utf8'))

class NullLogger:
    def __init__(self, filename):
        pass
    def log(self, line):
        pass
    def flush(self):
        pass


current_year = datetime.datetime.now().year



# player - buff
player_detect = collections.defaultdict(str)

# pet -> owner
pet_detect = dict()

# name -> death count
death_count = collections.defaultdict(int)

nef_corrupted_healing = NefCorruptedHealing()
huhuran = Huhuran()
gluth = Gluth()
cthun_chain = BeamChain(logname="C'Thun Chain Log (2+)", beamname="Eye of C'Thun 's Eye Beam", chainsize=2)
fourhm_chain = BeamChain(logname="4HM Zeliek Chain Log (4+)", beamname="Sir Zeliek 's Holy Wrath", chainsize=4)
techinfo = Techinfo()

def parse_line(app, line):
    """
    returns True when a match is found, so we can stop trying different parsers
    """
    try:

        tree = app.parser.parse(line)
        timestamp = tree.children[0]
        subtree = tree.children[1]

        # inline some parsing to reduce funcalls
        # for same reason not using visitors to traverse the parse tree
        if subtree.data == 'gains_consumable_line':
            name = subtree.children[0].value
            consumable = subtree.children[1].value
            if consumable in RENAME_CONSUMABLE:
                consumable = RENAME_CONSUMABLE[consumable]
            app.player[name][consumable] += 1
            return True
        elif subtree.data == 'tea_with_sugar_line':
            name = subtree.children[0].value
            app.player[name]['Tea with Sugar'] += 1
            return True
        elif subtree.data == 'rage_consumable_line':
            name = subtree.children[0].value
            consumable = subtree.children[3].value
            consumable += ' Potion'
            app.player[name][consumable] += 1
            return True
        elif subtree.data == 'buff_line':
            name = subtree.children[0].value
            buff = subtree.children[1].value
            player_detect[name] = buff
            return True
        elif subtree.data == 'dies_line':
            name = subtree.children[0].value
            death_count[name] += 1
            return True
        elif subtree.data == 'healpot_line':
            name = subtree.children[0].value
            amount = int(subtree.children[-1].value)
            is_crit = subtree.children[1].type == 'HEALPOT_CRIT'
            if is_crit:
                amount = amount / 1.5
            consumable = healpot_lookup(amount)
            app.player[name][consumable] += 1
            return True
        elif subtree.data == 'manapot_line':
            name = subtree.children[0].value
            mana = int(subtree.children[1].value)
            consumable = 'Restore Mana (mana potion?)'
            if 1350 <= mana <= 2250:
                consumable = 'Mana Potion - Major'
            elif 900 <= mana <= 1500:
                consumable = 'Mana Potion - Superior'
            elif 700 <= mana <= 900:
                consumable = 'Mana Potion - Greater'
            elif 455 <= mana <= 585:
                consumable = 'Mana Potion - 455 to 585'
            elif 280 <= mana <= 360:
                consumable = 'Mana Potion - Lesser'
            elif 140 <= mana <= 180:
                consumable = 'Mana Potion - Minor'
            app.player[name][consumable] += 1
            return True
        elif subtree.data == 'manarune_line':
            name = subtree.children[0].value
            consumable = subtree.children[-1].value
            app.player[name][consumable] += 1
            return True
        elif subtree.data == 'begins_to_cast_line':
            name = subtree.children[0].value
            spellname = subtree.children[-1].value

            if spellname in BEGINS_TO_CAST_CONSUMABLE:
                consumable = spellname
                if consumable in RENAME_CONSUMABLE:
                    consumable = RENAME_CONSUMABLE[consumable]
                app.player[name][consumable] += 1

            if name == "Kel'Thuzad" and spellname == 'Frostbolt':
                app.kt_frostbolt.begins_to_cast(line)

            return True
        elif subtree.data == 'casts_line':
            name = subtree.children[0].value
            spellname = subtree.children[1].value

            if spellname in CASTS_CONSUMABLE:
                consumable = spellname
                if consumable in RENAME_CONSUMABLE:
                    consumable = RENAME_CONSUMABLE[consumable]
                app.player[name][consumable] += 1

            if name == "Kel'Thuzad" and spellname == "Shadow Fissure":
                app.kt_shadowfissure.add(line)

            return True
        elif subtree.data == 'combatant_info_line':
            return True
        elif subtree.data == 'consolidated_line':
            for entry in subtree.children[1:]:
                if entry.data == 'consolidated_pet':
                    name = entry.children[0].value
                    petname = entry.children[1].value
                    pet_detect[petname] = name
                    player_detect[name] = 'pet: ' + petname
                else:
                    # parse but ignore the other consolidated entries
                    pass
            return True
        elif subtree.data == 'hits_line':

            name = subtree.children[0].value
            spellname = subtree.children[1].value
            targetname = subtree.children[2].value

            if spellname in app.hits_consumable.COOLDOWNS:
                app.hits_consumable.update(name, spellname, timestamp)

            if spellname in MELEE_INTERRUPT_SPELLS and targetname == "Kel'Thuzad":
                app.kt_frostbolt.interrupt(line)

            if name == "Kel'Thuzad" and spellname == "Frost Blast":
                app.kt_frostblast.add(line)

            if name == "Shadow Fissure" and spellname == "Void Blast":
                app.kt_shadowfissure.add(line)

            return True
        elif subtree.data == 'parry_line':
            name = subtree.children[0].value
            spellname = subtree.children[1].value
            targetname = subtree.children[2].value

            if spellname in MELEE_INTERRUPT_SPELLS and targetname == "Kel'Thuzad":
                app.kt_frostbolt.parry(line)

            return True

        elif subtree.data == 'resist_line':
            name = subtree.children[0].value
            spellname = subtree.children[1].value
            targetname = subtree.children[2].value


            if spellname in app.hits_consumable.COOLDOWNS:
                app.hits_consumable.update(name, spellname, timestamp)

            return True
        elif subtree.data == 'fails_line':
            name = subtree.children[0].value
            spellname = subtree.children[1].value

            if spellname in app.hits_consumable.COOLDOWNS:
                app.hits_consumable.update(name, spellname, timestamp)

            return True
        elif subtree.data == 'afflicted_line':
            name = subtree.children[0].value
            spellname = subtree.children[1].value

            if spellname == "Frost Blast":
                app.kt_frostblast.add(line)

            return True
        elif subtree.data == 'absorbed_line':

            name = subtree.children[0].value
            spellname = subtree.children[1].value

            if name == "Kel'Thuzad" and spellname == "Frost Blast":
                app.kt_frostblast.add(line)
            return True



    except LarkError as e:
        # parse errors ignored to try different strategies
        pass
    return False

def parse_log(app, filename):

    techinfo.get_file_size(filename)

    with io.open(filename, encoding='utf8') as f:
        linecount = 0
        skiplinecount = 0
        for line in f:
            linecount += 1

            if parse_line(app, line):
                continue




            if nef_corrupted_healing.parse(line):
                continue
            if huhuran.parse(line):
                continue
            if cthun_chain.parse(line):
                continue
            if gluth.parse(line):
                continue
            if fourhm_chain.parse(line):
                continue

            skiplinecount += 1

            app.unparsed_logger.log(line)

        techinfo.get_line_count(linecount)
        techinfo.get_skipped_line_count(skiplinecount)

        app.unparsed_logger.flush()


def generate_output(app):

    output = io.StringIO()

    print("""Notes:
    - The report is generated using the combat log.
    - Jujus and many foods are not in the combat log, so they can't be easily counted.
    - Dragonbreath chili and goblin sappers have only "on hit" messages, so their usage is estimated based on timestamps and cooldowns.
    - Mageblood and some other mana consumes are "mana regeneration" in the combat log, can't tell them apart.

    """, file=output)


    # remove pets
    for pet in pet_detect:
        if pet in player_detect:
            del player_detect[pet]

    # add players detected
    for name in player_detect:
        app.player[name]


    names = sorted(app.player.keys())
    for name in names:
        print(name, f'deaths:{death_count[name]}', file=output)
        cons = app.player[name]
        consumables = sorted(cons.keys())
        for consumable in consumables:
            count = cons[consumable]
            print('  ', consumable, count, file=output)
        if not consumables:
            print('  ', '<nothing found>', file=output)

    nef_corrupted_healing.print(output)
    huhuran.print(output)
    cthun_chain.print(output)
    gluth.print(output)
    fourhm_chain.print(output)
    app.kt_shadowfissure.print(output)
    app.kt_frostbolt.print(output)
    app.kt_frostblast.print(output)

    print(f"\n\nPets", file=output)
    for pet in pet_detect:
        print('  ', pet, 'owned by', pet_detect[pet], file=output)

    techinfo.print(output)

    print(output.getvalue())
    return output


def get_user_input():
    parser = argparse.ArgumentParser()
    parser.add_argument('logpath', help='path to WoWCombatLog.txt')
    parser.add_argument('--pastebin', action='store_true', help='upload result to a pastebin and return the url')
    parser.add_argument('--open-browser', action='store_true', help='used with --pastebin. open the pastebin url with your browser')

    parser.add_argument('--expert-log-unparsed-lines', action='store_true', help='create an unparsed.txt with everything that was not parsed')
    args = parser.parse_args()

    return args


def upload_pastebin(output):
    data = output.getvalue()

    username, password = 'summarize_consumes', 'summarize_consumes'
    auth = requests.auth.HTTPBasicAuth(username, password)
    data = output.getvalue().encode('utf8')
    response = requests.post(
        url='http://ix.io',
        files={'f:1': data},
        auth=auth,
        timeout=30,
    )

    print(response.text)
    if 'already exists' in response.text:
        print("didn't get a new url")
        import pdb;pdb.set_trace()
        raise RuntimeError('no url')

    url = response.text.strip().split('\n')[-1]
    return url


def open_browser(url):
    print(f'opening browser with {url}')
    webbrowser.open(url)





def main():

    args = get_user_input()

    app = create_app(
        expert_log_unparsed_lines=args.expert_log_unparsed_lines,
    )

    parse_log(app, filename=args.logpath)

    output = generate_output(app)

    if not args.pastebin: return
    url = upload_pastebin(output)

    if not args.open_browser: return
    open_browser(url)


if __name__ == '__main__':
    main()
