"""
uninstall_seeds.py - Removes the seeds feature from PyChoicer.

This script is called by 'seeds remove' inside the CLI.
It can also be run directly: python uninstall_seeds.py

What it does:
  1. Deletes pychoicer/seeds.py
  2. Removes the seeds import line from pychoicer/cli.py
  3. Removes the _cmd_seeds function from pychoicer/cli.py
  4. Removes the 'seeds' dispatch branch from pychoicer/cli.py
  5. Removes all seeds help entries from pychoicer/utils.py
  6. Deletes this script
"""

import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# When called via subprocess from cli.py, accept an explicit project dir
# to avoid __file__ resolution issues with relative paths.
if "--project-dir" in sys.argv:
    idx = sys.argv.index("--project-dir")
    if idx + 1 < len(sys.argv):
        BASE_DIR = sys.argv[idx + 1]
SEEDS_FILE = os.path.join(BASE_DIR, "pychoicer", "seeds.py")
CLI_FILE   = os.path.join(BASE_DIR, "pychoicer", "cli.py")
UTILS_FILE = os.path.join(BASE_DIR, "pychoicer", "utils.py")

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
GRAY   = "\033[90m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg: str)   -> None: print(f"  {GREEN}✓{RESET}  {msg}")
def err(msg: str)  -> None: print(f"  {RED}✗{RESET}  {msg}")
def info(msg: str) -> None: print(f"  {GRAY}·{RESET}  {msg}")


def delete_seeds_module() -> bool:
    if not os.path.isfile(SEEDS_FILE):
        info("seeds.py already absent — skipping")
        return True
    try:
        os.remove(SEEDS_FILE)
        ok("Deleted pychoicer/seeds.py")
        return True
    except OSError as e:
        err(f"Could not delete seeds.py: {e}")
        return False


def _read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _write(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def clean_cli() -> bool:
    """Remove seeds import, _cmd_seeds function, and dispatch branch from cli.py."""
    if not os.path.isfile(CLI_FILE):
        err("cli.py not found")
        return False

    content = _read(CLI_FILE)
    original = content

    # Remove import line
    content = re.sub(r"^from \.seeds import.*\n", "", content, flags=re.MULTILINE)

    # Remove _cmd_seeds function block
    content = re.sub(
        r"\ndef _cmd_seeds\(.*?\n(?=\n(?:def |class |#\s*-{5,}))",
        "\n",
        content,
        flags=re.DOTALL,
    )

    # Remove dispatch branch
    content = re.sub(
        r"[ \t]+elif cmd == \"seeds\":\n[ \t]+_cmd_seeds\(args\)\n",
        "",
        content,
    )

    if content == original:
        info("No seeds references found in cli.py — already clean")
        return True

    _write(CLI_FILE, content)
    ok("Cleaned pychoicer/cli.py")
    return True


def clean_utils() -> bool:
    """Remove all seeds-related help entries from utils.py."""
    if not os.path.isfile(UTILS_FILE):
        err("utils.py not found")
        return False

    content = _read(UTILS_FILE)
    original = content

    content = re.sub(r'[ \t]+\("seeds".*\n', "", content)
    content = re.sub(r'[ \t]+\("seeds --force".*\n', "", content)
    content = re.sub(r'[ \t]+\("seeds remove".*\n', "", content)

    if content == original:
        info("No seeds entries found in utils.py — already clean")
        return True

    _write(UTILS_FILE, content)
    ok("Cleaned pychoicer/utils.py")
    return True


def delete_self() -> None:
    try:
        os.remove(os.path.abspath(__file__))
        ok("Deleted uninstall_seeds.py")
    except OSError:
        info("Could not delete uninstall_seeds.py — remove it manually")


def run(confirm: bool = True) -> bool:
    print()
    print(f"  {BOLD}Remove seeds feature from PyChoicer?{RESET}")
    print(f"  {GRAY}This will delete seeds.py and clean cli.py + utils.py.{RESET}")
    print()

    if confirm:
        print(f"  {YELLOW}Continue? [y/N]{RESET} ", end="", flush=True)
        try:
            ans = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            print(f"  {GRAY}Aborted.{RESET}")
            return False
        if ans != "y":
            print(f"  {GRAY}Aborted.{RESET}")
            return False

    print()
    ok_1 = delete_seeds_module()
    ok_2 = clean_cli()
    ok_3 = clean_utils()
    success = ok_1 and ok_2 and ok_3

    if success:
        delete_self()
        print()
        print(f"  {GREEN}{BOLD}Seeds feature removed.{RESET}"
              f"  {GRAY}Restart PyChoicer for changes to take effect.{RESET}")
    else:
        print()
        print(f"  {YELLOW}Uninstall completed with errors — check output above.{RESET}")

    print()
    return success


if __name__ == "__main__":
    no_confirm = "--no-confirm" in sys.argv
    success = run(confirm=not no_confirm)
    sys.exit(0 if success else 1)
