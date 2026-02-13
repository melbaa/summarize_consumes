import argparse
import collections
import csv
import dataclasses
import datetime
import functools
import io
import json
import logging
import os
import re
import time
import webbrowser
import sys
import zipfile
from datetime import datetime as dt
from pathlib import Path
from typing import Dict
from typing import List
from typing import Tuple
from uuid import uuid4

import humanize
import requests
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from typing_extensions import Self

from melbalabs.summarize_consumes.consumable_model import IgnoreStrategyComponent
from melbalabs.summarize_consumes.consumable_model import SafeStrategyComponent
from melbalabs.summarize_consumes.consumable_model import EnhanceStrategyComponent
from melbalabs.summarize_consumes.consumable_model import OverwriteStrategyComponent
from melbalabs.summarize_consumes.consumable_model import ConsumableComponent
from melbalabs.summarize_consumes.consumable_model import DirectPrice
from melbalabs.summarize_consumes.consumable_model import PriceFromIngredients
from melbalabs.summarize_consumes.consumable_model import NoPrice
from melbalabs.summarize_consumes.consumable_db import all_defined_consumable_items
from melbalabs.summarize_consumes.entity_model import get_entities_with_component
from melbalabs.summarize_consumes.entity_model import get_entities_with_components
from melbalabs.summarize_consumes.entity_model import ClassDetectionComponent
from melbalabs.summarize_consumes.entity_model import TrackProcComponent
from melbalabs.summarize_consumes.entity_model import TrackSpellCastComponent
from melbalabs.summarize_consumes.entity_model import PlayerClass
from melbalabs.summarize_consumes.entity_model import Entity
from melbalabs.summarize_consumes.entity_model import CanonicalName
from melbalabs.summarize_consumes.consumable_model import PriceComponent
from melbalabs.summarize_consumes.entity_model import SpellAliasComponent
from melbalabs.summarize_consumes.consumable_model import SuperwowComponent
from melbalabs.summarize_consumes.entity_model import InterruptSpellComponent

from melbalabs.summarize_consumes.entity_model import RacialSpellComponent
from melbalabs.summarize_consumes.entity_model import TrinketComponent
from melbalabs.summarize_consumes.entity_model import ReceiveBuffSpellComponent
from melbalabs.summarize_consumes.entity_model import ClassCooldownComponent
from melbalabs.summarize_consumes.entity_db import TRINKET_RENAME
from melbalabs.summarize_consumes.parser import Parser2
from melbalabs.summarize_consumes.parser import Tree
from melbalabs.summarize_consumes.parser import ParserError
from melbalabs.summarize_consumes.parser import TreeType
from melbalabs.summarize_consumes.timeline import AbilityTimeline
from melbalabs.summarize_consumes.encounter_mobs import EncounterMobs
from melbalabs.summarize_consumes.encounter_mobs import NullEncounterMobs
from melbalabs.summarize_consumes.parser import ActionValue
import melbalabs.summarize_consumes.package as package


class App:
    pass


@functools.cache
def create_parser(debug, unparsed_logger):
    return Parser2(unparsed_logger=unparsed_logger)


class FastTimestampParser:
    def __init__(self):
        now = datetime.datetime.now()
        self.current_year = now.year
        self.system_month = now.month

        self.last_month_seen = None

        # (year, month, day) -> float timestamp
        self._day_cache = {}

    def get_initial_year(self, log_month: int) -> int:
        if log_month > self.system_month:
            return self.current_year - 1
        return self.current_year

    def parse(self, timestamp_token) -> float:
        month, day, hour, minute, sec, ms = timestamp_token.children
        month = int(month)
        day = int(day)

        # first run, initialize year
        if self.last_month_seen is None:
            self.current_year = self.get_initial_year(month)
            self.last_month_seen = month

        # date rolls forward, cache invalidates
        if self.last_month_seen == 12 and month == 1:
            self.current_year += 1
            self._day_cache.clear()
        # date rolls backward, cache invalidates
        elif self.last_month_seen == 1 and month == 12:
            self.current_year -= 1
            self._day_cache.clear()

        self.last_month_seen = month

        # one datetime object per day
        cache_key = (self.current_year, month, day)
        day_base = self._day_cache.get(cache_key)

        if day_base is None:
            day_base = dt(
                year=self.current_year, month=month, day=day, tzinfo=datetime.timezone.utc
            ).timestamp()
            self._day_cache[cache_key] = day_base

        return day_base + (int(hour) * 3600) + (int(minute) * 60) + int(sec) + (int(ms) / 1000.0)


@functools.cache
def dl_price_data(prices_server):
    try:
        URLS = {
            "nord": "https://melbalabs.com/static/twowprices.json",
            "telabim": "https://melbalabs.com/static/twowprices-telabim.json",
            "ambershire": "https://raw.githubusercontent.com/whtmst/twow-ambershire-prices/refs/heads/main/ambershire-prices-filtered.json",
        }
        url = URLS[prices_server]
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.exceptions.RequestException:
        logging.warning("web prices not available")
        return None


@functools.cache
def create_unparsed_loggers(expert_log_unparsed_lines):
    if expert_log_unparsed_lines:
        unparsed = UnparsedLogger(filename="unparsed.txt")
        unparsed_fast = UnparsedLogger(filename="unparsed-fast.txt")
    else:
        unparsed = NullLogger(filename="unparsed.txt")
        unparsed_fast = NullLogger(filename="unparsed-fast.txt")
    return unparsed, unparsed_fast


def create_encounter_mobs(write_encounter_mobs_output, known_bosses, player):
    if write_encounter_mobs_output:
        return EncounterMobs(known_bosses=known_bosses, player=player)
    return NullEncounterMobs()


def create_app(
    time_start,
    expert_log_unparsed_lines,
    prices_server,
    expert_disable_web_prices,
    expert_deterministic_logs,
    expert_log_superwow_merge,
    write_encounter_mobs_output,
):
    app = App()

    parser_debug = False
    if expert_log_unparsed_lines:
        parser_debug = True

    app.unparsed_logger, app.unparsed_logger_fast = create_unparsed_loggers(
        expert_log_unparsed_lines
    )

    app.timestamp_parser = FastTimestampParser()
    app.parser = create_parser(
        debug=parser_debug,
        unparsed_logger=app.unparsed_logger_fast,
    )

    # player - consumable - count
    app.player = collections.defaultdict(lambda: collections.defaultdict(int))
    app.player_superwow = collections.defaultdict(lambda: collections.defaultdict(int))
    app.player_superwow_unknown = collections.defaultdict(lambda: collections.defaultdict(int))

    app.merge_superwow_consumables = MergeSuperwowConsumables(
        player=app.player,
        player_superwow=app.player_superwow,
        player_superwow_unknown=app.player_superwow_unknown,
        expert_log_superwow_merge=expert_log_superwow_merge,
    )

    app.class_detection = ClassDetection(player=app.player)

    app.spell_count = SpellCount()
    app.sunder_armor_summary = SunderArmorSummary(
        spell_count=app.spell_count,
        class_detection=app.class_detection,
    )
    app.cooldown_summary = CooldownSummary(
        spell_count=app.spell_count,
        class_detection=app.class_detection,
    )

    app.proc_count = ProcCount()
    app.proc_summary = ProcSummary(proc_count=app.proc_count, player=app.player)

    app.auto_attack_stats = AutoAttackStats()
    app.auto_attack_summary = AutoAttackSummary(
        stats=app.auto_attack_stats,
        player=app.player,
        class_detection=app.class_detection,
    )

    # player - consumable - unix_timestamp
    app.last_hit_cache = collections.defaultdict(lambda: collections.defaultdict(float))

    # player - set of reasons this is considered a player
    app.player_detect = collections.defaultdict(set)

    app.pet_handler = PetHandler()

    # name -> death count
    app.death_count = collections.defaultdict(int)

    app.hits_consumable = HitsConsumable(player=app.player, last_hit_cache=app.last_hit_cache)

    app.web_price_provider = WebPriceProvider(prices_server=prices_server)
    price_providers = []
    if not expert_disable_web_prices:
        price_providers.append(app.web_price_provider)
    price_providers.append(LocalPriceProvider("prices.json"))
    app.pricedb = PriceDB(price_providers=price_providers)
    app.consumables_accumulator = ConsumablesAccumulator(
        player=app.player, pricedb=app.pricedb, death_count=app.death_count
    )
    app.print_consumables = PrintConsumables(accumulator=app.consumables_accumulator)
    app.print_consumable_totals_csv = PrintConsumableTotalsCsv(
        accumulator=app.consumables_accumulator
    )

    app.annihilator = Annihilator()
    app.flamebuffet = FlameBuffet()

    # bwl
    app.nef_corrupted_healing = NefCorruptedHealing()
    app.nef_wild_polymorph = NefWildPolymorph()
    # aq
    app.viscidus = Viscidus()
    app.huhuran = Huhuran()
    app.cthun_chain = BeamChain(
        logname="C'Thun Chain Log (2+)",
        beamname="Eye of C'Thun 's Eye Beam",
        chainsize=2,
    )
    # naxx
    app.gluth = Gluth()
    app.fourhm_chain = BeamChain(
        logname="4HM Zeliek Chain Log (4+)",
        beamname="Sir Zeliek 's Holy Wrath",
        chainsize=4,
    )
    app.kt_frostblast = KTFrostblast()
    app.kt_frostbolt = KTFrostbolt()
    app.kt_shadowfissure = KTShadowfissure()
    app.kt_guardian = KTGuardian()

    app.dmgstore = Dmgstore2(
        player=app.player,
        class_detection=app.class_detection,
        abilitycost=ABILITYCOST,
        abilitycooldown=ABILITYCOOLDOWN,
        logname="Damage Done",
        allow_selfdmg=False,
    )
    app.dmgtakenstore = Dmgstore2(
        player=app.player,
        class_detection=app.class_detection,
        abilitycost=ABILITYCOST,
        abilitycooldown=ABILITYCOOLDOWN,
        logname="Damage Taken",
        allow_selfdmg=True,
    )
    app.healstore = Dmgstore2(
        player=app.player,
        class_detection=app.class_detection,
        abilitycost=dict(),
        abilitycooldown=dict(),
        logname="Healing and Overhealing Done",
        allow_selfdmg=True,
    )

    app.ability_timeline = AbilityTimeline(
        known_bosses=KNOWN_BOSSES,
        player=app.player,
        dmgstore=app.dmgstore,
        cdspell_class=CDSPELL_CLASS,
        tracked_spells=set(LINE2SPELLCAST.values()),
    )

    app.encounter_mobs = create_encounter_mobs(
        write_encounter_mobs_output=write_encounter_mobs_output,
        known_bosses=KNOWN_BOSSES,
        player=app.player,
    )

    app.techinfo = Techinfo(
        time_start=time_start,
        prices_last_update=app.pricedb.last_update,
        prices_server=prices_server,
        expert_deterministic_logs=expert_deterministic_logs,
    )

    app.infographic = Infographic(
        accumulator=app.consumables_accumulator, class_detection=app.class_detection
    )

    app.log_downloader = LogDownloader()

    return app


def check_existing_file(file: Path, delete: bool = False) -> None:
    """Check if file exist and deletes it when forced to.

    - file (Path): File location
    - delete (bool | None, optional (False)): delete file if True
    """

    if file.exists() and file.is_file():
        if delete or False:
            file.unlink()
        return True
    return False


