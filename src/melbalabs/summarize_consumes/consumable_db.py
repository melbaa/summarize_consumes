from typing import List

from melbalabs.summarize_consumes.consumable_model import Consumable
from melbalabs.summarize_consumes.consumable_model import SuperwowConsumable
from melbalabs.summarize_consumes.consumable_model import DirectPrice
from melbalabs.summarize_consumes.consumable_model import PriceFromComponents
from melbalabs.summarize_consumes.consumable_model import NoPrice
from melbalabs.summarize_consumes.consumable_model import SafeStrategy
from melbalabs.summarize_consumes.consumable_model import EnhanceStrategy
from melbalabs.summarize_consumes.consumable_model import OverwriteStrategy
from melbalabs.summarize_consumes.consumable_model import IgnoreStrategy


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
        spell_aliases=[("gains_line", "Crystal Force"), ("uses_line", "Crystal Force")],
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
        spell_aliases=[("gains_line", "Crystal Spire"), ("uses_line", "Crystal Spire")],
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
        name="Gizzard Gum (Spiritual Domination)",
        price=PriceFromComponents(
            components=[
                (_vulture_gizzard, 10),
                (_snickerfang_jowl, 2),
            ]
        ),
        spell_aliases=[("gains_line", "Spiritual Domination"), ("uses_line", "Gizzard Gum")],
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
    Consumable(
        name="Restore Mana (mana potion)",
        price=NoPrice(),
        # special handling, no need to match
    ),
    SuperwowConsumable(
        name="Mana Potion - Minor",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Minor Mana Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Restore Mana (mana potion)"),
    ),
    SuperwowConsumable(
        name="Mana Potion - Lesser",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Full Moonshine")],  # small inaccuracy in logger
        strategy=OverwriteStrategy(target_consumable_name="Restore Mana (mana potion)"),
    ),
    SuperwowConsumable(
        name="Mana Potion",
        price=DirectPrice(itemid=3827),
        spell_aliases=[("uses_line", "Mana Potion")],
        strategy=OverwriteStrategy(target_consumable_name="Restore Mana (mana potion)"),
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
        spell_aliases=[
            ("uses_line", "Superior Mana Potion"),
            ("uses_line", "Combat Mana Potion"),
        ],
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
        name="Strong Troll's Blood Potion",
        price=DirectPrice(itemid=3388),
        spell_aliases=[("uses_line", "Strong Trolls Blood Potion")],
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
    SuperwowConsumable(
        name="Bloodkelp Elixir of Resistance",
        price=NoPrice(),
        spell_aliases=[
            ("gains_line", "Elixir of Resistance"),
            ("uses_line", "Bloodkelp Elixir of Resistance"),
        ],
        strategy=EnhanceStrategy(),
    ),
    SuperwowConsumable(
        name="Bloodkelp Elixir of Dodging",
        price=NoPrice(),
        spell_aliases=[
            ("gains_line", "Elixir of Dodging"),
            ("uses_line", "Bloodkelp Elixir of Dodging"),
        ],
        strategy=EnhanceStrategy(),
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
        strategy=EnhanceStrategy(),
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
    SuperwowConsumable(
        name="Baked Salmon",
        price=DirectPrice(itemid=13935),
        spell_aliases=[("uses_line", "Baked Salmon")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Blended Bean Brew",
        price=NoPrice(),  # has price, but low lvl
        spell_aliases=[("uses_line", "Blended Bean Brew")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Boiled Clams",
        price=NoPrice(),  # has price, but low lvl
        spell_aliases=[("uses_line", "Boiled Clams")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Bottled Alterac Spring Water",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Bottled Alterac Spring Water")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Bottled Winterspring Water",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Bottled Winterspring Water")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Bubbly Beverage",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Bubbly Beverage")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Catseye Elixir",
        price=NoPrice(),  # has price, but low lvl
        spell_aliases=[("uses_line", "Catseye Elixir")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Cleaning Cloth",
        price=NoPrice(),  # has price, but low lvl
        spell_aliases=[("uses_line", "Cleaning Cloth")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Combat Healing Potion",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Combat Healing Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Cowardly Flight Potion",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Cowardly Flight Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Crunchy Frog",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Crunchy Frog")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Crusty Flatbread",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Crusty Flatbread")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Crystal Infused Bandage",
        price=NoPrice(),  # TODO
        spell_aliases=[("uses_line", "Crystal Infused Bandage")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Deepsea Lobster",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Deepsea Lobster")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Delicious Pizza",
        price=NoPrice(),  # TODO
        spell_aliases=[("uses_line", "Delicious Pizza")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Dig Rat Stew",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Dig Rat Stew")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Discolored Healing Potion",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Discolored Healing Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Dreamless Sleep Potion",
        price=DirectPrice(itemid=12190),
        spell_aliases=[("uses_line", "Dreamless Sleep Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Egg Nog",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Egg Nog")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elderberry Pie",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Elderberry Pie")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Agility",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Agility")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Defense",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Defense")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Detect Demon",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Detect Demon")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Detect Lesser Invisibility",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Detect Lesser Invisibility")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Detect Undead",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Detect Undead")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Greater Water Breathing",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Greater Water Breathing")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Lesser Agility",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Lesser Agility")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Lions Strength",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Lions Strength")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Minor Agility",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Minor Agility")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Minor Fortitude",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Minor Fortitude")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Ogres Strength",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Ogres Strength")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Water Breathing",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Water Breathing")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Water Walking",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Elixir of Water Walking")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Elixir of Wisdom",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Elixir of Wisdom")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Festival Dumplings",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Festival Dumplings")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Fiery Festival Brew",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Fiery Festival Brew")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Fishliver Oil",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Fishliver Oil")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Fizzy Faire Drink",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Fizzy Faire Drink")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Freshly-Squeezed Lemonade",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Freshly-Squeezed Lemonade")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Gargantuan Tel'Abim Banana",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Gargantuan Tel'Abim Banana")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Gilneas Hot Stew",
        price=DirectPrice(itemid=84041),
        spell_aliases=[("uses_line", "Gilneas Hot Stew")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Greater Healing Potion",
        price=NoPrice(),  # TODO
        spell_aliases=[("uses_line", "Greater Healing Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Green Garden Tea",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Green Garden Tea")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Handful of Rose Petals",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Handful of Rose Petals")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Healing Potion",
        price=NoPrice(),  # TODO
        spell_aliases=[("uses_line", "Healing Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Heavy Runecloth Bandage",
        price=NoPrice(),  # TODO
        spell_aliases=[("uses_line", "Heavy Runecloth Bandage")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Highpeak Thistle",
        price=NoPrice(),  # useless
        spell_aliases=[("uses_line", "Highpeak Thistle")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Hot Smoked Bass",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Hot Smoked Bass")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Juicy Striped Melon",
        price=DirectPrice(itemid=51718),
        spell_aliases=[("uses_line", "Juicy Striped Melon")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Lesser Stoneshield Potion",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Lesser Stoneshield Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Lily Root",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Lily Root")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Magic Dust",
        price=DirectPrice(itemid=2091),
        spell_aliases=[("uses_line", "Magic Dust")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Major Healing Draught",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Major Healing Draught")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Major Mana Draught",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Major Mana Draught")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Mightfish Steak",
        price=NoPrice(),  # TODO
        spell_aliases=[("uses_line", "Mightfish Steak")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Minor Healing Potion",
        price=NoPrice(),  # TODO
        spell_aliases=[("uses_line", "Minor Healing Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Minor Magic Resistance Potion",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Minor Magic Resistance Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Morning Glory Dew",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Morning Glory Dew")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Mug of Shimmer Stout",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Mug of Shimmer Stout")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Oil of Olaf",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Oil of Olaf")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Party Grenade",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Party Grenade")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Plump Country Pumpkin",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Plump Country Pumpkin")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Potion of Fervor",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Potion of Fervor")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Raptor Punch",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Raptor Punch")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Raw Slitherskin Mackerel",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Raw Slitherskin Mackerel")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Razorlash Root",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Razorlash Root")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Really Sticky Glue",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Really Sticky Glue")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Refreshing Red Apple",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Refreshing Red Apple")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Restoring Balm",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Restoring Balm")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Ripe Tel'Abim Banana",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Ripe Tel'Abim Banana")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Roast Raptor",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Roast Raptor")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Roasted Kodo Meat",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Roasted Kodo Meat")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Runecloth Bandage",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Runecloth Bandage")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Scorpid Surprise",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Scorpid Surprise")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Scroll of Empowered Protection",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Scroll of Empowered Protection")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Scroll of Magic Warding",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Scroll of Magic Warding")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Scroll of Thorns",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Scroll of Thorns")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Senggin Root",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Senggin Root")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Spiced Beef Jerky",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Spiced Beef Jerky")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Stormstout",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Stormstout")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Sun-Parched Waterskin",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Sun-Parched Waterskin")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Super Snuff",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Super Snuff")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Superior Healing Draught",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Superior Healing Draught")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Superior Mana Draught",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Superior Mana Draught")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Sweet Mountain Berry",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Sweet Mountain Berry")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Swim Speed Potion",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Swim Speed Potion")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Tasty Summer Treat",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Tasty Summer Treat")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Toasted Smorc",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Toasted Smorc")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Volatile Concoction",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Volatile Concoction")],
        strategy=SafeStrategy(),
    ),
    SuperwowConsumable(
        name="Watered-down Beer",
        price=NoPrice(),
        spell_aliases=[("uses_line", "Watered-down Beer")],
        strategy=SafeStrategy(),
    ),
]


