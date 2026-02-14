from melbalabs.summarize_consumes.parser import TreeType
import bisect
import collections


class TimelineEntry:
    def __init__(
        self,
        timestamp_unix,
        source,
        spellname,
        line_type,
        amount,
        boss_context,
    ):
        self.timestamp_unix = timestamp_unix
        self.source = source
        self.spellname = spellname
        self.line_type = line_type
        self.amount = amount
        self.boss_context = boss_context


class AbilityTimeline:
    def __init__(self, known_bosses, player, dmgstore, cdspell_class, tracked_spells):
        self.known_boss_names = set(known_bosses.keys())
        self.player = player
        self.dmgstore = dmgstore

        self.mob_to_boss = {}

        for boss, mobs in known_bosses.items():
            for mob in mobs:
                self.mob_to_boss[mob] = boss

        # build a fast lookup set of important spells
        self._important_spells = set()
        for _, spells in cdspell_class:
            for spell in spells:
                self._important_spells.add(spell)

        for spell in tracked_spells:
            self._important_spells.add(spell)

        self.entries = []
        self.boss_entries = []
        self.damage_entries = []

    def is_important(self, spellname):
        return spellname in self._important_spells

    def add(self, source, target, spellname, line_type: TreeType, timestamp_unix, amount):
        boss_context = None
        if target in self.known_boss_names:
            boss_context = target
        elif target in self.mob_to_boss:
            boss_context = self.mob_to_boss[target]
        elif source in self.known_boss_names:
            boss_context = source
        elif source in self.mob_to_boss:
            boss_context = self.mob_to_boss[source]

        keep = False
        if boss_context:
            keep = True
        elif source in self.player and self.is_important(spellname):
            keep = True

        if not keep:
            return

        entry = TimelineEntry(
            timestamp_unix=timestamp_unix,
            source=source,
            spellname=spellname,
            line_type=line_type,
            amount=amount,
            boss_context=boss_context,
        )
        self.entries.append(entry)
        if boss_context:
            self.boss_entries.append(entry)
            is_dmg_to_boss = target in self.known_boss_names or target in self.mob_to_boss
            if amount > 0 and is_dmg_to_boss:
                self.damage_entries.append(entry)

    def add_extra_attacks(self, howmany, name, source, timestamp_unix):
        if source != "Windfury Totem":
            return

        # use the same spellname as the aura so they group together
        spellname = "Windfury Totem"

        for _ in range(howmany):
            self.add(
                source=name,
                target=name,
                spellname=spellname,
                line_type=TreeType.GAINS_EXTRA_ATTACKS_LINE,
                timestamp_unix=timestamp_unix,
                amount=0,
            )

    def print(self, output):
        if not self.entries:
            print("<nothing found>", file=output)
            return

        DIFF_SEC = 15

        # re-assign targets for important spells that are self-cast
        # or cast on non-boss targets
        # we want to group them with the boss fight they belong to
        # so we look for the closest boss event use the same target

        self.boss_entries.sort(key=lambda e: e.timestamp_unix)
        boss_event_timestamps = [e.timestamp_unix for e in self.boss_entries]

        self.damage_entries.sort(key=lambda e: e.timestamp_unix)
        damage_event_timestamps = [e.timestamp_unix for e in self.damage_entries]

        # group entries by boss context
        by_boss_context = collections.defaultdict(list)

        for entry in self.entries:
            candidate_boss_context = entry.boss_context
            if not candidate_boss_context and self.boss_entries:
                # find closest boss event
                idx = bisect.bisect_left(boss_event_timestamps, entry.timestamp_unix)
                best_boss = None
                min_diff = DIFF_SEC + 0.1  # within DIFF_SEC of a boss event

                if idx < len(self.boss_entries):
                    diff = abs(entry.timestamp_unix - self.boss_entries[idx].timestamp_unix)
                    if diff < min_diff:
                        min_diff = diff
                        best_boss = self.boss_entries[idx]
                if idx > 0:
                    diff = abs(entry.timestamp_unix - self.boss_entries[idx - 1].timestamp_unix)
                    if diff < min_diff:
                        min_diff = diff
                        best_boss = self.boss_entries[idx - 1]

                if best_boss:
                    candidate_boss_context = best_boss.boss_context

            if candidate_boss_context:
                # verify we are within DIFF_SEC of ANY damage entry
                # to avoid assigning pre-pull casts
                best_dmg_diff = DIFF_SEC + 0.1
                idx_dmg = bisect.bisect_left(damage_event_timestamps, entry.timestamp_unix)
                if idx_dmg < len(damage_event_timestamps):
                    best_dmg_diff = min(
                        best_dmg_diff,
                        abs(entry.timestamp_unix - damage_event_timestamps[idx_dmg]),
                    )
                if idx_dmg > 0:
                    best_dmg_diff = min(
                        best_dmg_diff,
                        abs(entry.timestamp_unix - damage_event_timestamps[idx_dmg - 1]),
                    )

                if best_dmg_diff <= DIFF_SEC:
                    is_direct_target = entry.boss_context == candidate_boss_context
                    if entry.amount == 0 or is_direct_target:
                        by_boss_context[candidate_boss_context].append(entry)

        for boss_context, entries in by_boss_context.items():
            # sort entries by timestamp
            entries.sort(key=lambda e: e.timestamp_unix)

            start_time = entries[0].timestamp_unix
            end_time = entries[-1].timestamp_unix
            duration = end_time - start_time

            if duration <= 0:
                duration = 1

            print(f"\n\nAbility Timeline for {boss_context} ({duration:.1f}s)", file=output)

            # identify all players involved
            players_involved = list(set(e.source for e in entries if e.source in self.player))

            # damage to ANY target during this time window
            # used for sorting
            impact_damage = collections.defaultdict(lambda: collections.defaultdict(int))
            for e in entries:
                impact_damage[e.source][e.spellname] += e.amount

            def get_player_target_dmg(p):
                return sum(impact_damage[p].values())

            # sort players by damage to this target
            players_involved.sort(key=get_player_target_dmg, reverse=True)

            scale = 1.0  # seconds per output character
            width = int(duration * scale)

            # Name                 0....+....10...+....20...
            print(f"{'Player (dmg) / Spell (dmg)':<40} Time (seconds) ->", file=output)

            # time axis
            axis = " " * (width + 1)
            axis_list = list(axis)
            for i in range(0, int(duration) + 5, 5):
                pos = int(i * scale)
                if pos <= width:
                    if i % 10 == 0:
                        s = str(i)
                        for k, c in enumerate(s):
                            if pos + k <= width:
                                axis_list[pos + k] = c
                    else:
                        if pos <= width and axis_list[pos] == " ":
                            axis_list[pos] = "'"
            print(" " * 40 + "".join(axis_list), file=output)

            for player in players_involved:
                player_entries = [e for e in entries if e.source == player]
                if not player_entries:
                    continue

                player_dmg = get_player_target_dmg(player)
                if player_dmg > 0:
                    print(f"{player} ({player_dmg})", file=output)
                else:
                    print(f"{player}", file=output)

                # group by spell hits on this target
                by_spell = collections.defaultdict(list)
                for e in player_entries:
                    by_spell[e.spellname].append(e)

                # sort spells. important first, then damage
                def get_spell_priority(spellname):
                    is_imp = self.is_important(spellname)
                    priority = 0 if is_imp else 1

                    # use the encounter-wide damage for this window
                    dmg = impact_damage[player][spellname]

                    return (priority, -dmg)

                sorted_spells = sorted(by_spell.keys(), key=get_spell_priority)

                for spellname in sorted_spells:
                    spell_entries = by_spell[spellname]

                    # build the row string
                    row = [" "] * (width + 1)
                    for e in spell_entries:
                        relative_time = e.timestamp_unix - start_time
                        pos = int(relative_time * scale)
                        if 0 <= pos < width:
                            symbol = "x"
                            if e.line_type == TreeType.GAINS_LINE:
                                symbol = "G"
                            elif e.line_type == TreeType.FADES_LINE:
                                symbol = "F"
                            row[pos] = symbol

                    dmg = impact_damage[player][spellname]
                    dmg_str = f" ({dmg})" if dmg > 0 else ""
                    text = f"  {spellname}{dmg_str}"
                    print(f"{text:<40}" + "".join(row), file=output)
