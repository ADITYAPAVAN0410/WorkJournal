import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict

IST = timezone(timedelta(hours=5, minutes=30))

JOURNAL_FILE = Path.home() / ".workjournal" / "journal.json"
VALID_CATEGORIES = ["coding", "meeting", "planning", "review", "research", "docs", "devops", "admin", "other", "practice"]

def load_journal() -> List[Dict]:
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

def log_task(description, category="other", start_time=None, end_time=None):
    entries = load_journal()
    today = datetime.now(IST).date().isoformat()

    def to_iso(t_str):
        if not t_str:
            return None
        return f"{today}T{t_str}:00+05:30"

    start_iso = to_iso(start_time) if start_time else datetime.now(IST).isoformat(timespec="seconds")
    end_iso = to_iso(end_time) if end_time else None

    entries.append({
        "timestamp": start_iso,
        "start_time": start_iso,
        "end_time": end_iso,
        "activity_description": description,
        "category": category,
    })
    save_journal(entries)

def fmt_date(ts: str) -> str:
    return datetime.fromisoformat(ts).strftime("%d-%m-%Y")

def fmt_time(ts: str) -> str:
    return datetime.fromisoformat(ts).strftime("%H:%M")

def fmt_duration(start_ts, end_ts) -> str:
    if not start_ts or not end_ts:
        return "N/A"
    try:
        start = datetime.fromisoformat(start_ts)
        end = datetime.fromisoformat(end_ts)
        delta = end - start
        if delta.total_seconds() <= 0:
            return "N/A"
        total_min = int(delta.total_seconds() // 60)
        h, m = divmod(total_min, 60)
        return f"{h}h {m}m"
    except Exception:
        return "N/A"

def duration_minutes(start_ts, end_ts) -> float:
    if not start_ts or not end_ts:
        return 0.0
    try:
        start = datetime.fromisoformat(start_ts)
        end = datetime.fromisoformat(end_ts)
        delta = end - start
        return max(0.0, delta.total_seconds() / 60)
    except Exception:
        return 0.0
