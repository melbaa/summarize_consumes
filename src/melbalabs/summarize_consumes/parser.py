from __future__ import annotations

import dataclasses
import enum
import re
from typing import Literal
from typing import Optional
from typing import Union

type PlayerName = str
type PetName = str
type RawSpellName = str
type RawStackCount = str  # will be converted to int when needed

invalid_player_name: PlayerName = "invalid_player_name_1234567890"
invalid_raw_spell_name: RawSpellName = "invalid_raw_spell_name_1234567890"
invalid_stackcount: RawStackCount = "invalid_stackcount_1234567890"


class Token:
    __slots__ = ("type", "value")

    def __init__(self, type_name, value) -> None:
        self.type = type_name
        self.value = value

    def __str__(self):
        return self.value

    def __int__(self) -> int:
        return int(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type!r}, {self.value!r})"


@enum.verify(enum.UNIQUE)
class TreeType(enum.Enum):
    TIMESTAMP = "timestamp"
    LINE = "line"
    GAINS_MANA_LINE = "gains_mana_line"
    HITS_ABILITY_LINE = "hits_ability_line"
    HITS_AUTOATTACK_LINE = "hits_autoattack_line"
    GAINS_LINE = "gains_line"
    HEALS_LINE = "heals_line"
    FADES_LINE = "fades_line"
    SUFFERS_LINE_SOURCE = "suffers_line_source"
    SUFFERS_LINE_NOSOURCE = "suffers_line_nosource"
    BEGINS_TO_CAST_LINE = "begins_to_cast_line"
    AFFLICTED_LINE = "afflicted_line"
    BLOCK_LINE = "block_line"
    CONSOLIDATED_PET = "consolidated_pet"
    CASTS_LINE = "casts_line"
    GAINS_EXTRA_ATTACKS_LINE = "gains_extra_attacks_line"
    GAINS_RAGE_LINE = "gains_rage_line"
    GAINS_HEALTH_LINE = "gains_health_line"
    GAINS_ENERGY_LINE = "gains_energy_line"
    RESIST_LINE = "resist_line"
    USES_LINE = "uses_line"
    DODGES_LINE = "dodges_line"
    MISSES_ABILITY_LINE = "misses_ability_line"
    MISSES_LINE = "misses_line"
    DIES_LINE = "dies_line"
    PARRY_LINE = "parry_line"
    REFLECTS_DAMAGE_LINE = "reflects_damage_line"
    BEGINS_TO_PERFORM_LINE = "begins_to_perform_line"
    DODGE_ABILITY_LINE = "dodge_ability_line"
    CAUSES_DAMAGE_LINE = "causes_damage_line"
    REMOVED_LINE = "removed_line"
    IMMUNE_ABILITY_LINE = "immune_ability_line"
    PARRY_ABILITY_LINE = "parry_ability_line"
    IMMUNE_LINE = "immune_line"
    PERFORMS_ON_LINE = "performs_on_line"
    PERFORMS_LINE = "performs_line"
    FALLS_LINE = "falls_line"
    IS_IMMUNE_ABILITY_LINE = "is_immune_ability_line"
    WAS_EVADED_LINE = "was_evaded_line"
    CONSOLIDATED_LINE = "consolidated_line"
    IS_ABSORBED_ABILITY_LINE = "is_absorbed_ability_line"
    ABSORBS_ABILITY_LINE = "absorbs_ability_line"
    SLAIN_LINE = "slain_line"
    CREATES_LINE = "creates_line"
    IS_KILLED_LINE = "is_killed_line"
    IS_DESTROYED_LINE = "is_destroyed_line"
    IS_REFLECTED_BACK_LINE = "is_reflected_back_line"
    COMBATANT_INFO_LINE = "combatant_info_line"
    NONE_LINE = "none_line"
    FAILS_TO_DISPEL_LINE = "fails_to_dispel_line"
    LAVA_LINE = "lava_line"
    SLAYS_LINE = "slays_line"
    PET_BEGINS_EATING_LINE = "pet_begins_eating_line"
    EQUIPPED_DURABILITY_LOSS_LINE = "equipped_durability_loss_line"
    BLOCK_ABILITY_LINE = "block_ability_line"
    ABSORBS_ALL_LINE = "absorbs_all_line"
    GAINS_HAPPINESS_LINE = "gains_happiness_line"
    IS_DISMISSED_LINE = "is_dismissed_line"
    DRAINS_MANA_LINE = "drains_mana_line"
    INTERRUPTS_LINE = "interrupts_line"
    # IS_DISMISSED_LINE2 = "is_dismissed_line2"
    # DRAINS_MANA_LINE2 = "drains_mana_line2"


@enum.verify(enum.UNIQUE)
class ActionValue(enum.Enum):
    HITS = "hits"
    CRITS = "crits"
    BLOCK = "block"
    GLANCE = "glance"


@dataclasses.dataclass
class GainsLineTree:
    data: Literal[TreeType.GAINS_LINE]
    name: PlayerName
    spellname: RawSpellName
    stackcount: RawStackCount


@dataclasses.dataclass
class GainsManaLineTree:
    data: Literal[TreeType.GAINS_MANA_LINE]
    name: PlayerName
    mana: str
    spellname: RawSpellName


@dataclasses.dataclass
class HitsAbilityLineTree:
    data: Literal[TreeType.HITS_ABILITY_LINE]
    name: PlayerName
    spellname: RawSpellName
    targetname: PlayerName
    damage: str
    spell_damage_type: str


@dataclasses.dataclass
class HitsAutoattackLineTree:
    data: Literal[TreeType.HITS_AUTOATTACK_LINE]
    name: PlayerName
    targetname: PlayerName
    damage: str
    action: ActionValue


@dataclasses.dataclass
class HealsLineTree:
    data: Literal[TreeType.HEALS_LINE]
    name: PlayerName
    spellname: RawSpellName
    heal_crit: str
    targetname: PlayerName
    heal_amount: str


@dataclasses.dataclass
class FadesLineTree:
    data: Literal[TreeType.FADES_LINE]
    spellname: RawSpellName
    targetname: PlayerName


@dataclasses.dataclass
class SuffersLineSourceTree:
    data: Literal[TreeType.SUFFERS_LINE_SOURCE]
    targetname: PlayerName
    damage: str
    spell_damage_type: str
    castername: PlayerName
    spellname: RawSpellName


@dataclasses.dataclass
class SuffersLineNosourceTree:
    data: Literal[TreeType.SUFFERS_LINE_NOSOURCE]
    targetname: PlayerName
    damage: str
    spell_damage_type: str


@dataclasses.dataclass
class BeginsToCastLineTree:
    data: Literal[TreeType.BEGINS_TO_CAST_LINE]
    name: PlayerName
    spellname: RawSpellName


@dataclasses.dataclass
class GainsHappinessLineTree:
    data: Literal[TreeType.GAINS_HAPPINESS_LINE]
    petname: str
    amount: str
    owner_name: str


@dataclasses.dataclass
class GainsHealthLineTree:
    data: Literal[TreeType.GAINS_HEALTH_LINE]
    targetname: str
    amount: str
    source: str
    spellname: str


@dataclasses.dataclass
class GainsRageLineTree:
    data: Literal[TreeType.GAINS_RAGE_LINE]
    name: str
    amount: str
    source: str
    spellname: str


@dataclasses.dataclass
class FailsToDispelLineTree:
    data: Literal[TreeType.FAILS_TO_DISPEL_LINE]


@dataclasses.dataclass
class ParryLineTree:
    data: Literal[TreeType.PARRY_LINE]
    attacker: str
    parrier: str


@dataclasses.dataclass
class IsDestroyedLineTree:
    data: Literal[TreeType.IS_DESTROYED_LINE]
    entity_name: str


@dataclasses.dataclass
class SlainLineTree:
    data: Literal[TreeType.SLAIN_LINE]
    victim: str
    slayer: str


@dataclasses.dataclass
class IsDismissedLineTree:
    data: Literal[TreeType.IS_DISMISSED_LINE]
    owner_name: str
    pet_name: str


@dataclasses.dataclass
class AbsorbsAllLineTree:
    data: Literal[TreeType.ABSORBS_ALL_LINE]
    attacker: str
    absorber: str


@dataclasses.dataclass
class InterruptsLineTree:
    data: Literal[TreeType.INTERRUPTS_LINE]
    interrupter: str
    targetname: str
    spellname: str


@dataclasses.dataclass
class EquippedDurabilityLossLineTree:
    data: Literal[TreeType.EQUIPPED_DURABILITY_LOSS_LINE]


@dataclasses.dataclass
class PetBeginsEatingLineTree:
    data: Literal[TreeType.PET_BEGINS_EATING_LINE]


@dataclasses.dataclass
class SlaysLineTree:
    data: Literal[TreeType.SLAYS_LINE]


@dataclasses.dataclass
class LavaLineTree:
    data: Literal[TreeType.LAVA_LINE]


@dataclasses.dataclass
class NoneLineTree:
    data: Literal[TreeType.NONE_LINE]


@dataclasses.dataclass
class CombatantInfoLineTree:
    data: Literal[TreeType.COMBATANT_INFO_LINE]


@dataclasses.dataclass
class IsReflectedBackLineTree:
    data: Literal[TreeType.IS_REFLECTED_BACK_LINE]
    caster: str
    spellname: str
    reflector: str


@dataclasses.dataclass
class IsKilledLineTree:
    data: Literal[TreeType.IS_KILLED_LINE]
    victim: str
    killer: str


@dataclasses.dataclass
class IsAbsorbedAbilityLineTree:
    data: Literal[TreeType.IS_ABSORBED_ABILITY_LINE]
    caster: str
    spellname: str
    target: str


@dataclasses.dataclass
class FallsLineTree:
    data: Literal[TreeType.FALLS_LINE]
    name: str
    amount: str


@dataclasses.dataclass
class PerformsOnLineTree:
    data: Literal[TreeType.PERFORMS_ON_LINE]
    performer: str
    spellname: str
    targetname: str


@dataclasses.dataclass
class PerformsLineTree:
    data: Literal[TreeType.PERFORMS_LINE]
    performer: str
    spellname: str


@dataclasses.dataclass
class ParryAbilityLineTree:
    data: Literal[TreeType.PARRY_ABILITY_LINE]
    caster: str
    spellname: str
    target: str


@dataclasses.dataclass
class ImmuneLineTree:
    data: Literal[TreeType.IMMUNE_LINE]
    attacker: str
    target: str


@dataclasses.dataclass
class ImmuneAbilityLineTree:
    data: Literal[TreeType.IMMUNE_ABILITY_LINE]
    caster: str
    spellname: str
    target: str


@dataclasses.dataclass
class IsImmuneAbilityLineTree:
    data: Literal[TreeType.IS_IMMUNE_ABILITY_LINE]
    targetname: str
    caster: str
    spellname: str


@dataclasses.dataclass
class RemovedLineTree:
    data: Literal[TreeType.REMOVED_LINE]
    name: str
    spellname: str


