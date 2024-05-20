import pytest

from melbalabs.summarize_consumes.main import create_app


@pytest.fixture
def app():
    time_start = 1700264355.3831115
    return create_app(time_start=time_start, expert_log_unparsed_lines=True)
