"""Tests to improve code coverage for all modules."""

import os
from unittest.mock import MagicMock, patch

from pytest_scenarios.pytest_fixtures import _get_option


def test_get_option_from_config():
    """Test getting option from pytest config."""
    request = MagicMock()
    request.config.getoption.return_value = "config_value"

    result = _get_option(request, "test-option", default="default_value")

    assert result == "config_value"


def test_get_option_from_environment():
    """Test getting option from environment variable."""
    request = MagicMock()

    def mock_getoption(opt, default=None):
        return default

    request.config.getoption = mock_getoption

    with patch.dict(os.environ, {"TEST_OPTION": "env_value"}):
        result = _get_option(request, "test-option", default="default_value")

    assert result == "env_value"


def test_get_option_default():
    """Test getting option default when not in config or environment."""
    request = MagicMock()

    def mock_getoption(opt, default=None):
        return default

    request.config.getoption = mock_getoption

    with patch.dict(os.environ, {}, clear=False):
        result = _get_option(request, "test-option", default="default_value")

    assert result == "default_value"


def test_get_option_name_with_hyphens_converts_to_underscores():
    """Test that option names with hyphens are converted to underscores for env vars."""
    request = MagicMock()

    def mock_getoption(opt, default=None):
        return default

    request.config.getoption = mock_getoption

    with patch.dict(os.environ, {"DB_URL": "mongodb://localhost"}):
        result = _get_option(request, "db-url", default="default")

    assert result == "mongodb://localhost"
