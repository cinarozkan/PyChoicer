"""
cli.py - Command-line interface loop and command dispatcher for ChoiceRanker.

Manages the interactive REPL session:
  - Parses user commands
  - Maintains item list state
  - Dispatches to ranking algorithms
  - Displays results
"""

import sys
from .utils import (
    Color, colorize, bold, info, success, warning, error, dim,
    separator, print_banner, print_help, parse_items_input,
)
from .ranking import merge_sort_rank, tournament_best
from .comparison import ComparisonAborted


# ---------------------------------------------------------------------------
# Result display helpers
# ---------------------------------------------------------------------------

def _display_full_ranking(ranked: list[str], questions: int) -> None:
    """Print a numbered ranking list with question count summary."""
    print()
    print(separator("═"))
    print(f"  {bold(colorize('Full Ranking Result', Color.YELLOW))}")
    print(separator("═"))
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    for i, item in enumerate(ranked, start=1):
        medal = medals.get(i, "  ")
        rank_str = colorize(f"{i:>2}.", Color.GRAY)
        item_str = colorize(item, Color.WHITE + Color.BOLD if i == 1 else Color.WHITE)
        print(f"  {rank_str} {medal}  {item_str}")
    print()
    print(f"  {dim('Questions asked:')} {colorize(str(questions), Color.CYAN + Color.BOLD)}")
    print(separator("═"))
    print()


def _display_best(best: str, questions: int) -> None:
    """Print the tournament winner with question count summary."""
    print()
    print(separator("═"))
    print(f"  {bold(colorize('Tournament Winner', Color.YELLOW))}")
    print(separator("═"))
    print(f"  🏆  {colorize(best, Color.GREEN + Color.BOLD)}")
    print()
    print(f"  {dim('Questions asked:')} {colorize(str(questions), Color.CYAN + Color.BOLD)}")
    print(separator("═"))
    print()


def _display_items(items: list[str]) -> None:
    """Print the current item list."""
    if not items:
        print(warning("  No items added yet. Use 'add' to add items."))
        return
    print()
    print(bold("  Current items:"))
    print(separator())
    for i, item in enumerate(items, start=1):
        print(f"  {colorize(str(i) + '.', Color.GRAY)}  {item}")
    print(separator())
    print()


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def _cmd_add(items: list[str], args: str) -> list[str]:
    """
    Handle the 'add' command.

    If args are provided on the same line (e.g. 'add Berlin, London'),
    use them directly. Otherwise prompt interactively.

    Returns the updated items list.
    """
    if args:
        raw = args
    else:
        print(info("  Enter items separated by commas:"))
        print(colorize("  > ", Color.YELLOW), end="", flush=True)
        try:
            raw = input().strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return items

    if not raw:
        print(error("  No input provided."))
        return items

    new_items = parse_items_input(raw)
    if not new_items:
        print(error("  No valid items found."))
        return items

    # Merge with existing, skip duplicates
    existing_lower = {x.lower() for x in items}
    added = 0
    for item in new_items:
        if item.lower() not in existing_lower:
            items.append(item)
            existing_lower.add(item.lower())
            added += 1

    skipped = len(new_items) - added
    msg = success(f"  ✓  {added} item(s) added.")
    if skipped:
        msg += warning(f"  ({skipped} duplicate(s) skipped)")
    print(msg)
    return items


def _cmd_reset(items: list[str]) -> list[str]:
    """Clear all items after confirmation."""
    if not items:
        print(warning("  Item list is already empty."))
        return items
    print(warning("  Reset all items? [y/N] "), end="", flush=True)
    try:
        ans = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return items
    if ans == "y":
        print(success("  ✓  All items cleared."))
        return []
    print(dim("  Reset cancelled."))
    return items


def _cmd_compare(items: list[str], args: str) -> None:
    """
    Handle the 'compare' command.

    Flags:
        -r / --rank   Full merge-sort ranking.
        -b / --best   Tournament knockout to find best item.
    """
    if len(items) < 2:
        print(error("  ✗  Need at least 2 items. Use 'add' to add items."))
        return

    flag = args.strip().lower()

    if flag in ("-r", "--rank"):
        mode = "rank"
    elif flag in ("-b", "--best"):
        mode = "best"
    else:
        # Interactive mode selection if no valid flag given
        print()
        print(bold("  Choose comparison mode:"))
        print(f"    {colorize('[1]', Color.CYAN)}  Full ranking  (merge-sort, ~n·log n questions)")
        print(f"    {colorize('[2]', Color.MAGENTA)}  Find best     (tournament, n-1 questions)")
        print()
        while True:
            print(colorize("  > ", Color.YELLOW), end="", flush=True)
            try:
                choice = input().strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return
            if choice == "1":
                mode = "rank"
                break
            if choice == "2":
                mode = "best"
                break
            print(error("  Please enter 1 or 2."))

    print()
    if mode == "rank":
        print(info(f"  Starting full ranking of {len(items)} items…"))
        print(dim("  (Type 'q' at any prompt to abort.)"))
        try:
            ranked, count = merge_sort_rank(items)
            _display_full_ranking(ranked, count)
        except ComparisonAborted:
            print(warning("\n  ⚠  Ranking aborted."))

    else:  # best
        print(info(f"  Finding best item among {len(items)} items…"))
        print(dim("  (Type 'q' at any prompt to abort.)"))
        try:
            best, count = tournament_best(items)
            _display_best(best, count)
        except ComparisonAborted:
            print(warning("\n  ⚠  Tournament aborted."))


# ---------------------------------------------------------------------------
# Main REPL loop
# ---------------------------------------------------------------------------

PROMPT = colorize("choiceranker", Color.CYAN) + colorize(" > ", Color.GRAY)


def run() -> None:
    """
    Start the interactive ChoiceRanker REPL session.

    Maintains item list in local state and dispatches commands until
    the user exits.
    """
    print_banner()
    print_help()

    items: list[str] = []

    while True:
        try:
            raw = input(PROMPT).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print(dim("  Goodbye! 👋"))
            sys.exit(0)

        if not raw:
            continue

        # Split command from inline arguments
        parts = raw.split(None, 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # ── Dispatch ──────────────────────────────────────────────────────
        if cmd in ("exit", "quit", "q"):
            print(dim("  Goodbye! 👋"))
            sys.exit(0)

        elif cmd in ("help", "h"):
            print_help()

        elif cmd in ("add", "a"):
            items = _cmd_add(items, args)

        elif cmd in ("list", "l"):
            _display_items(items)

        elif cmd in ("reset", "r"):
            items = _cmd_reset(items)

        elif cmd == "compare":
            _cmd_compare(items, args)

        elif cmd == "c":
            # Short alias 'c' always prompts for mode interactively
            _cmd_compare(items, "")

        else:
            print(error(f"  ✗  Unknown command: '{cmd}'  —  type 'help' for options."))
