import re
from melbalabs.summarize_consumes.main import generate_output
from melbalabs.summarize_consumes.main import main

def test_empty_log(capsys):
    args = ['testdata/empty.txt']
    main(args)
    result = capsys.readouterr()
    out = result.out
    err = result.err
    assert 'prices timestamp 20' in out

