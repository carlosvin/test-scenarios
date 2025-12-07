"""Tests for option resolution helpers and registration."""

import os
from typing import Optional
from unittest.mock import ANY, MagicMock, patch

from pytest_scenarios.pytest_fixtures import _get_option, pytest_addoption


def test_get_option_returns_cli_value() -> None:
    """CLI arguments should take priority over any other source."""

    request = MagicMock()
    request.config.getoption.return_value = "cli_value"
    request.config.getini.return_value = "ini_value"

    result = _get_option(request, "test-option", default="default_value")

    assert result == "cli_value"
    request.config.getoption.assert_called_once_with("--test-option", default="ini_value")


def test_get_option_falls_back_to_ini() -> None:
    """When CLI is unset, fall back to pytest.ini configuration."""

    request = MagicMock()
    request.config.getini.return_value = "ini_value"

    def mock_getoption(option: str, default: Optional[str] = None) -> Optional[str]:
        return default

    request.config.getoption.side_effect = mock_getoption

    result = _get_option(request, "test-option", default="default_value")

    assert result == "ini_value"


def test_pytest_addoption_registers_defaults() -> None:
    """pytest_addoption wires CLI and ini registrations with expected defaults."""

    parser = MagicMock()
    group = parser.getgroup.return_value
    ini_parser = group.parser

    pytest_addoption(parser)

    group.addoption.assert_any_call(
        "--templates-path",
        action="store",
        dest="templates_path",
        default="tests/templates",
        help=ANY,
    )
    group.addoption.assert_any_call(
        "--db-name",
        action="store",
        dest="db_name",
        default="test_db",
        help=ANY,
    )
    group.addoption.assert_any_call(
        "--db-url",
        action="store",
        dest="db_url",
        default="mongodb://127.0.0.1:27017",
        help=ANY,
    )
    ini_parser.addini.assert_any_call(
        name="templates-path",
        help=ANY,
        default="tests/templates",
        type="string",
    )
    ini_parser.addini.assert_any_call(
        name="db-name",
        help=ANY,
        default="test_db",
        type="string",
    )
    ini_parser.addini.assert_any_call(
        name="db-url",
        help=ANY,
        default="mongodb://127.0.0.1:27017",
        type="string",
    )


def test_pytest_addoption_honors_environment_defaults() -> None:
    """Environment variables should override hard-coded defaults during registration."""

    parser = MagicMock()
    group = parser.getgroup.return_value
    ini_parser = group.parser

    with patch.dict(os.environ, {"TEMPLATES_PATH": "env/templates"}):
        pytest_addoption(parser)

    group.addoption.assert_any_call(
        "--templates-path",
        action="store",
        dest="templates_path",
        default="env/templates",
        help=ANY,
    )
    ini_parser.addini.assert_any_call(
        name="templates-path",
        help=ANY,
        default="env/templates",
        type="string",
    )
