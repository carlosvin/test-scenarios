"""Tests to improve code coverage for option resolution and registration."""

import os
from unittest.mock import ANY, MagicMock, patch

from pytest_scenarios.pytest_fixtures import _get_option, pytest_addoption


def test_get_option_from_config():
    """Test getting option from pytest config."""
    request = MagicMock()
    request.config.getoption.return_value = "config_value"
    request.config.getini.return_value = None

    result = _get_option(request, "test-option", default="default_value")

    assert result == "config_value"


def test_get_option_from_environment():
    """Test getting option from environment variable."""
    request = MagicMock()

    def mock_getoption(opt, default=None):
        return default

    request.config.getoption = mock_getoption
    request.config.getini.return_value = None

    with patch.dict(os.environ, {"TEST_OPTION": "env_value"}):
        result = _get_option(request, "test-option", default="default_value")

    assert result == "env_value"


def test_get_option_default():
    """Test getting option default when not in config or environment."""
    request = MagicMock()

    def mock_getoption(opt, default=None):
        return default

    request.config.getoption = mock_getoption
    request.config.getini.return_value = None

    with patch.dict(os.environ, {}, clear=False):
        result = _get_option(request, "test-option", default="default_value")

    assert result == "default_value"


def test_get_option_name_with_hyphens_converts_to_underscores():
    """Test that option names with hyphens are converted to underscores for env vars."""
    request = MagicMock()

    def mock_getoption(opt, default=None):
        return default

    request.config.getoption = mock_getoption
    request.config.getini.return_value = None

    with patch.dict(os.environ, {"DB_URL": "mongodb://localhost"}):
        result = _get_option(request, "db-url", default="default")

    assert result == "mongodb://localhost"


def test_get_option_from_ini():
    """Test that pytest.ini values are used when CLI and env are unset."""
    request = MagicMock()
    request.config.getoption.return_value = None
    request.config.getini.return_value = "ini_value"

    with patch.dict(os.environ, {}, clear=False):
        result = _get_option(request, "test-option", default="default_value")

    assert result == "ini_value"


def test_get_option_handles_missing_ini():
    """Fallback to default when config.getini raises a ValueError."""

    request = MagicMock()
    request.config.getoption.return_value = None
    request.config.getini.side_effect = ValueError

    with patch.dict(os.environ, {}, clear=False):
        result = _get_option(request, "test-option", default="default_value")

    assert result == "default_value"


def test_pytest_addoption_registers_custom_options():
    """Ensure pytest_addoption registers CLI and ini options without errors."""

    parser = MagicMock()
    group = parser.getgroup.return_value

    pytest_addoption(parser)

    group.addoption.assert_any_call(
        "--templates-path",
        action="store",
        dest="templates_path",
        default=None,
        help=ANY,
    )
    group.addoption.assert_any_call(
        "--db-url",
        action="store",
        dest="db_url",
        default=None,
        help=ANY,
    )
    group.addoption.assert_any_call(
        "--db-name",
        action="store",
        dest="db_name",
        default=None,
        help=ANY,
    )
    parser.addini.assert_any_call(
        "templates-path",
        ANY,
        default="tests/templates",
    )
    parser.addini.assert_any_call(
        "db-url",
        ANY,
        default="mongodb://127.0.0.1:27017/?directConnection=true",
    )
    parser.addini.assert_any_call(
        "db-name",
        ANY,
        default="test_db",
    )
