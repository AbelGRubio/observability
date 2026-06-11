"""Unit tests for custom settings loading and configuration source behavior."""

import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from typing import Generator
import warnings

# Assuming the file is named custom_settings.py
from observe_core.custom_settings import load_cfg_file, CustomSettings


class TestCustomSettings(unittest.TestCase):
    """Unit tests for configuration loading and custom Pydantic settings."""

    def test_load_cfg_file_not_found(self) -> None:
        """Test that load_cfg_file returns an empty dict and warns when the file is missing."""
        non_existent_file: Path = Path("./non_existent_config.cfg")

        with patch("os.path.isfile", return_value=False):
            with warnings.catch_warnings(record=True) as triggered_warnings:
                warnings.simplefilter("always")
                result = load_cfg_file(non_existent_file)

                self.assertEqual(result, {})
                self.assertEqual(len(triggered_warnings), 1)
                self.assertTrue(issubclass(triggered_warnings[0].category, UserWarning))
                self.assertIn("Config file does not exist", str(triggered_warnings[0].message))

    def test_load_cfg_file_success(self) -> None:
        """Test that load_cfg_file successfully parses and flattens a valid CFG structure."""
        mock_cfg_content: str = """
        [DATABASE]
        host = localhost
        port = 5432

        [APP]
        debug = true
        """

        with patch("os.path.isfile", return_value=True):
            with patch("builtins.open", mock_open(read_data=mock_cfg_content)):
                result = load_cfg_file(Path("./dummy.cfg"))

                expected_dict = {
                    "host": "localhost",
                    "port": "5432",
                    "debug": "true"
                }
                self.assertEqual(result, expected_dict)

    def test_cfg_source_disabled(self) -> None:
        """Test that cfg_source returns an empty dict if config file usage is disabled."""

        class DisabledSettings(CustomSettings):
            __use_conf_file__ = False

        self.assertEqual(DisabledSettings.cfg_source(), {})

    @patch("observe_core.custom_settings.load_cfg_file")
    def test_cfg_source_enabled(self, mock_load: MagicMock) -> None:
        """Test that cfg_source invokes load_cfg_file with the correct path when enabled."""
        mock_load.return_value = {"key": "value"}

        class EnabledSettings(CustomSettings):
            __use_conf_file__ = True
            __conf_file__ = Path("/path/to/config.cfg")

        result = EnabledSettings.cfg_source()
        mock_load.assert_called_once_with(Path("/path/to/config.cfg"))
        self.assertEqual(result, {"key": "value"})

    def test_conf_file_getter_and_setter(self) -> None:
        """Test the dynamic getter, setter property behavior for the configuration path."""
        settings = CustomSettings()

        # Test setting a valid path string
        settings.conf_file = "/new/path.cfg"
        self.assertEqual(settings.conf_file, Path("/new/path.cfg"))

        # Test setting None disables config file loading
        settings.conf_file = None
        self.assertIsNone(settings.conf_file)

    @patch("observe_core.custom_settings.load_cfg_file")
    def test_reload_cfg(self, mock_load: MagicMock) -> None:
        """Test that reload_cfg correctly updates existing fields in the instantiated settings model."""
        mock_load.return_value = {"api_key": "new_secret_key", "invalid_field": "ignore_me"}

        class TestSettings(CustomSettings):
            api_key: str = "default"

        settings = TestSettings()
        settings.reload_cfg()

        # 'api_key' should be updated, 'invalid_field' should be safely ignored
        self.assertEqual(settings.api_key, "new_secret_key")
        self.assertFalse(hasattr(settings, "invalid_field"))


if __name__ == "__main__":
    unittest.main()
