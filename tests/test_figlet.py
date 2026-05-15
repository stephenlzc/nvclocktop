from gpu_clock.figlet import render_time


def test_render_time_keeps_stable_width_across_seconds():
    first = render_time("06:06:15 PM")
    second = render_time("06:06:16 PM")

    first_widths = [len(line) for line in first.splitlines()]
    second_widths = [len(line) for line in second.splitlines()]

    assert first_widths == second_widths
    assert len(set(first_widths)) == 1
