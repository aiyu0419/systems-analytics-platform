"""Smoke tests for Python package installation."""

from importlib.metadata import version

import systems_analytics


def test_package_is_importable() -> None:
    assert systems_analytics.__name__ == "systems_analytics"


def test_package_version() -> None:
    installed_version = version("systems-analytics-platform")
    assert installed_version == "0.1.0"
