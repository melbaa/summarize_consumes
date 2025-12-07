from typing import List

from melbalabs.summarize_consumes.parser import TreeType
from melbalabs.summarize_consumes.entity_model import Entity
from melbalabs.summarize_consumes.consumable_model import Ingredient
from melbalabs.summarize_consumes.consumable_model import Consumable
from melbalabs.summarize_consumes.consumable_model import DirectPrice
from melbalabs.summarize_consumes.consumable_model import SuperwowConsumable
from melbalabs.summarize_consumes.consumable_model import IgnoreStrategyComponent
from melbalabs.summarize_consumes.consumable_model import SafeStrategyComponent
from melbalabs.summarize_consumes.consumable_model import EnhanceStrategyComponent
from melbalabs.summarize_consumes.consumable_model import OverwriteStrategyComponent
from melbalabs.summarize_consumes.consumable_model import PriceFromIngredients
from melbalabs.summarize_consumes.consumable_model import NoPrice

_purple_lotus = Ingredient(name="Purple Lotus", price=DirectPrice(itemid=8831))
_large_brilliant_shard = Ingredient(name="Large Brilliant Shard", price=DirectPrice(itemid=14344))
_scorpok_pincer = Ingredient(name="Scorpok Pincer", price=DirectPrice(itemid=8393))
_blasted_boar_lung = Ingredient(name="Blasted Boar Lung", price=DirectPrice(itemid=8392))
_snickerfang_jowl = Ingredient(name="Snickerfang Jowl", price=DirectPrice(itemid=8391))
_basilisk_brain = Ingredient(name="Basilisk Brain", price=DirectPrice(itemid=8394))
_vulture_gizzard = Ingredient(name="Vulture Gizzard", price=DirectPrice(itemid=8396))
_zulian_coin = Ingredient(name="Zulian Coin", price=DirectPrice(itemid=19698))
_deeprock_salt = Ingredient(name="Deeprock Salt", price=DirectPrice(itemid=8150))
_essence_of_fire = Ingredient(name="Essence of Fire", price=DirectPrice(itemid=7078))
_larval_acid = Ingredient(name="Larval Acid", price=DirectPrice(itemid=18512))
_small_dream_shard = Ingredient(name="Small Dream Shard", price=DirectPrice(itemid=61198))
_bright_dream_shard = Ingredient(name="Bright Dream Shard", price=DirectPrice(itemid=61199))
_green_power_crystal = Ingredient(name="Green Power Crystal", price=DirectPrice(itemid=11185))
_blue_power_crystal = Ingredient(name="Blue Power Crystal", price=DirectPrice(itemid=11184))
_red_power_crystal = Ingredient(name="Red Power Crystal", price=DirectPrice(itemid=11186))
_yellow_power_crystal = Ingredient(name="Yellow Power Crystal", price=DirectPrice(itemid=11188))


