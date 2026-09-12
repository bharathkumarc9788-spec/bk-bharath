# Student Portfolio Automation System

A **pure-Python** student portfolio automation platform — 360° digital portfolios
with profile completion tracking, portfolio generation, an approval/publish
workflow, public portfolio pages and QR codes. The whole website is rendered by
Django (Python) with no separate frontend build step.

## Architecture

- **Backend & Frontend (Python):** `backend/` — a single Django project.
  The frontend is **server-rendered Python** (Django views + templates in the
  `web` app), served directly by Django at `http://127.0.0.1:8002/`.
  There is no separate JavaScript frontend. (A React/Vite API client that
  previously lived in `frontend/` is preserved for reference under
  `archive/frontend-react/`.)

| Layer        | Location                       |
|--------------|--------------------------------|
| Python views | `backend/web/views.py`         |
| URL routes   | `backend/web/urls.py`          |
| Templates    | `backend/web/templates/web/`   |
| Styles       | `backend/web/static/web/`      |
| Django admin | `/admin/` (HR superuser)       |
| REST API     | `/api/` (backend apps)         |

## Run it

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed            # demo users + students + portfolios
python manage.py runserver 8002  # → http://127.0.0.1:8002 (8000/8001 may be taken on this machine)
```

Open <http://127.0.0.1:8002> and sign in with a demo account:

- **HR Admin** — `admin / admin123`
- **Teacher** — `teacher / teacher123`
- **Parent** — `parent / parent123`

## Environment variables (`.env`)

See `.env.example`. `FRONTEND_URL` defaults to `http://127.0.0.1:8002` — the
Python frontend is served by Django itself and this value is used for public
portfolio URLs and the QR-code generator.

### Student demo login

Each seeded student has a login account: **username = student email**,
**password = `student123`** (e.g. `priya@college.edu / student123`).

## Key features

- Premium, responsive UI (pure CSS — gradients, glassmorphism, animations; no JS)
- Login / logout / role-based navigation (HR, STUDENT, TEACHER, PARENT)
- Dashboard with KPIs + server-computed charts (pure CSS bars, no JS)
- Student CRUD, search/filter, 360-degree profile with 10 sections
- Bulk CSV/XLSX upload with preview + import report
- Portfolio generator, templates, approval queue, publish + public URL + QR
- Views analytics, notifications