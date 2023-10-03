The project generates a summary of a raid combat log.
The summary includes consumables (as much as the combat log allows), details about some boss fights (huhuran, cthun chains, gluth, four horsemen chains, kt shadow fissures, kt frostbolts, kt frostblasts), pets found.

Check out summary.txt for an example.



usage: summarize_consumes.exe [-h] [--pastebin] [--open-browser] logpath

positional arguments:
  logpath         path to WoWCombatLog.txt

options:
  -h, --help      show this help message and exit
  --pastebin      upload result to a pastebin and return the url
  --open-browser  used with --pastebin. open the pastebin url with your browser





Install prepacked binary:

You can download an executable from the Releases section [1] and save it in your WoW Logs folder.

A bunch of anti-virus software as usual gives a false positive [2], so if you are worried, install from source as shown below.

[1] https://github.com/melbaa/summarize_consumes/releases
[2] https://www.virustotal.com/gui/file/49633f660d6efc13bfc8705d89349e5f28ef135cc7dc0639a563c61f3a3bffa2?nocache=1






Installing from source on windows:

To create a virtualenv with the project in the current directory
python -m venv venv

Install dependencies
.\venv\Scripts\pip.exe install -r .\requirements.txt
.\venv\Scripts\pip.exe install .

Create a summary
.\venv\Scripts\summarize_consumes.exe path\to\your\Logs\WoWCombatLog.txt > summary.txt

Create summary, upload to a pastebin and open with your browser
.\venv\Scripts\summarize_consumes.exe path\to\your\Logs\WoWCombatLog.txt --pastebin --open-browser


