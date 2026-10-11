# Deenly workspace

This monorepo contains `backend/` (Django, SQLite, aiogram, Django Q2) and
`frontend/` (React, TypeScript, Vite, licensed Minimal UI v7.4.0, MUI).

- Preserve existing bot data, user progress and Telegram templates.
- Keep business rules in backend domain services shared by bot and API.
- Use the same authenticated Telegram profile across bot and website.
- Use `docs/API_CONTRACT.md` for the initial API/frontend integration.
- Run Python commands from `backend/` and npm commands from `frontend/`.
- Do not commit env files, databases, vendor ZIPs, runtime artifacts or secrets.
- Do not modify the Nexa reference project; its code is an architecture reference.
- All mutating API endpoints require authentication, ownership and CSRF checks.

