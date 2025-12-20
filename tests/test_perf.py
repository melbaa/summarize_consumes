import io
import tracemalloc
import time
import cProfile
import pstats
from collections import defaultdict

import pytest


@pytest.mark.skip()
def test_basic(app):
    filename = r"testdata/naxx-superwow-2025-06-02.txt"

    startts = time.time()
    tracemalloc.start()
    with io.open(filename, encoding="utf8") as f:
        for line in f:
            pass

    endts = time.time()
    current, peak = tracemalloc.get_traced_memory()
    print(f"Memory usage: {current / 1024 / 1024:.1f} MB")
    print("time", endts - startts)

    """
    0.4 sec to finish
    not an issue
    """


@pytest.mark.skip()
def test_basic2(app):
    filename = r"testdata/naxx-superwow-2025-06-02.txt"

    startts = time.time()
    tracemalloc.start()
    with io.open(filename, encoding="utf8") as f:
        for line in f:
            p_ts_end = line.find("  ")
            if p_ts_end == -1:
                continue
            tree = app.parser.parse(line, p_ts_end)
            if not tree:
                continue

    endts = time.time()
    current, peak = tracemalloc.get_traced_memory()
    print(f"Memory usage: {current / 1024 / 1024:.1f} MB")
    print("time", endts - startts)
    import pdb

    pdb.set_trace()

    """
    0.2mb mem used
    not an issue
    """


@pytest.mark.skip()
def test_basic3(app):
    filename = r"testdata/naxx-superwow-2025-06-02.txt"

    profiler = cProfile.Profile()
    profiler.enable()
    startts = time.time()

    with io.open(filename, encoding="utf8") as f:
        for line in f:
            p_ts_end = line.find("  ")
            if p_ts_end == -1:
                continue
            tree = app.parser.parse(line, p_ts_end)
            if not tree:
                continue

    endts = time.time()
    profiler.disable()
    print("time", endts - startts)

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")

    stats.print_stats(100)

    r"""
tests/test_perf.py::test_basic3 time 1.914053201675415
         8156257 function calls in 1.735 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   477531    0.721    0.000    1.692    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\parser.py:295(parse)
  5214987    0.566    0.000    0.566    0.000 {method 'find' of 'str' objects}
   477126    0.199    0.000    0.362    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\parser.py:259(parse_ts)
   477126    0.107    0.000    0.107    0.000 {method 'match' of 're.Pattern' objects}
   477126    0.055    0.000    0.055    0.000 {method 'groups' of 're.Match' objects}
   249358    0.026    0.000    0.026    0.000 {method 'rfind' of 'str' objects}
   246590    0.014    0.000    0.014    0.000 {built-in method builtins.len}
   116532    0.010    0.000    0.010    0.000 {method 'isdigit' of 'str' objects}
    75073    0.009    0.000    0.009    0.000 {built-in method builtins.min}
   145672    0.008    0.000    0.008    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\parser.py:11(__init__)
    21891    0.005    0.000    0.007    0.000 C:\Users\melba\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\Lib\enum.py:720(__call__)
    98782    0.005    0.000    0.005    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\parser.py:103(__init__)
    41181    0.004    0.000    0.004    0.000 {method 'endswith' of 'str' objects}
     4176    0.001    0.000    0.003    0.000 <frozen codecs>:319(decode)
    21891    0.003    0.000    0.003    0.000 C:\Users\melba\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\Lib\enum.py:1128(__new__)
     4176    0.002    0.000    0.002    0.000 {built-in method _codecs.utf_8_decode}
     7013    0.001    0.000    0.001    0.000 {method 'append' of 'list' objects}
        1    0.000    0.000    0.000    0.000 {built-in method _io.open}
        1    0.000    0.000    0.000    0.000 C:\Users\melba\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\Lib\encodings\__init__.py:71(search_function)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        1    0.000    0.000    0.000    0.000 {method '__exit__' of '_io._IOBase' objects}
        1    0.000    0.000    0.000    0.000 C:\Users\melba\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\Lib\encodings\utf_8.py:33(getregentry)
        1    0.000    0.000    0.000    0.000 C:\Users\melba\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\Lib\encodings\__init__.py:43(normalize_encoding)
        1    0.000    0.000    0.000    0.000 <frozen codecs>:94(__new__)
        1    0.000    0.000    0.000    0.000 <frozen codecs>:309(__init__)
        1    0.000    0.000    0.000    0.000 {built-in method builtins.__import__}
        4    0.000    0.000    0.000    0.000 {method 'isalnum' of 'str' objects}
        2    0.000    0.000    0.000    0.000 {built-in method time.time}
        2    0.000    0.000    0.000    0.000 {method 'get' of 'dict' objects}
        4    0.000    0.000    0.000    0.000 {method 'isascii' of 'str' objects}
        1    0.000    0.000    0.000    0.000 {built-in method __new__ of type object at 0x00007FF9A48428F0}
        2    0.000    0.000    0.000    0.000 {built-in method builtins.isinstance}
        1    0.000    0.000    0.000    0.000 {method 'join' of 'str' objects}
        1    0.000    0.000    0.000    0.000 <frozen codecs>:260(__init__)
    """


@pytest.mark.skip()
def test_basic4(app):
    filename = r"testdata/naxx-superwow-2025-06-02.txt"
    filename = r"testperfdata/kara40-superwow-07-06-2025.txt"

    line_times = defaultdict(list)
    with io.open(filename, encoding="utf8") as f:
        for line in f:
            start = time.perf_counter()
            p_ts_end = line.find("  ")
            if p_ts_end == -1:
                continue
            tree = app.parser.parse(line, p_ts_end)
            if not tree:
                continue
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
            msg += "        < ---- BAD"
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
    __slots__ = ("success", "value")

    def __init__(self):
        self.success = False
        self.value = None


result_cache = Result()


def f2(val):
    result_cache.success = True
    result_cache.value = val
    return result_cache


def f3(val):
    raise ValueError("oops")


@pytest.mark.skip()
def test_tuple_return():
    profiler = cProfile.Profile()
    profiler.enable()

    for i in range(50_000_000):
        success, val = f1(i)

    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
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
    stats.sort_stats("cumulative")
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
    stats.sort_stats("cumulative")
    stats.print_stats(100)

    r"""

tests/test_perf.py::test_exc_result          50000001 function calls in 16.903 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
 50000000   16.902    0.000   16.902    0.000 Y:\turtle_client_116\Interface\AddOns\summarize_consumes\tests\test_perf.py:229(f3)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}

    """
