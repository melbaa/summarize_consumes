import pytest
import time

from melbalabs.summarize_consumes.main import create_app


@pytest.fixture
def app():
    time_start = 1700264355.3831115
    prices_server = "nord"
    return create_app(
        time_start=time_start,
        expert_log_unparsed_lines=True,
        prices_server=prices_server,
        expert_disable_web_prices=False,
        expert_deterministic_logs=True,
        expert_log_superwow_merge=False,
        write_encounter_mobs_output=False,
    )


@pytest.fixture
def app_log_merge():
    time_start = 1700264355.3831115
    prices_server = "nord"
    return create_app(
        time_start=time_start,
        expert_log_unparsed_lines=True,
        prices_server=prices_server,
        expert_disable_web_prices=False,
        expert_deterministic_logs=True,
        expert_log_superwow_merge=True,
        write_encounter_mobs_output=False,
    )


@pytest.fixture
def app_nondeterministic():
    prices_server = "nord"
    time_start = time.time()
    return create_app(
        time_start=time_start,
        expert_log_unparsed_lines=True,
        prices_server=prices_server,
        expert_disable_web_prices=False,
        expert_deterministic_logs=False,
        expert_log_superwow_merge=False,
        write_encounter_mobs_output=False,
    )
