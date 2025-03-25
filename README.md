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

