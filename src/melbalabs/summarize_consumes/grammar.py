grammar = r"""
start: timestamp "  " _line NEWLINE


_line: gains_line
    | gains_rage_line
    | gains_mana_line
    | drains_mana_line
    | drains_mana_line2
    | gains_energy_line
    | gains_health_line
    | gains_extra_attacks_line
    | uses_line
    | uses_line2
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




uses_line: multiword " uses " multiword (" on " multiword)? "."
uses_line2: multiword " uses " "Danonzo" " 's " multiword "."

equipped_durability_loss: multiword " 's equipped items suffer a 10% durability loss."

causes_damage_line: multiword " 's " multiword " causes " multiword " " INT " damage."

fails_to_dispel_line: multiword " fails to dispel " multiword " 's " multiword "."

is_reflected_back_line: multiword " 's " multiword " is reflected back by " multiword "."

is_destroyed_line: multiword " is destroyed."

interrupts_line: multiword " interrupts " multiword " 's " multiword "."

slays_line: multiword " slays " multiword "!"

none_line: "NONE"

falls_line: multiword " falls and loses " INT " health."
lava_line: multiword " loses " INT " health for swimming in lava." RESISTED_SUFFIX? ABSORBED_SUFFIX?

reflects_damage_line: multiword " reflects " INT spell_damage_type " to " multiword "."

creates_line: multiword " creates " multiword "."

suffers_line_nosource: " points of fire damage"
suffers_line_source: spell_damage_type " from " multiword " 's " multiword
suffers_line: multiword " suffers " INT (suffers_line_nosource | suffers_line_source) "." VULNERABILITY_SUFFIX? RESISTED_SUFFIX? ABSORBED_SUFFIX?

fades_line: multiword " fades from " multiword "."

removed_line: multiword " 's " multiword " is removed."

dies_line: multiword " dies."
is_killed_line: multiword " is killed by " multiword "."
slain_line: multiword " is slain by " multiword ("." | "!")

is_dismissed_line: multiword " 's " multiword " is dismissed."
is_dismissed_line2: multiword " is dismissed."
gains_happiness_line: multiword " gains " INT " Happiness from " multiword " 's Feed Pet Effect."
pet_begins_eating_line: multiword " pet begins eating a " multiword "."
block_ability_line: multiword " 's " multiword " was blocked by " multiword "."
block_line: multiword " attacks. " multiword " blocks."
parry_ability_line: multiword " 's " multiword " was parried by " multiword "."
parry_line: multiword " attacks. " multiword " parries."
dodges_line: multiword " attacks. " multiword " dodges."
dodge_ability_line: multiword " 's " multiword " was dodged by " multiword "."
misses_line: multiword " misses " multiword "."
misses_ability_line: multiword " 's " multiword (" missed "|" misses ") multiword "."
resist_line: multiword " 's " multiword " was resisted by " multiword "."
immune_ability_line: multiword " 's " multiword " fails. " multiword " is immune."
immune_line: multiword " attacks but " multiword " is immune."
is_immune_ability_line: multiword " is immune to " multiword " 's " multiword "."
is_absorbed_ability_line: multiword " 's " multiword " is absorbed by " multiword "."
absorbs_ability_line: multiword " absorbs " multiword " 's " multiword "."
absorbs_all_line: multiword " attacks. " multiword " absorbs all the damage."
was_evaded_line: multiword " 's " multiword " was evaded by " multiword "."

heals_line: multiword " 's " multiword HEAL_CRIT? " heals " multiword " for " INT "."

gains_line: multiword " gains " multiword PARENS_INT "."
gains_rage_line: multiword " gains " INT " Rage from " multiword " 's " multiword "."
gains_mana_line: multiword " gains " INT " Mana from " multiword " 's " multiword "."
drains_mana_line: multiword " 's " multiword " drains " INT " Mana from " multiword "." " " multiword " gains " INT " Mana."
drains_mana_line2: multiword " 's " multiword " drains " INT " Mana from " multiword "."
gains_energy_line: multiword " gains " INT " Energy from " multiword " 's " multiword "."
gains_health_line: multiword " gains " INT " health from " multiword " 's " multiword "."
gains_extra_attacks_line: multiword " gains " INT " extra attack" "s"? " through " multiword "."

afflicted_line: multiword " is afflicted by " multiword PARENS_INT "."
casts_line: multiword " casts " multiword (" on " multiword)? " damaged"? "."
begins_to_cast_line: multiword " begins to cast " multiword "."
performs_on_line: multiword " performs " multiword " on " multiword "."
performs_line: multiword " performs " multiword "."
begins_to_perform_line: multiword " begins to perform " multiword "."

consolidated_line: _CONSOLIDATED (_consolidated_case "{"?)+
combatant_info_line: _COMBATANT_INFO_TOKEN /.+/

hits_ability_line: _hits_ability_line_prefix VULNERABILITY_SUFFIX? RESISTED_SUFFIX? BLOCKED_SUFFIX? ABSORBED_SUFFIX?
_hits_ability_line_prefix: multiword " 's " multiword " " ("hits"|"crits") " " multiword " for " INT [spell_damage_type] "." glancing_suffix?
hits_autoattack_line: multiword " " ("hits"|"crits") " " multiword " for " INT [spell_damage_type] "." glancing_suffix? VULNERABILITY_SUFFIX? crushing_suffix? RESISTED_SUFFIX? BLOCKED_SUFFIX? ABSORBED_SUFFIX?


timestamp: INT "/" INT " " INT ":" INT ":" INT "." INT

glancing_suffix: " (glancing)"
RESISTED_SUFFIX: SPACE_LPAREN INT " resisted)"
ABSORBED_SUFFIX: SPACE_LPAREN INT " absorbed)"
BLOCKED_SUFFIX: SPACE_LPAREN INT " blocked)"
VULNERABILITY_SUFFIX: " (+" INT " vulnerability bonus)"
crushing_suffix: " (crushing)"
_consolidated_case: consolidated_pet
    | consolidated_loot
    | consolidated_zone
consolidated_pet: "PET: " _CONSOLIDATED_TIMESTAMP multiword "&" multiword
consolidated_loot: "LOOT: " _CONSOLIDATED_TIMESTAMP /[^\{\n]+/
consolidated_zone: "ZONE_INFO: " _CONSOLIDATED_TIMESTAMP /[^\{\n]+/



# higher prio terminals for disambiguation. keywords
_COMBATANT_INFO_TOKEN.2: "COMBATANT_INFO: "
_CONSOLIDATED.2: "CONSOLIDATED: "

spell_damage_type: " " /Fire|Frost|Holy|Arcane|Nature|Shadow|Physical/ " damage"

_CONSOLIDATED_TIMESTAMP: INT "." INT "." INT " " INT ":" INT ":" INT "&"

HEAL_CRIT: " critically"

multiword: MULTIWORD _paren_word?
_paren_word: SPACE_LPAREN MULTIWORD RPAREN

WORD: UCASE_LETTER (LETTER | DIGIT | CONNECTING_APOSTROPHE | CONNECTING_COLON | COMMA | SLASH)*
MULTIWORD: WORD ((SPACE | DASH | UNDERSCORE) CONNECTING_WORD)* SELF_DAMAGE? TRAILING_SPACE?
CONNECTING_APOSTROPHE: /(?<! )'/  # allow it only inside a word
CONNECTING_COLON: /(?<! ):/
CONNECTING_WORD: "and"|"with"|"by"|"of"|"to"|"the"|"75B"|"numbing"|"toasted"|"an"|DASH|WORD
    |/(?<=Lay )on(?= Hands)/
    |/(?<=Mark )for(?= Death)/
    |/(?<=Taste )for(?= Blood)/
    |/(?<=Thirst )for(?= Blood)/

SPACE: " "
SELF_DAMAGE: " (self damage)"
TRAILING_SPACE: /(?<! ) (?= )/  # space only if followed by another space and not preceded by another space
DASH: "-"
UNDERSCORE: "_"
COMMA: ","
SLASH: "/"
SPACE_LPAREN: " ("
RPAREN: ")"
PARENS_INT: SPACE_LPAREN INT RPAREN

# https://github.com/lark-parser/lark/blob/master/lark/grammars/common.lark
%import common.INT
%import common.UCASE_LETTER -> UCASE_LETTER
%import common.LETTER -> LETTER
%import common.DIGIT -> DIGIT
%import common.NEWLINE
"""



