"""
cli.py - Command-line interface loop and command dispatcher for PyChoicer.

Manages the interactive REPL session:
  - Parses user commands
  - Maintains item list state
  - Dispatches to ranking algorithms
  - Handles preset load/save/list/delete
"""

import os
import sys
from .utils import (
    Color, colorize, bold, info, success, warning, error, dim,
    separator, print_banner, print_help, parse_items_input,
)
from .ranking import merge_sort_rank, tournament_best
from .comparison import ComparisonAborted
from .presets import (
    save_preset, load_preset, list_presets, delete_preset,
    preset_exists, _sanitize_name,
)
from .seeds import install_seeds, seed_names


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
    print(f"  {dim(str(len(items)) + ' item(s) total.')}")
    print()


# ---------------------------------------------------------------------------
# Command handlers — Items
# ---------------------------------------------------------------------------

def _cmd_add(items: list[str], args: str) -> list[str]:
    """
    Handle the 'add' command.

    Accepts inline args ('add Berlin, London') or prompts interactively.
    Merges with existing items, silently skipping duplicates.

    Returns:
        Updated items list.
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


def _cmd_remove(items: list[str], args: str) -> list[str]:
    """
    Handle the 'remove' command.

    The user can specify either:
      - A number  (1-based index from 'list')
      - The item's name (case-insensitive, partial prefix match if unambiguous)

    If no args are given, the current list is displayed and the user is
    prompted interactively.

    Returns:
        Updated items list.
    """
    if not items:
        print(warning("  No items to remove."))
        return items

    if not args:
        _display_items(items)
        print(info("  Enter item number or name to remove:"))
        print(colorize("  > ", Color.YELLOW), end="", flush=True)
        try:
            args = input().strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return items

    if not args:
        print(error("  No input provided."))
        return items

    # Try numeric index first
    if args.isdigit():
        idx = int(args) - 1
        if 0 <= idx < len(items):
            removed = items.pop(idx)
            print(success(f"  ✓  Removed: {colorize(removed, Color.WHITE + Color.BOLD)}"))
            return items
        else:
            print(error(f"  ✗  No item at position {args}."))
            return items

    # Case-insensitive name match
    target = args.lower()
    matches = [(i, item) for i, item in enumerate(items) if item.lower() == target]

    # Fallback: prefix match
    if not matches:
        matches = [(i, item) for i, item in enumerate(items) if item.lower().startswith(target)]

    if len(matches) == 1:
        idx, removed = matches[0]
        items.pop(idx)
        print(success(f"  ✓  Removed: {colorize(removed, Color.WHITE + Color.BOLD)}"))
        return items
    elif len(matches) == 0:
        print(error(f"  ✗  No item matching '{args}' found."))
    else:
        # Ambiguous — show candidates
        print(warning(f"  Ambiguous match. Did you mean one of these?"))
        for i, item in matches:
            print(f"    {colorize(str(i + 1) + '.', Color.GRAY)}  {item}")
        print(dim("  Use the number to remove specifically."))

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


# ---------------------------------------------------------------------------
# Command handlers — Presets
# ---------------------------------------------------------------------------

def _display_presets() -> None:
    """Print the list of saved presets with item counts."""
    names = list_presets()
    if not names:
        print(warning("  No presets saved yet.  Use 'preset save <name>' to create one."))
        return
    print()
    print(bold("  Saved Presets:"))
    print(separator())
    for i, name in enumerate(names, start=1):
        try:
            items = load_preset(name)
            count_str = colorize(f"({len(items)} items)", Color.GRAY)
        except Exception:
            count_str = colorize("(unreadable)", Color.RED)
        print(f"  {colorize(str(i) + '.', Color.GRAY)}  {colorize(name, Color.CYAN)}  {count_str}")
    print(separator())
    print()


def _pick_preset_interactively(prompt: str) -> str | None:
    """
    Show preset list and let the user pick one by number or name.

    Args:
        prompt: Action description shown to the user (e.g. 'load', 'delete').

    Returns:
        The chosen preset name, or None if aborted.
    """
    names = list_presets()
    if not names:
        print(warning("  No presets available."))
        return None

    print()
    print(bold(f"  Choose a preset to {prompt}:"))
    print(separator())
    for i, name in enumerate(names, start=1):
        try:
            items = load_preset(name)
            count_str = colorize(f"({len(items)} items)", Color.GRAY)
        except Exception:
            count_str = ""
        print(f"  {colorize(str(i) + '.', Color.GRAY)}  {colorize(name, Color.CYAN)}  {count_str}")
    print(separator())
    print(colorize("  > ", Color.YELLOW), end="", flush=True)
    try:
        raw = input().strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None

    if not raw:
        return None

    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(names):
            return names[idx]
        print(error(f"  ✗  No preset at position {raw}."))
        return None

    # Name lookup (exact, then prefix)
    target = raw.lower()
    if target in names:
        return target
    matches = [n for n in names if n.startswith(target)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(warning(f"  Ambiguous preset name. Matches: {', '.join(matches)}"))
    else:
        print(error(f"  ✗  Preset '{raw}' not found."))
    return None


def _cmd_preset(items: list[str], args: str) -> list[str]:
    """
    Handle all 'preset' sub-commands:
        preset list
        preset load [name]
        preset save [name]
        preset delete [name]

    Args:
        items: Current item list.
        args:  Everything after 'preset' on the command line.

    Returns:
        Possibly-updated items list.
    """
    parts = args.split(None, 1)
    sub = parts[0].lower() if parts else ""
    sub_args = parts[1].strip() if len(parts) > 1 else ""

    # ── preset list ────────────────────────────────────────────────────────
    if sub in ("list", "l", ""):
        _display_presets()
        return items

    # ── preset load ────────────────────────────────────────────────────────
    if sub in ("load",):
        name = sub_args or _pick_preset_interactively("load")
        if not name:
            return items
        name = _sanitize_name(name)
        try:
            loaded = load_preset(name)
        except FileNotFoundError:
            print(error(f"  ✗  Preset '{name}' not found."))
            return items
        except ValueError as e:
            print(error(f"  ✗  {e}"))
            return items

        if items:
            print(warning(f"  You have {len(items)} existing item(s).  Replace or merge? [r/m] "), end="", flush=True)
            try:
                choice = input().strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                return items
            if choice == "r":
                items = loaded
                print(success(f"  ✓  Loaded preset '{name}' — {len(items)} items."))
            elif choice == "m":
                # Merge: add only new items
                existing_lower = {x.lower() for x in items}
                added = 0
                for item in loaded:
                    if item.lower() not in existing_lower:
                        items.append(item)
                        existing_lower.add(item.lower())
                        added += 1
                print(success(f"  ✓  Merged preset '{name}' — {added} new item(s) added."))
            else:
                print(dim("  Load cancelled."))
        else:
            items = loaded
            print(success(f"  ✓  Loaded preset '{colorize(name, Color.CYAN + Color.BOLD)}' — {len(items)} items."))

        return items

    # ── preset save ────────────────────────────────────────────────────────
    if sub in ("save",):
        if not items:
            print(error("  ✗  No items to save. Add items first."))
            return items

        if sub_args:
            name = sub_args
        else:
            print(info("  Enter preset name:"))
            print(colorize("  > ", Color.YELLOW), end="", flush=True)
            try:
                name = input().strip()
            except (EOFError, KeyboardInterrupt):
                print()
                return items

        if not name.strip():
            print(error("  ✗  Preset name cannot be empty."))
            return items

        clean = _sanitize_name(name)
        if not clean:
            print(error("  ✗  Preset name contains no valid characters."))
            return items

        # Warn if overwriting
        if preset_exists(clean):
            print(warning(f"  Preset '{clean}' already exists. Overwrite? [y/N] "), end="", flush=True)
            try:
                ans = input().strip().lower()
            except (EOFError, KeyboardInterrupt):
                print()
                return items
            if ans != "y":
                print(dim("  Save cancelled."))
                return items

        try:
            saved_name = save_preset(name, items)
        except ValueError as e:
            print(error(f"  ✗  {e}"))
            return items

        print(success(f"  ✓  Saved {len(items)} items as preset '{colorize(saved_name, Color.CYAN + Color.BOLD)}'."))
        return items

    # ── preset delete ──────────────────────────────────────────────────────
    if sub in ("delete", "del", "rm"):
        name = sub_args or _pick_preset_interactively("delete")
        if not name:
            return items
        name = _sanitize_name(name)
        if not preset_exists(name):
            print(error(f"  ✗  Preset '{name}' not found."))
            return items
        print(warning(f"  Delete preset '{name}'? [y/N] "), end="", flush=True)
        try:
            ans = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return items
        if ans == "y":
            try:
                delete_preset(name)
                print(success(f"  ✓  Preset '{name}' deleted."))
            except FileNotFoundError as e:
                print(error(f"  ✗  {e}"))
        else:
            print(dim("  Delete cancelled."))
        return items

    print(error(f"  ✗  Unknown preset sub-command: '{sub}'.  Try: list, load, save, delete"))
    return items


# ---------------------------------------------------------------------------
# Command handlers — Compare
# ---------------------------------------------------------------------------

def _cmd_compare(items: list[str], args: str) -> None:
    """
    Handle the 'compare' command.

    Flags:
        -r / --rank   Full merge-sort ranking.
        -b / --best   Tournament knockout to find best item.
    """
    if len(items) < 2:
        print(error("  ✗  Need at least 2 items. Use 'add' or 'preset load' to add items."))
        return

    flag = args.strip().lower()

    if flag in ("-r", "--rank"):
        mode = "rank"
    elif flag in ("-b", "--best"):
        mode = "best"
    else:
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
    else:
        print(info(f"  Finding best item among {len(items)} items…"))
        print(dim("  (Type 'q' at any prompt to abort.)"))
        try:
            best, count = tournament_best(items)
            _display_best(best, count)
        except ComparisonAborted:
            print(warning("\n  ⚠  Tournament aborted."))


def _cmd_seeds(args: str) -> None:
    """
    Handle the 'seeds' command.

    Sub-commands:
        (none)        Install seed presets, skip existing.
        --force / -f  Install seed presets, overwrite existing.
        remove        Run uninstall_seeds.py to strip the feature entirely.
    """
    flag = args.strip().lower()

    # ── seeds remove ──────────────────────────────────────────────────────
    if flag == "remove":
        import subprocess
        # Use absolute path of this file to reliably find project root
        pkg_dir     = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(pkg_dir)
        script      = os.path.join(project_dir, "uninstall_seeds.py")
        if not os.path.isfile(script):
            print(error("  ✗  uninstall_seeds.py not found next to main.py."))
            return
        print()
        print(dim("  Handing off to uninstall_seeds.py…"))
        print()
        subprocess.run([sys.executable, script, "--project-dir", project_dir], check=False)
        return

    # ── seeds / seeds --force ─────────────────────────────────────────────
    force = flag in ("--force", "-f")

    names = seed_names()
    print()
    print(bold("  Built-in seed presets:"))
    print(separator())
    for name in names:
        print(f"  {colorize('·', Color.GRAY)}  {colorize(name, Color.CYAN)}")
    print(separator())

    if not force:
        print(dim("  Existing presets will be skipped.  Use 'seeds --force' to overwrite."))

    print(warning("  Install seed presets? [y/N] "), end="", flush=True)
    try:
        ans = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if ans != "y":
        print(dim("  Cancelled."))
        return

    results = install_seeds(overwrite=force)
    print()
    for name, status in results:
        if status == "written":
            icon = success("✓")
            label = colorize("written", Color.GREEN)
        elif status == "overwritten":
            icon = success("✓")
            label = colorize("overwritten", Color.YELLOW)
        else:
            icon = dim("·")
            label = colorize("skipped (already exists)", Color.GRAY)
        print(f"  {icon}  {colorize(name, Color.CYAN)}  {dim('—')}  {label}")
    print()


# ---------------------------------------------------------------------------
# Main REPL loop
# ---------------------------------------------------------------------------

PROMPT = colorize("pychoicer", Color.CYAN) + colorize(" > ", Color.GRAY)


def run() -> None:
    """
    Start the interactive PyChoicer REPL session.

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

        elif cmd in ("remove", "rm"):
            items = _cmd_remove(items, args)

        elif cmd in ("list", "l"):
            _display_items(items)

        elif cmd == "reset":
            items = _cmd_reset(items)

        elif cmd == "preset":
            items = _cmd_preset(items, args)

        elif cmd == "seeds":
            _cmd_seeds(args)

        elif cmd == "compare":
            _cmd_compare(items, args)

        elif cmd == "c":
            _cmd_compare(items, "")

        else:
            print(error(f"  ✗  Unknown command: '{cmd}'  —  type 'help' for options."))
