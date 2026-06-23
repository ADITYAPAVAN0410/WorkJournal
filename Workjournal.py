import streamlit as st
from supabase import create_client
from datetime import datetime, timezone, timedelta
from typing import List, Dict

IST = timezone(timedelta(hours=5, minutes=30))

VALID_CATEGORIES = [
    "coding", "meeting", "planning", "review",
    "research", "docs", "devops", "admin", "other", "practice"
]

# ── Supabase client (cached) ──────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

# ── Auth ──────────────────────────────────────────────────────────────────────
def user_exists(username: str) -> bool:
    res = get_client().table("users").select("id").eq("username", username.lower()).execute()
    return len(res.data) > 0

def set_pin(username: str, pin: str) -> None:
    get_client().table("users").insert({"username": username.lower(), "pin": pin.strip()}).execute()

def verify_pin(username: str, pin: str) -> bool:
    res = get_client().table("users").select("pin").eq("username", username.lower()).execute()
    if not res.data:
        return False
    return res.data[0]["pin"] == pin.strip()

# ── Journal ───────────────────────────────────────────────────────────────────
def load_journal(username: str = "default") -> List[Dict]:
    res = (
        get_client()
        .table("journal_entries")
        .select("*")
        .eq("username", username.lower())
        .order("timestamp", desc=False)
        .execute()
    )
    return res.data or []

def log_task(description, category="other", start_time=None, end_time=None, username: str = "default"):
    today = datetime.now(IST).date().isoformat()

    def to_iso(t_str):
        if not t_str:
            return None
        return f"{today}T{t_str}:00+05:30"

    start_iso = to_iso(start_time) if start_time else datetime.now(IST).isoformat(timespec="seconds")
    end_iso   = to_iso(end_time)   if end_time   else None

    get_client().table("journal_entries").insert({
        "username":             username.lower(),
        "timestamp":            start_iso,
        "start_time":           start_iso,
        "end_time":             end_iso,
        "activity_description": description,
        "category":             category,
    }).execute()

# ── Formatters ────────────────────────────────────────────────────────────────
def fmt_date(ts: str) -> str:
    return datetime.fromisoformat(ts).strftime("%d-%m-%Y")

def fmt_time(ts: str) -> str:
    return datetime.fromisoformat(ts).strftime("%H:%M")

def fmt_duration(start_ts, end_ts) -> str:
    if not start_ts or not end_ts:
        return "N/A"
    try:
        delta = datetime.fromisoformat(end_ts) - datetime.fromisoformat(start_ts)
        if delta.total_seconds() <= 0:
            return "N/A"
        h, m = divmod(int(delta.total_seconds() // 60), 60)
        return f"{h}h {m}m"
    except Exception:
        return "N/A"

def duration_minutes(start_ts, end_ts) -> float:
    if not start_ts or not end_ts:
        return 0.0
    try:
        delta = datetime.fromisoformat(end_ts) - datetime.fromisoformat(start_ts)
        return max(0.0, delta.total_seconds() / 60)
    except Exception:
        return 0.0

# ── Overlap check ─────────────────────────────────────────────────────────────
def check_overlap(entries, new_start_str: str, new_end_str: str, username: str = "default") -> dict:
    today = datetime.now(IST).date().isoformat()

    def to_min(t: str) -> int:
        h, m = map(int, t.split(":"))
        return h * 60 + m

    new_s = to_min(new_start_str)
    new_e = to_min(new_end_str)

    if new_e <= new_s:
        return {"conflict": True, "reason": "end_before_start"}

    for e in entries:
        if datetime.fromisoformat(e["timestamp"]).date().isoformat() != today:
            continue
        if not e.get("start_time") or not e.get("end_time"):
            continue
        ex_s = to_min(fmt_time(e["start_time"]))
        ex_e = to_min(fmt_time(e["end_time"]))
        if new_s < ex_e and ex_s < new_e:
            return {"conflict": True, "reason": "overlap", "with": e}

    return {"conflict": False}
