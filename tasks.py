import os
import shutil
from pathlib import Path

from invoke import task

try:
    from colorama import just_fix_windows_console
    just_fix_windows_console()
except ModuleNotFoundError:
    pass


@task
def damage(c):
    cmd = "python -m melbalabs.summarize_consumes.main ..\..\..\Logs\WoWCombatLog.txt --expert-log-unparsed-lines --write-summary --write-damage-output --write-healing-output"
    c.run(cmd)



@task
def pytest(c):
    cmd = "pytest -vs --cache-clear --pdb --color=yes"
    c.run(cmd)

@task
def excludes(c):
    cmd = r"grep -v -f .\excludes.txt ..\..\..\Logs\WoWCombatLog.txt"
    c.run(cmd)

@task
def updateprices(c):
    cwd = Path('.')
    input_file = cwd / 'testdata' / 'empty.txt'
    print('downloading prices')
    cmd = f"python -m melbalabs.summarize_consumes.main {input_file} --expert-write-web-prices"
    c.run(cmd)

@task
def tar(c):
    c.run('tar --exclude __pycache__ -czvf src.tgz src')

@task
def genpkg(c):
    shutil.rmtree(Path('dist'))
    c.run('python -m build')

@task
def gendeps(c):
    cwd = Path('.')

    path = cwd / 'deps' / 'requirements'
    cmd = f'pip-compile --no-header --annotation-style line --no-strip-extras {path}.in'
    c.run(cmd)

    path_dev = cwd / 'deps' / 'requirements-dev'
    cmd = f'pip-compile --no-header --annotation-style line --no-strip-extras -c {path}.txt {path_dev}.in'
    c.run(cmd)

    path_release = cwd / 'deps' / 'requirements-release'
    cmd = f'pip-compile --no-header --annotation-style line --no-strip-extras -c {path}.txt -c {path_dev}.txt {path_release}.in'
    c.run(cmd)