class HitsConsumable:
    LATENCY = 1  # client logs timestamps can be behind due to lag
    COOLDOWNS = {
        "Dragonbreath Chili": 10 * 60 - LATENCY,
        "Goblin Sapper Charge": 5 * 60 - LATENCY,
        "Stratholme Holy Water": 1 * 60 - LATENCY,
    }

    def __init__(self, player, last_hit_cache):
        self.player = player
        self.last_hit_cache = last_hit_cache

    def update(self, name, consumable, timestamp_unix):
        cooldown = self.COOLDOWNS[consumable]
        delta = timestamp_unix - self.last_hit_cache[name][consumable]
        if delta >= cooldown:
            self.player[name][consumable] += 1
            self.last_hit_cache[name][consumable] = timestamp_unix
        elif delta < 0:
            # out of order lines? not worth crashing for
            pass


NAME2CONSUMABLE: Dict[str, Entity] = {}
for entity, _ in get_entities_with_component(ConsumableComponent):
    if entity.name in NAME2CONSUMABLE:
        raise ValueError(f"Duplicate consumable name: {entity.name}")
    NAME2CONSUMABLE[entity.name] = entity

RAWSPELLNAME2CONSUMABLE: Dict[Tuple[TreeType, str], Entity] = dict()
for item, (tag, alias_comp) in get_entities_with_components(
    ConsumableComponent, SpellAliasComponent
):
    # Only entities with spell aliases can be parsed from logs.
    for line_type, raw_spellname in alias_comp.spell_aliases:
        key = (line_type, raw_spellname)
        if key in RAWSPELLNAME2CONSUMABLE:
            raise ValueError(
                f"duplicate consumable alias. tried to add {key} for {item.name}"
                f" but {RAWSPELLNAME2CONSUMABLE[key].name} already added"
            )
        RAWSPELLNAME2CONSUMABLE[key] = item


def get_spell_rename_map():
    rename_map: Dict[Tuple[TreeType, str], CanonicalName] = {}
    for entity, alias_comp in get_entities_with_component(SpellAliasComponent):
        for line_type, raw_name in alias_comp.spell_aliases:
            rename_map[(line_type, raw_name)] = entity.name
    return rename_map


RENAME_SPELL = get_spell_rename_map()


def rename_spell(spell: str, line_type: TreeType):
    rename = RENAME_SPELL.get((line_type, spell))
    return rename or spell


# careful. not everything needs an itemid
NAME2ITEMID = {}
for item, price_comp in get_entities_with_component(PriceComponent):
    if isinstance(price_comp.price, DirectPrice):
        NAME2ITEMID[item.name] = price_comp.price.itemid


# used for pricing
ITEMID2NAME = {value: key for key, value in NAME2ITEMID.items()}


INTERRUPT_SPELLS = {
    entity.name for entity, _ in get_entities_with_component(InterruptSpellComponent)
}
TRINKET_SPELL = []
for _, trinket_comp in get_entities_with_component(TrinketComponent):
    TRINKET_SPELL.extend(trinket_comp.triggered_by_spells)
TRINKET_SPELL_SET = set(TRINKET_SPELL)
TRINKET_SPELL = list(TRINKET_SPELL_SET)


RACIAL_SPELL = [entity.name for entity, _ in get_entities_with_component(RacialSpellComponent)]
RECEIVE_BUFF_SPELL = {
    entity.name for entity, _ in get_entities_with_component(ReceiveBuffSpellComponent)
}


def build_cdspell_class():
    """
    Returns list in the old format: [[PlayerClass, [spell_names]], ...]
    Includes trinkets, racials, and receive buffs appended to each class.
    """
    class_spells = collections.defaultdict(list)
    for entity, comp in get_entities_with_component(ClassCooldownComponent):
        for pc in comp.player_classes:
            class_spells[pc].append(entity.name)

    shared_spells = sorted(TRINKET_SPELL) + sorted(RACIAL_SPELL) + sorted(RECEIVE_BUFF_SPELL)

    result = []
    for pc in [
        PlayerClass.WARRIOR,
        PlayerClass.MAGE,
        PlayerClass.SHAMAN,
        PlayerClass.DRUID,
        PlayerClass.PRIEST,
        PlayerClass.PALADIN,
        PlayerClass.ROGUE,
        PlayerClass.WARLOCK,
        PlayerClass.HUNTER,
    ]:
        spells = sorted(class_spells[pc]) + shared_spells
        result.append([pc, spells])

    return result


CDSPELL_CLASS = build_cdspell_class()
RENAME_TRINKET_SPELL = TRINKET_RENAME


BUFF_SPELL = {
    "Greater Blessing of Wisdom",
    "Greater Blessing of Salvation",
    "Greater Blessing of Light",
    "Greater Blessing of Kings",
    "Greater Blessing of Might",
    "Prayer of Spirit",
    "Prayer of Fortitude",
    "Prayer of Shadow Protection",
}

ABILITYCOST = {
    "Bloodthirst": 30,
    "Hamstring": 10,
    "Heroic Strike": 15,
    "Whirlwind": 25,
    "Cleave": 20,
    "Execute": 15,
    "Slam": 15,
}

ABILITYCOOLDOWN = {
    "Whirlwind": 8,
    "Cleave": 1,
}

KNOWN_BOSSES = {
    # bwl
    "Razorgore the Untamed": [],
    "Vaelastrasz the Corrupt": [],
    "Broodlord Lashlayer": [],
    "Firemaw": [],
    "Ebonroc": [],
    "Flamegor": [],
    "Chromaggus": [],
    "Nefarian": [],
    # aq40
    "The Prophet Skeram": [],
    "Princess Yauj": [],
    "Vem": [],
    "Lord Kri": [],
    "Battleguard Sartura": [],
    "Fankriss the Unyielding": [],
    "Viscidus": [],
    "Princess Huhuran": [],
    "Emperor Vek'lor": [],
    "Emperor Vek'nilash": [],
    "Ouro": [],
    "C'Thun": [],
    "Eye of C'Thun": [],
    # naxx
    "Anub'Rekhan": [
        "Crypt Guard",
    ],
    "Grand Widow Faerlina": [
        "Naxxramas Worshipper",
        "Naxxramas Follower",
    ],
    "Maexxna": [
        "Maexxna Spiderling",
    ],
    "Noth the Plaguebringer": [
        "Plagued Warrior",
    ],
    "Heigan the Unclean": [],
    "Loatheb": [],
    "Patchwerk": [],
    "Grobbulus": [
        "Fallout Slime",
    ],
    "Gluth": [],  # Zombie Chow? kinda whatever
    "Thaddius": [],
    "Feugen": [],
    "Stalagg": [],
    "Instructor Razuvious": [
        "Deathknight Understudy",
    ],
    "Gothik the Harvester": [
        "Spectral Deathknight",
        "Spectral Horse",
        "Spectral Rider",
        "Spectral Trainee",
        "Unrelenting Deathknight",
        "Unrelenting Rider",
        "Unrelenting Trainee",
    ],
    "Highlord Mograine": [],
    "Lady Blaumeux": [],
    "Sir Zeliek": [],
    "Thane Korth'azz": [],
    "Sapphiron": [],
    "Kel'Thuzad": [
        "Guardian of Icecrown",
        "Soldier of the Frozen Wastes",
        "Soul Weaver",
        "Unstoppable Abomination",
    ],
    # kara
    "Keeper Gnarlmoon": [
        "Blood Raven",
        "Red Owl",
        "Blue Owl",
    ],
    "Ley-Watcher Incantagos": [
        "Manascale Ley-Seeker",
        "Manascale Ley-Seeker (Ley-Watcher Incantagos)",
        "Manascale Whelp (Ley-Watcher Incantagos)",
        "Manascale Whelp",
        "Blue Affinity",
        "Red Affinity",
        "Green Affinity",
        "Black Affinity",
        "Red Affinity",
        "Mana Affinity",
    ],
    "Anomalus": [],
    "Echo of Medivh": [
        "Lingering Doom",
        "Unstoppable Infernal",
        "Shade of Medivh",
    ],
    "Chess": [
        "Withering Pawn",
        "Malfunctioning Knight",
        "Decaying Bishop",
        "Broken Rook",
        "Ghastly Horseman",
        "Pawn",
        "Knight",
        "Bishop",
        "Rook",
        "King",
    ],
    "Rupturan the Broken": [
        "Crumbling Exile",
        "Living Stone",
        "Living Fragment",
        "Fragment of Rupturan",
        "Felheart",
    ],
    "Sanv Tas'dal": [
        "Draenei Truthseeker",
        "Rift-Lost Draenei",
        "Rift-Lost Draenei (Sanv Tas'dal)",
        "Shadow-Lost Draenei",
        "Draenei Netherwalker",
        "Draenei Riftwalker",
        "Draenei Riftstalker",
    ],
    "Kruul": ["Nether Infernal"],
    "Mephistroth": [
        "Hellfury Shard",
        "Hellfire Imp",
        "Hellfire Doomguard",
        "Desolate Doomguard",
        "Nightmare Crawler",
    ],
}


def healpot_lookup(amount):
    # bigger ranges for rounding errors
    if 1049 <= amount <= 1751:
        return "Healing Potion - Major"
    if 699 <= amount <= 901:
        return "Healing Potion - Superior"
    if 454 <= amount <= 586:
        return "Healing Potion - Greater"
    if 279 <= amount <= 362:
        return "Healing Potion"
    if 139 <= amount <= 181:
        return "Healing Potion - Lesser"
    if 69 <= amount <= 91:
        return "Healing Potion - Minor"
    return "Healing Potion - unknown"


def manapot_lookup(mana):
    consumable = "Restore Mana (mana potion)"
    if 1350 <= mana <= 2250:
        consumable = "Mana Potion - Major"
    elif 900 <= mana <= 1500:
        consumable = "Mana Potion - Superior"
    elif 700 <= mana <= 900:
        consumable = "Mana Potion - Greater"
    elif 454 <= mana <= 587:
        consumable = "Mana Potion"
    elif 280 <= mana <= 360:
        consumable = "Mana Potion - Lesser"
    elif 140 <= mana <= 180:
        consumable = "Mana Potion - Minor"
    return consumable


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
        if not self.log:
            return

        print(f"\n\n{self.logname}", file=output)
        for line in self.log:
            print("  ", line, end="", file=output)


def print_collected_log(section_name, log_list, output):
    if not log_list:
        return
    print(f"\n\n{section_name}", file=output)
    for line in log_list:
        print("  ", line, end="", file=output)
    return


def print_collected_log_always(section_name, log_list, output):
    print(f"\n\n{section_name}", file=output)
    for line in log_list:
        print("  ", line, end="", file=output)
    if not log_list:
        print("  ", "<nothing found>", end="", file=output)
    return


class Annihilator:
    def __init__(self):
        self.logname = "Annihilator Log"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log_always(self.logname, self.log, output)


class FlameBuffet:
    def __init__(self):
        self.logname = "Flame Buffet (dragonling) Log"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log_always(self.logname, self.log, output)


