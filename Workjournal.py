import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict

IST = timezone(timedelta(hours=5, minutes=30))

# Config
JOURNAL_FILE = Path.home() / ".workjournal" / "journal.json"
VALID_CATEGORIES = ["coding", "meeting", "planning", "review", "research", "docs", "devops", "admin", "other", "practice"]

def load_journal() -> List[Dict]:
    """Load entries from journal.json."""
    JOURNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not JOURNAL_FILE.exists():
        JOURNAL_FILE.write_text("[]", encoding="utf-8")
        return []
    try:
        return json.loads(JOURNAL_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

def save_journal(entries) -> None:
    JOURNAL_FILE.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")

def log_task(description, category="other"):
    """Saves a new task to the journal."""
    entries = load_journal()
    entries.append({
        "timestamp": datetime.now(IST).isoformat(timespec="seconds"),
        "activity_description": description,
        "category": category,
    })
    save_journal(entries)

def fmt_date(ts: str) -> str:
    """Returns date in DD-MM-YYYY format."""
    return datetime.fromisoformat(ts).strftime("%d-%m-%Y")

def fmt_time(ts: str) -> str:
    """Returns time in HH:MM format."""
    return datetime.fromisoformat(ts).strftime("%H:%M")