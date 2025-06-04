# About

The project generates a summary of WoW raid combat logs.

The summary includes:
* consumables (as much as the combat log allows)
* consumable prices if data is available. First an attempt is made to download prices from the web. If that fails, prices are read from the local prices.json
* sunder summary (for superwow logs)
* cooldowns, resurrects, racial abilities and trinkets used
* annihilator log
* flame buffet (dragonling) log
* details about some boss fights
  * nefarian corrupted healing
  * nefarian wild polymorphs
  * viscidus frost hits
  * huhuran frenzy/berserk/tranq shots/peasant callers
  * cthun chains
  * gluth frenzy/tranq shots/decimate
  * four horsemen chains
  * kt shadow fissures
  * kt frostbolts
  * kt frostblasts
* pets found
* classes detected

It is assumed that the combat log was generated while a logging addon such as [AdvancedVanillaCombatLog](https://github.com/YamaYAML/LegacyPlayersV4/tree/main/Addons/AdvancedVanillaCombatLog) or [SuperWowCombatLogger](https://github.com/pepopo978/SuperWowCombatLogger) was active.<br>
Check out [the examples directory](https://github.com/melbaa/summarize_consumes/tree/master/examples) for summaries of various raids.<br>
Price data via https://www.wowauctions.net/


# Usage

## From the command line
```
usage: summarize_consumes.exe [-h] [--pastebin] [--open-browser] [--write-summary]
               [--write-consumable-totals-csv] [--write-damage-output]
               [--write-healing-output] [--write-damage-taken-output]
               [--prices-server {nord,telabim}] [--visualize]
               [--compare-players PLAYER1 PLAYER2]
               [--expert-log-unparsed-lines] [--expert-write-web-prices]
               [--expert-disable-web-prices] [--expert-deterministic-logs]
               logpath

positional arguments:
  logpath               path to WoWCombatLog.txt
                        or an url like https://turtlogs.com/viewer/8406/base?history_state=1

options:
  -h, --help            show this help message and exit
  --pastebin            upload result to a pastebin and return the url
  --open-browser        used with --pastebin. open the pastebin url with your browser
  --write-summary       writes output to summary.txt instead of the console
  --write-consumable-totals-csv
                        also writes consumable-totals.csv (name, copper, deaths)
  --write-damage-output
                        writes output to damage-output.txt
  --write-heailng-output
                        writes output to healing-output.txt
  --write-damage-taken-output
                        writes output to damage-taken-output.txt
  --prices-server {nord,telabim}
                        specify which server price data to use
  --visualize           Generate visual infographic
  --compare-players PLAYER1 PLAYER2
                        compare 2 players, output the difference in compare-players.txt
  --expert-log-unparsed-lines
                        create an unparsed.txt with everything that was not parsed
  --expert-write-web-prices
                        writes output to prices-web.json
  --expert-disable-web-prices
                        don't download price data
  --expert-deterministic-logs
                        disable environmental outputs
```

## Hosted javascript version

On [melbalabs](https://melbalabs.com/summarize_consumes/) you can find a simple version that analyzes the log in **your** browser. Nothing is sent across the network.


# Installation

## Using pre-built binary

You can download [an executable from the Releases section](https://github.com/melbaa/summarize_consumes/releases) and save it in your WoW Logs folder.<br>
The release is automatically generated and you can see exactly how in the [Actions section](https://github.com/melbaa/summarize_consumes/actions).<br>
A bunch of [anti-virus software as usual gives a false positive](https://www.virustotal.com/gui/file/49633f660d6efc13bfc8705d89349e5f28ef135cc7dc0639a563c61f3a3bffa2?nocache=1), so if you are worried, install from source as shown below.

## Installing from source on windows

This is only needed if you don't want to use the binary from the [releases section](https://github.com/melbaa/summarize_consumes/releases) and prefer to use the source code.

```bash
# Create a virtualenv with the project in the current directory:
python -m venv venv

# Install the project and its dependencies:
.\venv\Scripts\pip.exe install .

# Create a summary:
.\venv\Scripts\summarize_consumes.exe path\to\your\Logs\WoWCombatLog.txt > summary.txt

# Create summary, upload to a pastebin and open with your browser:
.\venv\Scripts\summarize_consumes.exe path\to\your\Logs\WoWCombatLog.txt --pastebin --open-browser
```

# Known Consumables

<!-- CONSUMABLES_TABLE_START -->
| Consumable | Price | Charges |
|------------|--------|----------|
| ??? Elixir of the Sages ??? | [13447](https://database.turtle-wow.org/?item=13447) | n/a |
| ??? Lesser Stoneshield Potion ??? | [4623](https://database.turtle-wow.org/?item=4623) | n/a |
| Advanced Target Dummy | [4392](https://database.turtle-wow.org/?item=4392) | n/a |
| Agility | n/a | n/a |
| Anti-Venom | [6452](https://database.turtle-wow.org/?item=6452) | n/a |
| Arcane Elixir | [9155](https://database.turtle-wow.org/?item=9155) | n/a |
| Arcane Protection | n/a | n/a |
| Basilisk Brain | [8394](https://database.turtle-wow.org/?item=8394) | n/a |
| Blasted Boar Lung | [8392](https://database.turtle-wow.org/?item=8392) | n/a |
| Blessed Sunfruit | n/a | n/a |
| Blessed Sunfruit Juice | n/a | n/a |
| Blessed Wizard Oil | [23123](https://database.turtle-wow.org/?item=23123) | n/a |
| Bloodkelp Elixir of Resistance | n/a | n/a |
| Blue Power Crystal | [11184](https://database.turtle-wow.org/?item=11184) | n/a |
| Bogling Root | [5206](https://database.turtle-wow.org/?item=5206) | n/a |
| Bright Dream Shard | [61199](https://database.turtle-wow.org/?item=61199) | n/a |
| Brilliant Mana Oil | [20748](https://database.turtle-wow.org/?item=20748) | 5 |
| Brilliant Wizard Oil | [20749](https://database.turtle-wow.org/?item=20749) | 5 |
| Buttermilk Delight | n/a | n/a |
| Conjured Crystal Water | n/a | n/a |
| Conjured Mana Orange | n/a | n/a |
| Consecrated Sharpening Stone | [23122](https://database.turtle-wow.org/?item=23122) | n/a |
| Crystal Basilisk Spine | [1703](https://database.turtle-wow.org/?item=1703) | n/a |
| Crystal Charge | - 10x Yellow Power Crystal<br>- 10x Red Power Crystal | 6 |
| Crystal Force | - 10x Green Power Crystal<br>- 10x Blue Power Crystal | 6 |
| Crystal Ward | - 10x Green Power Crystal<br>- 10x Red Power Crystal | 6 |
| Danonzo's Tel'Abim Delight | [60977](https://database.turtle-wow.org/?item=60977) | n/a |
| Danonzo's Tel'Abim Medley | [60978](https://database.turtle-wow.org/?item=60978) | n/a |
| Danonzo's Tel'Abim Surprise | [60976](https://database.turtle-wow.org/?item=60976) | n/a |
| Dark Desire | n/a | n/a |
| Dark Rune | [20520](https://database.turtle-wow.org/?item=20520) | n/a |
| Darnassus Gift of Friendship | n/a | n/a |
| Deeprock Salt | [8150](https://database.turtle-wow.org/?item=8150) | n/a |
| Demonic Rune | n/a | n/a |
| Dense Dynamite | [18641](https://database.turtle-wow.org/?item=18641) | n/a |
| Dense Sharpening Stone | [12404](https://database.turtle-wow.org/?item=12404) | n/a |
| Dense Weightstone | [12643](https://database.turtle-wow.org/?item=12643) | n/a |
| Dragonbreath Chili | [12217](https://database.turtle-wow.org/?item=12217) | n/a |
| Dreamshard Elixir | [61224](https://database.turtle-wow.org/?item=61224) | n/a |
| Dreamtonic | [61423](https://database.turtle-wow.org/?item=61423) | n/a |
| Elemental Sharpening Stone | [18262](https://database.turtle-wow.org/?item=18262) | n/a |
| Elixir of Brute Force | [13453](https://database.turtle-wow.org/?item=13453) | n/a |
| Elixir of Demonslaying | [9224](https://database.turtle-wow.org/?item=9224) | n/a |
| Elixir of Firepower | [6373](https://database.turtle-wow.org/?item=6373) | n/a |
| Elixir of Fortitude | [3825](https://database.turtle-wow.org/?item=3825) | n/a |
| Elixir of Frost Power | [17708](https://database.turtle-wow.org/?item=17708) | n/a |
| Elixir of Giant Growth | [6662](https://database.turtle-wow.org/?item=6662) | n/a |
| Elixir of Giants | [9206](https://database.turtle-wow.org/?item=9206) | n/a |
| Elixir of Greater Agility | [9187](https://database.turtle-wow.org/?item=9187) | n/a |
| Elixir of Greater Defense | [8951](https://database.turtle-wow.org/?item=8951) | n/a |
| Elixir of Greater Firepower | [21546](https://database.turtle-wow.org/?item=21546) | n/a |
| Elixir of Greater Intellect | [9179](https://database.turtle-wow.org/?item=9179) | n/a |
| Elixir of Greater Nature Power | [50237](https://database.turtle-wow.org/?item=50237) | n/a |
| Elixir of Poison Resistance | [3386](https://database.turtle-wow.org/?item=3386) | n/a |
| Elixir of Shadow Power | [9264](https://database.turtle-wow.org/?item=9264) | n/a |
| Elixir of Superior Defense | [13445](https://database.turtle-wow.org/?item=13445) | n/a |
| Elixir of the Mongoose | [13452](https://database.turtle-wow.org/?item=13452) | n/a |
| Emerald Blessing | - 1x Bright Dream Shard | n/a |
| Empowering Herbal Salad | [83309](https://database.turtle-wow.org/?item=83309) | n/a |
| Essence of Fire | [7078](https://database.turtle-wow.org/?item=7078) | n/a |
| Fire Protection | n/a | n/a |
| Fire Protection Potion | [6049](https://database.turtle-wow.org/?item=6049) | n/a |
| Fire-toasted Bun | n/a | n/a |
| Flask of Chromatic Resistance | [13513](https://database.turtle-wow.org/?item=13513) | n/a |
| Flask of Distilled Wisdom | [13511](https://database.turtle-wow.org/?item=13511) | n/a |
| Flask of Petrification | [13506](https://database.turtle-wow.org/?item=13506) | n/a |
| Flask of Supreme Power | [13512](https://database.turtle-wow.org/?item=13512) | n/a |
| Flask of the Titans | [13510](https://database.turtle-wow.org/?item=13510) | n/a |
| Free Action Potion | [5634](https://database.turtle-wow.org/?item=5634) | n/a |
| Frost Oil | [3829](https://database.turtle-wow.org/?item=3829) | n/a |
| Frost Protection | n/a | n/a |
| Frost Protection Potion | [6050](https://database.turtle-wow.org/?item=6050) | n/a |
| Frozen Rune | [22682](https://database.turtle-wow.org/?item=22682) | n/a |
| Gift of Arthas | [9088](https://database.turtle-wow.org/?item=9088) | n/a |
| Goblin Brainwashing Device | n/a | n/a |
| Goblin Sapper Charge | [10646](https://database.turtle-wow.org/?item=10646) | n/a |
| Gordok Green Grog | n/a | n/a |
| Graccu's Homemade Meat Pie | [17407](https://database.turtle-wow.org/?item=17407) | n/a |
| Graccu's Mince Meat Fruitcake | n/a | n/a |
| Great Rage Potion | [5633](https://database.turtle-wow.org/?item=5633) | n/a |
| Greater Arcane Elixir | [13454](https://database.turtle-wow.org/?item=13454) | n/a |
| Greater Arcane Protection Potion | [13461](https://database.turtle-wow.org/?item=13461) | n/a |
| Greater Dreamless Sleep Potion | [20002](https://database.turtle-wow.org/?item=20002) | n/a |
| Greater Fire Protection Potion | [13457](https://database.turtle-wow.org/?item=13457) | n/a |
| Greater Frost Protection Potion | [13456](https://database.turtle-wow.org/?item=13456) | n/a |
| Greater Holy Protection Potion | [13460](https://database.turtle-wow.org/?item=13460) | n/a |
| Greater Nature Protection Potion | [13458](https://database.turtle-wow.org/?item=13458) | n/a |
| Greater Shadow Protection Potion | [13459](https://database.turtle-wow.org/?item=13459) | n/a |
| Greater Stoneshield | [13455](https://database.turtle-wow.org/?item=13455) | n/a |
| Green Power Crystal | [11185](https://database.turtle-wow.org/?item=11185) | n/a |
| Grilled Squid | [13928](https://database.turtle-wow.org/?item=13928) | n/a |
| Gurubashi Gumbo | [53015](https://database.turtle-wow.org/?item=53015) | n/a |
| Hardened Mushroom | [51717](https://database.turtle-wow.org/?item=51717) | n/a |
| Healing Potion - Major | [13446](https://database.turtle-wow.org/?item=13446) | n/a |
| Healing Potion - Superior | [3928](https://database.turtle-wow.org/?item=3928) | n/a |
| Holy Protection | n/a | n/a |
| Holy Protection Potion | [6051](https://database.turtle-wow.org/?item=6051) | n/a |
| Hourglass Sand | [19183](https://database.turtle-wow.org/?item=19183) | n/a |
| Increased Intellect | n/a | n/a |
| Increased Stamina | n/a | n/a |
| Infallible Mind (Cerebral Cortex Compound) | - 10x Basilisk Brain<br>- 2x Vulture Gizzard | n/a |
| Invisibility Potion | [9172](https://database.turtle-wow.org/?item=9172) | n/a |
| Invulnerability | [3387](https://database.turtle-wow.org/?item=3387) | n/a |
| Iron Grenade | [4390](https://database.turtle-wow.org/?item=4390) | n/a |
| Ironforge Gift of Friendship | n/a | n/a |
| Juju Chill | [12434](https://database.turtle-wow.org/?item=12434) | n/a |
| Juju Ember | [12432](https://database.turtle-wow.org/?item=12432) | n/a |
| Juju Escape | [12435](https://database.turtle-wow.org/?item=12435) | n/a |
| Juju Flurry | [12430](https://database.turtle-wow.org/?item=12430) | n/a |
| Juju Guile | [12433](https://database.turtle-wow.org/?item=12433) | n/a |
| Juju Might | [12436](https://database.turtle-wow.org/?item=12436) | n/a |
| Juju Power | [12431](https://database.turtle-wow.org/?item=12431) | n/a |
| Jungle Remedy | [2633](https://database.turtle-wow.org/?item=2633) | n/a |
| Kreeg's Stout Beatdown | n/a | n/a |
| Large Brilliant Shard | [14344](https://database.turtle-wow.org/?item=14344) | n/a |
| Larval Acid | [18512](https://database.turtle-wow.org/?item=18512) | n/a |
| Le Fishe Au Chocolat | [84040](https://database.turtle-wow.org/?item=84040) | n/a |
| Lesser Invisibility Potion | [3823](https://database.turtle-wow.org/?item=3823) | n/a |
| Lesser Mana Oil | [20747](https://database.turtle-wow.org/?item=20747) | 5 |
| Living Action Potion | [20008](https://database.turtle-wow.org/?item=20008) | n/a |
| Lucidity Potion | [61225](https://database.turtle-wow.org/?item=61225) | n/a |
| Lung Juice Cocktail | - 1x Basilisk Brain<br>- 2x Scorpok Pincer<br>- 3x Blasted Boar Lung | n/a |
| MOLL-E, Remote Mail Terminal | n/a | n/a |
| Mageblood Potion | [20007](https://database.turtle-wow.org/?item=20007) | n/a |
| Magic Resistance Potion | [9036](https://database.turtle-wow.org/?item=9036) | n/a |
| Major Troll's Blood Potion | [20004](https://database.turtle-wow.org/?item=20004) | n/a |
| Mana Potion - Greater | [6149](https://database.turtle-wow.org/?item=6149) | n/a |
| Mana Potion - Major | [13444](https://database.turtle-wow.org/?item=13444) | n/a |
| Mana Potion - Superior | [13443](https://database.turtle-wow.org/?item=13443) | n/a |
| Mana Regeneration (food or mageblood) | n/a | n/a |
| Masterwork Target Dummy | [16023](https://database.turtle-wow.org/?item=16023) | n/a |
| Medivh's Merlot | [61174](https://database.turtle-wow.org/?item=61174) | n/a |
| Medivh's Merlot Blue Label | [61175](https://database.turtle-wow.org/?item=61175) | n/a |
| Midsummer Sausage | n/a | n/a |
| Mighty Rage Potion | [13442](https://database.turtle-wow.org/?item=13442) | n/a |
| Mighty Troll's Blood Potion | [3826](https://database.turtle-wow.org/?item=3826) | n/a |
| Nature Protection | n/a | n/a |
| Nature Protection Potion | [6052](https://database.turtle-wow.org/?item=6052) | n/a |
| Nightfin Soup | [13931](https://database.turtle-wow.org/?item=13931) | n/a |
| Noggenfogger Elixir | n/a | n/a |
| Oil of Immolation | [8956](https://database.turtle-wow.org/?item=8956) | n/a |
| Orgrimmar Gift of Friendship | n/a | n/a |
| Poisonous Mushroom | [5823](https://database.turtle-wow.org/?item=5823) | n/a |
| Potion of Quickness | [61181](https://database.turtle-wow.org/?item=61181) | n/a |
| Power Mushroom | [51720](https://database.turtle-wow.org/?item=51720) | n/a |
| Powerful Anti-Venom | [19440](https://database.turtle-wow.org/?item=19440) | n/a |
| Powerful Smelling Salts | - 4x Deeprock Salt<br>- 2x Essence of Fire<br>- 1x Larval Acid | n/a |
| Purification Potion | [13462](https://database.turtle-wow.org/?item=13462) | n/a |
| Purple Lotus | [8831](https://database.turtle-wow.org/?item=8831) | n/a |
| Rage Potion | [5631](https://database.turtle-wow.org/?item=5631) | n/a |
| Rage of Ages (ROIDS) | - 1x Scorpok Pincer<br>- 2x Blasted Boar Lung<br>- 3x Snickerfang Jowl | n/a |
| Red Power Crystal | [11186](https://database.turtle-wow.org/?item=11186) | n/a |
| Regeneration | n/a | n/a |
| Rejuvenation Potion - Major | [18253](https://database.turtle-wow.org/?item=18253) | n/a |
| Rejuvenation Potion - Minor | [2456](https://database.turtle-wow.org/?item=2456) | n/a |
| Restorative Potion | [9030](https://database.turtle-wow.org/?item=9030) | n/a |
| Rumsey Rum | n/a | n/a |
| Rumsey Rum Black Label | [21151](https://database.turtle-wow.org/?item=21151) | n/a |
| Rumsey Rum Dark | [21114](https://database.turtle-wow.org/?item=21114) | n/a |
| Scorpok Pincer | [8393](https://database.turtle-wow.org/?item=8393) | n/a |
| Scroll of Agility IV | [10309](https://database.turtle-wow.org/?item=10309) | n/a |
| Scroll of Intellect IV | [10308](https://database.turtle-wow.org/?item=10308) | n/a |
| Scroll of Protection IV | [10305](https://database.turtle-wow.org/?item=10305) | n/a |
| Scroll of Spirit IV | [10306](https://database.turtle-wow.org/?item=10306) | n/a |
| Scroll of Stamina IV | [10307](https://database.turtle-wow.org/?item=10307) | n/a |
| Scroll of Strength IV | [10310](https://database.turtle-wow.org/?item=10310) | n/a |
| Shadow Oil | [3824](https://database.turtle-wow.org/?item=3824) | n/a |
| Shadow Protection | n/a | n/a |
| Shadow Protection Potion | [6048](https://database.turtle-wow.org/?item=6048) | n/a |
| Sheen of Zanza | - 3x Zulian Coin | n/a |
| Slumber Sand | n/a | n/a |
| Small Dream Shard | [61198](https://database.turtle-wow.org/?item=61198) | n/a |
| Snickerfang Jowl | [8391](https://database.turtle-wow.org/?item=8391) | n/a |
| Solid Dynamite | [10507](https://database.turtle-wow.org/?item=10507) | n/a |
| Spirit of Zanza | - 3x Zulian Coin | n/a |
| Stamina | n/a | n/a |
| Stormwind Gift of Friendship | n/a | n/a |
| Stratholme Holy Water | n/a | n/a |
| Strength | n/a | n/a |
| Strike of the Scorpok | - 1x Blasted Boar Lung<br>- 2x Vulture Gizzard<br>- 3x Scorpok Pincer | n/a |
| Strong Anti-Venom | [6453](https://database.turtle-wow.org/?item=6453) | n/a |
| Sweet Surprise | n/a | n/a |
| Swiftness Potion | [2459](https://database.turtle-wow.org/?item=2459) | n/a |
| Swiftness of Zanza | - 3x Zulian Coin | n/a |
| Tea with Sugar | - 0.2x Small Dream Shard | n/a |
| Thistle Tea | [7676](https://database.turtle-wow.org/?item=7676) | n/a |
| Thorium Grenade | [15993](https://database.turtle-wow.org/?item=15993) | n/a |
| Thunder Bluff Gift of Friendship | n/a | n/a |
| Undercity Gift of Friendship | n/a | n/a |
| Very Berry Cream | n/a | n/a |
| Vulture Gizzard | [8396](https://database.turtle-wow.org/?item=8396) | n/a |
| Wildvine Potion | [9144](https://database.turtle-wow.org/?item=9144) | n/a |
| Windblossom Berries | n/a | n/a |
| Winter Veil Candy | n/a | n/a |
| Winter Veil Cookie | n/a | n/a |
| Winter Veil Eggnog | n/a | n/a |
| Winterfall Firewater | [12820](https://database.turtle-wow.org/?item=12820) | n/a |
| Wizard Oil | [20750](https://database.turtle-wow.org/?item=20750) | 5 |
| Yellow Power Crystal | [11188](https://database.turtle-wow.org/?item=11188) | n/a |
| Zulian Coin | [19698](https://database.turtle-wow.org/?item=19698) | n/a |
<!-- CONSUMABLES_TABLE_END -->



# High level design decisions

Provide prebuilt binaries - the project must be usable by people with no python knowledege and no python installation. Python is an implementation detail.

Trust in the provided binaries - open and auditable build process via github actions, no manual uploads.

The project must be easy to use in scripts and integrations. Keep it a standard command line program and use stdout, stderr and files for output.

The project must be usable by people with python knowledge. Follow common python project structure and make it importable as a library.

The project should be usable without access to servers and third party services.
* by default prices are downloaded from the web, but it's possible to use local prices. There's a prices.json provided in the repository.
* the basic output is on stdout or written to a local file via a cmdline flag. Allows people to share results via text files, chat programs or their own pastebins.
* the default output is plain text, which doesn't cause security problems, eg no random javascript code injections

Keep it convenient. Provide hosting for some of the features
* serving prices for nordanaar and telabim transparently
* pastebin automation to make results sharing easier
* a web based version usable with a browser

price gathering is a server side process, which is in sync with the consumables that the app knows about. It imports the ITEMID2NAME dictionary as a library, which makes it easier to maintain.

Feature flags for convenience.

It's ok for OPTIONAL features to have higher requirements (eg formatted output via HTML/JS; automatically submitting data to pastebins; browser automation; stateful processing; downloading prices from the web)

Features MUST NOT interfere with unrelated functionality and make it less robust.

As many tests as possible. Helps verify things still work as originally implemented across rewrites, runtime and library updates.

As much output in a single file as possible
* easier to search
* no tabs
* no delayed loading and failures from multiple HTTP requests

Features with very verbose output write their own files. Pastebins limit payload size, so eventually output has to be split up into more parts.

Parse log lines correctly and completely. No partial parses. Skip unknown syntax and report it.

Prefer to use a parser framework as it's easier to maintain. The syntax is simple enough to allow it.

The mental model for processing should be in multiple stages.
* data parsing
* counting, aggregating, processing the data
* data presentation / output, potentially in multiple formats and to multiple destinations

Dependencies in unpinned versions as documentation and to generate pinned dependencies for repeatable bulids.

Include basic runtime info in the output (project version, python version etc), so users don't have to be interrogated for it.

The linux binaries should be usable on older installs. Aim for 5+ years.

