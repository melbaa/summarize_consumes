import argparse
import collections
import csv
import dataclasses
import datetime
import functools
import io
import itertools
import json
import logging
import os
import re
import time
import webbrowser
import sys
import zipfile
from datetime import datetime as dt
from enum import Enum
from pathlib import Path
from typing import Dict
from typing import List
from typing import Tuple
from typing import Optional
from uuid import uuid4

import humanize
import requests
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from typing_extensions import Self


from melbalabs.summarize_consumes import grammar
from melbalabs.summarize_consumes.consumable_model import Consumable
from melbalabs.summarize_consumes.consumable_model import SuperwowConsumable
from melbalabs.summarize_consumes.consumable_model import IgnoreStrategy
from melbalabs.summarize_consumes.consumable_model import SafeStrategy
from melbalabs.summarize_consumes.consumable_model import EnhanceStrategy
from melbalabs.summarize_consumes.consumable_model import OverwriteStrategy
from melbalabs.summarize_consumes.consumable_model import DirectPrice
from melbalabs.summarize_consumes.consumable_model import PriceFromComponents
from melbalabs.summarize_consumes.consumable_model import NoPrice
from melbalabs.summarize_consumes.consumable_db import all_defined_consumable_items
import melbalabs.summarize_consumes.package as package


class ParserError(Exception):
    pass


CURRENT_YEAR = datetime.datetime.now().year


class PlayerClass(Enum):
    DRUID = "druid"
    HUNTER = "hunter"
    MAGE = "mage"
    PALADIN = "paladin"
    PRIEST = "priest"
    ROGUE = "rogue"
    SHAMAN = "shaman"
    WARLOCK = "warlock"
    WARRIOR = "warrior"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, class_string: str) -> "PlayerClass":
        # lowercase is the only extra processing. everything else should be an error
        return cls(class_string.lower())


class App:
    pass


class FallbackParser:
    def parse(self, line):
        raise ParserError("unknown line")


@functools.cache
def create_parser(grammar: str, debug, unparsed_logger):
    fallback_parser = FallbackParser()

    return Parser2(fallback_parser=fallback_parser, unparsed_logger=unparsed_logger)


class Token:
    __slots__ = ("type", "value")

    def __init__(self, type_name, value):
        self.type = type_name
        self.value = value

    def __str__(self):
        return self.value

    def __int__(self):
        return int(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.type!r}, {self.value!r})"


class Tree:
    __slots__ = ("data", "children")

    def __init__(self, data, children):
        self.data = data
        self.children = children


