import io
import tracemalloc
import time
import cProfile
import pstats
from collections import defaultdict
from typing import NewType

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
    filename = r"testperfdata/kara40-12-02-26.txt"

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
            subtree = tree.subtree
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

TreeType.EQUIPPED_DURABILITY_LOSS_LINE: 0.006ms avg, 1 lines
TreeType.IS_KILLED_LINE: 0.008ms avg, 1 lines
TreeType.INTERRUPTS_LINE: 0.009ms avg, 2 lines
TreeType.PET_BEGINS_EATING_LINE: 0.006ms avg, 3 lines
TreeType.IS_DESTROYED_LINE: 0.006ms avg, 4 lines
TreeType.IS_REFLECTED_BACK_LINE: 0.006ms avg, 5 lines
TreeType.BLOCK_ABILITY_LINE: 0.007ms avg, 9 lines
TreeType.PERFORMS_LINE: 0.004ms avg, 10 lines
TreeType.WAS_EVADED_LINE: 0.005ms avg, 15 lines
TreeType.GAINS_HAPPINESS_LINE: 0.008ms avg, 31 lines
TreeType.FALLS_LINE: 0.004ms avg, 77 lines
TreeType.CREATES_LINE: 0.005ms avg, 87 lines
TreeType.SLAIN_LINE: 0.007ms avg, 97 lines
TreeType.IS_IMMUNE_ABILITY_LINE: 0.005ms avg, 122 lines
TreeType.PERFORMS_ON_LINE: 0.004ms avg, 195 lines
TreeType.REFLECTS_DAMAGE_LINE: 0.003ms avg, 257 lines
TreeType.MISSES_ABILITY_LINE: 0.003ms avg, 338 lines
TreeType.REMOVED_LINE: 0.004ms avg, 369 lines
TreeType.BEGINS_TO_PERFORM_LINE: 0.004ms avg, 491 lines
TreeType.IMMUNE_LINE: 0.004ms avg, 519 lines
TreeType.DIES_LINE: 0.003ms avg, 602 lines
TreeType.COMBATANT_INFO_LINE: 0.007ms avg, 626 lines
TreeType.PARRY_LINE: 0.004ms avg, 721 lines
TreeType.MISSES_LINE: 0.003ms avg, 768 lines
TreeType.PARRY_ABILITY_LINE: 0.005ms avg, 849 lines
TreeType.DODGE_ABILITY_LINE: 0.004ms avg, 863 lines
TreeType.DRAINS_MANA_LINE: 0.008ms avg, 1103 lines
TreeType.DODGES_LINE: 0.003ms avg, 1269 lines
TreeType.GAINS_ENERGY_LINE: 0.003ms avg, 1385 lines
TreeType.IMMUNE_ABILITY_LINE: 0.004ms avg, 1726 lines
TreeType.CAUSES_DAMAGE_LINE: 0.003ms avg, 1809 lines
TreeType.USES_LINE: 0.003ms avg, 2390 lines
TreeType.GAINS_HEALTH_LINE: 0.003ms avg, 3052 lines
TreeType.RESIST_LINE: 0.003ms avg, 3742 lines
TreeType.GAINS_EXTRA_ATTACKS_LINE: 0.002ms avg, 3807 lines
TreeType.GAINS_RAGE_LINE: 0.003ms avg, 5662 lines
TreeType.AFFLICTED_LINE: 0.002ms avg, 10273 lines
TreeType.HITS_AUTOATTACK_LINE: 0.002ms avg, 16978 lines
TreeType.HEALS_LINE: 0.002ms avg, 18950 lines
TreeType.BEGINS_TO_CAST_LINE: 0.002ms avg, 19520 lines
TreeType.SUFFERS_LINE_SOURCE: 0.002ms avg, 23014 lines
TreeType.GAINS_LINE: 0.002ms avg, 25818 lines
TreeType.FADES_LINE: 0.001ms avg, 25849 lines
TreeType.GAINS_MANA_LINE: 0.001ms avg, 41798 lines
TreeType.HITS_ABILITY_LINE: 0.001ms avg, 84673 lines
TreeType.CASTS_LINE: 0.002ms avg, 136673 lines

    """


@pytest.mark.skip()
def test_basic5(app):
    filename = r"testdata/naxx-superwow-2025-06-02.txt"

    profiler = cProfile.Profile()
    profiler.enable()
    startts = time.time()

    from melbalabs.summarize_consumes.main import parse_log, generate_output

    parse_log(app, filename)
    output = generate_output(app)

    endts = time.time()
    profiler.disable()
    print("time", endts - startts)

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")

    stats.print_stats(100)

    r"""
    # NOTE: Run with `pytest tests/test_perf.py::test_basic5 -s` to see the output

    time 4.992723226547241
         15664031 function calls in 4.990 seconds

   Ordered by: cumulative time
   List reduced from 154 to 100 due to restriction <100>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.128    0.128    4.982    4.982 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:2688(parse_log)
   477531    0.304    0.000    4.847    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1984(parse_line)
   477126    0.680    0.000    2.392    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:2005(process_tree)
   477531    0.939    0.000    2.094    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\parser.py:1375(parse)
  5301702    0.715    0.000    0.715    0.000 {method 'find' of 'str' objects}
   364964    0.382    0.000    0.467    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1030(add)
   477126    0.390    0.000    0.443    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:166(parse)
   477126    0.189    0.000    0.399    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\parser.py:1337(parse_ts)
  1721193    0.232    0.000    0.326    0.000 {method 'get' of 'dict' objects}
   276205    0.176    0.000    0.233    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\timeline.py:57(add)
  1184352    0.141    0.000    0.216    0.000 C:\Users\melba\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\Lib\enum.py:1266(__hash__)
   281243    0.066    0.000    0.182    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:460(rename_spell)
   477126    0.133    0.000    0.133    0.000 {method 'match' of 're.Pattern' objects}
   217451    0.063    0.000    0.109    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1846(detect)
   199988    0.044    0.000    0.080    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1570(add)
   477126    0.077    0.000    0.077    0.000 {method 'groups' of 're.Match' objects}
  1186235    0.075    0.000    0.075    0.000 {built-in method builtins.hash}
   251824    0.033    0.000    0.033    0.000 {method 'rfind' of 'str' objects}
   295507    0.031    0.000    0.031    0.000 {method 'append' of 'list' objects}
    40019    0.010    0.000    0.026    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1577(add_stackcount)
    40444    0.024    0.000    0.024    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:991(__init__)
    45699    0.012    0.000    0.020    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1620(add)
   246615    0.020    0.000    0.020    0.000 {built-in method builtins.len}
    12702    0.010    0.000    0.020    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1416(add_crit)
    10282    0.008    0.000    0.016    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1420(add_glance)
     9189    0.007    0.000    0.015    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1412(add_hit)
   151619    0.014    0.000    0.014    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\timeline.py:54(is_important)
   116532    0.014    0.000    0.014    0.000 {method 'isdigit' of 'str' objects}
   113550    0.012    0.000    0.012    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\timeline.py:12(__init__)
    75073    0.012    0.000    0.012    0.000 {built-in method builtins.min}
    21891    0.007    0.000    0.012    0.000 C:\Users\melba\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\Lib\enum.py:720(__call__)
     5771    0.003    0.000    0.012    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\timeline.py:100(add_extra_attacks)
        1    0.000    0.000    0.010    0.010 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:2711(generate_output)
    57210    0.007    0.000    0.007    0.000 {method 'endswith' of 'str' objects}
        1    0.000    0.000    0.005    0.005 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1770(calculate)
     4176    0.002    0.000    0.005    0.000 <frozen codecs>:319(decode)
    21891    0.005    0.000    0.005    0.000 C:\Users\melba\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\Lib\enum.py:1128(__new__)
     2530    0.002    0.000    0.004    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1428(add_dodge)
     1990    0.002    0.000    0.003    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1432(add_miss)
      605    0.001    0.000    0.003    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1727(get_consumable_price)
     4176    0.003    0.000    0.003    0.000 {built-in method _codecs.utf_8_decode}
     7493    0.002    0.000    0.003    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\entity_model.py:80(has_component)
     5771    0.002    0.000    0.002    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1627(add_extra_attacks)
     1916    0.001    0.000    0.002    0.000 {method 'add' of 'set' objects}
     1156    0.001    0.000    0.002    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1424(add_parry)
     1098    0.001    0.000    0.002    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1436(add_block)
     3484    0.001    0.000    0.002    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1637(__new__)
        1    0.001    0.001    0.002    0.002 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:3051(merge)
      605    0.000    0.000    0.001    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1715(add_consumable)
        1    0.000    0.000    0.001    0.001 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1791(print)
        2    0.000    0.000    0.001    0.001 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1259(flush)
     1150    0.000    0.000    0.001    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1703(total_price)
     1184    0.000    0.000    0.001    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1642(__add__)
     1351    0.001    0.000    0.001    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\entity_model.py:76(get_components)
     1150    0.000    0.000    0.001    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1648(__mul__)
     2003    0.001    0.000    0.001    0.000 {built-in method builtins.print}
        3    0.001    0.000    0.001    0.000 {built-in method _io.open}
     7493    0.001    0.000    0.001    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\entity_model.py:53(get)
    11986    0.001    0.000    0.001    0.000 {built-in method builtins.isinstance}
     1145    0.001    0.000    0.001    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:417(update)
        1    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1447(print)
      545    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1651(__truediv__)
      405    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1256(log)
        1    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1363(print)
      595    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1674(to_string)
        3    0.000    0.000    0.000    0.000 {method '__exit__' of '_io._IOBase' objects}
     3485    0.000    0.000    0.000    0.000 {built-in method __new__ of type object at 0x00007FFFA70028F0}
        2    0.000    0.000    0.000    0.000 {method 'write' of '_io.BufferedWriter' objects}
      210    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1477(fmt)
      411    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1027(<lambda>)
      579    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1288(lookup)
      607    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1630(add_unbridled_wrath)
      420    0.000    0.000    0.000    0.000 <string>:2(__hash__)
      386    0.000    0.000    0.000    0.000 <string>:2(__eq__)
      128    0.000    0.000    0.000    0.000 {built-in method builtins.sorted}
        6    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:749(print_collected_log)
        1    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1199(set_file_size)
        1    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1508(print)
        1    0.000    0.000    0.000    0.000 <frozen genericpath>:60(getsize)
        1    0.000    0.000    0.000    0.000 {built-in method nt.stat}
      892    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1841(is_class)
      135    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1409(<lambda>)
      605    0.000    0.000    0.000    0.000 <string>:2(__init__)
        1    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1863(print)
      229    0.000    0.000    0.000    0.000 {method 'sort' of 'list' objects}
       54    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:250(<lambda>)
      295    0.000    0.000    0.000    0.000 {built-in method builtins.max}
      221    0.000    0.000    0.000    0.000 C:\Users\melba\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\Lib\enum.py:202(__get__)
      127    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:840(add)
       39    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:946(add)
        1    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:807(print)
       94    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:800(add)
        1    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1835(remove_unknown)
      104    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:708(manapot_lookup)
        1    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:819(print)
        1    0.000    0.000    0.000    0.000 C:\Users\melba\AppData\Roaming\uv\python\cpython-3.12.12-windows-x86_64-none\Lib\encodings\__init__.py:71(search_function)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
       84    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:816(add)
       50    0.000    0.000    0.000    0.000 Y:\twow\summarize_consumes\src\melbalabs\summarize_consumes\main.py:1567(<lambda>)
      163    0.000    0.000    0.000    0.000 {method 'pop' of 'dict' objects}

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


MyAlias = str
MyNewType = NewType("MyNewType", str)


@pytest.mark.skip()
def test_overhead1_type_alias_perf():
    import time

    start = time.perf_counter()

    for i in range(50_000_000):
        _ = MyAlias("test")

    elapsed = time.perf_counter() - start
    print(f"\nTypeAlias 50M calls: {elapsed:.3f}s")

    r"""
2026-02-22
TypeAlias 50M calls: 0.872s
    """


@pytest.mark.skip()
def test_overhead1_newtype_perf():
    import time

    start = time.perf_counter()

    for i in range(50_000_000):
        _ = MyNewType("test")

    elapsed = time.perf_counter() - start
    print(f"\nNewType 50M calls: {elapsed:.3f}s")

    r"""
2026-02-22
NewType 50M calls: 1.374s
    """
