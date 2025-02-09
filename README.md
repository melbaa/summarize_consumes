# About

The project generates a summary of WoW raid combat logs.

The summary includes:
* consumables (as much as the combat log allows)
* consumable prices if data is available. First an attempt is made to download prices from the web. If that fails, prices are read from the local prices.json
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
usage: summarize_consumes.exe [-h] [--pastebin] [--open-browser]
               [--write-summary] [--write-consumable-totals-csv]
               [--write-damage-output] [--write-healing-output]
               [--write-damage-taken-output] [--prices-server {nord,telabim}]
               [--compare-players PLAYER1 PLAYER2] [--expert-log-unparsed-lines]
               [--visualize]
               logpath

positional arguments:
  logpath               path to WoWCombatLog.txt

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
  --compare-players PLAYER1 PLAYER2
                        compare 2 players, output the difference in compare-players.txt
  --expert-log-unparsed-lines
                        create an unparsed.txt with everything that was not parsed
  --visualize           Generate visual infographic
```

## Hosted javascript version

On [melbalabs](https://melbalabs.com/summarize_consumes/) you can find a simple version that analyzes the log in your browser.


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
