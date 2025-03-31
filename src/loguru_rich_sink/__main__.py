"""Rich logger setup and usage."""

from __future__ import annotations

import atexit
import sys

from loguru import (
    logger,
)
try:
    from loguru import Logger # type: ignore
except ImportError:
    pass

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.traceback import install as tr_install

from loguru_rich_sink.sink import FORMAT, LOGS_DIR, RichSink, increment, read, setup


def get_console(console: Console = Console()) -> Console:
    """Initialize the console and return it.

    Args:
        console (Console, optional): A Rich console. Defaults to Console().

    Returns:
        Console: A Rich console.
    """
    tr_install(console=console)
    return console


def get_logger(
    console: Console = get_console(), logger: Logger = logger
) -> Logger:  # type: ignore
    """Initialize the logger with two sinks and return it."""
    logger = logger if logger is not None else logger
    run = setup()
    logger.remove()
    logger.configure(
        handlers=[
            {
                "sink": RichSink(),
                "format": "{message}",
                "level": "INFO",
                "backtrace": True,
                "diagnose": True,
                "colorize": False,
            },
            {
                "sink": str(LOGS_DIR / "trace.log"),
                "format": FORMAT,
                "level": "TRACE",
                "backtrace": True,
                "diagnose": True,
                "colorize": False,
            },
        ],
        extra={"run": run},
    )
    return logger


def get_progress(console: Console = get_console()) -> Progress:
    """Initialize the progress bar and return it."""
    if console is None:
        console = Console()
    progress = Progress(
        SpinnerColumn(spinner_name="earth"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        MofNCompleteColumn(),
    )
    progress.start()
    return progress


def on_exit():
    """At exit, read the run number and increment it."""
    try:
        run = read()
        logger.info(f"Run {run} Completed")
        run = increment()
    except FileNotFoundError as fnfe:
        logger.error(fnfe)
        run = setup()
        logger.info(f"Run {run} Completed")
    run = increment()


atexit.register(on_exit)

if __name__ == "__main__":
    logger = get_logger()

    logger.info("Started")
    logger.trace("Trace")
    logger.debug("Debug")
    logger.info("Info")
    logger.success("Success")
    logger.warning("Warning")
    logger.error("Error")
    logger.critical("Critical")

    logger.info("Finished")
    sys.exit(0)
    sys.exit(0)
