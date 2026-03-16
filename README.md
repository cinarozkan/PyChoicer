# PyChoicer v1.3.1

A command-line tool for ranking items through pairwise comparisons.  
Instead of asking "rank these 10 things", it asks simple **A or B?** questions and builds the ranking from your answers.

---

## Setup

No external dependencies. Requires Python 3.11+.

```bash
python main.py
```

---

## Project Structure

```
PyChoicer/
├── main.py
├── uninstall_seeds.py   # run to remove the seeds feature entirely
├── README.md
└── pychoicer/
    ├── __init__.py
    ├── cli.py        # REPL loop and command dispatcher
    ├── ranking.py    # Merge-sort and tournament algorithms
    ├── comparison.py # Pairwise question engine
    ├── presets.py    # Preset save/load/list/delete
    ├── seeds.py      # Built-in example presets
    └── utils.py      # Colors, formatting, input parsing
```

`presets/` directory is auto-created on first use.

---

## Commands

### Items

| Command | Description |
|---|---|
| `add <items>` / `a` | Add items, comma-separated. Duplicates are skipped. |
| `remove <item>` / `rm` | Remove by number or name. Supports prefix matching. |
| `list` / `l` | Show current items with index numbers. |
| `reset` | Clear all items (asks for confirmation). |

```
add istanbul, berlin, london, new york
add tokyo          # adds to existing list
remove 3           # removes item at position 3
remove ber         # removes "berlin" (prefix match)
remove             # shows list, then prompts interactively
```

---

### Compare

Starts an interactive comparison session. Items are shuffled before each session to avoid positional bias. Type `q` at any prompt to abort.

| Command | Description |
|---|---|
| `compare -r` / `--rank` | Full ranking via merge-sort. ~O(n log n) questions. |
| `compare -b` / `--best` | Find single best item via tournament. Exactly n-1 questions. |
| `compare` | Prompts you to choose a mode interactively. |

**How it works:**

- **Rank mode** uses merge-sort: recursively splits the list in halves and merges by asking your preference at each step. Produces a complete ordering with the minimum number of questions possible for full ranking.

- **Best mode** uses a knockout tournament: items are paired up, losers are eliminated, winners advance. Requires exactly `n - 1` questions regardless of list size.

---

### Presets

Presets are plain-text files stored in the `presets/` directory. Each file contains one item per line and can be edited manually.

| Command | Description |
|---|---|
| `preset list` | Show all saved presets with item counts. |
| `preset save <n>` | Save current items as a named preset. |
| `preset load <n>` | Load a preset. If items exist, asks to replace or merge. |
| `preset delete <n>` | Delete a preset (asks for confirmation). |

```
preset save cities
preset load cities        # prompts: replace or merge?
preset load               # shows list, lets you pick interactively
preset list
preset delete cities
```

Preset names preserve their casing. Spaces are converted to underscores; special characters are removed.

---

### Seeds

The `seeds` command installs built-in example presets into the `presets/` directory.

| Command | Description |
|---|---|
| `seeds` | Install built-in presets. Skips any that already exist. |
| `seeds --force` | Install and overwrite existing presets. |
| `seeds remove` | Remove the seeds feature entirely from the project. |

**Available seed presets:**

- `2026-F1-Drivers` — 22 drivers on the 2026 Formula 1 grid
- `Popular-Linux-Distros` — 31 well-known Linux distributions

> These two presets exist because of my personal interests in Formula 1 and Linux — they serve no other purpose than being convenient starting points for me. If you want to add your own seed presets, open `pychoicer/seeds.py` and append an entry to the `SEED_PRESETS` dict. To remove the seeds feature entirely, run `seeds remove` in the CLI or `python uninstall_seeds.py` directly — this deletes `seeds.py`, cleans all references from the codebase, and removes `uninstall_seeds.py` itself.

---

## Preset File Format

Presets are plain text, one item per line. You can create or edit them in any text editor.

```
# presets/cities.txt
istanbul
berlin
london
konya
new york
```