class KTFrostbolt:
    def __init__(self):
        self.logname = "KT Frostbolt Log"
        self.log = []

    def begins_to_cast(self, line):
        self.log.append("\n")
        self.log.append(line)

    def add(self, line):
        self.log.append(line)

    def parry(self, line):
        line = "*** honorable mention *** " + line
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class KTFrostblast:
    def __init__(self):
        self.logname = "KT Frost Blast Log"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class KTShadowfissure:
    def __init__(self):
        self.logname = "KT Shadow Fissure Log"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class KTGuardian:
    def __init__(self):
        self.logname = "KT Guardian of Icecrown Log"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class Viscidus:
    def __init__(self):
        self.logname = "Viscidus Frost Hits Log"
        # player - frost spell - count
        self.counts = collections.defaultdict(lambda: collections.defaultdict(int))
        self.totals = collections.defaultdict(int)
        self._found = False

    def add(self, player, spell):
        self.counts[player][spell] += 1
        self.totals[player] += 1

    def found(self):
        self._found = True

    def print(self, output):
        if not self._found:
            return
        print(f"\n\n{self.logname}", file=output)
        players = [(total, player) for player, total in self.totals.items()]
        players.sort(reverse=True)
        print("  ", "Total hits", sum(total for total, player in players), file=output)
        print(file=output)
        for total, player in players:
            print("  ", player, total, file=output)
            spells = [(total, spell) for spell, total in self.counts[player].items()]
            spells.sort(reverse=True)
            for total, spell in spells:
                print("  ", "  ", spell, total, file=output)


class Huhuran:
    def __init__(self):
        self.logname = "Princess Huhuran Log"
        self.log = []
        self._found = False

    def found(self):
        self._found = True

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        if not self._found:
            return
        print_collected_log(self.logname, self.log, output)


class NefCorruptedHealing:
    def __init__(self):
        self.logname = "Nefarian Priest Corrupted Healing"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class NefWildPolymorph:
    def __init__(self):
        self.logname = "Nefarian Wild Polymorph (mage call)"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class Gluth:
    def __init__(self):
        self.logname = "Gluth Log"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class BeamChain:
    def __init__(self, logname, beamname, chainsize):
        self.log = []  # for debugging/testing

        self.current_batch = []
        self.batches = []

        self.last_ts = 0
        self.logname = logname
        self.beamname = beamname
        self.chainsize = chainsize  # report chains bigger than this

    def add(self, timestamp_unix, line):
        self.log.append(line)

        cooldown = 2
        delta = timestamp_unix - self.last_ts
        if delta >= cooldown:
            self.commitbatch()
            self.last_ts = timestamp_unix

        self.current_batch.append(line)

    def commitbatch(self):
        if self.current_batch:
            self.batches.append(self.current_batch)
            self.current_batch = []

    def print(self, output):
        if not self.log:
            return

        self.commitbatch()

        found_batch = 0
        print(f"\n\n{self.logname}", file=output)

        for batch in self.batches:
            if len(batch) < self.chainsize:
                continue

            found_batch = 1

            print(file=output)
            for line in batch:
                print("  ", line, end="", file=output)

        if not found_batch:
            print(
                "  ",
                f"<no chains of {self.chainsize} found. well done>",
                end="",
                file=output,
            )


class DmgstoreEntry:
    def __init__(self):
        self.dmg = 0
        self.cost = 0
        self.hits = 0
        self.uses = 0
        self.last_ts = 0


class Dmgstore2:
    def __init__(
        self,
        player,
        class_detection: "ClassDetection",
        abilitycost,
        abilitycooldown,
        logname,
        allow_selfdmg,
    ):
        self.logname = logname
        self.player = player
        self.class_detection = class_detection
        self.abilitycost = abilitycost
        self.abilitycooldown = abilitycooldown
        self.allow_selfdmg = allow_selfdmg

        self.store_ability = collections.defaultdict(DmgstoreEntry)
        self.store_target = collections.defaultdict(DmgstoreEntry)
        self.store_source = collections.defaultdict(DmgstoreEntry)

        self.store_by_source_ability = collections.defaultdict(
            lambda: collections.defaultdict(DmgstoreEntry)
        )

    def add(self, source, target, ability, amount, timestamp_unix):
        if not self.allow_selfdmg and source == target:
            return
        cost = self.abilitycost.get(ability, 0)
        cooldown = self.abilitycooldown.get(ability, 0)

        entry_ability = self.store_ability[(source, target, ability)]
        entry_ability.dmg += amount
        entry_ability.hits += 1

        entry_target = self.store_target[(source, target)]
        entry_target.dmg += amount
        entry_target.hits += 1

        entry_source = self.store_source[source]
        entry_source.dmg += amount
        entry_source.hits += 1

        entry_by_source_ability = self.store_by_source_ability[source][ability]
        entry_by_source_ability.dmg += amount
        entry_by_source_ability.hits += 1

        delta = timestamp_unix - entry_by_source_ability.last_ts
        if delta >= cooldown:
            entry_by_source_ability.last_ts = timestamp_unix

            entry_by_source_ability.uses += 1
            entry_ability.uses += 1
            entry_target.uses += 1
            entry_source.uses += 1

            entry_by_source_ability.cost += cost
            entry_ability.cost += cost
            entry_target.cost += cost
            entry_source.cost += cost

    def print_compare_players(self, player1, player2, output):
        # fill blanks

        for source, target, ability in sorted(self.store_ability):
            if source == player1:
                self.store_ability[(player2, target, ability)]
                self.store_target[(player2, target)]
            elif source == player2:
                self.store_ability[(player1, target, ability)]
                self.store_target[(player1, target)]

        es1 = self.store_source[player1]
        es2 = self.store_source[player2]

        # extract data to report on
        p1 = dict()
        p2 = dict()

        for source, target, ability in sorted(self.store_ability):
            if source == player1:
                p1[(target, ability)] = self.store_ability[(player1, target, ability)]
            elif source == player2:
                p2[(target, ability)] = self.store_ability[(player2, target, ability)]

        print(f"output for {player1} - {player2}", file=output)
        print(file=output)

        print(
            f"total  dmg:{es1.dmg - es2.dmg} cost:{es1.cost - es2.cost} uses:{es1.uses - es2.uses} hits:{es1.hits - es2.hits}",
            file=output,
        )
        print(file=output)

        seen_target = set()
        for target, ability in p1:
            e1 = p1[(target, ability)]
            e2 = p2[(target, ability)]

            if target not in seen_target:
                seen_target.add(target)
                print(file=output)
                et1 = self.store_target[(player1, target)]
                et2 = self.store_target[(player2, target)]
                txt = f"{target}   dmg:{et1.dmg - et2.dmg} cost:{et1.cost - et2.cost} uses:{et1.uses - et2.uses} hits:{et1.hits - et2.hits}"
                print(txt, file=output)
            txt = f"{ability}   dmg:{e1.dmg - e2.dmg} cost:{e1.cost - e2.cost} uses:{e1.uses - e2.uses} hits:{e1.hits - e2.hits}"
            print(txt, file=output)

    def print_damage(self, output):
        # first find dmg totals
        # then abilities
        dmgtotals = collections.defaultdict(int)
        for (source, target, ability), entry in self.store_ability.items():
            if source not in self.player:
                continue
            dmgtotals[source] += entry.dmg

        sortdmgtotals = []
        for source, dmg in dmgtotals.items():
            sortdmgtotals.append((dmg, source))

        sortdmgtotals.sort(reverse=True)
        for dmg, source in sortdmgtotals:
            print(f"{source}  {dmg}", file=output)

            sortabilitytotals = []
            for ability, entry_by_source_ability in self.store_by_source_ability[source].items():
                dmg = entry_by_source_ability.dmg
                sortabilitytotals.append((dmg, ability))

            sortabilitytotals.sort(reverse=True)
            for dmg2, ability in sortabilitytotals:
                print(f"  {ability}  {dmg2}", file=output)

    def print_damage_taken(self, output):
        # by source, ability, target

        by_source = collections.defaultdict(int)
        by_ability = collections.defaultdict(lambda: collections.defaultdict(int))
        by_target = collections.defaultdict(lambda: collections.defaultdict(int))
        for (source, target, ability), entry in self.store_ability.items():
            if target not in self.player:
                continue

            dmg = entry.dmg
            by_source[source] += dmg
            by_ability[source][ability] += dmg
            by_target[(source, ability)][target] += dmg

        source_sorted = sorted(by_source, key=lambda k: by_source[k], reverse=True)
        for source in source_sorted:
            print(f"{source}  {by_source[source]}", file=output)

            ability_sorted = sorted(
                by_ability[source], key=lambda k: by_ability[source][k], reverse=True
            )

            for ability in ability_sorted:
                print("  ", f"{ability}  {by_ability[source][ability]}", file=output)

                target_sorted = sorted(
                    by_target[(source, ability)],
                    key=lambda k: by_target[(source, ability)][k],
                    reverse=True,
                )

                for target in target_sorted:
                    print(
                        "  ",
                        "  ",
                        f"{target}  {by_target[(source, ability)][target]}",
                        file=output,
                    )


class Techinfo:
    def __init__(self, time_start, prices_last_update, prices_server, expert_deterministic_logs):
        self.time_start = time_start
        self.logsize = 0
        self.linecount = 0
        self.skiplinecount = 0
        self.package_version = package.VERSION
        urlname, url = package.PROJECT_URL.split(",", maxsplit=1)
        assert urlname == "Homepage"
        self.project_homepage = url.strip()
        self.prices_last_update = prices_last_update
        self.prices_server = prices_server
        self.expert_deterministic_logs = expert_deterministic_logs

        self.implementation = str(sys.implementation).replace("namespace", "")
        self.platform = sys.platform
        self.version = sys.version

    def set_file_size(self, filename):
        self.logsize = os.path.getsize(filename)

    def set_line_count(self, count):
        self.linecount = count

    def set_skipped_line_count(self, count):
        self.skiplinecount = count

    def format_price_timestamp(self):
        if self.prices_last_update == 0:
            return "not available"
        dt = datetime.datetime.fromtimestamp(self.prices_last_update, datetime.UTC)
        delta = self.time_start - self.prices_last_update
        return f"{dt.isoformat()} ({humanize.naturaltime(delta)})"

    def format_skipped_percent(self):
        if self.linecount == 0:
            return ""
        return f"({(self.skiplinecount / self.linecount) * 100:.2f}%)"

    def print(self, output, time_end=None):
        if time_end is None:
            time_end = time.time()
        time_delta = time_end - self.time_start
        if time_delta == 0:
            time_delta = 0.00000001  # too fast sometimes
        print("\n\nTech", file=output)
        if not self.expert_deterministic_logs:
            print("  ", f"project version {self.package_version}", file=output)
            print("  ", f"project homepage {self.project_homepage}", file=output)
            print("  ", f"prices server {self.prices_server}", file=output)
            print("  ", f"prices timestamp {self.format_price_timestamp()}", file=output)
        print("  ", f"known consumables {len(all_defined_consumable_items)}", file=output)
        print("  ", f"log size {humanize.naturalsize(self.logsize)}", file=output)
        print("  ", f"log lines {self.linecount}", file=output)
        print(
            "  ",
            f"skipped log lines {self.skiplinecount} {self.format_skipped_percent()}",
            file=output,
        )
        if not self.expert_deterministic_logs:
            print(
                "  ",
                f"processed in {time_delta:.2f} seconds. {self.linecount / time_delta:.2f} log lines/sec",
                file=output,
            )
            print("  ", f"runtime platform {self.platform}", file=output)
            print("  ", f"runtime implementation {self.implementation}", file=output)
            print("  ", f"runtime version {self.version}", file=output)


