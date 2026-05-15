from gpu_clock.app import HELP_KEY, QUIT_KEY, _key_action, _refresh_interval


def test_refresh_interval_defaults_invalid_values():
    assert _refresh_interval(0) == 1.0
    assert _refresh_interval(-1) == 1.0


def test_refresh_interval_has_lower_bound():
    assert _refresh_interval(0.01) == 0.1
    assert _refresh_interval(2.5) == 2.5


def test_key_action_supports_quit_and_help_case_insensitively():
    assert _key_action("q") == QUIT_KEY
    assert _key_action("Q") == QUIT_KEY
    assert _key_action("h") == HELP_KEY
    assert _key_action("H") == HELP_KEY
    assert _key_action("x") is None
