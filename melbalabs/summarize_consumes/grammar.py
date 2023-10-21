import logging


grammar = r"""
start: timestamp "  " _line NEWLINE

_line: gains_line
    | tea_with_sugar_line
    | rage_consumable_line
    | dies_line
    | healpot_line
    | manapot_line
    | manarune_line
    | begins_to_cast_line
    | casts_line
    | consolidated_line
    | combatant_info_line
    | hits_line
    | parry_line
    | resist_line
    | fails_line
    | afflicted_line
    | is_absorbed_line
    | absorbs_line
    | removed_line
    | suffers_line


suffers_line: MULTIWORD " suffers " INT _SPELL_DAMAGE " from " MULTIWORD " 's " MULTIWORD "." (" (" INT " resisted)")? (" (" INT " absorbed)")?

removed_line: MULTIWORD " 's " MULTIWORD " is removed."

dies_line: MULTIWORD " dies."

parry_line: MULTIWORD " 's " MULTIWORD " was parried by " MULTIWORD "."
resist_line: MULTIWORD " 's " MULTIWORD " was resisted by " MULTIWORD "."
fails_line: MULTIWORD " 's " MULTIWORD " fails. " MULTIWORD " is immune."
is_absorbed_line: MULTIWORD " 's " MULTIWORD " is absorbed by " MULTIWORD "."
absorbs_line: MULTIWORD " absorbs " MULTIWORD " 's " MULTIWORD "."
tea_with_sugar_line: MULTIWORD " 's Tea with Sugar heals " MULTIWORD " for " INT "."
healpot_line: MULTIWORD " 's Healing Potion " HEALPOT_CRIT? "heals " MULTIWORD " for " INT "."

gains_line: MULTIWORD " gains " MULTIWORD " (1)."
rage_consumable_line: MULTIWORD " gains " INT " Rage from " MULTIWORD " 's " RAGE_CONSUMABLE "."

manapot_line: MULTIWORD " gains " INT " Mana from " MULTIWORD " 's Restore Mana."
manarune_line: MULTIWORD " gains " INT " Mana from " MULTIWORD " 's " MANARUNE_CONSUMABLE "."

afflicted_line: MULTIWORD " is afflicted by " MULTIWORD " (1)."
timestamp: INT "/" INT " " INT ":" INT ":" INT "." INT
casts_line: MULTIWORD " casts " MULTIWORD (" on " MULTIWORD)? "."
begins_to_cast_line: MULTIWORD " begins to cast " MULTIWORD "."

consolidated_line: _CONSOLIDATED (_consolidated_case "{"?)+
combatant_info_line: _COMBATANT_INFO_TOKEN /.+/
hits_line: MULTIWORD " 's " MULTIWORD " " ("hits"|"crits") " " MULTIWORD " for " INT _SPELL_DAMAGE? "." (" (" INT " resisted)")? (" (" INT " absorbed)")?




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

MANARUNE_CONSUMABLE: "Demonic Rune"
    | "Dark Rune"
HEALPOT_CRIT: "critically "
RAGE_CONSUMABLE: "Mighty Rage"
    | "Great Rage"
    | "Rage"

WORD: UCASE_LETTER (LETTER | DIGIT | CONNECTING_APOSTROPHE | CONNECTING_COLON)*
MULTIWORD: WORD ((SPACE | DASH | UNDERSCORE) CONNECTING_WORD)* TRAILING_SPACE?
CONNECTING_APOSTROPHE: /(?<! )'/  # allow it only inside a word
CONNECTING_COLON: /(?<! ):/
CONNECTING_WORD: "by"|"of"|"the"|WORD

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

