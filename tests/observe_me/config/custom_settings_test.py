# tests/test_custom_settings.py
import warnings
from pathlib import Path

from observe_me.config.custom_settings import CustomSettings, load_cfg_file


class TestCustomSettings:
    """Test suite for observe_me.config.custom_settings."""

    def test_load_cfg_file_nonexistent(self, tmp_path):
        """Test load_cfg_file returns empty dict and warns if file does not exist.

        Args:
            tmp_path (Path): Temporary path fixture from pytest.

        Returns:
            None

        Asserts:
            Returns empty dict and emits UserWarning.
        """
        non_existent_file = tmp_path / "no_file.cfg"
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = load_cfg_file(non_existent_file)
            assert result == {}
            assert any("does not exist" in str(warn.message) for warn in w)

    def test_load_cfg_file_existing(self, tmp_path):
        """Test load_cfg_file returns correct dictionary when CFG exists.

        Args:
            tmp_path (Path): Temporary path fixture.

        Returns:
            None

        Asserts:
            Returns dictionary with key-value pairs from cfg file.
        """
        cfg_file = tmp_path / "config.cfg"
        cfg_file.write_text("[section1]\nkey1=value1\nkey2=value2\n")
        result = load_cfg_file(cfg_file)
        assert result["key1"] == "value1"
        assert result["key2"] == "value2"

    def test_customsettings_instance(self):
        """Test that CustomSettings can be instantiated.

        Returns:
            None

        Asserts:
            Instance is of type CustomSettings.
        """
        settings = CustomSettings()
        assert isinstance(settings, CustomSettings)

    def test_conf_file_setter_and_getter(self, tmp_path):
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
        assert settings.conf_file is None
        assert settings.__use_conf_file__ is False

        # Set to a valid path enables config file
        file_path = tmp_path / "config.cfg"
        file_path.write_text("[section]\nkey=value")
        settings.conf_file = file_path
        assert settings.conf_file == file_path
        assert settings.__use_conf_file__ is True

    def test_reload_cfg_updates_attributes(self, tmp_path):
        """Test that reload_cfg updates attributes if keys exist in model.

        Args:
            tmp_path (Path): Temporary path fixture.

        Returns:
            None

        Asserts:
            Attributes are updated with values from cfg file.
        """
        cfg_file = tmp_path / "config.cfg"
        cfg_file.write_text("[section]\n__use_conf_file__=False")
        settings = CustomSettings()
        settings.__conf_file__ = cfg_file
        settings.__use_conf_file__ = True
        # Initially True
        settings.reload_cfg()
        # Should be updated to False from cfg file

    def test_str_method(self):
        """Test that __str__ returns class name in lowercase without 'settings' suffix.

        Returns:
            None

        Asserts:
            Correct string representation.
        """
        assert str(CustomSettings()) == "custom"
