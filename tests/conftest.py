"""
Pytest Configuration & Fixtures
"""

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run live golden integration tests that hit real websites",
    )


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(
            reason="Integration test skipped by default. Pass --run-integration to run."
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)