class Parser2:
    def __init__(self, fallback_parser, unparsed_logger):
        self.fallback_parser = fallback_parser
        self.excnum = 0
        self.unparsed_logger = unparsed_logger

        # The regex already ensures these are digits, so the isdigit() loop is no longer needed.
        self.TIMESTAMP_PATTERN = re.compile(r"(\d+)/(\d+) (\d+):(\d+):(\d+)\.(\d+)")

        self.timestamp_tokens = [Token("t", "") for _ in range(6)]
        self.timestamp_tree = Tree("timestamp", children=self.timestamp_tokens)

        # shared token cache
        self.name_token = Token("t", "")
        self.mana_token = Token("t", "")
        self.spellname_token = Token("t", "")
        self.damage_token = Token("t", "")
        self.targetname_token = Token("t", "")
        self.stackcount_token = Token("t", "")
        self.spell_damage_type_token = Token("t", "")
        self.heal_amount_token = Token("t", "")
        self.heal_crit_token = Token("HEAL_CRIT", "")

        # gains_mana_line cache
        subtree = Tree(
            data="gains_mana_line",
            children=[self.name_token, self.mana_token, self.spellname_token],
        )
        self.gains_mana_line_tree = Tree(data="line", children=[self.timestamp_tree, subtree])

        # hits_ability_line cache
        subtree = Tree(
            data="hits_ability_line",
            children=[
                self.name_token,
                self.spellname_token,
                self.targetname_token,
                self.damage_token,
                self.spell_damage_type_token,
            ],
        )
        self.hits_ability_line_tree = Tree(data="line", children=[self.timestamp_tree, subtree])

        # hits_autoattack_line cache
        subtree = Tree(
            data="hits_autoattack_line",
            children=[
                self.name_token,
                self.targetname_token,
                self.damage_token,
            ],
        )
        self.hits_autoattack_line_tree = Tree(data="line", children=[self.timestamp_tree, subtree])

        # gains_line cache
        subtree = Tree(
            data="gains_line",
            children=[
                self.name_token,
                self.spellname_token,
                self.stackcount_token,
            ],
        )
        self.gains_line_tree = Tree(data="line", children=[self.timestamp_tree, subtree])

        # heals_line cache
        subtree = Tree(
            data="heals_line",
            children=[
                self.name_token,
                self.spellname_token,
                self.heal_crit_token,
                self.targetname_token,
                self.heal_amount_token,
            ],
        )
        self.heals_line_tree = Tree(data="line", children=[self.timestamp_tree, subtree])

        # fades_line cache
        subtree = Tree(data="fades_line", children=[self.spellname_token, self.targetname_token])
        self.fades_line_tree = Tree(data="line", children=[self.timestamp_tree, subtree])

        # suffers_line cache (WITH source)
        source_subtree = Tree(
            data="suffers_line_source",
            children=[
                self.spell_damage_type_token,
                self.name_token,  # castername
                self.spellname_token,
            ],
        )
        subtree = Tree(
            data="suffers_line", children=[self.targetname_token, self.damage_token, source_subtree]
        )
        self.suffers_line_source_tree = Tree(data="line", children=[self.timestamp_tree, subtree])

        # suffers_line cache (NO source)
        nosource_subtree = Tree(
            data="suffers_line_nosource", children=[self.spell_damage_type_token]
        )
        subtree = Tree(
            data="suffers_line",
            children=[self.targetname_token, self.damage_token, nosource_subtree],
        )
        self.suffers_line_nosource_tree = Tree(data="line", children=[self.timestamp_tree, subtree])

        # begins_to_cast_line cache
        subtree = Tree(data="begins_to_cast_line", children=[self.name_token, self.spellname_token])
        self.begins_to_cast_line_tree = Tree(data="line", children=[self.timestamp_tree, subtree])

        # afflicted_line cache
        subtree = Tree(
            data="afflicted_line",
            children=[self.targetname_token, self.spellname_token],
        )

        self.afflicted_line_tree = Tree(data="line", children=[self.timestamp_tree, subtree])

    def parse_ts(self, line, p_ts_end):
        # 6/1 18:31:36.197  ...

        match = self.TIMESTAMP_PATTERN.match(line)

        if not match:
            raise ValueError("Invalid timestamp format")

        groups = match.groups()
        for i, value in enumerate(groups):
            self.timestamp_tokens[i].value = value

        return self.timestamp_tree

    def parse_consolidated_pet(self, pet_string: str):
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
        return Tree(data="consolidated_pet", children=[Token("t", name), Token("t", petname)])

    def parse(self, line, p_ts_end) -> Optional[Tree]:
        """
        assumes p_ts_end != -1
        throws ValueError when it sees invalid syntax
        """
        try:
            p_mana_from = line.find(" Mana from ", p_ts_end)
            if p_mana_from >= 0:
                # 6/1 18:38:06.514  Oileri gains 39 Mana from Interlani 's Greater Blessing of Wisdom.
                # 6/1 18:31:36.197  Chogup (Freedlock) gains 10 Mana from Clapya 's Mana Spring.

                # Find the start of the constant text ' gains '
                p_gains = line.find(" gains ", p_ts_end)

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
                spellname = line[p_s + 4 : -2]

                _ = self.parse_ts(line, p_ts_end)  # magic cached reference

                self.name_token.value = name  # magic cached reference
                self.mana_token.value = mana  # magic cached reference
                self.spellname_token.value = spellname  # magic cached reference
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
                timestamp = self.parse_ts(line, p_ts_end)
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
                    spellname = line[p_s + 4 : p_action]
                    targetname = line[p_action + len(action_verb) + 2 : p_for]

                    self.name_token.value = name  # magic cached reference
                    self.spellname_token.value = spellname  # magic cached reference
                    self.targetname_token.value = targetname  # magic cached reference
                    self.damage_token.value = damage_amount  # magic cached reference
                    self.spell_damage_type_token.value = damage_type_str  # magic cached reference
                    return self.hits_ability_line_tree  # magic cached reference

                else:  # It's a hits_autoattack_line
                    caster_name = line[p_ts_end + 2 : p_action]
                    target_name = line[p_action + len(action_verb) + 2 : p_for]

                    self.name_token.value = caster_name  # magic cached reference
                    self.targetname_token.value = target_name  # magic cached reference
                    self.damage_token.value = damage_amount  # magic cached reference
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
                timestamp = self.parse_ts(line, p_ts_end)

                # Extract the main variables using anchors.
                caster_name = line[p_ts_end + 2 : p_s]
                spell_name = line[p_s + 4 : p_action]
                target_name = line[p_action + len(action_verb) : p_for]

                p_num_start = p_for + 5
                p_period = line.find(".", p_num_start)
                p_num_end = p_period
                amount = line[p_num_start:p_num_end]

                self.name_token.value = caster_name  # magic cached reference
                self.spellname_token.value = spell_name  # magic cached reference
                self.heal_crit_token.value = crit_token_value  # magic cached reference
                self.targetname_token.value = target_name  # magic cached reference
                self.heal_amount_token.value = amount  # magic cached reference
                return self.heals_line_tree  # magic cached reference

            p_fades = line.find(" fades from ", p_ts_end)

            if p_fades != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # The spellname is between the timestamp and the anchor phrase.
                spellname = line[p_ts_end + 2 : p_fades]

                # The targetname is between the anchor and the final period.
                # 12 is len(' fades from '); -2 is .\n
                targetname = line[p_fades + 12 : -2]

                self.spellname_token.value = spellname  # magic cached reference
                self.targetname_token.value = targetname  # magic cached reference
                return self.fades_line_tree  # magic cached reference

            p_suffers = line.find(" suffers ", p_ts_end)

            if p_suffers != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # Target is always between the timestamp and " suffers ".
                targetname = line[p_ts_end + 2 : p_suffers]

                # Amount is always the first word after " suffers ".
                p_num_start = p_suffers + 9  # len(' suffers ')
                p_num_end = line.find(" ", p_num_start)
                amount = line[p_num_start:p_num_end]

                self.targetname_token.value = targetname  # magic cached reference
                self.damage_token.value = amount  # magic cached reference

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
                            spellname = line[p_s + len(suffix) : p_period]

                            # magic cached reference
                            self.spell_damage_type_token.value = damage_type
                            self.name_token.value = castername  # magic cached reference
                            self.spellname_token.value = spellname  # magic cached reference
                            return self.suffers_line_source_tree  # magic cached reference

                else:
                    # No source is present
                    # In this case, the grammar is "... points of [type] damage."
                    p_points = line.find(" points of ", p_num_end)
                    if p_points != -1:
                        p_damage_word = line.find(" damage.", p_points)

                        damage_type = line[p_points + 11 : p_damage_word]

                        self.spell_damage_type_token.value = damage_type  # magic cached reference
                        return self.suffers_line_nosource_tree  # magic cached reference

            p_gains = line.find(" gains ", p_ts_end)

            # The end of a gains_line is very specific: " (#)."
            p_paren_open = line.rfind(" (", p_gains)
            p_paren_close = line.find(").", p_paren_open)

            if p_gains != -1 and p_paren_open != -1 and p_paren_close != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # The name is between the timestamp and " gains ".
                name = line[p_ts_end + 2 : p_gains]

                # The spellname is between " gains " and the " (".
                # This correctly captures trailing spaces, like in "Shadow Protection  ".
                spellname = line[p_gains + 7 : p_paren_open]  # 7 is len(' gains ')

                # The stackcount is the number between the parentheses.
                stackcount = line[p_paren_open + 2 : p_paren_close]  # +2 skips " ("

                self.name_token.value = name  # magic cached reference
                self.spellname_token.value = spellname  # magic cached reference
                self.stackcount_token.value = stackcount  # magic cached reference
                return self.gains_line_tree

            action_phrase = " begins to cast "
            p_action = line.find(action_phrase, p_ts_end)

            if p_action != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # The caster's name is between the timestamp and the anchor phrase.
                caster_name = line[p_ts_end + 2 : p_action]

                spell_name = line[p_action + len(action_phrase) : -2]

                self.name_token.value = caster_name  # magic cached reference
                self.spellname_token.value = spell_name  # magic cached reference

                return self.begins_to_cast_line_tree  # magic cached reference

            action_phrase = " is afflicted by "
            p_action = line.find(action_phrase, p_ts_end)

            # The line must end with " (#)."
            p_paren_open = line.rfind(" (", p_action)
            p_paren_close = line.find(").", p_paren_open)

            # If all anchors are found in the correct order, we have a match.
            if p_action != -1 and p_paren_open != -1 and p_paren_close != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # The targetname is between the timestamp and the action phrase.
                targetname = line[p_ts_end + 2 : p_action]

                # The spellname is everything between the action phrase and the final " (#)".
                spellname = line[p_action + len(action_phrase) : p_paren_open]

                self.targetname_token.value = targetname  # magic cached reference
                self.spellname_token.value = spellname  # magic cached reference
                return self.afflicted_line_tree  # magic cached reference

            p_casts = line.find(" casts ", p_ts_end)

            if p_casts != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # Caster is always present and in the same spot.
                caster_name = line[p_ts_end + 2 : p_casts]

                # Now we determine the structure based on the optional parts.
                p_on = line.find(" on ", p_casts)

                spell_name = None
                target_name = None

                if p_on != -1:
                    # A target is present
                    # The spell is between " casts " and " on ".
                    spell_name = line[p_casts + 7 : p_on]  # 7 is len(' casts ')

                    # Now check if the special "damaged" case exists.
                    # The "damaged" phrase replaces the final period.
                    p_damaged = line.find(" damaged.", p_casts)
                    if p_damaged != -1 and line.find(":", p_on) != -1:
                        # For "on Target: ... damaged.", the target is between " on " and ":".
                        p_colon = line.find(":", p_on)
                        target_name = line[p_on + 4 : p_colon]  # 4 is len(' on ')
                    else:
                        # For "on Target.", the target is between " on " and the end.
                        target_name = line[p_on + 4 : -2]

                else:
                    # No target is present
                    # The spell is everything after " casts " to the end.
                    spell_name = line[p_casts + 7 : -2]

                children = [Token("t", caster_name), Token("t", spell_name)]
                if target_name:
                    children.append(Token("t", target_name))

                subtree = Tree(data="casts_line", children=children)

                return Tree(data="line", children=[timestamp, subtree])

            # already have this
            # p_gains = line.find(' gains ', p_ts_end)

            # We will find the anchors in order.
            p_extra = line.find(" extra attack", p_gains)  # Note: no 's' here
            p_through = line.find(" through ", p_extra)

            # If all three anchors are found in a valid sequence...
            if p_gains != -1 and p_extra != -1 and p_through != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # The name is between the timestamp and " gains ".
                name = line[p_ts_end + 2 : p_gains]

                # The number of attacks is between " gains " and " extra attack".
                howmany = line[p_gains + 7 : p_extra]  # 7 is len(' gains ')

                # The source is everything after " through " to the end.
                source = line[p_through + 9 : -2]  # 9 is len(' through ')

                # Construct the tree exactly as the consumer expects.
                subtree = Tree(
                    data="gains_extra_attacks_line",
                    children=[Token("t", name), Token("t", howmany), Token("t", source)],
                )

                return Tree(data="line", children=[timestamp, subtree])

            # already have this
            # p_gains = line.find(' gains ', p_ts_end)
            p_rage_from = line.find(" Rage from ", p_gains)
            p_s = line.find(" 's ", p_rage_from)

            # If all anchors are found, we have a match.
            if p_gains != -1 and p_rage_from != -1 and p_s != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # Slice out the 4 required pieces of data.
                recipient_name = line[p_ts_end + 2 : p_gains]
                rage_amount = line[p_gains + 7 : p_rage_from]  # len(' gains ') == 7
                caster_name = line[p_rage_from + 11 : p_s]  # len(' Rage from ') == 11

                # Spell name is from after " 's " to the final period.
                # Using rfind('.') is robust against spells with periods in their name.
                p_period = line.rfind(".", p_s)
                spell_name = line[p_s + 4 : p_period]  # len(" 's ") == 4

                # Construct the tree with 4 children, as expected by the consumer.
                subtree = Tree(
                    data="gains_rage_line",
                    children=[
                        Token("t", recipient_name),
                        Token("t", rage_amount),
                        Token("t", caster_name),
                        Token("t", spell_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            # already have this
            # p_gains = line.find(' gains ', p_ts_end)
            p_health_from = line.find(" health from ", p_gains)  # The only changed anchor
            p_s = line.find(" 's ", p_health_from)

            # If all anchors are found, we have a match.
            if p_gains != -1 and p_health_from != -1 and p_s != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # Slice out the 4 required pieces of data.
                target_name = line[p_ts_end + 2 : p_gains]
                health_amount = line[p_gains + 7 : p_health_from]  # len(' gains ') == 7
                caster_name = line[p_health_from + 13 : p_s]  # len(' health from ') == 13

                p_period = line.rfind(".", p_s)
                spell_name = line[p_s + 4 : p_period]  # len(" 's ") == 4

                # Construct the tree with 4 children, as expected by the consumer.
                subtree = Tree(
                    data="gains_health_line",
                    children=[
                        Token("t", target_name),
                        Token("t", health_amount),
                        Token("t", caster_name),
                        Token("t", spell_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            # already have this
            # p_gains = line.find(' gains ', p_ts_end)
            p_energy_from = line.find(" Energy from ", p_gains)  # The only changed anchor
            p_s = line.find(" 's ", p_energy_from)

            # If all anchors are found, we have a match.
            if p_gains != -1 and p_energy_from != -1 and p_s != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # Slice out the 4 required pieces of data.
                recipient_name = line[p_ts_end + 2 : p_gains]
                energy_amount = line[p_gains + 7 : p_energy_from]  # len(' gains ') == 7
                caster_name = line[p_energy_from + 13 : p_s]  # len(' Energy from ') == 13

                p_period = line.rfind(".", p_s)
                spell_name = line[p_s + 4 : p_period]  # len(" 's ") == 4

                # Construct the tree with 4 children, as expected.
                subtree = Tree(
                    data="gains_energy_line",
                    children=[
                        Token("t", recipient_name),
                        Token("t", energy_amount),
                        Token("t", caster_name),
                        Token("t", spell_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            p_s = line.find(" 's ", p_ts_end)
            p_resisted = line.find(" was resisted by ", p_s)

            # If both anchors are found, we have a match.
            if p_s != -1 and p_resisted != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # Slice out the 3 required pieces of data from between the anchors.
                caster_name = line[p_ts_end + 2 : p_s]
                spell_name = line[p_s + 4 : p_resisted]

                target_name = line[p_resisted + 17 : -2]  # 17 is len(' was resisted by ')

                # Construct the tree with 3 children, as expected by the consumer.
                subtree = Tree(
                    data="resist_line",
                    children=[
                        Token("t", caster_name),
                        Token("t", spell_name),
                        Token("t", target_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            p_uses = line.find(" uses ", p_ts_end)

            if p_uses != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # The user's name is always present.
                user_name = line[p_ts_end + 2 : p_uses]

                # Check for the optional target part.
                p_on = line.find(" on ", p_uses)

                spell_name = None
                target_name = None

                if p_on != -1:
                    # PATTERN WITH A TARGET
                    # The item/spell name is between " uses " and " on ".
                    spell_name = line[p_uses + 6 : p_on]  # 6 is len(' uses ')

                    # The target name is after " on " to the end of the line.
                    target_name = line[p_on + 4 : -2]  # 4 is len(' on ')
                else:
                    # PATTERN WITHOUT A TARGET
                    # The item/spell name is simply everything after " uses ".
                    spell_name = line[p_uses + 6 : -2]

                # Build the tree with 2 or 3 children depending on what was found.
                children = [Token("t", user_name), Token("t", spell_name)]
                if target_name:
                    children.append(Token("t", target_name))

                subtree = Tree(data="uses_line", children=children)

                return Tree(data="line", children=[timestamp, subtree])

            anchor1 = " attacks. "
            anchor2 = " dodges."

            # Find the position of both anchors sequentially.
            p_anchor1 = line.find(anchor1, p_ts_end)
            p_anchor2 = line.find(anchor2, p_anchor1)  # Start search after the first anchor

            # If both anchors were found in the correct order, we have a match.
            if p_anchor1 != -1 and p_anchor2 != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # The attacker is between the timestamp and the first anchor.
                attacker = line[p_ts_end + 2 : p_anchor1]

                # The dodger is between the first anchor and the second anchor.
                dodger_start = p_anchor1 + len(anchor1)
                dodger = line[dodger_start:p_anchor2]

                subtree = Tree(
                    data="dodges_line", children=[Token("t", attacker), Token("t", dodger)]
                )

                return Tree(data="line", children=[timestamp, subtree])

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
                    timestamp = self.parse_ts(line, p_ts_end)

                    caster_name = line[p_ts_end + 2 : p_s]
                    spell_name = line[p_s + 4 : p_verb]
                    target_name = line[p_verb + verb_len : -2]

                    subtree = Tree(
                        data="misses_ability_line",
                        children=[
                            Token("t", caster_name),
                            Token("t", spell_name),
                            Token("t", target_name),
                        ],
                    )
                    return Tree(data="line", children=[timestamp, subtree])

            else:
                # misses_line
                # If 's is NOT present, it can only be a simple miss.
                p_misses = line.find(" misses ", p_ts_end)
                if p_misses != -1:
                    timestamp = self.parse_ts(line, p_ts_end)

                    attacker = line[p_ts_end + 2 : p_misses]
                    target = line[p_misses + 8 : -2]  # len(' misses ')

                    subtree = Tree(
                        data="misses_line", children=[Token("t", attacker), Token("t", target)]
                    )
                    return Tree(data="line", children=[timestamp, subtree])

            anchor = " dies.\n"

            # Since we know the exact ending, we can use a single, highly efficient check.
            if line.endswith(anchor):
                timestamp = self.parse_ts(line, p_ts_end)

                # The name is between the timestamp and the start of our known suffix.
                # The slice end is -len(anchor) to remove " dies.\n"
                name_start = p_ts_end + 2
                name_end = -len(anchor)
                name = line[name_start:name_end]

                # Construct the simple one-child tree.
                subtree = Tree(data="dies_line", children=[Token("t", name)])

                return Tree(data="line", children=[timestamp, subtree])

            parries_anchor = " parries.\n"

            # Use a single, fast check to identify the line type.
            if line.endswith(parries_anchor):
                # Now that we know the line type, find the middle anchor.
                middle_anchor = " attacks. "
                p_attacks = line.find(middle_anchor, p_ts_end)

                if p_attacks != -1:
                    timestamp = self.parse_ts(line, p_ts_end)

                    # The attacker is between the timestamp and the middle anchor.
                    attacker = line[p_ts_end + 2 : p_attacks]

                    # The parrier is between the middle anchor and the final anchor.
                    # We can slice precisely using the lengths of our known strings.
                    parrier_start = p_attacks + len(middle_anchor)
                    parrier_end = -len(parries_anchor)
                    parrier = line[parrier_start:parrier_end]

                    # Construct the simple two-child tree.
                    subtree = Tree(
                        data="parry_line", children=[Token("t", attacker), Token("t", parrier)]
                    )

                    return Tree(data="line", children=[timestamp, subtree])

            # Find all the anchors in sequential order.
            p_reflects = line.find(" reflects ", p_ts_end)
            p_damage_to = line.find(" damage to ", p_reflects)  # Changed anchor name for clarity

            # If both anchors are found, we have a match.
            if p_reflects != -1 and p_damage_to != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # --- Slice out the 4 required pieces of data ---
                reflector_name = line[p_ts_end + 2 : p_reflects]

                middle_part_start = p_reflects + 10  # len(' reflects ')
                p_space_in_middle = line.find(" ", middle_part_start)

                amount = line[middle_part_start:p_space_in_middle]
                damage_type = line[p_space_in_middle + 1 : p_damage_to]

                # The target name is after the second anchor, with the final ".\n" removed.
                target_start = p_damage_to + 11  # len(' damage to ')
                target_end = -2  # Removes exactly ".\n"
                target_name = line[target_start:target_end]

                # Construct the tree with 4 children, as expected by the consumer.
                subtree = Tree(
                    data="reflects_damage_line",
                    children=[
                        Token("t", reflector_name),
                        Token("t", amount),
                        Token("t", damage_type),
                        Token("t", target_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            action_phrase = " begins to perform "
            p_action = line.find(action_phrase, p_ts_end)

            if p_action != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # The performer's name is between the timestamp and the anchor phrase.
                performer_name = line[p_ts_end + 2 : p_action]

                # The action name is after the anchor, with the final ".\n" removed.
                action_start = p_action + len(action_phrase)
                action_end = -2  # Removes exactly ".\n"
                action_name = line[action_start:action_end]

                # Construct the simple two-child tree.
                subtree = Tree(
                    data="begins_to_perform_line",
                    children=[Token("t", performer_name), Token("t", action_name)],
                )

                return Tree(data="line", children=[timestamp, subtree])

            # Find the two key anchors in sequential order.
            p_s = line.find(" 's ", p_ts_end)
            p_dodged = line.find(" was dodged by ", p_s)

            # If both anchors are found, we have a match.
            if p_s != -1 and p_dodged != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # Slice out the 3 required pieces of data from between the anchors.
                caster_name = line[p_ts_end + 2 : p_s]
                spell_name = line[p_s + 4 : p_dodged]

                # Target name is after the second anchor, with ".\n" removed.
                target_start = p_dodged + 15  # len(' was dodged by ')
                target_end = -2  # Removes exactly ".\n"
                target_name = line[target_start:target_end]

                # Construct the tree with 3 children.
                subtree = Tree(
                    data="dodge_ability_line",
                    children=[
                        Token("t", caster_name),
                        Token("t", spell_name),
                        Token("t", target_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            p_s = line.find(" 's ", p_ts_end)
            p_causes = line.find(" causes ", p_s)

            # The line must end with " damage.\n"
            final_anchor = " damage.\n"
            if p_s != -1 and p_causes != -1 and line.endswith(final_anchor):
                timestamp = self.parse_ts(line, p_ts_end)

                caster_name = line[p_ts_end + 2 : p_s]
                spell_name = line[p_s + 4 : p_causes]

                # To separate the target from the amount, we find the last space
                # before the final anchor " damage.".
                p_damage_word = line.rfind(" damage.", p_causes)
                p_last_space = line.rfind(" ", p_causes, p_damage_word)

                # 3. Target Name & 4. Amount can now be sliced.
                target_name = line[p_causes + 8 : p_last_space]  # len(' causes ')
                amount = line[p_last_space + 1 : p_damage_word]

                subtree = Tree(
                    data="causes_damage_line",
                    children=[
                        Token("t", caster_name),
                        Token("t", spell_name),
                        Token("t", target_name),
                        Token("t", amount),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            final_anchor = " is removed.\n"

            # We can validate the line with a single, fast check.
            if line.endswith(final_anchor):
                # If it ends correctly, now find the 's anchor.
                p_s = line.find(" 's ", p_ts_end)

                if p_s != -1:
                    timestamp = self.parse_ts(line, p_ts_end)

                    # The caster name is between the timestamp and 's.
                    caster_name = line[p_ts_end + 2 : p_s]

                    # The spell name is between 's and the final anchor.
                    spell_start = p_s + 4  # len(" 's ")
                    # Use rfind to get the start of the final anchor for a clean slice.
                    p_removed = line.rfind(" is removed.")
                    spell_name = line[spell_start:p_removed]

                    # Construct the simple two-child tree.
                    subtree = Tree(
                        data="removed_line",
                        children=[Token("t", caster_name), Token("t", spell_name)],
                    )

                    return Tree(data="line", children=[timestamp, subtree])

            anchor1 = " 's "
            anchor2 = " fails. "
            final_anchor = " is immune.\n"

            if line.endswith(final_anchor):
                p_anchor1 = line.find(anchor1, p_ts_end)
                p_anchor2 = line.find(anchor2, p_anchor1)

                if p_anchor1 != -1 and p_anchor2 != -1:
                    timestamp = self.parse_ts(line, p_ts_end)

                    caster_name = line[p_ts_end + 2 : p_anchor1]
                    spell_name = line[p_anchor1 + len(anchor1) : p_anchor2]

                    target_start = p_anchor2 + len(anchor2)
                    target_end = -len(final_anchor)
                    target_name = line[target_start:target_end]

                    subtree = Tree(
                        data="immune_ability_line",
                        children=[
                            Token("t", caster_name),
                            Token("t", spell_name),
                            Token("t", target_name),
                        ],
                    )

                    return Tree(data="line", children=[timestamp, subtree])

            # Find the two key anchors in sequential order.
            p_s = line.find(" 's ", p_ts_end)
            p_parried = line.find(" was parried by ", p_s)

            # If both anchors are found, we have a match.
            if p_s != -1 and p_parried != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                # Slice out the 3 required pieces of data from between the anchors.
                caster_name = line[p_ts_end + 2 : p_s]
                spell_name = line[p_s + 4 : p_parried]

                # Target name is after the second anchor, with ".\n" removed.
                target_start = p_parried + 16  # len(' was parried by ')
                target_end = -2  # Removes exactly ".\n"
                target_name = line[target_start:target_end]

                subtree = Tree(
                    data="parry_ability_line",
                    children=[
                        Token("t", caster_name),
                        Token("t", spell_name),
                        Token("t", target_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            middle_anchor = " attacks but "
            final_anchor_with_newline = " is immune.\n"

            # First, use a fast check to see if the line ends correctly.
            if line.endswith(final_anchor_with_newline):
                # If it does, find the middle anchor.
                p_middle = line.find(middle_anchor, p_ts_end)

                if p_middle != -1:
                    # We have a confirmed match.
                    timestamp = self.parse_ts(line, p_ts_end)

                    # The attacker is between the timestamp and the middle anchor.
                    attacker = line[p_ts_end + 2 : p_middle]

                    # The target is between the middle anchor and the final anchor.
                    # We can slice precisely using the lengths of our known strings.
                    target_start = p_middle + len(middle_anchor)
                    target_end = -len(final_anchor_with_newline)
                    target = line[target_start:target_end]

                    subtree = Tree(
                        data="immune_line", children=[Token("t", attacker), Token("t", target)]
                    )

                    return Tree(data="line", children=[timestamp, subtree])

            p_performs = line.find(" performs ", p_ts_end)

            if p_performs != -1:
                # A "performs" action was found. Now check for the "on" to disambiguate.
                p_on = line.find(" on ", p_performs)

                if p_on != -1:
                    # performs_on_line (most specific)
                    timestamp = self.parse_ts(line, p_ts_end)

                    performer = line[p_ts_end + 2 : p_performs]
                    spellname = line[p_performs + 10 : p_on]  # len(' performs ')
                    targetname = line[p_on + 4 : -2]  # len(' on '), removes ".\n"

                    subtree = Tree(
                        data="performs_on_line",
                        children=[
                            Token("t", performer),
                            Token("t", spellname),
                            Token("t", targetname),
                        ],
                    )
                    return Tree(data="line", children=[timestamp, subtree])

                else:
                    # performs_line (less specific, potentially dangerous)
                    # We only get here if " performs " was found, but " on " was NOT.
                    # very possible this matches a different line type someday
                    timestamp = self.parse_ts(line, p_ts_end)

                    performer = line[p_ts_end + 2 : p_performs]
                    spellname = line[p_performs + 10 : -2]  # len(' performs '), removes ".\n"

                    subtree = Tree(
                        data="performs_line",
                        children=[Token("t", performer), Token("t", spellname)],
                    )
                    return Tree(data="line", children=[timestamp, subtree])

            middle_anchor = " falls and loses "
            final_anchor_with_newline = " health.\n"

            # Use a fast check on the line's ending to pre-filter.
            if line.endswith(final_anchor_with_newline):
                # If the end matches, now find the middle anchor.
                p_middle = line.find(middle_anchor, p_ts_end)

                if p_middle != -1:
                    timestamp = self.parse_ts(line, p_ts_end)

                    name = line[p_ts_end + 2 : p_middle]

                    amount_start = p_middle + len(middle_anchor)
                    amount_end = -len(final_anchor_with_newline)
                    amount = line[amount_start:amount_end]

                    subtree = Tree(
                        data="falls_line", children=[Token("t", name), Token("t", amount)]
                    )

                    return Tree(data="line", children=[timestamp, subtree])

            anchor1 = " is immune to "
            anchor2 = " 's "

            p_anchor1 = line.find(anchor1, p_ts_end)
            p_anchor2 = line.find(anchor2, p_anchor1)

            # If both anchors are found in the correct order, we have a match.
            if p_anchor1 != -1 and p_anchor2 != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                target_name = line[p_ts_end + 2 : p_anchor1]

                caster_name = line[p_anchor1 + len(anchor1) : p_anchor2]

                # It's after the second anchor, with the final ".\n" removed.
                spell_start = p_anchor2 + len(anchor2)
                spell_end = -2  # Removes exactly ".\n"
                spell_name = line[spell_start:spell_end]

                # Construct the tree with 3 children in the correct order.
                subtree = Tree(
                    data="is_immune_ability_line",
                    children=[
                        Token("t", target_name),
                        Token("t", caster_name),
                        Token("t", spell_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            p_s = line.find(" 's ", p_ts_end)
            p_evaded = line.find(" was evaded by ", p_s)

            if p_s != -1 and p_evaded != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                caster_name = line[p_ts_end + 2 : p_s]
                spell_name = line[p_s + 4 : p_evaded]

                target_start = p_evaded + 15  # len(' was evaded by ')
                target_end = -2  # Removes exactly ".\n"
                target_name = line[target_start:target_end]

                subtree = Tree(
                    data="was_evaded_line",
                    children=[
                        Token("t", caster_name),
                        Token("t", spell_name),
                        Token("t", target_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            consolidated_anchor = "CONSOLIDATED: "
            p_consolidated = line.find(consolidated_anchor, p_ts_end)

            if p_consolidated != -1:
                # We have a CONSOLIDATED line.
                timestamp = self.parse_ts(line, p_ts_end)

                # Get the entire block of consolidated data.
                data_block = line[p_consolidated + len(consolidated_anchor) :]

                # Split the block into individual cases using "{" as the delimiter.
                cases = data_block.split("{")

                pet_entries = []
                for case_str in cases:
                    # For each case, check if it's a PET entry.
                    if case_str.startswith("PET: "):
                        pet_tree = self.parse_consolidated_pet(case_str)
                        if pet_tree:
                            pet_entries.append(pet_tree)

                subtree = Tree(data="consolidated_line", children=pet_entries)
                return Tree(data="line", children=[timestamp, subtree])

            p_s = line.find(" 's ", p_ts_end)
            p_absorbed = line.find(" is absorbed by ", p_s)

            # If both anchors are found, we have a match.
            if p_s != -1 and p_absorbed != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                caster_name = line[p_ts_end + 2 : p_s]
                spell_name = line[p_s + 4 : p_absorbed]

                target_start = p_absorbed + 16  # len(' is absorbed by ')
                target_end = -2  # Removes exactly ".\n"
                target_name = line[target_start:target_end]

                subtree = Tree(
                    data="is_absorbed_ability_line",
                    children=[
                        Token("t", caster_name),
                        Token("t", spell_name),
                        Token("t", target_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            p_absorbs = line.find(" absorbs ", p_ts_end)
            p_s = line.find(" 's ", p_absorbs)

            # If both anchors are found, we have a match.
            if p_absorbs != -1 and p_s != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                absorber_name = line[p_ts_end + 2 : p_absorbs]

                caster_name = line[p_absorbs + 9 : p_s]  # 9 is len(' absorbs ')

                # It's after the second anchor, with the final ".\n" removed.
                spell_start = p_s + 4  # len(" 's ")
                spell_end = -2  # Removes exactly ".\n"
                spell_name = line[spell_start:spell_end]

                subtree = Tree(
                    data="absorbs_ability_line",
                    children=[
                        Token("t", absorber_name),
                        Token("t", caster_name),
                        Token("t", spell_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            middle_anchor = " is slain by "
            p_slain = line.find(middle_anchor, p_ts_end)

            if p_slain != -1:
                last_char = line[-2]  # newline at end

                if last_char == "." or last_char == "!":
                    # We have a confirmed match.
                    timestamp = self.parse_ts(line, p_ts_end)

                    # The victim's name is between the timestamp and the middle anchor.
                    victim = line[p_ts_end + 2 : p_slain]

                    # cleanly remove any combination of '.', '!'
                    slayer_start = p_slain + len(middle_anchor)
                    slayer = line[slayer_start:-2]

                    subtree = Tree(
                        data="slain_line", children=[Token("t", victim), Token("t", slayer)]
                    )

                    return Tree(data="line", children=[timestamp, subtree])

            action_phrase = " creates "
            p_action = line.find(action_phrase, p_ts_end)

            if p_action != -1 and line.endswith(".\n"):
                timestamp = self.parse_ts(line, p_ts_end)

                creator_name = line[p_ts_end + 2 : p_action]

                item_start = p_action + len(action_phrase)
                item_end = -2  # Removes exactly ".\n"
                item_name = line[item_start:item_end]

                subtree = Tree(
                    data="creates_line", children=[Token("t", creator_name), Token("t", item_name)]
                )

                return Tree(data="line", children=[timestamp, subtree])

            middle_anchor = " is killed by "
            p_killed = line.find(middle_anchor, p_ts_end)

            if p_killed != -1 and line.endswith(".\n"):
                timestamp = self.parse_ts(line, p_ts_end)

                victim = line[p_ts_end + 2 : p_killed]

                killer_start = p_killed + len(middle_anchor)
                killer_end = -2  # Removes exactly ".\n"
                killer = line[killer_start:killer_end]

                subtree = Tree(
                    data="is_killed_line", children=[Token("t", victim), Token("t", killer)]
                )

                return Tree(data="line", children=[timestamp, subtree])

            final_anchor_with_newline = " is destroyed.\n"

            if line.endswith(final_anchor_with_newline):
                timestamp = self.parse_ts(line, p_ts_end)

                # The entity's name is between the timestamp and the start of our known suffix.
                # A negative slice is the cleanest way to remove the suffix.
                name_start = p_ts_end + 2
                name_end = -len(final_anchor_with_newline)
                entity_name = line[name_start:name_end]

                subtree = Tree(data="is_destroyed_line", children=[Token("t", entity_name)])

                return Tree(data="line", children=[timestamp, subtree])

            p_s = line.find(" 's ", p_ts_end)
            p_reflected = line.find(" is reflected back by ", p_s)

            # If both anchors are found, we have a match.
            if p_s != -1 and p_reflected != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                caster_name = line[p_ts_end + 2 : p_s]
                spell_name = line[p_s + 4 : p_reflected]

                reflector_start = p_reflected + 20  # len(' is reflected back by ')
                reflector_end = -2  # Removes exactly ".\n"
                reflector_name = line[reflector_start:reflector_end]

                subtree = Tree(
                    data="is_reflected_back_line",
                    children=[
                        Token("t", caster_name),
                        Token("t", spell_name),
                        Token("t", reflector_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            if line.find("COMBATANT_INFO: ", p_ts_end + 2, p_ts_end + 2 + 16) != -1:
                timestamp = self.parse_ts(line, p_ts_end)
                subtree = Tree(data="combatant_info_line", children=[])
                return Tree(data="line", children=[timestamp, subtree])

            if line.find("NONE", p_ts_end + 2, p_ts_end + 2 + 4) != -1:
                timestamp = self.parse_ts(line, p_ts_end)
                subtree = Tree(data="none_line", children=[])
                return Tree(data="line", children=[timestamp, subtree])

            if line.find(" fails to dispel ", p_ts_end + 2) != -1:
                timestamp = self.parse_ts(line, p_ts_end)
                subtree = Tree(data="fails_to_dispel_line", children=[])
                return Tree(data="line", children=[timestamp, subtree])

            if line.find(" health for swimming in lava.", p_ts_end + 2) != -1:
                timestamp = self.parse_ts(line, p_ts_end)
                subtree = Tree(data="lava_line", children=[])
                return Tree(data="line", children=[timestamp, subtree])

            if line.find(" slays ", p_ts_end + 2) != -1 and line.endswith("!\n"):
                timestamp = self.parse_ts(line, p_ts_end)
                subtree = Tree(data="slays_line", children=[])
                return Tree(data="line", children=[timestamp, subtree])

            if line.find(" pet begins eating a ", p_ts_end + 2) != -1:
                timestamp = self.parse_ts(line, p_ts_end)
                subtree = Tree(data="pet_begins_eating_line", children=[])
                return Tree(data="line", children=[timestamp, subtree])

            if line.endswith(" 's equipped items suffer a 10% durability loss.\n"):
                timestamp = self.parse_ts(line, p_ts_end)
                subtree = Tree(data="equipped_durability_loss_line", children=[])
                return Tree(data="line", children=[timestamp, subtree])

            p_s = line.find(" 's ", p_ts_end)
            p_blocked = line.find(" was blocked by ", p_s)

            if p_s != -1 and p_blocked != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                caster_name = line[p_ts_end + 2 : p_s]
                spell_name = line[p_s + 4 : p_blocked]

                blocker_start = p_blocked + 16  # len(' was blocked by ')
                blocker_end = -2  # Removes exactly ".\n"
                blocker_name = line[blocker_start:blocker_end]

                subtree = Tree(
                    data="block_ability_line",
                    children=[
                        Token("t", caster_name),
                        Token("t", spell_name),
                        Token("t", blocker_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            middle_anchor = " attacks. "
            final_anchor_with_newline = " blocks.\n"

            if line.endswith(final_anchor_with_newline):
                p_attacks = line.find(middle_anchor, p_ts_end)

                if p_attacks != -1:
                    timestamp = self.parse_ts(line, p_ts_end)

                    attacker = line[p_ts_end + 2 : p_attacks]

                    blocker_start = p_attacks + len(middle_anchor)
                    blocker_end = -len(final_anchor_with_newline)
                    blocker = line[blocker_start:blocker_end]

                    subtree = Tree(
                        data="block_line", children=[Token("t", attacker), Token("t", blocker)]
                    )

                    return Tree(data="line", children=[timestamp, subtree])

            p_interrupts = line.find(" interrupts ", p_ts_end)
            p_s = line.find(" 's ", p_interrupts)

            # If both anchors are found, we have a match.
            if p_interrupts != -1 and p_s != -1:
                timestamp = self.parse_ts(line, p_ts_end)

                interrupter_name = line[p_ts_end + 2 : p_interrupts]

                target_name = line[p_interrupts + 12 : p_s]  # 12 is len(' interrupts ')

                spell_start = p_s + 4  # len(" 's ")
                spell_end = -2  # Removes exactly ".\n"
                spell_name = line[spell_start:spell_end]

                subtree = Tree(
                    data="interrupts_line",
                    children=[
                        Token("t", interrupter_name),
                        Token("t", target_name),
                        Token("t", spell_name),
                    ],
                )

                return Tree(data="line", children=[timestamp, subtree])

            middle_anchor = " attacks. "
            final_anchor_with_newline = " absorbs all the damage.\n"

            if line.endswith(final_anchor_with_newline):
                # If it does, find the middle anchor.
                p_attacks = line.find(middle_anchor, p_ts_end)

                if p_attacks != -1:
                    timestamp = self.parse_ts(line, p_ts_end)

                    attacker = line[p_ts_end + 2 : p_attacks]

                    absorber_start = p_attacks + len(middle_anchor)
                    absorber_end = -len(final_anchor_with_newline)
                    absorber = line[absorber_start:absorber_end]

                    subtree = Tree(
                        data="absorbs_all_line",
                        children=[Token("t", attacker), Token("t", absorber)],
                    )

                    return Tree(data="line", children=[timestamp, subtree])

            anchor1 = " gains "
            anchor2 = " Happiness from "
            final_anchor_with_newline = " 's Feed Pet Effect.\n"

            if line.endswith(final_anchor_with_newline):
                p_anchor1 = line.find(anchor1, p_ts_end)
                p_anchor2 = line.find(anchor2, p_anchor1)

                if p_anchor1 != -1 and p_anchor2 != -1:
                    timestamp = self.parse_ts(line, p_ts_end)

                    pet_name = line[p_ts_end + 2 : p_anchor1]

                    amount = line[p_anchor1 + len(anchor1) : p_anchor2]

                    owner_start = p_anchor2 + len(anchor2)
                    owner_end = -len(final_anchor_with_newline)
                    owner_name = line[owner_start:owner_end]

                    subtree = Tree(
                        data="gains_happiness_line",
                        children=[Token("t", pet_name), Token("t", amount), Token("t", owner_name)],
                    )

                    return Tree(data="line", children=[timestamp, subtree])

            final_anchor = " is dismissed.\n"

            if line.endswith(final_anchor):
                # The key is finding the possessive "'s" before the final phrase.
                p_dismissed = line.rfind(" is dismissed.")
                p_s = line.rfind("'s", p_ts_end, p_dismissed)

                if p_s != -1:
                    timestamp = self.parse_ts(line, p_ts_end)

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

                    subtree = Tree(
                        data="is_dismissed_line",
                        children=[Token("t", owner_name), Token("t", pet_name)],
                    )
                    return Tree(data="line", children=[timestamp, subtree])

        except Exception as e:
            self.excnum += 1
            msg = f"{e} {line} \n"
            self.unparsed_logger.log(msg)

        # no fallbacks anymore
        # return self.fallback_parser.parse(line)

        return None


@functools.cache
def dl_price_data(prices_server):
    try:
        URLS = {
            "nord": "https://melbalabs.com/static/twowprices.json",
            "telabim": "https://melbalabs.com/static/twowprices-telabim.json",
        }
        url = URLS[prices_server]
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.exceptions.RequestException:
        logging.warning("web prices not available")
        return None


@functools.cache
def create_unparsed_loggers(expert_log_unparsed_lines):
    if expert_log_unparsed_lines:
        unparsed = UnparsedLogger(filename="unparsed.txt")
        unparsed_fast = UnparsedLogger(filename="unparsed-fast.txt")
    else:
        unparsed = NullLogger(filename="unparsed.txt")
        unparsed_fast = NullLogger(filename="unparsed-fast.txt")
    return unparsed, unparsed_fast


def create_app(
    time_start,
    expert_log_unparsed_lines,
    prices_server,
    expert_disable_web_prices,
    expert_deterministic_logs,
    expert_log_superwow_merge,
):
    app = App()

    parser_debug = False
    if expert_log_unparsed_lines:
        parser_debug = True

    app.unparsed_logger, app.unparsed_logger_fast = create_unparsed_loggers(
        expert_log_unparsed_lines
    )

    app.parser = create_parser(
        grammar=grammar.grammar, debug=parser_debug, unparsed_logger=app.unparsed_logger_fast
    )

    # player - consumable - count
    app.player = collections.defaultdict(lambda: collections.defaultdict(int))
    app.player_superwow = collections.defaultdict(lambda: collections.defaultdict(int))
    app.player_superwow_unknown = collections.defaultdict(lambda: collections.defaultdict(int))

    app.merge_superwow_consumables = MergeSuperwowConsumables(
        player=app.player,
        player_superwow=app.player_superwow,
        player_superwow_unknown=app.player_superwow_unknown,
        expert_log_superwow_merge=expert_log_superwow_merge,
    )

    app.class_detection = ClassDetection(player=app.player)

    app.spell_count = SpellCount()
    app.sunder_armor_summary = SunderArmorSummary(
        spell_count=app.spell_count,
        class_detection=app.class_detection,
    )
    app.cooldown_summary = CooldownSummary(
        spell_count=app.spell_count,
        class_detection=app.class_detection,
    )

    app.proc_count = ProcCount()
    app.proc_summary = ProcSummary(proc_count=app.proc_count, player=app.player)

    # player - consumable - unix_timestamp
    app.last_hit_cache = collections.defaultdict(lambda: collections.defaultdict(float))

    # player - set of reasons this is considered a player
    app.player_detect = collections.defaultdict(set)

    app.pet_handler = PetHandler()

    # name -> death count
    app.death_count = collections.defaultdict(int)

    app.hits_consumable = HitsConsumable(player=app.player, last_hit_cache=app.last_hit_cache)

    app.web_price_provider = WebPriceProvider(prices_server=prices_server)
    price_providers = []
    if not expert_disable_web_prices:
        price_providers.append(app.web_price_provider)
    price_providers.append(LocalPriceProvider("prices.json"))
    app.pricedb = PriceDB(price_providers=price_providers)
    app.consumables_accumulator = ConsumablesAccumulator(
        player=app.player, pricedb=app.pricedb, death_count=app.death_count
    )
    app.print_consumables = PrintConsumables(accumulator=app.consumables_accumulator)
    app.print_consumable_totals_csv = PrintConsumableTotalsCsv(
        accumulator=app.consumables_accumulator
    )

    app.annihilator = Annihilator()
    app.flamebuffet = FlameBuffet()

    # bwl
    app.nef_corrupted_healing = NefCorruptedHealing()
    app.nef_wild_polymorph = NefWildPolymorph()
    # aq
    app.viscidus = Viscidus()
    app.huhuran = Huhuran()
    app.cthun_chain = BeamChain(
        logname="C'Thun Chain Log (2+)",
        beamname="Eye of C'Thun 's Eye Beam",
        chainsize=2,
    )
    # naxx
    app.gluth = Gluth()
    app.fourhm_chain = BeamChain(
        logname="4HM Zeliek Chain Log (4+)",
        beamname="Sir Zeliek 's Holy Wrath",
        chainsize=4,
    )
    app.kt_frostblast = KTFrostblast()
    app.kt_frostbolt = KTFrostbolt()
    app.kt_shadowfissure = KTShadowfissure()
    app.kt_guardian = KTGuardian()

    app.dmgstore = Dmgstore2(
        player=app.player,
        class_detection=app.class_detection,
        abilitycost=ABILITYCOST,
        abilitycooldown=ABILITYCOOLDOWN,
        logname="Damage Done",
        allow_selfdmg=False,
    )
    app.dmgtakenstore = Dmgstore2(
        player=app.player,
        class_detection=app.class_detection,
        abilitycost=ABILITYCOST,
        abilitycooldown=ABILITYCOOLDOWN,
        logname="Damage Taken",
        allow_selfdmg=True,
    )
    app.healstore = Dmgstore2(
        player=app.player,
        class_detection=app.class_detection,
        abilitycost=dict(),
        abilitycooldown=dict(),
        logname="Healing and Overhealing Done",
        allow_selfdmg=True,
    )

    app.techinfo = Techinfo(
        time_start=time_start,
        prices_last_update=app.pricedb.last_update,
        prices_server=prices_server,
        expert_deterministic_logs=expert_deterministic_logs,
    )

    app.infographic = Infographic(
        accumulator=app.consumables_accumulator, class_detection=app.class_detection
    )

    app.log_downloader = LogDownloader()

    return app


def parse_ts2unixtime(timestamp):
    month, day, hour, minute, sec, ms = timestamp.children
    month = int(month)
    day = int(day)
    hour = int(hour)
    minute = int(minute)
    sec = int(sec)
    ms = int(ms)
    timestamp = dt(
        year=CURRENT_YEAR,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=sec,
        tzinfo=datetime.timezone.utc,
    )
    unixtime = timestamp.timestamp()  # seconds
    return unixtime


def check_existing_file(file: Path, delete: bool = False) -> None:
    """Check if file exist and deletes it when forced to.

    - file (Path): File location
    - delete (bool | None, optional (False)): delete file if True
    """

    if file.exists() and file.is_file():
        if delete or False:
            file.unlink()
        return True
    return False


class HitsConsumable:
    COOLDOWNS = {
        "Dragonbreath Chili": 10 * 60,
        "Goblin Sapper Charge": 5 * 60,
        "Stratholme Holy Water": 1 * 60,
    }

    def __init__(self, player, last_hit_cache):
        self.player = player
        self.last_hit_cache = last_hit_cache

    def update(self, name, consumable, timestamp_unix):
        cooldown = self.COOLDOWNS[consumable]
        delta = timestamp_unix - self.last_hit_cache[name][consumable]
        if delta >= cooldown:
            self.player[name][consumable] += 1
            self.last_hit_cache[name][consumable] = timestamp_unix
        elif delta < 0:
            # probably a new year, will ignore for now
            raise RuntimeError("fixme")


NAME2CONSUMABLE: Dict[str, Consumable] = {item.name: item for item in all_defined_consumable_items}

RAWSPELLNAME2CONSUMABLE: Dict[Tuple[str, str], Consumable] = {}
for item in all_defined_consumable_items:
    for line_type, raw_spellname in item.spell_aliases:
        key = (line_type, raw_spellname)
        if key in RAWSPELLNAME2CONSUMABLE:
            raise ValueError(
                f"duplicate consumable alias. tried to add {key} for {item.name}"
                f" but {RAWSPELLNAME2CONSUMABLE[key].name} already added"
            )
        RAWSPELLNAME2CONSUMABLE[key] = item


RENAME_SPELL = {
    ("hits_ability_line", "Holy Shock"): "Holy Shock (dmg)",
    ("heals_line", "Holy Shock"): "Holy Shock (heal)",
    ("heals_line", "Tea"): "Tea with Sugar",
    ("gains_rage_line", "Blood Fury"): "Gri'lek's Charm of Might",
}


def rename_spell(spell, line_type):
    rename = RENAME_SPELL.get((line_type, spell))
    return rename or spell


# careful. not everything needs an itemid
NAME2ITEMID = {
    consumable.name: consumable.price.itemid
    for consumable in all_defined_consumable_items
    if isinstance(consumable.price, DirectPrice)
}


# used for pricing
ITEMID2NAME = {value: key for key, value in NAME2ITEMID.items()}


USES_CONSUMABLE_RENAME = {
    "Tea With Sugar": "Tea with Sugar",
}


INTERRUPT_SPELLS = {
    "Kick",
    "Pummel",
    "Shield Bash",
    "Earth Shock",
}


CDSPELL_CLASS = [
    [
        PlayerClass.WARRIOR,
        [
            "Death Wish",
            "Sweeping Strikes",
            "Shield Wall",
            "Recklessness",
            "Bloodrage",
        ],
    ],
    [PlayerClass.MAGE, ["Combustion", "Scorch"]],
    [
        PlayerClass.SHAMAN,
        [
            "Nature's Swiftness",
            "Windfury Totem",
            "Mana Tide Totem",
            "Grace of Air Totem",
            "Tranquil Air Totem",
            "Strength of Earth Totem",
            "Mana Spring Totem",
            "Searing Totem",
            "Fire Nova Totem",
            "Magma Totem",
            "Ancestral Spirit",
        ],
    ],
    [PlayerClass.DRUID, ["Nature's Swiftness", "Rebirth", "Swiftmend"]],
    [
        PlayerClass.PRIEST,
        [
            "Inner Focus",
            "Resurrection",
        ],
    ],
    [
        PlayerClass.PALADIN,
        ["Divine Favor", "Holy Shock (heal)", "Holy Shock (dmg)", "Redemption"],
    ],
    [
        PlayerClass.ROGUE,
        [
            "Adrenaline Rush",
            "Blade Flurry",
        ],
    ],
    [PlayerClass.WARLOCK, []],
    [PlayerClass.HUNTER, ["Rapid Fire"]],
]


RECEIVE_BUFF_SPELL = {
    "Power Infusion",
    "Bloodlust",
    "Chastise Haste",
}
RACIAL_SPELL = [
    "Blood Fury",
    "Berserking",
    "Stoneform",
    "Desperate Prayer",
    "Will of the Forsaken",
    "War Stomp",
]
TRINKET_SPELL = [
    "Kiss of the Spider",
    "Slayer's Crest",
    "Jom Gabbar",
    "Badge of the Swarmguard",
    "Earthstrike",
    "Diamond Flask",
    "Gri'lek's Charm of Might",
    "The Eye of the Dead",
    "Healing of the Ages",
    "Essence of Sapphiron",
    "Ephemeral Power",
    "Unstable Power",
    "Mind Quickening",
    "Nature Aligned",
    "Death by Peasant",
    "Immune Charm/Fear/Stun",
    "Immune Charm/Fear/Polymorph",
    "Immune Fear/Polymorph/Snare",
    "Immune Fear/Polymorph/Stun",
    "Immune Root/Snare/Stun",
]
RENAME_TRINKET_SPELL = {
    "Unstable Power": "Zandalarian Hero Charm",
    "Ephemeral Power": "Talisman of Ephemeral Power",
    "Essence of Sapphiron": "The Restrained Essence of Sapphiron",
    "Mind Quickening": "Mind Quickening Gem",
    "Nature Aligned": "Natural Alignment Crystal",
    "Death by Peasant": "Barov Peasant Caller",
    "Healing of the Ages": "Hibernation Crystal",
    "Rapid Healing": "Hazza'rah's Charm of Healing",
    "Chromatic Infusion": "Draconic Infused Emblem",
    "Immune Charm/Fear/Stun": "Insignia of the Alliance/Horde",
    "Immune Charm/Fear/Polymorph": "Insignia of the Alliance/Horde",
    "Immune Fear/Polymorph/Snare": "Insignia of the Alliance/Horde",
    "Immune Fear/Polymorph/Stun": "Insignia of the Alliance/Horde",
    "Immune Root/Snare/Stun": "Insignia of the Alliance/Horde",
}
for spell in itertools.chain(TRINKET_SPELL, RACIAL_SPELL, sorted(RECEIVE_BUFF_SPELL)):
    for clsorder in CDSPELL_CLASS:
        spells = clsorder[1]
        spells.append(spell)


BUFF_SPELL = {
    "Greater Blessing of Wisdom",
    "Greater Blessing of Salvation",
    "Greater Blessing of Light",
    "Greater Blessing of Kings",
    "Greater Blessing of Might",
    "Prayer of Spirit",
    "Prayer of Fortitude",
    "Prayer of Shadow Protection",
}

ABILITYCOST = {
    "Bloodthirst": 30,
    "Hamstring": 10,
    "Heroic Strike": 15,
    "Whirlwind": 25,
    "Cleave": 20,
    "Execute": 15,
    "Slam": 15,
}

ABILITYCOOLDOWN = {
    "Whirlwind": 8,
    "Cleave": 1,
}

KNOWN_BOSS_NAMES = {
    # naxx
    "Anub'Rekhan",
    "Grand Widow Faerlina",
    "Maexxna",
    "Noth the Plaguebringer",
    "Heigan the Unclean",
    "Loatheb",
    "Patchwerk",
    "Grobbulus",
    "Gluth",
    "Thaddius",
    "Feugen",
    "Stalagg",
    "Instructor Razuvious",
    "Gothik the Harvester",
    "Highlord Mograine",
    "Lady Blaumeux",
    "Sir Zeliek",
    "Thane Korth'azz",
    "Sapphiron",
    "Kel'Thuzad",
}


def healpot_lookup(amount):
    # bigger ranges for rounding errors
    if 1049 <= amount <= 1751:
        return "Healing Potion - Major"
    if 699 <= amount <= 901:
        return "Healing Potion - Superior"
    if 454 <= amount <= 586:
        return "Healing Potion - Greater"
    if 139 <= amount <= 181:
        return "Healing Potion - Lesser"
    if 69 <= amount <= 91:
        return "Healing Potion - Minor"
    return "Healing Potion - unknown"


def manapot_lookup(mana):
    consumable = "Restore Mana (mana potion)"
    if 1350 <= mana <= 2250:
        consumable = "Mana Potion - Major"
    elif 900 <= mana <= 1500:
        consumable = "Mana Potion - Superior"
    elif 700 <= mana <= 900:
        consumable = "Mana Potion - Greater"
    elif 280 <= mana <= 360:
        consumable = "Mana Potion - Lesser"
    elif 140 <= mana <= 180:
        consumable = "Mana Potion - Minor"
    return consumable


class LogParser:
    # simple slow parser for individual lines with no context

    def __init__(self, logname, needles):
        self.log = []
        self.logname = logname
        self.needles = needles

    def parse(self, line):
        for needle in self.needles:
            match = re.search(needle, line)
            if match:
                self.log.append(line)
                return 1

    def print(self, output):
        if not self.log:
            return

        print(f"\n\n{self.logname}", file=output)
        for line in self.log:
            print("  ", line, end="", file=output)


def print_collected_log(section_name, log_list, output):
    if not log_list:
        return
    print(f"\n\n{section_name}", file=output)
    for line in log_list:
        print("  ", line, end="", file=output)
    return


def print_collected_log_always(section_name, log_list, output):
    print(f"\n\n{section_name}", file=output)
    for line in log_list:
        print("  ", line, end="", file=output)
    if not log_list:
        print("  ", "<nothing found>", end="", file=output)
    return


class Annihilator:
    def __init__(self):
        self.logname = "Annihilator Log"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log_always(self.logname, self.log, output)


class FlameBuffet:
    def __init__(self):
        self.logname = "Flame Buffet (dragonling) Log"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log_always(self.logname, self.log, output)


class KTFrostbolt:
    def __init__(self):
        self.logname = "KT Frostbolt Log"
        self.log = []

    def begins_to_cast(self, line):
        self.log.append("\n")
        self.log.append(line)

    def add(self, line):
        self.log.append(line)

    def parry(self, line):
        line = "*** honorable mention *** " + line
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class KTFrostblast:
    def __init__(self):
        self.logname = "KT Frost Blast Log"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class KTShadowfissure:
    def __init__(self):
        self.logname = "KT Shadow Fissure Log"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class KTGuardian:
    def __init__(self):
        self.logname = "KT Guardian of Icecrown Log"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class Viscidus:
    def __init__(self):
        self.logname = "Viscidus Frost Hits Log"
        # player - frost spell - count
        self.counts = collections.defaultdict(lambda: collections.defaultdict(int))
        self.totals = collections.defaultdict(int)
        self._found = False

    def add(self, player, spell):
        self.counts[player][spell] += 1
        self.totals[player] += 1

    def found(self):
        self._found = True

    def print(self, output):
        if not self._found:
            return
        print(f"\n\n{self.logname}", file=output)
        players = [(total, player) for player, total in self.totals.items()]
        players.sort(reverse=True)
        print("  ", "Total hits", sum(total for total, player in players), file=output)
        print(file=output)
        for total, player in players:
            print("  ", player, total, file=output)
            spells = [(total, spell) for spell, total in self.counts[player].items()]
            spells.sort(reverse=True)
            for total, spell in spells:
                print("  ", "  ", spell, total, file=output)


class Huhuran:
    def __init__(self):
        self.logname = "Princess Huhuran Log"
        self.log = []
        self._found = False

    def found(self):
        self._found = True

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        if not self._found:
            return
        print_collected_log(self.logname, self.log, output)


class NefCorruptedHealing:
    def __init__(self):
        self.logname = "Nefarian Priest Corrupted Healing"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class NefWildPolymorph:
    def __init__(self):
        self.logname = "Nefarian Wild Polymorph (mage call)"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class Gluth:
    def __init__(self):
        self.logname = "Gluth Log"
        self.log = []

    def add(self, line):
        self.log.append(line)

    def print(self, output):
        print_collected_log(self.logname, self.log, output)


class BeamChain:
    def __init__(self, logname, beamname, chainsize):
        self.log = []  # for debugging/testing

        self.current_batch = []
        self.batches = []

        self.last_ts = 0
        self.logname = logname
        self.beamname = beamname
        self.chainsize = chainsize  # report chains bigger than this

    def add(self, timestamp_unix, line):
        self.log.append(line)

        cooldown = 2
        delta = timestamp_unix - self.last_ts
        if delta >= cooldown:
            self.commitbatch()
            self.last_ts = timestamp_unix

        self.current_batch.append(line)

    def commitbatch(self):
        if self.current_batch:
            self.batches.append(self.current_batch)
            self.current_batch = []

    def print(self, output):
        if not self.log:
            return

        self.commitbatch()

        found_batch = 0
        print(f"\n\n{self.logname}", file=output)

        for batch in self.batches:
            if len(batch) < self.chainsize:
                continue

            found_batch = 1

            print(file=output)
            for line in batch:
                print("  ", line, end="", file=output)

        if not found_batch:
            print(
                "  ",
                f"<no chains of {self.chainsize} found. well done>",
                end="",
                file=output,
            )


class DmgstoreEntry:
    def __init__(self):
        self.dmg = 0
        self.cost = 0
        self.hits = 0
        self.uses = 0
        self.last_ts = 0


class Dmgstore2:
    def __init__(
        self,
        player,
        class_detection: "ClassDetection",
        abilitycost,
        abilitycooldown,
        logname,
        allow_selfdmg,
    ):
        self.logname = logname
        self.player = player
        self.class_detection = class_detection
        self.abilitycost = abilitycost
        self.abilitycooldown = abilitycooldown
        self.allow_selfdmg = allow_selfdmg

        self.store_ability = collections.defaultdict(DmgstoreEntry)
        self.store_target = collections.defaultdict(DmgstoreEntry)
        self.store_source = collections.defaultdict(DmgstoreEntry)

        self.store_by_source_ability = collections.defaultdict(
            lambda: collections.defaultdict(DmgstoreEntry)
        )

    def add(self, source, target, ability, amount, timestamp_unix):
        if not self.allow_selfdmg and source == target:
            return
        cost = self.abilitycost.get(ability, 0)
        cooldown = self.abilitycooldown.get(ability, 0)

        entry_ability = self.store_ability[(source, target, ability)]
        entry_ability.dmg += amount
        entry_ability.hits += 1

        entry_target = self.store_target[(source, target)]
        entry_target.dmg += amount
        entry_target.hits += 1

        entry_source = self.store_source[source]
        entry_source.dmg += amount
        entry_source.hits += 1

        entry_by_source_ability = self.store_by_source_ability[source][ability]
        entry_by_source_ability.dmg += amount
        entry_by_source_ability.hits += 1

        delta = timestamp_unix - entry_by_source_ability.last_ts
        if delta >= cooldown:
            entry_by_source_ability.last_ts = timestamp_unix

            entry_by_source_ability.uses += 1
            entry_ability.uses += 1
            entry_target.uses += 1
            entry_source.uses += 1

            entry_by_source_ability.cost += cost
            entry_ability.cost += cost
            entry_target.cost += cost
            entry_source.cost += cost

    def print_compare_players(self, player1, player2, output):
        # fill blanks

        for source, target, ability in sorted(self.store_ability):
            if source == player1:
                self.store_ability[(player2, target, ability)]
                self.store_target[(player2, target)]
            elif source == player2:
                self.store_ability[(player1, target, ability)]
                self.store_target[(player1, target)]

        es1 = self.store_source[player1]
        es2 = self.store_source[player2]

        # extract data to report on
        p1 = dict()
        p2 = dict()

        for source, target, ability in sorted(self.store_ability):
            if source == player1:
                p1[(target, ability)] = self.store_ability[(player1, target, ability)]
            elif source == player2:
                p2[(target, ability)] = self.store_ability[(player2, target, ability)]

        print(f"output for {player1} - {player2}", file=output)
        print(file=output)

        print(
            f"total  dmg:{es1.dmg - es2.dmg} cost:{es1.cost - es2.cost} uses:{es1.uses - es2.uses} hits:{es1.hits - es2.hits}",
            file=output,
        )
        print(file=output)

        seen_target = set()
        for target, ability in p1:
            e1 = p1[(target, ability)]
            e2 = p2[(target, ability)]

            if target not in seen_target:
                seen_target.add(target)
                print(file=output)
                et1 = self.store_target[(player1, target)]
                et2 = self.store_target[(player2, target)]
                txt = f"{target}   dmg:{et1.dmg - et2.dmg} cost:{et1.cost - et2.cost} uses:{et1.uses - et2.uses} hits:{et1.hits - et2.hits}"
                print(txt, file=output)
            txt = f"{ability}   dmg:{e1.dmg - e2.dmg} cost:{e1.cost - e2.cost} uses:{e1.uses - e2.uses} hits:{e1.hits - e2.hits}"
            print(txt, file=output)

    def print_damage(self, output):
        # first find dmg totals
        # then abilities
        dmgtotals = collections.defaultdict(int)
        for (source, target, ability), entry in self.store_ability.items():
            if source not in self.player:
                continue
            dmgtotals[source] += entry.dmg

        sortdmgtotals = []
        for source, dmg in dmgtotals.items():
            sortdmgtotals.append((dmg, source))

        sortdmgtotals.sort(reverse=True)
        for dmg, source in sortdmgtotals:
            print(f"{source}  {dmg}", file=output)

            sortabilitytotals = []
            for ability, entry_by_source_ability in self.store_by_source_ability[source].items():
                dmg = entry_by_source_ability.dmg
                sortabilitytotals.append((dmg, ability))

            sortabilitytotals.sort(reverse=True)
            for dmg2, ability in sortabilitytotals:
                print(f"  {ability}  {dmg2}", file=output)

    def print_damage_taken(self, output):
        # by source, ability, target

        by_source = collections.defaultdict(int)
        by_ability = collections.defaultdict(lambda: collections.defaultdict(int))
        by_target = collections.defaultdict(lambda: collections.defaultdict(int))
        for (source, target, ability), entry in self.store_ability.items():
            if target not in self.player:
                continue

            dmg = entry.dmg
            by_source[source] += dmg
            by_ability[source][ability] += dmg
            by_target[(source, ability)][target] += dmg

        source_sorted = sorted(by_source, key=lambda k: by_source[k], reverse=True)
        for source in source_sorted:
            print(f"{source}  {by_source[source]}", file=output)

            ability_sorted = sorted(
                by_ability[source], key=lambda k: by_ability[source][k], reverse=True
            )

            for ability in ability_sorted:
                print("  ", f"{ability}  {by_ability[source][ability]}", file=output)

                target_sorted = sorted(
                    by_target[(source, ability)],
                    key=lambda k: by_target[(source, ability)][k],
                    reverse=True,
                )

                for target in target_sorted:
                    print(
                        "  ",
                        "  ",
                        f"{target}  {by_target[(source, ability)][target]}",
                        file=output,
                    )


class Techinfo:
    def __init__(self, time_start, prices_last_update, prices_server, expert_deterministic_logs):
        self.time_start = time_start
        self.logsize = 0
        self.linecount = 0
        self.skiplinecount = 0
        self.package_version = package.VERSION
        urlname, url = package.PROJECT_URL.split(",", maxsplit=1)
        assert urlname == "Homepage"
        self.project_homepage = url.strip()
        self.prices_last_update = prices_last_update
        self.prices_server = prices_server
        self.expert_deterministic_logs = expert_deterministic_logs

        self.implementation = str(sys.implementation).replace("namespace", "")
        self.platform = sys.platform
        self.version = sys.version

    def set_file_size(self, filename):
        self.logsize = os.path.getsize(filename)

    def set_line_count(self, count):
        self.linecount = count

    def set_skipped_line_count(self, count):
        self.skiplinecount = count

    def format_price_timestamp(self):
        if self.prices_last_update == 0:
            return "not available"
        dt = datetime.datetime.fromtimestamp(self.prices_last_update, datetime.UTC)
        delta = self.time_start - self.prices_last_update
        return f"{dt.isoformat()} ({humanize.naturaltime(delta)})"

    def format_skipped_percent(self):
        if self.linecount == 0:
            return ""
        return f"({(self.skiplinecount / self.linecount) * 100:.2f}%)"

    def print(self, output, time_end=None):
        if time_end is None:
            time_end = time.time()
        time_delta = time_end - self.time_start
        print("\n\nTech", file=output)
        if not self.expert_deterministic_logs:
            print("  ", f"project version {self.package_version}", file=output)
            print("  ", f"project homepage {self.project_homepage}", file=output)
            print("  ", f"prices server {self.prices_server}", file=output)
            print("  ", f"prices timestamp {self.format_price_timestamp()}", file=output)
        print("  ", f"known consumables {len(all_defined_consumable_items)}", file=output)
        print("  ", f"log size {humanize.naturalsize(self.logsize)}", file=output)
        print("  ", f"log lines {self.linecount}", file=output)
        print(
            "  ",
            f"skipped log lines {self.skiplinecount} {self.format_skipped_percent()}",
            file=output,
        )
        if not self.expert_deterministic_logs:
            print(
                "  ",
                f"processed in {time_delta:.2f} seconds. {self.linecount / time_delta:.2f} log lines/sec",
                file=output,
            )
            print("  ", f"runtime platform {self.platform}", file=output)
            print("  ", f"runtime implementation {self.implementation}", file=output)
            print("  ", f"runtime version {self.version}", file=output)


class UnparsedLogger:
    def __init__(self, filename):
        self.filename = filename
        self.buffer = io.StringIO()

    def log(self, line):
        print(line, end="", file=self.buffer)

    def flush(self):
        print("writing unparsed to", self.filename)
        with open(self.filename, "wb") as f:
            f.write(self.buffer.getvalue().encode("utf8"))


class NullLogger:
    def __init__(self, filename):
        pass

    def log(self, line):
        pass

    def flush(self):
        pass


class LocalPriceProvider:
    def __init__(self, filename):
        self.filename = filename

    def load(self):
        filename = self.filename
        if not os.path.exists(filename):
            logging.warning(f"local prices not available. {filename} not found")
            return
        logging.info("loading local prices from {filename}")
        with open(filename) as f:
            prices = json.load(f)
            return prices


class WebPriceProvider:
    def __init__(self, prices_server):
        self.prices_server = prices_server

    def load(self):
        logging.info("loading web prices")
        prices = dl_price_data(prices_server=self.prices_server)
        return prices


class PriceDB:
    def __init__(self, price_providers):
        self.data = dict()
        self.last_update = 0

        for provider in price_providers:
            prices = provider.load()
            if not prices:
                continue
            self.load_incoming(prices)
            return

    def lookup(self, itemid):
        return self.data.get(itemid)

    def load_incoming(self, incoming):
        self.last_update = incoming["last_update"]
        for key, val in incoming["data"].items():
            key = int(key)
            self.data[key] = val


class PetHandler:
    def __init__(self):
        # owner -> set of pets
        self.store = collections.defaultdict(set)

    def add(self, owner, pet):
        self.store[owner].add(pet)

    def get_all_pets(self):
        for owner, petset in self.store.items():
            for pet in petset:
                yield pet

    def print(self, output):
        if not len(self.store):
            return
        print("\n\nPets", file=output)
        for owner, petset in self.store.items():
            for pet in sorted(petset):
                print("  ", pet, "owned by", owner, file=output)


class SunderArmorSummary:
    def __init__(self, spell_count, class_detection: "ClassDetection"):
        self.counts = spell_count.counts
        self.class_detection = class_detection

    def print(self, output):
        print("\n\nSunder Armor Summary (trash and boss counts)", file=output)
        warriors = [
            name
            for name, player_class in self.class_detection.store.items()
            if player_class is PlayerClass.WARRIOR
        ]

        found_sunder = False
        entries = []
        sunder_trash = self.counts.get("Sunder Armor", {})
        sunder_boss = self.counts.get("Sunder Armor (boss)", {})

        for warrior in warriors:
            trash = sunder_trash.get(warrior, 0)
            boss = sunder_boss.get(warrior, 0)
            entries.append((-trash, -boss, warrior, trash, boss))
            if trash or boss:
                found_sunder = True

        if found_sunder:
            entries.sort()

            for _, _, name, trash, boss in entries:
                line = f"   {name} {trash}"
                if boss > 0:
                    line += f" {boss}"
                print(line, file=output)
        elif entries:
            print("   <nothing found. needs superwow>", file=output)
        else:
            print("   <nothing found>", file=output)


class CooldownSummary:
    def __init__(self, spell_count, class_detection: "ClassDetection"):
        # spell - player - count
        self.counts = spell_count.counts
        self.class_detection = class_detection

    def print(self, output):
        print("\n\nCooldown Summary", file=output)
        for player_class, spells in CDSPELL_CLASS:
            cls_printed = False
            for spell in spells:
                if spell not in self.counts:
                    continue

                data = []
                for name, total in self.counts[spell].items():
                    if not self.class_detection.is_class(cls=player_class, name=name):
                        continue
                    data.append((total, name))
                data.sort(reverse=True)

                if not data:
                    continue

                if not cls_printed:
                    print("  ", player_class.value.capitalize(), file=output)
                    cls_printed = True
                if spell in RENAME_TRINKET_SPELL:
                    spell = RENAME_TRINKET_SPELL[spell]
                if spell in RECEIVE_BUFF_SPELL:
                    spell += " (received)"
                print("  ", "  ", spell, file=output)
                for total, name in data:
                    print("  ", "  ", "  ", name, total, file=output)


class ProcSummary:
    def __init__(self, proc_count, player):
        # spell - player - count
        self.counts = proc_count.counts
        self.counts_extra_attacks = proc_count.counts_extra_attacks
        self.player = player

    def print(self, output):
        print("\n\nProc Summary", file=output)
        for proc in sorted(self.counts):
            data = []
            for name in sorted(self.counts[proc]):
                total = self.counts[proc][name]
                if name not in self.player:
                    continue
                data.append((total, name))
            data.sort(reverse=True)

            if not data:
                continue
            print("  ", proc, file=output)
            for total, name in data:
                print("  ", "  ", name, total, file=output)

        # extra attacks
        print("  ", "Extra Attacks", file=output)
        for source in sorted(self.counts_extra_attacks):
            data = []
            for name in sorted(self.counts_extra_attacks[source]):
                total = self.counts_extra_attacks[source][name]
                if name not in self.player:
                    continue
                data.append((total, name))
            data.sort(reverse=True)

            if not data:
                continue
            print("  ", "  ", source, file=output)
            for total, name in data:
                print("  ", "  ", "  ", name, total, file=output)


# count unique casts, the player using their spell. not the lingering buff/debuff procs
# eg count a totem being dropped, not the buff procs it gives after that
LINE2SPELLCAST = {
    "afflicted_line": {
        "Death Wish",
    },
    "gains_line": {
        "Immune Charm/Fear/Stun",
        "Immune Charm/Fear/Polymorph",
        "Immune Fear/Polymorph/Snare",
        "Immune Fear/Polymorph/Stun",
        "Immune Root/Snare/Stun",
        "Will of the Forsaken",
        "Bloodrage",
        "Recklessness",
        "Shield Wall",
        "Sweeping Strikes",
        "Elemental Mastery",
        "Inner Focus",
        "Rapid Healing",
        "Chromatic Infusion",
        "Combustion",
        "Adrenaline Rush",  # careful with hunters
        "Cold Blood",
        "Blade Flurry",
        "Nature's Swiftness",  # sham and druid
        "Rapid Fire",
        "The Eye of the Dead",
        "Healing of the Ages",
        "Earthstrike",
        "Diamond Flask",
        "Kiss of the Spider",
        "Slayer's Crest",
        "Jom Gabbar",
        "Badge of the Swarmguard",
        "Essence of Sapphiron",
        "Ephemeral Power",
        "Unstable Power",
        "Mind Quickening",
        "Nature Aligned",
        "Divine Favor",
        "Berserking",
        "Stoneform",
        # buffs received
        "Power Infusion",
        "Bloodlust",
        "Chastise Haste",
    },
    "gains_rage_line": {
        "Gri'lek's Charm of Might",
    },
    "heals_line": {
        "Holy Shock (heal)",
        "Desperate Prayer",
        "Swiftmend",
    },
    "casts_line": {
        "Windfury Totem",
        "Mana Tide Totem",
        "Grace of Air Totem",
        "Tranquil Air Totem",
        "Strength of Earth Totem",
        "Mana Spring Totem",
        "Searing Totem",
        "Fire Nova Totem",
        "Magma Totem",
        "Ancestral Spirit",
        "Redemption",
        "Resurrection",
        "Rebirth",
        "Sunder Armor",  # superwow
        "Sunder Armor (boss)",  # rename, superwow
        "Blood Fury",  # superwow, spellid 23234
    },
    "hits_ability_line": {
        "Sinister Strike",
        "Scorch",
        "Holy Shock (dmg)",
    },
    "begins_to_perform_line": {
        "War Stomp",
    },
}


class SpellCount:
    def __init__(self):
        # spell - name - count
        self.counts = collections.defaultdict(lambda: collections.defaultdict(int))

    def add(self, line_type, name, spell):
        if line_type not in LINE2SPELLCAST:
            return
        if spell not in LINE2SPELLCAST[line_type]:
            return
        self.counts[spell][name] += 1

    def add_stackcount(self, line_type, name, spell, stackcount):
        if (
            spell in {"Combustion", "Unstable Power", "Jom Gabbar"}
            and line_type == "gains_line"
            and stackcount != 1
        ):
            return
        self.add(line_type=line_type, name=name, spell=spell)


LINE2PROC = {
    "gains_line": {
        "Enrage",
        "Flurry",
        "Elemental Devastation",
        "Stormcaller's Wrath",
        "Spell Blasting",
        "Clearcasting",
        "Vengeance",
        "Nature's Grace",
    },
}


class ProcCount:
    def __init__(
        self,
    ):
        # effect - name - count
        self.counts = collections.defaultdict(lambda: collections.defaultdict(int))

        # source - name - count
        self.counts_extra_attacks = collections.defaultdict(lambda: collections.defaultdict(int))

    def add(self, line_type, name, spell):
        if line_type not in LINE2PROC:
            return
        if spell not in LINE2PROC[line_type]:
            return
        self.counts[spell][name] += 1

    def add_extra_attacks(self, howmany, source, name):
        self.counts_extra_attacks[source][name] += howmany


class Currency(int):
    string_pattern = r"((?P<gold>\d+)g)?\s?((?P<silver>\d+)s)?\s?((?P<copper>\d+)c)?"

    def __new__(cls, value, *args, **kwargs) -> Self:
        if isinstance(value, str):
            return cls.from_string(value)
        return super().__new__(cls, value, *args, **kwargs)

    def __add__(self, other) -> Self:
        return Currency(super().__add__(other))

    def __sub__(self, other) -> Self:
        return Currency(super().__sub__(other))

    def __mul__(self, other) -> Self:
        return Currency(super().__mul__(other))

    def __truediv__(self, other) -> Self:
        return Currency(super().__truediv__(other))

    def __mod__(self, other) -> Self:
        return Currency(super().__mod__(other))

    @classmethod
    def from_string(cls, s: str) -> Self:
        m = re.search(cls.string_pattern, s)
        if not any(m.groupdict().values()):
            raise ValueError(f"Invalid currency string format: {s}")
        return cls(
            sum(
                [
                    int(m.group("gold") or 0) * 10000,
                    int(m.group("silver") or 0) * 100,
                    int(m.group("copper") or 0),
                ]
            )
        )

    def to_string(self, short: bool = False) -> str:
        if short:
            return f"{int(self) / 10000.0:.1f}g"

        value = int(self)
        copper = value % 100
        value = value // 100
        silver = value % 100
        value = value // 100
        gold = value
        s = ""

        first = True
        for amount, suffix in zip([gold, silver, copper], "gsc"):
            if amount:
                if not first:
                    s += " "
                else:
                    first = False
                s += f"{amount}{suffix}"
        return s


@dataclasses.dataclass
class ConsumableStore:
    item_name: str
    amount: int = 0
    price: Currency = Currency(0)

    @property
    def total_price(self) -> Currency:
        return self.price * self.amount


@dataclasses.dataclass
class ConsumablesEntry:
    name: str
    deaths: int = 0
    consumables: List[ConsumableStore] = dataclasses.field(default_factory=list)
    total_spent: Currency = Currency(0)

    def add_consumable(self, consumable: ConsumableStore) -> None:
        self.consumables.append(consumable)
        self.total_spent += consumable.total_price


@dataclasses.dataclass
class ConsumablesAccumulator:
    player: Dict
    pricedb: PriceDB
    death_count: Dict[str, int]
    data: List[ConsumablesEntry] = dataclasses.field(default_factory=list)

    def get_consumable_price(self, consumable_name: str) -> Currency:
        consumable = NAME2CONSUMABLE.get(consumable_name)

        price = Currency(0)
        if not consumable:
            # logging.warning(f"Consumable '{consumable_name}' not defined.")
            return price

        if isinstance(consumable.price, NoPrice):
            return price

        # Determine the list of items whose direct itemid-based price we need to sum up.
        # For a crafted item, these are its components.
        # For a base item, it's the item itself.
        components_to_price: List[Tuple[Consumable, float]]

        item_charges = consumable.price.charges

        if isinstance(consumable.price, PriceFromComponents):
            components_to_price = consumable.price.components
        elif isinstance(
            consumable.price, DirectPrice
        ):  # It's a base item (or has no defined components)
            components_to_price = [(consumable, 1.0)]
        else:  # Should not happen if NoPrice is handled
            raise RuntimeError("this should be unreachable")

        for base_item, quantity in components_to_price:
            if not isinstance(base_item.price, DirectPrice) or not base_item.price.itemid:
                # This item/component doesn't have an itemID to look up.
                # logging.debug(f"Item '{base_item.name}' has no itemid for pricing.")
                continue

            unit_price = self.pricedb.lookup(base_item.price.itemid)
            if unit_price is None:
                # logging.debug(f"Price not found for item '{base_item.name}' (ID: {base_item.price.itemid}).")
                continue

            price += int(unit_price * quantity)

        return price / item_charges

    def calculate(self) -> None:
        for name in sorted(self.player):
            consumables = sorted(self.player[name])
            player_entry = ConsumablesEntry(name, deaths=self.death_count[name])
            for consumable_name in sorted(
                consumables
            ):  # consumable_name is already a canonical string
                player_entry.add_consumable(
                    ConsumableStore(
                        consumable_name,
                        amount=self.player[name][consumable_name],
                        price=self.get_consumable_price(consumable_name),
                    )
                )
            self.data.append(player_entry)


class PrintConsumables:
    def __init__(self, accumulator: ConsumablesAccumulator):
        self.accumulator = accumulator

    def print(self, output):
        for player in self.accumulator.data:
            print(player.name, f"deaths:{player.deaths}", file=output)
            for cons in player.consumables:
                spent = f"  ({cons.total_price.to_string()})" if cons.price else ""
                print("  ", cons.item_name, cons.amount, spent, file=output)
            if not player.consumables:
                print("  ", "<nothing found>", file=output)
            elif player.total_spent:
                print(file=output)
                print("  ", "total spent:", player.total_spent.to_string(), file=output)


class PrintConsumableTotalsCsv:
    def __init__(self, accumulator: ConsumablesAccumulator):
        self.accumulator = accumulator

    def print(self, output):
        writer = csv.writer(output)
        for player in self.accumulator.data:
            writer.writerow([player.name, player.total_spent, player.deaths])


# line type -> spell -> PlayerClass
# shouldn't need to be an exhaustive list, only the most common
# unique spells, no ambiguity
UNIQUE_LINE2SPELL2CLASS: Dict[str, Dict[str, PlayerClass]] = {
    "afflicted_line": {
        "Death Wish": PlayerClass.WARRIOR,
    },
    "gains_line": {
        "Recklessness": PlayerClass.WARRIOR,
        "Shield Wall": PlayerClass.WARRIOR,
        "Bloodrage": PlayerClass.WARRIOR,
        "Sweeping Strikes": PlayerClass.WARRIOR,
        "Combustion": PlayerClass.MAGE,
        "Adrenaline Rush": PlayerClass.ROGUE,
        "Blade Flurry": PlayerClass.ROGUE,
        "Cold Blood": PlayerClass.ROGUE,
        "Slice and Dice": PlayerClass.ROGUE,
        "Divine Favor": PlayerClass.PALADIN,
        "Seal of Command": PlayerClass.PALADIN,
        "Seal of Righteousness": PlayerClass.PALADIN,
    },
    "heals_line": {
        "Flash of Light": PlayerClass.PALADIN,
        "Holy Light": PlayerClass.PALADIN,
        "Holy Shock (heal)": PlayerClass.PALADIN,
        "Heal": PlayerClass.PRIEST,
        "Flash Heal": PlayerClass.PRIEST,
        "Greater Heal": PlayerClass.PRIEST,
        "Prayer of Healing": PlayerClass.PRIEST,
    },
    "hits_ability_line": {
        "Cleave": PlayerClass.WARRIOR,
        "Whirlwind": PlayerClass.WARRIOR,
        "Bloodthirst": PlayerClass.WARRIOR,
        "Heroic Strike": PlayerClass.WARRIOR,
        "Sinister Strike": PlayerClass.ROGUE,
        "Arcane Explosion": PlayerClass.MAGE,
        "Fire Blast": PlayerClass.MAGE,
        "Starfire": PlayerClass.DRUID,
        "Moonfire": PlayerClass.DRUID,
        "Wrath": PlayerClass.DRUID,
        "Shadow Bolt": PlayerClass.WARLOCK,
        "Mind Blast": PlayerClass.PRIEST,
        "Arcane Shot": PlayerClass.HUNTER,
        "Multi-Shot": PlayerClass.HUNTER,
        "Holy Shock (dmg)": PlayerClass.PALADIN,
    },
    "gains_health_line": {
        "Rejuvenation": PlayerClass.DRUID,
        "Regrowth": PlayerClass.DRUID,
    },
    "begins_to_cast_line": {
        "Shadow Bolt": PlayerClass.WARLOCK,
        "Rejuvenation": PlayerClass.DRUID,
        "Regrowth": PlayerClass.DRUID,
        "Wrath": PlayerClass.DRUID,
        # frostbolt not unique enough probably, eg frost oils
        "Fireball": PlayerClass.MAGE,
        "Scorch": PlayerClass.MAGE,
        "Polymorph": PlayerClass.MAGE,
        "Chain Heal": PlayerClass.SHAMAN,
        "Lesser Healing Wave": PlayerClass.SHAMAN,
        "Mind Blast": PlayerClass.PRIEST,
        "Smite": PlayerClass.PRIEST,
        "Heal": PlayerClass.PRIEST,
        "Flash Heal": PlayerClass.PRIEST,
        "Greater Heal": PlayerClass.PRIEST,
        "Prayer of Healing": PlayerClass.PRIEST,
        "Multi-Shot": PlayerClass.HUNTER,
        "Flash of Light": PlayerClass.PALADIN,
        "Holy Light": PlayerClass.PALADIN,
    },
    "begins_to_perform_line": {
        "Auto Shot": PlayerClass.HUNTER,
        "Trueshot": PlayerClass.HUNTER,
    },
    "casts_line": {
        "Windfury Totem": PlayerClass.SHAMAN,
        "Mana Tide Totem": PlayerClass.SHAMAN,
        "Grace of Air Totem": PlayerClass.SHAMAN,
        "Tranquil Air Totem": PlayerClass.SHAMAN,
        "Strength of Earth Totem": PlayerClass.SHAMAN,
        "Mana Spring Totem": PlayerClass.SHAMAN,
        "Searing Totem": PlayerClass.SHAMAN,
        "Fire Nova Totem": PlayerClass.SHAMAN,
        "Magma Totem": PlayerClass.SHAMAN,
        "Ancestral Spirit": PlayerClass.SHAMAN,
        "Redemption": PlayerClass.PALADIN,
        "Resurrection": PlayerClass.PRIEST,
        "Rebirth": PlayerClass.DRUID,
    },
}


class ClassDetection:
    def __init__(self, player):
        self.store: Dict[str, PlayerClass] = dict()
        self.player = player

    def remove_unknown(self):
        knowns = set(self.player)
        for name in list(self.store):
            if name not in knowns:
                del self.store[name]

    def is_class(self, cls: PlayerClass, name: str) -> bool:
        if name not in self.store:
            return False
        return self.store[name] is cls

    def detect(self, line_type: str, name: str, spell: str):
        if line_type not in UNIQUE_LINE2SPELL2CLASS:
            return
        spell2class = UNIQUE_LINE2SPELL2CLASS[line_type]
        if spell not in spell2class:
            return

        detected_class: PlayerClass = spell2class[spell]

        if name not in self.store:
            self.store[name] = detected_class
            return

        # sanity check if a player is detected as a different class
        # if self.store.get(name) is not detected_class:
        #     logging.warning(
        #         f"{name} re-detected from {self.store[name].value} to {detected_class.value} via {spell}"
        #     )
        #     # decide on a strategy: overwrite, keep first, error
        #     self.store[name] = detected_class # overwrite

    def print(self, output):
        print("\n\nClass Detection", file=output)
        for name in sorted(self.player):
            player_class = self.store.get(name, PlayerClass.UNKNOWN)
            print("  ", name, player_class.value, file=output)


class Infographic:
    BACKGROUND_COLOR = "#282B2C"
    CLASS_COLOURS: Dict[PlayerClass, str] = {
        PlayerClass.DRUID: "#FF7D0A",
        PlayerClass.HUNTER: "#ABD473",
        PlayerClass.MAGE: "#69CCF0",
        PlayerClass.PALADIN: "#F58CBA",
        PlayerClass.PRIEST: "#FFFFFF",
        PlayerClass.ROGUE: "#FFF569",
        PlayerClass.SHAMAN: "#0070DE",
        PlayerClass.WARLOCK: "#9482C9",
        PlayerClass.WARRIOR: "#C79C6E",
        PlayerClass.UNKNOWN: "#660099",
    }
    DEFAULT_FILENAME = "infographic"

    def __init__(
        self,
        accumulator: ConsumablesAccumulator,
        class_detection: ClassDetection = None,
        title: str = "",
    ):
        self.accumulator = accumulator
        self.detected_classes: Dict[str, PlayerClass] = (
            class_detection.store if class_detection else {}
        )
        self.title = title

    def generate(self, output_file: Path = None) -> None:
        players = sorted(self.accumulator.data, key=lambda entry: -entry.total_spent)
        names = [e.name for e in players]
        colors = [
            self.CLASS_COLOURS[self.detected_classes.get(name, PlayerClass.UNKNOWN)]
            for name in names
        ]
        bar_values = [p.total_spent for p in players]

        width = 3
        height = len(players) // width + 2
        specs = [[{"type": "xy", "colspan": width}] + [None] * (width - 1)]
        specs.extend([[{"type": "domain"}] * width] * (height - 1))
        bar_chart_height = 400
        pie_chart_height = 500

        fig = make_subplots(
            rows=height,
            cols=width,
            row_heights=[bar_chart_height] + [pie_chart_height] * (height - 1),
            subplot_titles=[None] + names,
            specs=specs,
        )

        fig.add_trace(
            go.Bar(
                x=names,
                y=bar_values,
                marker=dict(color=colors),
                name="Gold spent",
                showlegend=False,
                text=[v.to_string(short=True) for v in bar_values],
                textposition="outside",
            ),
            row=1,
            col=1,
        )

        for pos, player in enumerate(players):
            item_costs = [items.total_price for items in player.consumables]
            item_texts = [
                f"x{items.amount}, {items.total_price.to_string(short=True)}"
                for items in player.consumables
            ]

            fig.add_trace(
                go.Pie(
                    labels=[c.item_name for c in player.consumables],
                    values=item_costs,
                    text=item_texts,
                    showlegend=False,
                    textposition="inside",
                    textinfo="label+percent+text",
                    name=player.name,
                ),
                row=(pos // width) + 2,
                col=(pos % width) + 1,
            )

        fig.update_layout(
            title=self.title,
            template="plotly_dark",
            plot_bgcolor=self.BACKGROUND_COLOR,
            paper_bgcolor=self.BACKGROUND_COLOR,
            title_x=0.5,
            height=bar_chart_height + (pie_chart_height * height - 1),
        )

        bg_script = f'document.body.style.backgroundColor = "{self.BACKGROUND_COLOR}"; '
        output = fig.to_html(post_script=[bg_script])

        filename = output_file or self.DEFAULT_FILENAME
        filepath = Path(filename).with_suffix(".html")

        if check_existing_file(filepath):
            while check_existing_file(
                filepath := filepath.with_stem(f"{filename}_{str(uuid4())[-4:]}")
            ):
                pass

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"Infographic saved to: {filepath}")


def parse_line(app, line):
    try:
        if line == "\n":
            return False

        # no ts, nothing to do
        p_ts_end = line.find("  ")
        if p_ts_end == -1:
            return False

        tree = app.parser.parse(line, p_ts_end)
        if not tree:
            return False

        return parse_line2(app, line, tree)

    except ParserError:
        # parse errors ignored to try different strategies
        # print(line)
        # print(app.parser.parse(line))
        # raise
        return False

    except Exception:
        logging.exception(line)
        raise


def parse_line2(app, line, tree: Tree):
    """
    returns True when a match is found, so we can stop trying different parsers
    """
    timestamp = tree.children[0]
    subtree = tree.children[1]

    timestamp_unix = parse_ts2unixtime(timestamp)

    # inline some parsing to reduce funcalls
    # for same reason not using visitors to traverse the parse tree
    if subtree.data == "gains_line":
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        stackcount = int(subtree.children[2].value)

        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
        app.spell_count.add_stackcount(
            line_type=subtree.data,
            name=name,
            spell=spellname,
            stackcount=stackcount,
        )
        app.proc_count.add(line_type=subtree.data, name=name, spell=spellname)

        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1

        if spellname in BUFF_SPELL:
            app.player_detect[name].add("buff: " + spellname)

        if spellname == "Armor Shatter":
            app.annihilator.add(line)
        if spellname == "Flame Buffet":
            app.flamebuffet.add(line)

        if name == "Princess Huhuran" and spellname in {"Frenzy", "Berserk"}:
            app.huhuran.add(line)
        if name == "Gluth" and spellname == "Frenzy":
            app.gluth.add(line)

        return True
    elif subtree.data == "gains_rage_line":
        name = subtree.children[0].value
        spellname = subtree.children[3].value

        spellname = rename_spell(spellname, line_type=subtree.data)
        app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)

        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1
        return True
    elif subtree.data == "gains_energy_line":
        return True
    elif subtree.data == "gains_health_line":
        targetname = subtree.children[0].value
        amount = int(subtree.children[1].value)
        name = subtree.children[2].value
        spellname = subtree.children[3].value

        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)

        app.healstore.add(name, targetname, spellname, amount, timestamp_unix)
        return True
    elif subtree.data == "uses_line":
        name = subtree.children[0].value
        spellname = subtree.children[1].value

        spellname = USES_CONSUMABLE_RENAME.get(spellname, spellname)
        consumable_item = RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname))
        if consumable_item and isinstance(consumable_item, SuperwowConsumable):
            if isinstance(consumable_item.strategy, IgnoreStrategy):
                return True  # Parsed and explicitly ignored

            # For all other strategies (Safe, Enhance, Overwrite, or any future ones)
            # on a SuperwowConsumable, add it to player_superwow for merging.
            app.player_superwow[name][consumable_item.name] += 1
            return True  # Parsed and staged for merge

        # If RAWSPELLNAME2CONSUMABLE.get found nothing or not a superwow consumable
        app.player_superwow_unknown[name][spellname] += 1
        return True

    elif subtree.data == "dies_line":
        name = subtree.children[0].value
        app.death_count[name] += 1

        if name == "Princess Huhuran":
            app.huhuran.add(line)
        if name == "Gluth":
            app.gluth.add(line)

        return True
    elif subtree.data == "heals_line":
        is_crit = subtree.children[2].value == "critically"

        name = subtree.children[0].value
        spellname = subtree.children[1].value

        targetname = subtree.children[3].value
        amount = int(subtree.children[4].value)

        spellname = rename_spell(spellname, line_type=subtree.data)

        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
        app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)

        if spellname == "Tea with Sugar":
            app.player[name]["Tea with Sugar"] += 1
        elif spellname == "Healing Potion":
            if is_crit:
                consumable = healpot_lookup(amount / 1.5)
            else:
                consumable = healpot_lookup(amount)
            app.player[name][consumable] += 1
        elif spellname == "Rejuvenation Potion":
            if amount > 500:
                app.player[name]["Rejuvenation Potion - Major"] += 1
            else:
                app.player[name]["Rejuvenation Potion - Minor"] += 1

        app.healstore.add(name, targetname, spellname, amount, timestamp_unix)
        return True

    elif subtree.data == "gains_mana_line":
        name = subtree.children[0].value
        spellname = subtree.children[-1].value
        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1
        if spellname == "Restore Mana":
            mana = int(subtree.children[1].value)
            consumable = manapot_lookup(mana)
            app.player[name][consumable] += 1
        return True
    elif subtree.data == "drains_mana_line":
        return True
    elif subtree.data == "drains_mana_line2":
        return True
    elif subtree.data == "begins_to_cast_line":
        name = subtree.children[0].value
        spellname = subtree.children[-1].value

        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)

        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1

        if name == "Kel'Thuzad" and spellname == "Frostbolt":
            app.kt_frostbolt.begins_to_cast(line)

        return True
    elif subtree.data == "casts_line":
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1

        if spellname == "Sunder Armor":
            if len(subtree.children) < 3:
                # a mystery sunder armor with no target
                targetname = "unknown"
            else:
                targetname = subtree.children[2].value
            if targetname in KNOWN_BOSS_NAMES:
                spellname += " (boss)"

        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
        app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)

        if spellname == "Wild Polymorph":
            app.nef_wild_polymorph.add(line)

        if spellname == "Death by Peasant":
            app.huhuran.add(line)

        if len(subtree.children) == 3:
            targetname = subtree.children[2].value

            if spellname == "Tranquilizing Shot" and targetname == "Princess Huhuran":
                app.huhuran.add(line)
            if spellname == "Tranquilizing Shot" and targetname == "Gluth":
                app.gluth.add(line)

        if name == "Kel'Thuzad" and spellname == "Shadow Fissure":
            app.kt_shadowfissure.add(line)

        return True
    elif subtree.data == "combatant_info_line":
        return True
    elif subtree.data == "consolidated_line":
        for entry in subtree.children:
            if entry.data == "consolidated_pet":
                name = entry.children[0].value
                petname = entry.children[1].value
                app.pet_handler.add(name, petname)
                app.player_detect[name].add("pet: " + petname)
            else:
                # parse but ignore the other consolidated entries
                pass
        return True
    elif subtree.data == "hits_ability_line":
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        targetname = subtree.children[2].value
        amount = int(subtree.children[3].value)

        spellname = rename_spell(spellname, line_type=subtree.data)

        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
        app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)

        if spellname in app.hits_consumable.COOLDOWNS:
            app.hits_consumable.update(name, spellname, timestamp_unix)

        if targetname == "Viscidus":
            app.viscidus.found()
            spell_damage_type = subtree.children[4]
            if spell_damage_type.value == "Frost":
                app.viscidus.add(name, spellname)

        if targetname == "Princess Huhuran":
            app.huhuran.found()

        if name == "Eye of C'Thun" and spellname == "Eye Beam":
            app.cthun_chain.add(timestamp_unix, line)

        if name == "Gluth" and spellname == "Decimate":
            app.gluth.add(line)

        if name == "Sir Zeliek" and spellname == "Holy Wrath":
            app.fourhm_chain.add(timestamp_unix, line)

        if spellname in INTERRUPT_SPELLS and targetname == "Kel'Thuzad":
            app.kt_frostbolt.add(line)

        if (
            name == "Kel'Thuzad"
            and spellname == "Frostbolt"
            and int(subtree.children[3].value) >= 4000
        ):
            app.kt_frostbolt.add(line)

        if name == "Kel'Thuzad" and spellname == "Frost Blast":
            app.kt_frostblast.add(line)

        if name == "Shadow Fissure" and spellname == "Void Blast":
            app.kt_shadowfissure.add(line)

        app.dmgstore.add(name, targetname, spellname, amount, timestamp_unix)
        app.dmgtakenstore.add(name, targetname, spellname, amount, timestamp_unix)

        return True
    elif subtree.data == "hits_autoattack_line":
        name = subtree.children[0].value
        target = subtree.children[1].value
        amount = int(subtree.children[2].value)

        if name == "Guardian of Icecrown":
            app.kt_guardian.add(line)
        app.dmgstore.add(name, target, "hit", amount, timestamp_unix)
        app.dmgtakenstore.add(name, target, "hit", amount, timestamp_unix)
        return True
    elif subtree.data == "parry_ability_line":
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        targetname = subtree.children[2].value

        if spellname in INTERRUPT_SPELLS and targetname == "Kel'Thuzad":
            app.kt_frostbolt.parry(line)

        return True
    elif subtree.data == "parry_line":
        return True
    elif subtree.data == "block_line":
        return True
    elif subtree.data == "block_ability_line":
        return True
    elif subtree.data == "interrupts_line":
        return True

    elif subtree.data == "resist_line":
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        targetname = subtree.children[2].value

        if spellname in app.hits_consumable.COOLDOWNS:
            app.hits_consumable.update(name, spellname, timestamp_unix)

        if spellname == "Armor Shatter":
            app.annihilator.add(line)

        if name == "Eye of C'Thun" and spellname == "Eye Beam":
            app.cthun_chain.add(timestamp_unix, line)

        if name == "Sir Zeliek" and spellname == "Holy Wrath":
            app.fourhm_chain.add(timestamp_unix, line)

        if spellname in INTERRUPT_SPELLS and targetname == "Kel'Thuzad":
            app.kt_frostbolt.parry(line)

        return True
    elif subtree.data == "immune_ability_line":
        name = subtree.children[0].value
        spellname = subtree.children[1].value

        if spellname in app.hits_consumable.COOLDOWNS:
            app.hits_consumable.update(name, spellname, timestamp_unix)

        return True
    elif subtree.data == "is_immune_ability_line":
        targetname = subtree.children[0].value
        name = subtree.children[1].value
        spellname = subtree.children[2].value
        if spellname in app.hits_consumable.COOLDOWNS:
            app.hits_consumable.update(name, spellname, timestamp_unix)
        return True

    elif subtree.data == "immune_line":
        return True
    elif subtree.data == "afflicted_line":
        targetname = subtree.children[0].value
        spellname = subtree.children[1].value

        app.class_detection.detect(line_type=subtree.data, name=targetname, spell=spellname)
        app.spell_count.add(line_type=subtree.data, name=targetname, spell=spellname)

        if spellname == "Armor Shatter":
            app.annihilator.add(line)
        if spellname == "Decimate":
            app.gluth.add(line)
        if spellname == "Frost Blast":
            app.kt_frostblast.add(line)

        if targetname == "Guardian of Icecrown":
            app.kt_guardian.add(line)

        return True
    elif subtree.data == "is_destroyed_line":
        return True
    elif subtree.data == "is_absorbed_ability_line":
        name = subtree.children[0].value
        spellname = subtree.children[1].value

        if spellname == "Corrupted Healing":
            app.nef_corrupted_healing.add(line)

        if name == "Eye of C'Thun" and spellname == "Eye Beam":
            app.cthun_chain.add(timestamp_unix, line)

        if name == "Sir Zeliek" and spellname == "Holy Wrath":
            app.fourhm_chain.add(timestamp_unix, line)

        if name == "Kel'Thuzad" and spellname == "Frost Blast":
            app.kt_frostblast.add(line)

        return True
    elif subtree.data == "absorbs_ability_line":
        targetname = subtree.children[0].value
        name = subtree.children[1].value
        spellname = subtree.children[2].value
        if spellname == "Corrupted Healing":
            app.nef_corrupted_healing.add(line)
        return True
    elif subtree.data == "absorbs_all_line":
        return True
    elif subtree.data == "fails_to_dispel_line":
        return True
    elif subtree.data == "pet_begins_eating_line":
        return True
    elif subtree.data == "is_dismissed_line":
        name = subtree.children[0].value
        petname = subtree.children[1].value
        app.pet_handler.add(name, petname)
        return True
    elif subtree.data == "is_dismissed_line2":
        name, petname = subtree.children[0].value.split(" ", 1)
        if name[-2:] == "'s":
            name = name[:-2]
        app.pet_handler.add(name, petname)
        return True
    elif subtree.data == "gains_happiness_line":
        petname = subtree.children[0].value
        amount = subtree.children[1].value
        name = subtree.children[2].value
        app.pet_handler.add(name, petname)
        return True
    elif subtree.data == "removed_line":
        name = subtree.children[0].value
        spellname = subtree.children[1].value

        if name == "Princess Huhuran" and spellname == "Frenzy":
            app.huhuran.add(line)

        if name == "Gluth" and spellname == "Frenzy":
            app.gluth.add(line)

        return True
    elif subtree.data == "suffers_line":
        targetname = subtree.children[0].value
        amount = int(subtree.children[1])
        if subtree.children[2].data == "suffers_line_source":
            name = subtree.children[2].children[1].value
            spellname = subtree.children[2].children[2].value

            if spellname == "Corrupted Healing":
                app.nef_corrupted_healing.add(line)

            app.dmgstore.add(name, targetname, spellname, amount, timestamp_unix)
            app.dmgtakenstore.add(name, targetname, spellname, amount, timestamp_unix)
        else:
            # nosource
            pass

        return True
    elif subtree.data == "fades_line":
        spellname = subtree.children[0].value
        targetname = subtree.children[1].value

        if spellname == "Armor Shatter":
            app.annihilator.add(line)
        if targetname == "Guardian of Icecrown":
            app.kt_guardian.add(line)

        return True
    elif subtree.data == "slain_line":
        return True
    elif subtree.data == "creates_line":
        return True
    elif subtree.data == "is_killed_line":
        return True
    elif subtree.data == "performs_on_line":
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        targetname = subtree.children[2].value

        if consumable_item := RAWSPELLNAME2CONSUMABLE.get((subtree.data, spellname)):
            app.player[name][consumable_item.name] += 1

        return True
    elif subtree.data == "performs_line":
        return True
    elif subtree.data == "begins_to_perform_line":
        name = subtree.children[0].value
        spellname = subtree.children[-1].value
        app.class_detection.detect(line_type=subtree.data, name=name, spell=spellname)
        app.spell_count.add(line_type=subtree.data, name=name, spell=spellname)
        return True
    elif subtree.data == "gains_extra_attacks_line":
        name = subtree.children[0].value
        howmany = int(subtree.children[1].value)
        source = subtree.children[2].value
        app.proc_count.add_extra_attacks(howmany=howmany, name=name, source=source)
        return True
    elif subtree.data == "dodges_line":
        return True
    elif subtree.data == "dodge_ability_line":
        return True
    elif subtree.data == "reflects_damage_line":
        name = subtree.children[0].value
        amount = int(subtree.children[1].value)
        target = subtree.children[3].value
        app.dmgstore.add(name, target, "reflect", amount, timestamp_unix)
        app.dmgtakenstore.add(name, target, "reflect", amount, timestamp_unix)
        return True
    elif subtree.data == "causes_damage_line":
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        target = subtree.children[2].value
        amount = int(subtree.children[3].value)
        app.dmgstore.add(name, target, spellname, amount, timestamp_unix)
        app.dmgtakenstore.add(name, target, spellname, amount, timestamp_unix)
        return True
    elif subtree.data == "is_reflected_back_line":
        return True
    elif subtree.data == "misses_line":
        return True
    elif subtree.data == "misses_ability_line":
        return True
    elif subtree.data == "falls_line":
        return True
    elif subtree.data == "none_line":
        return True
    elif subtree.data == "lava_line":
        return True
    elif subtree.data == "slays_line":
        return True
    elif subtree.data == "was_evaded_line":
        name = subtree.children[0].value
        spellname = subtree.children[1].value
        targetname = subtree.children[2].value

        if spellname == "Wild Polymorph":
            app.nef_wild_polymorph.add(line)
        return True
    elif subtree.data == "equipped_durability_loss_line":
        return True

    return False


def parse_log(app, filename):
    app.techinfo.set_file_size(filename)

    with io.open(filename, encoding="utf8") as f:
        linecount = 0
        skiplinecount = 0
        for line in f:
            linecount += 1

            if parse_line(app, line):
                continue

            skiplinecount += 1

            app.unparsed_logger.log(line)

        app.techinfo.set_line_count(linecount)
        app.techinfo.set_skipped_line_count(skiplinecount)

        app.unparsed_logger.flush()
        app.unparsed_logger_fast.flush()


def generate_output(app):
    output = io.StringIO()

    print(
        """Notes:
    - The report is generated using the combat log, which is far from perfect.
    - Use the report as evidence something DID happen and keep in mind the data is not exhaustive. In other words the report DOES NOT cover everything.
    - Some events are missing because the person logging wasn't in the instance yet or was too far away. This means inferring something DID NOT happen may be hard or impossible and requires extra care.
    - This is called "open-world assumption" - missing information doesn't imply falsity.
    - Without superwow, many spells and consumables are not logged and can't be easily counted. Examples are jujus, many foods, mageblood and other mana consumables, lesser vs greater protection potions, gift of arthas etc.
    - Dragonbreath chili and goblin sappers have only "on hit" messages, so their usage is estimated based on timestamps and cooldowns.

""",
        file=output,
    )

    # remove pets from players
    for pet in app.pet_handler.get_all_pets():
        if pet in app.player_detect:
            del app.player_detect[pet]

    # add players detected
    for name in app.player_detect:
        app.player[name]

    # remove unknowns from class detection
    app.class_detection.remove_unknown()

    # merge superwow extra data so everything else can see it
    app.merge_superwow_consumables.merge()

    # calculate consumables
    app.consumables_accumulator.calculate()

    app.print_consumables.print(output)

    app.sunder_armor_summary.print(output)
    app.cooldown_summary.print(output)
    app.proc_summary.print(output)

    # app.dmgstore.print_alphabetic(output)

    app.annihilator.print(output)
    app.flamebuffet.print(output)

    # bwl
    app.nef_corrupted_healing.print(output)
    app.nef_wild_polymorph.print(output)
    # aq
    app.viscidus.print(output)
    app.huhuran.print(output)
    app.cthun_chain.print(output)
    # naxx
    app.gluth.print(output)
    app.fourhm_chain.print(output)
    app.kt_shadowfissure.print(output)
    app.kt_frostbolt.print(output)
    app.kt_frostblast.print(output)
    # app.kt_guardian.print(output)

    app.pet_handler.print(output)
    app.class_detection.print(output)
    app.techinfo.print(output)

    return output


def write_output(
    output,
    write_summary,
):
    if write_summary:
        filename = "summary.txt"
        with open(filename, "wb") as f:
            f.write(output.getvalue().encode("utf8"))
            print("writing summary to", filename)
    else:
        print(output.getvalue())


def get_user_input(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "logpath",
        help="path to WoWCombatLog.txt or an url like https://turtlogs.com/viewer/8406/base?history_state=1",
    )
    parser.add_argument(
        "--pastebin",
        action="store_true",
        help="upload result to a pastebin and return the url",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        help="used with --pastebin. open the pastebin url with your browser",
    )

    parser.add_argument(
        "--write-summary",
        action="store_true",
        help="writes output to summary.txt instead of the console",
    )
    parser.add_argument(
        "--write-consumable-totals-csv",
        action="store_true",
        help="also writes consumable-totals.csv (name, copper, deaths)",
    )
    parser.add_argument(
        "--write-damage-output",
        action="store_true",
        help="writes output to damage-output.txt",
    )
    parser.add_argument(
        "--write-healing-output",
        action="store_true",
        help="writes output to healing-output.txt",
    )
    parser.add_argument(
        "--write-damage-taken-output",
        action="store_true",
        help="writes output to damage-taken-output.txt",
    )

    parser.add_argument(
        "--prices-server",
        choices=["nord", "telabim"],
        default="nord",
        help="specify which server price data to use",
    )

    parser.add_argument(
        "--visualize",
        action="store_true",
        required=False,
        help="Generate visual infographic",
    )
    parser.add_argument(
        "--compare-players",
        nargs=2,
        metavar=("PLAYER1", "PLAYER2"),
        required=False,
        help="compare 2 players, output the difference in compare-players.txt",
    )

    parser.add_argument(
        "--expert-log-unparsed-lines",
        action="store_true",
        help="create an unparsed.txt with everything that was not parsed",
    )
    parser.add_argument(
        "--expert-write-web-prices",
        action="store_true",
        help="writes output to prices-web.json",
    )
    parser.add_argument(
        "--expert-disable-web-prices",
        action="store_true",
        help="don't download price data",
    )
    parser.add_argument(
        "--expert-deterministic-logs",
        action="store_true",
        help="disable environmental outputs",
    )
    parser.add_argument("--expert-log-superwow-merge", action="store_true")

    args = parser.parse_args(argv)

    return args


class IxioUploader:
    def upload(self, output):
        data = output.getvalue().encode("utf8")

        username, password = "summarize_consumes", "summarize_consumes"
        auth = requests.auth.HTTPBasicAuth(username, password)
        response = requests.post(
            url="http://ix.io",
            files={"f:1": data},
            auth=auth,
            timeout=30,
        )
        print(response.text)
        if "already exists" in response.text:
            return None
        if "down for DDOS" in response.text:
            return None
        if "ix.io is taking a break" in response.text:
            return None
        if response.status_code != 200:
            return None
        url = response.text.strip().split("\n")[-1]
        return url


class RpasteUploader:
    def upload(self, output):
        data = output.getvalue().encode("utf8")
        response = requests.post(
            url="https://rpa.st/curl",
            data={"raw": data, "expiry": "forever"},
            timeout=30,
        )
        if response.status_code != 200:
            print(response.text)
            return None
        lines = response.text.splitlines()
        for line in lines:
            if "Raw URL" in line:
                url = line.split()[-1]
                return url


class BpasteUploader:
    def upload(self, output):
        data = output.getvalue().encode("utf8")
        response = requests.post(
            # url='https://bpaste.net/curl',
            url="https://bpa.st/curl",
            data={"raw": data, "expiry": "1month"},
            timeout=30,
        )
        if response.status_code != 200:
            print(response.text)
            return None
        lines = response.text.splitlines()
        for line in lines:
            if "Raw URL" in line:
                url = line.split()[-1]
                return url


def upload_pastebin(output):
    url = BpasteUploader().upload(output)
    if not url:
        url = RpasteUploader().upload(output)
    if not url:
        url = IxioUploader().upload(output)
    if url:
        print("pastebin url", url)
    else:
        print("couldn't get a pastebin url")
    return url


def open_browser(url):
    print(f"opening browser with {url}")
    webbrowser.open(url)


class LogDownloader:
    def __init__(self):
        self.output_name = "summarize-consumes-turtlogs.txt"

    def try_download(self, filename):
        output_name = self.output_name
        if os.path.exists(filename):
            return filename

        urlprefixes = [
            "https://www.turtlogs.com/viewer/",
            "https://turtlogs.com/viewer/",
        ]
        found = False
        for urlprefix in urlprefixes:
            if filename.startswith(urlprefix):
                newfilename = filename[len(urlprefix) :]
                found = True
                break
        if not found:
            return filename

        try:
            logid = newfilename.split("/")[0]
            logid = int(logid)
            resp = requests.get(f"https://turtlogs.com/API/instance/export/{logid}")
            resp.raise_for_status()

            upload_id = resp.json()["upload_id"]

            resp = requests.get(f"https://www.turtlogs.com/uploads/upload_{upload_id}.zip")
            resp.raise_for_status()

            zip_buffer = io.BytesIO(resp.content)

            with zipfile.ZipFile(zip_buffer) as zip_file:
                file_list = zip_file.namelist()

                if not file_list:
                    raise ValueError("ZIP file is empty")

                text_file_name = file_list[0]

                with zip_file.open(text_file_name) as text_file:
                    content = text_file.read()

                with open(output_name, "wb") as output_file:
                    print("writing downloaded log to", output_name)
                    output_file.write(content)
                return output_name

        except ValueError:
            pass
        return filename


class MergeSuperwowConsumables:
    def __init__(
        self,
        player,
        player_superwow,
        player_superwow_unknown,
        expert_log_superwow_merge,
    ):
        self.player = player
        self.player_superwow = player_superwow
        self.player_superwow_unknown = player_superwow_unknown
        self.logfile = None
        self.filename = "superwow-merge.txt"
        if expert_log_superwow_merge:
            self.logfile = open(self.filename, "w")

    def log(self, txt):
        if not self.logfile:
            return
        print(txt, file=self.logfile)

    def merge(self):
        if self.logfile:
            print("writing superwow merge to", self.filename)

        # note that both player and player_superwow map a canonical consumable
        # name (from all_defined_consumable_items) to its count.
        # you can investigate eg. the uses_line and gains_line code to
        # convince yourself it's true
        #
        # so the c and c_swow names are only different in how they are used.
        # c is used for the native counts in player
        # c_swow is used for the superwow counts in player_superwow
        #
        # it follows that when c == c_swow, we are looking at the same consumable,
        # but with data from the native and superwow logs respectively.
        # so when c != c_swow, we are comparing different consumables. probably
        # an ambiguous one and a more specific superwow one.

        for player in self.player_superwow:
            consumables_swow = set(self.player_superwow[player])
            consumables = set(self.player[player])
            for c_swow in consumables_swow:
                consumable = NAME2CONSUMABLE.get(c_swow)

                match consumable:
                    case None:
                        self.log(f"impossible! consumable not found {c_swow}")
                        continue

                    case SuperwowConsumable(strategy=SafeStrategy()):
                        if self.player[player].get(c_swow, 0):
                            self.log(f"impossible! consumable not safe {consumable}")
                        self.player[player][c_swow] = self.player_superwow[player][c_swow]
                        del self.player_superwow[player][c_swow]

                    case SuperwowConsumable(strategy=EnhanceStrategy()):
                        self.player[player][c_swow] = max(
                            self.player_superwow[player][c_swow], self.player[player][c_swow]
                        )
                        del self.player_superwow[player][c_swow]

                    case SuperwowConsumable(strategy=OverwriteStrategy(target_consumable_name=c)):
                        # will try to delete the native counts with the old name and use the new name coming from superwow
                        # eg. the prot pots have non-specific native names, but with superwow the specific name shows up
                        c = consumable.strategy.target_consumable_name

                        if (
                            c != c_swow
                            and self.player[player].get(c, 0) > self.player_superwow[player][c_swow]
                        ):
                            self.log(f"partial merge (overwrite). {player} {c} > {c_swow}")

                            remain = self.player[player][c] - self.player_superwow[player][c_swow]
                            self.player[player][c] = remain
                            self.player[player][c_swow] = self.player_superwow[player][c_swow]
                            del self.player_superwow[player][c_swow]

                            continue

                        self.player[player].pop(c, None)  # might not exist
                        self.player[player][c_swow] = self.player_superwow[player][c_swow]
                        del self.player_superwow[player][c_swow]

                    case _:
                        self.log(f"{c_swow} not known??")
                        continue

        all_unknown = set()
        for player, consumables in self.player_superwow_unknown.items():
            self.log(f"unknown consumables for {player}: {consumables}")
            for cons in consumables:
                all_unknown.add(cons)

        self.log("all unknown suggestions:")
        for cons in all_unknown:
            self.log(repr({cons: cons}))

        def printer(player):
            for player, cons in player.items():
                for cname, count in cons.items():
                    self.log(f"{player} {cname} {count}")

        self.log("data dumps:")
        # self.log(f'self.player:')
        # printer(self.player)
        self.log("self.player_superwow:")
        printer(self.player_superwow)
        self.log("self.player_superwow_unknown:")
        printer(self.player_superwow_unknown)


def main(argv):
    args = get_user_input(argv)

    time_start = time.time()
    app = create_app(
        time_start=time_start,
        expert_log_unparsed_lines=args.expert_log_unparsed_lines,
        prices_server=args.prices_server,
        expert_disable_web_prices=args.expert_disable_web_prices,
        expert_deterministic_logs=args.expert_deterministic_logs,
        expert_log_superwow_merge=args.expert_log_superwow_merge,
    )

    logpath = app.log_downloader.try_download(filename=args.logpath)

    parse_log(app, filename=logpath)

    output = generate_output(app)

    if args.write_consumable_totals_csv:

        def feature():
            output = io.StringIO()
            app.print_consumable_totals_csv.print(output)

            filename = "consumable-totals.csv"
            with open(filename, "wb") as f:
                f.write(output.getvalue().encode("utf8"))
                print("writing consumable totals to", filename)

        feature()

    if args.compare_players:

        def feature():
            player1, player2 = args.compare_players
            player1 = player1.capitalize()
            player2 = player2.capitalize()

            output = io.StringIO()
            app.dmgstore.print_compare_players(player1=player1, player2=player2, output=output)

            filename = "compare-players.txt"
            with open(filename, "wb") as f:
                print("writing comparison of players to", filename)
                f.write(output.getvalue().encode("utf8"))

        feature()

    if args.write_damage_output:

        def feature():
            output = io.StringIO()
            app.dmgstore.print_damage(output=output)
            filename = "damage-output.txt"
            with open(filename, "wb") as f:
                print("writing damage output to", filename)
                f.write(output.getvalue().encode("utf8"))
                if args.pastebin:
                    upload_pastebin(output)

        feature()

    if args.write_healing_output:

        def feature():
            output = io.StringIO()
            app.healstore.print_damage(output=output)
            filename = "healing-output.txt"
            with open(filename, "wb") as f:
                print("writing healing output to", filename)
                f.write(output.getvalue().encode("utf8"))
                if args.pastebin:
                    upload_pastebin(output)

        feature()

    if args.write_damage_taken_output:

        def feature():
            output = io.StringIO()
            app.dmgtakenstore.print_damage_taken(output=output)
            filename = "damage-taken-output.txt"
            with open(filename, "wb") as f:
                print("writing damage taken output to", filename)
                f.write(output.getvalue().encode("utf8"))
                if args.pastebin:
                    upload_pastebin(output)

        feature()

    if args.visualize:
        app.infographic.generate(output_file=Path(logpath).stem)

    if args.expert_write_web_prices:

        def feature():
            prices = app.web_price_provider.load()
            filename = "prices-web.json"
            with open(filename, "w", newline="") as f:
                print("writing web prices to", filename)
                json.dump(prices, f, indent=4)

        feature()

    write_output(output, write_summary=args.write_summary)
    if not args.pastebin:
        return
    url = upload_pastebin(output)

    if not args.open_browser:
        return
    if not url:
        return
    open_browser(url)


if __name__ == "__main__":
    main(sys.argv[1:])
