from pyparsing import Word
from pyparsing import nums
from pyparsing import alphanums
from pyparsing import Group
from pyparsing import Literal
from pyparsing import ParseException



def parse_line(expr, line):
    try:
        return expr.parse_string(line, parse_all=True)
    except ParseException:
        return None


log_ts = (Word(nums) + '/' + Word(nums) + Word(nums) + ':' + Word(nums) + ':' + Word(nums) + '.' + Word(nums))("logts")

rage_pot = (Literal('Mighty Rage') | 'Great Rage' | 'Rage')("rage_pot")
rage_line = log_ts + Word(alphanums)("name") + 'gains' + Word(nums) + "Rage from" + Word(alphanums) + "'s" + rage_pot + '.'


