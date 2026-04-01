# PyChoicer v1.4.1

A command-line tool for ranking items through pairwise comparisons.  
Instead of asking "rank these 10 things", it asks simple **A or B?** questions and builds the ranking from your answers.

This project was originally made with AI for my own needs

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
├── README.md
└── pychoicer/
    ├── __init__.py
    ├── cli.py        # REPL loop and command dispatcher
    ├── ranking.py    # Merge-sort and tournament algorithms
    ├── comparison.py # Pairwise question engine
    ├── presets.py    # Preset save/load/list/delete
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

Presets are plain text, one item per line. You can create or edit them in any text editor.

```
# presets/cities.txt
istanbul
berlin
london
konya
new york
```

---
