from melbalabs.summarize_consumes.entity_model import Entity
from melbalabs.summarize_consumes.entity_model import PlayerClass
from melbalabs.summarize_consumes.entity_model import TrinketComponent
from melbalabs.summarize_consumes.entity_model import InterruptSpellComponent
from melbalabs.summarize_consumes.entity_model import RacialSpellComponent
from melbalabs.summarize_consumes.entity_model import ClassCooldownComponent
from melbalabs.summarize_consumes.entity_model import ReceiveBuffSpellComponent
from melbalabs.summarize_consumes.entity_model import get_entities_with_component


_blood_fury_trinket = Entity("Blood Fury (trinket)", [])
_healing_of_the_ages = Entity("Healing of the Ages", [])
_essence_of_sapphiron = Entity("Essence of Sapphiron", [])
_ephemeral_power = Entity("Ephemeral Power", [])
_unstable_power = Entity("Unstable Power", [])
_mind_quickening = Entity("Mind Quickening", [])
_nature_aligned = Entity("Nature Aligned", [])
_death_by_peasant = Entity("Death by Peasant", [])
_immune_charm_fear_stun = Entity("Immune Charm/Fear/Stun", [])
_immune_charm_fear_polymorph = Entity("Immune Charm/Fear/Polymorph", [])
_immune_fear_polymorph_snare = Entity("Immune Fear/Polymorph/Snare", [])
_immune_fear_polymorph_stun = Entity("Immune Fear/Polymorph/Stun", [])
_immune_root_snare_stun = Entity("Immune Root/Snare/Stun", [])
_elunes_guardian = Entity("Elunes Guardian", [])
_molten_power = Entity("Molten Power", [])
_rapid_healing = Entity("Rapid Healing", [])
_chromatic_infusion = Entity("Chromatic Infusion", [])


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
    _blood_fury_trinket,
    _healing_of_the_ages,
    _essence_of_sapphiron,
    _ephemeral_power,
    _unstable_power,
    _mind_quickening,
    _nature_aligned,
    _death_by_peasant,
    _immune_charm_fear_stun,
    _immune_charm_fear_polymorph,
    _immune_fear_polymorph_snare,
    _immune_fear_polymorph_stun,
    _immune_root_snare_stun,
    _elunes_guardian,
    _molten_power,
    _rapid_healing,
    _chromatic_infusion,
    Entity(
        "Gri'lek's Charm of Might",
        [TrinketComponent(triggered_by_spells=[_blood_fury_trinket.name])],
    ),
    Entity(
        "Hibernation Crystal", [TrinketComponent(triggered_by_spells=[_healing_of_the_ages.name])]
    ),
    Entity(
        "The Restrained Essence of Sapphiron",
        [TrinketComponent(triggered_by_spells=[_essence_of_sapphiron.name])],
    ),
    Entity(
        "Talisman of Ephemeral Power",
        [TrinketComponent(triggered_by_spells=[_ephemeral_power.name])],
    ),
    Entity(
        "Zandalarian Hero Charm", [TrinketComponent(triggered_by_spells=[_unstable_power.name])]
    ),
    Entity("Mind Quickening Gem", [TrinketComponent(triggered_by_spells=[_mind_quickening.name])]),
    Entity(
        "Natural Alignment Crystal", [TrinketComponent(triggered_by_spells=[_nature_aligned.name])]
    ),
    Entity(
        "Barov Peasant Caller", [TrinketComponent(triggered_by_spells=[_death_by_peasant.name])]
    ),
    Entity(
        "Insignia of the Alliance/Horde",
        [
            TrinketComponent(
                triggered_by_spells=[
                    _immune_charm_fear_stun.name,
                    _immune_charm_fear_polymorph.name,
                    _immune_fear_polymorph_snare.name,
                    _immune_fear_polymorph_stun.name,
                    _immune_root_snare_stun.name,
                ]
            )
        ],
    ),
    Entity("The Scythe of Elune", [TrinketComponent(triggered_by_spells=[_elunes_guardian.name])]),
    Entity("Molten Emberstone", [TrinketComponent(triggered_by_spells=[_molten_power.name])]),
    Entity(
        "Hazza'rah's Charm of Healing",
        [TrinketComponent(triggered_by_spells=[_rapid_healing.name])],
    ),
    Entity(
        "Draconic Infused Emblem",
        [TrinketComponent(triggered_by_spells=[_chromatic_infusion.name])],
    ),
    Entity("Kiss of the Spider", [TrinketComponent(triggered_by_spells=["Kiss of the Spider"])]),
    Entity("Slayer's Crest", [TrinketComponent(triggered_by_spells=["Slayer's Crest"])]),
    Entity("Jom Gabbar", [TrinketComponent(triggered_by_spells=["Jom Gabbar"])]),
    Entity(
        "Badge of the Swarmguard",
        [TrinketComponent(triggered_by_spells=["Badge of the Swarmguard"])],
    ),
    Entity("Earthstrike", [TrinketComponent(triggered_by_spells=["Earthstrike"])]),
    Entity("Diamond Flask", [TrinketComponent(triggered_by_spells=["Diamond Flask"])]),
    Entity("The Eye of the Dead", [TrinketComponent(triggered_by_spells=["The Eye of the Dead"])]),
    Entity(
        "Jewel of Wild Magics", [TrinketComponent(triggered_by_spells=["Jewel of Wild Magics"])]
    ),
    Entity(
        "Remains of Overwhelming Power",
        [TrinketComponent(triggered_by_spells=["Remains of Overwhelming Power"])],
    ),
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


def get_trinket_rename_map():
    rename_map = {}
    for entity, trinket_comp in get_entities_with_component(TrinketComponent):
        for spell_name in trinket_comp.triggered_by_spells:
            if spell_name != entity.name:
                rename_map[spell_name] = entity.name
    return rename_map


TRINKET_RENAME = get_trinket_rename_map()
