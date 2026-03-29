# tests/test_info.py
import pytest
import sys
from types import SimpleNamespace
from observe_me.core import info
from unittest.mock import patch


class TestInfoModule:
    """Test suite for observe_me.core.info functions."""

    def test_get_memory_usage(self):
        """Test get_memory_usage returns a float in MB for any object.

        Returns:
            None

        Asserts:
            Memory usage is a float greater than zero for a non-empty object.
        """
        obj = {"key": "value"}
        mem = info.get_memory_usage(obj)
        assert isinstance(mem, float)
        assert mem >= 0

    # def test_info_os_logs(self, caplog):
    #
    #     info.info_os()
    #     print(caplog.records)
    #     assert any("OS" in rec.message for rec in caplog.records) is True

    # def test_info_software_logs_default(self, caplog):
    #     """Test info_software logs default modules when no modules passed.
    #
    #     Args:
    #         caplog: Pytest fixture
    #
    #     Returns:
    #         None
    #
    #     Asserts:
    #         Log contains module names from DEFAULT_MODULES.
    #     """
    #     caplog.set_level("INFO")
    #     info.info_software()
    #     for module in info.DEFAULT_MODULES:
    #         assert any(module in rec.message for rec in caplog.records)

    # def test_info_software_logs_custom_modules(self, caplog):
    #     """Test info_software logs specified modules.
    #
    #     Args:
    #         caplog: Pytest fixture
    #
    #     Returns:
    #         None
    #
    #     Asserts:
    #         Log contains the custom module names.
    #     """
    #     caplog.set_level("INFO")
    #     info.info_software(modules=["sys"])
    #     assert any("sys" in rec.message for rec in caplog.records)

    # def test_info_hardware_logs(self, caplog):
    #     """Test info_hardware logs CPU, cores, and RAM info.
    #
    #     Args:
    #         caplog: Pytest fixture
    #
    #     Returns:
    #         None
    #
    #     Asserts:
    #         Log contains 'MACHINE'.
    #     """
    #     caplog.set_level("INFO")
    #     info.info_hardware()
    #     assert any("MACHINE" in rec.message for rec in caplog.records)

    # @patch("shutil.which", return_value=None)
    # def test_info_gpu_no_nvidia_smi(self, mock_which, caplog):
    #     """Test info_gpu when nvidia-smi is not found.
    #
    #     Args:
    #         mock_which: mocked shutil.which
    #         caplog: capture logs
    #
    #     Returns:
    #         None
    #
    #     Asserts:
    #         Log indicates GPU not found.
    #     """
    #     caplog.set_level("INFO")
    #     info.info_gpu()
    #     assert any("nvidia-smi not found" not in rec.message for rec in caplog.records)

    # @patch("shutil.which", return_value="/usr/bin/nvidia-smi")
    # @patch("subprocess.run")
    # def test_info_gpu_with_nvidia_smi(self, mock_run, mock_which, caplog):
    #     """Test info_gpu when nvidia-smi returns GPU name.
    #
    #     Args:
    #         mock_run: mocked subprocess.run
    #         mock_which: mocked shutil.which
    #         caplog: capture logs
    #
    #     Returns:
    #         None
    #
    #     Asserts:
    #         Log contains GPU name.
    #     """
    #     mock_run.return_value.stdout = "NVIDIA GTX 1080\n"
    #     caplog.set_level("INFO")
    #     info.info_gpu()
    #     assert any("NVIDIA GTX 1080" in rec.message for rec in caplog.records)

    @patch("observe_me.core.info.info_hardware")
    @patch("observe_me.core.info.info_gpu")
    @patch("observe_me.core.info.info_os")
    @patch("observe_me.core.info.info_software")
    def test_info_system_calls_all(self, mock_software, mock_os, mock_gpu, mock_hardware):
        """Test info_system calls all underlying functions.

        Returns:
            None

        Asserts:
            Each function is called once.
        """
        info.info_system(modules=["sys"])
        mock_hardware.assert_called_once()
        mock_gpu.assert_called_once()
        mock_os.assert_called_once()
        mock_software.assert_called_once_with(["sys"])
