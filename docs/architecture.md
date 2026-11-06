# Architecture

Browser dashboard → FastAPI endpoints → SQLite database.

A deterministic classifier assigns each request to leave, purchase, access or general. The corresponding sample policy text is returned. Every new request starts pending. Review decisions are explicit and logged in an audit table.

## Data
The requests table stores the requester, text, category, status, policy guidance and timestamps. The audit table records creation and review actions with entered actor names.

## Boundaries
This prototype is local-only and not suitable for deployment without authentication, role-based access, privacy controls, request protection and security testing. The sample policy statements are fictional.

## Future integrations (not implemented)
Power Apps intake, Power Automate approvals, authenticated SharePoint knowledge retrieval and evaluated optional LLM classification.