class UnparsedLogger:
    def __init__(self, filename):
        self.filename = filename
        self.buffer = io.StringIO()

    def log(self, line):
        print(line, end="", file=self.buffer)

    def flush(self):
        print("writing unparsed to", self.filename)
        with open(self.filename, "wb") as f:
            f.write(self.buffer.getvalue().encode("utf8"))


class NullLogger:
    def __init__(self, filename):
        pass

    def log(self, line):
        pass

    def flush(self):
        pass


class LocalPriceProvider:
    def __init__(self, filename):
        self.filename = filename

    def load(self):
        filename = self.filename
        if not os.path.exists(filename):
            logging.warning(f"local prices not available. {filename} not found")
            return
        logging.info("loading local prices from {filename}")
        with open(filename) as f:
            prices = json.load(f)
            return prices


class WebPriceProvider:
    def __init__(self, prices_server):
        self.prices_server = prices_server

    def load(self):
        logging.info("loading web prices")
        prices = dl_price_data(prices_server=self.prices_server)
        return prices


class PriceDB:
    def __init__(self, price_providers):
        self.data = dict()
        self.last_update = 0

        for provider in price_providers:
            prices = provider.load()
            if not prices:
                continue
            self.load_incoming(prices)
            return

    def lookup(self, itemid):
        return self.data.get(itemid)

    def load_incoming(self, incoming):
        self.last_update = incoming["last_update"]
        for key, val in incoming["data"].items():
            key = int(key)
            self.data[key] = val


class PetHandler:
    def __init__(self):
        # owner -> set of pets
        self.store = collections.defaultdict(set)

    def add(self, owner, pet):
        self.store[owner].add(pet)

    def get_all_pets(self):
        for owner, petset in self.store.items():
            for pet in petset:
                yield pet

    def print(self, output):
        if not len(self.store):
            return
        print("\n\nPets", file=output)
        for owner, petset in self.store.items():
            for pet in sorted(petset):
                print("  ", pet, "owned by", owner, file=output)


class SunderArmorSummary:
    def __init__(self, spell_count, class_detection: "ClassDetection"):
        self.counts = spell_count.counts
        self.class_detection = class_detection

    def print(self, output):
        print("\n\nSunder Armor Summary (trash and boss counts)", file=output)
        warriors = [
            name
            for name, player_class in self.class_detection.store.items()
            if player_class is PlayerClass.WARRIOR
        ]

        found_sunder = False
        entries = []
        sunder_trash = self.counts.get("Sunder Armor", {})
        sunder_boss = self.counts.get("Sunder Armor (boss)", {})

        for warrior in warriors:
            trash = sunder_trash.get(warrior, 0)
            boss = sunder_boss.get(warrior, 0)
            entries.append((-trash, -boss, warrior, trash, boss))
            if trash or boss:
                found_sunder = True

        if found_sunder:
            entries.sort()

            for _, _, name, trash, boss in entries:
                line = f"   {name} {trash}"
                if boss > 0:
                    line += f" {boss}"
                print(line, file=output)
        elif entries:
            print("   <nothing found. needs superwow>", file=output)
        else:
            print("   <nothing found>", file=output)


class CooldownSummary:
    def __init__(self, spell_count, class_detection: "ClassDetection"):
        # spell - player - count
        self.counts = spell_count.counts
        self.class_detection = class_detection

    def print(self, output):
        print("\n\nCooldown Summary", file=output)
        for player_class, spells in CDSPELL_CLASS:
            cls_printed = False
            for spell in spells:
                if spell not in self.counts:
                    continue

                data = []
                for name, total in self.counts[spell].items():
                    if not self.class_detection.is_class(cls=player_class, name=name):
                        continue
                    data.append((total, name))
                data.sort(reverse=True)

                if not data:
                    continue

                if not cls_printed:
                    print("  ", player_class.value.capitalize(), file=output)
                    cls_printed = True
                if spell in RENAME_TRINKET_SPELL:
                    spell = RENAME_TRINKET_SPELL[spell]
                if spell in RECEIVE_BUFF_SPELL:
                    spell += " (received)"
                print("  ", "  ", spell, file=output)
                for total, name in data:
                    print("  ", "  ", "  ", name, total, file=output)


class AutoAttackStats:
    def __init__(self):
        # player -> stat -> count
        self.stats = collections.defaultdict(lambda: collections.defaultdict(int))

    def add_hit(self, attacker):
        self.stats[attacker]["swings"] += 1
        self.stats[attacker]["hits"] += 1

    def add_crit(self, attacker):
        self.stats[attacker]["swings"] += 1
        self.stats[attacker]["crits"] += 1

    def add_glance(self, attacker):
        self.stats[attacker]["swings"] += 1
        self.stats[attacker]["glances"] += 1

    def add_parry(self, attacker):
        self.stats[attacker]["swings"] += 1
        self.stats[attacker]["parries"] += 1

    def add_dodge(self, attacker):
        self.stats[attacker]["swings"] += 1
        self.stats[attacker]["dodges"] += 1

    def add_miss(self, attacker):
        self.stats[attacker]["swings"] += 1
        self.stats[attacker]["misses"] += 1

    def add_block(self, attacker):
        self.stats[attacker]["swings"] += 1
        self.stats[attacker]["blocks"] += 1


class AutoAttackSummary:
    def __init__(self, stats, player, class_detection):
        self.stats = stats
        self.player = player
        self.class_detection = class_detection

    def print(self, output):
        print("\n\nAuto Attack Summary", file=output)

        all_names = sorted(self.stats.stats)

        for player_class in PlayerClass:
            # check if we have any players for this class
            class_players = []
            for name in all_names:
                if name not in self.player:
                    continue
                if not self.class_detection.is_class(player_class, name):
                    continue
                class_players.append(name)

            if not class_players:
                continue

            class_players.sort(key=lambda n: self.stats.stats[n]["swings"], reverse=True)

            print(f"   {player_class.value.capitalize()}", file=output)

            for name in class_players:
                data = self.stats.stats[name]
                swings = data["swings"]
                if swings == 0:
                    continue

                def fmt(key):
                    count = data[key]
                    if count == 0:
                        return None
                    pct = (count / swings) * 100
                    return f"         {key} {count}   ({pct:.1f}%)"

                print(f"      {name} swings {swings}", file=output)

                for key in ["hits", "crits", "parries", "misses", "dodges", "blocks", "glances"]:
                    line = fmt(key)
                    if line:
                        print(line, file=output)


class ProcSummary:
    def __init__(self, proc_count, player):
        # spell - player - count
        self.counts = proc_count.counts
        self.counts_extra_attacks = proc_count.counts_extra_attacks
        self.amount_unbridled_wrath = proc_count.amount_unbridled_wrath
        self.player = player

    def print(self, output):
        print("\n\nProc Summary", file=output)
        for proc in sorted(self.counts):
            data = []
            for name in sorted(self.counts[proc]):
                total = self.counts[proc][name]
                if name not in self.player:
                    continue
                data.append((total, name))
            data.sort(reverse=True)

            if not data:
                continue
            print("  ", proc, file=output)
            for total, name in data:
                line = f"      {name} {total}"
                if proc == "Unbridled Wrath":
                    uw_amount = self.amount_unbridled_wrath[name]
                    line += f" for {uw_amount} rage"
                print(line, file=output)

        # extra attacks
        print("  ", "Extra Attacks", file=output)
        for source in sorted(self.counts_extra_attacks):
            data = []
            for name in sorted(self.counts_extra_attacks[source]):
                total = self.counts_extra_attacks[source][name]
                if name not in self.player:
                    continue
                data.append((total, name))
            data.sort(reverse=True)

            if not data:
                continue
            print("  ", "  ", source, file=output)
            for total, name in data:
                print("  ", "  ", "  ", name, total, file=output)


# count unique casts, the player using their spell. not the lingering buff/debuff procs
# eg count a totem being dropped, not the buff procs it gives after that
LINE2SPELLCAST = {}

for entity, (tag, alias_comp) in get_entities_with_components(
    TrackSpellCastComponent, SpellAliasComponent
):
    for line_type, raw_spellname in alias_comp.spell_aliases:
        key = (line_type, raw_spellname)
        if key in LINE2SPELLCAST:
            raise ValueError(
                f"duplicate spell alias. tried to add {key} for {entity.name}"
                f" but {key} already added"
            )
        LINE2SPELLCAST[key] = entity.name


class SpellCount:
    def __init__(self):
        # spell - name - count
        self.counts = collections.defaultdict(lambda: collections.defaultdict(int))

    def add(self, line_type, name, spell):
        key = (line_type, spell)
        if key not in LINE2SPELLCAST:
            return
        spellname_canonical = LINE2SPELLCAST[key]
        self.counts[spellname_canonical][name] += 1

    def add_stackcount(self, line_type, name, spell, stackcount):
        if (
            spell in {"Combustion", "Unstable Power", "Jom Gabbar"}
            and line_type == TreeType.GAINS_LINE
            and stackcount != 1
        ):
            return
        self.add(line_type=line_type, name=name, spell=spell)


LINE2PROC = {}


for entity, (tag, alias_comp) in get_entities_with_components(
    TrackProcComponent, SpellAliasComponent
):
    for line_type, raw_spellname in alias_comp.spell_aliases:
        key = (line_type, raw_spellname)
        if key in LINE2PROC:
            raise ValueError(
                f"duplicate spell alias. tried to add {key} for {entity.name}"
                f" but {key} already added"
            )
        LINE2PROC[key] = entity.name


class ProcCount:
    def __init__(
        self,
    ):
        # effect - name - count
        self.counts = collections.defaultdict(lambda: collections.defaultdict(int))

        # source - name - count
        self.counts_extra_attacks = collections.defaultdict(lambda: collections.defaultdict(int))

        # name - amount
        self.amount_unbridled_wrath = collections.defaultdict(int)

    def add(self, line_type, name, spell):
        key = (line_type, spell)
        if key not in LINE2PROC:
            return
        spellname_canonical = LINE2PROC[key]
        self.counts[spellname_canonical][name] += 1

    def add_extra_attacks(self, howmany, source, name):
        self.counts_extra_attacks[source][name] += howmany

    def add_unbridled_wrath(self, amount, name):
        self.amount_unbridled_wrath[name] += amount


class Currency(int):
    string_pattern = r"((?P<gold>\d+)g)?\s?((?P<silver>\d+)s)?\s?((?P<copper>\d+)c)?"

    def __new__(cls, value, *args, **kwargs) -> Self:
        if isinstance(value, str):
            return cls.from_string(value)
        return super().__new__(cls, value, *args, **kwargs)

    def __add__(self, other) -> Self:
        return Currency(super().__add__(other))

    def __sub__(self, other) -> Self:
        return Currency(super().__sub__(other))

    def __mul__(self, other) -> Self:
        return Currency(super().__mul__(other))

    def __truediv__(self, other) -> Self:
        return Currency(super().__truediv__(other))

    def __mod__(self, other) -> Self:
        return Currency(super().__mod__(other))

    @classmethod
    def from_string(cls, s: str) -> Self:
        m = re.search(cls.string_pattern, s)
        if not any(m.groupdict().values()):
            raise ValueError(f"Invalid currency string format: {s}")
        return cls(
            sum(
                [
                    int(m.group("gold") or 0) * 10000,
                    int(m.group("silver") or 0) * 100,
                    int(m.group("copper") or 0),
                ]
            )
        )

    def to_string(self, short: bool = False) -> str:
        if short:
            return f"{int(self) / 10000.0:.1f}g"

        value = int(self)
        copper = value % 100
        value = value // 100
        silver = value % 100
        value = value // 100
        gold = value
        s = ""

        first = True
        for amount, suffix in zip([gold, silver, copper], "gsc"):
            if amount:
                if not first:
                    s += " "
                else:
                    first = False
                s += f"{amount}{suffix}"
        return s


