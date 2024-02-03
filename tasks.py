import os
from pathlib import Path

from invoke import Collection, task

try:
    from colorama import just_fix_windows_console
    just_fix_windows_console()
except ModuleNotFoundError:
    pass


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
        cmd = f"python -m melbalabs.summarize_consumes.main {input_file} --write-summary --write-consumable-totals-csv"
        c.run(cmd)
        output_file = cwd / 'examples' / f'summary-{filename}'
        c.run(f'mv summary.txt {output_file}')
        csv_output_file = cwd / 'examples' / f'consumable-totals-{filename}.csv'
        c.run(f'mv consumable-totals.csv {csv_output_file}')

@task
def commit(c, message):
    cmd = 'bumpver update --no-fetch'
    c.run(cmd)

    # bumpver still buggy
    c.run('dos2unix pyproject.toml')
    c.run('dos2unix src/melbalabs/summarize_consumes/package.py')

    c.run(f'git add pyproject.toml src/melbalabs/summarize_consumes/package.py')
    c.run(f'git commit -m "{message}"')

@task
def gendeps(c):
    filenames = os.listdir('deps')
    cwd = Path('.')

    path = cwd / 'deps' / 'requirements.in'
    cmd = f'pip-compile --no-header --annotation-style line --no-strip-extras {path}'
    c.run(cmd)

    path_dev = cwd / 'deps' / 'requirements-dev.in'
    cmd = f'pip-compile --no-header --annotation-style line --no-strip-extras -c {path} {path_dev}'
    c.run(cmd)

    path_release = cwd / 'deps' / 'requirements-release.in'
    cmd = f'pip-compile --no-header --annotation-style line --no-strip-extras -c {path} -c {path_dev} {path_release}'
    c.run(cmd)
