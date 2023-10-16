from pyparsing import Word
from pyparsing import nums
from pyparsing import alphanums
from pyparsing import Group
from pyparsing import Literal
from pyparsing import White
from pyparsing import Regex
from pyparsing import Combine
from pyparsing import ParseException

# from pyparsing import ParserElement
# ParserElement.enable_packrat()


def parse_line(expr, line):
    try:
        return expr.parse_string(line, parse_all=True)
    except ParseException:
        return None


# log_ts = (Word(nums) + '/' + Word(nums) + Word(nums) + ':' + Word(nums) + ':' + Word(nums) + '.' + Word(nums))("log_ts")
month, day, hour, minute, sec, ms = "\d+", "\d+", "\d+", "\d+", "\d+", "\d+"
log_ts = Regex(fr"{month}/{day} {hour}:{minute}:{sec}\.{ms}")("log_ts")

# players have no spaces in their name
name = Word(alphanums)("name")
anon = Word(alphanums)

rage_pot = (Literal('Mighty Rage') | 'Great Rage' | 'Rage')("rage_pot")
rage_line = log_ts + name + 'gains' + Word(nums) + "Rage from" + anon + "'s" + rage_pot + '.'

tea_with_sugar_line = log_ts + name + "'s Tea with Sugar heals" + anon + 'for' + Word(nums) + '.'

gains_consumable = (
    Literal("Greater Arcane Elixir")
    | 'Arcane Elixir'
    | 'Elixir of the Mongoose'
    | 'Elixir of the Giants'
    | 'Flask of the Titans'
    | 'Supreme Power'
    | 'Distilled Wisdom'
    | 'Spirit of Zanza'
    | 'Swiftness of Zanza'
    | 'Sheen of Zanza'
    | 'Rage of Ages'
    | 'Invulnerability'
    | 'Noggenfogger Elixir'
    | 'Shadow Power'
    | 'Greater Stoneshield'
    | 'Stoneshield'
    | 'Health II'
    | 'Rumsey Rum Black Label'
    | 'Rumsey Rum'
    | 'Fury of the Bogling'
    | 'Winterfall Firewater'
    | 'Greater Agility'
    | 'Elixir of the Sages'
    | 'Greater Firepower'
    | 'Fire Power'
    | 'Strike of the Scorpok'
    | 'Spirit of the Boar'
    | 'Greater Armor'
    | 'Free Action'
    | 'Blessed Sunfruit'
    | 'Elixir of Resistance'
    | 'Gordok Green Grog'
    | 'Frost Power'
    | 'Gift of Arthas'
    | '100 Energy'  # Restore Energy aka Thistle Tea
    | 'Restoration'
    | 'Crystal Ward'
    | 'Infallible Mind'
    | 'Crystal Protection'
    | 'Dreamtonic'
    | 'Dreamshard Elixir'
    | "Medivh's Merlot"
    | "Elixir of Greater Nature Power"

    # ambiguous
    | 'Increased Stamina'
    | 'Increased Intellect'
    | 'Mana Regeneration'
    | 'Regeneration'
    | 'Agility'  # pots or scrolls
    | 'Strength'
    | 'Stamina'
    | 'Enlarge'
    | 'Greater Intellect'
    | 'Greater Armor'
   # |  'Armor',  # same as a spell?

    # extra space here because there's a spell version with no space, which shouldn't match
    | 'Nature Protection '
    | 'Shadow Protection '
    | 'Holy Protection '

    | 'Fire Protection'
    | 'Frost Protection'
    | 'Arcane Protection'
)("consumable")
gains_consumable_line = (log_ts + name + 'gains' + gains_consumable
    + White(' ')  # insist on having at least 1 space here always
    + '(1).'
)

