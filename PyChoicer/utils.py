"""
utils.py - Utility functions for PyChoicer CLI.

Provides colored output, formatting helpers, and shared constants.
"""

import random
from typing import Any


# ANSI color codes for terminal output
class Color:
    """ANSI escape codes for terminal colors."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    # Foreground colors
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"


def colorize(text: str, *codes: str) -> str:
    """
    Wrap text with ANSI color/style codes.

    Args:
        text: The string to colorize.
        *codes: One or more Color constants to apply.

    Returns:
        The text wrapped with ANSI codes and a reset at the end.
    """
    prefix = "".join(codes)
    return f"{prefix}{text}{Color.RESET}"


def bold(text: str) -> str:
    """Return bold text."""
    return colorize(text, Color.BOLD)


def info(text: str) -> str:
    """Return cyan-colored informational text."""
    return colorize(text, Color.CYAN)


def success(text: str) -> str:
    """Return green-colored success text."""
    return colorize(text, Color.GREEN)


def warning(text: str) -> str:
    """Return yellow-colored warning text."""
    return colorize(text, Color.YELLOW)


def error(text: str) -> str:
    """Return red-colored error text."""
    return colorize(text, Color.RED)


def dim(text: str) -> str:
    """Return dimmed/gray text."""
    return colorize(text, Color.DIM)


def separator(char: str = "─", width: int = 40) -> str:
    """Return a horizontal separator line."""
    return colorize(char * width, Color.GRAY)


def print_banner() -> None:
    """Print the PyChoicer welcome banner."""
    print()
    print(colorize("  ╔══════════════════════════════════════╗", Color.CYAN))
    print(colorize("  ║  ", Color.CYAN) + colorize("PyChoicer", Color.BOLD + Color.YELLOW) +
          colorize(" v1.2                    ║", Color.CYAN))
    print(colorize("  ║  ", Color.CYAN) + colorize("Rank items via pairwise comparison  ", Color.WHITE) +
          colorize("║", Color.CYAN))
    print(colorize("  ╚══════════════════════════════════════╝", Color.CYAN))
    print()


def print_help() -> None:
    """Print the help / command reference screen."""
    print()
    print(bold("  Available Commands:"))
    print(separator())

    sections = [
        ("ITEMS", [
            ("add / a  <items>",     "Add items  (comma-separated)"),
            ("remove / rm  <item>",  "Remove an item by name or number"),
            ("list / l",             "List current items"),
            ("reset",                "Clear all items"),
        ]),
        ("PRESETS", [
            ("preset list",          "Show all saved presets"),
            ("preset load <name>",   "Load a preset into current items"),
            ("preset save <name>",   "Save current items as a preset"),
            ("preset delete <name>", "Delete a saved preset"),
            ("seeds",                "Install built-in example presets"),
            ("seeds --force",        "Install and overwrite existing ones"),
        ]),
        ("COMPARE", [
            ("compare -r / --rank",  "Full ranking   (merge-sort, ~n·log n)"),
            ("compare -b / --best",  "Find best item (tournament, n-1)"),
        ]),
        ("OTHER", [
            ("help / h",             "Show this help screen"),
            ("exit / q",             "Quit the program"),
        ]),
    ]

    for section_title, commands in sections:
        print(f"\n  {colorize(section_title, Color.GRAY + Color.BOLD)}")
        for cmd, desc in commands:
            print(f"  {colorize(cmd, Color.YELLOW):<36} {colorize(desc, Color.WHITE)}")

    print()
    print(separator())
    print()


def parse_items_input(raw: str) -> list[str]:
    """
    Parse a comma-separated string of items.

    - Trims surrounding whitespace from each item.
    - Removes empty strings.
    - Removes duplicates (case-insensitive), preserving first occurrence.

    Args:
        raw: Raw user input string.

    Returns:
        Cleaned, deduplicated list of item strings.
    """
    parts = [p.strip() for p in raw.split(",")]
    seen: set[str] = set()
    result: list[str] = []
    for part in parts:
        if not part:
            continue
        key = part.lower()
        if key not in seen:
            seen.add(key)
            result.append(part)
    return result


def shuffled_copy(items: list[Any]) -> list[Any]:
    """Return a shuffled copy of a list without modifying the original."""
    copy = list(items)
    random.shuffle(copy)
    return copy
