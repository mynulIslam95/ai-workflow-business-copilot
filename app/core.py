"""Deterministic workflow rules and persistence."""
import re
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

POLICIES = {
    "leave": ("Leave policy", "Submit time-off requests five working days in advance. Manager approval is required."),
    "purchase": ("Purchasing policy", "Purchases above EUR 250 require manager approval before ordering."),
    "access": ("Access policy", "Access requests require the system owner's approval."),
    "general": ("Workflow guidance", "Describe your request, business reason and responsible approver."),
}
RULES = {
    "leave": ("leave", "vacation", "holiday", "time off", "pto"),
    "purchase": ("purchase", "buy", "order", "supplier", "invoice", "equipment"),
    "access": ("access", "permission", "account", "login", "role"),
}

def classify(message):
    words = message.lower()
    scores = {k: sum(bool(re.search(r"\b" + re.escape(term) + r"\b", words)) for term in terms) for k, terms in RULES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "general"

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.executescript("""
    CREATE TABLE IF NOT EXISTS requests(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      requester TEXT NOT NULL, message TEXT NOT NULL,
      category TEXT NOT NULL, status TEXT NOT NULL,
      policy_title TEXT NOT NULL, policy_excerpt TEXT NOT NULL,
      created_at TEXT NOT NULL, reviewed_at TEXT);
    CREATE TABLE IF NOT EXISTS audit(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      request_id INTEGER NOT NULL,
      action TEXT NOT NULL, actor TEXT NOT NULL,
      timestamp TEXT NOT NULL, note TEXT NOT NULL);
    """)
    return con

def get_request(con, request_id):
    row = con.execute("SELECT * FROM requests WHERE id=?", (request_id,)).fetchone()
    return dict(row) if row else None

def create_request(con, requester, message):
    category = classify(message)
    title, excerpt = POLICIES[category]
    cur = con.execute("INSERT INTO requests(requester,message,category,status,policy_title,policy_excerpt,created_at) VALUES(?,?,?,?,?,?,?)", (requester, message, category, "pending", title, excerpt, now()))
    con.execute("INSERT INTO audit(request_id,action,actor,timestamp,note) VALUES(?,?,?,?,?)", (cur.lastrowid, "created", requester, now(), "Classified using keyword rules"))
    con.commit()
    return get_request(con, cur.lastrowid)

def review(con, request_id, decision, actor, note):
    if decision not in ("approved", "rejected"):
        raise ValueError("Decision must be approved or rejected")
    item = get_request(con, request_id)
    if item is None:
        raise LookupError("Request not found")
    if item["status"] != "pending":
        raise ValueError("Only pending requests may be reviewed")
    con.execute("UPDATE requests SET status=?, reviewed_at=? WHERE id=?", (decision, now(), request_id))
    con.execute("INSERT INTO audit(request_id,action,actor,timestamp,note) VALUES(?,?,?,?,?)", (request_id, decision, actor, now(), note))
    con.commit()
    return get_request(con, request_id)
