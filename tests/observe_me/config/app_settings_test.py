"""tests/test_app_settings.py"""
from observe_me.config.app_settings import AppSettings


class TestAppSettings:
    """Test suite for observe_me.config.app_settings.AppSettings."""

    def test_appsettings_instance(self) -> None:
        """Test that AppSettings can be instantiated.

        Returns:
            None

        Asserts:
            The returned object is an instance of AppSettings.
        """
        settings = AppSettings()
        assert isinstance(settings, AppSettings)

    def test_default_values(self) -> None:
        """Test that default values are correctly set.

        Returns:
            None

        Asserts:
            api_ip, api_port, minutes_refresh_conf, cors_origins_ have expected defaults.
        """
        settings = AppSettings()
        assert settings.api_ip == "localhost"
        assert settings.api_port == 5000
        assert settings.minutes_refresh_conf == 1
        assert settings.cors_origins_ == "*"

    def test_cors_origins_property_empty(self) -> None:
        """Test that cors_origins property returns an empty list when cors_origins_ is empty.

        Returns:
            None

        Asserts:
            cors_origins is an empty list.
        """
        settings = AppSettings(cors_origins_="")
        assert settings.cors_origins == ['']

    def test_cors_origins_property_multiple(self) -> None:
        """Test that cors_origins property splits comma-separated string into list.

        Returns:
            None

        Asserts:
            cors_origins returns list of strings.
        """
        test_value = "http://localhost,http://example.com"
        settings = AppSettings(cors_origins_=test_value)
        assert settings.cors_origins == ["http://localhost", "http://example.com"]
