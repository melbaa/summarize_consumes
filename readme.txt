The project generates a summary of a raid combat log.

The summary includes
* consumables (as much as the combat log allows)
* consumable prices if data is available. First an attempt is made to download prices from the web. If that fails, prices are read from the local prices.json
* cooldowns, resurrects, racial abilities and trinkets used
* annihilator log
* flame buffet (dragonling) log
* details about some boss fights
** nefarian corrupted healing
** nefarian wild polymorphs
** viscidus frost hits
** huhuran frenzy/berserk/tranq shots/peasant callers
** cthun chains
** gluth frenzy/tranq shots/decimate
** four horsemen chains
** kt shadow fissures
** kt frostbolts
** kt frostblasts
* pets found
* classes detected

It is assumed that the combat log was generated while the AdvancedVanillaCombatLog addon (https://github.com/YamaYAML/LegacyPlayersV4/tree/main/Addons/AdvancedVanillaCombatLog) is active.

Check out the examples directory (https://github.com/melbaa/summarize_consumes/tree/master/examples) for summaries of various raids.

Price data via https://www.wowauctions.net/



usage: summarize_consumes.exe [-h] [--pastebin] [--open-browser] logpath

positional arguments:
  logpath               path to WoWCombatLog.txt

options:
  -h, --help            show this help message and exit
  --pastebin            upload result to a pastebin and return the url
  --open-browser        used with --pastebin. open the pastebin url with your browser
  --write-summary       writes output to summary.txt instead of the console
  --write-consumable-totals-csv
                        also writes consumable-totals.csv (name, copper, deaths)
  --compare-players PLAYER1 PLAYER2
                        compare 2 players, output the difference in compare-players.txt



Install prepacked binary:

You can download an executable from the Releases section [1] and save it in your WoW Logs folder.
The release is automatically generated and you can see exactly how in the Actions section [2].
A bunch of anti-virus software as usual gives a false positive [3], so if you are worried, install from source as shown below.

[1] https://github.com/melbaa/summarize_consumes/releases
[2] https://github.com/melbaa/summarize_consumes/actions
[3] https://www.virustotal.com/gui/file/49633f660d6efc13bfc8705d89349e5f28ef135cc7dc0639a563c61f3a3bffa2?nocache=1






Installing from source on windows:

This is only needed if you don't want to use the binary from the Releases section and prefer to use the source code.

To create a virtualenv with the project in the current directory
python -m venv venv

Install the project and its dependencies
.\venv\Scripts\pip.exe install .

Create a summary
.\venv\Scripts\summarize_consumes.exe path\to\your\Logs\WoWCombatLog.txt > summary.txt

Create summary, upload to a pastebin and open with your browser
.\venv\Scripts\summarize_consumes.exe path\to\your\Logs\WoWCombatLog.txt --pastebin --open-browser