@dataclasses.dataclass
class ConsumableStore:
    item_name: str
    amount: int = 0
    price: Currency = Currency(0)

    @property
    def total_price(self) -> Currency:
        return self.price * self.amount


@dataclasses.dataclass
class ConsumablesEntry:
    name: str
    deaths: int = 0
    consumables: List[ConsumableStore] = dataclasses.field(default_factory=list)
    total_spent: Currency = Currency(0)

    def add_consumable(self, consumable: ConsumableStore) -> None:
        self.consumables.append(consumable)
        self.total_spent += consumable.total_price


@dataclasses.dataclass
class ConsumablesAccumulator:
    player: Dict
    pricedb: PriceDB
    death_count: Dict[str, int]
    data: List[ConsumablesEntry] = dataclasses.field(default_factory=list)

    def get_consumable_price(self, consumable_name: str) -> Currency:
        price = Currency(0)
        spell = NAME2CONSUMABLE.get(consumable_name)
        if not spell:
            return price

        price_comps = spell.get_components(PriceComponent)
        if not price_comps:
            return price
        item_price_info = price_comps[0].price

        if isinstance(item_price_info, NoPrice):
            return price

        # Determine the list of items whose direct itemid-based price we need to sum up.
        # For a crafted item, these are its components.
        # For a base item, it's the item itself.
        ingredients_to_price: List[Tuple[Entity, float]]
        item_charges = item_price_info.charges

        if isinstance(item_price_info, PriceFromIngredients):
            ingredients_to_price = item_price_info.ingredients
        elif isinstance(item_price_info, DirectPrice):
            ingredients_to_price = [(spell, 1.0)]
        else:
            raise RuntimeError("this should be unreachable, NoPrice should be handled already")

        for ingredient, quantity in ingredients_to_price:
            ingredient_price_comps = ingredient.get_components(PriceComponent)
            if not ingredient_price_comps or not isinstance(
                ingredient_price_comps[0].price, DirectPrice
            ):
                continue
            ingredient_price_info = ingredient_price_comps[0].price

            unit_price = self.pricedb.lookup(ingredient_price_info.itemid)
            if unit_price is None:
                continue

            price += int(unit_price * quantity)

        return price / item_charges

    def calculate(self) -> None:
        for name in sorted(self.player):
            consumables = sorted(self.player[name])
            player_entry = ConsumablesEntry(name, deaths=self.death_count[name])
            for consumable_name in sorted(
                consumables
            ):  # consumable_name is already a canonical string
                player_entry.add_consumable(
                    ConsumableStore(
                        consumable_name,
                        amount=self.player[name][consumable_name],
                        price=self.get_consumable_price(consumable_name),
                    )
                )
            self.data.append(player_entry)


class PrintConsumables:
    def __init__(self, accumulator: ConsumablesAccumulator):
        self.accumulator = accumulator

    def print(self, output):
        for player in self.accumulator.data:
            print(player.name, f"deaths:{player.deaths}", file=output)
            for cons in player.consumables:
                spent = f"  ({cons.total_price.to_string()})" if cons.price else ""
                print("  ", cons.item_name, cons.amount, spent, file=output)
            if not player.consumables:
                print("  ", "<nothing found>", file=output)
            elif player.total_spent:
                print(file=output)
                print("  ", "total spent:", player.total_spent.to_string(), file=output)


class PrintConsumableTotalsCsv:
    def __init__(self, accumulator: ConsumablesAccumulator):
        self.accumulator = accumulator

    def print(self, output):
        writer = csv.writer(output)
        for player in self.accumulator.data:
            writer.writerow([player.name, player.total_spent, player.deaths])


# shouldn't need to be an exhaustive list, only the most common
# unique spells, no ambiguity
UNIQUE_LINE2SPELL2CLASS = {}

for entity, (det_comp,) in get_entities_with_components(ClassDetectionComponent):
    player_class = det_comp.player_class
    for line_type, raw_spellname in det_comp.triggered_by:
        key = (line_type, raw_spellname)
        if key in UNIQUE_LINE2SPELL2CLASS:
            raise ValueError(
                f"duplicate spell alias. tried to add {key} for {player_class}"
                f" but {key} already added"
            )
        UNIQUE_LINE2SPELL2CLASS[key] = player_class


class ClassDetection:
    def __init__(self, player):
        self.store: Dict[str, PlayerClass] = dict()
        self.player = player

    def remove_unknown(self):
        knowns = set(self.player)
        for name in list(self.store):
            if name not in knowns:
                del self.store[name]

    def is_class(self, cls: PlayerClass, name: str) -> bool:
        if name not in self.store:
            return False
        return self.store[name] is cls

    def detect(self, line_type: str, name: str, spell: str):
        if (line_type, spell) not in UNIQUE_LINE2SPELL2CLASS:
            return
        detected_class = UNIQUE_LINE2SPELL2CLASS[line_type, spell]

        if name not in self.store:
            self.store[name] = detected_class
            return

        # sanity check if a player is detected as a different class
        # if self.store.get(name) is not detected_class:
        #     logging.warning(
        #         f"{name} re-detected from {self.store[name].value} to {detected_class.value} via {spell}"
        #     )
        #     # decide on a strategy: overwrite, keep first, error
        #     self.store[name] = detected_class # overwrite

    def print(self, output):
        print("\n\nClass Detection", file=output)
        for name in sorted(self.player):
            player_class = self.store.get(name, PlayerClass.UNKNOWN)
            print("  ", name, player_class.value, file=output)


class Infographic:
    BACKGROUND_COLOR = "#282B2C"
    CLASS_COLOURS: Dict[PlayerClass, str] = {
        PlayerClass.DRUID: "#FF7D0A",
        PlayerClass.HUNTER: "#ABD473",
        PlayerClass.MAGE: "#69CCF0",
        PlayerClass.PALADIN: "#F58CBA",
        PlayerClass.PRIEST: "#FFFFFF",
        PlayerClass.ROGUE: "#FFF569",
        PlayerClass.SHAMAN: "#0070DE",
        PlayerClass.WARLOCK: "#9482C9",
        PlayerClass.WARRIOR: "#C79C6E",
        PlayerClass.UNKNOWN: "#660099",
    }
    DEFAULT_FILENAME = "infographic"

    def __init__(
        self,
        accumulator: ConsumablesAccumulator,
        class_detection: ClassDetection = None,
        title: str = "",
    ):
        self.accumulator = accumulator
        self.detected_classes: Dict[str, PlayerClass] = (
            class_detection.store if class_detection else {}
        )
        self.title = title

    def generate(self, output_file: Path = None) -> None:
        players = sorted(self.accumulator.data, key=lambda entry: -entry.total_spent)
        names = [e.name for e in players]
        colors = [
            self.CLASS_COLOURS[self.detected_classes.get(name, PlayerClass.UNKNOWN)]
            for name in names
        ]
        bar_values = [p.total_spent for p in players]

        width = 3
        height = len(players) // width + 2
        specs = [[{"type": "xy", "colspan": width}] + [None] * (width - 1)]
        specs.extend([[{"type": "domain"}] * width] * (height - 1))
        bar_chart_height = 400
        pie_chart_height = 500

        fig = make_subplots(
            rows=height,
            cols=width,
            row_heights=[bar_chart_height] + [pie_chart_height] * (height - 1),
            subplot_titles=[None] + names,
            specs=specs,
        )

        fig.add_trace(
            go.Bar(
                x=names,
                y=bar_values,
                marker=dict(color=colors),
                name="Gold spent",
                showlegend=False,
                text=[v.to_string(short=True) for v in bar_values],
                textposition="outside",
            ),
            row=1,
            col=1,
        )

        for pos, player in enumerate(players):
            item_costs = [items.total_price for items in player.consumables]
            item_texts = [
                f"x{items.amount}, {items.total_price.to_string(short=True)}"
                for items in player.consumables
            ]

            fig.add_trace(
                go.Pie(
                    labels=[c.item_name for c in player.consumables],
                    values=item_costs,
                    text=item_texts,
                    showlegend=False,
                    textposition="inside",
                    textinfo="label+percent+text",
                    name=player.name,
                ),
                row=(pos // width) + 2,
                col=(pos % width) + 1,
            )

        fig.update_layout(
            title=self.title,
            template="plotly_dark",
            plot_bgcolor=self.BACKGROUND_COLOR,
            paper_bgcolor=self.BACKGROUND_COLOR,
            title_x=0.5,
            height=bar_chart_height + (pie_chart_height * height - 1),
        )

        bg_script = f'document.body.style.backgroundColor = "{self.BACKGROUND_COLOR}"; '
        output = fig.to_html(post_script=[bg_script])

        filename = output_file or self.DEFAULT_FILENAME
        filepath = Path(filename).with_suffix(".html")

        if check_existing_file(filepath):
            while check_existing_file(
                filepath := filepath.with_stem(f"{filename}_{str(uuid4())[-4:]}")
            ):
                pass

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"Infographic saved to: {filepath}")


def parse_line(app, line):
    try:
        if line == "\n":
            return False

        # no ts, nothing to do
        p_ts_end = line.find("  ")
        if p_ts_end == -1:
            return False

        tree = app.parser.parse(line, p_ts_end)
        if not tree:
            return False

        return process_tree(app, line, tree)

    except ParserError:
        # parse errors ignored to try different strategies
        # print(line)
        # print(app.parser.parse(line))
        # raise
        return False

    except Exception:
        logging.exception(line)
        raise


