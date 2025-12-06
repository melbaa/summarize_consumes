
import pytest
import io
from melbalabs.summarize_consumes.main import parse_line, AutoAttackStats, AutoAttackSummary

def test_auto_attack_stats(app):
    lines = """
4/14 21:49:18.451  PlayerHits hits Target for 100.
4/14 21:49:18.452  PlayerCrits crits Target for 200.
4/14 21:49:18.453  PlayerGlances hits Target for 50. (glancing)
4/14 21:49:18.455  PlayerPartBlock hits Target for 50. (10 blocked)
4/14 21:49:18.456  PlayerFullBlock attacks. Target blocks.
4/14 21:49:18.457  PlayerParries attacks. Target parries.
4/14 21:49:18.458  PlayerDodges attacks. Target dodges.
4/14 21:49:18.459  PlayerMisses misses Target.
4/14 21:49:18.460  PlayerMixed hits Target for 100.
4/14 21:49:18.461  PlayerMixed crits Target for 200.
4/14 21:49:18.462  PlayerMixed hits Target for 50. (glancing)

# Players must consume something to be tracked
4/14 21:49:18.000  PlayerHits 's Goblin Sapper Charge hits Target for 500.
4/14 21:49:18.001  PlayerCrits 's Goblin Sapper Charge hits Target for 500.
4/14 21:49:18.002  PlayerGlances 's Goblin Sapper Charge hits Target for 500.
4/14 21:49:18.003  PlayerPartBlock 's Goblin Sapper Charge hits Target for 500.
4/14 21:49:18.004  PlayerFullBlock 's Goblin Sapper Charge hits Target for 500.
4/14 21:49:18.005  PlayerParries 's Goblin Sapper Charge hits Target for 500.
4/14 21:49:18.006  PlayerDodges 's Goblin Sapper Charge hits Target for 500.
4/14 21:49:18.007  PlayerMisses 's Goblin Sapper Charge hits Target for 500.
4/14 21:49:18.008  PlayerMixed 's Goblin Sapper Charge hits Target for 500.


"""
    for line in lines.strip().splitlines(keepends=True):
        parse_line(app, line)

    stats = app.auto_attack_stats.stats

    # Verify Counts
    assert stats["PlayerHits"]["hits"] == 1
    assert stats["PlayerHits"]["swings"] == 1

    assert stats["PlayerCrits"]["crits"] == 1
    assert stats["PlayerCrits"]["swings"] == 1

    assert stats["PlayerGlances"]["glances"] == 1
    assert stats["PlayerGlances"]["swings"] == 1

    assert stats["PlayerPartBlock"]["blocks"] == 1
    assert stats["PlayerPartBlock"]["swings"] == 1

    assert stats["PlayerFullBlock"]["blocks"] == 1
    assert stats["PlayerFullBlock"]["swings"] == 1

    assert stats["PlayerParries"]["parries"] == 1
    assert stats["PlayerParries"]["swings"] == 1

    assert stats["PlayerDodges"]["dodges"] == 1
    assert stats["PlayerDodges"]["swings"] == 1

    assert stats["PlayerMisses"]["misses"] == 1
    assert stats["PlayerMisses"]["swings"] == 1

    assert stats["PlayerMixed"]["hits"] == 1
    assert stats["PlayerMixed"]["crits"] == 1
    assert stats["PlayerMixed"]["glances"] == 1
    assert stats["PlayerMixed"]["swings"] == 3

    output = io.StringIO()
    app.auto_attack_summary.print(output)
    content = output.getvalue()

    assert "   PlayerHits swings 1" in content
    assert "      hits 1   (100.0%)" in content

    assert "   PlayerCrits swings 1" in content
    assert "      crits 1   (100.0%)" in content

    assert "   PlayerGlances swings 1" in content
    assert "      glances 1   (100.0%)" in content
    
    assert "   PlayerMixed swings 3" in content
    assert "      hits 1   (33.3%)" in content
    assert "      crits 1   (33.3%)" in content
    assert "      glances 1   (33.3%)" in content
