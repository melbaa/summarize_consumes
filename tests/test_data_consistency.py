from melbalabs.summarize_consumes.main import NAME2ITEMID
from melbalabs.summarize_consumes.main import NAME2ITEMID_BOP
from melbalabs.summarize_consumes.main import NAME2CONSUMABLE
from melbalabs.summarize_consumes.main import USES_CONSUMABLE_RENAME
from melbalabs.summarize_consumes.main import USES_CONSUMABLE_ENHANCE
from melbalabs.summarize_consumes.main import USES_CONSUMABLE_OVERWRITE
from melbalabs.summarize_consumes.main import USES_CONSUMABLE_SAFE
from melbalabs.summarize_consumes.main import all_defined_consumable_items

from melbalabs.summarize_consumes.consumable import PriceFromComponents
from melbalabs.summarize_consumes.consumable import DirectPrice



def test_consumes_exist():
    logger_consumes = {
"Bloodkelp Elixir of Resistance",
"Bloodkelp Elixir of Dodging",
"Jungle Remedy",
"Elixir of Fortitude",
"Shadow Oil",
"Juicy Striped Melon",
"Ironforge Gift of Friendship",
"Darnassus Gift of Friendship",
"Elixir of Giant Growth",
"Orgrimmar Gift of Friendship",
"Thunder Bluff Gift of Friendship",
"Undercity Gift of Friendship",
"Wizard Oil",
"Arcanite Dragonling",
"Brilliant Mana Oil",
"Mug of Shimmer Stout",
"Elixir of Poison Resistance",
"Elixir of Water Walking",
"Le Fishe Au Chocolat",
"Raw Slitherskin Mackerel",
"Gilneas Hot Stew",
"Hardened Mushroom",
"Elixir of Agility",
"Fire Protection Potion",
"Magic Dust",
"Elixir of Greater Agility",
"Frost Protection Potion",
"Buttermilk Delight",
"Very Berry Cream",
"Sweet Surprise",
"Dark Desire",
"Holy Protection Potion",
"Senggin Root",
"Ancient Cornerstone Grimoire",
"Elixir of Superior Defense",
"Elixir of Greater Defense",
"Nature Protection Potion",
"Elixir of Lesser Agility",
"Elixir of Ogres Strength",
"Hourglass Sand",
"Elixir of Wisdom",
"Restorative Potion",
"Lesser Invisibility Potion",
"Limited Invulnerability Potion",
"Powerful Smelling Salts",
"Magic Resistance Potion",
"Party Grenade",
"Graccus Homemade Meat Pie",
"Crunchy Frog",
"Ripe Tel'Abim Banana",
"Green Garden Tea",
"Bottled Winterspring Water",
"Morning Glory Dew",
"Crystal Basilisk Spine",
"Mighty Rage Potion",
"Combat Mana Potion",
"Wildvine Potion",
"Elixir of Detect Undead",
"Major Healing Potion",
"Greater Mana Potion",
"Invisibility Potion",
"Elixir of Brute Force",
"Elixir of the Mongoose",
"Conjured Mana Orange",
"Elixir of Greater Intellect",
"Greater Fire Protection Potion",
"Greater Frost Protection Potion",
"Greater Holy Protection Potion",
"Greater Nature Protection Potion",
"Greater Shadow Protection Potion",
"Elixir of Giants",
"Elixir of Demonslaying",
"Elixir of Detect Demon",
"Bottled Alterac Spring Water",
"Weak Trolls Blood Potion",
"Fire-toasted Bun",
"Midsummer Sausage",
"Toasted Smorc",
"Festival Dumplings",
"Egg Nog",
"Swim Speed Potion",
"Oil of Olaf",
"Elixir of Firepower",
"Runecloth Bandage",
"Heavy Runecloth Bandage",
"Slumber Sand",
"Major Rejuvenation Potion",
"Juicy Striped Melon",
"Blessed Sunfruit",
"Noggenfogger Elixir",
"Conjured Crystal Water",
"Elixir of Shadow Power",
"Alchemists Stone",
"Danonzos Tel'Abim Medley",
"Flask of Petrification",
"Flask of the Titans",
"Flask of Distilled Wisdom",
"Flask of Supreme Power",
"Flask of Chromatic Resistance",
"Danonzos Tel'Abim Surprise",
"Power Mushroom",
"Blessed Wizard Oil",
"Fishliver Oil",
"Powerful Anti-Venom",
"Dense Weightstone",
"Frost Oil",
"Super Snuff",
"Frozen Rune",
"Anti-Venom",
"Strong Anti-Venom",
"Tea with Sugar",
"Gordok Green Grog",
"Kreegs Stout Beatdown",
"Scorpid Surprise",
"Lesser Mana Oil",
"Nightfin Soup",
"Medivhs Merlot Blue Label",
"Watered-down Beer",
"Elixir of Greater Water Breathing",
"Demonic Rune",
"Winter Veil Eggnog",
"Winter Veil Cookie",
"Potion of Fervor",
"Thistle Tea",
"Major Trolls Blood Potion",
"Mageblood Potion",
"Living Action Potion",
"Sweet Mountain Berry",
"Grilled Squid",
"Hot Smoked Bass",
"Nightfin Soup",
"Mightfish Steak",
"Spirit of Zanza",
"Elixir of Lions Strength",
"Catseye Elixir",
"Minor Rejuvenation Potion",
"Crystal Infused Bandage",
"Elixir of Minor Agility",
"Elixir of Minor Fortitude",
"Swiftness Potion",
"Minor Magic Resistance Potion",
"Lesser Stoneshield Potion",
"Bubbly Beverage",
"Freshly-Squeezed Lemonade",
"Deepsea Lobster",
"Scroll of Thorns",
"Sheen of Zanza",
"Elixir of Detect Lesser Invisibility",
"Potion of Quickness",
"Lucidity Potion",
"Dreamshard Elixir",
"Scroll of Magic Warding",
"Winterfall Firewater",
"Major Mana Potion",
"Crystal Force",
"Elixir of the Sages",
"Greater Stoneshield Potion",
"Greater Arcane Protection Potion",
"Barov Peasant Caller",
"Barov Peasant Caller",
"Purification Potion",
"Graccus Mince Meat Fruitcake",
"Crystal Charge",
"Lesser Mark of the Dawn",
"Mark of the Dawn",
"Greater Mark of the Dawn",
"Rumsey Rum",
"Roasted Kodo Meat",
"Boiled Clams",
"Plump Country Pumpkin",
"Roast Raptor",
"Empowering Herbal Salad",
"Gargantuan Tel'Abim Banana",
"Superior Healing Draught",
"Major Mana Draught",
"Superior Mana Draught",
"Greater Dreamless Sleep Potion",
"Swiftness of Zanza",
"Elixir of Greater Firepower",
"Low Energy Regulator",
"Shimmering Moonstone Tablet",
"Coldhowls Necklace",
"The Black Pendant",
"Stormstout",
"Permanent Sheen of Zanza",
"Permanent Spirit of Zanza",
"Permanent Swiftness of Zanza",
"Elixir of Frost Power",
"Crusty Flatbread",
"Poisonous Mushroom",
"Tasty Summer Treat",
"Elixir of Greater Nature Power",
"Really Sticky Glue",
"Oil of Immolation",
"Gift of Arthas",
"Dig Rat Stew",
"Goblin Sapper Charge",
"Severed Voodoo Claw",
"Rage of Ages",
"Lung Juice Cocktail",
"Ground Scorpok Assay",
"Windblossom Berries",
"Blended Bean Brew",
"Fizzy Faire Drink",
"Dreamtonic",
"Spiced Beef Jerky",
"Handful of Rose Petals",
"Blessed Sunfruit Juice",
"Minor Mana Potion",
"Full Moonshine",
"Minor Healing Potion",
"Discolored Healing Potion",
"Healing Potion",
"Scroll of Empowered Protection",
"Solid Dynamite",
"Medivhs Merlot",
"Elixir of Water Breathing",
"Bogling Root",
"Scroll of Protection IV",
"Brilliant Wizard Oil",
"Juju Escape",
"Juju Flurry",
"Razorlash Root",
"Cerebral Cortex Compound",
"Winter Veil Candy",
"Juju Ember",
"Juju Guile",
"Stratholme Holy Water",
"Juju Might",
"Combat Healing Potion",
"Dense Dynamite",
"Goblin Brainwashing Device",
"Thorium Grenade",
"Dreamless Sleep Potion",
"Baked Salmon",
"Stormwind Gift of Friendship",
"Rumsey Rum Dark",
"Defender of the Timbermaw",
"Dense Sharpening Stone",
"Rage Potion",
"Great Rage Potion",
"Cowardly Flight Potion",
"Free Action Potion",
"Gnomish Battle Chicken",
"Arcane Elixir",
"Greater Arcane Elixir",
"Elemental Sharpening Stone",
"Dark Rune",
"Consecrated Sharpening Stone",
"Danonzos Tel'Abim Delight",
"Rumsey Rum Black Label",
"Delicious Pizza",
"Juju Chill",
"Raptor Punch",
"Juju Power",
"Iron Grenade",
"Goblin Rocket Boots",
"Highpeak Thistle",
"Mana Potion",
"Greater Healing Potion",
"MOLL-E, Remote Mail Terminal",
"Crystal Spire",
"Sun-Parched Waterskin",
"Dragonbreath Chili",
"Refreshing Red Apple",
"Restoring Balm",
"Mighty Trolls Blood Potion",
"Strong Trolls Blood Potion",
"Elixir of Defense",
"Scroll of Strength IV",
"Scroll of Stamina IV",
"Scroll of Spirit IV",
"Scroll of Intellect IV",
"Cleaning Cloth",
"Scroll of Agility IV",
"Lily Root",
"Major Healing Draught",
"Shadow Protection Potion",
"Gizzard Gum",
"Gurubashi Gumbo",
"Volatile Concoction",
"Fiery Festival Brew",
"Elderberry Pie",



    }
    skips = {
        'Permanent Swiftness of Zanza',
        'Permanent Spirit of Zanza',
        'Permanent Sheen of Zanza',
        'The Black Pendant',
        'Shimmering Moonstone Tablet',
    }
    found = set()

    # check if the logger consume is added to USES_CONSUMABLE whitelists
    # and to NAME2ITEMID for pricing
    for key in logger_consumes:
        if key.startswith('Danonzo'): continue
        if key in skips: continue
        key = USES_CONSUMABLE_RENAME.get(key, key)
        whitelisted = 0
        if key in USES_CONSUMABLE_SAFE:
            whitelisted += 1
        elif key in USES_CONSUMABLE_ENHANCE:
            key = USES_CONSUMABLE_ENHANCE.get(key, key)
            whitelisted += 1
        elif key in USES_CONSUMABLE_OVERWRITE:
            whitelisted += 1
        else:
            found.add((key, 'not categorized'))
            continue

        if key in NAME2CONSUMABLE:
            continue
        if key in NAME2ITEMID:
            continue
        if key in NAME2ITEMID_BOP:
            continue

        found.add((key, 'not priced'))
    for key in sorted(found):
        print(key)
    # assert not found