@dataclasses.dataclass
class CausesDamageLineTree:
    data: Literal[TreeType.CAUSES_DAMAGE_LINE]
    caster: str
    spellname: str
    target: str
    amount: str


@dataclasses.dataclass
class DodgeAbilityLineTree:
    data: Literal[TreeType.DODGE_ABILITY_LINE]
    caster: str
    spellname: str
    target: str


@dataclasses.dataclass
class BeginsToPerformLineTree:
    data: Literal[TreeType.BEGINS_TO_PERFORM_LINE]
    name: str
    spellname: str


@dataclasses.dataclass
class DiesLineTree:
    data: Literal[TreeType.DIES_LINE]
    name: str


@dataclasses.dataclass
class MissesAbilityLineTree:
    data: Literal[TreeType.MISSES_ABILITY_LINE]
    caster: str
    spellname: str
    target: str


@dataclasses.dataclass
class MissesLineTree:
    data: Literal[TreeType.MISSES_LINE]
    attacker: str
    target: str


@dataclasses.dataclass
class DodgesLineTree:
    data: Literal[TreeType.DODGES_LINE]
    attacker: str
    dodger: str


@dataclasses.dataclass
class UsesLineTree:
    data: Literal[TreeType.USES_LINE]
    name: str
    item: str
    target: str | None


@dataclasses.dataclass
class ResistLineTree:
    data: Literal[TreeType.RESIST_LINE]
    caster: str
    spellname: str
    target: str


@dataclasses.dataclass
class BlockAbilityLineTree:
    data: Literal[TreeType.BLOCK_ABILITY_LINE]
    caster: str
    spellname: str
    blocker: str


@dataclasses.dataclass
class CreatesLineTree:
    data: Literal[TreeType.CREATES_LINE]
    creator: str
    item: str


@dataclasses.dataclass
class AbsorbsAbilityLineTree:
    data: Literal[TreeType.ABSORBS_ABILITY_LINE]
    absorber: str
    caster: str
    spellname: str


@dataclasses.dataclass
class GainsEnergyLineTree:
    data: Literal[TreeType.GAINS_ENERGY_LINE]
    recipient: str
    amount: str
    caster: str
    spellname: str


@dataclasses.dataclass
class WasEvadedLineTree:
    data: Literal[TreeType.WAS_EVADED_LINE]
    name: str
    spellname: str
    targetname: str


@dataclasses.dataclass
class ReflectsDamageLineTree:
    data: Literal[TreeType.REFLECTS_DAMAGE_LINE]
    reflector: str
    amount: str
    damage_type: str
    target: str


@dataclasses.dataclass
class CastsLineTree:
    data: Literal[TreeType.CASTS_LINE]
    name: PlayerName
    spellname: RawSpellName
    targetname: PlayerName | None


@dataclasses.dataclass
class DrainsManaLineTree:
    data: Literal[TreeType.DRAINS_MANA_LINE]
    caster: PlayerName
    spellname: RawSpellName
    mana: str
    targetname: PlayerName
    gains: str


@dataclasses.dataclass
class GainsExtraAttacksLineTree:
    data: Literal[TreeType.GAINS_EXTRA_ATTACKS_LINE]
    name: PlayerName
    howmany: RawStackCount
    source: RawSpellName


@dataclasses.dataclass
class AfflictedLineTree:
    data: Literal[TreeType.AFFLICTED_LINE]
    targetname: PlayerName
    spellname: RawSpellName


@dataclasses.dataclass
class BlockLineTree:
    data: Literal[TreeType.BLOCK_LINE]
    name: PlayerName
    targetname: PlayerName


@dataclasses.dataclass
class ConsolidatedPetTree:
    data: Literal[TreeType.CONSOLIDATED_PET]
    name: PlayerName
    petname: PetName


@dataclasses.dataclass
class ConsolidatedLineTree:
    data: Literal[TreeType.CONSOLIDATED_LINE]
    children: list[ConsolidatedPetTree] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class TimestampTree:
    data: Literal[TreeType.TIMESTAMP]
    month: str
    day: str
    hour: str
    minute: str
    sec: str
    ms: str


@dataclasses.dataclass
class LineTree:
    data: Literal[TreeType.LINE]
    timestamp: TimestampTree
    subtree: Union[
        GainsLineTree,
        GainsManaLineTree,
        GainsHealthLineTree,
        HealsLineTree,
        FadesLineTree,
        GainsHappinessLineTree,
        SuffersLineSourceTree,
        SuffersLineNosourceTree,
        BeginsToCastLineTree,
        AfflictedLineTree,
        BlockLineTree,
        CastsLineTree,
        GainsRageLineTree,
        GainsExtraAttacksLineTree,
        ParryLineTree,
        ReflectsDamageLineTree,
        IsDestroyedLineTree,
        DrainsManaLineTree,
        WasEvadedLineTree,
        SlainLineTree,
        GainsEnergyLineTree,
        AbsorbsAbilityLineTree,
        CreatesLineTree,
        BlockAbilityLineTree,
        ResistLineTree,
        UsesLineTree,
        ConsolidatedLineTree,
        DodgesLineTree,
        MissesAbilityLineTree,
        MissesLineTree,
        DiesLineTree,
        BeginsToPerformLineTree,
        DodgeAbilityLineTree,
        CausesDamageLineTree,
        RemovedLineTree,
        ImmuneAbilityLineTree,
        ImmuneLineTree,
        IsImmuneAbilityLineTree,
        ParryAbilityLineTree,
        PerformsOnLineTree,
        PerformsLineTree,
        FallsLineTree,
        IsAbsorbedAbilityLineTree,
        IsKilledLineTree,
        IsReflectedBackLineTree,
        CombatantInfoLineTree,
        NoneLineTree,
        LavaLineTree,
        SlaysLineTree,
        PetBeginsEatingLineTree,
        EquippedDurabilityLossLineTree,
        InterruptsLineTree,
        AbsorbsAllLineTree,
        IsDismissedLineTree,
        FailsToDispelLineTree,
        HitsAbilityLineTree,
        HitsAutoattackLineTree,
    ]


