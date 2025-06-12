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
| ??? Elixir of the Sages ??? | [13447](https://database.turtle-wow.org/?item=13447) |  |
| ??? Lesser Stoneshield Potion ??? | [4623](https://database.turtle-wow.org/?item=4623) |  |
| Advanced Target Dummy | [4392](https://database.turtle-wow.org/?item=4392) |  |
| Agility |  |  |
| Anti-Venom | [6452](https://database.turtle-wow.org/?item=6452) |  |
| Arcane Elixir | [9155](https://database.turtle-wow.org/?item=9155) |  |
| Arcane Protection |  |  |
| Armor |  |  |
| Baked Salmon | [13935](https://database.turtle-wow.org/?item=13935) |  |
| Basilisk Brain | [8394](https://database.turtle-wow.org/?item=8394) |  |
| Blasted Boar Lung | [8392](https://database.turtle-wow.org/?item=8392) |  |
| Blended Bean Brew |  |  |
| Blessed Sunfruit |  |  |
| Blessed Sunfruit Juice |  |  |
| Blessed Wizard Oil | [23123](https://database.turtle-wow.org/?item=23123) |  |
| Bloodkelp Elixir of Dodging |  |  |
| Bloodkelp Elixir of Resistance |  |  |
| Blue Power Crystal | [11184](https://database.turtle-wow.org/?item=11184) |  |
| Bogling Root | [5206](https://database.turtle-wow.org/?item=5206) |  |
| Boiled Clams |  |  |
| Bottled Alterac Spring Water |  |  |
| Bottled Winterspring Water |  |  |
| Bright Dream Shard | [61199](https://database.turtle-wow.org/?item=61199) |  |
| Brilliant Mana Oil | [20748](https://database.turtle-wow.org/?item=20748) | 5 |
| Brilliant Wizard Oil | [20749](https://database.turtle-wow.org/?item=20749) | 5 |
| Bubbly Beverage |  |  |
| Buttermilk Delight |  |  |
| Catseye Elixir |  |  |
| Cleaning Cloth |  |  |
| Combat Healing Potion |  |  |
| Conjured Crystal Water |  |  |
| Conjured Mana Orange |  |  |
| Consecrated Sharpening Stone | [23122](https://database.turtle-wow.org/?item=23122) |  |
| Cowardly Flight Potion |  |  |
| Crunchy Frog |  |  |
| Crusty Flatbread |  |  |
| Crystal Basilisk Spine | [1703](https://database.turtle-wow.org/?item=1703) |  |
| Crystal Charge | 10 x Yellow Power Crystal<br>10 x Red Power Crystal | 6 |
| Crystal Force | 10 x Green Power Crystal<br>10 x Blue Power Crystal | 6 |
| Crystal Infused Bandage |  |  |
| Crystal Spire | 10 x Blue Power Crystal<br>10 x Yellow Power Crystal | 6 |
| Crystal Ward | 10 x Green Power Crystal<br>10 x Red Power Crystal | 6 |
| Danonzo's Tel'Abim Delight | [60977](https://database.turtle-wow.org/?item=60977) |  |
| Danonzo's Tel'Abim Medley | [60978](https://database.turtle-wow.org/?item=60978) |  |
| Danonzo's Tel'Abim Surprise | [60976](https://database.turtle-wow.org/?item=60976) |  |
| Dark Desire |  |  |
| Dark Rune | [20520](https://database.turtle-wow.org/?item=20520) |  |
| Deeprock Salt | [8150](https://database.turtle-wow.org/?item=8150) |  |
| Deepsea Lobster |  |  |
| Delicious Pizza |  |  |
| Demonic Rune |  |  |
| Dense Dynamite | [18641](https://database.turtle-wow.org/?item=18641) |  |
| Dense Sharpening Stone | [12404](https://database.turtle-wow.org/?item=12404) |  |
| Dense Weightstone | [12643](https://database.turtle-wow.org/?item=12643) |  |
| Dig Rat Stew |  |  |
| Discolored Healing Potion |  |  |
| Dragonbreath Chili | [12217](https://database.turtle-wow.org/?item=12217) |  |
| Dreamless Sleep Potion | [12190](https://database.turtle-wow.org/?item=12190) |  |
| Dreamshard Elixir | [61224](https://database.turtle-wow.org/?item=61224) |  |
| Dreamtonic | [61423](https://database.turtle-wow.org/?item=61423) |  |
| Egg Nog |  |  |
| Elderberry Pie |  |  |
| Elemental Sharpening Stone | [18262](https://database.turtle-wow.org/?item=18262) |  |
| Elixir of Agility |  |  |
| Elixir of Brute Force | [13453](https://database.turtle-wow.org/?item=13453) |  |
| Elixir of Defense |  |  |
| Elixir of Demonslaying | [9224](https://database.turtle-wow.org/?item=9224) |  |
| Elixir of Detect Demon |  |  |
| Elixir of Detect Lesser Invisibility |  |  |
| Elixir of Detect Undead |  |  |
| Elixir of Firepower | [6373](https://database.turtle-wow.org/?item=6373) |  |
| Elixir of Fortitude | [3825](https://database.turtle-wow.org/?item=3825) |  |
| Elixir of Frost Power | [17708](https://database.turtle-wow.org/?item=17708) |  |
| Elixir of Giant Growth | [6662](https://database.turtle-wow.org/?item=6662) |  |
| Elixir of Giants | [9206](https://database.turtle-wow.org/?item=9206) |  |
| Elixir of Greater Agility | [9187](https://database.turtle-wow.org/?item=9187) |  |
| Elixir of Greater Defense | [8951](https://database.turtle-wow.org/?item=8951) |  |
| Elixir of Greater Firepower | [21546](https://database.turtle-wow.org/?item=21546) |  |
| Elixir of Greater Intellect | [9179](https://database.turtle-wow.org/?item=9179) |  |
| Elixir of Greater Nature Power | [50237](https://database.turtle-wow.org/?item=50237) |  |
| Elixir of Greater Water Breathing |  |  |
| Elixir of Lesser Agility |  |  |
| Elixir of Lions Strength |  |  |
| Elixir of Minor Agility |  |  |
| Elixir of Minor Fortitude |  |  |
| Elixir of Ogres Strength |  |  |
| Elixir of Poison Resistance | [3386](https://database.turtle-wow.org/?item=3386) |  |
| Elixir of Shadow Power | [9264](https://database.turtle-wow.org/?item=9264) |  |
| Elixir of Superior Defense | [13445](https://database.turtle-wow.org/?item=13445) |  |
| Elixir of Water Breathing |  |  |
| Elixir of Water Walking |  |  |
| Elixir of Wisdom |  |  |
| Elixir of the Mongoose | [13452](https://database.turtle-wow.org/?item=13452) |  |
| Emerald Blessing | 1 x Bright Dream Shard |  |
| Empowering Herbal Salad | [83309](https://database.turtle-wow.org/?item=83309) |  |
| Essence of Fire | [7078](https://database.turtle-wow.org/?item=7078) |  |
| Festival Dumplings |  |  |
| Fiery Festival Brew |  |  |
| Fire Protection |  |  |
| Fire Protection Potion | [6049](https://database.turtle-wow.org/?item=6049) |  |
| Fire-toasted Bun |  |  |
| Fishliver Oil |  |  |
| Fizzy Faire Drink |  |  |
| Flask of Chromatic Resistance | [13513](https://database.turtle-wow.org/?item=13513) |  |
| Flask of Distilled Wisdom | [13511](https://database.turtle-wow.org/?item=13511) |  |
| Flask of Petrification | [13506](https://database.turtle-wow.org/?item=13506) |  |
| Flask of Supreme Power | [13512](https://database.turtle-wow.org/?item=13512) |  |
| Flask of the Titans | [13510](https://database.turtle-wow.org/?item=13510) |  |
| Free Action Potion | [5634](https://database.turtle-wow.org/?item=5634) |  |
| Freshly-Squeezed Lemonade |  |  |
| Frost Oil | [3829](https://database.turtle-wow.org/?item=3829) |  |
| Frost Protection |  |  |
| Frost Protection Potion | [6050](https://database.turtle-wow.org/?item=6050) |  |
| Frozen Rune | [22682](https://database.turtle-wow.org/?item=22682) |  |
| Gargantuan Tel'Abim Banana |  |  |
| Gift of Arthas | [9088](https://database.turtle-wow.org/?item=9088) |  |
| Gift of Friendship - Darnassus (agi) |  |  |
| Gift of Friendship - Ironforge (stam) |  |  |
| Gift of Friendship - Orgrimmar (agi) |  |  |
| Gift of Friendship - Stormwind (int) |  |  |
| Gift of Friendship - Thunder Bluff (stam) |  |  |
| Gift of Friendship - Undercity (int) |  |  |
| Gilneas Hot Stew | [84041](https://database.turtle-wow.org/?item=84041) |  |
| Gizzard Gum (Spiritual Domination) | 10 x Vulture Gizzard<br>2 x Snickerfang Jowl |  |
| Goblin Brainwashing Device |  |  |
| Goblin Sapper Charge | [10646](https://database.turtle-wow.org/?item=10646) |  |
| Gordok Green Grog |  |  |
| Graccu's Homemade Meat Pie | [17407](https://database.turtle-wow.org/?item=17407) |  |
| Graccu's Mince Meat Fruitcake |  |  |
| Great Rage Potion | [5633](https://database.turtle-wow.org/?item=5633) |  |
| Greater Arcane Elixir | [13454](https://database.turtle-wow.org/?item=13454) |  |
| Greater Arcane Protection Potion | [13461](https://database.turtle-wow.org/?item=13461) |  |
| Greater Dreamless Sleep Potion | [20002](https://database.turtle-wow.org/?item=20002) |  |
| Greater Fire Protection Potion | [13457](https://database.turtle-wow.org/?item=13457) |  |
| Greater Frost Protection Potion | [13456](https://database.turtle-wow.org/?item=13456) |  |
| Greater Healing Potion |  |  |
| Greater Holy Protection Potion | [13460](https://database.turtle-wow.org/?item=13460) |  |
| Greater Nature Protection Potion | [13458](https://database.turtle-wow.org/?item=13458) |  |
| Greater Shadow Protection Potion | [13459](https://database.turtle-wow.org/?item=13459) |  |
| Greater Stoneshield | [13455](https://database.turtle-wow.org/?item=13455) |  |
| Green Garden Tea |  |  |
| Green Power Crystal | [11185](https://database.turtle-wow.org/?item=11185) |  |
| Grilled Squid | [13928](https://database.turtle-wow.org/?item=13928) |  |
| Gurubashi Gumbo | [53015](https://database.turtle-wow.org/?item=53015) |  |
| Handful of Rose Petals |  |  |
| Hardened Mushroom | [51717](https://database.turtle-wow.org/?item=51717) |  |
| Healing Potion |  |  |
| Healing Potion - Major | [13446](https://database.turtle-wow.org/?item=13446) |  |
| Healing Potion - Superior | [3928](https://database.turtle-wow.org/?item=3928) |  |
| Heavy Runecloth Bandage |  |  |
| Highpeak Thistle |  |  |
| Holy Protection |  |  |
| Holy Protection Potion | [6051](https://database.turtle-wow.org/?item=6051) |  |
| Hot Smoked Bass |  |  |
| Hourglass Sand | [19183](https://database.turtle-wow.org/?item=19183) |  |
| Increased Intellect |  |  |
| Increased Stamina |  |  |
| Infallible Mind (Cerebral Cortex Compound) | 10 x Basilisk Brain<br>2 x Vulture Gizzard |  |
| Intellect |  |  |
| Invisibility Potion | [9172](https://database.turtle-wow.org/?item=9172) |  |
| Invulnerability | [3387](https://database.turtle-wow.org/?item=3387) |  |
| Iron Grenade | [4390](https://database.turtle-wow.org/?item=4390) |  |
| Juicy Striped Melon | [51718](https://database.turtle-wow.org/?item=51718) |  |
| Juju Chill | [12434](https://database.turtle-wow.org/?item=12434) |  |
| Juju Ember | [12432](https://database.turtle-wow.org/?item=12432) |  |
| Juju Escape | [12435](https://database.turtle-wow.org/?item=12435) |  |
| Juju Flurry | [12430](https://database.turtle-wow.org/?item=12430) |  |
| Juju Guile | [12433](https://database.turtle-wow.org/?item=12433) |  |
| Juju Might | [12436](https://database.turtle-wow.org/?item=12436) |  |
| Juju Power | [12431](https://database.turtle-wow.org/?item=12431) |  |
| Jungle Remedy | [2633](https://database.turtle-wow.org/?item=2633) |  |
| Kreeg's Stout Beatdown |  |  |
| Large Brilliant Shard | [14344](https://database.turtle-wow.org/?item=14344) |  |
| Larval Acid | [18512](https://database.turtle-wow.org/?item=18512) |  |
| Le Fishe Au Chocolat | [84040](https://database.turtle-wow.org/?item=84040) |  |
| Lesser Invisibility Potion | [3823](https://database.turtle-wow.org/?item=3823) |  |
| Lesser Mana Oil | [20747](https://database.turtle-wow.org/?item=20747) | 5 |
| Lesser Stoneshield Potion |  |  |
| Lily Root |  |  |
| Living Action Potion | [20008](https://database.turtle-wow.org/?item=20008) |  |
| Lucidity Potion | [61225](https://database.turtle-wow.org/?item=61225) |  |
| Lung Juice Cocktail | 1 x Basilisk Brain<br>2 x Scorpok Pincer<br>3 x Blasted Boar Lung |  |
| MOLL-E, Remote Mail Terminal |  |  |
| Mageblood Potion | [20007](https://database.turtle-wow.org/?item=20007) |  |
| Magic Dust | [2091](https://database.turtle-wow.org/?item=2091) |  |
| Magic Resistance Potion | [9036](https://database.turtle-wow.org/?item=9036) |  |
| Major Healing Draught |  |  |
| Major Mana Draught |  |  |
| Major Troll's Blood Potion | [20004](https://database.turtle-wow.org/?item=20004) |  |
| Mana Potion | [3827](https://database.turtle-wow.org/?item=3827) |  |
| Mana Potion - Greater | [6149](https://database.turtle-wow.org/?item=6149) |  |
| Mana Potion - Lesser |  |  |
| Mana Potion - Major | [13444](https://database.turtle-wow.org/?item=13444) |  |
| Mana Potion - Minor |  |  |
| Mana Potion - Superior | [13443](https://database.turtle-wow.org/?item=13443) |  |
| Mana Regeneration (food or mageblood) |  |  |
| Masterwork Target Dummy | [16023](https://database.turtle-wow.org/?item=16023) |  |
| Medivh's Merlot | [61174](https://database.turtle-wow.org/?item=61174) |  |
| Medivh's Merlot Blue Label | [61175](https://database.turtle-wow.org/?item=61175) |  |
| Midsummer Sausage |  |  |
| Mightfish Steak |  |  |
| Mighty Rage Potion | [13442](https://database.turtle-wow.org/?item=13442) |  |
| Mighty Troll's Blood Potion | [3826](https://database.turtle-wow.org/?item=3826) |  |
| Minor Healing Potion |  |  |
| Minor Magic Resistance Potion |  |  |
| Morning Glory Dew |  |  |
| Mug of Shimmer Stout |  |  |
| Nature Protection |  |  |
| Nature Protection Potion | [6052](https://database.turtle-wow.org/?item=6052) |  |
| Nightfin Soup | [13931](https://database.turtle-wow.org/?item=13931) |  |
| Noggenfogger Elixir |  |  |
| Oil of Immolation | [8956](https://database.turtle-wow.org/?item=8956) |  |
| Oil of Olaf |  |  |
| Party Grenade |  |  |
| Plump Country Pumpkin |  |  |
| Poisonous Mushroom | [5823](https://database.turtle-wow.org/?item=5823) |  |
| Potion of Fervor |  |  |
| Potion of Quickness | [61181](https://database.turtle-wow.org/?item=61181) |  |
| Power Mushroom | [51720](https://database.turtle-wow.org/?item=51720) |  |
| Powerful Anti-Venom | [19440](https://database.turtle-wow.org/?item=19440) |  |
| Powerful Smelling Salts | 4 x Deeprock Salt<br>2 x Essence of Fire<br>1 x Larval Acid |  |
| Purification Potion | [13462](https://database.turtle-wow.org/?item=13462) |  |
| Purple Lotus | [8831](https://database.turtle-wow.org/?item=8831) |  |
| Rage Potion | [5631](https://database.turtle-wow.org/?item=5631) |  |
| Rage of Ages (ROIDS) | 1 x Scorpok Pincer<br>2 x Blasted Boar Lung<br>3 x Snickerfang Jowl |  |
| Raptor Punch |  |  |
| Raw Slitherskin Mackerel |  |  |
| Razorlash Root |  |  |
| Really Sticky Glue |  |  |
| Red Power Crystal | [11186](https://database.turtle-wow.org/?item=11186) |  |
| Refreshing Red Apple |  |  |
| Regeneration |  |  |
| Rejuvenation Potion - Major | [18253](https://database.turtle-wow.org/?item=18253) |  |
| Rejuvenation Potion - Minor | [2456](https://database.turtle-wow.org/?item=2456) |  |
| Restorative Potion | [9030](https://database.turtle-wow.org/?item=9030) |  |
| Restore Mana (mana potion) |  |  |
| Restoring Balm |  |  |
| Ripe Tel'Abim Banana |  |  |
| Roast Raptor |  |  |
| Roasted Kodo Meat |  |  |
| Rumsey Rum |  |  |
| Rumsey Rum Black Label | [21151](https://database.turtle-wow.org/?item=21151) |  |
| Rumsey Rum Dark | [21114](https://database.turtle-wow.org/?item=21114) |  |
| Runecloth Bandage |  |  |
| Scorpid Surprise |  |  |
| Scorpok Pincer | [8393](https://database.turtle-wow.org/?item=8393) |  |
| Scroll of Agility IV | [10309](https://database.turtle-wow.org/?item=10309) |  |
| Scroll of Empowered Protection |  |  |
| Scroll of Intellect IV | [10308](https://database.turtle-wow.org/?item=10308) |  |
| Scroll of Magic Warding |  |  |
| Scroll of Protection IV | [10305](https://database.turtle-wow.org/?item=10305) |  |
| Scroll of Spirit IV | [10306](https://database.turtle-wow.org/?item=10306) |  |
| Scroll of Stamina IV | [10307](https://database.turtle-wow.org/?item=10307) |  |
| Scroll of Strength IV | [10310](https://database.turtle-wow.org/?item=10310) |  |
| Scroll of Thorns |  |  |
| Senggin Root |  |  |
| Shadow Oil | [3824](https://database.turtle-wow.org/?item=3824) |  |
| Shadow Protection |  |  |
| Shadow Protection Potion | [6048](https://database.turtle-wow.org/?item=6048) |  |
| Sheen of Zanza | 3 x Zulian Coin |  |
| Slumber Sand |  |  |
| Small Dream Shard | [61198](https://database.turtle-wow.org/?item=61198) |  |
| Snickerfang Jowl | [8391](https://database.turtle-wow.org/?item=8391) |  |
| Solid Dynamite | [10507](https://database.turtle-wow.org/?item=10507) |  |
| Spiced Beef Jerky |  |  |
| Spirit |  |  |
| Spirit of Zanza | 3 x Zulian Coin |  |
| Stamina |  |  |
| Stormstout |  |  |
| Stratholme Holy Water |  |  |
| Strength |  |  |
| Strike of the Scorpok | 1 x Blasted Boar Lung<br>2 x Vulture Gizzard<br>3 x Scorpok Pincer |  |
| Strong Anti-Venom | [6453](https://database.turtle-wow.org/?item=6453) |  |
| Strong Troll's Blood Potion | [3388](https://database.turtle-wow.org/?item=3388) |  |
| Sun-Parched Waterskin |  |  |
| Super Snuff |  |  |
| Superior Healing Draught |  |  |
| Superior Mana Draught |  |  |
| Sweet Mountain Berry |  |  |
| Sweet Surprise |  |  |
| Swiftness Potion | [2459](https://database.turtle-wow.org/?item=2459) |  |
| Swiftness of Zanza | 3 x Zulian Coin |  |
| Swim Speed Potion |  |  |
| Tasty Summer Treat |  |  |
| Tea with Sugar | 0.2 x Small Dream Shard |  |
| Thistle Tea | [7676](https://database.turtle-wow.org/?item=7676) |  |
| Thorium Grenade | [15993](https://database.turtle-wow.org/?item=15993) |  |
| Toasted Smorc |  |  |
| Very Berry Cream |  |  |
| Volatile Concoction |  |  |
| Vulture Gizzard | [8396](https://database.turtle-wow.org/?item=8396) |  |
| Watered-down Beer |  |  |
| Weak Troll's Blood Potion | [3382](https://database.turtle-wow.org/?item=3382) |  |
| Wildvine Potion | [9144](https://database.turtle-wow.org/?item=9144) |  |
| Windblossom Berries |  |  |
| Winter Veil Candy |  |  |
| Winter Veil Cookie |  |  |
| Winter Veil Eggnog |  |  |
| Winterfall Firewater | [12820](https://database.turtle-wow.org/?item=12820) |  |
| Wizard Oil | [20750](https://database.turtle-wow.org/?item=20750) | 5 |
| Yellow Power Crystal | [11188](https://database.turtle-wow.org/?item=11188) |  |
| Zulian Coin | [19698](https://database.turtle-wow.org/?item=19698) |  |
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

# Parsing Notes

The syntax can be very ambiguous and open-ended. We don't know all variable length names of players, NPCs, pets, spells and the structure of all log lines, because all those things are dynamic and can change patch to patch.

The approach that has worked well so far is to take a certain log message and be very specific about parsing exactly that and not much else. Work defensively slowly expanding the set of parsed messages.

Ambiguity example: `on` shows up both inside the spell name and as a token separating the spell name and player name.  
```
Player casts Lay on Hands on Player.
```

The second part is optional. Both of those are valid.  
```
Player casts Spell on Player.
Player casts Spell.
```

More ambiguity. `'s` works the same way as part of a name or as its own token.  
```
4/21 21:01:38.861  Psykhe 's Tea with Sugar heals Psykhe for 1613.  
4/12 20:11:17.188  Psykhe begins to cast Kreeg's Stout Beatdown.
```

A lot of punctuation.  
```
Ragnaros casts Melt Weapon on Psykhe: Iblis, Blade of the Fallen Seraph damaged.
```

Those are different spells. A rare case of significant trailing whitespace.  
```
4/11 22:44:54.456  Player gains Shadow Protection (1).  
4/11 23:40:19.784  Player gains Shadow Protection  (1).  
```
