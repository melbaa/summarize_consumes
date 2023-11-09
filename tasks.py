import os
from pathlib import Path

from invoke import Collection, task

from colorama import just_fix_windows_console
just_fix_windows_console()

@task
def unparsed(c):
    cmd = "python -m melbalabs.summarize_consumes.main ..\..\..\Logs\WoWCombatLog.txt --expert-log-unparsed-lines --write-summary"
    c.run(cmd)

@task
def pytest(c):
    cmd = "pytest -vs --cache-clear --pdb --color=yes"
    c.run(cmd)

@task
def excludes(c):
    cmd = "grep -v -f .\excludes.txt ..\..\..\Logs\WoWCombatLog.txt"
    c.run(cmd)

@task
def examples(c):
    print('regenerating examples')
    filenames = os.listdir('testdata')
    cwd = Path('.')
    for filename in filenames:
        input_file = cwd / 'testdata' / filename
        cmd = f"python -m melbalabs.summarize_consumes.main {input_file} --write-summary"
        c.run(cmd)
        output_file = cwd / 'examples' / f'summary-{filename}'
        c.run(f'mv summary.txt {output_file}')