def process_tree(app, line, tree: Tree):
    """
    returns True to mark line as processed
    """
    timestamp = tree.children[0]
    subtree = tree.children[1]

    timestamp_unix = app.timestamp_parser.parse(timestamp)

    # inline everything to reduce funcalls
    # for same reason not using visitors to traverse the parse tree
    if subtree.data == TreeType.GAINS_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        stackcount = int(subtree.children[2].value)

        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
        app.spell_count.add_stackcount(
            line_type=subtree.data,
            name=name,
            spell=spellname,
            stackcount=stackcount,
        )
        app.proc_count.add(line_type=subtree.data, name=name, spell=spellname)

        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1

        if spellname in BUFF_SPELL:
            app.player_detect[name].add("buff: " + spellname)

        if spellname in TRINKET_SPELL_SET:
            app.player_detect[name].add("trinket: " + spellname)

        if spellname == "Armor Shatter":
            app.annihilator.add(line)
        if spellname == "Flame Buffet":
            app.flamebuffet.add(line)

        if name == "Princess Huhuran" and spellname in {"Frenzy", "Berserk"}:
            app.huhuran.add(line)
        if name == "Gluth" and spellname == "Frenzy":
            app.gluth.add(line)

        spellname_canonical = rename_spell(spellname, subtree.data)
        app.ability_timeline.add(
            source=name,
            target=name,
            spellname=spellname_canonical,
            line_type=subtree.data,
            timestamp_unix=timestamp_unix,
            amount=0,
        )

        return True
    elif subtree.data == TreeType.GAINS_RAGE_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[3].value

        app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)
        app.proc_count.add(line_type=subtree.data, name=name, spell=spellname)

        if spellname == "Unbridled Wrath":
            amount = int(subtree.children[1].value)
            app.proc_count.add_unbridled_wrath(amount=amount, name=name)

        spellname_canonical = rename_spell(spellname, subtree.data)
        app.ability_timeline.add(
            source=name,
            target=name,
            spellname=spellname_canonical,
            line_type=subtree.data,
            timestamp_unix=timestamp_unix,
            amount=0,
        )

        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1
        return True
    elif subtree.data == TreeType.GAINS_ENERGY_LINE:
        return True
    elif subtree.data == TreeType.GAINS_HEALTH_LINE:
        targetname = subtree.children[0].value
        amount = int(subtree.children[1].value)
        name = subtree.children[2].value
        spellname = subtree.children[3].value

        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)

        app.healstore.add(name, targetname, spellname, amount, timestamp_unix)
        return True
    elif subtree.data == TreeType.USES_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[1].value

        consumable_item = RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname))
        if consumable_item:
            # Check if this is a superwow consumable
            if consumable_item.has_component(IgnoreStrategyComponent):
                return True  # Parsed and explicitly ignored
            if consumable_item.has_component(SuperwowComponent):
                app.player_superwow[name][consumable_item.name] += 1
                return True  # Parsed and staged for merge

        # If RAWSPELLNAME2CONSUMABLE.get found nothing or not a superwow consumable
        app.player_superwow_unknown[name][spellname] += 1
        return True

    elif subtree.data == TreeType.DIES_LINE:
        name = subtree.children[0].value
        app.death_count[name] += 1

        if name == "Princess Huhuran":
            app.huhuran.add(line)
        if name == "Gluth":
            app.gluth.add(line)

        return True
    elif subtree.data == TreeType.HEALS_LINE:
        is_crit = subtree.children[2].value == "critically"

        name = subtree.children[0].value
        spellname = subtree.children[1].value

        targetname = subtree.children[3].value
        amount = int(subtree.children[4].value)

        # rename
        if spellname == "Healing Potion":
            if is_crit:
                spellname = healpot_lookup(amount / 1.5)
            else:
                spellname = healpot_lookup(amount)

        # rename
        if spellname == "Rejuvenation Potion":
            if amount > 500:
                spellname = "Major Rejuvenation Potion"
            else:
                spellname = "Minor Rejuvenation Potion"

        spellname_canonical = rename_spell(spellname, line_type=subtree.data)

        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
        app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)

        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1

        app.healstore.add(name, targetname, spellname_canonical, amount, timestamp_unix)
        return True

    elif subtree.data == TreeType.GAINS_MANA_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[-1].value

        # rename
        if spellname == "Restore Mana":
            mana = int(subtree.children[1].value)
            spellname = manapot_lookup(mana)

        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1

        return True
    elif subtree.data == TreeType.DRAINS_MANA_LINE:
        return True
    elif subtree.data == TreeType.DRAINS_MANA_LINE2:
        return True
    elif subtree.data == TreeType.BEGINS_TO_CAST_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[-1].value

        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)

        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1

        if name == "Kel'Thuzad" and spellname == "Frostbolt":
            app.kt_frostbolt.begins_to_cast(line)

        return True
    elif subtree.data == TreeType.CASTS_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1

        if spellname == "Sunder Armor":
            if len(subtree.children) < 3:
                # a mystery sunder armor with no target
                targetname = "unknown"
            else:
                targetname = subtree.children[2].value
            if targetname in KNOWN_BOSSES:
                spellname += " (boss)"

        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
        app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)

        if spellname == "Wild Polymorph":
            app.nef_wild_polymorph.add(line)

        if spellname == "Death by Peasant":
            app.huhuran.add(line)

        spellname_canonical = rename_spell(spellname, subtree.data)

        if len(subtree.children) == 3:
            targetname = subtree.children[2].value

            app.ability_timeline.add(
                source=name,
                target=targetname,
                spellname=spellname_canonical,
                line_type=subtree.data,
                timestamp_unix=timestamp_unix,
                amount=0,
            )

            if spellname == "Tranquilizing Shot" and targetname == "Princess Huhuran":
                app.huhuran.add(line)
            if spellname == "Tranquilizing Shot" and targetname == "Gluth":
                app.gluth.add(line)
        else:
            # self cast or no target
            app.ability_timeline.add(
                source=name,
                target=name,
                spellname=spellname_canonical,
                line_type=subtree.data,
                timestamp_unix=timestamp_unix,
                amount=0,
            )

        if name == "Kel'Thuzad" and spellname == "Shadow Fissure":
            app.kt_shadowfissure.add(line)

        return True
    elif subtree.data == TreeType.COMBATANT_INFO_LINE:
        return True
    elif subtree.data == TreeType.CONSOLIDATED_LINE:
        for entry in subtree.children:
            if entry.data == TreeType.CONSOLIDATED_PET:
                name = entry.children[0].value
                petname = entry.children[1].value
                app.pet_handler.add(name, petname)
                app.player_detect[name].add("pet: " + petname)
            else:
                # parse but ignore the other consolidated entries
                pass
        return True
    elif subtree.data == TreeType.HITS_ABILITY_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        targetname = subtree.children[2].value
        amount = int(subtree.children[3].value)

        spellname_canonical = rename_spell(spellname, line_type=subtree.data)

        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
        app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)
        app.ability_timeline.add(
            source=name,
            target=targetname,
            spellname=spellname_canonical,
            line_type=subtree.data,
            timestamp_unix=timestamp_unix,
            amount=amount,
        )

        if spellname in app.hits_consumable.COOLDOWNS:
            app.hits_consumable.update(name, spellname, timestamp_unix)

        if targetname == "Viscidus":
            app.viscidus.found()
            spell_damage_type = subtree.children[4]
            if spell_damage_type.value == "Frost":
                app.viscidus.add(name, spellname)

        if targetname == "Princess Huhuran":
            app.huhuran.found()

        if name == "Eye of C'Thun" and spellname == "Eye Beam":
            app.cthun_chain.add(timestamp_unix, line)

        if name == "Gluth" and spellname == "Decimate":
            app.gluth.add(line)

        if name == "Sir Zeliek" and spellname == "Holy Wrath":
            app.fourhm_chain.add(timestamp_unix, line)

        if spellname in INTERRUPT_SPELLS and targetname == "Kel'Thuzad":
            app.kt_frostbolt.add(line)

        if (
            name == "Kel'Thuzad"
            and spellname == "Frostbolt"
            and int(subtree.children[3].value) >= 4000
        ):
            app.kt_frostbolt.add(line)

        if name == "Kel'Thuzad" and spellname == "Frost Blast":
            app.kt_frostblast.add(line)

        if name == "Shadow Fissure" and spellname == "Void Blast":
            app.kt_shadowfissure.add(line)

        app.dmgstore.add(name, targetname, spellname_canonical, amount, timestamp_unix)
        app.dmgtakenstore.add(name, targetname, spellname_canonical, amount, timestamp_unix)

        # app.encounter_mobs.add(source=name, target=targetname, timestamp_unix=timestamp_unix)

        return True
    elif subtree.data == TreeType.HITS_AUTOATTACK_LINE:
        name = subtree.children[0].value
        target = subtree.children[1].value
        amount = int(subtree.children[2].value)
        action_verb = subtree.children[3].value

        app.dmgstore.add(name, target, "Auto Attack", amount, timestamp_unix)
        app.dmgtakenstore.add(name, target, "Auto Attack", amount, timestamp_unix)

        app.ability_timeline.add(
            source=name,
            target=target,
            spellname="Auto Attack",
            line_type=subtree.data,
            timestamp_unix=timestamp_unix,
            amount=amount,
        )

        # app.encounter_mobs.add(source=name, target=target, timestamp_unix=timestamp_unix)

        if name == "Guardian of Icecrown":
            app.kt_guardian.add(line)

        if action_verb == ActionValue.HITS:
            app.auto_attack_stats.add_hit(name)
        elif action_verb == ActionValue.BLOCK:
            app.auto_attack_stats.add_block(name)
        elif action_verb == ActionValue.CRITS:
            app.auto_attack_stats.add_crit(name)
        elif action_verb == ActionValue.GLANCE:
            app.auto_attack_stats.add_glance(name)
        else:
            return False

        return True
    elif subtree.data == TreeType.PARRY_ABILITY_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        targetname = subtree.children[2].value

        if spellname in INTERRUPT_SPELLS and targetname == "Kel'Thuzad":
            app.kt_frostbolt.parry(line)

        return True
    elif subtree.data == TreeType.PARRY_LINE:
        name = subtree.children[0].value
        app.auto_attack_stats.add_parry(name)
        return True
    elif subtree.data == TreeType.BLOCK_LINE:
        name = subtree.children[0].value
        app.auto_attack_stats.add_block(name)
        return True
    elif subtree.data == TreeType.MISSES_LINE:
        name = subtree.children[0].value
        app.auto_attack_stats.add_miss(name)
        return True
    elif subtree.data == TreeType.DODGES_LINE:
        name = subtree.children[0].value
        app.auto_attack_stats.add_dodge(name)
        return True
    elif subtree.data == TreeType.BLOCK_ABILITY_LINE:
        return True
    elif subtree.data == TreeType.INTERRUPTS_LINE:
        return True

    elif subtree.data == TreeType.RESIST_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        targetname = subtree.children[2].value

        if spellname in app.hits_consumable.COOLDOWNS:
            app.hits_consumable.update(name, spellname, timestamp_unix)

        if spellname == "Armor Shatter":
            app.annihilator.add(line)

        if name == "Eye of C'Thun" and spellname == "Eye Beam":
            app.cthun_chain.add(timestamp_unix, line)

        if name == "Sir Zeliek" and spellname == "Holy Wrath":
            app.fourhm_chain.add(timestamp_unix, line)

        if spellname in INTERRUPT_SPELLS and targetname == "Kel'Thuzad":
            app.kt_frostbolt.parry(line)

        return True
    elif subtree.data == TreeType.IMMUNE_ABILITY_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[1].value

        if spellname in app.hits_consumable.COOLDOWNS:
            app.hits_consumable.update(name, spellname, timestamp_unix)

        return True
    elif subtree.data == TreeType.IS_IMMUNE_ABILITY_LINE:
        targetname = subtree.children[0].value
        name = subtree.children[1].value
        spellname = subtree.children[2].value
        if spellname in app.hits_consumable.COOLDOWNS:
            app.hits_consumable.update(name, spellname, timestamp_unix)
        return True

    elif subtree.data == TreeType.IMMUNE_LINE:
        return True
    elif subtree.data == TreeType.AFFLICTED_LINE:
        targetname = subtree.children[0].value
        spellname = subtree.children[1].value

        app.class_detection.detect(line_type=subtree.data, name=targetname, spell=spellname)
        app.spell_count.add(line_type=subtree.data, name=targetname, spell=spellname)

        if spellname == "Armor Shatter":
            app.annihilator.add(line)
        if spellname == "Decimate":
            app.gluth.add(line)
        if spellname == "Frost Blast":
            app.kt_frostblast.add(line)

        if targetname == "Guardian of Icecrown":
            app.kt_guardian.add(line)

        spellname_canonical = rename_spell(spellname, line_type=subtree.data)
        app.ability_timeline.add(
            source=targetname,
            target=targetname,
            spellname=spellname_canonical,
            line_type=subtree.data,
            timestamp_unix=timestamp_unix,
            amount=0,
        )

        return True
    elif subtree.data == TreeType.IS_DESTROYED_LINE:
        return True
    elif subtree.data == TreeType.IS_ABSORBED_ABILITY_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[1].value

        if spellname == "Corrupted Healing":
            app.nef_corrupted_healing.add(line)

        if name == "Eye of C'Thun" and spellname == "Eye Beam":
            app.cthun_chain.add(timestamp_unix, line)

        if name == "Sir Zeliek" and spellname == "Holy Wrath":
            app.fourhm_chain.add(timestamp_unix, line)

        if name == "Kel'Thuzad" and spellname == "Frost Blast":
            app.kt_frostblast.add(line)

        return True
    elif subtree.data == TreeType.ABSORBS_ABILITY_LINE:
        targetname = subtree.children[0].value
        name = subtree.children[1].value
        spellname = subtree.children[2].value
        if spellname == "Corrupted Healing":
            app.nef_corrupted_healing.add(line)
        return True
    elif subtree.data == TreeType.ABSORBS_ALL_LINE:
        return True
    elif subtree.data == TreeType.FAILS_TO_DISPEL_LINE:
        return True
    elif subtree.data == TreeType.PET_BEGINS_EATING_LINE:
        return True
    elif subtree.data == TreeType.IS_DISMISSED_LINE:
        name = subtree.children[0].value
        petname = subtree.children[1].value
        app.pet_handler.add(name, petname)
        return True
    elif subtree.data == TreeType.IS_DISMISSED_LINE2:
        name, petname = subtree.children[0].value.split(" ", 1)
        if name[-2:] == "'s":
            name = name[:-2]
        app.pet_handler.add(name, petname)
        return True
    elif subtree.data == TreeType.GAINS_HAPPINESS_LINE:
        petname = subtree.children[0].value
        amount = subtree.children[1].value
        name = subtree.children[2].value
        app.pet_handler.add(name, petname)
        return True
    elif subtree.data == TreeType.REMOVED_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[1].value

        if name == "Princess Huhuran" and spellname == "Frenzy":
            app.huhuran.add(line)

        if name == "Gluth" and spellname == "Frenzy":
            app.gluth.add(line)

        return True
    elif subtree.data == TreeType.SUFFERS_LINE:
        targetname = subtree.children[0].value
        amount = int(subtree.children[1])
        if subtree.children[2].data == TreeType.SUFFERS_LINE_SOURCE:
            name = subtree.children[2].children[1].value
            spellname = subtree.children[2].children[2].value

            if spellname == "Corrupted Healing":
                app.nef_corrupted_healing.add(line)

            app.dmgstore.add(name, targetname, spellname, amount, timestamp_unix)
            app.dmgtakenstore.add(name, targetname, spellname, amount, timestamp_unix)

            spellname_canonical = rename_spell(spellname, line_type=subtree.data)
            app.ability_timeline.add(
                source=name,
                target=targetname,
                spellname=spellname_canonical,
                line_type=subtree.data,
                timestamp_unix=timestamp_unix,
                amount=amount,
            )
        else:
            # nosource
            pass

        return True
    elif subtree.data == TreeType.FADES_LINE:
        spellname = subtree.children[0].value
        targetname = subtree.children[1].value

        if spellname == "Armor Shatter":
            app.annihilator.add(line)
        if targetname == "Guardian of Icecrown":
            app.kt_guardian.add(line)

        spellname_canonical = rename_spell(spellname, line_type=subtree.data)
        app.ability_timeline.add(
            source=targetname,
            target=targetname,
            spellname=spellname_canonical,
            line_type=subtree.data,
            timestamp_unix=timestamp_unix,
            amount=0,
        )

        return True
    elif subtree.data == TreeType.SLAIN_LINE:
        return True
    elif subtree.data == TreeType.CREATES_LINE:
        return True
    elif subtree.data == TreeType.IS_KILLED_LINE:
        return True
    elif subtree.data == TreeType.PERFORMS_ON_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        targetname = subtree.children[2].value

        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1

        return True
    elif subtree.data == TreeType.PERFORMS_LINE:
        return True
    elif subtree.data == TreeType.BEGINS_TO_PERFORM_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[-1].value
        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
        app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)
        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1
        return True
    elif subtree.data == TreeType.GAINS_EXTRA_ATTACKS_LINE:
        name = subtree.children[0].value
        howmany = int(subtree.children[1].value)
        source = subtree.children[2].value
        app.proc_count.add_extra_attacks(howmany=howmany, name=name, source=source)
        return True
    elif subtree.data == TreeType.DODGES_LINE:
        return True
    elif subtree.data == TreeType.DODGE_ABILITY_LINE:
        return True
    elif subtree.data == TreeType.REFLECTS_DAMAGE_LINE:
        name = subtree.children[0].value
        amount = int(subtree.children[1].value)
        target = subtree.children[3].value
        app.dmgstore.add(name, target, "reflect", amount, timestamp_unix)
        app.dmgtakenstore.add(name, target, "reflect", amount, timestamp_unix)
        return True
    elif subtree.data == TreeType.CAUSES_DAMAGE_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        target = subtree.children[2].value
        amount = int(subtree.children[3].value)
        app.dmgstore.add(name, target, spellname, amount, timestamp_unix)
        app.dmgtakenstore.add(name, target, spellname, amount, timestamp_unix)

        spellname_canonical = rename_spell(spellname, line_type=subtree.data)
        app.ability_timeline.add(
            source=name,
            target=target,
            spellname=spellname_canonical,
            line_type=subtree.data,
            timestamp_unix=timestamp_unix,
            amount=amount,
        )
        return True
    elif subtree.data == TreeType.IS_REFLECTED_BACK_LINE:
        return True
    elif subtree.data == TreeType.MISSES_LINE:
        return True
    elif subtree.data == TreeType.MISSES_ABILITY_LINE:
        return True
    elif subtree.data == TreeType.FALLS_LINE:
        return True
    elif subtree.data == TreeType.NONE_LINE:
        return True
    elif subtree.data == TreeType.LAVA_LINE:
        return True
    elif subtree.data == TreeType.SLAYS_LINE:
        return True
    elif subtree.data == TreeType.WAS_EVADED_LINE:
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        targetname = subtree.children[2].value

        if spellname == "Wild Polymorph":
            app.nef_wild_polymorph.add(line)
        return True
    elif subtree.data == TreeType.EQUIPPED_DURABILITY_LOSS_LINE:
        return True

    return False


