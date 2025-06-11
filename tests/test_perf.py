import io
import tracemalloc
import time
import cProfile
import pstats
from collections import defaultdict

import pytest
import lark

@pytest.mark.skip()
def test_basic(app):
    filename = r'testdata/naxx-superwow-2025-06-02.txt'


    startts = time.time()
    tracemalloc.start()
    with io.open(filename, encoding="utf8") as f:
        for line in f:
            pass

    endts = time.time()
    current, peak = tracemalloc.get_traced_memory()
    print(f"Memory usage: {current / 1024 / 1024:.1f} MB")
    print('time', endts - startts)

    """
    0.4 sec to finish
    not an issue
    """



@pytest.mark.skip()
def test_basic2(app):
    filename = r'testdata/naxx-superwow-2025-06-02.txt'


    startts = time.time()
    tracemalloc.start()
    with io.open(filename, encoding="utf8") as f:
        for line in f:
            pass

            try:
                tree = app.parser.parse(line)
            except lark.LarkError:
                pass

    endts = time.time()
    current, peak = tracemalloc.get_traced_memory()
    print(f"Memory usage: {current / 1024 / 1024:.1f} MB")
    print('time', endts - startts)
    import pdb;pdb.set_trace()

    """
    0.2mb mem used
    not an issue
    """



@pytest.mark.skip()
def test_basic3(app):
    filename = r'testdata/naxx-superwow-2025-06-02.txt'

    profiler = cProfile.Profile()
    profiler.enable()
    startts = time.time()

    with io.open(filename, encoding="utf8") as f:
        for line in f:
            try:
                tree = app.parser.parse(line)
            except lark.LarkError:
                pass

    endts = time.time()
    profiler.disable()
    print('time', endts - startts)

    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')

    import pdb;pdb.set_trace()
    pass

    r"""
    stats.print_stats(20)
         242636180 function calls (242631756 primitive calls) in 167.183 seconds

   Ordered by: cumulative time
   List reduced from 148 to 20 due to restriction <20>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   477531    0.543    0.000  167.164    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\lark.py:640(parse)
   477531    1.008    0.000  166.621    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\parser_frontends.py:100(parse)
   477531    0.465    0.000  162.189    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\parsers\lalr_parser.py:40(parse)
   477531    0.988    0.000  161.724    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\parsers\lalr_parser.py:83(parse)
   477531    7.459    0.000  160.318    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\parsers\lalr_parser.py:91(parse_from_state)
 10521770    8.977    0.000  101.349    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\lexer.py:661(lex)
 10523157   25.101    0.000   90.320    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\lexer.py:590(next_token)
 10520355   24.896    0.000   49.792    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\parsers\lalr_parser_state.py:67(feed_token)
 10047041    7.399    0.000   35.087    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\lexer.py:587(match)
 10525001    9.625    0.000   26.308    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\lexer.py:387(match)
 11833334    8.499    0.000   21.718    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\lexer.py:202(__new__)
 10526297   13.547    0.000   13.547    0.000 {method 'match' of 're.Pattern' objects}
 11833334    9.089    0.000   13.219    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\lexer.py:213(_future_new)
 10045640    5.236    0.000    7.353    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\lexer.py:292(feed)
 32670573    7.305    0.000    7.305    0.000 {method 'append' of 'list' objects}
  1624534    3.444    0.000    7.266    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\venv\Lib\site-packages\lark\parse_tree_builder.py:145(__call__)
24465262/24464050    4.221    0.000    4.221    0.000 {built-in method builtins.len}
 11833335    4.130    0.000    4.130    0.000 {built-in method __new__ of type object at 0x00007FFEE88808F0}
  1254318    1.427    0.000    3.751    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\src\melbalabs\summarize_consumes\main.py:72(multiword)
 17356491    3.453    0.000    3.453    0.000 {built-in method builtins.isinstance}
    """




@pytest.mark.skip()
def test_basic4(app):
    filename = r'testdata/naxx-superwow-2025-06-02.txt'

    line_times = defaultdict(list)
    with io.open(filename, encoding="utf8") as f:
        for line in f:
            start = time.perf_counter()
            try:
                tree = app.parser.parse(line)
                subtree = tree.children[1]
                elapsed = time.perf_counter() - start
                line_type = subtree.data

                line_times[line_type].append(elapsed)
            except lark.LarkError:
                pass

    alltimes = []
    for line_type, times in line_times.items():
        avg_time = sum(times) / len(times)
        msg = f"{line_type}: {avg_time*1000:.3f}ms avg, {len(times)} lines"
        alltimes.append((len(times), msg))

    for lentimes, msg in sorted(alltimes):
        print(msg)


    r"""


is_destroyed_line: 0.099ms avg, 4 lines
is_dismissed_line: 0.113ms avg, 4 lines
pet_begins_eating_line: 0.098ms avg, 5 lines
equipped_durability_loss: 0.087ms avg, 6 lines
block_ability_line: 0.149ms avg, 7 lines
interrupts_line: 0.104ms avg, 9 lines
performs_line: 0.102ms avg, 9 lines
is_killed_line: 0.096ms avg, 27 lines
immune_line: 0.087ms avg, 28 lines
gains_happiness_line: 0.137ms avg, 29 lines
is_immune_ability_line: 0.125ms avg, 30 lines
was_evaded_line: 0.122ms avg, 33 lines
creates_line: 0.103ms avg, 34 lines
falls_line: 0.088ms avg, 39 lines
misses_ability_line: 0.122ms avg, 71 lines
slain_line: 0.107ms avg, 140 lines
performs_on_line: 0.118ms avg, 242 lines
combatant_info_line: 0.082ms avg, 584 lines
parry_ability_line: 0.120ms avg, 692 lines
immune_ability_line: 0.125ms avg, 738 lines
removed_line: 0.102ms avg, 760 lines
causes_damage_line: 0.116ms avg, 810 lines
dodge_ability_line: 0.121ms avg, 1027 lines
begins_to_perform_line: 0.105ms avg, 1061 lines
reflects_damage_line: 0.124ms avg, 1143 lines
parry_line: 0.106ms avg, 1156 lines
dies_line: 0.089ms avg, 1266 lines
misses_line: 0.105ms avg, 1990 lines
dodges_line: 0.105ms avg, 2530 lines
uses_line: 0.103ms avg, 3163 lines
resist_line: 0.121ms avg, 3208 lines
gains_energy_line: 0.130ms avg, 3701 lines
gains_health_line: 0.124ms avg, 3872 lines
gains_rage_line: 0.128ms avg, 5680 lines
gains_extra_attacks_line: 0.118ms avg, 5771 lines
casts_line: 0.116ms avg, 9447 lines
afflicted_line: 0.103ms avg, 17241 lines
begins_to_cast_line: 0.013ms avg, 19222 lines
hits_autoattack_line: 0.013ms avg, 33271 lines
gains_line: 0.013ms avg, 40019 lines
suffers_line: 0.015ms avg, 40398 lines
fades_line: 0.011ms avg, 41059 lines
heals_line: 0.013ms avg, 43326 lines
hits_ability_line: 0.014ms avg, 83261 lines
gains_mana_line: 0.011ms avg, 109936 lines

    """




