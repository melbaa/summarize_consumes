import argparse
import collections
import csv
import dataclasses
import datetime
import functools
import io
import itertools
import json
import logging
import os
import re
import time
import webbrowser
import sys
import zipfile
from datetime import datetime as dt
from enum import Enum
from pathlib import Path
from typing import Dict
from typing import List
from typing import Tuple
from uuid import uuid4

import humanize
import lark
import requests
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from typing_extensions import Self

from melbalabs.summarize_consumes import grammar
from melbalabs.summarize_consumes.consumable import Consumable
from melbalabs.summarize_consumes.consumable import SuperwowConsumable
from melbalabs.summarize_consumes.consumable import IgnoreStrategy
from melbalabs.summarize_consumes.consumable import SafeStrategy
from melbalabs.summarize_consumes.consumable import EnhanceStrategy
from melbalabs.summarize_consumes.consumable import OverwriteStrategy
from melbalabs.summarize_consumes.consumable import DirectPrice
from melbalabs.summarize_consumes.consumable import PriceFromComponents
from melbalabs.summarize_consumes.consumable import NoPrice
import melbalabs.summarize_consumes.package as package


LarkError = lark.LarkError
CURRENT_YEAR = datetime.datetime.now().year


class PlayerClass(Enum):
    DRUID = "druid"
    HUNTER = "hunter"
    MAGE = "mage"
    PALADIN = "paladin"
    PRIEST = "priest"
    ROGUE = "rogue"
    SHAMAN = "shaman"
    WARLOCK = "warlock"
    WARRIOR = "warrior"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, class_string: str) -> "PlayerClass":
        # lowercase is the only extra processing. everything else should be an error
        return cls(class_string.lower())


class App:
    pass


class TreeTransformer(lark.Transformer):
    def multiword(self, args):
        result = ""
        for arg in args:
            result += arg
        return lark.Token("MULTIWORD_T", result)

    def PARENS_INT(self, args):
        return lark.Token("INT_T", args[2:-1])


@functools.cache
def create_parser(grammar: str, debug):
    parser = lark.Lark(
        grammar,
        parser="lalr",
        debug=debug,
        # ambiguity='explicit',  # not in lalr
        strict=True,
        transformer=TreeTransformer(),
    )

    return parser


@functools.cache
def dl_price_data(prices_server):
    try:
        URLS = {
            "nord": "https://melbalabs.com/static/twowprices.json",
            "telabim": "https://melbalabs.com/static/twowprices-telabim.json",
        }
        url = URLS[prices_server]
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.exceptions.RequestException:
        logging.warning("web prices not available")
        return None


def create_app(
    time_start,
    expert_log_unparsed_lines,
    prices_server,
    expert_disable_web_prices,
    expert_deterministic_logs,
    expert_write_lalr_states,
    expert_log_superwow_merge,
):
    app = App()

    lark_debug = False
    if expert_log_unparsed_lines or expert_write_lalr_states:
        lark.logger.setLevel(logging.DEBUG)
        lark_debug = True

    app.parser = create_parser(grammar=grammar.grammar, debug=lark_debug)

    if expert_write_lalr_states:

        def feature():
            parser = app.parser
            states = parser.parser.parser.parser.parse_table.states
            filename = "lalr-states.txt"
            with open(filename, "w") as f:
                for terminal in parser.terminals:
                    print("  ", terminal.name, f"'{terminal.pattern.value}'", file=f)
                print(file=f)

                for state, actions in states.items():
                    print(state, file=f)
                    for token, (action, arg) in actions.items():
                        print("  ", token, action, arg, file=f)
                    print(file=f)
            print("writing lalr table to", filename)

        feature()

    if expert_log_unparsed_lines:
        app.unparsed_logger = UnparsedLogger(filename="unparsed.txt")
    else:
        app.unparsed_logger = NullLogger(filename="unparsed.txt")

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


