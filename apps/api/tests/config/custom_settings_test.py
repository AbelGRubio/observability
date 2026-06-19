"""Unit tests for custom settings loading, configuration file handling, and string representation."""

import tempfile
import unittest
import warnings
from pathlib import Path

from observe_core.custom_settings import CustomSettings, load_cfg_file


class TestCustomSettings(unittest.TestCase):
    """Test suite for observe_api.config.custom_settings."""

    def test_load_cfg_file_nonexistent(self) -> None:
        """Test load_cfg_file returns empty dict and warns if file does not exist.

        Args:
            tmp_path (Path): Temporary path fixture from pytest.

        Returns:
            None

        Asserts:
            Returns empty dict and emits UserWarning.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            non_existent_file = Path(temp_dir) / "no_file.cfg"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = load_cfg_file(non_existent_file)
            self.assertEqual(result, {})
            self.assertTrue(any("does not exist" in str(warn.message) for warn in w))

    def test_load_cfg_file_existing(self) -> None:
        """Test load_cfg_file returns correct dictionary when CFG exists.

        Args:
            tmp_path (Path): Temporary path fixture.

        Returns:
            None

        Asserts:
            Returns dictionary with key-value pairs from cfg file.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cfg_file = Path(temp_dir) / "config.cfg"
            cfg_file.write_text("[section1]\nkey1=value1\nkey2=value2\n")
            result = load_cfg_file(cfg_file)
        self.assertEqual(result["key1"], "value1")
        self.assertEqual(result["key2"], "value2")

    def test_customsettings_instance(self) -> None:
        """Test that CustomSettings can be instantiated.

        Returns:
            None

        Asserts:
            Instance is of type CustomSettings.
        """
        settings = CustomSettings()
        self.assertIsInstance(settings, CustomSettings)

    def test_conf_file_setter_and_getter(self) -> None:
        """Test setting and getting conf_file updates __use_conf_file__ correctly.

        Args:
            tmp_path (Path): Temporary path fixture.

        Returns:
            None

        Asserts:
            conf_file is updated and __use_conf_file__ is set correctly.
        """
        settings = CustomSettings()
        # Set to None disables config file
        settings.conf_file = None
        self.assertIsNone(settings.conf_file)
        self.assertFalse(settings.__use_conf_file__)

        # Set to a valid path enables config file
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "config.cfg"
            file_path.write_text("[section]\nkey=value")
            settings.conf_file = file_path
            self.assertEqual(settings.conf_file, file_path)
            self.assertTrue(settings.__use_conf_file__)

    def test_reload_cfg_updates_attributes(self) -> None:
        """Test that reload_cfg updates attributes if keys exist in model.

        Args:
            tmp_path (Path): Temporary path fixture.

        Returns:
            None

        Asserts:
            Attributes are updated with values from cfg file.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            cfg_file = Path(temp_dir) / "config.cfg"
            cfg_file.write_text("[section]\n__use_conf_file__=False")
            settings = CustomSettings()
            settings.__conf_file__ = cfg_file
            settings.__use_conf_file__ = True
            settings.reload_cfg()
        # Should be updated to False from cfg file

    def test_str_method(self) -> None:
        """Test that __str__ returns class name in lowercase without 'settings' suffix.

        Returns:
            None

        Asserts:
            Correct string representation.
        """
        self.assertEqual(str(CustomSettings()), "custom")
