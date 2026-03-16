"""
presets.py - Preset management for PyChoicer.

Presets are plain-text files stored in a 'presets/' directory next to main.py.
Each preset file contains one item per line.

File format (example: presets/cities.txt):
    istanbul
    berlin
    london
    new york

Functions:
    save_preset   — Write current items to a named preset file.
    load_preset   — Read items from a preset file.
    list_presets  — Return all available preset names.
    delete_preset — Remove a preset file.
"""

import os
import re

# Directory where preset files are stored (relative to main.py location)
PRESETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "presets")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_dir() -> None:
    """Create the presets directory if it doesn't exist."""
    os.makedirs(PRESETS_DIR, exist_ok=True)


def _preset_path(name: str) -> str:
    """Return the full file path for a preset name."""
    return os.path.join(PRESETS_DIR, f"{name}.txt")


def _sanitize_name(name: str) -> str:
    """
    Sanitize a preset name for use as a filename.

    Strips whitespace, replaces spaces with underscores,
    and removes any character that isn't alphanumeric, underscore, hyphen,
    or a Unicode letter (to support names like Hülkenberg).

    Case is preserved so that seed preset names like '2026-F1-Drivers'
    round-trip correctly.

    Args:
        name: Raw preset name from user input.

    Returns:
        Safe filename-compatible string, or empty string if nothing remains.
    """
    name = name.strip()
    name = name.replace(" ", "_")
    name = re.sub(r"[^\w\-]", "", name)
    return name


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def save_preset(name: str, items: list[str]) -> str:
    """
    Save a list of items to a named preset file.

    Args:
        name: Human-readable preset name (will be sanitized).
        items: List of item strings to save.

    Returns:
        The sanitized preset name actually used.

    Raises:
        ValueError: If name is empty after sanitizing, or items list is empty.
    """
    clean = _sanitize_name(name)
    if not clean:
        raise ValueError("Preset name is invalid or empty after sanitizing.")
    if not items:
        raise ValueError("Cannot save an empty item list as a preset.")

    _ensure_dir()
    path = _preset_path(clean)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(items))
    return clean


def load_preset(name: str) -> list[str]:
    """
    Load items from a preset file.

    Args:
        name: Preset name (exact, as returned by list_presets).

    Returns:
        List of item strings.

    Raises:
        FileNotFoundError: If the preset does not exist.
        ValueError: If the file is empty or contains no valid items.
    """
    path = _preset_path(name)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Preset '{name}' not found.")

    with open(path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    items = [line.strip() for line in raw_lines if line.strip()]
    if not items:
        raise ValueError(f"Preset '{name}' is empty.")
    return items


def list_presets() -> list[str]:
    """
    Return a sorted list of available preset names (without .txt extension).

    Returns:
        List of preset name strings, or empty list if none exist.
    """
    _ensure_dir()
    names = []
    for fname in sorted(os.listdir(PRESETS_DIR)):
        if fname.endswith(".txt"):
            names.append(fname[:-4])  # strip .txt
    return names


def delete_preset(name: str) -> None:
    """
    Delete a preset file.

    Args:
        name: Preset name to delete.

    Raises:
        FileNotFoundError: If the preset does not exist.
    """
    path = _preset_path(name)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Preset '{name}' not found.")
    os.remove(path)


def preset_exists(name: str) -> bool:
    """Return True if a preset with the given name exists."""
    return os.path.isfile(_preset_path(name))
