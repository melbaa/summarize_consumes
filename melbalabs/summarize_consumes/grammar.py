import logging


grammar = r"""
start: timestamp "  " _line NEWLINE

_line: gains_consumable_line
    | tea_with_sugar_line
    | rage_consumable_line
    | buff_line
    | dies_line
    | healpot_line
    | manapot_line
    | manarune_line
    | begins_to_cast_line
    | casts_consumable_line
    | consolidated_line
    | combatant_info_line
    | hits_line
    | parry_line
    | resist_line
    | fails_line


timestamp: INT "/" INT " " INT ":" INT ":" INT "." INT
casts_consumable_line: WORD " casts " CASTS_CONSUMABLE (" on " WORD)? "."
begins_to_cast_line: WORD " begins to cast " MULTIWORD "."
gains_consumable_line: WORD " gains " GAINS_CONSUMABLE " (1)."
tea_with_sugar_line: WORD " 's Tea with Sugar heals " WORD " for " INT "."
rage_consumable_line: WORD " gains " INT " Rage from " WORD " 's " RAGE_CONSUMABLE "."
buff_line: WORD " gains " BUFF_SPELL " (1)."
dies_line: WORD " dies."
healpot_line: WORD " 's Healing Potion " HEALPOT_CRIT? "heals " WORD " for " INT "."
manapot_line: WORD " gains " INT " Mana from " WORD " 's Restore Mana."
manarune_line: WORD " gains " INT " Mana from " WORD " 's " MANARUNE_CONSUMABLE "."
consolidated_line: WORD ": " (_consolidated_case "{"?)+
combatant_info_line: _COMBATANT_INFO_TOKEN /.+/
hits_line: WORD " 's " MULTIWORD " " ("hits"|"crits") " " MULTIWORD " for " INT _SPELL_DAMAGE? "." (" (" INT " resisted)")? (" (" INT " absorbed)")?
parry_line: WORD " 's " MULTIWORD " was parried by " MULTIWORD "."
resist_line: WORD " 's " MULTIWORD " was resisted by " MULTIWORD "."
fails_line: WORD " 's " MULTIWORD " fails. " MULTIWORD " is immune."



_consolidated_case: consolidated_pet
    | consolidated_loot
    | consolidated_zone
consolidated_pet: "PET: " _CONSOLIDATED_TIMESTAMP WORD "&" MULTIWORD
consolidated_loot: "LOOT: " _CONSOLIDATED_TIMESTAMP /[^\{\n]+/
consolidated_zone: "ZONE_INFO: " _CONSOLIDATED_TIMESTAMP /[^\{\n]+/


# higher prio terminals
_COMBATANT_INFO_TOKEN.2: "COMBATANT_INFO: "


_SPELL_DAMAGE: " " ("Fire"|"Frost"|"Holy"|"Arcane"|"Nature"|"Shadow") " damage"
_CONSOLIDATED_TIMESTAMP: INT "." INT "." INT " " INT ":" INT ":" INT "&"
CASTS_CONSUMABLE: "Powerful Anti-Venom"
    |  "Strong Anti-Venom"
    |  "Cure Ailments"
    |  "Advanced Target Dummy"
GAINS_CONSUMABLE: "Greater Arcane Elixir"
    | "Arcane Elixir"
    | "Elixir of the Mongoose"
    | "Elixir of the Giants"
    | "Elixir of the Sages"
    | "Elixir of Resistance"
    | "Elixir of Greater Nature Power"
    | "Flask of the Titans"
    | "Supreme Power"
    | "Distilled Wisdom"
    | "Spirit of Zanza"
    | "Swiftness of Zanza"
    | "Sheen of Zanza"
    | "Rage of Ages"
    | "Invulnerability"
    | "Noggenfogger Elixir"
    | "Shadow Power"
    | "Stoneshield"
    | "Health II"
    | "Rumsey Rum Black Label"
    | "Rumsey Rum"
    | "Fury of the Bogling"
    | "Winterfall Firewater"
    | "Greater Agility"
    | "Greater Firepower"
    | "Greater Armor"
    | "Greater Stoneshield"
    | "Fire Power"
    | "Strike of the Scorpok"
    | "Spirit of the Boar"
    | "Free Action"
    | "Blessed Sunfruit"
    | "Gordok Green Grog"
    | "Frost Power"
    | "Gift of Arthas"
    | "100 Energy"  # Restore Energy aka Thistle Tea
    | "Restoration"
    | "Crystal Ward"
    | "Infallible Mind"
    | "Crystal Protection"
    | "Dreamtonic"
    | "Dreamshard Elixir"
    | "Medivh's Merlot"
    # ambiguous
    | "Increased Stamina"
    | "Increased Intellect"
    | "Mana Regeneration"
    | "Regeneration"
    | "Agility"  # pots or scrolls
    | "Strength"
    | "Stamina"
    | "Enlarge"
    | "Greater Intellect"
    | "Greater Armor"
  # |  "Armor",  # same as a spell?
    # protections
    | "Fire Protection"
    | "Frost Protection"
    | "Arcane Protection"
    # extra space here because there's a spell version with no space, which shouldn't match
    | "Nature Protection "
    | "Shadow Protection "
    | "Holy Protection "
MANARUNE_CONSUMABLE: "Demonic Rune"
    | "Dark Rune"
HEALPOT_CRIT: "critically "
BUFF_SPELL: "Greater Blessing of Wisdom"
    | "Greater Blessing of Salvation"
    | "Greater Blessing of Light"
    | "Greater Blessing of Kings"
    | "Greater Blessing of Might"
    | "Prayer of Spirit"
    | "Prayer of Fortitude"
    | "Prayer of Shadow Protection"
RAGE_CONSUMABLE: "Mighty Rage"
    | "Great Rage"
    | "Rage"

WORD: UCASE_LETTER (LETTER | DIGIT | CONNECTING_APOSTROPHE)*
MULTIWORD: WORD ((SPACE | DASH) CONNECTING_WORD)*
CONNECTING_APOSTROPHE: /(?<! )'/  # allow it only inside a word
CONNECTING_WORD: "of"|"the"|WORD

_TS_SEP: SPACE SPACE
SPACE: " "
DASH: "-"

# https://github.com/lark-parser/lark/blob/master/lark/grammars/common.lark
%import common.INT
%import common.UCASE_LETTER -> UCASE_LETTER
%import common.LETTER -> LETTER
%import common.DIGIT -> DIGIT
%import common.NEWLINE
"""

