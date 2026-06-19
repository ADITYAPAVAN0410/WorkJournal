# WorkJournal (`wj`)

A lightweight CLI tool for logging and reviewing your daily work activities — right from the terminal.

---

## Quick Start

### 1. Install the dependency

```bash
pip install tabulate
```

### 2. Make the script executable

```bash
chmod +x /path/to/workjournal.py
```

### 3. Set up the `wj` alias

#### For **Zsh** users (`.zshrc`)

```bash
echo 'alias wj="python3 /path/to/workjournal.py"' >> ~/.zshrc
source ~/.zshrc
```

#### For **Bash** users (`.bashrc`)

```bash
echo 'alias wj="python3 /path/to/workjournal.py"' >> ~/.bashrc
source ~/.bashrc
```

> **Tip:** Replace `/path/to/workjournal.py` with the actual absolute path, e.g. `~/scripts/workjournal.py` or `/usr/local/bin/workjournal.py`.

#### Optional: Install as a global command (no alias needed)

```bash
cp workjournal.py /usr/local/bin/wj
chmod +x /usr/local/bin/wj
# Edit the shebang at line 1 if needed: #!/usr/bin/env python3
```

---

## Usage

### Log an activity

```bash
wj log "Reviewed pull requests for the auth module"
wj log "Standup with the team" --category meeting
wj log "Drafted Q3 roadmap" --category planning
```

### View reports

```bash
wj report daily      # Everything logged today
wj report weekly     # Last 7 days
wj report monthly    # Current calendar month
```

### List all categories

```bash
wj categories
```

### Show help

```bash
wj help
```

---

## Categories

| Category   | Use for                              |
|------------|--------------------------------------|
| `coding`   | Writing or reviewing code            |
| `meeting`  | Standups, syncs, calls               |
| `planning` | Roadmaps, sprint planning, estimates |
| `review`   | Code reviews, document reviews       |
| `research` | Investigating, spike work            |
| `docs`     | Writing documentation                |
| `devops`   | CI/CD, deployments, infra            |
| `admin`    | HR tasks, expenses, admin work       |
| `other`    | Anything else (default)              |

---

## Data Storage

All entries are saved to:

```
~/.workjournal/journal.json
```

The file is created automatically on first use. You can back it up, sync it to a cloud drive, or open it in any text editor — it's plain JSON.

**Sample entry:**
```json
{
  "timestamp": "2026-06-17T09:15:00",
  "activity_description": "Reviewed pull requests for the auth module",
  "category": "review"
}
```

---

## Example Session

```bash
$ wj log "Morning standup" --category meeting
  ✅  Logged [🤝 meeting]: Morning standup
       @ 09:02 AM on Wed 17 Jun 2026

$ wj log "Fixed the HRIS integration bug" --category coding
  ✅  Logged [💻 coding]: Fixed the HRIS integration bug
       @ 10:45 AM on Wed 17 Jun 2026

$ wj log "Updated onboarding checklist doc" --category docs
  ✅  Logged [📝 docs]: Updated onboarding checklist doc
       @ 02:30 PM on Wed 17 Jun 2026

$ wj report daily

  📓  WorkJournal — Today  (Wed 17 Jun 2026)  (3 entries)
  ╭────────────────┬────────────┬─────────────┬──────────────────────────────────────╮
  │ Date           │ Time       │ Category    │ Activity                             │
  ├────────────────┼────────────┼─────────────┼──────────────────────────────────────┤
  │ Wed 17 Jun 2026│ 09:02 AM   │ 🤝 meeting  │ Morning standup                      │
  │ Wed 17 Jun 2026│ 10:45 AM   │ 💻 coding   │ Fixed the HRIS integration bug       │
  │ Wed 17 Jun 2026│ 02:30 PM   │ 📝 docs     │ Updated onboarding checklist doc     │
  ╰────────────────┴────────────┴─────────────┴──────────────────────────────────────╯

  Breakdown → 💻 coding: 1  📝 docs: 1  🤝 meeting: 1
```

---

## Requirements

- Python 3.8+
- `tabulate` library (`pip install tabulate`)
