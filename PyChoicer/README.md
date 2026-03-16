# ChoiceRanker

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
choice_ranker/
├── main.py           # Entry point
├── choice_ranker/
│   ├── cli.py        # REPL loop and command dispatcher
│   ├── ranking.py    # Merge-sort and tournament algorithms
│   ├── comparison.py # Pairwise question engine
│   ├── presets.py    # Preset save/load/list/delete
│   └── utils.py      # Colors, formatting, input parsing
└── presets/          # Auto-created. Stores preset .txt files
```

---

## Commands

### Items

| Command | Description |
|---|---|
| `add <items>` / `a` | Add items, comma-separated. Duplicates are skipped. |
| `remove <item>` / `rm` | Remove by number or name. Supports prefix matching. |
| `list` / `l` | Show current items with index numbers. |
| `reset` | Clear all items (asks for confirmation). |

**Examples:**
```
add istanbul, berlin, london, new york
add tokyo          # adds to existing list
remove 3           # removes item at position 3
remove ber         # removes "berlin" (prefix match)
remove             # shows list, then prompts interactively
```

---

### Compare

Starts an interactive comparison session. Items are shuffled before each session to avoid positional bias.

| Command | Description |
|---|---|
| `compare -r` / `--rank` | Full ranking via merge-sort. ~O(n log n) questions. |
| `compare -b` / `--best` | Find single best item via tournament. Exactly n-1 questions. |
| `compare` | Prompts you to choose a mode interactively. |

During comparison, type `q` at any prompt to abort the session.

**How it works:**

- **Rank mode** uses merge-sort: recursively splits the list in halves and merges by asking your preference at each step. Produces a complete ordering with the minimum number of questions possible for full ranking.

- **Best mode** uses a knockout tournament: items are paired up, losers are eliminated, winners advance. Requires exactly `n - 1` questions regardless of list size.

---

### Presets

Presets are plain-text files stored in the `presets/` directory. Each file contains one item per line and can be edited by hand.

| Command | Description |
|---|---|
| `preset list` | Show all saved presets with item counts. |
| `preset save <name>` | Save current items as a named preset. |
| `preset load <name>` | Load a preset. If items exist, asks to replace or merge. |
| `preset delete <name>` | Delete a preset (asks for confirmation). |
| `preset show <name>` | Preview a preset's contents without loading it. |

**Examples:**
```
preset save cities
preset load cities        # prompts: replace or merge?
preset load               # shows list, lets you pick interactively
preset list               # cities (6 items)
preset delete cities
```

Preset names are sanitized automatically: spaces become underscores, special characters are removed.

---

## Example Session

```
choiceranker > add istanbul, berlin, london, konya, batum, new york
  ✓  6 item(s) added.

choiceranker > preset save cities
  ✓  Saved 6 items as preset 'cities'.

choiceranker > compare -b
  Finding best item among 6 items…

  [1/5]  Which do you prefer?
    [1]  berlin
    [2]  london
  > 1

  ...

  ══════════════════════════════════════
  Tournament Winner
  ══════════════════════════════════════
  🏆  berlin

  Questions asked: 5

choiceranker > remove batum
  ✓  Removed: batum

choiceranker > compare -r
  Starting full ranking of 5 items…
  ...
```

---

## Preset File Format

Preset files are plain text, one item per line:

```
# presets/cities.txt
istanbul
berlin
london
konya
new york
```

You can create or edit preset files manually in any text editor.