def test_sanity1():

    for name in NAME2ITEMID:
        assert name in NAME2CONSUMABLE
        assert NAME2CONSUMABLE[name].price.itemid == NAME2ITEMID[name]


def test_sanity3():
    assert set(NAME2ITEMID_BOP).isdisjoint(set(NAME2ITEMID))

def test_uses_consumable_disjoint():
    enh = set(USES_CONSUMABLE_ENHANCE)
    ow = set(USES_CONSUMABLE_OVERWRITE)
    safe = set(USES_CONSUMABLE_SAFE)
    assert enh.isdisjoint(ow)
    assert enh.isdisjoint(safe)
    assert ow.isdisjoint(safe)

def test_sanity4():
    # check if a SAFE consumable isn't that safe
    

    # Check that SAFE consumables don't have spell aliases outside of uses_line
    for safe_consumable in USES_CONSUMABLE_SAFE:
        for consumable_item in all_defined_consumable_items:
            if safe_consumable != consumable_item.name: continue
            print(safe_consumable)
            for line_type, raw_spellname in consumable_item.spell_aliases:
                if line_type != 'uses_line':
                    raise ValueError(
                        f'{safe_consumable} found in spell_alias with anothe line_type {line_type}, '
                        'but SAFE consumables should only appear in uses_line'
                    )


def test_sanity5():
    uniq = len(set(consumable.name for consumable in all_defined_consumable_items))
    len(all_defined_consumable_items) == uniq

