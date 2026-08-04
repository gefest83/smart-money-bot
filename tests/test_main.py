from main import run


def test_run_returns_int():
    assert isinstance(run(), int)
