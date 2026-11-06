"""Local demo API. Not suitable for public deployment."""
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from .core import connect, create_request, get_request, review

ROOT = Path(__file__).resolve().parent.parent
DB = os.environ.get("COPILOT_DB", str(ROOT / "data" / "requests.db"))
app = FastAPI(title="AI Workflow Automation & Business Copilot", version="1.0.0")

class NewRequest(BaseModel):
    requester: str = Field(min_length=2, max_length=80)
    message: str = Field(min_length=5, max_length=2000)

class ReviewRequest(BaseModel):
    actor: str = Field(min_length=2, max_length=80)
    decision: str
    note: str = Field(default="Reviewed by human", max_length=500)

@app.get("/")
def home():
    return FileResponse(ROOT / "static" / "index.html")

@app.get("/health")
def health():
    return {"status": "ok", "mode": "deterministic demo", "live_integrations": False}

@app.post("/api/requests", status_code=201)
def submit(body: NewRequest):
    with connect(DB) as con:
        return create_request(con, body.requester, body.message)

@app.get("/api/requests")
def list_requests():
    with connect(DB) as con:
        return [dict(row) for row in con.execute("SELECT * FROM requests ORDER BY id DESC LIMIT 100")]

@app.get("/api/requests/{request_id}")
def detail(request_id: int):
    with connect(DB) as con:
        item = get_request(con, request_id)
        if item is None:
            raise HTTPException(404, "Request not found")
        return item

@app.post("/api/requests/{request_id}/review")
def decide(request_id: int, body: ReviewRequest):
    with connect(DB) as con:
        try:
            return review(con, request_id, body.decision, body.actor, body.note)
        except LookupError as e:
            raise HTTPException(404, str(e)) from e
        except ValueError as e:
            raise HTTPException(409, str(e)) from e

@app.get("/api/audit")
def audit():
    with connect(DB) as con:
        return [dict(row) for row in con.execute("SELECT * FROM audit ORDER BY id DESC LIMIT 200")]

@app.get("/api/summary")
def summary():
    with connect(DB) as con:
        total = con.execute("SELECT count(*) FROM requests").fetchone()[0]
        status = {r[0]: r[1] for r in con.execute("SELECT status,count(*) FROM requests GROUP BY status")}
        categories = {r[0]: r[1] for r in con.execute("SELECT category,count(*) FROM requests GROUP BY category")}
        return {"total": total, "by_status": status, "by_category": categories}