all_defined_consumable_items: List[Entity] = [
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
        price=PriceFromIngredients(
            charges=6,
            ingredients=[
                (_green_power_crystal, 10),
                (_red_power_crystal, 10),
            ],
        ),
        spell_aliases=[(TreeType.GAINS_LINE, "Crystal Ward")],
    ),
    SuperwowConsumable(
        name="Crystal Force",
        price=PriceFromIngredients(
            charges=6,
            ingredients=[
                (_green_power_crystal, 10),
                (_blue_power_crystal, 10),
            ],
        ),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Crystal Force"),
            (TreeType.USES_LINE, "Crystal Force"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Crystal Spire",
        price=PriceFromIngredients(
            charges=6,
            ingredients=[
                (_blue_power_crystal, 10),
                (_yellow_power_crystal, 10),
            ],
        ),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Crystal Spire"),
            (TreeType.USES_LINE, "Crystal Spire"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Crystal Charge",
        price=PriceFromIngredients(
            charges=6,
            ingredients=[
                (_yellow_power_crystal, 10),
                (_red_power_crystal, 10),
            ],
        ),
        spell_aliases=[(TreeType.USES_LINE, "Crystal Charge")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Brilliant Mana Oil",
        price=DirectPrice(charges=5, itemid=20748),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Brilliant Mana Oil"),
            (TreeType.USES_LINE, "Brilliant Mana Oil"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Brilliant Mana Oil"),
    ),
    Consumable(
        name="Lesser Mana Oil",
        price=DirectPrice(charges=5, itemid=20747),
        spell_aliases=[(TreeType.BEGINS_TO_CAST_LINE, "Lesser Mana Oil")],
    ),
    SuperwowConsumable(
        name="Blessed Wizard Oil",
        price=DirectPrice(itemid=23123),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Blessed Wizard Oil"),
            (TreeType.USES_LINE, "Blessed Wizard Oil"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Blessed Wizard Oil"),
    ),
    SuperwowConsumable(
        name="Brilliant Wizard Oil",
        price=DirectPrice(charges=5, itemid=20749),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Brilliant Wizard Oil"),
            (TreeType.USES_LINE, "Brilliant Wizard Oil"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Brilliant Wizard Oil"),
    ),
    SuperwowConsumable(
        name="Wizard Oil",
        price=DirectPrice(charges=5, itemid=20750),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Wizard Oil"),
            (TreeType.USES_LINE, "Wizard Oil"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Wizard Oil"),
    ),
    Consumable(
        name="Frost Oil",
        price=DirectPrice(itemid=3829),
        spell_aliases=[(TreeType.BEGINS_TO_CAST_LINE, "Frost Oil")],
    ),
    SuperwowConsumable(
        name="Shadow Oil",
        price=DirectPrice(itemid=3824),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Shadow Oil"),
            (TreeType.USES_LINE, "Shadow Oil"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Shadow Oil"),
    ),
    SuperwowConsumable(
        name="Rage of Ages (ROIDS)",
        price=PriceFromIngredients(
            ingredients=[
                (_scorpok_pincer, 1),
                (_blasted_boar_lung, 2),
                (_snickerfang_jowl, 3),
            ]
        ),
        spell_aliases=[(TreeType.GAINS_LINE, "Rage of Ages"), (TreeType.USES_LINE, "Rage of Ages")],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Strike of the Scorpok",
        price=PriceFromIngredients(
            ingredients=[
                (_blasted_boar_lung, 1),
                (_vulture_gizzard, 2),
                (_scorpok_pincer, 3),
            ]
        ),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Strike of the Scorpok"),
            (TreeType.USES_LINE, "Ground Scorpok Assay"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Lung Juice Cocktail",
        price=PriceFromIngredients(
            ingredients=[
                (_basilisk_brain, 1),
                (_scorpok_pincer, 2),
                (_blasted_boar_lung, 3),
            ]
        ),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Spirit of the Boar"),
            (TreeType.USES_LINE, "Lung Juice Cocktail"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Gizzard Gum (Spiritual Domination)",
        price=PriceFromIngredients(
            ingredients=[
                (_vulture_gizzard, 10),
                (_snickerfang_jowl, 2),
            ]
        ),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Spiritual Domination"),
            (TreeType.USES_LINE, "Gizzard Gum"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Infallible Mind (Cerebral Cortex Compound)",
        price=PriceFromIngredients(
            ingredients=[
                (_basilisk_brain, 10),
                (_vulture_gizzard, 2),
            ]
        ),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Infallible Mind"),
            (TreeType.USES_LINE, "Cerebral Cortex Compound"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Sheen of Zanza",
        price=PriceFromIngredients(ingredients=[(_zulian_coin, 3)]),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Sheen of Zanza"),
            (TreeType.USES_LINE, "Sheen of Zanza"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Spirit of Zanza",
        price=PriceFromIngredients(ingredients=[(_zulian_coin, 3)]),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Spirit of Zanza"),
            (TreeType.USES_LINE, "Spirit of Zanza"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Swiftness of Zanza",
        price=PriceFromIngredients(ingredients=[(_zulian_coin, 3)]),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Swiftness of Zanza"),
            (TreeType.USES_LINE, "Swiftness of Zanza"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Powerful Smelling Salts",
        price=PriceFromIngredients(
            ingredients=[
                (_deeprock_salt, 4),
                (_essence_of_fire, 2),
                (_larval_acid, 1),
            ]
        ),
        spell_aliases=[
            (TreeType.PERFORMS_ON_LINE, "Powerful Smelling Salts"),
            (TreeType.USES_LINE, "Powerful Smelling Salts"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Tea with Sugar",
        price=PriceFromIngredients(ingredients=[(_small_dream_shard, 1 / 5)]),
        spell_aliases=[
            (TreeType.HEALS_LINE, "Tea"),
            (TreeType.HEALS_LINE, "Tea with Sugar"),
            (TreeType.USES_LINE, "Tea with Sugar"),
            (TreeType.USES_LINE, "Tea With Sugar"),  # old name
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Tea with Sugar"),
    ),
    Consumable(
        # superwow, but looks like native logs
        name="Emerald Blessing",
        price=PriceFromIngredients(ingredients=[(_bright_dream_shard, 1)]),
        spell_aliases=[(TreeType.CASTS_LINE, "Emerald Blessing")],
    ),
    SuperwowConsumable(
        name="Hourglass Sand",
        price=DirectPrice(itemid=19183),
        spell_aliases=[(TreeType.USES_LINE, "Hourglass Sand")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Restorative Potion",
        price=DirectPrice(itemid=9030),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Restoration"),
            (TreeType.USES_LINE, "Restorative Potion"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Flask of Chromatic Resistance",
        price=DirectPrice(itemid=13513),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Chromatic Resistance"),
            (TreeType.USES_LINE, "Flask of Chromatic Resistance"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Flask of the Titans",
        price=DirectPrice(itemid=13510),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Flask of the Titans"),
            (TreeType.USES_LINE, "Flask of the Titans"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Flask of Supreme Power",
        price=DirectPrice(itemid=13512),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Supreme Power"),
            (TreeType.USES_LINE, "Flask of Supreme Power"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Flask of Distilled Wisdom",
        price=DirectPrice(itemid=13511),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Distilled Wisdom"),
            (TreeType.USES_LINE, "Flask of Distilled Wisdom"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Flask of Petrification",
        price=DirectPrice(itemid=13506),
        spell_aliases=[(TreeType.USES_LINE, "Flask of Petrification")],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Fortitude",
        price=DirectPrice(itemid=3825),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Health II"),
            (TreeType.USES_LINE, "Elixir of Fortitude"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Bogling Root",
        price=DirectPrice(itemid=5206),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Fury of the Bogling"),
            (TreeType.USES_LINE, "Bogling Root"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    Consumable(
        name="Crystal Basilisk Spine",
        price=DirectPrice(itemid=1703),
        spell_aliases=[(TreeType.GAINS_LINE, "Crystal Protection")],
    ),
    SuperwowConsumable(
        name="??? Elixir of the Sages ???",
        price=DirectPrice(itemid=13447),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Elixir of the Sages"),
            (TreeType.USES_LINE, "Elixir of the Sages"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Greater Agility",
        price=DirectPrice(itemid=9187),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Greater Agility"),
            (TreeType.USES_LINE, "Elixir of Greater Agility"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Superior Defense",
        price=DirectPrice(itemid=13445),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Greater Armor"),
            (TreeType.USES_LINE, "Elixir of Superior Defense"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Free Action Potion",
        price=DirectPrice(itemid=5634),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Free Action"),
            (TreeType.USES_LINE, "Free Action Potion"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Frost Power",
        price=DirectPrice(itemid=17708),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Frost Power"),
            (TreeType.USES_LINE, "Elixir of Frost Power"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Greater Arcane Elixir",
        price=DirectPrice(itemid=13454),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Greater Arcane Elixir"),
            (TreeType.USES_LINE, "Greater Arcane Elixir"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Thistle Tea",
        price=DirectPrice(itemid=7676),
        spell_aliases=[(TreeType.GAINS_LINE, "100 energy"), (TreeType.USES_LINE, "Thistle Tea")],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Brute Force",
        price=DirectPrice(itemid=13453),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Elixir of Brute Force"),
            (TreeType.USES_LINE, "Elixir of Brute Force"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Winterfall Firewater",
        price=DirectPrice(itemid=12820),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Winterfall Firewater"),
            (TreeType.USES_LINE, "Winterfall Firewater"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Great Rage Potion",
        price=DirectPrice(itemid=5633),
        spell_aliases=[
            (TreeType.GAINS_RAGE_LINE, "Great Rage"),
            (TreeType.USES_LINE, "Great Rage Potion"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Rage Potion",
        price=DirectPrice(itemid=5631),
        spell_aliases=[(TreeType.GAINS_RAGE_LINE, "Rage"), (TreeType.USES_LINE, "Rage Potion")],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Juju Power",
        price=DirectPrice(itemid=12431),
        spell_aliases=[(TreeType.USES_LINE, "Juju Power")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Juju Flurry",
        price=DirectPrice(itemid=12430),
        spell_aliases=[(TreeType.USES_LINE, "Juju Flurry")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Juju Might",
        price=DirectPrice(itemid=12436),
        spell_aliases=[(TreeType.USES_LINE, "Juju Might")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Juju Guile",
        price=DirectPrice(itemid=12433),
        spell_aliases=[(TreeType.USES_LINE, "Juju Guile")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Juju Escape",
        price=DirectPrice(itemid=12435),
        spell_aliases=[(TreeType.USES_LINE, "Juju Escape")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Juju Ember",
        price=DirectPrice(itemid=12432),
        spell_aliases=[(TreeType.USES_LINE, "Juju Ember")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Juju Chill",
        price=DirectPrice(itemid=12434),
        spell_aliases=[(TreeType.USES_LINE, "Juju Chill")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Gurubashi Gumbo",
        price=DirectPrice(itemid=53015),
        spell_aliases=[(TreeType.USES_LINE, "Gurubashi Gumbo")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Hardened Mushroom",
        price=DirectPrice(itemid=51717),
        spell_aliases=[(TreeType.USES_LINE, "Hardened Mushroom")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Increased Stamina"),
    ),
    SuperwowConsumable(
        name="Oil of Immolation",
        price=DirectPrice(itemid=8956),
        spell_aliases=[(TreeType.USES_LINE, "Oil of Immolation")],
        strategy=SafeStrategyComponent(),
    ),
    Consumable(
        name="??? Lesser Stoneshield Potion ???",
        price=DirectPrice(itemid=4623),
        spell_aliases=[(TreeType.GAINS_LINE, "Stoneshield")],
    ),
    SuperwowConsumable(
        name="Greater Stoneshield",
        price=DirectPrice(itemid=13455),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Greater Stoneshield"),
            (TreeType.USES_LINE, "Greater Stoneshield Potion"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Lucidity Potion",
        price=DirectPrice(itemid=61225),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Lucidity Potion"),
            (TreeType.USES_LINE, "Lucidity Potion"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    Consumable(
        name="Restore Mana (mana potion)",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.GAINS_MANA_LINE, "Restore Mana (mana potion)"),
        ],
    ),
    SuperwowConsumable(
        name="Mana Potion - Minor",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.GAINS_MANA_LINE, "Mana Potion - Minor"),
            (TreeType.USES_LINE, "Minor Mana Potion"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Restore Mana (mana potion)"),
    ),
    SuperwowConsumable(
        name="Mana Potion - Lesser",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.GAINS_MANA_LINE, "Mana Potion - Lesser"),
            (TreeType.USES_LINE, "Full Moonshine"),  # small inaccuracy in logger
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Restore Mana (mana potion)"),
    ),
    SuperwowConsumable(
        name="Mana Potion",
        price=DirectPrice(itemid=3827),
        spell_aliases=[
            (TreeType.GAINS_MANA_LINE, "Mana Potion"),
            (TreeType.USES_LINE, "Mana Potion"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Restore Mana (mana potion)"),
    ),
    SuperwowConsumable(
        name="Mana Potion - Greater",
        price=DirectPrice(itemid=6149),
        spell_aliases=[
            (TreeType.GAINS_MANA_LINE, "Mana Potion - Greater"),
            (TreeType.USES_LINE, "Greater Mana Potion"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Restore Mana (mana potion)"),
    ),
    SuperwowConsumable(
        name="Mana Potion - Superior",
        price=DirectPrice(itemid=13443),
        spell_aliases=[
            (TreeType.GAINS_MANA_LINE, "Mana Potion - Superior"),
            (TreeType.USES_LINE, "Superior Mana Potion"),
            (TreeType.USES_LINE, "Combat Mana Potion"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Restore Mana (mana potion)"),
    ),
    SuperwowConsumable(
        name="Mana Potion - Major",
        price=DirectPrice(itemid=13444),
        spell_aliases=[
            (TreeType.GAINS_MANA_LINE, "Mana Potion - Major"),
            (TreeType.USES_LINE, "Major Mana Potion"),
            (TreeType.USES_LINE, "Diet McWeaksauce"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Restore Mana (mana potion)"),
    ),
    SuperwowConsumable(
        name="Healing Potion - Major",
        price=DirectPrice(itemid=13446),
        spell_aliases=[
            (TreeType.HEALS_LINE, "Healing Potion - Major"),
            (TreeType.USES_LINE, "Major Healing Potion"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Healing Potion - unknown"),
    ),
    SuperwowConsumable(
        name="Healing Potion - Superior",
        price=DirectPrice(itemid=3928),
        spell_aliases=[
            (TreeType.HEALS_LINE, "Healing Potion - Superior"),
            (TreeType.USES_LINE, "Combat Healing Potion"),
            (TreeType.USES_LINE, "Superior Healing Potion"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Healing Potion - unknown"),
    ),
    SuperwowConsumable(
        name="Healing Potion - Greater",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.HEALS_LINE, "Healing Potion - Greater"),
            (TreeType.USES_LINE, "Greater Healing Potion"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Healing Potion - unknown"),
    ),
    SuperwowConsumable(
        name="Healing Potion",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.HEALS_LINE, "Healing Potion"),
            (TreeType.USES_LINE, "Healing Potion"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Healing Potion - unknown"),
    ),
    SuperwowConsumable(
        name="Healing Potion - Lesser",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.HEALS_LINE, "Healing Potion - Lesser"),
            (TreeType.USES_LINE, "Lesser Healing Potion"),
            (TreeType.USES_LINE, "Discolored Healing Potion"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Healing Potion - unknown"),
    ),
    SuperwowConsumable(
        name="Healing Potion - Minor",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.HEALS_LINE, "Healing Potion - Minor"),
            (TreeType.USES_LINE, "Minor Healing Potion"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Healing Potion - unknown"),
    ),
    Consumable(
        name="Healing Potion - unknown",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.HEALS_LINE, "Healing Potion - unknown"),
        ],
    ),
    SuperwowConsumable(
        name="Elixir of Giants",
        price=DirectPrice(itemid=9206),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Elixir of the Giants"),
            (TreeType.USES_LINE, "Elixir of Giants"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Rumsey Rum Black Label",
        price=DirectPrice(itemid=21151),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Rumsey Rum Black Label"),
            (TreeType.USES_LINE, "Rumsey Rum Black Label"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Rumsey Rum Dark",
        price=DirectPrice(itemid=21114),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Rumsey Rum Dark"),
            (TreeType.USES_LINE, "Rumsey Rum Dark"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elemental Sharpening Stone",
        price=DirectPrice(itemid=18262),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Sharpen Weapon - Critical"),
            (TreeType.USES_LINE, "Elemental Sharpening Stone"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Elemental Sharpening Stone"),
    ),
    SuperwowConsumable(
        name="Consecrated Sharpening Stone",
        price=DirectPrice(itemid=23122),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Consecrated Weapon"),
            (TreeType.USES_LINE, "Consecrated Sharpening Stone"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Consecrated Sharpening Stone"),
    ),
    SuperwowConsumable(
        name="Invulnerability",
        price=DirectPrice(itemid=3387),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Invulnerability"),
            (TreeType.USES_LINE, "Limited Invulnerability Potion"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Dragonbreath Chili",
        price=DirectPrice(itemid=12217),
        spell_aliases=[(TreeType.USES_LINE, "Dragonbreath Chili")],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Dreamtonic",
        price=DirectPrice(itemid=61423),
        spell_aliases=[(TreeType.GAINS_LINE, "Dreamtonic"), (TreeType.USES_LINE, "Dreamtonic")],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Goblin Sapper Charge",
        price=DirectPrice(itemid=10646),
        spell_aliases=[(TreeType.USES_LINE, "Goblin Sapper Charge")],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Medivh's Merlot Blue Label",
        price=DirectPrice(itemid=61175),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Medivh's Merlot Blue Label"),
            (TreeType.USES_LINE, "Medivhs Merlot Blue Label"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Medivh's Merlot",
        price=DirectPrice(itemid=61174),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Medivh's Merlot"),
            (TreeType.USES_LINE, "Medivhs Merlot"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Greater Arcane Protection Potion",
        price=DirectPrice(itemid=13461),
        spell_aliases=[(TreeType.USES_LINE, "Greater Arcane Protection Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Arcane Protection"),
    ),
    SuperwowConsumable(
        name="Greater Holy Protection Potion",
        price=DirectPrice(itemid=13460),
        spell_aliases=[(TreeType.USES_LINE, "Greater Holy Protection Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Holy Protection"),
    ),
    SuperwowConsumable(
        name="Greater Shadow Protection Potion",
        price=DirectPrice(itemid=13459),
        spell_aliases=[(TreeType.USES_LINE, "Greater Shadow Protection Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Shadow Protection"),
    ),
    SuperwowConsumable(
        name="Greater Nature Protection Potion",
        price=DirectPrice(itemid=13458),
        spell_aliases=[(TreeType.USES_LINE, "Greater Nature Protection Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Nature Protection"),
    ),
    SuperwowConsumable(
        name="Greater Fire Protection Potion",
        price=DirectPrice(itemid=13457),
        spell_aliases=[(TreeType.USES_LINE, "Greater Fire Protection Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Fire Protection"),
    ),
    SuperwowConsumable(
        name="Greater Frost Protection Potion",
        price=DirectPrice(itemid=13456),
        spell_aliases=[(TreeType.USES_LINE, "Greater Frost Protection Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Frost Protection"),
    ),
    SuperwowConsumable(
        name="Holy Protection Potion",
        price=DirectPrice(itemid=6051),
        spell_aliases=[(TreeType.USES_LINE, "Holy Protection Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Holy Protection"),
    ),
    SuperwowConsumable(
        name="Shadow Protection Potion",
        price=DirectPrice(itemid=6048),
        spell_aliases=[(TreeType.USES_LINE, "Shadow Protection Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Shadow Protection"),
    ),
    SuperwowConsumable(
        name="Nature Protection Potion",
        price=DirectPrice(itemid=6052),
        spell_aliases=[(TreeType.USES_LINE, "Nature Protection Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Nature Protection"),
    ),
    SuperwowConsumable(
        name="Fire Protection Potion",
        price=DirectPrice(itemid=6049),
        spell_aliases=[(TreeType.USES_LINE, "Fire Protection Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Fire Protection"),
    ),
    SuperwowConsumable(
        name="Frost Protection Potion",
        price=DirectPrice(itemid=6050),
        spell_aliases=[(TreeType.USES_LINE, "Frost Protection Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Frost Protection"),
    ),
    SuperwowConsumable(
        name="Dreamshard Elixir",
        price=DirectPrice(itemid=61224),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Dreamshard Elixir"),
            (TreeType.USES_LINE, "Dreamshard Elixir"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Dense Dynamite",
        price=DirectPrice(itemid=18641),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Dense Dynamite"),
            (TreeType.USES_LINE, "Dense Dynamite"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Dense Dynamite"),
    ),
    SuperwowConsumable(
        name="Solid Dynamite",
        price=DirectPrice(itemid=10507),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Solid Dynamite"),
            (TreeType.USES_LINE, "Solid Dynamite"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Gift of Arthas",
        price=DirectPrice(itemid=9088),
        spell_aliases=[(TreeType.USES_LINE, "Gift of Arthas")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Thorium Grenade",
        price=DirectPrice(itemid=15993),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Thorium Grenade"),
            (TreeType.USES_LINE, "Thorium Grenade"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Iron Grenade",
        price=DirectPrice(itemid=4390),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Iron Grenade"),
            (TreeType.USES_LINE, "Iron Grenade"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Grilled Squid",
        price=DirectPrice(itemid=13928),
        spell_aliases=[(TreeType.USES_LINE, "Grilled Squid")],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Greater Intellect",
        price=DirectPrice(itemid=9179),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Greater Intellect"),
            (TreeType.USES_LINE, "Elixir of Greater Intellect"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Rejuvenation Potion - Major",
        price=DirectPrice(itemid=18253),
        spell_aliases=[
            (TreeType.HEALS_LINE, "Major Rejuvenation Potion"),
            (TreeType.USES_LINE, "Major Rejuvenation Potion"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Rejuvenation Potion - Minor",
        price=DirectPrice(itemid=2456),
        spell_aliases=[
            (TreeType.HEALS_LINE, "Minor Rejuvenation Potion"),
            (TreeType.USES_LINE, "Minor Rejuvenation Potion"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Swiftness Potion",
        price=DirectPrice(itemid=2459),
        spell_aliases=[(TreeType.USES_LINE, "Swiftness Potion")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Invisibility Potion",
        price=DirectPrice(itemid=9172),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Invisibility"),
            (TreeType.USES_LINE, "Invisibility Potion"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Lesser Invisibility Potion",
        price=DirectPrice(itemid=3823),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Lesser Invisibility"),
            (TreeType.USES_LINE, "Lesser Invisibility Potion"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Powerful Anti-Venom",
        price=DirectPrice(itemid=19440),
        spell_aliases=[
            (TreeType.CASTS_LINE, "Powerful Anti-Venom"),
            (TreeType.USES_LINE, "Powerful Anti-Venom"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Strong Anti-Venom",
        price=DirectPrice(itemid=6453),
        spell_aliases=[
            (TreeType.CASTS_LINE, "Strong Anti-Venom"),
            (TreeType.USES_LINE, "Strong Anti-Venom"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Anti-Venom",
        price=DirectPrice(itemid=6452),
        spell_aliases=[(TreeType.CASTS_LINE, "Anti-Venom"), (TreeType.USES_LINE, "Anti-Venom")],
        strategy=EnhanceStrategyComponent(),
    ),
    Consumable(
        name="Dissolvent Poison II",
        price=DirectPrice(itemid=54010),
        spell_aliases=[(TreeType.BEGINS_TO_PERFORM_LINE, "Dissolvent Poison II")],
    ),
    SuperwowConsumable(
        name="Dark Rune",
        price=DirectPrice(itemid=20520),
        spell_aliases=[(TreeType.GAINS_MANA_LINE, "Dark Rune"), (TreeType.USES_LINE, "Dark Rune")],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Mageblood Potion",
        price=DirectPrice(itemid=20007),
        spell_aliases=[(TreeType.USES_LINE, "Mageblood Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Mana Regeneration (food or mageblood)"),
    ),
    SuperwowConsumable(
        name="Danonzo's Tel'Abim Surprise",
        price=DirectPrice(itemid=60976),
        spell_aliases=[(TreeType.USES_LINE, "Danonzos Tel'Abim Surprise")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Danonzo's Tel'Abim Delight",
        price=DirectPrice(itemid=60977),
        spell_aliases=[(TreeType.USES_LINE, "Danonzos Tel'Abim Delight")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Danonzo's Tel'Abim Medley",
        price=DirectPrice(itemid=60978),
        spell_aliases=[(TreeType.USES_LINE, "Danonzos Tel'Abim Medley")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Wildvine Potion",
        price=DirectPrice(itemid=9144),
        spell_aliases=[(TreeType.USES_LINE, "Wildvine Potion")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Scroll of Stamina IV",
        price=DirectPrice(itemid=10307),
        spell_aliases=[(TreeType.USES_LINE, "Scroll of Stamina IV")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Stamina"),
    ),
    SuperwowConsumable(
        name="Scroll of Strength IV",
        price=DirectPrice(itemid=10310),
        spell_aliases=[(TreeType.USES_LINE, "Scroll of Strength IV")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Strength"),
    ),
    SuperwowConsumable(
        name="Scroll of Spirit IV",
        price=DirectPrice(itemid=10306),
        spell_aliases=[(TreeType.USES_LINE, "Scroll of Spirit IV")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Spirit"),
    ),
    SuperwowConsumable(
        name="Scroll of Protection IV",
        price=DirectPrice(itemid=10305),
        spell_aliases=[(TreeType.USES_LINE, "Scroll of Protection IV")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Armor"),
    ),
    SuperwowConsumable(
        name="Scroll of Intellect IV",
        price=DirectPrice(itemid=10308),
        spell_aliases=[(TreeType.USES_LINE, "Scroll of Intellect IV")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Intellect"),
    ),
    SuperwowConsumable(
        name="Scroll of Agility IV",
        price=DirectPrice(itemid=10309),
        spell_aliases=[(TreeType.USES_LINE, "Scroll of Agility IV")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Agility"),
    ),
    SuperwowConsumable(
        name="Purification Potion",
        price=DirectPrice(itemid=13462),
        spell_aliases=[(TreeType.USES_LINE, "Purification Potion")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Poisonous Mushroom",
        price=DirectPrice(itemid=5823),
        spell_aliases=[(TreeType.USES_LINE, "Poisonous Mushroom")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Nightfin Soup",
        price=DirectPrice(itemid=13931),
        spell_aliases=[(TreeType.USES_LINE, "Nightfin Soup")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Mana Regeneration (food or mageblood)"),
    ),
    SuperwowConsumable(
        name="Weak Troll's Blood Potion",
        price=DirectPrice(itemid=3382),
        spell_aliases=[(TreeType.USES_LINE, "Weak Trolls Blood Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Regeneration"),
    ),
    SuperwowConsumable(
        name="Strong Troll's Blood Potion",
        price=DirectPrice(itemid=3388),
        spell_aliases=[(TreeType.USES_LINE, "Strong Trolls Blood Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Regeneration"),
    ),
    SuperwowConsumable(
        name="Major Troll's Blood Potion",
        price=DirectPrice(itemid=20004),
        spell_aliases=[(TreeType.USES_LINE, "Major Trolls Blood Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Regeneration"),
    ),
    SuperwowConsumable(
        name="Mighty Troll's Blood Potion",
        price=DirectPrice(itemid=3826),
        spell_aliases=[(TreeType.USES_LINE, "Mighty Trolls Blood Potion")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Regeneration"),
    ),
    SuperwowConsumable(
        name="Magic Resistance Potion",
        price=DirectPrice(itemid=9036),
        spell_aliases=[(TreeType.USES_LINE, "Magic Resistance Potion")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Jungle Remedy",
        price=DirectPrice(itemid=2633),
        spell_aliases=[
            (TreeType.CASTS_LINE, "Cure Ailments"),
            (TreeType.USES_LINE, "Jungle Remedy"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Living Action Potion",
        price=DirectPrice(itemid=20008),
        spell_aliases=[(TreeType.USES_LINE, "Living Action Potion")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Empowering Herbal Salad",
        price=DirectPrice(itemid=83309),
        spell_aliases=[(TreeType.USES_LINE, "Empowering Herbal Salad")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Poison Resistance",
        price=DirectPrice(itemid=3386),
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Poison Resistance")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Demonslaying",
        price=DirectPrice(itemid=9224),
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Demonslaying")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Graccu's Homemade Meat Pie",
        price=DirectPrice(itemid=17407),
        spell_aliases=[(TreeType.USES_LINE, "Graccus Homemade Meat Pie")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Greater Dreamless Sleep Potion",
        price=DirectPrice(itemid=20002),
        spell_aliases=[(TreeType.USES_LINE, "Greater Dreamless Sleep Potion")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Greater Defense",
        price=DirectPrice(itemid=8951),
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Greater Defense")],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Giant Growth",
        price=DirectPrice(itemid=6662),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Enlarge"),
            (TreeType.USES_LINE, "Elixir of Giant Growth"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Frozen Rune",
        price=DirectPrice(itemid=22682),
        spell_aliases=[(TreeType.USES_LINE, "Frozen Rune")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Fire Protection"),
    ),
    SuperwowConsumable(
        name="Arcane Elixir",
        price=DirectPrice(itemid=9155),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Arcane Elixir"),
            (TreeType.USES_LINE, "Arcane Elixir"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Dense Sharpening Stone",
        price=DirectPrice(itemid=12404),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Sharpen Blade V"),
            (TreeType.USES_LINE, "Dense Sharpening Stone"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Dense Sharpening Stone"),
    ),
    SuperwowConsumable(
        name="Dense Weightstone",
        price=DirectPrice(itemid=12643),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Enhance Blunt Weapon V"),
            (TreeType.USES_LINE, "Dense Weightstone"),
        ],
        strategy=OverwriteStrategyComponent(target_consumable_name="Dense Weightstone"),
    ),
    SuperwowConsumable(
        name="Bloodkelp Elixir of Resistance",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Elixir of Resistance"),
            (TreeType.USES_LINE, "Bloodkelp Elixir of Resistance"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Bloodkelp Elixir of Dodging",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Elixir of Dodging"),
            (TreeType.USES_LINE, "Bloodkelp Elixir of Dodging"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    Consumable(
        name="Fire-toasted Bun",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Fire-toasted Bun")],
    ),
    SuperwowConsumable(
        name="Blessed Sunfruit",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Blessed Sunfruit"),
            (TreeType.USES_LINE, "Blessed Sunfruit"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Blessed Sunfruit Juice",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Blessed Sunfruit Juice"),
            (TreeType.USES_LINE, "Blessed Sunfruit Juice"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Windblossom Berries",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Windblossom Berries")],
        strategy=OverwriteStrategyComponent(target_consumable_name="Increased Stamina"),
    ),
    SuperwowConsumable(
        name="Rumsey Rum",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Rumsey Rum"), (TreeType.USES_LINE, "Rumsey Rum")],
        strategy=EnhanceStrategyComponent(),
    ),
    Consumable(
        name="Increased Stamina",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Increased Stamina")],
    ),
    Consumable(
        name="Increased Intellect",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Increased Intellect")],
    ),
    Consumable(
        name="Mana Regeneration (food or mageblood)",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Mana Regeneration")],
    ),
    Consumable(
        name="Regeneration",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Regeneration")],
    ),
    Consumable(
        name="Agility",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Agility")],
    ),
    Consumable(
        name="Strength",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Strength")],
    ),
    Consumable(
        name="Stamina",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Stamina")],
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
        spell_aliases=[(TreeType.GAINS_LINE, "Fire Protection")],
    ),
    Consumable(
        name="Frost Protection",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Frost Protection")],
    ),
    Consumable(
        name="Arcane Protection",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Arcane Protection")],
    ),
    Consumable(
        name="Nature Protection",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Nature Protection ")],  # need the trailing space
    ),
    Consumable(
        name="Shadow Protection",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Shadow Protection ")],  # need the trailing space
    ),
    Consumable(
        name="Holy Protection",
        price=NoPrice(),
        spell_aliases=[(TreeType.GAINS_LINE, "Holy Protection ")],  # need the trailing space
    ),
    SuperwowConsumable(
        name="Kreeg's Stout Beatdown",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.BEGINS_TO_CAST_LINE, "Kreeg's Stout Beatdown"),
            (TreeType.USES_LINE, "Kreegs Stout Beatdown"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    Consumable(
        name="Advanced Target Dummy",
        price=DirectPrice(itemid=4392),
        spell_aliases=[(TreeType.CASTS_LINE, "Advanced Target Dummy")],
    ),
    Consumable(
        name="Masterwork Target Dummy",
        price=DirectPrice(itemid=16023),
        spell_aliases=[(TreeType.CASTS_LINE, "Masterwork Target Dummy")],
    ),
    SuperwowConsumable(
        name="Conjured Mana Orange",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Conjured Mana Orange")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Conjured Crystal Water",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Conjured Crystal Water")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Winter Veil Eggnog",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Winter Veil Eggnog")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Winter Veil Candy",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Winter Veil Candy")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Winter Veil Cookie",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Winter Veil Cookie")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Gift of Friendship - Ironforge (stam)",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Ironforge Gift of Friendship")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Gift of Friendship - Stormwind (int)",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Stormwind Gift of Friendship")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Gift of Friendship - Darnassus (agi)",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Darnassus Gift of Friendship")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Gift of Friendship - Orgrimmar (agi)",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Orgrimmar Gift of Friendship")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Gift of Friendship - Thunder Bluff (stam)",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Thunder Bluff Gift of Friendship")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Gift of Friendship - Undercity (int)",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Undercity Gift of Friendship")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Slumber Sand",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Slumber Sand")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Sweet Surprise",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Sweet Surprise")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Midsummer Sausage",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Midsummer Sausage")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Very Berry Cream",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Very Berry Cream")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Dark Desire",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Dark Desire")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Buttermilk Delight",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Buttermilk Delight")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Graccu's Mince Meat Fruitcake",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Graccus Mince Meat Fruitcake")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="MOLL-E, Remote Mail Terminal",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "MOLL-E, Remote Mail Terminal")],
        strategy=IgnoreStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Goblin Brainwashing Device",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Goblin Brainwashing Device")],
        strategy=IgnoreStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Stratholme Holy Water",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Stratholme Holy Water")],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Firepower",
        price=DirectPrice(itemid=6373),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Fire Power"),
            (TreeType.USES_LINE, "Elixir of Firepower"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Greater Firepower",
        price=DirectPrice(itemid=21546),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Greater Firepower"),
            (TreeType.USES_LINE, "Elixir of Greater Firepower"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Shadow Power",
        price=DirectPrice(itemid=9264),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Shadow Power"),
            (TreeType.USES_LINE, "Elixir of Shadow Power"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Potion of Quickness",
        price=DirectPrice(itemid=61181),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Potion of Quickness"),
            (TreeType.USES_LINE, "Potion of Quickness"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Le Fishe Au Chocolat",
        price=DirectPrice(itemid=84040),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Le Fishe Au Chocolat"),
            (TreeType.USES_LINE, "Le Fishe Au Chocolat"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of the Mongoose",
        price=DirectPrice(itemid=13452),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Elixir of the Mongoose"),
            (TreeType.USES_LINE, "Elixir of the Mongoose"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Greater Nature Power",
        price=DirectPrice(itemid=50237),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Elixir of Greater Nature Power"),
            (TreeType.USES_LINE, "Elixir of Greater Nature Power"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Power Mushroom",
        price=DirectPrice(itemid=51720),
        spell_aliases=[(TreeType.USES_LINE, "Power Mushroom")],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Gordok Green Grog",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Gordok Green Grog"),
            (TreeType.USES_LINE, "Gordok Green Grog"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Mighty Rage Potion",
        price=DirectPrice(itemid=13442),
        spell_aliases=[
            (TreeType.GAINS_RAGE_LINE, "Mighty Rage"),
            (TreeType.USES_LINE, "Mighty Rage Potion"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Noggenfogger Elixir",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.GAINS_LINE, "Noggenfogger Elixir"),
            (TreeType.USES_LINE, "Noggenfogger Elixir"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Demonic Rune",
        price=NoPrice(),
        spell_aliases=[
            (TreeType.GAINS_MANA_LINE, "Demonic Rune"),
            (TreeType.USES_LINE, "Demonic Rune"),
        ],
        strategy=EnhanceStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Baked Salmon",
        price=DirectPrice(itemid=13935),
        spell_aliases=[(TreeType.USES_LINE, "Baked Salmon")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Blended Bean Brew",
        price=NoPrice(),  # has price, but low lvl
        spell_aliases=[(TreeType.USES_LINE, "Blended Bean Brew")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Boiled Clams",
        price=NoPrice(),  # has price, but low lvl
        spell_aliases=[(TreeType.USES_LINE, "Boiled Clams")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Bottled Alterac Spring Water",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Bottled Alterac Spring Water")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Bottled Winterspring Water",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Bottled Winterspring Water")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Bubbly Beverage",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Bubbly Beverage")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Catseye Elixir",
        price=NoPrice(),  # has price, but low lvl
        spell_aliases=[(TreeType.USES_LINE, "Catseye Elixir")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Cleaning Cloth",
        price=NoPrice(),  # has price, but low lvl
        spell_aliases=[(TreeType.USES_LINE, "Cleaning Cloth")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Cowardly Flight Potion",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Cowardly Flight Potion")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Crunchy Frog",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Crunchy Frog")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Crusty Flatbread",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Crusty Flatbread")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Crystal Infused Bandage",
        price=NoPrice(),  # TODO
        spell_aliases=[(TreeType.USES_LINE, "Crystal Infused Bandage")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Deepsea Lobster",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Deepsea Lobster")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Delicious Pizza",
        price=NoPrice(),  # TODO
        spell_aliases=[(TreeType.USES_LINE, "Delicious Pizza")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Dig Rat Stew",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Dig Rat Stew")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Dreamless Sleep Potion",
        price=DirectPrice(itemid=12190),
        spell_aliases=[(TreeType.USES_LINE, "Dreamless Sleep Potion")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Egg Nog",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Egg Nog")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elderberry Pie",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Elderberry Pie")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Agility",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Agility")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Defense",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Defense")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Detect Demon",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Detect Demon")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Detect Lesser Invisibility",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Detect Lesser Invisibility")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Detect Undead",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Detect Undead")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Greater Water Breathing",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Greater Water Breathing")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Lesser Agility",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Lesser Agility")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Lions Strength",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Lions Strength")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Minor Agility",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Minor Agility")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Minor Fortitude",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Minor Fortitude")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Ogres Strength",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Ogres Strength")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Water Breathing",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Water Breathing")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Water Walking",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Water Walking")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Elixir of Wisdom",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Elixir of Wisdom")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Festival Dumplings",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Festival Dumplings")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Fiery Festival Brew",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Fiery Festival Brew")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Fishliver Oil",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Fishliver Oil")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Fizzy Faire Drink",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Fizzy Faire Drink")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Freshly-Squeezed Lemonade",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Freshly-Squeezed Lemonade")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Gargantuan Tel'Abim Banana",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Gargantuan Tel'Abim Banana")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Gilneas Hot Stew",
        price=DirectPrice(itemid=84041),
        spell_aliases=[(TreeType.USES_LINE, "Gilneas Hot Stew")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Green Garden Tea",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Green Garden Tea")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Handful of Rose Petals",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Handful of Rose Petals")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Heavy Runecloth Bandage",
        price=NoPrice(),  # TODO
        spell_aliases=[(TreeType.USES_LINE, "Heavy Runecloth Bandage")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Highpeak Thistle",
        price=NoPrice(),  # useless
        spell_aliases=[(TreeType.USES_LINE, "Highpeak Thistle")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Hot Smoked Bass",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Hot Smoked Bass")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Juicy Striped Melon",
        price=DirectPrice(itemid=51718),
        spell_aliases=[(TreeType.USES_LINE, "Juicy Striped Melon")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Lesser Stoneshield Potion",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Lesser Stoneshield Potion")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Lily Root",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Lily Root")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Magic Dust",
        price=DirectPrice(itemid=2091),
        spell_aliases=[(TreeType.USES_LINE, "Magic Dust")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Major Healing Draught",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Major Healing Draught")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Major Mana Draught",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Major Mana Draught")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Mightfish Steak",
        price=NoPrice(),  # TODO
        spell_aliases=[(TreeType.USES_LINE, "Mightfish Steak")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Minor Magic Resistance Potion",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Minor Magic Resistance Potion")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Morning Glory Dew",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Morning Glory Dew")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Mug of Shimmer Stout",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Mug of Shimmer Stout")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Oil of Olaf",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Oil of Olaf")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Party Grenade",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Party Grenade")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Plump Country Pumpkin",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Plump Country Pumpkin")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Potion of Fervor",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Potion of Fervor")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Raptor Punch",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Raptor Punch")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Raw Slitherskin Mackerel",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Raw Slitherskin Mackerel")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Razorlash Root",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Razorlash Root")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Really Sticky Glue",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Really Sticky Glue")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Refreshing Red Apple",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Refreshing Red Apple")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Restoring Balm",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Restoring Balm")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Ripe Tel'Abim Banana",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Ripe Tel'Abim Banana")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Roast Raptor",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Roast Raptor")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Roasted Kodo Meat",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Roasted Kodo Meat")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Runecloth Bandage",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Runecloth Bandage")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Scorpid Surprise",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Scorpid Surprise")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Scroll of Empowered Protection",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Scroll of Empowered Protection")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Scroll of Magic Warding",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Scroll of Magic Warding")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Scroll of Thorns",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Scroll of Thorns")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Senggin Root",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Senggin Root")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Spiced Beef Jerky",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Spiced Beef Jerky")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Stormstout",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Stormstout")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Sun-Parched Waterskin",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Sun-Parched Waterskin")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Super Snuff",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Super Snuff")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Superior Healing Draught",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Superior Healing Draught")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Superior Mana Draught",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Superior Mana Draught")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Sweet Mountain Berry",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Sweet Mountain Berry")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Swim Speed Potion",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Swim Speed Potion")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Tasty Summer Treat",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Tasty Summer Treat")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Toasted Smorc",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Toasted Smorc")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Volatile Concoction",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Volatile Concoction")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Watered-down Beer",
        price=NoPrice(),
        spell_aliases=[(TreeType.USES_LINE, "Watered-down Beer")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Concoction of the Emerald Mongoose",
        price=DirectPrice(itemid=47410),
        spell_aliases=[(TreeType.USES_LINE, "Concoction of the Emerald Mongoose")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Concoction of the Arcane Giant",
        price=DirectPrice(itemid=47412),
        spell_aliases=[(TreeType.USES_LINE, "Concoction of the Arcane Giant")],
        strategy=SafeStrategyComponent(),
    ),
    SuperwowConsumable(
        name="Concoction of the Dreamwater",
        price=DirectPrice(itemid=47414),
        spell_aliases=[(TreeType.USES_LINE, "Concoction of the Dreamwater")],
        strategy=SafeStrategyComponent(),
    ),
]
