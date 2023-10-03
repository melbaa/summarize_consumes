The project generates a summary of a raid combat log.
The summary includes consumables (as much as the combat log allows), details about some boss fights (huhuran, cthun chains, gluth, four horsemen chains, kt shadow fissures, kt frostbolts, kt frostblasts), pets found.

Check out summary.txt for an example.



Example install on windows:

To create a virtualenv with the project in the current directory
python -m venv venv

Install dependencies
.\venv\Scripts\pip.exe install -r .\requirements.txt
.\venv\Scripts\pip.exe install .

Create a summary
.\venv\Scripts\summarize_consumes.exe path\to\your\Logs\WoWCombatLog.txt > summary.txt

Usually you want to share the summary, there's a util that generates it, uploads it to a pastebin and opens the link in your browser.
.\venv\Scripts\summarize_consumes_upload.exe path\to\your\Logs\WoWCombatLog.txt > summary.txt


TODO
release an .exe so people don't have to mess with python
