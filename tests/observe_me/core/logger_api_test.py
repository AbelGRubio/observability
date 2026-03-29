# tests/test_logger_api.py
import time

from observe_me.core.logger_api import LoggerApi


class TestLoggerApi:
    """Test suite for observe_me.core.logger_api.LoggerApi."""

    def test_logger_instance(self):
        """Test that LoggerApi can be instantiated.

        Returns:
            None

        Asserts:
            Instance is of type LoggerApi.
        """
        logger = LoggerApi("test_logger")
        assert isinstance(logger, LoggerApi)
        assert logger.name == "test_logger"

    # def test_detail_method_logs(self, caplog):
    #     """Test that detail() logs a message at custom DETAIL level.
    #
    #     Args:
    #         caplog: Pytest fixture to capture logs.
    #
    #     Returns:
    #         None
    #
    #     Asserts:
    #         Message appears in logs at correct level.
    #     """
    #     logger = LoggerApi("detail_test")
    #     with caplog.at_level(detail_level):
    #         logger.detail("test detail message")
    #     assert any("test detail message" in rec.message for rec in caplog.records)
    #     assert all(rec.levelno == detail_level or rec.levelno != detail_level for rec in caplog.records)

    def test_start_time_and_time_it(self):
        """Test that start_time and time_it correctly measure elapsed time.

        Returns:
            None

        Asserts:
            Elapsed time is greater than zero for a small sleep.
        """
        logger = LoggerApi("timer_test")
        logger.start_time("my_timer")
        time.sleep(0.01)
        elapsed = logger.time_it("my_timer")
        assert isinstance(elapsed, float)
        assert elapsed > 0

    def test_time_it_without_start(self):
        """Test that time_it returns 0 if timer name not started.

        Returns:
            None

        Asserts:
            Returns float 0.0
        """
        logger = LoggerApi("timer_test")
        elapsed = logger.time_it("unknown_timer")
        assert elapsed == 0.0

    def test_dec_time_it_decorator(self):
        """Test dec_time_it decorator measures execution time.

        Returns:
            None

        Asserts:
            Decorated function returns correct value and timer is recorded.
        """
        logger = LoggerApi("decorator_test")

        @logger.dec_time_it("decorator_timer")
        def dummy_function(x, y):
            time.sleep(0.01)
            return x + y

        result = dummy_function(1, 2)
        assert result == 3
        # Timer should now exist in _timers_it
        assert "decorator_timer" in logger._timers_it

    def test_print_timers(self, capsys):
        """Test that print_timers prints a table of timers.

        Args:
            capsys: Pytest fixture to capture stdout.

        Returns:
            None

        Asserts:
            Printed output contains timer name and elapsed time.
        """
        logger = LoggerApi("print_timer_test")
        logger._timers_it = {"timer1": 0.123, "timer2": 0.456}
        logger.print_timers()
        captured = capsys.readouterr().out
        assert "timer1" in captured
        assert "timer2" in captured
        assert "TOTAL" in captured

    def test_get_logger_function(self):
        """Test get_logger returns LoggerApi instance.

        Returns:
            None

        Asserts:
            Returned object is LoggerApi.
        """
        logger = LoggerApi("my_logger")
        from observe_me.core.logger_api import get_logger
        l = get_logger("another_logger")
        assert isinstance(l, LoggerApi)
        assert l.name == "another_logger"
