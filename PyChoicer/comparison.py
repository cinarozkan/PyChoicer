"""
comparison.py - Interactive pairwise comparison engine.

Responsible for asking the user "which do you prefer?" questions and
returning the winner. All I/O for individual comparisons is isolated here.
"""

from .utils import Color, colorize, bold, error, separator


class ComparisonAborted(Exception):
    """Raised when the user chooses to abort mid-comparison session."""


def ask_pair(item_a: str, item_b: str, question_num: int, total: int | None = None) -> str:
    """
    Ask the user to choose between two items.

    Displays a formatted prompt and loops until a valid answer (1 or 2)
    is given. Raises ComparisonAborted if the user types 'q' or 'quit'.

    Args:
        item_a: First item label.
        item_b: Second item label.
        question_num: Current question index (1-based, for display).
        total: Optional total question count for progress display.

    Returns:
        The string value of the winning item (item_a or item_b).
    """
    progress = f"[{question_num}/{total}]" if total else f"[#{question_num}]"

    print()
    print(separator())
    print(f"  {colorize(progress, Color.GRAY)}  {bold('Which do you prefer?')}")
    print()
    print(f"    {colorize('[1]', Color.CYAN + Color.BOLD)}  {colorize(item_a, Color.WHITE + Color.BOLD)}")
    print(f"    {colorize('[2]', Color.MAGENTA + Color.BOLD)}  {colorize(item_b, Color.WHITE + Color.BOLD)}")
    print()

    while True:
        try:
            raw = input(colorize("  > ", Color.YELLOW)).strip().lower()
        except (EOFError, KeyboardInterrupt):
            raise ComparisonAborted("Session interrupted by user.")

        if raw in ("q", "quit", "exit"):
            raise ComparisonAborted("User quit during comparison.")
        if raw == "1":
            return item_a
        if raw == "2":
            return item_b

        print(error("  ✗  Please enter 1 or 2  (or 'q' to quit)."))
