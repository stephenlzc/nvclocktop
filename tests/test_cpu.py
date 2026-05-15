from gpu_clock.cpu import _load_average, _mac_cpu_model


def test_load_average_is_optional():
    value = _load_average()
    assert value is None or len(value) == 3


def test_mac_cpu_model_has_fallback(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise TimeoutError

    monkeypatch.setattr("subprocess.run", raise_timeout)
    assert _mac_cpu_model()
