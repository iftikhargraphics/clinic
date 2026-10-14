# Doctor & Clinic Website and Management System

A starter full-stack template using HTML, CSS, Vanilla JavaScript, FastAPI, SQLAlchemy and SQLite/PostgreSQL. All included doctor profiles and service descriptions are fictional demo content.

## Implemented in this starter

- Responsive public landing page with clinic services, doctor cards, contact links and booking form.
- FastAPI endpoints for public doctors/services and appointment requests.
- SQLAlchemy models and development-time schema initialization.
- Appointment overlap checks per doctor and pending/confirmed/completed/cancelled/no-show statuses.
- Staff login using PBKDF2-HMAC password hashing and short-lived signed bearer tokens.
- Protected staff appointment listing and status updates, plus basic audit events.
- Accessible labels, status messages, focus indicators and reduced-motion handling.
- Environment-based configuration, CORS allowlist and basic security response headers.

## Important limitations

This is a development starter, **not a production-ready healthcare platform**. Before real patient use, implement and independently review rate limiting, account recovery, session revocation, stronger scheduling concurrency guarantees, migrations, robust audit coverage, retention/deletion policies, monitoring, backups, staff account management, patient portal ownership checks, CSRF/session strategy if switching to cookies, notification consent and provider integrations. Do not store clinical notes or real patient information in this starter. The demo appointment endpoint stores contact information and must be protected operationally.

`Base.metadata.create_all()` is used for local bootstrap only. Alembic migrations are required before production. The current appointment conflict check can still race under concurrent requests; use database-backed exclusion/locking or a carefully designed transactional reservation strategy before production.

## Local setup on Windows / VS Code

1. Install Python 3.11+ and VS Code.
2. Open this folder in VS Code.
3. In PowerShell:

   ```powershell
   cd backend
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item ..\.env.example ..\.env
   ```

4. Edit the root `.env`: set `SECRET_KEY` to a long random value and set a unique `SEED_ADMIN_PASSWORD`. Do not commit `.env`. The default admin email is `admin@example.test`; change it for your environment.
5. Load the root environment variables before starting the API. From the repository root:

   ```powershell
   pip install -r backendequirements.txt
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   $env:SECRET_KEY="paste-a-generated-random-secret-here"
   $env:SEED_ADMIN_EMAIL="admin@example.test"
   $env:SEED_ADMIN_PASSWORD="use-a-unique-strong-password"
   $env:DATABASE_URL="sqlite:///./clinic.db"
   uvicorn backend.app.main:app --reload --app-dir .
   ```

   Alternative: `cd backend`, activate `.venv`, set the same environment variables in PowerShell, then run `uvicorn app.main:app --reload`. In this alternative, ensure the root `.env` values are exported into the process; the app does not automatically load `.env` in this starter.

6. Visit `http://127.0.0.1:8000/docs` for interactive API docs and `http://127.0.0.1:8000/health` for health status.
7. Serve the `frontend` directory using VS Code Live Server (typically `http://127.0.0.1:5500`). Set `window.CLINIC_API_BASE` before `app.js` if your API uses another URL.
8. Open `frontend/admin/login.html` and sign in using the configured seed admin credentials.
9. Run tests from the repository root after installing dependencies:

   ```powershell
   $env:PYTHONPATH="backend"
   pytest backend/tests -q
   ```

## Database and migrations

SQLite is used by default for local work. PostgreSQL is intended for deployment. Install Alembic and add reviewed migration scripts before production; do not rely on automatic table creation for schema changes. For PostgreSQL, set `DATABASE_URL` to `postgresql+psycopg://...` using credentials stored in the host's secret manager.

## Hosting and domain

The public HTML/CSS/JS can be hosted on static hosting. FastAPI cannot run on static-only hosting; use a Python-capable VPS/app host or a verified Hostinger plan that explicitly supports persistent Python ASGI applications. Confirm the current plan's Python version, ASGI process management, environment variables, database connectivity, and deployment restrictions with the host before purchase. Use managed PostgreSQL or secured PostgreSQL on a server, HTTPS, a reverse proxy, backups, monitoring and least-privilege credentials.

For a custom domain: point DNS records to the host's documented targets, configure TLS/HTTPS, set the exact frontend origin in `ALLOWED_ORIGINS`, set the API URL in frontend configuration, and test from mobile and desktop. Update canonical URLs and sitemap to the real domain, then verify the domain in Google Search Console and submit the sitemap. Google indexing and ranking are not guaranteed.

## Pre-production checklist

- [ ] Independent security review and penetration testing
- [ ] Alembic migrations and concurrency-safe appointment reservation
- [ ] Rate limiting, brute-force protection, account recovery and session revocation
- [ ] Role/ownership tests for every protected endpoint
- [ ] Privacy notice and local healthcare/privacy legal review
- [ ] TLS, secure deployment headers, strict CORS, secret manager
- [ ] Encrypted backups and tested restore procedure
- [ ] Data retention/deletion, incident response and audit review
- [ ] Real clinic-approved content, credentials, fees, policies and consent
- [ ] Notification provider credentials and delivery-status handling, if enabled
- [ ] WCAG 2.2 AA audit, browser/device QA and performance checks
