from gpu_clock.gpu import _gpu_process_from_row, _int_text, _metal_version, _parse_csv_lines


def test_parse_csv_lines_trims_cells():
    assert _parse_csv_lines("GPU, 1, 2\nOther, 3, 4") == [
        ["GPU", "1", "2"],
        ["Other", "3", "4"],
    ]


def test_gpu_process_keeps_basic_nvidia_smi_fields_for_missing_proc():
    process = _gpu_process_from_row(["999999999", "python", "188"])
    assert process.pid == 999999999
    assert process.process_name == "python"
    assert process.used_memory_mib == 188
    assert process.user is None
    assert process.command is None


def test_apple_gpu_helpers_parse_system_profiler_values():
    assert _int_text("16") == 16
    assert _int_text(None) is None
    assert _metal_version("spdisplays_metal3") == "Metal 3"
    assert _metal_version("unknown") is None
