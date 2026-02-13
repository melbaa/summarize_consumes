class EncounterMobs:
    def __init__(self, known_boss_names, player):
        self.known_boss_names = known_boss_names
        self.player = player
        self.events = []  # (timestamp, source, target)
        self.boss_timestamps = []  # (timestamp, boss_name)

    def add(self, source, target, timestamp_unix):
        source = source.strip()
        target = target.strip()
        self.events.append((timestamp_unix, source, target))
        if source in self.known_boss_names:
            self.boss_timestamps.append((timestamp_unix, source))
        elif target in self.known_boss_names:
            self.boss_timestamps.append((timestamp_unix, target))

    def print(self, output):
        if not self.boss_timestamps:
            return

        # merged boss activity windows
        # Sort boss timestamps just in case they are out of order
        sorted_boss_ts = sorted(self.boss_timestamps)

        engagements = []  # List of { 'start': ts, 'end': ts, 'bosses': set }

        WINDOW = 30  # seconds to merge boss mentions into same engagement
        PROXIMITY = 60  # seconds around engagement to look for mobs

        for ts, name in sorted_boss_ts:
            if not engagements or ts > engagements[-1]["end"] + WINDOW:
                engagements.append({"start": ts, "end": ts, "bosses": {name}})
            else:
                engagements[-1]["end"] = ts
                engagements[-1]["bosses"].add(name)

        # filter mobs and associate with engagements
        # Junk filters
        junk_suffixes = (
            " Totem",
            " Totem I",
            " Totem II",
            " Totem III",
            " Totem IV",
            " Totem V",
            " Totem VI",
            " Totem VII",
        )
        junk_names = {
            "Environment",
            "Unknown",
            "Rat",
            "Maggot",
            "Bat",
            "Spore",
            "Searching Eye",
            "Arcanite Dragonling",
            "Battle Chicken",
            "Mechanical Yeti",
            "Barov Peasant",
            "Guardian Felhunter",
            "Void Zone",
            "Plague Fissure",
            "Grobbulus Cloud",
            "Web Wrap",
            "Shadow Fissure",
            "Explosive Trap II",
        }

        engagement_mobs = [set() for _ in range(len(engagements))]

        # Sort events by timestamp for efficient processing
        sorted_events = sorted(self.events, key=lambda x: x[0])

        # Use a sliding window / pointer approach for O(E + W) complexity
        eng_idx = 0
        for ts, source, target in sorted_events:
            # Advance engagement pointer if this event is way past the current one
            while eng_idx < len(engagements) and ts > engagements[eng_idx]["end"] + PROXIMITY:
                eng_idx += 1

            if eng_idx >= len(engagements):
                break

            # Check if event is within proximity of ANY engagement (it might overlap multiple)
            # For simplicity, we can just check the current and next few if needed,
            # but usually engagements are far apart.
            for i in range(eng_idx, len(engagements)):
                eng = engagements[i]
                if ts < eng["start"] - PROXIMITY:
                    break  # Events are sorted, so we can stop searching engagements

                if (
                    abs(ts - eng["start"]) <= PROXIMITY
                    or abs(ts - eng["end"]) <= PROXIMITY
                    or (eng["start"] <= ts <= eng["end"])
                ):
                    for name in [source, target]:
                        if (
                            name not in self.player
                            and name not in self.known_boss_names
                            and name not in junk_names
                            and not name.endswith(junk_suffixes)
                        ):
                            engagement_mobs[i].add(name)

        # 3. Print grouped output
        printed_anything = False
        for i, eng in enumerate(engagements):
            mobs = engagement_mobs[i]
            if not mobs:
                continue

            boss_header = ", ".join(sorted(eng["bosses"]))
            print(boss_header, file=output)
            for mob in sorted(mobs):
                print(f"  - {mob}", file=output)
            printed_anything = True

        if not printed_anything:
            return


class NullEncounterMobs:
    def __init__(self, *args, **kwargs):
        pass

    def add(self, *args, **kwargs):
        pass

    def print(self, *args, **kwargs):
        pass
