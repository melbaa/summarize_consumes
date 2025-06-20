import io
import tracemalloc
import time
import cProfile
import pstats
from collections import defaultdict

import pytest


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
            
            p_ts_end = line.find('  ')
            if p_ts_end == -1: continue
            tree = app.parser.parse(line, p_ts_end)
            if not tree: continue
        

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
        
            p_ts_end = line.find('  ')
            if p_ts_end == -1: continue
            tree = app.parser.parse(line, p_ts_end)
            if not tree: continue
        

    endts = time.time()
    profiler.disable()
    print('time', endts - startts)

    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')

    stats.print_stats(100)

    r"""
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
    filename = r'testperfdata/kara40-superwow-07-06-2025.txt'

    line_times = defaultdict(list)
    with io.open(filename, encoding="utf8") as f:
        for line in f:
            start = time.perf_counter()
            p_ts_end = line.find('  ')
            if p_ts_end == -1: continue
            tree = app.parser.parse(line, p_ts_end)
            if not tree: continue
            subtree = tree.children[1]
            elapsed = time.perf_counter() - start
            line_type = subtree.data

            line_times[line_type].append(elapsed)
        
    alltimes = []
    for line_type, times in line_times.items():
        avg_time = sum(times) / len(times)
        avg_time *= 1000
        msg = f"{line_type}: {avg_time:.3f}ms avg, {len(times)} lines"
        if avg_time > 0.02:
            msg += '        < ---- BAD'
        alltimes.append((len(times), msg))

    for lentimes, msg in sorted(alltimes):
        print(msg)


    r"""

tests/test_perf.py::test_basic4 fails_to_dispel_line: 0.015ms avg, 1 lines
is_killed_line: 0.014ms avg, 3 lines
block_ability_line: 0.017ms avg, 4 lines
is_destroyed_line: 0.013ms avg, 8 lines
was_evaded_line: 0.013ms avg, 10 lines
equipped_durability_loss_line: 0.017ms avg, 12 lines
interrupts_line: 0.017ms avg, 13 lines
is_reflected_back_line: 0.014ms avg, 55 lines
is_immune_ability_line: 0.012ms avg, 58 lines
causes_damage_line: 0.011ms avg, 81 lines
creates_line: 0.013ms avg, 82 lines
slain_line: 0.013ms avg, 113 lines
misses_ability_line: 0.009ms avg, 114 lines
falls_line: 0.011ms avg, 125 lines
begins_to_perform_line: 0.010ms avg, 153 lines
performs_on_line: 0.013ms avg, 329 lines
immune_line: 0.012ms avg, 569 lines
removed_line: 0.012ms avg, 1177 lines
parry_ability_line: 0.012ms avg, 1183 lines
dies_line: 0.009ms avg, 1431 lines
dodge_ability_line: 0.011ms avg, 1525 lines
combatant_info_line: 0.019ms avg, 1618 lines
parry_line: 0.010ms avg, 1821 lines
reflects_damage_line: 0.011ms avg, 2122 lines
immune_ability_line: 0.015ms avg, 2656 lines
dodges_line: 0.009ms avg, 3102 lines
misses_line: 0.009ms avg, 3527 lines
gains_energy_line: 0.009ms avg, 3960 lines
uses_line: 0.009ms avg, 5101 lines
resist_line: 0.008ms avg, 7501 lines
gains_extra_attacks_line: 0.007ms avg, 7819 lines
gains_rage_line: 0.008ms avg, 12756 lines
casts_line: 0.008ms avg, 16925 lines
gains_health_line: 0.009ms avg, 18176 lines
afflicted_line: 0.005ms avg, 20359 lines
begins_to_cast_line: 0.005ms avg, 24774 lines
suffers_line: 0.006ms avg, 36617 lines
heals_line: 0.004ms avg, 47223 lines
hits_autoattack_line: 0.004ms avg, 51016 lines
fades_line: 0.004ms avg, 57770 lines
gains_line: 0.005ms avg, 59728 lines
gains_mana_line: 0.003ms avg, 111084 lines
hits_ability_line: 0.004ms avg, 159598 lines

    """


def f1(val):
    return True, val


class Result:
    __slots__ = ('success', 'value')
    def __init__(self):
        self.success = False
        self.value = None

result_cache = Result()

def f2(val):
    result_cache.success = True
    result_cache.value = val
    return result_cache

def f3(val):
    raise ValueError('oops')

@pytest.mark.skip()
def test_tuple_return():

    profiler = cProfile.Profile()
    profiler.enable()

    for i in range(50_000_000):
        success, val = f1(i)

    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(100)

    r"""


tests/test_perf.py::test_tuple_return          50000001 function calls in 6.582 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
 50000000    6.582    0.000    6.582    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\tests\test_perf.py:212(f1)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
    """

@pytest.mark.skip()
def test_cache_result_return():

    profiler = cProfile.Profile()
    profiler.enable()

    for i in range(50_000_000):
        retval = f2(i)


    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(100)

    r"""
tests/test_perf.py::test_cache_result_return          50000001 function calls in 7.557 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
 50000000    7.557    0.000    7.557    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\tests\test_perf.py:224(f2)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}


    """

@pytest.mark.skip()
def test_exc_result():


    profiler = cProfile.Profile()
    profiler.enable()

    for i in range(50_000_000):
        try:
            f3(i)
        except ValueError as e:
            pass

    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(100)

    r"""

tests/test_perf.py::test_exc_result          50000001 function calls in 16.903 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
 50000000   16.902    0.000   16.902    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\tests\test_perf.py:229(f3)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}

    """
