"""Aqui se define como va a ser el logger."""

import functools
import logging
import os
import time
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any, ClassVar

from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from rich.console import Console
from rich.default_styles import DEFAULT_STYLES
from rich.logging import RichHandler
from rich.table import Table
from rich.theme import Theme

detail_level = logging.DEBUG + 5

logging.addLevelName(detail_level, "DETAIL")


class LoggerApi(logging.Logger):
    """Custom logger."""

    _timers: ClassVar[dict[str, float]] = {}
    _timers_it: ClassVar[dict[str, float]] = {}

    def __init__(self, name: str | None = None) -> None:
        """Start logger api."""
        if not name:
            name = "api"

        super().__init__(name)

        self._titles_level = {
            DEBUG: f"DEBUG {name.upper()}",
            INFO: f"INFO {name.upper()}",
            WARNING: f"WARNING {name.upper()}",
            ERROR: f"ERROR {name.upper()}",
            detail_level: f"DETAIL {name.upper()}",
            CRITICAL: f"CRITICAL {name.upper()}",
        }

        self.console = None
        self.start_logger()

    def add_opentelemetry(self):
        logger_provider = LoggerProvider()

        exporter = OTLPLogExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),  # o tu endpoint
            insecure=True
        )

        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(exporter)
        )

        handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
        self.addHandler(handler)

    def start_logger(self) -> None:
        """Define logger."""
        custom_theme = Theme({
            **DEFAULT_STYLES,
            "logging.level.detail": "magenta",
            "logging.level.debug": "cyan",
            "logging.level.info": "green",
            "logging.level.warning": "yellow",
            "logging.level.error": "bold red",
            "logging.level.critical": "bold white on red",
        })

        self.console = Console(
            theme=custom_theme,
            soft_wrap=True,
            stderr=False,
            force_terminal=True,
            color_system="truecolor",
            width=200,
        )

        # Console con Rich
        console_handler = RichHandler(
            console=self.console,
            omit_repeated_times=True,
            rich_tracebacks=True,
            show_time=True,
            show_level=True,
            show_path=False,
            markup=True,
        )

        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(
            logging.Formatter("%(name)s\t%(threadName)s\t%(message)s", datefmt="%Y-%m-%d %H:%M:%S")
        )
        self.addHandler(console_handler)

        # Archivo rotativo
        Path(".logs").mkdir(exist_ok=True)
        file_handler = TimedRotatingFileHandler(".logs/app.log", when="midnight", interval=1, backupCount=7)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s\t%(levelname)s\t%(name)s\t%(threadName)s\t%(message)s",
                "%Y-%m-%d %H:%M:%S",
            )
        )
        self.addHandler(file_handler)

        self.add_opentelemetry()

    def _get_title(self, level: int) -> str:
        """Obtiene el título para webhook."""
        return self._titles_level.get(level, self.name.upper())

    def detail(self, msg: str, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        """Méto do personalizado para el nivel DETAIL."""
        if self.isEnabledFor(detail_level):
            super().log(detail_level, msg, *args, **kwargs)

    def start_time(self, name: str | None = None, level: int | None = DEBUG) -> None:
        """Start a timer only if a name is provided."""
        if not name:
            name = "no-timer-name"

        if not hasattr(self, "_timers"):
            self._timers = {}

        self._timers[name] = time.perf_counter()

        if level:
            self.log(level, f"[cyan]⏱️ Timer started: {name}")

    def time_it(self, name: str | None = None, msg: str | None = None, level: int | None = DEBUG) -> float:
        """Stop timer.

        If name is provided, uses stored start time.
        If not, measures elapsed from a fresh start (no storage).
        """
        now = time.perf_counter()

        if not name:
            name = "no-timer-name"

        if name and hasattr(self, "_timers") and name in self._timers:
            start = self._timers.pop(name)
            elapsed = now - start
        else:
            # fallback: no stored timer
            elapsed = 0.0

        self._timers_it[name] = elapsed

        final_msg = msg or (f"[cyan]⏱️ {name}: {elapsed:.4f}s" if name else "⏱️ Timer finished")

        if level:
            self.log(level, final_msg)

        return elapsed

    def dec_time_it(self, name: str | None = None, level: int = DEBUG) -> Any:
        """Decorator to measure execution time."""

        def decorator(func: Any) -> Any:
            """Decorator."""

            @functools.wraps(func)
            def wrapper(*args: tuple, **kwargs: dict) -> Any:
                """Add wrapper."""
                timer_name = name or func.__name__

                self.start_time(timer_name)

                try:
                    return func(*args, **kwargs)
                finally:
                    self.time_it(timer_name, level=level)

            return wrapper

        return decorator

    def print_timers(self) -> None:
        """Print all recorded timers in a table."""
        if not hasattr(self, "_timers_it") or not self._timers_it:
            self.info("No timers recorded")
            return

        table = Table(title="⏱️ Timers")

        table.add_column("Name", justify="left")
        table.add_column("Time (s)", justify="right")

        total = 0.0

        for name, elapsed in self._timers_it.items():
            table.add_row(name, f"{elapsed:.6f}")
            total += elapsed

        table.add_row("[bold]TOTAL[/bold]", f"[bold]{total:.6f}[/bold]")

        self.console.print(table)
        self.info("Timers: " + ", ".join(f"{k}={v:.4f}s" for k, v in self._timers_it.items()))


def get_logger(name: str) -> LoggerApi:
    """Obtain the logger."""
    return LoggerApi(name)