def parse_ts2unixtime(timestamp):
    month, day, hour, minute, sec, ms = timestamp.children
    month = int(month)
    day = int(day)
    hour = int(hour)
    minute = int(minute)
    sec = int(sec)
    ms = int(ms)
    timestamp = dt(
        year=CURRENT_YEAR,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=sec,
        tzinfo=datetime.timezone.utc,
    )
    unixtime = timestamp.timestamp()  # seconds
    return unixtime


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
    COOLDOWNS = {
        "Dragonbreath Chili": 10 * 60,
        "Goblin Sapper Charge": 5 * 60,
        "Stratholme Holy Water": 1 * 60,
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
            # probably a new year, will ignore for now
            raise RuntimeError("fixme")


_purple_lotus = Consumable(name="Purple Lotus", price=DirectPrice(itemid=8831))
_large_brilliant_shard = Consumable(name="Large Brilliant Shard", price=DirectPrice(itemid=14344))
_scorpok_pincer = Consumable(name="Scorpok Pincer", price=DirectPrice(itemid=8393))
_blasted_boar_lung = Consumable(name="Blasted Boar Lung", price=DirectPrice(itemid=8392))
_snickerfang_jowl = Consumable(name="Snickerfang Jowl", price=DirectPrice(itemid=8391))
_basilisk_brain = Consumable(name="Basilisk Brain", price=DirectPrice(itemid=8394))
_vulture_gizzard = Consumable(name="Vulture Gizzard", price=DirectPrice(itemid=8396))
_zulian_coin = Consumable(name="Zulian Coin", price=DirectPrice(itemid=19698))
_deeprock_salt = Consumable(name="Deeprock Salt", price=DirectPrice(itemid=8150))
_essence_of_fire = Consumable(name="Essence of Fire", price=DirectPrice(itemid=7078))
_larval_acid = Consumable(name="Larval Acid", price=DirectPrice(itemid=18512))
_small_dream_shard = Consumable(name="Small Dream Shard", price=DirectPrice(itemid=61198))
_bright_dream_shard = Consumable(name="Bright Dream Shard", price=DirectPrice(itemid=61199))
_green_power_crystal = Consumable(name="Green Power Crystal", price=DirectPrice(itemid=11185))
_blue_power_crystal = Consumable(name="Blue Power Crystal", price=DirectPrice(itemid=11184))
_red_power_crystal = Consumable(name="Red Power Crystal", price=DirectPrice(itemid=11186))
_yellow_power_crystal = Consumable(name="Yellow Power Crystal", price=DirectPrice(itemid=11188))


all_defined_consumable_items: List[Consumable] = [
    _purple_lotus,
    _large_brilliant_shard,
    _scorpok_pincer,
    _blasted_boar_lung,
    _snickerfang_jowl,
    _basilisk_brain,
    _vulture_gizzard,
    _zulian_coin,
    _deeprock_salt,
    _essence_of_fire,
    _larval_acid,
    _small_dream_shard,
    _bright_dream_shard,
    _green_power_crystal,
    _blue_power_crystal,
    _red_power_crystal,
    _yellow_power_crystal,
    Consumable(
        name="Crystal Ward",
        price=PriceFromComponents(
            charges=6,
            components=[
                (_green_power_crystal, 10),
                (_red_power_crystal, 10),
            ],
        ),
        spell_aliases=[("gains_line", "Crystal Ward")],
    ),
    SuperwowConsumable(
        name="Crystal Force",
        price=PriceFromComponents(
            charges=6,
            components=[
                (_green_power_crystal, 10),
                (_blue_power_crystal, 10),
            ],
        ),
        spell_aliases=[("gains_line", "Crystal Force"), ('uses_line', 'Crystal Force')],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Crystal Spire",
        price=PriceFromComponents(
            charges=6,
            components=[
                (_blue_power_crystal, 10),
                (_yellow_power_crystal, 10),
            ],
        ),
        spell_aliases=[("gains_line", "Crystal Spire"), ('uses_line', 'Crystal Spire')],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Crystal Charge",
        price=PriceFromComponents(
            charges=6,
            components=[
                (_yellow_power_crystal, 10),
                (_red_power_crystal, 10),
            ],
        ),
        spell_aliases=[("uses_line", "Crystal Charge")],
        strategy=SafeStrategy(),
    ),

    SuperwowConsumable(
        name="Brilliant Mana Oil",
        price=DirectPrice(charges=5, itemid=20748),
        spell_aliases=[
            ("begins_to_cast_line", "Brilliant Mana Oil"),
            ("uses_line", "Brilliant Mana Oil"),
        ],
        strategy=OverwriteStrategy(target_consumable_name="Brilliant Mana Oil"),
    ),
    Consumable(
        name="Lesser Mana Oil",
        price=DirectPrice(charges=5, itemid=20747),
        spell_aliases=[("begins_to_cast_line", "Lesser Mana Oil")],
    ),
    SuperwowConsumable(
        name="Blessed Wizard Oil",
        price=DirectPrice(itemid=23123),
        spell_aliases=[
            ("begins_to_cast_line", "Blessed Wizard Oil"),
            ("uses_line", "Blessed Wizard Oil"),
        ],
        strategy=OverwriteStrategy(target_consumable_name="Blessed Wizard Oil"),
    ),
    SuperwowConsumable(
        name="Brilliant Wizard Oil",
        price=DirectPrice(charges=5, itemid=20749),
        spell_aliases=[
            ("begins_to_cast_line", "Brilliant Wizard Oil"),
            ("uses_line", "Brilliant Wizard Oil"),
        ],
        strategy=OverwriteStrategy(target_consumable_name="Brilliant Wizard Oil"),
    ),
    SuperwowConsumable(
        name="Wizard Oil",
        price=DirectPrice(charges=5, itemid=20750),
        spell_aliases=[("begins_to_cast_line", "Wizard Oil"), ("uses_line", "Wizard Oil")],
        strategy=OverwriteStrategy(target_consumable_name="Wizard Oil"),
    ),
    Consumable(
        name="Frost Oil",
        price=DirectPrice(itemid=3829),
        spell_aliases=[("begins_to_cast_line", "Frost Oil")],
    ),
    SuperwowConsumable(
        name="Shadow Oil",
        price=DirectPrice(itemid=3824),
        spell_aliases=[("begins_to_cast_line", "Shadow Oil"), ("uses_line", "Shadow Oil")],
        strategy=OverwriteStrategy(target_consumable_name="Shadow Oil"),
    ),
    SuperwowConsumable(
        name="Rage of Ages (ROIDS)",
        price=PriceFromComponents(
            components=[
                (_scorpok_pincer, 1),
                (_blasted_boar_lung, 2),
                (_snickerfang_jowl, 3),
            ]
        ),
        spell_aliases=[("gains_line", "Rage of Ages"), ("uses_line", "Rage of Ages")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Strike of the Scorpok",
        price=PriceFromComponents(
            components=[
                (_blasted_boar_lung, 1),
                (_vulture_gizzard, 2),
                (_scorpok_pincer, 3),
            ]
        ),
        spell_aliases=[
            ("gains_line", "Strike of the Scorpok"),
            ("uses_line", "Ground Scorpok Assay"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Lung Juice Cocktail",
        price=PriceFromComponents(
            components=[
                (_basilisk_brain, 1),
                (_scorpok_pincer, 2),
                (_blasted_boar_lung, 3),
            ]
        ),
        spell_aliases=[("gains_line", "Spirit of the Boar"), ("uses_line", "Lung Juice Cocktail")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Infallible Mind (Cerebral Cortex Compound)",
        price=PriceFromComponents(
            components=[
                (_basilisk_brain, 10),
                (_vulture_gizzard, 2),
            ]
        ),
        spell_aliases=[
            ("gains_line", "Infallible Mind"),
            ("uses_line", "Cerebral Cortex Compound"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Sheen of Zanza",
        price=PriceFromComponents(components=[(_zulian_coin, 3)]),
        spell_aliases=[("gains_line", "Sheen of Zanza"), ("uses_line", "Sheen of Zanza")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Spirit of Zanza",
        price=PriceFromComponents(components=[(_zulian_coin, 3)]),
        spell_aliases=[("gains_line", "Spirit of Zanza"), ("uses_line", "Spirit of Zanza")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Swiftness of Zanza",
        price=PriceFromComponents(components=[(_zulian_coin, 3)]),
        spell_aliases=[("gains_line", "Swiftness of Zanza"), ("uses_line", "Swiftness of Zanza")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Powerful Smelling Salts",
        price=PriceFromComponents(
            components=[
                (_deeprock_salt, 4),
                (_essence_of_fire, 2),
                (_larval_acid, 1),
            ]
        ),
        spell_aliases=[
            ("performs_on_line", "Powerful Smelling Salts"),
            ("uses_line", "Powerful Smelling Salts"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Tea with Sugar",
        price=PriceFromComponents(components=[(_small_dream_shard, 1 / 5)]),
        spell_aliases=[("heals_line", "Tea"), ("uses_line", "Tea with Sugar")],
        strategy=OverwriteStrategy(target_consumable_name="Tea with Sugar"),
    ),
    Consumable(
        # superwow, but looks like native logs
        name="Emerald Blessing",
        price=PriceFromComponents(components=[(_bright_dream_shard, 1)]),
        spell_aliases=[("casts_line", "Emerald Blessing")],
    ),
    SuperwowConsumable(
        name="Hourglass Sand",
        price=DirectPrice(itemid=19183),
        spell_aliases=[("uses_line", "Hourglass Sand")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Restorative Potion",
        price=DirectPrice(itemid=9030),
        spell_aliases=[("gains_line", "Restoration"), ("uses_line", "Restorative Potion")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Flask of Chromatic Resistance",
        price=DirectPrice(itemid=13513),
        spell_aliases=[
            ("gains_line", "Chromatic Resistance"),
            ("uses_line", "Flask of Chromatic Resistance"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Flask of the Titans",
        price=DirectPrice(itemid=13510),
        spell_aliases=[("gains_line", "Flask of the Titans"), ("uses_line", "Flask of the Titans")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Flask of Supreme Power",
        price=DirectPrice(itemid=13512),
        spell_aliases=[("gains_line", "Supreme Power"), ("uses_line", "Flask of Supreme Power")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Flask of Distilled Wisdom",
        price=DirectPrice(itemid=13511),
        spell_aliases=[
            ("gains_line", "Distilled Wisdom"),
            ("uses_line", "Flask of Distilled Wisdom"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Flask of Petrification",
        price=DirectPrice(itemid=13506),
        spell_aliases=[("uses_line", "Flask of Petrification")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Fortitude",
        price=DirectPrice(itemid=3825),
        spell_aliases=[("gains_line", "Health II"), ("uses_line", "Elixir of Fortitude")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Bogling Root",
        price=DirectPrice(itemid=5206),
        spell_aliases=[("gains_line", "Fury of the Bogling"), ("uses_line", "Bogling Root")],
        strategy=EnhanceStrategy(),
    ),
    Consumable(
        name="Crystal Basilisk Spine",
        price=DirectPrice(itemid=1703),
        spell_aliases=[("gains_line", "Crystal Protection")],
    ),
    SuperwowConsumable(
        name="??? Elixir of the Sages ???",
        price=DirectPrice(itemid=13447),
        spell_aliases=[("gains_line", "Elixir of the Sages"), ("uses_line", "Elixir of the Sages")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Greater Agility",
        price=DirectPrice(itemid=9187),
        spell_aliases=[
            ("gains_line", "Greater Agility"),
            ("uses_line", "Elixir of Greater Agility"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Superior Defense",
        price=DirectPrice(itemid=13445),
        spell_aliases=[
            ("gains_line", "Greater Armor"),
            ("uses_line", "Elixir of Superior Defense"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Free Action Potion",
        price=DirectPrice(itemid=5634),
        spell_aliases=[("gains_line", "Free Action"), ("uses_line", "Free Action Potion")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Frost Power",
        price=DirectPrice(itemid=17708),
        spell_aliases=[("gains_line", "Frost Power"), ("uses_line", "Elixir of Frost Power")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Greater Arcane Elixir",
        price=DirectPrice(itemid=13454),
        spell_aliases=[
            ("gains_line", "Greater Arcane Elixir"),
            ("uses_line", "Greater Arcane Elixir"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Thistle Tea",
        price=DirectPrice(itemid=7676),
        spell_aliases=[("gains_line", "100 energy"), ("uses_line", "Thistle Tea")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Brute Force",
        price=DirectPrice(itemid=13453),
        spell_aliases=[
            ("gains_line", "Elixir of Brute Force"),
            ("uses_line", "Elixir of Brute Force"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Winterfall Firewater",
        price=DirectPrice(itemid=12820),
        spell_aliases=[
            ("gains_line", "Winterfall Firewater"),
            ("uses_line", "Winterfall Firewater"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Great Rage Potion",
        price=DirectPrice(itemid=5633),
        spell_aliases=[("gains_rage_line", "Great Rage"), ("uses_line", "Great Rage Potion")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Rage Potion",
        price=DirectPrice(itemid=5631),
        spell_aliases=[("gains_rage_line", "Rage"), ("uses_line", "Rage Potion")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Juju Power",
        price=DirectPrice(itemid=12431),
        spell_aliases=[("uses_line", "Juju Power")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Juju Flurry",
        price=DirectPrice(itemid=12430),
        spell_aliases=[("uses_line", "Juju Flurry")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Juju Might",
        price=DirectPrice(itemid=12436),
        spell_aliases=[("uses_line", "Juju Might")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Juju Guile",
        price=DirectPrice(itemid=12433),
        spell_aliases=[("uses_line", "Juju Guile")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Juju Escape",
        price=DirectPrice(itemid=12435),
        spell_aliases=[("uses_line", "Juju Escape")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Juju Ember",
        price=DirectPrice(itemid=12432),
        spell_aliases=[("uses_line", "Juju Ember")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Juju Chill",
        price=DirectPrice(itemid=12434),
        spell_aliases=[("uses_line", "Juju Chill")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Gurubashi Gumbo",
        price=DirectPrice(itemid=53015),
        spell_aliases=[("uses_line", "Gurubashi Gumbo")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Hardened Mushroom",
        price=DirectPrice(itemid=51717),
        spell_aliases=[("uses_line", "Hardened Mushroom")],
        strategy=OverwriteStrategy(target_consumable_name="Increased Stamina"),
    ),
    SuperwowConsumable(
        name="Oil of Immolation",
        price=DirectPrice(itemid=8956),
        spell_aliases=[("uses_line", "Oil of Immolation")],
        strategy=SafeStrategy(),
    ),
    Consumable(
        name="??? Lesser Stoneshield Potion ???",
        price=DirectPrice(itemid=4623),
        spell_aliases=[("gains_line", "Stoneshield")],
    ),
    SuperwowConsumable(
        name="Greater Stoneshield",
        price=DirectPrice(itemid=13455),
        spell_aliases=[
            ("gains_line", "Greater Stoneshield"),
            ("uses_line", "Greater Stoneshield Potion"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Lucidity Potion",
        price=DirectPrice(itemid=61225),
        spell_aliases=[("gains_line", "Lucidity Potion"), ("uses_line", "Lucidity Potion")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Mana Potion - Greater",
        price=DirectPrice(itemid=6149),
        spell_aliases=[("uses_line", "Greater Mana Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Restore Mana (mana potion)"),
    ),
    SuperwowConsumable(
        name="Mana Potion - Superior",
        price=DirectPrice(itemid=13443),
        spell_aliases=[("uses_line", "Superior Mana Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Restore Mana (mana potion)"),
    ),
    SuperwowConsumable(
        name="Mana Potion - Major",
        price=DirectPrice(itemid=13444),
        spell_aliases=[("uses_line", "Major Mana Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Restore Mana (mana potion)"),
    ),
    SuperwowConsumable(
        name="Healing Potion - Major",
        price=DirectPrice(itemid=13446),
        spell_aliases=[("uses_line", "Major Healing Potion")],
        strategy=EnhanceStrategy(),
    ),
    Consumable(name="Healing Potion - Superior", price=DirectPrice(itemid=3928)),
    SuperwowConsumable(
        name="Elixir of Giants",
        price=DirectPrice(itemid=9206),
        spell_aliases=[("gains_line", "Elixir of the Giants"), ("uses_line", "Elixir of Giants")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Rumsey Rum Black Label",
        price=DirectPrice(itemid=21151),
        spell_aliases=[
            ("gains_line", "Rumsey Rum Black Label"),
            ("uses_line", "Rumsey Rum Black Label"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Rumsey Rum Dark",
        price=DirectPrice(itemid=21114),
        spell_aliases=[("gains_line", "Rumsey Rum Dark"), ("uses_line", "Rumsey Rum Dark")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Elemental Sharpening Stone",
        price=DirectPrice(itemid=18262),
        spell_aliases=[
            ("begins_to_cast_line", "Sharpen Weapon - Critical"),
            ("uses_line", "Elemental Sharpening Stone"),
        ],
        strategy=OverwriteStrategy(target_consumable_name="Elemental Sharpening Stone"),
    ),
    SuperwowConsumable(
        name="Consecrated Sharpening Stone",
        price=DirectPrice(itemid=23122),
        spell_aliases=[
            ("begins_to_cast_line", "Consecrated Weapon"),
            ("uses_line", "Consecrated Sharpening Stone"),
        ],
        strategy=OverwriteStrategy(target_consumable_name="Consecrated Sharpening Stone"),
    ),
    SuperwowConsumable(
        name="Invulnerability",
        price=DirectPrice(itemid=3387),
        spell_aliases=[
            ("gains_line", "Invulnerability"),
            ("uses_line", "Limited Invulnerability Potion"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Dragonbreath Chili",
        price=DirectPrice(itemid=12217),
        spell_aliases=[("uses_line", "Dragonbreath Chili")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Dreamtonic",
        price=DirectPrice(itemid=61423),
        spell_aliases=[("gains_line", "Dreamtonic"), ("uses_line", "Dreamtonic")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Goblin Sapper Charge",
        price=DirectPrice(itemid=10646),
        spell_aliases=[("uses_line", "Goblin Sapper Charge")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Medivh's Merlot Blue Label",
        price=DirectPrice(itemid=61175),
        spell_aliases=[
            ("gains_line", "Medivh's Merlot Blue Label"),
            ("uses_line", "Medivhs Merlot Blue Label"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Medivh's Merlot",
        price=DirectPrice(itemid=61174),
        spell_aliases=[("gains_line", "Medivh's Merlot"), ("uses_line", "Medivhs Merlot")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Greater Arcane Protection Potion",
        price=DirectPrice(itemid=13461),
        spell_aliases=[("uses_line", "Greater Arcane Protection Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Arcane Protection"),
    ),
    SuperwowConsumable(
        name="Greater Holy Protection Potion",
        price=DirectPrice(itemid=13460),
        spell_aliases=[("uses_line", "Greater Holy Protection Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Holy Protection"),
    ),
    SuperwowConsumable(
        name="Greater Shadow Protection Potion",
        price=DirectPrice(itemid=13459),
        spell_aliases=[("uses_line", "Greater Shadow Protection Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Shadow Protection"),
    ),
    SuperwowConsumable(
        name="Greater Nature Protection Potion",
        price=DirectPrice(itemid=13458),
        spell_aliases=[("uses_line", "Greater Nature Protection Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Nature Protection"),
    ),
    SuperwowConsumable(
        name="Greater Fire Protection Potion",
        price=DirectPrice(itemid=13457),
        spell_aliases=[("uses_line", "Greater Fire Protection Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Fire Protection"),
    ),
    SuperwowConsumable(
        name="Greater Frost Protection Potion",
        price=DirectPrice(itemid=13456),
        spell_aliases=[("uses_line", "Greater Frost Protection Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Frost Protection"),
    ),
    SuperwowConsumable(
        name="Holy Protection Potion",
        price=DirectPrice(itemid=6051),
        spell_aliases=[("uses_line", "Holy Protection Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Holy Protection"),
    ),
    SuperwowConsumable(
        name="Shadow Protection Potion",
        price=DirectPrice(itemid=6048),
        spell_aliases=[("uses_line", "Shadow Protection Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Shadow Protection"),
    ),
    SuperwowConsumable(
        name="Nature Protection Potion",
        price=DirectPrice(itemid=6052),
        spell_aliases=[("uses_line", "Nature Protection Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Nature Protection"),
    ),
    SuperwowConsumable(
        name="Fire Protection Potion",
        price=DirectPrice(itemid=6049),
        spell_aliases=[("uses_line", "Fire Protection Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Fire Protection"),
    ),
    SuperwowConsumable(
        name="Frost Protection Potion",
        price=DirectPrice(itemid=6050),
        spell_aliases=[("uses_line", "Frost Protection Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Frost Protection"),
    ),
    SuperwowConsumable(
        name="Dreamshard Elixir",
        price=DirectPrice(itemid=61224),
        spell_aliases=[("gains_line", "Dreamshard Elixir"), ("uses_line", "Dreamshard Elixir")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Dense Dynamite",
        price=DirectPrice(itemid=18641),
        spell_aliases=[("begins_to_cast_line", "Dense Dynamite"), ("uses_line", "Dense Dynamite")],
        strategy=OverwriteStrategy(target_consumable_name="Dense Dynamite"),
    ),
    SuperwowConsumable(
        name="Solid Dynamite",
        price=DirectPrice(itemid=10507),
        spell_aliases=[("begins_to_cast_line", "Solid Dynamite"), ("uses_line", "Solid Dynamite")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Gift of Arthas",
        price=DirectPrice(itemid=9088),
        spell_aliases=[("uses_line", "Gift of Arthas")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Thorium Grenade",
        price=DirectPrice(itemid=15993),
        spell_aliases=[
            ("begins_to_cast_line", "Thorium Grenade"),
            ("uses_line", "Thorium Grenade"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Iron Grenade",
        price=DirectPrice(itemid=4390),
        spell_aliases=[("begins_to_cast_line", "Iron Grenade"), ("uses_line", "Iron Grenade")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Grilled Squid",
        price=DirectPrice(itemid=13928),
        spell_aliases=[("uses_line", "Grilled Squid")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Greater Intellect",
        price=DirectPrice(itemid=9179),
        spell_aliases=[
            ("gains_line", "Greater Intellect"),
            ("uses_line", "Elixir of Greater Intellect"),
        ],
        strategy=EnhanceStrategy(),
    ),
    Consumable(
        name="Restore Mana (mana potion)",
        price=NoPrice(),
        spell_aliases=[("gains_mana_line", "Restore Mana")],
    ),
    SuperwowConsumable(
        name="Mana Potion - Combat",
        price=DirectPrice(itemid=18841),
        spell_aliases=[("uses_line", "Combat Mana Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Restore Mana (mana potion)"),
    ),
    SuperwowConsumable(
        name="Rejuvenation Potion - Major",
        price=DirectPrice(itemid=18253),
        spell_aliases=[("uses_line", "Major Rejuvenation Potion")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Rejuvenation Potion - Minor",
        price=DirectPrice(itemid=2456),
        spell_aliases=[("uses_line", "Minor Rejuvenation Potion")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Swiftness Potion",
        price=DirectPrice(itemid=2459),
        spell_aliases=[("uses_line", "Swiftness Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Invisibility Potion",
        price=DirectPrice(itemid=9172),
        spell_aliases=[("gains_line", "Invisibility"), ("uses_line", "Invisibility Potion")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Lesser Invisibility Potion",
        price=DirectPrice(itemid=3823),
        spell_aliases=[
            ("gains_line", "Lesser Invisibility"),
            ("uses_line", "Lesser Invisibility Potion"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Powerful Anti-Venom",
        price=DirectPrice(itemid=19440),
        spell_aliases=[("casts_line", "Powerful Anti-Venom"), ("uses_line", "Powerful Anti-Venom")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Strong Anti-Venom",
        price=DirectPrice(itemid=6453),
        spell_aliases=[("casts_line", "Strong Anti-Venom"), ("uses_line", "Strong Anti-Venom")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Anti-Venom",
        price=DirectPrice(itemid=6452),
        spell_aliases=[("casts_line", "Anti-Venom"), ("uses_line", "Anti-Venom")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Dark Rune",
        price=DirectPrice(itemid=20520),
        spell_aliases=[("gains_mana_line", "Dark Rune"), ("uses_line", "Dark Rune")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Mageblood Potion",
        price=DirectPrice(itemid=20007),
        spell_aliases=[("uses_line", "Mageblood Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Mana Regeneration (food or mageblood)"),
    ),
    SuperwowConsumable(
        name="Danonzo's Tel'Abim Surprise",
        price=DirectPrice(itemid=60976),
        spell_aliases=[("uses_line", "Danonzos Tel'Abim Surprise")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Danonzo's Tel'Abim Delight",
        price=DirectPrice(itemid=60977),
        spell_aliases=[("uses_line", "Danonzos Tel'Abim Delight")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Danonzo's Tel'Abim Medley",
        price=DirectPrice(itemid=60978),
        spell_aliases=[("uses_line", "Danonzos Tel'Abim Medley")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Wildvine Potion",
        price=DirectPrice(itemid=9144),
        spell_aliases=[("uses_line", "Wildvine Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Scroll of Stamina IV",
        price=DirectPrice(itemid=10307),
        spell_aliases=[("uses_line", "Scroll of Stamina IV")],
        strategy=OverwriteStrategy(target_consumable_name="Stamina"),
    ),
    SuperwowConsumable(
        name="Scroll of Strength IV",
        price=DirectPrice(itemid=10310),
        spell_aliases=[("uses_line", "Scroll of Strength IV")],
        strategy=OverwriteStrategy(target_consumable_name="Strength"),
    ),
    SuperwowConsumable(
        name="Scroll of Spirit IV",
        price=DirectPrice(itemid=10306),
        spell_aliases=[("uses_line", "Scroll of Spirit IV")],
        strategy=OverwriteStrategy(target_consumable_name="Spirit"),
    ),
    SuperwowConsumable(
        name="Scroll of Protection IV",
        price=DirectPrice(itemid=10305),
        spell_aliases=[("uses_line", "Scroll of Protection IV")],
        strategy=OverwriteStrategy(target_consumable_name="Armor"),
    ),
    SuperwowConsumable(
        name="Scroll of Intellect IV",
        price=DirectPrice(itemid=10308),
        spell_aliases=[("uses_line", "Scroll of Intellect IV")],
        strategy=OverwriteStrategy(target_consumable_name="Intellect"),
    ),
    SuperwowConsumable(
        name="Scroll of Agility IV",
        price=DirectPrice(itemid=10309),
        spell_aliases=[("uses_line", "Scroll of Agility IV")],
        strategy=OverwriteStrategy(target_consumable_name="Agility"),
    ),
    SuperwowConsumable(
        name="Purification Potion",
        price=DirectPrice(itemid=13462),
        spell_aliases=[("uses_line", "Purification Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Poisonous Mushroom",
        price=DirectPrice(itemid=5823),
        spell_aliases=[("uses_line", "Poisonous Mushroom")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Nightfin Soup",
        price=DirectPrice(itemid=13931),
        spell_aliases=[("uses_line", "Nightfin Soup")],
        strategy=OverwriteStrategy(target_consumable_name="Mana Regeneration (food or mageblood)"),
    ),
    SuperwowConsumable(
        name="Weak Troll's Blood Potion",
        price=DirectPrice(itemid=3382),
        spell_aliases=[("uses_line", "Weak Trolls Blood Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Regeneration"),
    ),
    SuperwowConsumable(
        name="Major Troll's Blood Potion",
        price=DirectPrice(itemid=20004),
        spell_aliases=[("uses_line", "Major Trolls Blood Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Regeneration"),
    ),
    SuperwowConsumable(
        name="Mighty Troll's Blood Potion",
        price=DirectPrice(itemid=3826),
        spell_aliases=[("uses_line", "Mighty Trolls Blood Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Regeneration"),
    ),
    SuperwowConsumable(
        name="Magic Resistance Potion",
        price=DirectPrice(itemid=9036),
        spell_aliases=[("uses_line", "Magic Resistance Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Jungle Remedy",
        price=DirectPrice(itemid=2633),
        spell_aliases=[("casts_line", "Cure Ailments"), ("uses_line", "Jungle Remedy")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Living Action Potion",
        price=DirectPrice(itemid=20008),
        spell_aliases=[("uses_line", "Living Action Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Empowering Herbal Salad",
        price=DirectPrice(itemid=83309),
        spell_aliases=[("uses_line", "Empowering Herbal Salad")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Poison Resistance",
        price=DirectPrice(itemid=3386),
        spell_aliases=[("uses_line", "Elixir of Poison Resistance")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Demonslaying",
        price=DirectPrice(itemid=9224),
        spell_aliases=[("uses_line", "Elixir of Demonslaying")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Graccu's Homemade Meat Pie",
        price=DirectPrice(itemid=17407),
        spell_aliases=[("uses_line", "Graccus Homemade Meat Pie")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Greater Dreamless Sleep Potion",
        price=DirectPrice(itemid=20002),
        spell_aliases=[("uses_line", "Greater Dreamless Sleep Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Greater Defense",
        price=DirectPrice(itemid=8951),
        spell_aliases=[("uses_line", "Elixir of Greater Defense")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Giant Growth",
        price=DirectPrice(itemid=6662),
        spell_aliases=[("gains_line", "Enlarge"), ("uses_line", "Elixir of Giant Growth")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Frozen Rune",
        price=DirectPrice(itemid=22682),
        spell_aliases=[("uses_line", "Frozen Rune")],
        strategy=OverwriteStrategy(target_consumable_name="Fire Protection"),
    ),
    SuperwowConsumable(
        name="Arcane Elixir",
        price=DirectPrice(itemid=9155),
        spell_aliases=[("gains_line", "Arcane Elixir"), ("uses_line", "Arcane Elixir")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Dense Sharpening Stone",
        price=DirectPrice(itemid=12404),
        spell_aliases=[
            ("begins_to_cast_line", "Sharpen Blade V"),
            ("uses_line", "Dense Sharpening Stone"),
        ],
        strategy=OverwriteStrategy(target_consumable_name="Dense Sharpening Stone"),
    ),
    SuperwowConsumable(
        name="Dense Weightstone",
        price=DirectPrice(itemid=12643),
        spell_aliases=[
            ("begins_to_cast_line", "Enhance Blunt Weapon V"),
            ("uses_line", "Dense Weightstone"),
        ],
        strategy=OverwriteStrategy(target_consumable_name="Dense Weightstone"),
    ),
    Consumable(
        name="Bloodkelp Elixir of Resistance",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Elixir of Resistance")],
    ),
    Consumable(
        name="Fire-toasted Bun",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Fire-toasted Bun")],
    ),
    SuperwowConsumable(
        name="Blessed Sunfruit",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Blessed Sunfruit"), ("uses_line", "Blessed Sunfruit")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Blessed Sunfruit Juice",
        price=NoPrice(),
        spell_aliases=[
            ("gains_line", "Blessed Sunfruit Juice"),
            ("uses_line", "Blessed Sunfruit Juice"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Windblossom Berries",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Windblossom Berries")],
        strategy=OverwriteStrategy(target_consumable_name="Increased Stamina"),
    ),
    SuperwowConsumable(
        name="Rumsey Rum",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Rumsey Rum"), ("uses_line", "Rumsey Rum")],
        strategy=EnhanceStrategy(),
    ),
    Consumable(
        name="Increased Stamina",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Increased Stamina")],
    ),
    Consumable(
        name="Increased Intellect",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Increased Intellect")],
    ),
    Consumable(
        name="Mana Regeneration (food or mageblood)",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Mana Regeneration")],
    ),
    Consumable(
        name="Regeneration",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Regeneration")],
    ),
    Consumable(
        name="Agility",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Agility")],
    ),
    Consumable(
        name="Strength",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Strength")],
    ),
    Consumable(
        name="Stamina",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Stamina")],
    ),
    Consumable(
        name="Spirit",
        price=NoPrice(),
    ),
    Consumable(
        name="Armor",
        price=NoPrice(),
    ),
    Consumable(
        name="Intellect",
        price=NoPrice(),
    ),
    Consumable(
        name="Fire Protection",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Fire Protection")],
    ),
    Consumable(
        name="Frost Protection",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Frost Protection")],
    ),
    Consumable(
        name="Arcane Protection",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Arcane Protection")],
    ),
    Consumable(
        name="Nature Protection",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Nature Protection ")],  # need the trailing space
    ),
    Consumable(
        name="Shadow Protection",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Shadow Protection ")],  # need the trailing space
    ),
    Consumable(
        name="Holy Protection",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Holy Protection ")],  # need the trailing space
    ),
    SuperwowConsumable(
        name="Kreeg's Stout Beatdown",
        price=NoPrice(),
        spell_aliases=[
            ("begins_to_cast_line", "Kreeg's Stout Beatdown"),
            ("uses_line", "Kreegs Stout Beatdown"),
        ],
        strategy=EnhanceStrategy(),
    ),
    Consumable(
        name="Advanced Target Dummy",
        price=DirectPrice(itemid=4392),
        spell_aliases=[("casts_line", "Advanced Target Dummy")],
    ),
    Consumable(
        name="Masterwork Target Dummy",
        price=DirectPrice(itemid=16023),
        spell_aliases=[("casts_line", "Masterwork Target Dummy")],
    ),

    SuperwowConsumable(
        name="Conjured Mana Orange",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Conjured Mana Orange")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Conjured Crystal Water",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Conjured Crystal Water")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Winter Veil Eggnog",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Winter Veil Eggnog")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Winter Veil Candy",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Winter Veil Candy")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Winter Veil Cookie",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Winter Veil Cookie")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Gift of Friendship - Ironforge (stam)",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Ironforge Gift of Friendship")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Gift of Friendship - Stormwind (int)",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Stormwind Gift of Friendship")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Gift of Friendship - Darnassus (agi)",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Darnassus Gift of Friendship")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Gift of Friendship - Orgrimmar (agi)",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Orgrimmar Gift of Friendship")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Gift of Friendship - Thunder Bluff (stam)",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Thunder Bluff Gift of Friendship")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Gift of Friendship - Undercity (int)",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Undercity Gift of Friendship")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Slumber Sand",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Slumber Sand")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Sweet Surprise",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Sweet Surprise")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Midsummer Sausage",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Midsummer Sausage")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Very Berry Cream",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Very Berry Cream")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Dark Desire",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Dark Desire")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Buttermilk Delight",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Buttermilk Delight")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Graccu's Mince Meat Fruitcake",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Graccus Mince Meat Fruitcake")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="MOLL-E, Remote Mail Terminal",
        price=NoPrice(),
        spell_aliases=[("uses_line", "MOLL-E, Remote Mail Terminal")],
        strategy=IgnoreStrategy(),
    ),
    SuperwowConsumable(
        name="Goblin Brainwashing Device",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Goblin Brainwashing Device")],
        strategy=IgnoreStrategy(),
    ),
    SuperwowConsumable(
        name="Stratholme Holy Water",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Stratholme Holy Water")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Firepower",
        price=DirectPrice(itemid=6373),
        spell_aliases=[("gains_line", "Fire Power"), ("uses_line", "Elixir of Firepower")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Greater Firepower",
        price=DirectPrice(itemid=21546),
        spell_aliases=[
            ("gains_line", "Greater Firepower"),
            ("uses_line", "Elixir of Greater Firepower"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Shadow Power",
        price=DirectPrice(itemid=9264),
        spell_aliases=[("gains_line", "Shadow Power"), ("uses_line", "Elixir of Shadow Power")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Potion of Quickness",
        price=DirectPrice(itemid=61181),
        spell_aliases=[("gains_line", "Potion of Quickness"), ("uses_line", "Potion of Quickness")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Le Fishe Au Chocolat",
        price=DirectPrice(itemid=84040),
        spell_aliases=[
            ("gains_line", "Le Fishe Au Chocolat"),
            ("uses_line", "Le Fishe Au Chocolat"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of the Mongoose",
        price=DirectPrice(itemid=13452),
        spell_aliases=[
            ("gains_line", "Elixir of the Mongoose"),
            ("uses_line", "Elixir of the Mongoose"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Greater Nature Power",
        price=DirectPrice(itemid=50237),
        spell_aliases=[
            ("gains_line", "Elixir of Greater Nature Power"),
            ("uses_line", "Elixir of Greater Nature Power"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Power Mushroom",
        price=DirectPrice(itemid=51720),
        spell_aliases=[("uses_line", "Power Mushroom")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Gordok Green Grog",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Gordok Green Grog"), ("uses_line", "Gordok Green Grog")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Mighty Rage Potion",
        price=DirectPrice(itemid=13442),
        spell_aliases=[("gains_rage_line", "Mighty Rage"), ("uses_line", "Mighty Rage Potion")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Noggenfogger Elixir",
        price=NoPrice(),
        spell_aliases=[("gains_line", "Noggenfogger Elixir"), ("uses_line", "Noggenfogger Elixir")],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Demonic Rune",
        price=NoPrice(),
        spell_aliases=[("gains_mana_line", "Demonic Rune"), ("uses_line", "Demonic Rune")],
        strategy=EnhanceStrategy(),
    ),
]


NAME2CONSUMABLE: Dict[str, Consumable] = {item.name: item for item in all_defined_consumable_items}

RAWSPELLNAME2CONSUMABLE: Dict[Tuple[str, str], Consumable] = {}
for item in all_defined_consumable_items:
    for line_type, raw_spellname in item.spell_aliases:
        key = (line_type, raw_spellname)
        if key in RAWSPELLNAME2CONSUMABLE:
            raise ValueError(
                f"duplicate consumable alias. tried to add {key} for {item.name}"
                f" but {RAWSPELLNAME2CONSUMABLE[key].name} already added"
            )
        RAWSPELLNAME2CONSUMABLE[key] = item


RENAME_SPELL = {
    ("hits_ability_line", "Holy Shock"): "Holy Shock (dmg)",
    ("heals_line", "Holy Shock"): "Holy Shock (heal)",
    ("heals_line", "Tea"): "Tea with Sugar",
    ("gains_rage_line", "Blood Fury"): "Gri'lek's Charm of Might",
}


def rename_spell(spell, line_type):
    rename = RENAME_SPELL.get((line_type, spell))
    return rename or spell


# careful. not everything needs an itemid
NAME2ITEMID = {
    consumable.name: consumable.price.itemid
    for consumable in all_defined_consumable_items
    if isinstance(consumable.price, DirectPrice)
}


# used for pricing
ITEMID2NAME = {value: key for key, value in NAME2ITEMID.items()}


USES_CONSUMABLE_RENAME = {
    "Tea With Sugar": "Tea with Sugar",
}


INTERRUPT_SPELLS = {
    "Kick",
    "Pummel",
    "Shield Bash",
    "Earth Shock",
}


CDSPELL_CLASS = [
    [
        PlayerClass.WARRIOR,
        [
            "Death Wish",
            "Sweeping Strikes",
            "Shield Wall",
            "Recklessness",
            "Bloodrage",
        ],
    ],
    [PlayerClass.MAGE, ["Combustion", "Scorch"]],
    [
        PlayerClass.SHAMAN,
        [
            "Nature's Swiftness",
            "Windfury Totem",
            "Mana Tide Totem",
            "Grace of Air Totem",
            "Tranquil Air Totem",
            "Strength of Earth Totem",
            "Mana Spring Totem",
            "Searing Totem",
            "Fire Nova Totem",
            "Magma Totem",
            "Ancestral Spirit",
        ],
    ],
    [PlayerClass.DRUID, ["Nature's Swiftness", "Rebirth", "Swiftmend"]],
    [
        PlayerClass.PRIEST,
        [
            "Inner Focus",
            "Resurrection",
        ],
    ],
    [
        PlayerClass.PALADIN,
        ["Divine Favor", "Holy Shock (heal)", "Holy Shock (dmg)", "Redemption"],
    ],
    [
        PlayerClass.ROGUE,
        [
            "Adrenaline Rush",
            "Blade Flurry",
        ],
    ],
    [PlayerClass.WARLOCK, []],
    [PlayerClass.HUNTER, ["Rapid Fire"]],
]


RECEIVE_BUFF_SPELL = {
    "Power Infusion",
    "Bloodlust",
    "Chastise Haste",
}
RACIAL_SPELL = [
    "Blood Fury",
    "Berserking",
    "Stoneform",
    "Desperate Prayer",
    "Will of the Forsaken",
    "War Stomp",
]
TRINKET_SPELL = [
    "Kiss of the Spider",
    "Slayer's Crest",
    "Jom Gabbar",
    "Badge of the Swarmguard",
    "Earthstrike",
    "Diamond Flask",
    "Gri'lek's Charm of Might",
    "The Eye of the Dead",
    "Healing of the Ages",
    "Essence of Sapphiron",
    "Ephemeral Power",
    "Unstable Power",
    "Mind Quickening",
    "Nature Aligned",
    "Death by Peasant",
    "Immune Charm/Fear/Stun",
    "Immune Charm/Fear/Polymorph",
    "Immune Fear/Polymorph/Snare",
    "Immune Fear/Polymorph/Stun",
    "Immune Root/Snare/Stun",
]
RENAME_TRINKET_SPELL = {
    "Unstable Power": "Zandalarian Hero Charm",
    "Ephemeral Power": "Talisman of Ephemeral Power",
    "Essence of Sapphiron": "The Restrained Essence of Sapphiron",
    "Mind Quickening": "Mind Quickening Gem",
    "Nature Aligned": "Natural Alignment Crystal",
    "Death by Peasant": "Barov Peasant Caller",
    "Healing of the Ages": "Hibernation Crystal",
    "Rapid Healing": "Hazza'rah's Charm of Healing",
    "Chromatic Infusion": "Draconic Infused Emblem",
    "Immune Charm/Fear/Stun": "Insignia of the Alliance/Horde",
    "Immune Charm/Fear/Polymorph": "Insignia of the Alliance/Horde",
    "Immune Fear/Polymorph/Snare": "Insignia of the Alliance/Horde",
    "Immune Fear/Polymorph/Stun": "Insignia of the Alliance/Horde",
    "Immune Root/Snare/Stun": "Insignia of the Alliance/Horde",
}
for spell in itertools.chain(TRINKET_SPELL, RACIAL_SPELL, sorted(RECEIVE_BUFF_SPELL)):
    for clsorder in CDSPELL_CLASS:
        spells = clsorder[1]
        spells.append(spell)


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

KNOWN_BOSS_NAMES = {
    # naxx
    "Anub'Rekhan",
    "Grand Widow Faerlina",
    "Maexxna",
    "Noth the Plaguebringer",
    "Heigan the Unclean",
    "Loatheb",
    "Patchwerk",
    "Grobbulus",
    "Gluth",
    "Thaddius",
    "Feugen",
    "Stalagg",
    "Instructor Razuvious",
    "Gothik the Harvester",
    "Highlord Mograine",
    "Lady Blaumeux",
    "Sir Zeliek",
    "Thane Korth'azz",
    "Sapphiron",
    "Kel'Thuzad",
}


def healpot_lookup(amount):
    # bigger ranges for rounding errors
    if 1049 <= amount <= 1751:
        return "Healing Potion - Major"
    if 699 <= amount <= 901:
        return "Healing Potion - Superior"
    if 454 <= amount <= 586:
        return "Healing Potion - Greater"
    if 139 <= amount <= 181:
        return "Healing Potion - Lesser"
    if 69 <= amount <= 91:
        return "Healing Potion - Minor"
    return "Healing Potion - unknown"


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


class ProcSummary:
    def __init__(self, proc_count, player):
        # spell - player - count
        self.counts = proc_count.counts
        self.counts_extra_attacks = proc_count.counts_extra_attacks
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
                print("  ", "  ", name, total, file=output)

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
LINE2SPELLCAST = {
    "afflicted_line": {
        "Death Wish",
    },
    "gains_line": {
        "Immune Charm/Fear/Stun",
        "Immune Charm/Fear/Polymorph",
        "Immune Fear/Polymorph/Snare",
        "Immune Fear/Polymorph/Stun",
        "Immune Root/Snare/Stun",
        "Will of the Forsaken",
        "Bloodrage",
        "Recklessness",
        "Shield Wall",
        "Sweeping Strikes",
        "Elemental Mastery",
        "Inner Focus",
        "Rapid Healing",
        "Chromatic Infusion",
        "Combustion",
        "Adrenaline Rush",  # careful with hunters
        "Cold Blood",
        "Blade Flurry",
        "Nature's Swiftness",  # sham and druid
        "Rapid Fire",
        "The Eye of the Dead",
        "Healing of the Ages",
        "Earthstrike",
        "Diamond Flask",
        "Kiss of the Spider",
        "Slayer's Crest",
        "Jom Gabbar",
        "Badge of the Swarmguard",
        "Essence of Sapphiron",
        "Ephemeral Power",
        "Unstable Power",
        "Mind Quickening",
        "Nature Aligned",
        "Divine Favor",
        "Berserking",
        "Stoneform",
        # buffs received
        "Power Infusion",
        "Bloodlust",
        "Chastise Haste",
    },
    "gains_rage_line": {
        "Gri'lek's Charm of Might",
    },
    "heals_line": {
        "Holy Shock (heal)",
        "Desperate Prayer",
        "Swiftmend",
    },
    "casts_line": {
        "Windfury Totem",
        "Mana Tide Totem",
        "Grace of Air Totem",
        "Tranquil Air Totem",
        "Strength of Earth Totem",
        "Mana Spring Totem",
        "Searing Totem",
        "Fire Nova Totem",
        "Magma Totem",
        "Ancestral Spirit",
        "Redemption",
        "Resurrection",
        "Rebirth",
        "Sunder Armor",  # superwow
        "Sunder Armor (boss)",  # rename, superwow
        "Blood Fury",  # superwow, spellid 23234
    },
    "hits_ability_line": {
        "Sinister Strike",
        "Scorch",
        "Holy Shock (dmg)",
    },
    "begins_to_perform_line": {
        "War Stomp",
    },
}


class SpellCount:
    def __init__(self):
        # spell - name - count
        self.counts = collections.defaultdict(lambda: collections.defaultdict(int))

    def add(self, line_type, name, spell):
        if line_type not in LINE2SPELLCAST:
            return
        if spell not in LINE2SPELLCAST[line_type]:
            return
        self.counts[spell][name] += 1

    def add_stackcount(self, line_type, name, spell, stackcount):
        if (
            spell in {"Combustion", "Unstable Power", "Jom Gabbar"}
            and line_type == "gains_line"
            and stackcount != 1
        ):
            return
        self.add(line_type=line_type, name=name, spell=spell)


LINE2PROC = {
    "gains_line": {
        "Enrage",
        "Flurry",
        "Elemental Devastation",
        "Stormcaller's Wrath",
        "Spell Blasting",
        "Clearcasting",
        "Vengeance",
        "Nature's Grace",
    },
}


class ProcCount:
    def __init__(
        self,
    ):
        # effect - name - count
        self.counts = collections.defaultdict(lambda: collections.defaultdict(int))

        # source - name - count
        self.counts_extra_attacks = collections.defaultdict(lambda: collections.defaultdict(int))

    def add(self, line_type, name, spell):
        if line_type not in LINE2PROC:
            return
        if spell not in LINE2PROC[line_type]:
            return
        self.counts[spell][name] += 1

    def add_extra_attacks(self, howmany, source, name):
        self.counts_extra_attacks[source][name] += howmany


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
        consumable = NAME2CONSUMABLE.get(consumable_name)

        price = Currency(0)
        if not consumable:
            # logging.warning(f"Consumable '{consumable_name}' not defined.")
            return price

        if isinstance(consumable.price, NoPrice):
            return price

        # Determine the list of items whose direct itemid-based price we need to sum up.
        # For a crafted item, these are its components.
        # For a base item, it's the item itself.
        components_to_price: List[Tuple[Consumable, float]]

        item_charges = consumable.price.charges

        if isinstance(consumable.price, PriceFromComponents):
            components_to_price = consumable.price.components
        elif isinstance(
            consumable.price, DirectPrice
        ):  # It's a base item (or has no defined components)
            components_to_price = [(consumable, 1.0)]
        else:  # Should not happen if NoPrice is handled
            raise RuntimeError("this should be unreachable")

        for base_item, quantity in components_to_price:
            if not isinstance(base_item.price, DirectPrice) or not base_item.price.itemid:
                # This item/component doesn't have an itemID to look up.
                # logging.debug(f"Item '{base_item.name}' has no itemid for pricing.")
                continue

            unit_price = self.pricedb.lookup(base_item.price.itemid)
            if unit_price is None:
                # logging.debug(f"Price not found for item '{base_item.name}' (ID: {base_item.price.itemid}).")
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


# line type -> spell -> PlayerClass
# shouldn't need to be an exhaustive list, only the most common
# unique spells, no ambiguity
UNIQUE_LINE2SPELL2CLASS: Dict[str, Dict[str, PlayerClass]] = {
    "afflicted_line": {
        "Death Wish": PlayerClass.WARRIOR,
    },
    "gains_line": {
        "Recklessness": PlayerClass.WARRIOR,
        "Shield Wall": PlayerClass.WARRIOR,
        "Bloodrage": PlayerClass.WARRIOR,
        "Sweeping Strikes": PlayerClass.WARRIOR,
        "Combustion": PlayerClass.MAGE,
        "Adrenaline Rush": PlayerClass.ROGUE,
        "Blade Flurry": PlayerClass.ROGUE,
        "Cold Blood": PlayerClass.ROGUE,
        "Slice and Dice": PlayerClass.ROGUE,
        "Divine Favor": PlayerClass.PALADIN,
        "Seal of Command": PlayerClass.PALADIN,
        "Seal of Righteousness": PlayerClass.PALADIN,
    },
    "heals_line": {
        "Flash of Light": PlayerClass.PALADIN,
        "Holy Light": PlayerClass.PALADIN,
        "Holy Shock (heal)": PlayerClass.PALADIN,
        "Heal": PlayerClass.PRIEST,
        "Flash Heal": PlayerClass.PRIEST,
        "Greater Heal": PlayerClass.PRIEST,
        "Prayer of Healing": PlayerClass.PRIEST,
    },
    "hits_ability_line": {
        "Cleave": PlayerClass.WARRIOR,
        "Whirlwind": PlayerClass.WARRIOR,
        "Bloodthirst": PlayerClass.WARRIOR,
        "Heroic Strike": PlayerClass.WARRIOR,
        "Sinister Strike": PlayerClass.ROGUE,
        "Arcane Explosion": PlayerClass.MAGE,
        "Fire Blast": PlayerClass.MAGE,
        "Starfire": PlayerClass.DRUID,
        "Moonfire": PlayerClass.DRUID,
        "Wrath": PlayerClass.DRUID,
        "Shadow Bolt": PlayerClass.WARLOCK,
        "Mind Blast": PlayerClass.PRIEST,
        "Arcane Shot": PlayerClass.HUNTER,
        "Multi-Shot": PlayerClass.HUNTER,
        "Holy Shock (dmg)": PlayerClass.PALADIN,
    },
    "gains_health_line": {
        "Rejuvenation": PlayerClass.DRUID,
        "Regrowth": PlayerClass.DRUID,
    },
    "begins_to_cast_line": {
        "Shadow Bolt": PlayerClass.WARLOCK,
        "Rejuvenation": PlayerClass.DRUID,
        "Regrowth": PlayerClass.DRUID,
        "Wrath": PlayerClass.DRUID,
        # frostbolt not unique enough probably, eg frost oils
        "Fireball": PlayerClass.MAGE,
        "Scorch": PlayerClass.MAGE,
        "Polymorph": PlayerClass.MAGE,
        "Chain Heal": PlayerClass.SHAMAN,
        "Lesser Healing Wave": PlayerClass.SHAMAN,
        "Mind Blast": PlayerClass.PRIEST,
        "Smite": PlayerClass.PRIEST,
        "Heal": PlayerClass.PRIEST,
        "Flash Heal": PlayerClass.PRIEST,
        "Greater Heal": PlayerClass.PRIEST,
        "Prayer of Healing": PlayerClass.PRIEST,
        "Multi-Shot": PlayerClass.HUNTER,
        "Flash of Light": PlayerClass.PALADIN,
        "Holy Light": PlayerClass.PALADIN,
    },
    "begins_to_perform_line": {
        "Auto Shot": PlayerClass.HUNTER,
        "Trueshot": PlayerClass.HUNTER,
    },
    "casts_line": {
        "Windfury Totem": PlayerClass.SHAMAN,
        "Mana Tide Totem": PlayerClass.SHAMAN,
        "Grace of Air Totem": PlayerClass.SHAMAN,
        "Tranquil Air Totem": PlayerClass.SHAMAN,
        "Strength of Earth Totem": PlayerClass.SHAMAN,
        "Mana Spring Totem": PlayerClass.SHAMAN,
        "Searing Totem": PlayerClass.SHAMAN,
        "Fire Nova Totem": PlayerClass.SHAMAN,
        "Magma Totem": PlayerClass.SHAMAN,
        "Ancestral Spirit": PlayerClass.SHAMAN,
        "Redemption": PlayerClass.PALADIN,
        "Resurrection": PlayerClass.PRIEST,
        "Rebirth": PlayerClass.DRUID,
    },
}


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
        if line_type not in UNIQUE_LINE2SPELL2CLASS:
            return
        spell2class = UNIQUE_LINE2SPELL2CLASS[line_type]
        if spell not in spell2class:
            return

        detected_class: PlayerClass = spell2class[spell]

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
        return parse_line2(app, line)
    except Exception:
        logging.exception(line)
        raise


def parse_line2(app, line):
    """
    returns True when a match is found, so we can stop trying different parsers
    """
    try:
        tree = app.parser.parse(line)
        timestamp = tree.children[0]
        subtree = tree.children[1]

        timestamp_unix = parse_ts2unixtime(timestamp)

        # inline some parsing to reduce funcalls
        # for same reason not using visitors to traverse the parse tree
        if subtree.data == "gains_line":
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

            if spellname == "Armor Shatter":
                app.annihilator.add(line)
            if spellname == "Flame Buffet":
                app.flamebuffet.add(line)

            if name == "Princess Huhuran" and spellname in {"Frenzy", "Berserk"}:
                app.huhuran.add(line)
            if name == "Gluth" and spellname == "Frenzy":
                app.gluth.add(line)

            return True
        elif subtree.data == "gains_rage_line":
            name = subtree.children[0].value
            spellname = subtree.children[3].value

            spellname = rename_spell(spellname, line_type=subtree.data)
            app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)

            if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
                app.player[name][consumable_item.name] += 1
            return True
        elif subtree.data == "gains_energy_line":
            return True
        elif subtree.data == "gains_health_line":
            targetname = subtree.children[0].value
            amount = int(subtree.children[1].value)
            name = subtree.children[2].value
            spellname = subtree.children[3].value

            app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)

            app.healstore.add(name, targetname, spellname, amount, timestamp_unix)
            return True
        elif subtree.data == "uses_line":
            name = subtree.children[0].value
            spellname = subtree.children[1].value

            spellname = USES_CONSUMABLE_RENAME.get(spellname, spellname)
            consumable_item = RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname))
            if consumable_item and isinstance(consumable_item, SuperwowConsumable):
                if isinstance(consumable_item.strategy, IgnoreStrategy):
                    return True  # Parsed and explicitly ignored

                # For all other strategies (Safe, Enhance, Overwrite, or any future ones)
                # on a SuperwowConsumable, add it to player_superwow for merging.
                app.player_superwow[name][consumable_item.name] += 1
                return True  # Parsed and staged for merge

            # If RAWSPELLNAME2CONSUMABLE.get found nothing or not a superwow consumable
            app.player_superwow_unknown[name][spellname] += 1
            # To mark this "unknown use" as handled by the uses_line rule:
            return True  # Consider this line "handled" by noting it as unknown within uses_line context.
            # This prevents it from definitely becoming a "skipped line" if no other rule matches.

        elif subtree.data == "dies_line":
            name = subtree.children[0].value
            app.death_count[name] += 1

            if name == "Princess Huhuran":
                app.huhuran.add(line)
            if name == "Gluth":
                app.gluth.add(line)

            return True
        elif subtree.data == "heals_line":
            is_crit = subtree.children[2].type == "HEAL_CRIT"

            name = subtree.children[0].value
            spellname = subtree.children[1].value

            if is_crit:
                targetname = subtree.children[3].value
                amount = int(subtree.children[4].value)
            else:
                targetname = subtree.children[2].value
                amount = int(subtree.children[3].value)

            spellname = rename_spell(spellname, line_type=subtree.data)

            app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
            app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)

            if spellname == "Tea with Sugar":
                app.player[name]["Tea with Sugar"] += 1
            elif spellname == "Healing Potion":
                if is_crit:
                    consumable = healpot_lookup(amount / 1.5)
                else:
                    consumable = healpot_lookup(amount)
                app.player[name][consumable] += 1
            elif spellname == "Rejuvenation Potion":
                if amount > 500:
                    app.player[name]["Rejuvenation Potion - Major"] += 1
                else:
                    app.player[name]["Rejuvenation Potion - Minor"] += 1

            app.healstore.add(name, targetname, spellname, amount, timestamp_unix)
            return True

        elif subtree.data == "gains_mana_line":
            name = subtree.children[0].value
            spellname = subtree.children[-1].value
            if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
                app.player[name][consumable_item.name] += 1

            return True
        elif subtree.data == "drains_mana_line":
            return True
        elif subtree.data == "drains_mana_line2":
            return True
        elif subtree.data == "begins_to_cast_line":
            name = subtree.children[0].value
            spellname = subtree.children[-1].value

            app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)

            if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
                app.player[name][consumable_item.name] += 1

            if name == "Kel'Thuzad" and spellname == "Frostbolt":
                app.kt_frostbolt.begins_to_cast(line)

            return True
        elif subtree.data == "casts_line":
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
                if targetname in KNOWN_BOSS_NAMES:
                    spellname += " (boss)"

            app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
            app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)

            if spellname == "Wild Polymorph":
                app.nef_wild_polymorph.add(line)

            if spellname == "Death by Peasant":
                app.huhuran.add(line)

            if len(subtree.children) == 3:
                targetname = subtree.children[2].value

                if spellname == "Tranquilizing Shot" and targetname == "Princess Huhuran":
                    app.huhuran.add(line)
                if spellname == "Tranquilizing Shot" and targetname == "Gluth":
                    app.gluth.add(line)

            if name == "Kel'Thuzad" and spellname == "Shadow Fissure":
                app.kt_shadowfissure.add(line)

            return True
        elif subtree.data == "combatant_info_line":
            return True
        elif subtree.data == "consolidated_line":
            for entry in subtree.children:
                if entry.data == "consolidated_pet":
                    name = entry.children[0].value
                    petname = entry.children[1].value
                    app.pet_handler.add(name, petname)
                    app.player_detect[name].add("pet: " + petname)
                else:
                    # parse but ignore the other consolidated entries
                    pass
            return True
        elif subtree.data == "hits_ability_line":
            name = subtree.children[0].value
            spellname = subtree.children[1].value
            targetname = subtree.children[2].value
            amount = int(subtree.children[3].value)

            spellname = rename_spell(spellname, line_type=subtree.data)

            app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
            app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)

            if spellname in app.hits_consumable.COOLDOWNS:
                app.hits_consumable.update(name, spellname, timestamp_unix)

            if targetname == "Viscidus":
                app.viscidus.found()
                spell_damage_type = subtree.children[4]
                if spell_damage_type and spell_damage_type.children[0].value == "Frost":
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

            app.dmgstore.add(name, targetname, spellname, amount, timestamp_unix)
            app.dmgtakenstore.add(name, targetname, spellname, amount, timestamp_unix)

            return True
        elif subtree.data == "hits_autoattack_line":
            name = subtree.children[0].value
            target = subtree.children[1].value
            amount = int(subtree.children[2].value)

            if name == "Guardian of Icecrown":
                app.kt_guardian.add(line)
            app.dmgstore.add(name, target, "hit", amount, timestamp_unix)
            app.dmgtakenstore.add(name, target, "hit", amount, timestamp_unix)
            return True
        elif subtree.data == "parry_ability_line":
            name = subtree.children[0].value
            spellname = subtree.children[1].value
            targetname = subtree.children[2].value

            if spellname in INTERRUPT_SPELLS and targetname == "Kel'Thuzad":
                app.kt_frostbolt.parry(line)

            return True
        elif subtree.data == "parry_line":
            return True
        elif subtree.data == "block_line":
            return True
        elif subtree.data == "block_ability_line":
            return True
        elif subtree.data == "interrupts_line":
            return True

        elif subtree.data == "resist_line":
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
        elif subtree.data == "immune_ability_line":
            name = subtree.children[0].value
            spellname = subtree.children[1].value

            if spellname in app.hits_consumable.COOLDOWNS:
                app.hits_consumable.update(name, spellname, timestamp_unix)

            return True
        elif subtree.data == "is_immune_ability_line":
            targetname = subtree.children[0].value
            name = subtree.children[1].value
            spellname = subtree.children[2].value
            if spellname in app.hits_consumable.COOLDOWNS:
                app.hits_consumable.update(name, spellname, timestamp_unix)
            return True

        elif subtree.data == "immune_line":
            return True
        elif subtree.data == "afflicted_line":
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

            return True
        elif subtree.data == "is_destroyed_line":
            return True
        elif subtree.data == "is_absorbed_ability_line":
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
        elif subtree.data == "absorbs_ability_line":
            targetname = subtree.children[0].value
            name = subtree.children[1].value
            spellname = subtree.children[2].value
            if spellname == "Corrupted Healing":
                app.nef_corrupted_healing.add(line)
            return True
        elif subtree.data == "absorbs_all_line":
            return True
        elif subtree.data == "fails_to_dispel_line":
            return True
        elif subtree.data == "pet_begins_eating_line":
            return True
        elif subtree.data == "is_dismissed_line":
            name = subtree.children[0].value
            petname = subtree.children[1].value
            app.pet_handler.add(name, petname)
            return True
        elif subtree.data == "is_dismissed_line2":
            name, petname = subtree.children[0].value.split(" ", 1)
            if name[-2:] == "'s":
                name = name[:-2]
            app.pet_handler.add(name, petname)
            return True
        elif subtree.data == "gains_happiness_line":
            petname = subtree.children[0].value
            amount = subtree.children[1].value
            name = subtree.children[2].value
            app.pet_handler.add(name, petname)
            return True
        elif subtree.data == "removed_line":
            name = subtree.children[0].value
            spellname = subtree.children[1].value

            if name == "Princess Huhuran" and spellname == "Frenzy":
                app.huhuran.add(line)

            if name == "Gluth" and spellname == "Frenzy":
                app.gluth.add(line)

            return True
        elif subtree.data == "suffers_line":
            targetname = subtree.children[0].value
            amount = int(subtree.children[1])
            if subtree.children[2].data == "suffers_line_source":
                name = subtree.children[2].children[1].value
                spellname = subtree.children[2].children[2].value

                if spellname == "Corrupted Healing":
                    app.nef_corrupted_healing.add(line)

                app.dmgstore.add(name, targetname, spellname, amount, timestamp_unix)
                app.dmgtakenstore.add(name, targetname, spellname, amount, timestamp_unix)
            else:
                # nosource
                pass

            return True
        elif subtree.data == "fades_line":
            spellname = subtree.children[0].value
            targetname = subtree.children[1].value

            if spellname == "Armor Shatter":
                app.annihilator.add(line)
            if targetname == "Guardian of Icecrown":
                app.kt_guardian.add(line)

            return True
        elif subtree.data == "slain_line":
            return True
        elif subtree.data == "creates_line":
            return True
        elif subtree.data == "is_killed_line":
            return True
        elif subtree.data == "performs_on_line":
            name = subtree.children[0].value
            spellname = subtree.children[1].value
            targetname = subtree.children[2].value

            if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
                app.player[name][consumable_item.name] += 1

            return True
        elif subtree.data == "performs_line":
            return True
        elif subtree.data == "begins_to_perform_line":
            name = subtree.children[0].value
            spellname = subtree.children[-1].value
            app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
            app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)
            return True
        elif subtree.data == "gains_extra_attacks_line":
            name = subtree.children[0].value
            howmany = int(subtree.children[1].value)
            source = subtree.children[2].value
            app.proc_count.add_extra_attacks(howmany=howmany, name=name, source=source)
            return True
        elif subtree.data == "dodges_line":
            return True
        elif subtree.data == "dodge_ability_line":
            return True
        elif subtree.data == "reflects_damage_line":
            name = subtree.children[0].value
            amount = int(subtree.children[1].value)
            target = subtree.children[3].value
            app.dmgstore.add(name, target, "reflect", amount, timestamp_unix)
            app.dmgtakenstore.add(name, target, "reflect", amount, timestamp_unix)
            return True
        elif subtree.data == "causes_damage_line":
            name = subtree.children[0].value
            spellname = subtree.children[1].value
            target = subtree.children[2].value
            amount = int(subtree.children[3].value)
            app.dmgstore.add(name, target, spellname, amount, timestamp_unix)
            app.dmgtakenstore.add(name, target, spellname, amount, timestamp_unix)
            return True
        elif subtree.data == "is_reflected_back_line":
            return True
        elif subtree.data == "misses_line":
            return True
        elif subtree.data == "misses_ability_line":
            return True
        elif subtree.data == "falls_line":
            return True
        elif subtree.data == "none_line":
            return True
        elif subtree.data == "lava_line":
            return True
        elif subtree.data == "slays_line":
            return True
        elif subtree.data == "was_evaded_line":
            name = subtree.children[0].value
            spellname = subtree.children[1].value
            targetname = subtree.children[2].value

            if spellname == "Wild Polymorph":
                app.nef_wild_polymorph.add(line)
            return True
        elif subtree.data == "equipped_durability_loss":
            return True

    except LarkError:
        # parse errors ignored to try different strategies
        # print(line)
        # print(app.parser.parse(line))
        # raise

        pass

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
        "--prices-server",
        choices=["nord", "telabim"],
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
    parser.add_argument("--expert-write-lalr-states", action="store_true")
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

        for player in self.player_superwow:
            consumables_swow = set(self.player_superwow[player])
            consumables = set(self.player[player])
            for c_swow in consumables_swow:
                consumable = NAME2CONSUMABLE.get(c_swow)

                match consumable:
                    case None:
                        self.log(f"impossible! consumable not found {c_swow}")
                        continue

                    case SuperwowConsumable(strategy=SafeStrategy()):
                        if self.player[player].get(c_swow, 0):
                            self.log(f"impossible! consumable not safe {consumable}")
                        self.player[player][c_swow] = self.player_superwow[player][c_swow]
                        del self.player_superwow[player][c_swow]

                    case SuperwowConsumable(strategy=EnhanceStrategy()):
                        self.player[player][c_swow] = max(
                            self.player_superwow[player][c_swow], self.player[player][c_swow]
                        )
                        del self.player_superwow[player][c_swow]

                    case SuperwowConsumable(strategy=OverwriteStrategy(target_consumable_name=c)):
                        # will try to delete the native counts with the old name and use the new name coming from superwow
                        # eg. the prot pots have non-specific native names, but with superwow the specific name shows up
                        c = consumable.strategy.target_consumable_name
                        # if c not in consumables:
                        #    self.log(f"mismatch from {c_swow} to {c}. {player} {c} is not in consumables")
                        if (
                            c != c_swow
                            and self.player[player].get(c, 0) > self.player_superwow[player][c_swow]
                        ):
                            self.log(f"partial merge (overwrite). {player} {c} > {c_swow}")

                            remain = self.player[player][c] - self.player_superwow[player][c_swow]
                            self.player[player][c] = remain
                            self.player[player][c_swow] = self.player_superwow[player][c_swow]
                            del self.player_superwow[player][c_swow]

                            continue

                        self.player[player].pop(c, None)  # might not exist
                        self.player[player][c_swow] = self.player_superwow[player][c_swow]
                        del self.player_superwow[player][c_swow]

                    case _:
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
        expert_write_lalr_states=args.expert_write_lalr_states,
        expert_log_superwow_merge=args.expert_log_superwow_merge,
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