class Parser2:
    def __init__(self, unparsed_logger):
        self.unparsed_logger = unparsed_logger

        # The regex already ensures these are digits, so the isdigit() loop is no longer needed.
        self.TIMESTAMP_PATTERN = re.compile(r"(\d+)/(\d+) (\d+):(\d+):(\d+)\.(\d+)")

        self.timestamp_tree = TimestampTree(
            data=TreeType.TIMESTAMP,
            month="",
            day="",
            hour="",
            minute="",
            sec="",
            ms="",
        )

        # gains_mana_line cache
        self.subtree_gains_mana_line = GainsManaLineTree(
            data=TreeType.GAINS_MANA_LINE,
            name=invalid_player_name,
            mana=invalid_stackcount,
            spellname=invalid_raw_spell_name,
        )
        self.gains_mana_line_tree = LineTree(
            data=TreeType.LINE, timestamp=self.timestamp_tree, subtree=self.subtree_gains_mana_line
        )

        # gains_happiness_line cache
        self.subtree_gains_happiness_line = GainsHappinessLineTree(
            data=TreeType.GAINS_HAPPINESS_LINE,
            petname=invalid_player_name,
            amount=invalid_stackcount,
            owner_name=invalid_player_name,
        )
        self.gains_happiness_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_gains_happiness_line,
        )

        # hits_ability_line cache
        self.subtree_hits_ability_line = HitsAbilityLineTree(
            data=TreeType.HITS_ABILITY_LINE,
            name=invalid_player_name,
            spellname=invalid_raw_spell_name,
            targetname=invalid_player_name,
            damage=invalid_stackcount,
            spell_damage_type=invalid_raw_spell_name,
        )
        self.hits_ability_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_hits_ability_line,
        )

        # hits_autoattack_line cache
        self.subtree_hits_autoattack_line = HitsAutoattackLineTree(
            data=TreeType.HITS_AUTOATTACK_LINE,
            name=invalid_player_name,
            targetname=invalid_player_name,
            damage=invalid_stackcount,
            action=ActionValue.HITS,
        )
        self.hits_autoattack_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_hits_autoattack_line,
        )

        # gains_line cache

        self.subtree_gains_line = GainsLineTree(
            data=TreeType.GAINS_LINE,
            name=invalid_player_name,
            spellname=invalid_raw_spell_name,
            stackcount=invalid_stackcount,
        )
        self.gains_line_tree = LineTree(
            data=TreeType.LINE, timestamp=self.timestamp_tree, subtree=self.subtree_gains_line
        )

        # heals_line cache
        self.subtree_heals_line = HealsLineTree(
            data=TreeType.HEALS_LINE,
            name=invalid_player_name,
            spellname=invalid_raw_spell_name,
            heal_crit="",
            targetname=invalid_player_name,
            heal_amount=invalid_stackcount,
        )
        self.heals_line_tree = LineTree(
            data=TreeType.LINE, timestamp=self.timestamp_tree, subtree=self.subtree_heals_line
        )

        # fades_line cache
        self.subtree_fades_line = FadesLineTree(
            data=TreeType.FADES_LINE,
            spellname=invalid_raw_spell_name,
            targetname=invalid_player_name,
        )
        self.fades_line_tree = LineTree(
            data=TreeType.LINE, timestamp=self.timestamp_tree, subtree=self.subtree_fades_line
        )

        # suffers_line cache (WITH source)
        self.subtree_suffers_line_source = SuffersLineSourceTree(
            data=TreeType.SUFFERS_LINE_SOURCE,
            targetname=invalid_player_name,
            damage=invalid_stackcount,
            spell_damage_type=invalid_raw_spell_name,
            castername=invalid_player_name,
            spellname=invalid_raw_spell_name,
        )
        self.suffers_line_source_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_suffers_line_source,
        )

        # suffers_line cache (NO source)
        self.subtree_suffers_line_nosource = SuffersLineNosourceTree(
            data=TreeType.SUFFERS_LINE_NOSOURCE,
            targetname=invalid_player_name,
            damage=invalid_stackcount,
            spell_damage_type=invalid_raw_spell_name,
        )
        self.suffers_line_nosource_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_suffers_line_nosource,
        )

        # begins_to_cast_line cache
        self.subtree_begins_to_cast_line = BeginsToCastLineTree(
            data=TreeType.BEGINS_TO_CAST_LINE,
            name=invalid_player_name,
            spellname=invalid_raw_spell_name,
        )
        self.begins_to_cast_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_begins_to_cast_line,
        )

        # afflicted_line cache
        self.subtree_afflicted_line = AfflictedLineTree(
            data=TreeType.AFFLICTED_LINE,
            targetname=invalid_player_name,
            spellname=invalid_raw_spell_name,
        )
        self.afflicted_line_tree = LineTree(
            data=TreeType.LINE, timestamp=self.timestamp_tree, subtree=self.subtree_afflicted_line
        )

        # block_line cache
        self.subtree_block_line = BlockLineTree(
            data=TreeType.BLOCK_LINE,
            name=invalid_player_name,
            targetname=invalid_player_name,
        )
        self.block_line_tree = LineTree(
            data=TreeType.LINE, timestamp=self.timestamp_tree, subtree=self.subtree_block_line
        )

        # casts_line cache
        self.subtree_casts_line = CastsLineTree(
            data=TreeType.CASTS_LINE,
            name=invalid_player_name,
            spellname=invalid_raw_spell_name,
            targetname=None,
        )
        self.casts_line_tree = LineTree(
            data=TreeType.LINE, timestamp=self.timestamp_tree, subtree=self.subtree_casts_line
        )

        # gains_rage_line cache
        self.subtree_gains_rage_line = GainsRageLineTree(
            data=TreeType.GAINS_RAGE_LINE,
            name=invalid_player_name,
            amount=invalid_stackcount,
            source=invalid_player_name,
            spellname=invalid_raw_spell_name,
        )
        self.gains_rage_line_tree = LineTree(
            data=TreeType.LINE, timestamp=self.timestamp_tree, subtree=self.subtree_gains_rage_line
        )

        # gains_extra_attacks_line cache
        self.subtree_gains_extra_attacks_line = GainsExtraAttacksLineTree(
            data=TreeType.GAINS_EXTRA_ATTACKS_LINE,
            name=invalid_player_name,
            howmany=invalid_stackcount,
            source=invalid_raw_spell_name,
        )
        self.gains_extra_attacks_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_gains_extra_attacks_line,
        )

        # parry_line cache
        self.subtree_parry_line = ParryLineTree(
            data=TreeType.PARRY_LINE, attacker=invalid_player_name, parrier=invalid_player_name
        )
        self.parry_line_tree = LineTree(
            data=TreeType.LINE, timestamp=self.timestamp_tree, subtree=self.subtree_parry_line
        )

        # fails_to_dispel_line cache
        self.subtree_fails_to_dispel_line = FailsToDispelLineTree(
            data=TreeType.FAILS_TO_DISPEL_LINE
        )
        self.fails_to_dispel_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_fails_to_dispel_line,
        )

        # reflects_damage_line cache
        self.subtree_reflects_damage_line = ReflectsDamageLineTree(
            data=TreeType.REFLECTS_DAMAGE_LINE,
            reflector=invalid_player_name,
            amount=invalid_stackcount,
            damage_type=invalid_raw_spell_name,
            target=invalid_player_name,
        )
        self.reflects_damage_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_reflects_damage_line,
        )

        # is_destroyed_line cache
        self.subtree_is_destroyed_line = IsDestroyedLineTree(
            data=TreeType.IS_DESTROYED_LINE,
            entity_name=invalid_player_name,
        )
        self.is_destroyed_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_is_destroyed_line,
        )

        # was_evaded_line cache
        self.subtree_was_evaded_line = WasEvadedLineTree(
            data=TreeType.WAS_EVADED_LINE,
            name=invalid_player_name,
            spellname=invalid_raw_spell_name,
            targetname=invalid_player_name,
        )
        self.was_evaded_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_was_evaded_line,
        )

        # slain_line cache
        self.subtree_slain_line = SlainLineTree(
            data=TreeType.SLAIN_LINE,
            victim=invalid_player_name,
            slayer=invalid_player_name,
        )
        self.slain_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_slain_line,
        )

        # gains_energy_line cache
        self.subtree_gains_energy_line = GainsEnergyLineTree(
            data=TreeType.GAINS_ENERGY_LINE,
            recipient=invalid_player_name,
            amount=invalid_stackcount,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
        )
        self.gains_energy_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_gains_energy_line,
        )

        # absorbs_ability_line cache
        self.subtree_absorbs_ability_line = AbsorbsAbilityLineTree(
            data=TreeType.ABSORBS_ABILITY_LINE,
            absorber=invalid_player_name,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
        )
        self.absorbs_ability_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_absorbs_ability_line,
        )

        # creates_line cache
        self.subtree_creates_line = CreatesLineTree(
            data=TreeType.CREATES_LINE,
            creator=invalid_player_name,
            item=invalid_raw_spell_name,
        )
        self.creates_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_creates_line,
        )

        # block_ability_line cache
        self.subtree_block_ability_line = BlockAbilityLineTree(
            data=TreeType.BLOCK_ABILITY_LINE,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
            blocker=invalid_player_name,
        )
        self.block_ability_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_block_ability_line,
        )

        # resist_line cache
        self.subtree_resist_line = ResistLineTree(
            data=TreeType.RESIST_LINE,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
            target=invalid_player_name,
        )
        self.resist_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_resist_line,
        )

        # uses_line cache
        self.subtree_uses_line = UsesLineTree(
            data=TreeType.USES_LINE,
            name=invalid_player_name,
            item=invalid_raw_spell_name,
            target=None,
        )
        self.uses_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_uses_line,
        )

        # dodges_line cache
        self.subtree_dodges_line = DodgesLineTree(
            data=TreeType.DODGES_LINE,
            attacker=invalid_player_name,
            dodger=invalid_player_name,
        )
        self.dodges_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_dodges_line,
        )

        # misses_ability_line cache
        self.subtree_misses_ability_line = MissesAbilityLineTree(
            data=TreeType.MISSES_ABILITY_LINE,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
            target=invalid_player_name,
        )
        self.misses_ability_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_misses_ability_line,
        )

        # misses_line cache
        self.subtree_misses_line = MissesLineTree(
            data=TreeType.MISSES_LINE,
            attacker=invalid_player_name,
            target=invalid_player_name,
        )
        self.misses_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_misses_line,
        )

        # dies_line cache
        self.subtree_dies_line = DiesLineTree(
            data=TreeType.DIES_LINE,
            name=invalid_player_name,
        )
        self.dies_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_dies_line,
        )

        # begins_to_perform_line cache
        self.subtree_begins_to_perform_line = BeginsToPerformLineTree(
            data=TreeType.BEGINS_TO_PERFORM_LINE,
            name=invalid_player_name,
            spellname=invalid_raw_spell_name,
        )
        self.begins_to_perform_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_begins_to_perform_line,
        )

        # dodge_ability_line cache
        self.subtree_dodge_ability_line = DodgeAbilityLineTree(
            data=TreeType.DODGE_ABILITY_LINE,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
            target=invalid_player_name,
        )
        self.dodge_ability_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_dodge_ability_line,
        )

        # causes_damage_line cache
        self.subtree_causes_damage_line = CausesDamageLineTree(
            data=TreeType.CAUSES_DAMAGE_LINE,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
            target=invalid_player_name,
            amount=invalid_stackcount,
        )
        self.causes_damage_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_causes_damage_line,
        )

        # removed_line cache
        self.subtree_removed_line = RemovedLineTree(
            data=TreeType.REMOVED_LINE,
            name=invalid_player_name,
            spellname=invalid_raw_spell_name,
        )
        self.removed_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_removed_line,
        )

        # immune_ability_line cache
        self.subtree_immune_ability_line = ImmuneAbilityLineTree(
            data=TreeType.IMMUNE_ABILITY_LINE,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
            target=invalid_player_name,
        )
        self.immune_ability_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_immune_ability_line,
        )

        # immune_line cache
        self.subtree_immune_line = ImmuneLineTree(
            data=TreeType.IMMUNE_LINE,
            attacker=invalid_player_name,
            target=invalid_player_name,
        )
        self.immune_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_immune_line,
        )

        # is_immune_ability_line cache
        self.subtree_is_immune_ability_line = IsImmuneAbilityLineTree(
            data=TreeType.IS_IMMUNE_ABILITY_LINE,
            targetname=invalid_player_name,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
        )
        self.is_immune_ability_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_is_immune_ability_line,
        )

        # parry_ability_line cache
        self.subtree_parry_ability_line = ParryAbilityLineTree(
            data=TreeType.PARRY_ABILITY_LINE,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
            target=invalid_player_name,
        )
        self.parry_ability_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_parry_ability_line,
        )

        # performs_on_line cache
        self.subtree_performs_on_line = PerformsOnLineTree(
            data=TreeType.PERFORMS_ON_LINE,
            performer=invalid_player_name,
            spellname=invalid_raw_spell_name,
            targetname=invalid_player_name,
        )
        self.performs_on_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_performs_on_line,
        )

        # performs_line cache
        self.subtree_performs_line = PerformsLineTree(
            data=TreeType.PERFORMS_LINE,
            performer=invalid_player_name,
            spellname=invalid_raw_spell_name,
        )
        self.performs_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_performs_line,
        )

        # falls_line cache
        self.subtree_falls_line = FallsLineTree(
            data=TreeType.FALLS_LINE,
            name=invalid_player_name,
            amount="0",
        )
        self.falls_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_falls_line,
        )

        # is_absorbed_ability_line cache
        self.subtree_is_absorbed_ability_line = IsAbsorbedAbilityLineTree(
            data=TreeType.IS_ABSORBED_ABILITY_LINE,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
            target=invalid_player_name,
        )
        self.is_absorbed_ability_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_is_absorbed_ability_line,
        )

        # is_killed_line cache
        self.subtree_is_killed_line = IsKilledLineTree(
            data=TreeType.IS_KILLED_LINE,
            victim=invalid_player_name,
            killer=invalid_player_name,
        )
        self.is_killed_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_is_killed_line,
        )

        # is_reflected_back_line cache
        self.subtree_is_reflected_back_line = IsReflectedBackLineTree(
            data=TreeType.IS_REFLECTED_BACK_LINE,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
            reflector=invalid_player_name,
        )
        self.is_reflected_back_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_is_reflected_back_line,
        )

        # combatant_info_line cache
        self.subtree_combatant_info_line = CombatantInfoLineTree(data=TreeType.COMBATANT_INFO_LINE)
        self.combatant_info_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_combatant_info_line,
        )

        # none_line cache
        self.subtree_none_line = NoneLineTree(data=TreeType.NONE_LINE)
        self.none_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_none_line,
        )

        # lava_line cache
        self.subtree_lava_line = LavaLineTree(data=TreeType.LAVA_LINE)
        self.lava_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_lava_line,
        )

        # slays_line cache
        self.subtree_slays_line = SlaysLineTree(data=TreeType.SLAYS_LINE)
        self.slays_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_slays_line,
        )

        # pet_begins_eating_line cache
        self.subtree_pet_begins_eating_line = PetBeginsEatingLineTree(
            data=TreeType.PET_BEGINS_EATING_LINE
        )
        self.pet_begins_eating_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_pet_begins_eating_line,
        )

        # equipped_durability_loss_line cache
        self.subtree_equipped_durability_loss_line = EquippedDurabilityLossLineTree(
            data=TreeType.EQUIPPED_DURABILITY_LOSS_LINE
        )
        self.equipped_durability_loss_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_equipped_durability_loss_line,
        )

        # interrupts_line cache
        self.subtree_interrupts_line = InterruptsLineTree(
            data=TreeType.INTERRUPTS_LINE,
            interrupter="",
            targetname="",
            spellname="",
        )
        self.interrupts_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_interrupts_line,
        )

        # absorbs_all_line cache
        self.subtree_absorbs_all_line = AbsorbsAllLineTree(
            data=TreeType.ABSORBS_ALL_LINE, attacker="", absorber=""
        )
        self.absorbs_all_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_absorbs_all_line,
        )

        # is_dismissed_line cache
        self.subtree_is_dismissed_line = IsDismissedLineTree(
            data=TreeType.IS_DISMISSED_LINE, owner_name="", pet_name=""
        )
        self.is_dismissed_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_is_dismissed_line,
        )

        # gains_health_line cache
        self.subtree_gains_health_line = GainsHealthLineTree(
            data=TreeType.GAINS_HEALTH_LINE,
            targetname=invalid_player_name,
            amount=invalid_stackcount,
            source=invalid_player_name,
            spellname=invalid_raw_spell_name,
        )
        self.gains_health_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_gains_health_line,
        )

        # drains_mana_line cache
        self.subtree_drains_mana_line = DrainsManaLineTree(
            data=TreeType.DRAINS_MANA_LINE,
            caster=invalid_player_name,
            spellname=invalid_raw_spell_name,
            mana=invalid_stackcount,
            targetname=invalid_player_name,
            gains=invalid_stackcount,
        )
        self.drains_mana_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_drains_mana_line,
        )

        # consolidated_line cache
        self.subtree_consolidated_line = ConsolidatedLineTree(
            data=TreeType.CONSOLIDATED_LINE,
            children=[],
        )
        self.consolidated_line_tree = LineTree(
            data=TreeType.LINE,
            timestamp=self.timestamp_tree,
            subtree=self.subtree_consolidated_line,
        )

    def parse_ts(self, line, p_ts_end):
        # 6/1 18:31:36.197  ...

        match = self.TIMESTAMP_PATTERN.match(line)

        if not match:
            raise ValueError("Invalid timestamp format")

        groups = match.groups()
        self.timestamp_tree.month = groups[0]
        self.timestamp_tree.day = groups[1]
        self.timestamp_tree.hour = groups[2]
        self.timestamp_tree.minute = groups[3]
        self.timestamp_tree.sec = groups[4]
        self.timestamp_tree.ms = groups[5]

        return self.timestamp_tree

    def parse_consolidated_pet(self, pet_string: str) -> Optional[ConsolidatedPetTree]:
        """Parses a single 'PET: ...' substring."""

        # We don't need the timestamp, so we find the first '&' to skip it.
        p_first_amp = pet_string.find("&")
        if p_first_amp == -1:
            return None

        # Now find the second '&' which separates the name from the pet name.
        p_second_amp = pet_string.find("&", p_first_amp + 1)
        if p_second_amp == -1:
            return None

        # Slice out the name and pet name.
        name = pet_string[p_first_amp + 1 : p_second_amp]
        petname = pet_string[p_second_amp + 1 :].strip()  # strip() for safety

        # Return the subtree for this pet entry.
        return ConsolidatedPetTree(data=TreeType.CONSOLIDATED_PET, name=name, petname=petname)

    def parse(self, line: str, p_ts_end) -> Optional[LineTree]:
        """
        assumes p_ts_end != -1
        throws ValueError when it sees unexpected syntax
        return None when it's not one of the expected line types
        """
        try:
            p_mana_from = line.find(" Mana from ", p_ts_end)
            if p_mana_from >= 0:
                # 6/1 18:38:06.514  Oileri gains 39 Mana from Interlani 's Greater Blessing of Wisdom.
                # 6/1 18:31:36.197  Chogup (Freedlock) gains 10 Mana from Clapya 's Mana Spring.

                # Find the start of the constant text ' gains '
                p_gains = line.find(" gains ", p_ts_end)

                if p_gains >= 0 and p_gains < p_mana_from:
                    # The recipient's name is everything between the double space and ' gains '
                    # p_ts_end + 2 skips the double space itself.
                    name = line[p_ts_end + 2 : p_gains]

                    # Find the remaining anchors, starting the search from where we left off.
                    p_s = line.find(" 's ", p_mana_from)

                    # Slice the data out from between the anchors
                    # len(' gains ') == 7
                    mana = line[p_gains + 7 : p_mana_from]

                    # len(' Mana from ') == 11
                    # castername = line[p_mana_from + 11 : p_s]  # don't need this currently

                    # len(" 's ") == 4. The -2 strips the final period '.\n'
                    spellname_gains_mana = line[p_s + 4 : -2]

                    _ = self.parse_ts(line, p_ts_end)  # magic cached reference

                    self.subtree_gains_mana_line.name = name  # magic cached reference
                    self.subtree_gains_mana_line.mana = mana  # magic cached reference
                    self.subtree_gains_mana_line.spellname = (
                        spellname_gains_mana  # magic cached reference
                    )
                    return self.gains_mana_line_tree  # magic cached reference

            # It has already been determined NOT to be a 'Mana from' event.
            # we'll look for an attack or ability line

            # 6/1 18:32:22.922  Doelfinest 's Exorcism crits Bile Retcher for 1433 Holy damage.
            # 6/1 18:32:52.900  Minoas 's Auto Attack (pet) hits Patchwork Golem for 105. (glancing)
            # 6/1 19:05:23.441  Interlani hits Patchwerk for 120.
            # 6/1 18:32:52.900  Jinp hits Patchwork Golem for 156. (glancing)
            # 2/21 21:20:32.779  Psykhe hits Flamewaker Elite for 333. (glancing) (+15 vulnerability bonus)

            # Find the action word, starting the search after the timestamp.
            action_verb = "hits"
            p_action = line.find(" hits ", p_ts_end)

            if p_action == -1:
                action_verb = "crits"
                p_action = line.find(" crits ", p_ts_end)

            # If no action, or not followed by ' for ', it's not a damage line.
            p_for = line.find(" for ", p_action)
            if p_action >= 0 and p_for >= 0:
                _ = self.parse_ts(line, p_ts_end)
                p_num_start = p_for + 5

                p_space = line.find(" ", p_num_start)
                p_period = line.find(".", p_num_start)

                # Determine the end of the number by finding the EARLIEST delimiter.
                if p_space != -1 and p_period != -1:
                    # Both delimiters were found, so choose the one that comes first.
                    p_num_end = min(p_space, p_period)
                elif p_space != -1:
                    # Only a space was found, so that's our endpoint.
                    p_num_end = p_space
                else:
                    # Only a period was found
                    p_num_end = p_period

                damage_amount = line[p_num_start:p_num_end]
                if not damage_amount.isdigit():
                    raise ValueError("invalid number?")

                damage_type_str = ""
                # there's text after the damage_amount and it's not in parens
                if p_space != -1:
                    # According to the grammar, the type must be followed by " damage".
                    # We find the start of that phrase to define the end of our type word.
                    p_damage_word = line.find(" damage", p_space)

                    # If the phrase " damage" was found right after a word...
                    if p_damage_word != -1:
                        # ...then the damage type is the slice between the first space and " damage".
                        damage_type_str = line[p_space + 1 : p_damage_word]

                # having a " 's " between the timestamp and action means it's an ability
                p_s = line.find(" 's ", p_ts_end, p_action)
                if p_s != -1:  # It's a hits_ability_line
                    name = line[p_ts_end + 2 : p_s]
                    spellname_hits_ability = line[p_s + 4 : p_action]
                    targetname_hits_ability = line[p_action + len(action_verb) + 2 : p_for]

                    self.subtree_hits_ability_line.name = name  # magic cached reference
                    self.subtree_hits_ability_line.spellname = (
                        spellname_hits_ability  # magic cached reference
                    )
                    self.subtree_hits_ability_line.targetname = (
                        targetname_hits_ability  # magic cached reference
                    )
                    self.subtree_hits_ability_line.damage = damage_amount  # magic cached reference
                    self.subtree_hits_ability_line.spell_damage_type = (
                        damage_type_str  # magic cached reference
                    )
                    return self.hits_ability_line_tree  # magic cached reference

                else:  # It's a hits_autoattack_line
                    # 2/9 21:47:33.736  Flamewaker Elite hits Supal for 399. (146 blocked)

                    if line.find("blocked)", p_num_end) != -1:
                        action_value = ActionValue.BLOCK
                    elif line.find("(glancing)", p_num_end) != -1:
                        action_value = ActionValue.GLANCE
                    else:
                        action_value = ActionValue(action_verb)

                    caster_name = line[p_ts_end + 2 : p_action]
                    targetname_hits_autoattack = line[p_action + len(action_verb) + 2 : p_for]

                    self.subtree_hits_autoattack_line.name = caster_name  # magic cached reference
                    self.subtree_hits_autoattack_line.targetname = (
                        targetname_hits_autoattack  # magic cached reference
                    )
                    self.subtree_hits_autoattack_line.damage = (
                        damage_amount  # magic cached reference
                    )
                    self.subtree_hits_autoattack_line.action = (
                        action_value  # magic cached reference
                    )
                    return self.hits_autoattack_line_tree  # magic cached reference

            # 12/13 14:20:41.781  BudwiserHL 's Holy Light heals Pitbound for 2166.
            # 12/14 01:27:54.282  NimpheraFH 's Flash Heal heals Didja for 1074.
            # 12/14 01:28:58.237  NimpheraGH 's Greater Heal critically heals Didja for 3525.
            # 12/14 01:28:02.673  NimpheraPH 's Prayer of Healing critically heals Krrom for 1564.
            # 12/14 01:28:02.673  NimpheraH 's Heal critically heals Krrom for 1564.

            crit_token_value = "critically"
            action_verb = " critically heals "
            p_action = line.find(action_verb, p_ts_end)

            if p_action == -1:
                crit_token_value = ""
                action_verb = " heals "
                p_action = line.find(action_verb, p_ts_end)

            # We also need 's before the action and ' for ' after it.
            p_s = line.find(" 's ", p_ts_end, p_action)
            p_for = line.find(" for ", p_action)

            # If all our required anchors are present, we have a heal line.
            if p_action != -1 and p_s != -1 and p_for != -1:
                _ = self.parse_ts(line, p_ts_end)

                # Extract the main variables using anchors.
                caster_name = line[p_ts_end + 2 : p_s]
                spellname_heals = line[p_s + 4 : p_action]
                targetname_heals = line[p_action + len(action_verb) : p_for]

                p_num_start = p_for + 5
                p_period = line.find(".", p_num_start)
                p_num_end = p_period
                amount = line[p_num_start:p_num_end]

                self.subtree_heals_line.name = caster_name  # magic cached reference
                self.subtree_heals_line.spellname = spellname_heals  # magic cached reference
                self.subtree_heals_line.heal_crit = crit_token_value  # magic cached reference
                self.subtree_heals_line.targetname = targetname_heals  # magic cached reference
                self.subtree_heals_line.heal_amount = amount  # magic cached reference
                return self.heals_line_tree  # magic cached reference

            p_fades = line.find(" fades from ", p_ts_end)

            if p_fades != -1:
                _ = self.parse_ts(line, p_ts_end)

                # The spellname is between the timestamp and the anchor phrase.
                spellname_fades = line[p_ts_end + 2 : p_fades]

                # The targetname is between the anchor and the final period.
                # 12 is len(' fades from '); -2 is .\n
                targetname_fades = line[p_fades + 12 : -2]

                self.subtree_fades_line.spellname = spellname_fades  # magic cached reference
                self.subtree_fades_line.targetname = targetname_fades  # magic cached reference
                return self.fades_line_tree  # magic cached reference

            p_suffers = line.find(" suffers ", p_ts_end)

            if p_suffers != -1:
                _ = self.parse_ts(line, p_ts_end)

                # Target is always between the timestamp and " suffers ".
                targetname_suffers = line[p_ts_end + 2 : p_suffers]

                # Amount is always the first word after " suffers ".
                p_num_start = p_suffers + 9  # len(' suffers ')
                p_num_end = line.find(" ", p_num_start)
                amount = line[p_num_start:p_num_end]

                self.subtree_suffers_line_source.targetname = targetname_suffers
                self.subtree_suffers_line_source.damage = amount

                # figure out if there's a source
                # The source is indicated by the phrase " damage from ".
                p_from = line.find(" damage from ", p_num_end)

                if p_from != -1:
                    # Source is present
                    damage_type = line[p_num_end + 1 : p_from]

                    # Find the 's marker to separate caster and spell.
                    p_s_start = p_from + 13  # len(' damage from ')

                    for suffix in (" 's ", "'s "):
                        # try to parse 6/14 22:02:29.549  Magn suffers 528 Shadow damage from Ima'ghaol, Herald of Desolation's Aura of Agony.
                        p_s = line.find(suffix, p_s_start)
                        if p_s != -1:
                            # The final period marks the end of the spell.
                            p_period = line.rfind(".", p_s)

                            castername = line[p_s_start:p_s]
                            spellname_suffers_line = line[p_s + len(suffix) : p_period]

                            # magic cached reference
                            self.subtree_suffers_line_source.spell_damage_type = damage_type
                            self.subtree_suffers_line_source.castername = (
                                castername  # magic cached reference
                            )
                            self.subtree_suffers_line_source.spellname = (
                                spellname_suffers_line  # magic cached reference
                            )
                            return self.suffers_line_source_tree  # magic cached reference

                else:
                    # No source is present
                    # In this case, the grammar is "... points of [type] damage."
                    p_points = line.find(" points of ", p_num_end)
                    if p_points != -1:
                        p_damage_word = line.find(" damage.", p_points)

                        damage_type = line[p_points + 11 : p_damage_word]

                        self.subtree_suffers_line_nosource.targetname = targetname_suffers
                        self.subtree_suffers_line_nosource.damage = amount
                        self.subtree_suffers_line_nosource.spell_damage_type = damage_type
                        return self.suffers_line_nosource_tree  # magic cached reference

            p_gains = line.find(" gains ", p_ts_end)

            # The end of a gains_line is very specific: " (#)."
            p_paren_open = line.rfind(" (", p_gains)
            p_paren_close = line.find(").", p_paren_open)

            if p_gains != -1 and p_paren_open != -1 and p_paren_close != -1:
                _ = self.parse_ts(line, p_ts_end)

                # The name is between the timestamp and " gains ".
                name = line[p_ts_end + 2 : p_gains]

                # The spellname is between " gains " and the " (".
                # This correctly captures trailing spaces, like in "Shadow Protection  ".
                spellname_gains = line[p_gains + 7 : p_paren_open]  # 7 is len(' gains ')

                # The stackcount is the number between the parentheses.
                stackcount = line[p_paren_open + 2 : p_paren_close]  # +2 skips " ("

                self.subtree_gains_line.name = name  # magic cached reference
                self.subtree_gains_line.spellname = spellname_gains  # magic cached reference
                self.subtree_gains_line.stackcount = stackcount  # magic cached reference
                return self.gains_line_tree

            action_phrase = " begins to cast "
            p_action = line.find(action_phrase, p_ts_end)

            if p_action != -1:
                _ = self.parse_ts(line, p_ts_end)

                # The caster's name is between the timestamp and the anchor phrase.
                caster_name = line[p_ts_end + 2 : p_action]

                spellname_begins_to_cast = line[p_action + len(action_phrase) : -2]

                self.subtree_begins_to_cast_line.name = caster_name  # magic cached reference
                self.subtree_begins_to_cast_line.spellname = (
                    spellname_begins_to_cast  # magic cached reference
                )

                return self.begins_to_cast_line_tree  # magic cached reference

            action_phrase = " is afflicted by "
            p_action = line.find(action_phrase, p_ts_end)

            # The line must end with " (#)."
            p_paren_open = line.rfind(" (", p_action)
            p_paren_close = line.find(").", p_paren_open)

            # If all anchors are found in the correct order, we have a match.
            if p_action != -1 and p_paren_open != -1 and p_paren_close != -1:
                _ = self.parse_ts(line, p_ts_end)

                # The targetname is between the timestamp and the action phrase.
                targetname_afflicted = line[p_ts_end + 2 : p_action]

                # The spellname is everything between the action phrase and the final " (#)".
                spellname_afflicted = line[p_action + len(action_phrase) : p_paren_open]

                self.subtree_afflicted_line.targetname = (
                    targetname_afflicted  # magic cached reference
                )
                self.subtree_afflicted_line.spellname = (
                    spellname_afflicted  # magic cached reference
                )
                return self.afflicted_line_tree  # magic cached reference

            p_casts = line.find(" casts ", p_ts_end)

            if p_casts != -1:
                _ = self.parse_ts(line, p_ts_end)

                # Caster is always present and in the same spot.
                caster_name = line[p_ts_end + 2 : p_casts]

                # Now we determine the structure based on the optional parts.
                p_on = line.find(" on ", p_casts)

                spellname_casts: str
                targetname_casts: str | None = None

                if p_on != -1:
                    # A target is present
                    # The spell is between " casts " and " on ".
                    spellname_casts = line[p_casts + 7 : p_on]  # 7 is len(' casts ')

                    # Now check if the special "damaged" case exists.
                    # The "damaged" phrase replaces the final period.
                    p_damaged = line.find(" damaged.", p_casts)
                    if p_damaged != -1 and line.find(":", p_on) != -1:
                        # For "on Target: ... damaged.", the target is between " on " and ":".
                        p_colon = line.find(":", p_on)
                        targetname_casts = line[p_on + 4 : p_colon]  # 4 is len(' on ')
                    else:
                        # For "on Target.", the target is between " on " and the end.
                        targetname_casts = line[p_on + 4 : -2]

                else:
                    # No target is present
                    # The spell is everything after " casts " to the end.
                    spellname_casts = line[p_casts + 7 : -2]

                self.subtree_casts_line.name = caster_name
                self.subtree_casts_line.spellname = spellname_casts
                self.subtree_casts_line.targetname = targetname_casts

                return self.casts_line_tree  # magic cached reference

            # already have this
            # p_gains = line.find(' gains ', p_ts_end)

            # We will find the anchors in order.
            p_extra = line.find(" extra attack", p_gains)  # Note: no 's' here
            p_through = line.find(" through ", p_extra)

            # If all three anchors are found in a valid sequence...
            if p_gains != -1 and p_extra != -1 and p_through != -1:
                _ = self.parse_ts(line, p_ts_end)

                # The name is between the timestamp and " gains ".
                name = line[p_ts_end + 2 : p_gains]

                # The number of attacks is between " gains " and " extra attack".
                howmany = line[p_gains + 7 : p_extra]  # 7 is len(' gains ')

                # The source is everything after " through " to the end.
                source = line[p_through + 9 : -2]  # 9 is len(' through ')

                self.subtree_gains_extra_attacks_line.name = name
                self.subtree_gains_extra_attacks_line.howmany = howmany
                self.subtree_gains_extra_attacks_line.source = source

                return self.gains_extra_attacks_line_tree  # magic cached reference

            # already have this
            # p_gains = line.find(' gains ', p_ts_end)
            p_rage_from = line.find(" Rage from ", p_gains)
            p_s = line.find(" 's ", p_rage_from)

            # If all anchors are found, we have a match.
            if p_gains != -1 and p_rage_from != -1 and p_s != -1:
                _ = self.parse_ts(line, p_ts_end)

                # Slice out the 4 required pieces of data.
                recipient_name = line[p_ts_end + 2 : p_gains]
                rage_amount = line[p_gains + 7 : p_rage_from]  # len(' gains ') == 7
                caster_name = line[p_rage_from + 11 : p_s]  # len(' Rage from ') == 11

                # Spell name is from after " 's " to the final period.
                # Using rfind('.') is robust against spells with periods in their name.
                p_period = line.rfind(".", p_s)
                spellname_gains_rage = line[p_s + 4 : p_period]  # len(" 's ") == 4

                # Construct the tree with 4 children, as expected by the consumer.
                self.subtree_gains_rage_line.name = recipient_name
                self.subtree_gains_rage_line.amount = rage_amount
                self.subtree_gains_rage_line.source = caster_name
                self.subtree_gains_rage_line.spellname = spellname_gains_rage

                return self.gains_rage_line_tree

            # already have this
            # p_gains = line.find(' gains ', p_ts_end)
            p_health_from = line.find(" health from ", p_gains)  # The only changed anchor
            p_s = line.find(" 's ", p_health_from)

            # If all anchors are found, we have a match.
            if p_gains != -1 and p_health_from != -1 and p_s != -1:
                _ = self.parse_ts(line, p_ts_end)

                # Slice out the 4 required pieces of data.
                targetname_gains_health = line[p_ts_end + 2 : p_gains]
                health_amount = line[p_gains + 7 : p_health_from]  # len(' gains ') == 7
                caster_name = line[p_health_from + 13 : p_s]  # len(' health from ') == 13

                p_period = line.rfind(".", p_s)
                spellname_gains_health = line[p_s + 4 : p_period]  # len(" 's ") == 4

                # Construct the tree with 4 children, as expected by the consumer.
                self.subtree_gains_health_line.targetname = targetname_gains_health
                self.subtree_gains_health_line.amount = health_amount
                self.subtree_gains_health_line.source = caster_name
                self.subtree_gains_health_line.spellname = spellname_gains_health

                return self.gains_health_line_tree

            # already have this
            # p_gains = line.find(' gains ', p_ts_end)
            p_energy_from = line.find(" Energy from ", p_gains)  # The only changed anchor
            p_s = line.find(" 's ", p_energy_from)

            # If all anchors are found, we have a match.
            if p_gains != -1 and p_energy_from != -1 and p_s != -1:
                _ = self.parse_ts(line, p_ts_end)

                # Slice out the 4 required pieces of data.
                recipient_name = line[p_ts_end + 2 : p_gains]
                energy_amount = line[p_gains + 7 : p_energy_from]  # len(' gains ') == 7
                caster_name = line[p_energy_from + 13 : p_s]  # len(' Energy from ') == 13

                p_period = line.rfind(".", p_s)
                spellname_gains_energy = line[p_s + 4 : p_period]  # len(" 's ") == 4

                # Construct the tree using the cache
                self.subtree_gains_energy_line.recipient = recipient_name
                self.subtree_gains_energy_line.amount = energy_amount
                self.subtree_gains_energy_line.caster = caster_name
                self.subtree_gains_energy_line.spellname = spellname_gains_energy

                return self.gains_energy_line_tree

            p_s = line.find(" 's ", p_ts_end)
            p_resisted = line.find(" was resisted by ", p_s)

            # If both anchors are found, we have a match.
            if p_s != -1 and p_resisted != -1:
                _ = self.parse_ts(line, p_ts_end)

                # Slice out the 3 required pieces of data from between the anchors.
                caster_name = line[p_ts_end + 2 : p_s]
                spellname_resisted = line[p_s + 4 : p_resisted]

                targetname_resist = line[p_resisted + 17 : -2]  # 17 is len(' was resisted by ')

                # Construct the tree using the cache
                self.subtree_resist_line.caster = caster_name
                self.subtree_resist_line.spellname = spellname_resisted
                self.subtree_resist_line.target = targetname_resist

                return self.resist_line_tree

            p_uses = line.find(" uses ", p_ts_end)

            if p_uses != -1:
                _ = self.parse_ts(line, p_ts_end)

                # The user's name is always present.
                user_name = line[p_ts_end + 2 : p_uses]

                # Check for the optional target part.
                p_on = line.find(" on ", p_uses)

                spellname_uses: str
                targetname_uses: str | None = None

                if p_on != -1:
                    # PATTERN WITH A TARGET
                    # The item/spell name is between " uses " and " on ".
                    spellname_uses = line[p_uses + 6 : p_on]  # 6 is len(' uses ')

                    # The target name is after " on " to the end of the line.
                    targetname_uses = line[p_on + 4 : -2]  # 4 is len(' on ')
                else:
                    # PATTERN WITHOUT A TARGET
                    # The item/spell name is simply everything after " uses ".
                    spellname_uses = line[p_uses + 6 : -2]

                # Construct the tree using the cache
                self.subtree_uses_line.name = user_name
                self.subtree_uses_line.item = spellname_uses
                self.subtree_uses_line.target = targetname_uses

                return self.uses_line_tree

            anchor1 = " attacks. "
            anchor2 = " dodges."

            # Find the position of both anchors sequentially.
            p_anchor1 = line.find(anchor1, p_ts_end)
            p_anchor2 = line.find(anchor2, p_anchor1)  # Start search after the first anchor

            # If both anchors were found in the correct order, we have a match.
            if p_anchor1 != -1 and p_anchor2 != -1:
                _ = self.parse_ts(line, p_ts_end)

                # The attacker is between the timestamp and the first anchor.
                attacker = line[p_ts_end + 2 : p_anchor1]

                # The dodger is between the first anchor and the second anchor.
                dodger_start = p_anchor1 + len(anchor1)
                dodger = line[dodger_start:p_anchor2]

                # Construct the tree using the cache
                self.subtree_dodges_line.attacker = attacker
                self.subtree_dodges_line.dodger = dodger

                return self.dodges_line_tree

            # miss ability or autoattacks
            p_s = line.find(" 's ", p_ts_end)

            if p_s != -1:
                # misses_ability_line
                # If 's is present, it MUST be an ability miss.
                # Now, we find which verb is used.
                p_verb = line.find(" missed ", p_s)
                verb_len = 8  # len(' missed ')
                if p_verb == -1:
                    p_verb = line.find(" misses ", p_s)
                    verb_len = 8  # len(' misses ')

                # If we found a verb after 's, we can parse.
                if p_verb != -1:
                    _ = self.parse_ts(line, p_ts_end)

                    caster_name = line[p_ts_end + 2 : p_s]
                    spellname_misses_ability = line[p_s + 4 : p_verb]
                    targetname_misses_ability = line[p_verb + verb_len : -2]

                    # Construct the tree using the cache
                    self.subtree_misses_ability_line.caster = caster_name
                    self.subtree_misses_ability_line.spellname = spellname_misses_ability
                    self.subtree_misses_ability_line.target = targetname_misses_ability

                    return self.misses_ability_line_tree

            else:
                # misses_line
                # If 's is NOT present, it can only be a simple miss.
                p_misses = line.find(" misses ", p_ts_end)
                if p_misses != -1:
                    _ = self.parse_ts(line, p_ts_end)

                    attacker = line[p_ts_end + 2 : p_misses]
                    target = line[p_misses + 8 : -2]  # len(' misses ')

                    # Construct the tree using the cache
                    self.subtree_misses_line.attacker = attacker
                    self.subtree_misses_line.target = target

                    return self.misses_line_tree

            anchor = " dies.\n"

            # Since we know the exact ending, we can use a single, highly efficient check.
            if line.endswith(anchor):
                _ = self.parse_ts(line, p_ts_end)

                # The name is between the timestamp and the start of our known suffix.
                # The slice end is -len(anchor) to remove " dies.\n"
                name_start = p_ts_end + 2
                name_end = -len(anchor)
                name = line[name_start:name_end]

                # Construct the tree using the cache
                self.subtree_dies_line.name = name

                return self.dies_line_tree

            parries_anchor = " parries.\n"

            # Use a single, fast check to identify the line type.
            if line.endswith(parries_anchor):
                # Now that we know the line type, find the middle anchor.
                middle_anchor = " attacks. "
                p_attacks = line.find(middle_anchor, p_ts_end)

                if p_attacks != -1:
                    _ = self.parse_ts(line, p_ts_end)

                    # The attacker is between the timestamp and the middle anchor.
                    attacker = line[p_ts_end + 2 : p_attacks]

                    # The parrier is between the middle anchor and the final anchor.
                    # We can slice precisely using the lengths of our known strings.
                    parrier_start = p_attacks + len(middle_anchor)
                    parrier_end = -len(parries_anchor)
                    parrier = line[parrier_start:parrier_end]

                    # Construct the simple two-child tree.
                    self.subtree_parry_line.attacker = attacker
                    self.subtree_parry_line.parrier = parrier

                    return self.parry_line_tree

            blocks_anchor = " blocks.\n"
            if line.endswith(blocks_anchor):
                middle_anchor = " attacks. "
                p_attacks = line.find(middle_anchor, p_ts_end)

                if p_attacks != -1:
                    _ = self.parse_ts(line, p_ts_end)

                    attacker = line[p_ts_end + 2 : p_attacks]
                    blocker_start = p_attacks + len(middle_anchor)
                    blocker_end = -len(blocks_anchor)
                    blocker = line[blocker_start:blocker_end]

                    self.subtree_block_line.name = attacker
                    self.subtree_block_line.targetname = blocker
                    return self.block_line_tree

            # Find all the anchors in sequential order.
            p_reflects = line.find(" reflects ", p_ts_end)
            p_damage_to = line.find(" damage to ", p_reflects)  # Changed anchor name for clarity

            # If both anchors are found, we have a match.
            if p_reflects != -1 and p_damage_to != -1:
                _ = self.parse_ts(line, p_ts_end)

                # --- Slice out the 4 required pieces of data ---
                reflector_name = line[p_ts_end + 2 : p_reflects]

                middle_part_start = p_reflects + 10  # len(' reflects ')
                p_space_in_middle = line.find(" ", middle_part_start)

                amount = line[middle_part_start:p_space_in_middle]
                damage_type = line[p_space_in_middle + 1 : p_damage_to]

                # The target name is after the second anchor, with the final ".\n" removed.
                target_start = p_damage_to + 11  # len(' damage to ')
                target_end = -2  # Removes exactly ".\n"
                targetname_reflects = line[target_start:target_end]

                # Construct the tree using the cache
                self.subtree_reflects_damage_line.reflector = reflector_name
                self.subtree_reflects_damage_line.amount = amount
                self.subtree_reflects_damage_line.damage_type = damage_type
                self.subtree_reflects_damage_line.target = targetname_reflects

                return self.reflects_damage_line_tree

            action_phrase = " begins to perform "
            p_action = line.find(action_phrase, p_ts_end)

            if p_action != -1:
                _ = self.parse_ts(line, p_ts_end)

                # The performer's name is between the timestamp and the anchor phrase.
                performer_name = line[p_ts_end + 2 : p_action]

                # The action name is after the anchor, with the final ".\n" removed.
                action_start = p_action + len(action_phrase)
                action_end = -2  # Removes exactly ".\n"
                action_name = line[action_start:action_end]

                # Construct the tree using the cache
                self.subtree_begins_to_perform_line.name = performer_name
                self.subtree_begins_to_perform_line.spellname = action_name

                return self.begins_to_perform_line_tree

            # Find the two key anchors in sequential order.
            p_s = line.find(" 's ", p_ts_end)
            p_dodged = line.find(" was dodged by ", p_s)

            # If both anchors are found, we have a match.
            if p_s != -1 and p_dodged != -1:
                _ = self.parse_ts(line, p_ts_end)

                # Slice out the 3 required pieces of data from between the anchors.
                caster_name = line[p_ts_end + 2 : p_s]
                spellname_dodge_ability = line[p_s + 4 : p_dodged]

                # Target name is after the second anchor, with ".\n" removed.
                target_start = p_dodged + 15  # len(' was dodged by ')
                target_end = -2  # Removes exactly ".\n"
                targetname_dodge_ability = line[target_start:target_end]

                # Construct the tree using the cache
                self.subtree_dodge_ability_line.caster = caster_name
                self.subtree_dodge_ability_line.spellname = spellname_dodge_ability
                self.subtree_dodge_ability_line.target = targetname_dodge_ability

                return self.dodge_ability_line_tree

            p_s = line.find(" 's ", p_ts_end)
            p_causes = line.find(" causes ", p_s)

            # The line must end with " damage.\n"
            final_anchor = " damage.\n"
            if p_s != -1 and p_causes != -1 and line.endswith(final_anchor):
                _ = self.parse_ts(line, p_ts_end)

                caster_name = line[p_ts_end + 2 : p_s]
                spellname_causes_damage = line[p_s + 4 : p_causes]

                # To separate the target from the amount, we find the last space
                # before the final anchor " damage.".
                p_damage_word = line.rfind(" damage.", p_causes)
                p_last_space = line.rfind(" ", p_causes, p_damage_word)

                # target name & amount can now be sliced.
                targetname_causes_damage = line[p_causes + 8 : p_last_space]  # len(' causes ')
                amount = line[p_last_space + 1 : p_damage_word]

                # Construct the tree using the cache
                self.subtree_causes_damage_line.caster = caster_name
                self.subtree_causes_damage_line.spellname = spellname_causes_damage
                self.subtree_causes_damage_line.target = targetname_causes_damage
                self.subtree_causes_damage_line.amount = amount

                return self.causes_damage_line_tree

            final_anchor = " is removed.\n"

            # We can validate the line with a single, fast check.
            if line.endswith(final_anchor):
                # If it ends correctly, now find the 's anchor.
                p_s = line.find(" 's ", p_ts_end)

                if p_s != -1:
                    _ = self.parse_ts(line, p_ts_end)

                    # The caster name is between the timestamp and 's.
                    caster_name = line[p_ts_end + 2 : p_s]

                    # The spell name is between 's and the final anchor.
                    spell_start = p_s + 4  # len(" 's ")
                    # Use rfind to get the start of the final anchor for a clean slice.
                    p_removed = line.rfind(" is removed.")
                    spellname_removed = line[spell_start:p_removed]

                    # Construct the tree using the cache
                    self.subtree_removed_line.name = caster_name
                    self.subtree_removed_line.spellname = spellname_removed

                    return self.removed_line_tree

            anchor1 = " 's "
            anchor2 = " fails. "
            final_anchor = " is immune.\n"

            if line.endswith(final_anchor):
                p_anchor1 = line.find(anchor1, p_ts_end)
                p_anchor2 = line.find(anchor2, p_anchor1)

                if p_anchor1 != -1 and p_anchor2 != -1:
                    _ = self.parse_ts(line, p_ts_end)

                    caster_name = line[p_ts_end + 2 : p_anchor1]
                    spellname_immune = line[p_anchor1 + len(anchor1) : p_anchor2]

                    target_start = p_anchor2 + len(anchor2)
                    target_end = -len(final_anchor)
                    targetname_immune_ability = line[target_start:target_end]

                    # Construct the tree using the cache
                    self.subtree_immune_ability_line.caster = caster_name
                    self.subtree_immune_ability_line.spellname = spellname_immune
                    self.subtree_immune_ability_line.target = targetname_immune_ability

                    return self.immune_ability_line_tree

            # Find the two key anchors in sequential order.
            p_s = line.find(" 's ", p_ts_end)
            p_parried = line.find(" was parried by ", p_s)

            # If both anchors are found, we have a match.
            if p_s != -1 and p_parried != -1:
                _ = self.parse_ts(line, p_ts_end)

                # Slice out the 3 required pieces of data from between the anchors.
                caster_name = line[p_ts_end + 2 : p_s]
                spellname_parry_ability = line[p_s + 4 : p_parried]

                # Target name is after the second anchor, with ".\n" removed.
                target_start = p_parried + 16  # len(' was parried by ')
                target_end = -2  # Removes exactly ".\n"
                targetname_parry_ability = line[target_start:target_end]

                # Construct the tree using the cache
                self.subtree_parry_ability_line.caster = caster_name
                self.subtree_parry_ability_line.spellname = spellname_parry_ability
                self.subtree_parry_ability_line.target = targetname_parry_ability

                return self.parry_ability_line_tree

            middle_anchor = " attacks but "
            final_anchor_with_newline = " is immune.\n"

            # First, use a fast check to see if the line ends correctly.
            if line.endswith(final_anchor_with_newline):
                # If it does, find the middle anchor.
                p_middle = line.find(middle_anchor, p_ts_end)

                if p_middle != -1:
                    # We have a confirmed match.
                    _ = self.parse_ts(line, p_ts_end)

                    # The attacker is between the timestamp and the middle anchor.
                    attacker = line[p_ts_end + 2 : p_middle]

                    # The target is between the middle anchor and the final anchor.
                    # We can slice precisely using the lengths of our known strings.
                    target_start = p_middle + len(middle_anchor)
                    target_end = -len(final_anchor_with_newline)
                    target = line[target_start:target_end]

                    # Construct the tree using the cache
                    self.subtree_immune_line.attacker = attacker
                    self.subtree_immune_line.target = target

                    return self.immune_line_tree

            p_performs = line.find(" performs ", p_ts_end)

            if p_performs != -1:
                # A "performs" action was found. Now check for the "on" to disambiguate.
                p_on = line.find(" on ", p_performs)

                if p_on != -1:
                    # performs_on_line (most specific)
                    _ = self.parse_ts(line, p_ts_end)

                    performer = line[p_ts_end + 2 : p_performs]
                    spellname_performs_on = line[p_performs + 10 : p_on]  # len(' performs ')
                    targetname_performs_on = line[p_on + 4 : -2]  # len(' on '), removes ".\n"

                    # Construct the tree using the cache
                    self.subtree_performs_on_line.performer = performer
                    self.subtree_performs_on_line.spellname = spellname_performs_on
                    self.subtree_performs_on_line.targetname = targetname_performs_on

                    return self.performs_on_line_tree

                else:
                    # performs_line (less specific, potentially dangerous)
                    # We only get here if " performs " was found, but " on " was NOT.
                    # very possible this matches a different line type someday
                    _ = self.parse_ts(line, p_ts_end)

                    performer = line[p_ts_end + 2 : p_performs]
                    spellname_performs = line[
                        p_performs + 10 : -2
                    ]  # len(' performs '), removes ".\n"

                    # Construct the tree using the cache
                    self.subtree_performs_line.performer = performer
                    self.subtree_performs_line.spellname = spellname_performs

                    return self.performs_line_tree

            middle_anchor = " falls and loses "
            final_anchor_with_newline = " health.\n"

            # Use a fast check on the line's ending to pre-filter.
            if line.endswith(final_anchor_with_newline):
                # If the end matches, now find the middle anchor.
                p_middle = line.find(middle_anchor, p_ts_end)

                if p_middle != -1:
                    _ = self.parse_ts(line, p_ts_end)

                    name = line[p_ts_end + 2 : p_middle]

                    amount_start = p_middle + len(middle_anchor)
                    amount_end = -len(final_anchor_with_newline)
                    amount = line[amount_start:amount_end]

                    # Construct the tree using the cache
                    self.subtree_falls_line.name = name
                    self.subtree_falls_line.amount = amount

                    return self.falls_line_tree

            anchor1 = " is immune to "
            anchor2 = " 's "

            p_anchor1 = line.find(anchor1, p_ts_end)
            p_anchor2 = line.find(anchor2, p_anchor1)

            # If both anchors are found in the correct order, we have a match.
            if p_anchor1 != -1 and p_anchor2 != -1:
                _ = self.parse_ts(line, p_ts_end)

                targetname_is_immune = line[p_ts_end + 2 : p_anchor1]

                caster_name = line[p_anchor1 + len(anchor1) : p_anchor2]

                # It's after the second anchor, with the final ".\n" removed.
                spell_start = p_anchor2 + len(anchor2)
                spell_end = -2  # Removes exactly ".\n"
                spellname_is_immune = line[spell_start:spell_end]

                # Construct the tree with 3 children in the correct order.
                # Construct the tree using the cache
                self.subtree_is_immune_ability_line.targetname = targetname_is_immune
                self.subtree_is_immune_ability_line.caster = caster_name
                self.subtree_is_immune_ability_line.spellname = spellname_is_immune

                return self.is_immune_ability_line_tree

            p_s = line.find(" 's ", p_ts_end)
            p_evaded = line.find(" was evaded by ", p_s)

            if p_s != -1 and p_evaded != -1:
                _ = self.parse_ts(line, p_ts_end)

                caster_name = line[p_ts_end + 2 : p_s]
                spellname_was_evaded = line[p_s + 4 : p_evaded]

                target_start = p_evaded + 15  # len(' was evaded by ')
                target_end = -2  # Removes exactly ".\n"
                targetname_was_evaded = line[target_start:target_end]

                # Construct the tree using the cache
                self.subtree_was_evaded_line.name = caster_name
                self.subtree_was_evaded_line.spellname = spellname_was_evaded
                self.subtree_was_evaded_line.targetname = targetname_was_evaded

                return self.was_evaded_line_tree

            consolidated_anchor = "CONSOLIDATED: "
            p_consolidated = line.find(consolidated_anchor, p_ts_end)

            if p_consolidated != -1:
                # We have a CONSOLIDATED line.
                _ = self.parse_ts(line, p_ts_end)

                # Get the entire block of consolidated data.
                data_block = line[p_consolidated + len(consolidated_anchor) :]

                # Split the block into individual cases using "{" as the delimiter.
                cases = data_block.split("{")

                self.subtree_consolidated_line.children.clear()
                for case_str in cases:
                    # For each case, check if it's a PET entry.
                    if case_str.startswith("PET: "):
                        pet_tree = self.parse_consolidated_pet(case_str)
                        if pet_tree:
                            self.subtree_consolidated_line.children.append(pet_tree)

                return self.consolidated_line_tree

            p_s = line.find(" 's ", p_ts_end)
            p_absorbed = line.find(" is absorbed by ", p_s)

            # If both anchors are found, we have a match.
            if p_s != -1 and p_absorbed != -1:
                _ = self.parse_ts(line, p_ts_end)

                caster_name = line[p_ts_end + 2 : p_s]
                spellname_is_absorbed = line[p_s + 4 : p_absorbed]

                target_start = p_absorbed + 16  # len(' is absorbed by ')
                target_end = -2  # Removes exactly ".\n"
                targetname_is_absorbed = line[target_start:target_end]

                # Construct the tree using the cache
                self.subtree_is_absorbed_ability_line.caster = caster_name
                self.subtree_is_absorbed_ability_line.spellname = spellname_is_absorbed
                self.subtree_is_absorbed_ability_line.target = targetname_is_absorbed

                return self.is_absorbed_ability_line_tree

            p_absorbs = line.find(" absorbs ", p_ts_end)
            p_s = line.find(" 's ", p_absorbs)

            # If both anchors are found, we have a match.
            if p_absorbs != -1 and p_s != -1:
                _ = self.parse_ts(line, p_ts_end)

                absorber_name = line[p_ts_end + 2 : p_absorbs]

                caster_name = line[p_absorbs + 9 : p_s]  # 9 is len(' absorbs ')

                # It's after the second anchor, with the final ".\n" removed.
                spell_start = p_s + 4  # len(" 's ")
                spell_end = -2  # Removes exactly ".\n"
                spellname_absorbs_ability = line[spell_start:spell_end]

                # Construct the tree using the cache
                self.subtree_absorbs_ability_line.absorber = absorber_name
                self.subtree_absorbs_ability_line.caster = caster_name
                self.subtree_absorbs_ability_line.spellname = spellname_absorbs_ability

                return self.absorbs_ability_line_tree

            middle_anchor = " is slain by "
            p_slain = line.find(middle_anchor, p_ts_end)

            if p_slain != -1:
                last_char = line[-2]  # newline at end

                if last_char == "." or last_char == "!":
                    # We have a confirmed match.
                    _ = self.parse_ts(line, p_ts_end)

                    # The victim's name is between the timestamp and the middle anchor.
                    victim = line[p_ts_end + 2 : p_slain]

                    # cleanly remove any combination of '.', '!'
                    slayer_start = p_slain + len(middle_anchor)
                    slayer = line[slayer_start:-2]

                    # Construct the tree using the cache
                    self.subtree_slain_line.victim = victim
                    self.subtree_slain_line.slayer = slayer

                    return self.slain_line_tree

            action_phrase = " creates "
            p_action = line.find(action_phrase, p_ts_end)

            if p_action != -1 and line.endswith(".\n"):
                _ = self.parse_ts(line, p_ts_end)

                creator_name = line[p_ts_end + 2 : p_action]

                item_start = p_action + len(action_phrase)
                item_end = -2  # Removes exactly ".\n"
                item_name = line[item_start:item_end]

                # Construct the tree using the cache
                self.subtree_creates_line.creator = creator_name
                self.subtree_creates_line.item = item_name

                return self.creates_line_tree

            middle_anchor = " is killed by "
            p_killed = line.find(middle_anchor, p_ts_end)

            if p_killed != -1 and line.endswith(".\n"):
                _ = self.parse_ts(line, p_ts_end)

                victim = line[p_ts_end + 2 : p_killed]

                killer_start = p_killed + len(middle_anchor)
                killer_end = -2  # Removes exactly ".\n"
                killer = line[killer_start:killer_end]

                # Construct the tree using the cache
                self.subtree_is_killed_line.victim = victim
                self.subtree_is_killed_line.killer = killer

                return self.is_killed_line_tree

            final_anchor_with_newline = " is destroyed.\n"

            if line.endswith(final_anchor_with_newline):
                _ = self.parse_ts(line, p_ts_end)

                # The entity's name is between the timestamp and the start of our known suffix.
                # A negative slice is the cleanest way to remove the suffix.
                name_start = p_ts_end + 2
                name_end = -len(final_anchor_with_newline)
                entity_name = line[name_start:name_end]

                # Construct the tree using the cache
                self.subtree_is_destroyed_line.entity_name = entity_name

                return self.is_destroyed_line_tree

            p_s = line.find(" 's ", p_ts_end)
            p_reflected = line.find(" is reflected back by ", p_s)

            # If both anchors are found, we have a match.
            if p_s != -1 and p_reflected != -1:
                _ = self.parse_ts(line, p_ts_end)

                caster_name = line[p_ts_end + 2 : p_s]
                spellname_is_reflected = line[p_s + 4 : p_reflected]

                reflector_start = p_reflected + 20  # len(' is reflected back by ')
                reflector_end = -2  # Removes exactly ".\n"
                reflector_name = line[reflector_start:reflector_end]

                # Construct the tree using the cache
                self.subtree_is_reflected_back_line.caster = caster_name
                self.subtree_is_reflected_back_line.spellname = spellname_is_reflected
                self.subtree_is_reflected_back_line.reflector = reflector_name

                return self.is_reflected_back_line_tree

            if line.find("COMBATANT_INFO: ", p_ts_end + 2, p_ts_end + 2 + 16) != -1:
                _ = self.parse_ts(line, p_ts_end)
                return self.combatant_info_line_tree

            if line.find("NONE", p_ts_end + 2, p_ts_end + 2 + 4) != -1:
                _ = self.parse_ts(line, p_ts_end)
                return self.none_line_tree

            if line.find(" fails to dispel ", p_ts_end + 2) != -1:
                _ = self.parse_ts(line, p_ts_end)
                return self.fails_to_dispel_line_tree

            if line.find(" health for swimming in lava.", p_ts_end + 2) != -1:
                _ = self.parse_ts(line, p_ts_end)
                return self.lava_line_tree

            if line.find(" slays ", p_ts_end + 2) != -1 and line.endswith("!\n"):
                _ = self.parse_ts(line, p_ts_end)
                return self.slays_line_tree

            if line.find(" pet begins eating a ", p_ts_end + 2) != -1:
                _ = self.parse_ts(line, p_ts_end)
                return self.pet_begins_eating_line_tree

            if line.endswith(" 's equipped items suffer a 10% durability loss.\n"):
                _ = self.parse_ts(line, p_ts_end)
                return self.equipped_durability_loss_line_tree

            p_s = line.find(" 's ", p_ts_end)
            p_blocked = line.find(" was blocked by ", p_s)

            if p_s != -1 and p_blocked != -1:
                _ = self.parse_ts(line, p_ts_end)

                caster_name = line[p_ts_end + 2 : p_s]
                spellname_block_ability = line[p_s + 4 : p_blocked]

                blocker_start = p_blocked + 16  # len(' was blocked by ')
                blocker_end = -2  # Removes exactly ".\n"
                blocker_name = line[blocker_start:blocker_end]

                # Construct the tree using the cache
                self.subtree_block_ability_line.caster = caster_name
                self.subtree_block_ability_line.spellname = spellname_block_ability
                self.subtree_block_ability_line.blocker = blocker_name

                return self.block_ability_line_tree

            middle_anchor = " attacks. "
            final_anchor_with_newline = " blocks.\n"

            if line.endswith(final_anchor_with_newline):
                p_attacks = line.find(middle_anchor, p_ts_end)

                if p_attacks != -1:
                    _ = self.parse_ts(line, p_ts_end)

                    attacker = line[p_ts_end + 2 : p_attacks]

                    blocker_start = p_attacks + len(middle_anchor)
                    blocker_end = -len(final_anchor_with_newline)
                    blocker = line[blocker_start:blocker_end]

                    self.subtree_block_line.name = attacker
                    self.subtree_block_line.targetname = blocker
                    return self.block_line_tree

            p_interrupts = line.find(" interrupts ", p_ts_end)
            p_s = line.find(" 's ", p_interrupts)

            # If both anchors are found, we have a match.
            if p_interrupts != -1 and p_s != -1:
                _ = self.parse_ts(line, p_ts_end)

                interrupter_name = line[p_ts_end + 2 : p_interrupts]

                targetname_interrupts = line[p_interrupts + 12 : p_s]  # 12 is len(' interrupts ')

                spell_start = p_s + 4  # len(" 's ")
                spell_end = -2  # Removes exactly ".\n"
                spellname_interrupts = line[spell_start:spell_end]

                # Construct the tree using the cache
                self.subtree_interrupts_line.interrupter = interrupter_name
                self.subtree_interrupts_line.targetname = targetname_interrupts
                self.subtree_interrupts_line.spellname = spellname_interrupts

                return self.interrupts_line_tree

            middle_anchor = " attacks. "
            final_anchor_with_newline = " absorbs all the damage.\n"

            if line.endswith(final_anchor_with_newline):
                # If it does, find the middle anchor.
                p_attacks = line.find(middle_anchor, p_ts_end)

                if p_attacks != -1:
                    _ = self.parse_ts(line, p_ts_end)

                    attacker = line[p_ts_end + 2 : p_attacks]

                    absorber_start = p_attacks + len(middle_anchor)
                    absorber_end = -len(final_anchor_with_newline)
                    absorber = line[absorber_start:absorber_end]

                    # Construct the tree using the cache
                    self.subtree_absorbs_all_line.attacker = attacker
                    self.subtree_absorbs_all_line.absorber = absorber

                    return self.absorbs_all_line_tree

            anchor1 = " gains "
            anchor2 = " Happiness from "
            final_anchor_with_newline = " 's Feed Pet Effect.\n"

            if line.endswith(final_anchor_with_newline):
                p_anchor1 = line.find(anchor1, p_ts_end)
                p_anchor2 = line.find(anchor2, p_anchor1)

                if p_anchor1 != -1 and p_anchor2 != -1:
                    _ = self.parse_ts(line, p_ts_end)

                    pet_name = line[p_ts_end + 2 : p_anchor1]

                    amount = line[p_anchor1 + len(anchor1) : p_anchor2]

                    owner_start = p_anchor2 + len(anchor2)
                    owner_end = -len(final_anchor_with_newline)
                    owner_name = line[owner_start:owner_end]

                    self.subtree_gains_happiness_line.petname = pet_name
                    self.subtree_gains_happiness_line.amount = amount
                    self.subtree_gains_happiness_line.owner_name = owner_name

                    return self.gains_happiness_line_tree

            final_anchor = " is dismissed.\n"

            if line.endswith(final_anchor):
                # The key is finding the possessive "'s" before the final phrase.
                p_dismissed = line.rfind(" is dismissed.")
                p_s = line.rfind("'s", p_ts_end, p_dismissed)

                if p_s != -1:
                    _ = self.parse_ts(line, p_ts_end)

                    # Check if the character *before* the apostrophe is a space.
                    if line[p_s - 1] == " ":
                        # Case: "Pitsharp 's"
                        # The owner name ends one character before the space.
                        owner_name = line[p_ts_end + 2 : p_s - 1]
                    else:
                        # Case: "Leyzara's"
                        # The owner name ends right at the apostrophe.
                        owner_name = line[p_ts_end + 2 : p_s]
                    pet_start = p_s + 3  # Skips over "'s "

                    pet_name = line[pet_start:p_dismissed]

                    # Construct the tree using the cache
                    self.subtree_is_dismissed_line.owner_name = owner_name
                    self.subtree_is_dismissed_line.pet_name = pet_name

                    return self.is_dismissed_line_tree

            # 7/14 20:33:44.437  Titicacal 's Drain Mana drains 139 Mana from Obsidian Eradicator. Titicacal gains 139 Mana.
            # 7/14 00:00:03.782  Solnius 's Sanctum Mind Decay drains 135 Mana from Interlan.

            p_drains = line.find(" drains ", p_ts_end)
            if p_drains != -1:
                p_s = line.find(" 's ", p_ts_end, p_drains)
                p_mana_from = line.find(" Mana from ", p_drains)
                p_period = line.find(".", p_mana_from)
                if p_s != -1 and p_mana_from != -1 and p_period != -1:
                    caster = line[p_ts_end + 2 : p_s]
                    spellname = line[p_s + 4 : p_drains]
                    mana = line[p_drains + 8 : p_mana_from]
                    targetname = line[p_mana_from + 11 : p_period]

                    gains = "0"
                    # check for ". Caster gains X Mana."
                    p_dot_space = p_period
                    p_gains2 = line.find(" gains ", p_dot_space)
                    p_mana_dot = line.find(" Mana.", p_gains2)
                    if p_gains2 != -1 and p_mana_dot != -1:
                        gains = line[p_gains2 + 7 : p_mana_dot]

                    self.subtree_drains_mana_line.caster = caster
                    self.subtree_drains_mana_line.spellname = spellname
                    self.subtree_drains_mana_line.mana = mana
                    self.subtree_drains_mana_line.targetname = targetname
                    self.subtree_drains_mana_line.gains = gains
                    self.parse_ts(line, p_ts_end)

                    return self.drains_mana_line_tree

        except Exception as e:
            msg = f"{e} {line} \n"
            self.unparsed_logger.log(msg)

        return None
