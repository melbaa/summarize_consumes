import logging


grammar = r"""
start: timestamp "  " _line NEWLINE

_line: gains_line
    | gains_rage_line
    | gains_mana_line
    | gains_energy_line
    | gains_health_line
    | gains_extra_attacks_line
    | dies_line
    | begins_to_cast_line
    | casts_line
    | consolidated_line
    | combatant_info_line
    | block_ability_line
    | block_line
    | parry_ability_line
    | parry_line
    | misses_line
    | misses_ability_line
    | resist_line
    | immune_ability_line
    | immune_line
    | is_immune_ability_line
    | is_destroyed_line
    | afflicted_line
    | is_absorbed_ability_line
    | absorbs_ability_line
    | absorbs_all_line
    | interrupts_line
    | fails_to_dispel_line
    | was_evaded_line
    | removed_line
    | none_line
    | suffers_line
    | hits_ability_line
    | hits_autoattack_line
    | dodges_line
    | dodge_ability_line
    | fades_line
    | slain_line
    | heals_line
    | creates_line
    | is_killed_line
    | performs_on_line
    | performs_line
    | begins_to_perform_line
    | reflects_damage_line
    | is_reflected_back_line
    | falls_line
    | lava_line
    | slays_line
    | pet_begins_eating_line
    | gains_happiness_line
    | is_dismissed_line
    | is_dismissed_line2
    | causes_damage_line
    | equipped_durability_loss

equipped_durability_loss: MULTIWORD " 's equipped items suffer a 10% durability loss."

causes_damage_line: MULTIWORD " 's " MULTIWORD " causes " MULTIWORD " " INT " damage."

fails_to_dispel_line: MULTIWORD " fails to dispel " MULTIWORD " 's " MULTIWORD "."

is_reflected_back_line: MULTIWORD " 's " MULTIWORD " is reflected back by " MULTIWORD "."

is_destroyed_line: MULTIWORD " is destroyed."

interrupts_line: MULTIWORD " interrupts " MULTIWORD " 's " MULTIWORD "."

slays_line: MULTIWORD " slays " MULTIWORD "!"

none_line: "NONE"

falls_line: MULTIWORD " falls and loses " INT " health."
lava_line: MULTIWORD " loses " INT " health for swimming in lava." (" (" resisted_suffix)?  (" (" absorbed_suffix)?

reflects_damage_line: MULTIWORD " reflects " INT spell_damage_type " to " MULTIWORD "."

creates_line: MULTIWORD " creates " MULTIWORD "."

suffers_line_nosource: " points of fire damage"
suffers_line_source: spell_damage_type " from " MULTIWORD " 's " MULTIWORD
suffers_line: MULTIWORD " suffers " INT (suffers_line_nosource | suffers_line_source) "." (" (" vulnerability_suffix)? (" (" resisted_suffix)?  (" (" absorbed_suffix)?

fades_line: MULTIWORD " fades from " MULTIWORD "."

removed_line: MULTIWORD " 's " MULTIWORD " is removed."

dies_line: MULTIWORD " dies."
is_killed_line: MULTIWORD " is killed by " MULTIWORD "."
slain_line: MULTIWORD " is slain by " MULTIWORD "!"

is_dismissed_line: MULTIWORD " 's " MULTIWORD " is dismissed."
is_dismissed_line2: MULTIWORD " is dismissed."
gains_happiness_line: MULTIWORD " gains " INT " Happiness from " MULTIWORD " 's Feed Pet Effect."
pet_begins_eating_line: MULTIWORD " pet begins eating a " MULTIWORD "."
block_ability_line: MULTIWORD " 's " MULTIWORD " was blocked by " MULTIWORD "."
block_line: MULTIWORD " attacks. " MULTIWORD " blocks."
parry_ability_line: MULTIWORD " 's " MULTIWORD " was parried by " MULTIWORD "."
parry_line: MULTIWORD " attacks. " MULTIWORD " parries."
dodges_line: MULTIWORD " attacks. " MULTIWORD " dodges."
dodge_ability_line: MULTIWORD " 's " MULTIWORD " was dodged by " MULTIWORD "."
misses_line: MULTIWORD " misses " MULTIWORD "."
misses_ability_line: MULTIWORD " 's " MULTIWORD (" missed "|" misses ") MULTIWORD "."
resist_line: MULTIWORD " 's " MULTIWORD " was resisted by " MULTIWORD "."
immune_ability_line: MULTIWORD " 's " MULTIWORD " fails. " MULTIWORD " is immune."
immune_line: MULTIWORD " attacks but " MULTIWORD " is immune."
is_immune_ability_line: MULTIWORD " is immune to " MULTIWORD " 's " MULTIWORD "."
is_absorbed_ability_line: MULTIWORD " 's " MULTIWORD " is absorbed by " MULTIWORD "."
absorbs_ability_line: MULTIWORD " absorbs " MULTIWORD " 's " MULTIWORD "."
absorbs_all_line: MULTIWORD " attacks. " MULTIWORD " absorbs all the damage."
was_evaded_line: MULTIWORD " 's " MULTIWORD " was evaded by " MULTIWORD "."

heals_line: MULTIWORD " 's " MULTIWORD HEAL_CRIT? " heals " MULTIWORD " for " INT "."

gains_line: MULTIWORD " gains " MULTIWORD " (" INT ")."
gains_rage_line: MULTIWORD " gains " INT " Rage from " MULTIWORD " 's " MULTIWORD "."
gains_mana_line: MULTIWORD " gains " INT " Mana from " MULTIWORD " 's " MULTIWORD "."
gains_energy_line: MULTIWORD " gains " INT " Energy from " MULTIWORD " 's " MULTIWORD "."
gains_health_line: MULTIWORD " gains " INT " health from " MULTIWORD " 's " MULTIWORD "."
gains_extra_attacks_line: MULTIWORD " gains " INT " extra attack" "s"? " through " MULTIWORD "."

afflicted_line: MULTIWORD " is afflicted by " MULTIWORD " (" INT ")."
timestamp: INT "/" INT " " INT ":" INT ":" INT "." INT
casts_line: MULTIWORD " casts " MULTIWORD (" on " MULTIWORD)? " damaged"? "."
begins_to_cast_line: MULTIWORD " begins to cast " MULTIWORD "."
performs_on_line: MULTIWORD " performs " MULTIWORD " on " MULTIWORD "."
performs_line: MULTIWORD " performs " MULTIWORD "."
begins_to_perform_line: MULTIWORD " begins to perform " MULTIWORD "."

consolidated_line: _CONSOLIDATED (_consolidated_case "{"?)+
combatant_info_line: _COMBATANT_INFO_TOKEN /.+/

hits_ability_line: _hits_ability_line_prefix (" (" vulnerability_suffix)? (" (" resisted_suffix)? (" (" blocked_suffix)? (" (" absorbed_suffix)?
_hits_ability_line_prefix: MULTIWORD " 's " MULTIWORD " " ("hits"|"crits") " " MULTIWORD " for " INT [spell_damage_type] "." glancing_suffix?
hits_autoattack_line: MULTIWORD " " ("hits"|"crits") " " MULTIWORD " for " INT [spell_damage_type] "." glancing_suffix? crushing_suffix? (" (" resisted_suffix)? (" (" blocked_suffix)?  (" (" absorbed_suffix)?




glancing_suffix: (" (glancing)")
resisted_suffix: (INT " resisted)")
absorbed_suffix: (INT " absorbed)")
blocked_suffix: (INT " blocked)")
vulnerability_suffix: "+" INT " vulnerability bonus)"
crushing_suffix: (" (crushing)")
_consolidated_case: consolidated_pet
    | consolidated_loot
    | consolidated_zone
consolidated_pet: "PET: " _CONSOLIDATED_TIMESTAMP MULTIWORD "&" MULTIWORD
consolidated_loot: "LOOT: " _CONSOLIDATED_TIMESTAMP /[^\{\n]+/
consolidated_zone: "ZONE_INFO: " _CONSOLIDATED_TIMESTAMP /[^\{\n]+/


# higher prio terminals for disambiguation. keywords
_COMBATANT_INFO_TOKEN.2: "COMBATANT_INFO: "
_CONSOLIDATED.2: "CONSOLIDATED: "


spell_damage_type: " " /Fire|Frost|Holy|Arcane|Nature|Shadow|Physical/ " damage"

_CONSOLIDATED_TIMESTAMP: INT "." INT "." INT " " INT ":" INT ":" INT "&"

HEAL_CRIT: " critically"

WORD: UCASE_LETTER (LETTER | DIGIT | CONNECTING_APOSTROPHE | CONNECTING_COLON | COMMA)*
PAREN_WORD: "(" WORD ")"
MULTIWORD: WORD ((SPACE | DASH | UNDERSCORE) CONNECTING_WORD)* SELF_DAMAGE? TRAILING_SPACE?
CONNECTING_APOSTROPHE: /(?<! )'/  # allow it only inside a word
CONNECTING_COLON: /(?<! ):/
CONNECTING_WORD: "and"|"with"|"by"|"of"|"to"|"the"|"75B"|"numbing"|"toasted"|"an"|DASH|PAREN_WORD|WORD|/(?<=Lay )on(?= Hands)/

_TS_SEP: SPACE SPACE
SPACE: " "
SELF_DAMAGE: " (self damage)"
TRAILING_SPACE: /(?<! ) (?= )/  # space only if followed by another space and not preceded by another space
DASH: "-"
UNDERSCORE: "_"
COMMA: ","

# https://github.com/lark-parser/lark/blob/master/lark/grammars/common.lark
%import common.INT
%import common.UCASE_LETTER -> UCASE_LETTER
%import common.LETTER -> LETTER
%import common.DIGIT -> DIGIT
%import common.NEWLINE
"""

