from melbalabs.summarize_consumes.entity_model import ClassDetectionComponent
from melbalabs.summarize_consumes.entity_model import TrackProcComponent
from melbalabs.summarize_consumes.entity_model import TrackSpellCastComponent
from melbalabs.summarize_consumes.entity_model import Entity
from melbalabs.summarize_consumes.entity_model import PlayerClass
from melbalabs.summarize_consumes.entity_model import TrinketComponent
from melbalabs.summarize_consumes.entity_model import InterruptSpellComponent
from melbalabs.summarize_consumes.entity_model import RacialSpellComponent
from melbalabs.summarize_consumes.entity_model import ClassCooldownComponent
from melbalabs.summarize_consumes.entity_model import ReceiveBuffSpellComponent
from melbalabs.summarize_consumes.entity_model import SpellAliasComponent
from melbalabs.summarize_consumes.entity_model import get_entities_with_component
from melbalabs.summarize_consumes.parser import TreeType


_blood_fury_trinket = Entity(
    "Blood Fury (trinket)",
    [SpellAliasComponent([(TreeType.GAINS_RAGE_LINE, "Blood Fury")]), TrackSpellCastComponent()],
)
_healing_of_the_ages = Entity(
    "Healing of the Ages",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Healing of the Ages")]),
        TrackSpellCastComponent(),
    ],
)
_essence_of_sapphiron = Entity(
    "Essence of Sapphiron",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Essence of Sapphiron")]),
        TrackSpellCastComponent(),
    ],
)
_ephemeral_power = Entity(
    "Ephemeral Power",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Ephemeral Power")]),
        TrackSpellCastComponent(),
    ],
)
_unstable_power = Entity(
    "Unstable Power",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Unstable Power")]),
        TrackSpellCastComponent(),
    ],
)
_mind_quickening = Entity(
    "Mind Quickening",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Mind Quickening")]),
        TrackSpellCastComponent(),
    ],
)
_nature_aligned = Entity(
    "Nature Aligned",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Nature Aligned")]),
        TrackSpellCastComponent(),
    ],
)
_death_by_peasant = Entity(
    "Death by Peasant",
    [
        TrackSpellCastComponent(),
        SpellAliasComponent([(TreeType.CASTS_LINE, "Death by Peasant")]),
    ],
)
_immune_charm_fear_stun = Entity(
    "Immune Charm/Fear/Stun",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Immune Charm/Fear/Stun")]),
        TrackSpellCastComponent(),
    ],
)
_immune_charm_fear_polymorph = Entity(
    "Immune Charm/Fear/Polymorph",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Immune Charm/Fear/Polymorph")]),
        TrackSpellCastComponent(),
    ],
)
_immune_fear_polymorph_snare = Entity(
    "Immune Fear/Polymorph/Snare",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Immune Fear/Polymorph/Snare")]),
        TrackSpellCastComponent(),
    ],
)
_immune_fear_polymorph_stun = Entity(
    "Immune Fear/Polymorph/Stun",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Immune Fear/Polymorph/Stun")]),
        TrackSpellCastComponent(),
    ],
)
_immune_root_snare_stun = Entity(
    "Immune Root/Snare/Stun",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Immune Root/Snare/Stun")]),
        TrackSpellCastComponent(),
    ],
)
_elunes_guardian = Entity(
    "Elunes Guardian",
    [
        SpellAliasComponent([(TreeType.CASTS_LINE, "Elunes Guardian")]),
        TrackSpellCastComponent(),
    ],
)
_molten_power = Entity(
    "Molten Power",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Molten Power")]),
        TrackSpellCastComponent(),
    ],
)
_rapid_healing = Entity(
    "Rapid Healing",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Rapid Healing")]),
        TrackSpellCastComponent(),
    ],
)
_chromatic_infusion = Entity(
    "Chromatic Infusion",
    [
        SpellAliasComponent([(TreeType.GAINS_LINE, "Chromatic Infusion")]),
        TrackSpellCastComponent(),
    ],
)


