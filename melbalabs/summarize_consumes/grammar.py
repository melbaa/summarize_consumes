import lark


parser = lark.Lark(r"""
start: timestamp "  " _line NEWLINE?

_line: gains_consumable_line
    | tea_with_sugar_line
    | rage_consumable_line
    | buff_line
    | dies_line
    | healpot_line
    | manapot_line
    | manarune_line
    | begins_to_cast_consumable_line
    | casts_consumable_line

casts_consumable_line: PLAYER " casts " CASTS_CONSUMABLE (" on " PLAYER)? "."
begins_to_cast_consumable_line: PLAYER " begins to cast " BEGINS_TO_CAST_CONSUMABLE "."
gains_consumable_line: PLAYER " gains " GAINS_CONSUMABLE " (1)."
tea_with_sugar_line: PLAYER " 's Tea with Sugar heals " PLAYER " for " INT "."
rage_consumable_line: PLAYER " gains " INT " Rage from " PLAYER " 's " RAGE_CONSUMABLE "."
buff_line: PLAYER " gains " BUFF_SPELL " (1)."
dies_line: PLAYER " dies."
healpot_line: PLAYER " 's Healing Potion " HEALPOT_CRIT? "heals " PLAYER " for " INT "."
manapot_line: PLAYER " gains " INT " Mana from " PLAYER " 's Restore Mana."
manarune_line: PLAYER " gains " INT " Mana from " PLAYER " 's " MANARUNE_CONSUMABLE "."  # TODO same as above

CASTS_CONSUMABLE: "Powerful Anti-Venom"
    |  "Strong Anti-Venom"
    |  "Cure Ailments"
    |  "Advanced Target Dummy"
BEGINS_TO_CAST_CONSUMABLE: "Brilliant Mana Oil"
    | "Lesser Mana Oil"
    | "Brilliant Wizard Oil"
    | "Blessed Wizard Oil"
    | "Wizard Oil"
    | "Frost Oil"
    | "Shadow Oil"
    | "Dense Dynamite"
    | "Solid Dynamite"
    | "Sharpen Weapon - Critical"
    | "Consecrated Weapon"
    | "Iron Grenade"
    | "Thorium Grenade"
    | "Kreeg's Stout Beatdown"
    | "Fire-toasted Bun"
    | "Sharpen Blade V"
    | "Enhance Blunt Weapon V"
    | "Crystal Force"

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

PLAYER: CNAME

timestamp: INT "/" INT " " INT ":" INT ":" INT "." INT

%import common.INT
%import common.CNAME
%import common.NEWLINE
""",
    parser='lalr',
    # strict=True,
)

