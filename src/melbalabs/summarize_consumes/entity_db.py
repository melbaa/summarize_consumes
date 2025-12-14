"""
Central spell database using component model.
All spells with their properties defined in one place.
"""

from melbalabs.summarize_consumes.entity_model import Entity
from melbalabs.summarize_consumes.entity_model import PlayerClass
from melbalabs.summarize_consumes.entity_model import TrinketComponent
from melbalabs.summarize_consumes.entity_model import InterruptSpellComponent
from melbalabs.summarize_consumes.entity_model import RacialSpellComponent
from melbalabs.summarize_consumes.entity_model import ClassCooldownComponent
from melbalabs.summarize_consumes.entity_model import ReceiveBuffSpellComponent


# spell name -> item name map
TRINKET_RENAME = {
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
    "Elunes Guardian": "The Scythe of Elune",
    "Molten Power": "Molten Emberstone",
    "Blood Fury (trinket)": "Gri'lek's Charm of Might",
}


all_entities = [
    Entity("Kick", [InterruptSpellComponent()]),
    Entity("Pummel", [InterruptSpellComponent()]),
    Entity("Shield Bash", [InterruptSpellComponent()]),
    Entity("Earth Shock", [InterruptSpellComponent()]),
    Entity("Blood Fury", [RacialSpellComponent()]),
    Entity("Berserking", [RacialSpellComponent()]),
    Entity("Stoneform", [RacialSpellComponent()]),
    Entity("Desperate Prayer", [RacialSpellComponent()]),
    Entity("Will of the Forsaken", [RacialSpellComponent()]),
    Entity("War Stomp", [RacialSpellComponent()]),
    Entity("Blood Fury (trinket)", [TrinketComponent()]),
    Entity("Kiss of the Spider", [TrinketComponent()]),
    Entity("Slayer's Crest", [TrinketComponent()]),
    Entity("Jom Gabbar", [TrinketComponent()]),
    Entity("Badge of the Swarmguard", [TrinketComponent()]),
    Entity("Earthstrike", [TrinketComponent()]),
    Entity("Diamond Flask", [TrinketComponent()]),
    Entity("The Eye of the Dead", [TrinketComponent()]),
    Entity("Healing of the Ages", [TrinketComponent()]),
    Entity("Essence of Sapphiron", [TrinketComponent()]),
    Entity("Ephemeral Power", [TrinketComponent()]),
    Entity("Unstable Power", [TrinketComponent()]),
    Entity("Mind Quickening", [TrinketComponent()]),
    Entity("Nature Aligned", [TrinketComponent()]),
    Entity("Death by Peasant", [TrinketComponent()]),
    Entity("Immune Charm/Fear/Stun", [TrinketComponent()]),
    Entity("Immune Charm/Fear/Polymorph", [TrinketComponent()]),
    Entity("Immune Fear/Polymorph/Snare", [TrinketComponent()]),
    Entity("Immune Fear/Polymorph/Stun", [TrinketComponent()]),
    Entity("Immune Root/Snare/Stun", [TrinketComponent()]),
    Entity("Jewel of Wild Magics", [TrinketComponent()]),
    Entity("Remains of Overwhelming Power", [TrinketComponent()]),
    Entity("Elunes Guardian", [TrinketComponent()]),
    Entity("Molten Power", [TrinketComponent()]),
    Entity("Rapid Healing", [TrinketComponent()]),
    Entity("Chromatic Infusion", [TrinketComponent()]),
    Entity("Power Infusion", [ReceiveBuffSpellComponent()]),
    Entity("Bloodlust", [ReceiveBuffSpellComponent()]),
    Entity("Chastise Haste", [ReceiveBuffSpellComponent()]),
    Entity("Death Wish", [ClassCooldownComponent([PlayerClass.WARRIOR])]),
    Entity("Sweeping Strikes", [ClassCooldownComponent([PlayerClass.WARRIOR])]),
    Entity("Shield Wall", [ClassCooldownComponent([PlayerClass.WARRIOR])]),
    Entity("Recklessness", [ClassCooldownComponent([PlayerClass.WARRIOR])]),
    Entity("Bloodrage", [ClassCooldownComponent([PlayerClass.WARRIOR])]),
    Entity("Combustion", [ClassCooldownComponent([PlayerClass.MAGE])]),
    Entity("Scorch", [ClassCooldownComponent([PlayerClass.MAGE])]),
    Entity(
        "Nature's Swiftness",
        [
            ClassCooldownComponent([PlayerClass.SHAMAN, PlayerClass.DRUID]),  # shared spell
        ],
    ),
    Entity("Windfury Totem", [ClassCooldownComponent([PlayerClass.SHAMAN])]),
    Entity("Mana Tide Totem", [ClassCooldownComponent([PlayerClass.SHAMAN])]),
    Entity("Grace of Air Totem", [ClassCooldownComponent([PlayerClass.SHAMAN])]),
    Entity("Tranquil Air Totem", [ClassCooldownComponent([PlayerClass.SHAMAN])]),
    Entity("Strength of Earth Totem", [ClassCooldownComponent([PlayerClass.SHAMAN])]),
    Entity("Mana Spring Totem", [ClassCooldownComponent([PlayerClass.SHAMAN])]),
    Entity("Searing Totem", [ClassCooldownComponent([PlayerClass.SHAMAN])]),
    Entity("Fire Nova Totem", [ClassCooldownComponent([PlayerClass.SHAMAN])]),
    Entity("Magma Totem", [ClassCooldownComponent([PlayerClass.SHAMAN])]),
    Entity("Ancestral Spirit", [ClassCooldownComponent([PlayerClass.SHAMAN])]),
    Entity("Rebirth", [ClassCooldownComponent([PlayerClass.DRUID])]),
    Entity("Swiftmend", [ClassCooldownComponent([PlayerClass.DRUID])]),
    Entity("Inner Focus", [ClassCooldownComponent([PlayerClass.PRIEST])]),
    Entity("Resurrection", [ClassCooldownComponent([PlayerClass.PRIEST])]),
    Entity("Divine Favor", [ClassCooldownComponent([PlayerClass.PALADIN])]),
    Entity("Holy Shock (heal)", [ClassCooldownComponent([PlayerClass.PALADIN])]),
    Entity("Holy Shock (dmg)", [ClassCooldownComponent([PlayerClass.PALADIN])]),
    Entity("Redemption", [ClassCooldownComponent([PlayerClass.PALADIN])]),
    Entity("Adrenaline Rush", [ClassCooldownComponent([PlayerClass.ROGUE])]),
    Entity("Blade Flurry", [ClassCooldownComponent([PlayerClass.ROGUE])]),
    Entity("Rapid Fire", [ClassCooldownComponent([PlayerClass.HUNTER])]),
]