all_entities = [
    Entity("Kick", [InterruptSpellComponent()]),
    Entity("Pummel", [InterruptSpellComponent()]),
    Entity("Shield Bash", [InterruptSpellComponent()]),
    Entity("Earth Shock", [InterruptSpellComponent()]),
    Entity(
        "Blood Fury",
        [
            # superwow, spellid 23234
            RacialSpellComponent(),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Blood Fury")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Berserking",
        [
            RacialSpellComponent(),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Berserking")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Stoneform",
        [
            RacialSpellComponent(),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Stoneform")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Desperate Prayer",
        [
            RacialSpellComponent(),
            SpellAliasComponent([(TreeType.HEALS_LINE, "Desperate Prayer")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Will of the Forsaken",
        [
            RacialSpellComponent(),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Will of the Forsaken")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "War Stomp",
        [
            RacialSpellComponent(),
            SpellAliasComponent([(TreeType.BEGINS_TO_PERFORM_LINE, "War Stomp")]),
            TrackSpellCastComponent(),
        ],
    ),
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
    Entity(
        "Kiss of the Spider",
        [
            TrinketComponent(triggered_by_spells=["Kiss of the Spider"]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Kiss of the Spider")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Slayer's Crest",
        [
            TrinketComponent(triggered_by_spells=["Slayer's Crest"]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Slayer's Crest")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Jom Gabbar",
        [
            TrinketComponent(triggered_by_spells=["Jom Gabbar"]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Jom Gabbar")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Badge of the Swarmguard",
        [
            TrinketComponent(triggered_by_spells=["Badge of the Swarmguard"]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Badge of the Swarmguard")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Earthstrike",
        [
            TrinketComponent(triggered_by_spells=["Earthstrike"]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Earthstrike")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Diamond Flask",
        [
            TrinketComponent(triggered_by_spells=["Diamond Flask"]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Diamond Flask")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "The Eye of the Dead",
        [
            TrinketComponent(triggered_by_spells=["The Eye of the Dead"]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "The Eye of the Dead")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Jewel of Wild Magics",
        [
            TrinketComponent(triggered_by_spells=["Jewel of Wild Magics"]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Jewel of Wild Magics")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Remains of Overwhelming Power",
        [
            TrinketComponent(triggered_by_spells=["Remains of Overwhelming Power"]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Remains of Overwhelming Power")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Power Infusion",
        [
            ReceiveBuffSpellComponent(),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Power Infusion")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Bloodlust",
        [
            ReceiveBuffSpellComponent(),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Bloodlust")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Chastise Haste",
        [
            ReceiveBuffSpellComponent(),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Chastise Haste")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Sunder Armor",
        [
            # superwow
            TrackSpellCastComponent(),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Sunder Armor")]),
            ClassDetectionComponent(
                PlayerClass.WARRIOR,
                triggered_by=[(TreeType.CASTS_LINE, "Sunder Armor")],
            ),
        ],
    ),
    Entity(
        "Sunder Armor (boss)",
        [
            # superwow, renamed
            TrackSpellCastComponent(),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Sunder Armor (boss)")]),
        ],
    ),
    Entity(
        "Death Wish",
        [
            ClassCooldownComponent([PlayerClass.WARRIOR]),
            SpellAliasComponent([(TreeType.AFFLICTED_LINE, "Death Wish")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.WARRIOR,
                triggered_by=[(TreeType.AFFLICTED_LINE, "Death Wish")],
            ),
        ],
    ),
    Entity(
        "Sweeping Strikes",
        [
            ClassCooldownComponent([PlayerClass.WARRIOR]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Sweeping Strikes")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.WARRIOR,
                triggered_by=[(TreeType.GAINS_LINE, "Sweeping Strikes")],
            ),
        ],
    ),
    Entity(
        "Shield Wall",
        [
            ClassCooldownComponent([PlayerClass.WARRIOR]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Shield Wall")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.WARRIOR, triggered_by=[(TreeType.GAINS_LINE, "Shield Wall")]
            ),
        ],
    ),
    Entity(
        "Recklessness",
        [
            ClassCooldownComponent([PlayerClass.WARRIOR]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Recklessness")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.WARRIOR,
                triggered_by=[(TreeType.GAINS_LINE, "Recklessness")],
            ),
        ],
    ),
    Entity(
        "Bloodrage",
        [
            ClassCooldownComponent([PlayerClass.WARRIOR]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Bloodrage")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.WARRIOR, triggered_by=[(TreeType.GAINS_LINE, "Bloodrage")]
            ),
        ],
    ),
    Entity(
        "Combustion",
        [
            ClassCooldownComponent([PlayerClass.MAGE]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Combustion")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.MAGE, triggered_by=[(TreeType.GAINS_LINE, "Combustion")]
            ),
        ],
    ),
    Entity(
        "Scorch",
        [
            ClassCooldownComponent([PlayerClass.MAGE]),
            TrackSpellCastComponent(),
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Scorch")]),
            ClassDetectionComponent(
                PlayerClass.MAGE,
                triggered_by=[
                    (TreeType.HITS_ABILITY_LINE, "Scorch"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Scorch"),
                ],
            ),
        ],
    ),
    Entity(
        "Nature's Swiftness",
        [
            ClassCooldownComponent([PlayerClass.SHAMAN, PlayerClass.DRUID]),  # shared spell
            SpellAliasComponent([(TreeType.GAINS_LINE, "Nature's Swiftness")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Windfury Totem",
        [
            ClassCooldownComponent([PlayerClass.SHAMAN]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Windfury Totem")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.SHAMAN,
                triggered_by=[(TreeType.CASTS_LINE, "Windfury Totem")],
            ),
        ],
    ),
    Entity(
        "Mana Tide Totem",
        [
            ClassCooldownComponent([PlayerClass.SHAMAN]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Mana Tide Totem")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.SHAMAN,
                triggered_by=[(TreeType.CASTS_LINE, "Mana Tide Totem")],
            ),
        ],
    ),
    Entity(
        "Grace of Air Totem",
        [
            ClassCooldownComponent([PlayerClass.SHAMAN]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Grace of Air Totem")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.SHAMAN,
                triggered_by=[(TreeType.CASTS_LINE, "Grace of Air Totem")],
            ),
        ],
    ),
    Entity(
        "Tranquil Air Totem",
        [
            ClassCooldownComponent([PlayerClass.SHAMAN]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Tranquil Air Totem")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.SHAMAN,
                triggered_by=[(TreeType.CASTS_LINE, "Tranquil Air Totem")],
            ),
        ],
    ),
    Entity(
        "Strength of Earth Totem",
        [
            ClassCooldownComponent([PlayerClass.SHAMAN]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Strength of Earth Totem")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.SHAMAN,
                triggered_by=[(TreeType.CASTS_LINE, "Strength of Earth Totem")],
            ),
        ],
    ),
    Entity(
        "Mana Spring Totem",
        [
            ClassCooldownComponent([PlayerClass.SHAMAN]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Mana Spring Totem")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.SHAMAN,
                triggered_by=[(TreeType.CASTS_LINE, "Mana Spring Totem")],
            ),
        ],
    ),
    Entity(
        "Searing Totem",
        [
            ClassCooldownComponent([PlayerClass.SHAMAN]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Searing Totem")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.SHAMAN,
                triggered_by=[(TreeType.CASTS_LINE, "Searing Totem")],
            ),
        ],
    ),
    Entity(
        "Fire Nova Totem",
        [
            ClassCooldownComponent([PlayerClass.SHAMAN]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Fire Nova Totem")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.SHAMAN,
                triggered_by=[(TreeType.CASTS_LINE, "Fire Nova Totem")],
            ),
        ],
    ),
    Entity(
        "Magma Totem",
        [
            ClassCooldownComponent([PlayerClass.SHAMAN]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Magma Totem")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.SHAMAN,
                triggered_by=[(TreeType.CASTS_LINE, "Magma Totem")],
            ),
        ],
    ),
    Entity(
        "Ancestral Spirit",
        [
            ClassCooldownComponent([PlayerClass.SHAMAN]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Ancestral Spirit")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.SHAMAN,
                triggered_by=[(TreeType.CASTS_LINE, "Ancestral Spirit")],
            ),
        ],
    ),
    Entity(
        "Rebirth",
        [
            ClassCooldownComponent([PlayerClass.DRUID]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Rebirth")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.DRUID, triggered_by=[(TreeType.CASTS_LINE, "Rebirth")]
            ),
        ],
    ),
    Entity(
        "Swiftmend",
        [
            ClassCooldownComponent([PlayerClass.DRUID]),
            SpellAliasComponent([(TreeType.HEALS_LINE, "Swiftmend")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Inner Focus",
        [
            ClassCooldownComponent([PlayerClass.PRIEST]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Inner Focus")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Resurrection",
        [
            ClassCooldownComponent([PlayerClass.PRIEST]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Resurrection")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.PRIEST,
                triggered_by=[(TreeType.CASTS_LINE, "Resurrection")],
            ),
        ],
    ),
    Entity(
        "Divine Favor",
        [
            ClassCooldownComponent([PlayerClass.PALADIN]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Divine Favor")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.PALADIN,
                triggered_by=[(TreeType.GAINS_LINE, "Divine Favor")],
            ),
        ],
    ),
    Entity(
        "Holy Shock (heal)",
        [
            ClassCooldownComponent([PlayerClass.PALADIN]),
            SpellAliasComponent([(TreeType.HEALS_LINE, "Holy Shock")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.PALADIN,
                triggered_by=[(TreeType.HEALS_LINE, "Holy Shock")],
            ),
        ],
    ),
    Entity(
        "Holy Shock (dmg)",
        [
            ClassCooldownComponent([PlayerClass.PALADIN]),
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Holy Shock")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.PALADIN,
                triggered_by=[(TreeType.HITS_ABILITY_LINE, "Holy Shock")],
            ),
        ],
    ),
    Entity(
        "Redemption",
        [
            ClassCooldownComponent([PlayerClass.PALADIN]),
            SpellAliasComponent([(TreeType.CASTS_LINE, "Redemption")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.PALADIN, triggered_by=[(TreeType.CASTS_LINE, "Redemption")]
            ),
        ],
    ),
    Entity(
        "Adrenaline Rush",
        [
            ClassCooldownComponent([PlayerClass.ROGUE]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Adrenaline Rush")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.ROGUE,
                triggered_by=[(TreeType.GAINS_LINE, "Adrenaline Rush")],
            ),
        ],
    ),
    Entity(
        "Blade Flurry",
        [
            ClassCooldownComponent([PlayerClass.ROGUE]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Blade Flurry")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.ROGUE, triggered_by=[(TreeType.GAINS_LINE, "Blade Flurry")]
            ),
        ],
    ),
    Entity(
        "Sinister Strike",
        [
            TrackSpellCastComponent(),
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Sinister Strike")]),
            ClassDetectionComponent(
                PlayerClass.ROGUE,
                triggered_by=[(TreeType.HITS_ABILITY_LINE, "Sinister Strike")],
            ),
        ],
    ),
    Entity(
        "Rapid Fire",
        [
            ClassCooldownComponent([PlayerClass.HUNTER]),
            SpellAliasComponent([(TreeType.GAINS_LINE, "Rapid Fire")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Elemental Mastery",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Elemental Mastery")]),
            TrackSpellCastComponent(),
        ],
    ),
    Entity(
        "Cold Blood",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Cold Blood")]),
            TrackSpellCastComponent(),
            ClassDetectionComponent(
                PlayerClass.ROGUE, triggered_by=[(TreeType.GAINS_LINE, "Cold Blood")]
            ),
        ],
    ),
    Entity(
        "Enrage",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Enrage")]),
            TrackProcComponent(),
        ],
    ),
    Entity(
        "Flurry",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Flurry")]),
            TrackProcComponent(),
        ],
    ),
    Entity(
        "Elemental Devastation",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Elemental Devastation")]),
            TrackProcComponent(),
        ],
    ),
    Entity(
        "Stormcaller's Wrath",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Stormcaller's Wrath")]),
            TrackProcComponent(),
        ],
    ),
    Entity(
        "Spell Blasting",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Spell Blasting")]),
            TrackProcComponent(),
        ],
    ),
    Entity(
        "Clearcasting",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Clearcasting")]),
            TrackProcComponent(),
        ],
    ),
    Entity(
        "Vengeance",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Vengeance")]),
            TrackProcComponent(),
        ],
    ),
    Entity(
        "Nature's Grace",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Nature's Grace")]),
            TrackProcComponent(),
        ],
    ),
    Entity(
        "Unbridled Wrath",
        [
            SpellAliasComponent([(TreeType.GAINS_RAGE_LINE, "Unbridled Wrath")]),
            TrackProcComponent(),
        ],
    ),
    Entity(
        "Cleave",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Cleave")]),
            ClassDetectionComponent(
                PlayerClass.WARRIOR, triggered_by=[(TreeType.HITS_ABILITY_LINE, "Cleave")]
            ),
        ],
    ),
    Entity(
        "Whirlwind",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Whirlwind")]),
            ClassDetectionComponent(
                PlayerClass.WARRIOR,
                triggered_by=[(TreeType.HITS_ABILITY_LINE, "Whirlwind")],
            ),
        ],
    ),
    Entity(
        "Bloodthirst",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Bloodthirst")]),
            ClassDetectionComponent(
                PlayerClass.WARRIOR,
                triggered_by=[(TreeType.HITS_ABILITY_LINE, "Bloodthirst")],
            ),
        ],
    ),
    Entity(
        "Heroic Strike",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Heroic Strike")]),
            ClassDetectionComponent(
                PlayerClass.WARRIOR,
                triggered_by=[(TreeType.HITS_ABILITY_LINE, "Heroic Strike")],
            ),
        ],
    ),
    Entity(
        "Slice and Dice",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Slice and Dice")]),
            ClassDetectionComponent(
                PlayerClass.ROGUE, triggered_by=[(TreeType.GAINS_LINE, "Slice and Dice")]
            ),
        ],
    ),
    Entity(
        "Seal of Command",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Seal of Command")]),
            ClassDetectionComponent(
                PlayerClass.PALADIN,
                triggered_by=[(TreeType.GAINS_LINE, "Seal of Command")],
            ),
        ],
    ),
    Entity(
        "Seal of Righteousness",
        [
            SpellAliasComponent([(TreeType.GAINS_LINE, "Seal of Righteousness")]),
            ClassDetectionComponent(
                PlayerClass.PALADIN,
                triggered_by=[(TreeType.GAINS_LINE, "Seal of Righteousness")],
            ),
        ],
    ),
    Entity(
        "Flash of Light",
        [
            SpellAliasComponent([(TreeType.HEALS_LINE, "Flash of Light")]),
            ClassDetectionComponent(
                PlayerClass.PALADIN,
                triggered_by=[
                    (TreeType.HEALS_LINE, "Flash of Light"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Flash of Light"),
                ],
            ),
        ],
    ),
    Entity(
        "Holy Light",
        [
            SpellAliasComponent([(TreeType.HEALS_LINE, "Holy Light")]),
            ClassDetectionComponent(
                PlayerClass.PALADIN,
                triggered_by=[
                    (TreeType.HEALS_LINE, "Holy Light"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Holy Light"),
                ],
            ),
        ],
    ),
    Entity(
        "Heal",
        [
            SpellAliasComponent([(TreeType.HEALS_LINE, "Heal")]),
            ClassDetectionComponent(
                PlayerClass.PRIEST,
                triggered_by=[
                    (TreeType.HEALS_LINE, "Heal"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Heal"),
                ],
            ),
        ],
    ),
    Entity(
        "Flash Heal",
        [
            SpellAliasComponent([(TreeType.HEALS_LINE, "Flash Heal")]),
            ClassDetectionComponent(
                PlayerClass.PRIEST,
                triggered_by=[
                    (TreeType.HEALS_LINE, "Flash Heal"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Flash Heal"),
                ],
            ),
        ],
    ),
    Entity(
        "Greater Heal",
        [
            SpellAliasComponent([(TreeType.HEALS_LINE, "Greater Heal")]),
            ClassDetectionComponent(
                PlayerClass.PRIEST,
                triggered_by=[
                    (TreeType.HEALS_LINE, "Greater Heal"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Greater Heal"),
                ],
            ),
        ],
    ),
    Entity(
        "Prayer of Healing",
        [
            SpellAliasComponent([(TreeType.HEALS_LINE, "Prayer of Healing")]),
            ClassDetectionComponent(
                PlayerClass.PRIEST,
                triggered_by=[
                    (TreeType.HEALS_LINE, "Prayer of Healing"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Prayer of Healing"),
                ],
            ),
        ],
    ),
    Entity(
        "Mind Blast",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Mind Blast")]),
            ClassDetectionComponent(
                PlayerClass.PRIEST,
                triggered_by=[
                    (TreeType.HITS_ABILITY_LINE, "Mind Blast"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Mind Blast"),
                ],
            ),
        ],
    ),
    Entity(
        "Smite",
        [
            ClassDetectionComponent(
                PlayerClass.PRIEST,
                triggered_by=[(TreeType.BEGINS_TO_CAST_LINE, "Smite")],
            ),
        ],
    ),
    Entity(
        "Rejuvenation",
        [
            SpellAliasComponent([(TreeType.GAINS_HEALTH_LINE, "Rejuvenation")]),
            ClassDetectionComponent(
                PlayerClass.DRUID,
                triggered_by=[
                    (TreeType.GAINS_HEALTH_LINE, "Rejuvenation"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Rejuvenation"),
                ],
            ),
        ],
    ),
    Entity(
        "Regrowth",
        [
            SpellAliasComponent([(TreeType.GAINS_HEALTH_LINE, "Regrowth")]),
            ClassDetectionComponent(
                PlayerClass.DRUID,
                triggered_by=[
                    (TreeType.GAINS_HEALTH_LINE, "Regrowth"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Regrowth"),
                ],
            ),
        ],
    ),
    Entity(
        "Starfire",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Starfire")]),
            ClassDetectionComponent(
                PlayerClass.DRUID,
                triggered_by=[(TreeType.HITS_ABILITY_LINE, "Starfire")],
            ),
        ],
    ),
    Entity(
        "Moonfire",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Moonfire")]),
            ClassDetectionComponent(
                PlayerClass.DRUID,
                triggered_by=[(TreeType.HITS_ABILITY_LINE, "Moonfire")],
            ),
        ],
    ),
    Entity(
        "Wrath",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Wrath")]),
            ClassDetectionComponent(
                PlayerClass.DRUID,
                triggered_by=[
                    (TreeType.HITS_ABILITY_LINE, "Wrath"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Wrath"),
                ],
            ),
        ],
    ),
    Entity(
        "Arcane Explosion",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Arcane Explosion")]),
            ClassDetectionComponent(
                PlayerClass.MAGE,
                triggered_by=[(TreeType.HITS_ABILITY_LINE, "Arcane Explosion")],
            ),
        ],
    ),
    Entity(
        "Fire Blast",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Fire Blast")]),
            ClassDetectionComponent(
                PlayerClass.MAGE,
                triggered_by=[(TreeType.HITS_ABILITY_LINE, "Fire Blast")],
            ),
        ],
    ),
    Entity(
        "Fireball",
        [
            ClassDetectionComponent(
                PlayerClass.MAGE,
                triggered_by=[(TreeType.BEGINS_TO_CAST_LINE, "Fireball")],
            ),
        ],
    ),
    Entity(
        "Polymorph",
        [
            ClassDetectionComponent(
                PlayerClass.MAGE,
                triggered_by=[(TreeType.BEGINS_TO_CAST_LINE, "Polymorph")],
            ),
        ],
    ),
    Entity(
        "Shadow Bolt",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Shadow Bolt")]),
            ClassDetectionComponent(
                PlayerClass.WARLOCK,
                triggered_by=[
                    (TreeType.HITS_ABILITY_LINE, "Shadow Bolt"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Shadow Bolt"),
                ],
            ),
        ],
    ),
    Entity(
        "Arcane Shot",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Arcane Shot")]),
            ClassDetectionComponent(
                PlayerClass.HUNTER,
                triggered_by=[(TreeType.HITS_ABILITY_LINE, "Arcane Shot")],
            ),
        ],
    ),
    Entity(
        "Multi-Shot",
        [
            SpellAliasComponent([(TreeType.HITS_ABILITY_LINE, "Multi-Shot")]),
            ClassDetectionComponent(
                PlayerClass.HUNTER,
                triggered_by=[
                    (TreeType.HITS_ABILITY_LINE, "Multi-Shot"),
                    (TreeType.BEGINS_TO_CAST_LINE, "Multi-Shot"),
                ],
            ),
        ],
    ),
    Entity(
        "Auto Shot",
        [
            SpellAliasComponent([(TreeType.BEGINS_TO_PERFORM_LINE, "Auto Shot")]),
            ClassDetectionComponent(
                PlayerClass.HUNTER,
                triggered_by=[(TreeType.BEGINS_TO_PERFORM_LINE, "Auto Shot")],
            ),
        ],
    ),
    Entity(
        "Trueshot",
        [
            SpellAliasComponent([(TreeType.BEGINS_TO_PERFORM_LINE, "Trueshot")]),
            ClassDetectionComponent(
                PlayerClass.HUNTER,
                triggered_by=[(TreeType.BEGINS_TO_PERFORM_LINE, "Trueshot")],
            ),
        ],
    ),
    Entity(
        "Chain Heal",
        [
            ClassDetectionComponent(
                PlayerClass.SHAMAN,
                triggered_by=[(TreeType.BEGINS_TO_CAST_LINE, "Chain Heal")],
            ),
        ],
    ),
    Entity(
        "Lesser Healing Wave",
        [
            ClassDetectionComponent(
                PlayerClass.SHAMAN,
                triggered_by=[(TreeType.BEGINS_TO_CAST_LINE, "Lesser Healing Wave")],
            ),
        ],
    ),
    Entity(
        "Shield Block",
        [TrackSpellCastComponent(), SpellAliasComponent([(TreeType.GAINS_LINE, "Shield Block")])],
    ),
    Entity(
        "Berserker Rage",
        [TrackSpellCastComponent(), SpellAliasComponent([(TreeType.GAINS_LINE, "Berserker Rage")])],
    ),
]


def get_trinket_rename_map():
    rename_map = {}
    for entity, trinket_comp in get_entities_with_component(TrinketComponent):
        for spell_name in trinket_comp.triggered_by_spells:
            if spell_name != entity.name:
                rename_map[spell_name] = entity.name
    return rename_map


TRINKET_RENAME = get_trinket_rename_map()
