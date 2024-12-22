"""The Rich Sink for the loguru logger."""

from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.panel import Panel

from rich.style import Style
from rich.text import Text
from rich.traceback import install as tr_install
from rich_gradient import Color, Gradient

def get_console(
        record: bool = False,
        console: Optional[Console] = None) -> Console:
    """Initialize the console and return it.

    Args:
        console (Console, optional): A Rich console. Defaults to Console().

    Returns:
        Console: A Rich console.
    """
    if console is None:
        if record:
            console = Console(record=True)
        else:
            console = Console()
    else:
        console.record=True if record else False
    tr_install(console=console)
    return console


FORMAT: str = (
    "{time:HH:mm:ss.SSS} | Run {extra[run]} | {file.name: ^12} | Line {line} | {level} | {message}"
)
CWD: Path = Path.cwd()
LOGS_DIR: Path = CWD / "logs"
RUN_FILE: Path = LOGS_DIR / "run.txt"


def find_cwd(
    start_dir: Path = Path.cwd(),
    verbose: bool = False) -> Path:
    """Find the current working directory.

    Args:
        start_dir (Path, optional): The starting directory. Defaults to Path.cwd().
        verbose (bool, optional): Print the output of the where command. Defaults to False.

    Returns:
        Path: The current working directory.
    """
    cwd: Path = start_dir
    while not (cwd / "pyproject.toml").exists():
        cwd = cwd.parent
        if cwd == Path.home():
            break
    if verbose:
        console = get_console()
        console.line(2)
        console.print(
            Panel(
                f"[i #5f00ff]{cwd.resolve()}",
                title=Gradient(
                    "Current Working Directory",
                    colors=[
                        Color("#ff005f"),
                        Color("#ff00af"),
                        Color("#ff00ff"),
                    ],
                    style="bold"
                ).as_text()
            )
        )
        console.line(2)
    return cwd


def setup() -> int:
    """Setup the logger and return the run count."""
    console = get_console()
    if not LOGS_DIR.exists():
        LOGS_DIR.mkdir(parents=True)
        console.print(f"Created Logs Directory: {LOGS_DIR}")
    if not RUN_FILE.exists():
        with open(RUN_FILE, "w", encoding="utf-8") as f:
            f.write("0")
            console.print("Created Run File, Set to 0")

    with open(RUN_FILE, "r", encoding="utf-8") as f:
        run = int(f.read())
        return run


def read() -> int:
    """Read the run count from the file."""
    if not RUN_FILE.exists():
        console.print("[b #ff0000]Run File Not Found[/][i #ff9900], Creating...[/]")
        setup()
    with open(RUN_FILE, "r", encoding="utf-8") as f:
        run = int(f.read())
    return run


def write(run: int) -> None:
    """Write the run count to the file."""
    with open(RUN_FILE, "w", encoding="utf-8") as f:
        f.write(str(run))


def increment() -> int:
    """Increment the run count and write it to the file."""
    run = read()
    run += 1
    write(run)
    return run


LEVEL_STYLES: Dict[str, Style] = {
    "TRACE": Style(italic=True),
    "DEBUG": Style(color="#aaaaaa"),
    "INFO": Style(color="#00afff"),
    "SUCCESS": Style(bold=True, color="#00ff00"),
    "WARNING": Style(italic=True, color="#ffaf00"),
    "ERROR": Style(bold=True, color="#ff5000"),
    "CRITICAL": Style(bold=True, color="#ff0000"),
}

GRADIENTS: Dict[str, List[Color]] = {
    "TRACE": [Color("#888888"), Color("#aaaaaa"), Color("#cccccc")],
    "DEBUG": [Color("#338888"), Color("#55aaaa"), Color("#77cccc")],
    "INFO": [Color("#008fff"), Color("#00afff"), Color("#00cfff")],
    "SUCCESS": [Color("#00aa00"), Color("#00ff00"), Color("#afff00")],
    "WARNING": [Color("#ffaa00"), Color("#ffcc00"), Color("#ffff00")],
    "ERROR": [Color("#ff0000"), Color("#ff5500"), Color("#ff7700")],
    "CRITICAL": [Color("#ff0000"), Color("#ff005f"), Color("#ff00af")],
}

class RichSink:
    """A loguru sink that uses the great `rich` library to print log messages.

    Args:
        run (Optional[int], optional): The current run number. If None, it will \
be read from a file. Defaults to None.
        console (Optional[Console]): A Rich console. If None, it will be \
initialized. Defaults to None.


    """
    def __init__(self, run: Optional[int] = None, console: Optional[Console] = None) -> None:
        if run is None:
            try:
                run = read()
            except FileNotFoundError:
                run = setup()
        self.run = run
        self.console = console or get_console()

    def __call__(self, message) -> None:
        record = message.record
        level = record["level"].name
        colors = GRADIENTS[level]
        style = LEVEL_STYLES[level]

        # title
        title: Text = Gradient(
            f" {level} | {record['file'].name} | Line {record['line']} ", colors=colors
        ).as_text()
        title.highlight_words("|", style="italic #666666")
        title.stylize(Style(reverse=True))

        # subtitle
        subtitle: Text = Text.assemble(
            Text(f"Run {self.run}"),
            Text(" | "),
            Text(record["time"].strftime("%H:%M:%S.%f")[:-3]),
            Text(record["time"].strftime(" %p")),
        )
        subtitle.highlight_words(":", style="dim #aaaaaa")

        # Message
        message_text: Text = Gradient(record["message"], colors, style="bold")
        # Generate and print log panel with aligned title and subtitle
        log_panel: Panel = Panel(
            message_text,
            title=title,
            title_align="left",  # Left align the title
            subtitle=subtitle,
            subtitle_align="right",  # Right align the subtitle
            border_style=style + Style(bold=True),
            padding=(1, 2),
        )
        self.console.print(log_panel)

def rich_sink(message) -> None:
    """A loguru sink that uses the great `rich` library to print log messages."""
    record = message.record
    level = record["level"].name
    colors = GRADIENTS[level]
    style = LEVEL_STYLES[level]

    # title
    title: Text = Gradient(
        f" {level} | {record['file'].name} | Line {record['line']} ", colors=colors
    ).as_text()
    title.highlight_words("|", style="italic #999999")
    title.stylize(Style(reverse=True))

    # subtitle
    run: int = read()
    subtitle: Text = Text.assemble(
        Text(f"Run {run}"),
        Text(" | "),
        Text(record["time"].strftime("%H:%M:%S.%f")[:-3]),
        Text(record["time"].strftime(" %p")),
    )
    subtitle.highlight_words(":", style="dim #aaaaaa")

    # Message
    message_text: Text = Gradient(record["message"], colors, style="bold")
    # Generate and print log panel with aligned title and subtitle
    log_panel: Panel = Panel(
        message_text,
        title=title,
        title_align="left",  # Left align the title
        subtitle=subtitle,
        subtitle_align="right",  # Right align the subtitle
        border_style=style + Style(bold=True),
        padding=(1, 2),
    )
    console = get_console(True)
    console.print(log_panel)
    record["extra"]["rich"] = console.export_text()


if __name__ == "__main__":
    console = get_console()
    console.print("CWD:", find_cwd(verbose=True))
