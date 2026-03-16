"""
seeds.py - Built-in example presets for PyChoicer.

The `seeds` command writes these preset files to the presets/ directory.
This is a personal preference feature — the bundled sets (F1 drivers,
Linux distros) reflect the author's own interests and are included purely
for convenience.

Adding a new seed: append an entry to SEED_PRESETS below.
"""

from .presets import PRESETS_DIR, _preset_path, preset_exists
import os

# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

SEED_PRESETS: dict[str, list[str]] = {
    "2026-F1-Drivers": [
        "Lando Norris",
        "Oscar Piastri",
        "George Russell",
        "Andrea Kimi Antonelli",
        "Charles Leclerc",
        "Lewis Hamilton",
        "Max Verstappen",
        "Isack Hadjar",
        "Fernando Alonso",
        "Lance Stroll",
        "Pierre Gasly",
        "Franco Colapinto",
        "Carlos Sainz",
        "Alexander Albon",
        "Esteban Ocon",
        "Oliver Bearman",
        "Liam Lawson",
        "Arvid Lindblad",
        "Nico Hülkenberg",
        "Gabriel Bortoleto",
        "Sergio Pérez",
        "Valtteri Bottas",
    ],
    "Popular-Linux-Distros": [
        "Ubuntu",
        "Linux Mint",
        "Debian",
        "Fedora",
        "Arch Linux",
        "Manjaro",
        "Pop!_OS",
        "openSUSE",
        "Zorin OS",
        "Kali Linux",
        "EndeavourOS",
        "MX Linux",
        "elementary OS",
        "Garuda Linux",
        "AlmaLinux",
        "Rocky Linux",
        "Red Hat Enterprise Linux",
        "CentOS Stream",
        "Gentoo",
        "NixOS",
        "Deepin",
        "Solus",
        "Slackware",
        "Parrot OS",
        "Alpine Linux",
        "Void Linux",
        "CachyOS",
        "Puppy Linux",
        "Oracle Linux",
        "Bazzite",
        "Vanilla OS",
    ],
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def install_seeds(overwrite: bool = False) -> list[tuple[str, str]]:
    """
    Write all seed presets to the presets/ directory.

    Args:
        overwrite: If True, existing files are overwritten.
                   If False, existing files are skipped.

    Returns:
        List of (preset_name, status) tuples where status is
        "written", "skipped", or "overwritten".
    """
    os.makedirs(PRESETS_DIR, exist_ok=True)
    results: list[tuple[str, str]] = []

    for name, items in SEED_PRESETS.items():
        path = _preset_path(name)
        exists = preset_exists(name)

        if exists and not overwrite:
            results.append((name, "skipped"))
            continue

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(items))

        status = "overwritten" if exists else "written"
        results.append((name, status))

    return results


def seed_names() -> list[str]:
    """Return the names of all available seed presets."""
    return list(SEED_PRESETS.keys())
