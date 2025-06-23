import re
from typing import Optional


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


class FallbackParser:
    def parse(self, line):
        raise ParserError("unknown line")


class ParserError(Exception):
    pass


class Parser2:
    def __init__(self, unparsed_logger):
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
            msg = f"{e} {line} \n"
            self.unparsed_logger.log(msg)

        return None
