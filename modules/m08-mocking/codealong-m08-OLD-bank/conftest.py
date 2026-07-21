"""Module 8 code-along — register the `integration` marker so `pytest -m` works cleanly."""


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: test that hits a live server")
