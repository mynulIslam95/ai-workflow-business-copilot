# AI Workflow Automation & Business Copilot

A business workflow prototype using FastAPI, SQLite and a responsive web dashboard.

## Features
- Keyword-based classification of leave, purchase and access requests
- Illustrative internal policy guidance
- Manual approval or rejection
- SQLite request storage and audit history
- Dashboard, summary endpoints and automated tests

**Scope:** This is a deterministic, rules-based prototype, not a live LLM agent. It uses synthetic business scenarios. Power Apps, Power Automate and Microsoft Copilot integrations are future extensions and are not implemented.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 or http://127.0.0.1:8000/docs.

Run tests: `pytest -q`.

## Endpoints

- `GET /health`
- `POST /api/requests`
- `GET /api/requests`
- `GET /api/requests/{id}`
- `POST /api/requests/{id}/review`
- `GET /api/audit`
- `GET /api/summary`

## Limitations
Do not deploy publicly as-is. Authentication, authorization, rate limiting and production privacy controls are not implemented. Reviewer identities are user-entered and unverified. Approval does not trigger any external action. Do not use real employee information.

See `docs/architecture.md` for design notes.
