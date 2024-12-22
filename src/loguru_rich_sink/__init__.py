from rich.console import Console
from rich.traceback import install as tr_install

from loguru_rich_sink.__main__ import (
    get_console,
    get_logger,
    get_progress,
    logger,
    on_exit,
)
from loguru_rich_sink.sink import RichSink, increment, read, rich_sink, setup, write

console = Console()
tr_install(console=console)

__all__ = [
    "RichSink",
    "get_console",
    "get_logger",
    "get_progress",
    "rich_sink",
    "setup",
    "read",
    "write",
    "increment",
    "on_exit",
    "logger",
]

setup()