def parse_log(app, filename):
    app.techinfo.set_file_size(filename)

    with io.open(filename, encoding="utf8") as f:
        linecount = 0
        skiplinecount = 0
        for line in f:
            linecount += 1

            if parse_line(app, line):
                continue

            skiplinecount += 1

            app.unparsed_logger.log(line)

        app.techinfo.set_line_count(linecount)
        app.techinfo.set_skipped_line_count(skiplinecount)

        app.unparsed_logger.flush()
        app.unparsed_logger_fast.flush()


def generate_output(app):
    output = io.StringIO()

    print(
        """Notes:
    - The report is generated using the combat log, which is far from perfect.
    - Use the report as evidence something DID happen and keep in mind the data is not exhaustive. In other words the report DOES NOT cover everything.
    - Some events are missing because the person logging wasn't in the instance yet or was too far away. This means inferring something DID NOT happen may be hard or impossible and requires extra care.
    - This is called "open-world assumption" - missing information doesn't imply falsity.
    - Without superwow, many spells and consumables are not logged and can't be easily counted. Examples are jujus, many foods, mageblood and other mana consumables, lesser vs greater protection potions, gift of arthas etc.
    - Dragonbreath chili and goblin sappers have only "on hit" messages, so their usage is estimated based on timestamps and cooldowns.

""",
        file=output,
    )

    # remove pets from players
    for pet in app.pet_handler.get_all_pets():
        if pet in app.player_detect:
            del app.player_detect[pet]

    # add players detected
    for name in app.player_detect:
        app.player[name]

    # remove unknowns from class detection
    app.class_detection.remove_unknown()

    # merge superwow extra data so everything else can see it
    app.merge_superwow_consumables.merge()

    # calculate consumables
    app.consumables_accumulator.calculate()

    app.print_consumables.print(output)

    app.sunder_armor_summary.print(output)
    app.cooldown_summary.print(output)
    app.proc_summary.print(output)
    app.auto_attack_summary.print(output)

    # app.dmgstore.print_alphabetic(output)

    app.annihilator.print(output)
    app.flamebuffet.print(output)

    # bwl
    app.nef_corrupted_healing.print(output)
    app.nef_wild_polymorph.print(output)
    # aq
    app.viscidus.print(output)
    app.huhuran.print(output)
    app.cthun_chain.print(output)
    # naxx
    app.gluth.print(output)
    app.fourhm_chain.print(output)
    app.kt_shadowfissure.print(output)
    app.kt_frostbolt.print(output)
    app.kt_frostblast.print(output)
    # app.kt_guardian.print(output)

    app.pet_handler.print(output)
    app.class_detection.print(output)

    app.techinfo.print(output)

    return output


def write_output(
    output,
    write_summary,
):
    if write_summary:
        filename = "summary.txt"
        with open(filename, "wb") as f:
            f.write(output.getvalue().encode("utf8"))
            print("writing summary to", filename)
    else:
        print(output.getvalue())


def get_user_input(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "logpath",
        help="path to WoWCombatLog.txt or an url like https://turtlogs.com/viewer/8406/base?history_state=1",
    )
    parser.add_argument(
        "--pastebin",
        action="store_true",
        help="upload result to a pastebin and return the url",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="used with --pastebin. open the pastebin url with your browser",
    )

    parser.add_argument(
        "--write-summary",
        action="store_true",
        help="writes output to summary.txt instead of the console",
    )
    parser.add_argument(
        "--write-consumable-totals-csv",
        action="store_true",
        help="also writes consumable-totals.csv (name, copper, deaths)",
    )
    parser.add_argument(
        "--write-damage-output",
        action="store_true",
        help="writes output to damage-output.txt",
    )
    parser.add_argument(
        "--write-healing-output",
        action="store_true",
        help="writes output to healing-output.txt",
    )
    parser.add_argument(
        "--write-damage-taken-output",
        action="store_true",
        help="writes output to damage-taken-output.txt",
    )
    parser.add_argument(
        "--write-ability-timeline-output",
        action="store_true",
        help="writes output to ability-timeline.txt",
    )
    parser.add_argument(
        "--write-encounter-mobs-output",
        action="store_true",
        help="writes output to encounter-mobs.txt",
    )

    parser.add_argument(
        "--prices-server",
        choices=["nord", "telabim", "ambershire"],
        default="nord",
        help="specify which server price data to use",
    )

    parser.add_argument(
        "--visualize",
        action="store_true",
        required=False,
        help="Generate visual infographic",
    )
    parser.add_argument(
        "--compare-players",
        nargs=2,
        metavar=("PLAYER1", "PLAYER2"),
        required=False,
        help="compare 2 players, output the difference in compare-players.txt",
    )

    parser.add_argument(
        "--expert-log-unparsed-lines",
        action="store_true",
        help="create an unparsed.txt with everything that was not parsed",
    )
    parser.add_argument(
        "--expert-write-web-prices",
        action="store_true",
        help="writes output to prices-web.json",
    )
    parser.add_argument(
        "--expert-disable-web-prices",
        action="store_true",
        help="don't download price data",
    )
    parser.add_argument(
        "--expert-deterministic-logs",
        action="store_true",
        help="disable environmental outputs",
    )
    parser.add_argument("--expert-log-superwow-merge", action="store_true")

    args = parser.parse_args(argv)

    return args


