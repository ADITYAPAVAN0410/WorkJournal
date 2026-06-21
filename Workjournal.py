import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Dict

IST = timezone(timedelta(hours=5, minutes=30))

VALID_CATEGORIES = ["coding", "meeting", "planning", "review", "research", "docs", "devops", "admin", "other", "practice"]

def _user_dir(username: str) -> Path:
    path = Path.home() / ".worklog" / username.strip().lower()
    path.mkdir(parents=True, exist_ok=True)
    return path

def _journal_file(username: str) -> Path:
    return _user_dir(username) / "journal.json"

def _pin_file(username: str) -> Path:
    return _user_dir(username) / "pin.txt"

def user_exists(username: str) -> bool:
    return _pin_file(username).exists()

def set_pin(username: str, pin: str) -> None:
    _pin_file(username).write_text(pin.strip(), encoding="utf-8")

def verify_pin(username: str, pin: str) -> bool:
    f = _pin_file(username)
    if not f.exists():
        return False
    return f.read_text(encoding="utf-8").strip() == pin.strip()

def load_journal(username: str = "default") -> List[Dict]:
    f = _journal_file(username)
    if not f.exists():
        f.write_text("[]", encoding="utf-8")
        return []
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

def save_journal(entries, username: str = "default") -> None:
    _journal_file(username).write_text(
        json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8"
    )

def log_task(description, category="other", start_time=None, end_time=None, username: str = "default"):
    entries = load_journal(username)
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
    save_journal(entries, username)

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

def check_overlap(entries, new_start_str: str, new_end_str: str, username: str = "default") -> dict:
    """
    Returns {"conflict": True, "with": <entry>} if new_start–new_end overlaps
    any existing entry logged on the same date, else {"conflict": False}.
    Overlap rule: (A.start < B.end) AND (B.start < A.end)
    """
    today = datetime.now(IST).date().isoformat()

    def to_minutes(t_str: str) -> int:
        h, m = map(int, t_str.split(":"))
        return h * 60 + m

    new_s = to_minutes(new_start_str)
    new_e = to_minutes(new_end_str)

    if new_e <= new_s:
        return {"conflict": True, "reason": "end_before_start"}

    for e in entries:
        e_date = datetime.fromisoformat(e["timestamp"]).date().isoformat()
        if e_date != today:
            continue
        if not e.get("start_time") or not e.get("end_time"):
            continue
        ex_s = to_minutes(fmt_time(e["start_time"]))
        ex_e = to_minutes(fmt_time(e["end_time"]))
        if new_s < ex_e and ex_s < new_e:
            return {"conflict": True, "reason": "overlap", "with": e}

    return {"conflict": False}


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
