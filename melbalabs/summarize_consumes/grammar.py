import logging


grammar = r"""
start: timestamp "  " _line NEWLINE

_line: gains_line
    | gains_rage_line
    | gains_mana_line
    | gains_energy_line
    | gains_health_line
    | dies_line
    | begins_to_cast_line
    | casts_line
    | consolidated_line
    | combatant_info_line
    | parry_line
    | resist_line
    | fails_line
    | afflicted_line
    | is_absorbed_line
    | absorbs_line
    | removed_line
    | suffers_line
    | hits_ability_line
    | hits_autoattack_line
    | fades_line
    | slain_line
    | heals_line
    | creates_line
    | is_killed_line



creates_line: MULTIWORD " creates " MULTIWORD "."

suffers_line: MULTIWORD " suffers " INT _SPELL_DAMAGE " from " MULTIWORD " 's " MULTIWORD "." (" (" resisted_suffix)?  (" (" absorbed_suffix)?

fades_line: MULTIWORD " fades from " MULTIWORD "."

removed_line: MULTIWORD " 's " MULTIWORD " is removed."

dies_line: MULTIWORD " dies."
is_killed_line: MULTIWORD " is killed by " MULTIWORD "."
slain_line: MULTIWORD " is slain by " MULTIWORD "!"

parry_line: MULTIWORD " 's " MULTIWORD " was parried by " MULTIWORD "."
resist_line: MULTIWORD " 's " MULTIWORD " was resisted by " MULTIWORD "."
fails_line: MULTIWORD " 's " MULTIWORD " fails. " MULTIWORD " is immune."
is_absorbed_line: MULTIWORD " 's " MULTIWORD " is absorbed by " MULTIWORD "."
absorbs_line: MULTIWORD " absorbs " MULTIWORD " 's " MULTIWORD "."

heals_line: MULTIWORD " 's " MULTIWORD HEAL_CRIT? " heals " MULTIWORD " for " INT "."

gains_line: MULTIWORD " gains " MULTIWORD " (" INT ")."
gains_rage_line: MULTIWORD " gains " INT " Rage from " MULTIWORD " 's " MULTIWORD "."
gains_mana_line: MULTIWORD " gains " INT " Mana from " MULTIWORD " 's " MULTIWORD "."
gains_energy_line: MULTIWORD " gains " INT " Energy from " MULTIWORD " 's " MULTIWORD "."
gains_health_line: MULTIWORD " gains " INT " health from " MULTIWORD " 's " MULTIWORD "."

afflicted_line: MULTIWORD " is afflicted by " MULTIWORD " (" INT ")."
timestamp: INT "/" INT " " INT ":" INT ":" INT "." INT
casts_line: MULTIWORD " casts " MULTIWORD (" on " MULTIWORD)? "."
begins_to_cast_line: MULTIWORD " begins to cast " MULTIWORD "."

consolidated_line: _CONSOLIDATED (_consolidated_case "{"?)+
combatant_info_line: _COMBATANT_INFO_TOKEN /.+/
hits_ability_line: _hits_ability_line_prefix (" (" resisted_suffix)? (" (" blocked_suffix)? (" (" absorbed_suffix)?
_hits_ability_line_prefix: MULTIWORD " 's " MULTIWORD " " ("hits"|"crits") " " MULTIWORD " for " INT _SPELL_DAMAGE? "."
hits_autoattack_line: MULTIWORD " " ("hits"|"crits") " " MULTIWORD " for " INT "." glancing_suffix? (" (" resisted_suffix)? (" (" blocked_suffix)?  (" (" absorbed_suffix)?




glancing_suffix: (" (glancing)")
resisted_suffix: (INT " resisted)")
absorbed_suffix: (INT " absorbed)")
blocked_suffix: (INT " blocked)")
_consolidated_case: consolidated_pet
    | consolidated_loot
    | consolidated_zone
consolidated_pet: "PET: " _CONSOLIDATED_TIMESTAMP MULTIWORD "&" MULTIWORD
consolidated_loot: "LOOT: " _CONSOLIDATED_TIMESTAMP /[^\{\n]+/
consolidated_zone: "ZONE_INFO: " _CONSOLIDATED_TIMESTAMP /[^\{\n]+/


# higher prio terminals for disambiguation. keywords
_COMBATANT_INFO_TOKEN.2: "COMBATANT_INFO: "
_CONSOLIDATED.2: "CONSOLIDATED: "


_SPELL_DAMAGE: " " ("Fire"|"Frost"|"Holy"|"Arcane"|"Nature"|"Shadow"|"Physical") " damage"
_CONSOLIDATED_TIMESTAMP: INT "." INT "." INT " " INT ":" INT ":" INT "&"

HEAL_CRIT: " critically"

WORD: UCASE_LETTER (LETTER | DIGIT | CONNECTING_APOSTROPHE | CONNECTING_COLON)*
PAREN_WORD: "(" WORD ")"
MULTIWORD: WORD ((SPACE | DASH | UNDERSCORE) CONNECTING_WORD)* TRAILING_SPACE?
CONNECTING_APOSTROPHE: /(?<! )'/  # allow it only inside a word
CONNECTING_COLON: /(?<! ):/
CONNECTING_WORD: "with"|"by"|"of"|"the"|PAREN_WORD|WORD

_TS_SEP: SPACE SPACE
SPACE: " "
TRAILING_SPACE: /(?<! ) (?= )/  # space only if followed by another space and not preceded by another space
DASH: "-"
UNDERSCORE: "_"

# https://github.com/lark-parser/lark/blob/master/lark/grammars/common.lark
%import common.INT
%import common.UCASE_LETTER -> UCASE_LETTER
%import common.LETTER -> LETTER
%import common.DIGIT -> DIGIT
%import common.NEWLINE
"""