class IxioUploader:
    def upload(self, output):
        data = output.getvalue().encode("utf8")

        username, password = "summarize_consumes", "summarize_consumes"
        auth = requests.auth.HTTPBasicAuth(username, password)
        response = requests.post(
            url="http://ix.io",
            files={"f:1": data},
            auth=auth,
            timeout=30,
        )
        print(response.text)
        if "already exists" in response.text:
            return None
        if "down for DDOS" in response.text:
            return None
        if "ix.io is taking a break" in response.text:
            return None
        if response.status_code != 200:
            return None
        url = response.text.strip().split("\n")[-1]
        return url


class RpasteUploader:
    def upload(self, output):
        data = output.getvalue().encode("utf8")
        response = requests.post(
            url="https://rpa.st/curl",
            data={"raw": data, "expiry": "forever"},
            timeout=30,
        )
        if response.status_code != 200:
            print(response.text)
            return None
        lines = response.text.splitlines()
        for line in lines:
            if "Raw URL" in line:
                url = line.split()[-1]
                return url


class BpasteUploader:
    def upload(self, output):
        data = output.getvalue().encode("utf8")
        response = requests.post(
            # url='https://bpaste.net/curl',
            url="https://bpa.st/curl",
            data={"raw": data, "expiry": "1month"},
            timeout=30,
        )
        if response.status_code != 200:
            print(response.text)
            return None
        lines = response.text.splitlines()
        for line in lines:
            if "Raw URL" in line:
                url = line.split()[-1]
                return url


def upload_pastebin(output):
    url = BpasteUploader().upload(output)
    if not url:
        url = RpasteUploader().upload(output)
    if not url:
        url = IxioUploader().upload(output)
    if url:
        print("pastebin url", url)
    else:
        print("couldn't get a pastebin url")
    return url


def open_browser(url):
    print(f"opening browser with {url}")
    webbrowser.open(url)


class LogDownloader:
    def __init__(self):
        self.output_name = "summarize-consumes-turtlogs.txt"

    def try_download(self, filename):
        output_name = self.output_name
        if os.path.exists(filename):
            return filename

        urlprefixes = [
            "https://www.turtlogs.com/viewer/",
            "https://turtlogs.com/viewer/",
        ]
        found = False
        for urlprefix in urlprefixes:
            if filename.startswith(urlprefix):
                newfilename = filename[len(urlprefix) :]
                found = True
                break
        if not found:
            return filename

        try:
            logid = newfilename.split("/")[0]
            logid = int(logid)
            resp = requests.get(f"https://turtlogs.com/API/instance/export/{logid}")
            resp.raise_for_status()

            upload_id = resp.json()["upload_id"]

            resp = requests.get(f"https://www.turtlogs.com/uploads/upload_{upload_id}.zip")
            resp.raise_for_status()

            zip_buffer = io.BytesIO(resp.content)

            with zipfile.ZipFile(zip_buffer) as zip_file:
                file_list = zip_file.namelist()

                if not file_list:
                    raise ValueError("ZIP file is empty")

                text_file_name = file_list[0]

                with zip_file.open(text_file_name) as text_file:
                    content = text_file.read()

                with open(output_name, "wb") as output_file:
                    print("writing downloaded log to", output_name)
                    output_file.write(content)
                return output_name

        except ValueError:
            pass
        return filename


class MergeSuperwowConsumables:
    def __init__(
        self,
        player,
        player_superwow,
        player_superwow_unknown,
        expert_log_superwow_merge,
    ):
        self.player = player
        self.player_superwow = player_superwow
        self.player_superwow_unknown = player_superwow_unknown
        self.logfile = None
        self.filename = "superwow-merge.txt"
        if expert_log_superwow_merge:
            self.logfile = open(self.filename, "w")

    def log(self, txt):
        if not self.logfile:
            return
        print(txt, file=self.logfile)

    def merge(self):
        if self.logfile:
            print("writing superwow merge to", self.filename)

        # note that both player and player_superwow map a canonical consumable
        # name (from all_defined_consumable_items) to its count.
        # you can investigate eg. the uses_line and gains_line code to
        # convince yourself it's true
        #
        # so the c and c_swow names are only different in how they are used.
        # c is used for the native counts in player
        # c_swow is used for the superwow counts in player_superwow
        #
        # it follows that when c == c_swow, we are looking at the same consumable,
        # but with data from the native and superwow logs respectively.
        # so when c != c_swow, we are comparing different consumables. possibly
        # an ambiguous one and a more specific superwow one.

        for player in self.player_superwow:
            consumables_swow = set(self.player_superwow[player])
            consumables = set(self.player[player])
            for c_swow in consumables_swow:
                spell = NAME2CONSUMABLE.get(c_swow)
                if spell is None:
                    self.log(f"impossible! consumable not found {c_swow}")
                    continue

                if spell.has_component(SafeStrategyComponent):
                    if self.player[player].get(c_swow, 0):
                        self.log(f"impossible! consumable not safe {spell}")
                    self.player[player][c_swow] = self.player_superwow[player][c_swow]
                    del self.player_superwow[player][c_swow]

                elif spell.has_component(EnhanceStrategyComponent):
                    self.player[player][c_swow] = max(
                        self.player_superwow[player][c_swow], self.player[player][c_swow]
                    )
                    del self.player_superwow[player][c_swow]

                elif spell.has_component(OverwriteStrategyComponent):
                    # will try to delete the native counts with the old name and use the new name coming from superwow
                    # eg. the prot pots have non-specific native names, but with superwow the specific name shows up
                    strategy_comp = spell.get_components(OverwriteStrategyComponent)[0]
                    target_name = strategy_comp.target_consumable_name

                    if (
                        target_name != c_swow
                        and self.player[player].get(target_name, 0)
                        > self.player_superwow[player][c_swow]
                    ):
                        self.log(f"partial merge (overwrite). {player} {target_name} > {c_swow}")

                        remain = (
                            self.player[player][target_name] - self.player_superwow[player][c_swow]
                        )
                        self.player[player][target_name] = remain
                        self.player[player][c_swow] = self.player_superwow[player][c_swow]
                        del self.player_superwow[player][c_swow]

                        continue

                    self.player[player].pop(target_name, None)  # might not exist
                    self.player[player][c_swow] = self.player_superwow[player][c_swow]
                    del self.player_superwow[player][c_swow]

                else:
                    self.log(f"{c_swow} not known??")
                    continue

        all_unknown = set()
        for player, consumables in self.player_superwow_unknown.items():
            self.log(f"unknown consumables for {player}: {consumables}")
            for cons in consumables:
                all_unknown.add(cons)

        self.log("all unknown suggestions:")
        for cons in all_unknown:
            self.log(repr({cons: cons}))

        def printer(player):
            for player, cons in player.items():
                for cname, count in cons.items():
                    self.log(f"{player} {cname} {count}")

        self.log("data dumps:")
        # self.log(f'self.player:')
        # printer(self.player)
        self.log("self.player_superwow:")
        printer(self.player_superwow)
        self.log("self.player_superwow_unknown:")
        printer(self.player_superwow_unknown)


def main(argv):
    args = get_user_input(argv)

    time_start = time.time()
    app = create_app(
        time_start=time_start,
        expert_log_unparsed_lines=args.expert_log_unparsed_lines,
        prices_server=args.prices_server,
        expert_disable_web_prices=args.expert_disable_web_prices,
        expert_deterministic_logs=args.expert_deterministic_logs,
        expert_log_superwow_merge=args.expert_log_superwow_merge,
        write_encounter_mobs_output=args.write_encounter_mobs_output,
    )

    logpath = app.log_downloader.try_download(filename=args.logpath)

    parse_log(app, filename=logpath)

    output = generate_output(app)

    if args.write_consumable_totals_csv:

        def feature():
            output = io.StringIO()
            app.print_consumable_totals_csv.print(output)

            filename = "consumable-totals.csv"
            with open(filename, "wb") as f:
                f.write(output.getvalue().encode("utf8"))
                print("writing consumable totals to", filename)

        feature()

    if args.compare_players:

        def feature():
            player1, player2 = args.compare_players
            player1 = player1.capitalize()
            player2 = player2.capitalize()

            output = io.StringIO()
            app.dmgstore.print_compare_players(player1=player1, player2=player2, output=output)

            filename = "compare-players.txt"
            with open(filename, "wb") as f:
                print("writing comparison of players to", filename)
                f.write(output.getvalue().encode("utf8"))

        feature()

    if args.write_damage_output:

        def feature():
            output = io.StringIO()
            app.dmgstore.print_damage(output=output)
            filename = "damage-output.txt"
            with open(filename, "wb") as f:
                print("writing damage output to", filename)
                f.write(output.getvalue().encode("utf8"))
                if args.pastebin:
                    upload_pastebin(output)

        feature()

    if args.write_healing_output:

        def feature():
            output = io.StringIO()
            app.healstore.print_damage(output=output)
            filename = "healing-output.txt"
            with open(filename, "wb") as f:
                print("writing healing output to", filename)
                f.write(output.getvalue().encode("utf8"))
                if args.pastebin:
                    upload_pastebin(output)

        feature()

    if args.write_damage_taken_output:

        def feature():
            output = io.StringIO()
            app.dmgtakenstore.print_damage_taken(output=output)
            filename = "damage-taken-output.txt"
            with open(filename, "wb") as f:
                print("writing damage taken output to", filename)
                f.write(output.getvalue().encode("utf8"))
                if args.pastebin:
                    upload_pastebin(output)

        feature()

    if args.write_ability_timeline_output:

        def feature():
            output = io.StringIO()
            app.ability_timeline.print(output)
            filename = "ability-timeline.txt"
            with open(filename, "wb") as f:
                print("writing ability timeline output to", filename)
                f.write(output.getvalue().encode("utf8"))
                if args.pastebin:
                    upload_pastebin(output)

        feature()

    if args.write_encounter_mobs_output:

        def feature():
            output = io.StringIO()
            app.encounter_mobs.print(output)
            filename = "encounter-mobs.txt"
            with open(filename, "wb") as f:
                print("writing encounter mobs output to", filename)
                f.write(output.getvalue().encode("utf8"))
                if args.pastebin:
                    upload_pastebin(output)

        feature()

    if args.visualize:
        app.infographic.generate(output_file=Path(logpath).stem)

    if args.expert_write_web_prices:

        def feature():
            prices = app.web_price_provider.load()
            filename = "prices-web.json"
            with open(filename, "w", newline="") as f:
                print("writing web prices to", filename)
                json.dump(prices, f, indent=4)

        feature()

    write_output(output, write_summary=args.write_summary)
    if not args.pastebin:
        return
    url = upload_pastebin(output)

    if not args.open_browser:
        return
    if not url:
        return
    open_browser(url)


if __name__ == "__main__":
    main(sys.argv[1:])
