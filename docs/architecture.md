# Architecture

## System Flow

```
STUDENT DATA → VALIDATION → SQLite/PostgreSQL → STUDENT PROFILE → 360° COLLECTION
→ PROFILE COMPLETION % → TEMPLATE SELECTION → PORTFOLIO GENERATION → PREVIEW
→ STUDENT EDIT → HR/TEACHER REVIEW → APPROVAL → PUBLISH → PUBLIC URL + QR CODE
→ RECRUITER VIEW → ANALYTICS
```

## Backend (Python + Django REST Framework)

```
Users ─ HR / Student / Teacher / Parent
        └── Django views (server-rendered Python frontend, `web` app)
        └── REST API under /api/ (models → serializers → viewsets → JSON)
Student ─ Education, Skill, Project, Internship, Certification, Achievement,
          Activity, TeacherFeedback, ParentFeedback, StudentGoal
Portfolio ─ Template, Portfolio (snapshot JSON), PortfolioVersion,
            PortfolioApproval (history), PortfolioView (analytics)
```

Key service modules:

| File | Responsibility |
|------|----------------|
| `portfolio/services.py` | portfolio data snapshot, generation, approval workflow, publish, public data, view tracking |
| `common/completion.py` | per-section + overall profile completion (computed from real records, not hard-coded) |
| `analytics/views.py` | dashboard KPIs, completion bins, department analysis, status distribution, support list |
| `audit/models.py` | action log + `log_action()` helper |
| `web/views.py` | server-rendered Python frontend (login, dashboard, students, generator, approval, public pages) |

## Frontend
- **Primary:** server-rendered Django templates in `backend/web/templates/web/` (no separate frontend build needed).
- **Alternative (React API client):** `frontend/` — a Vite + React app that consumes the same `/api` endpoints (dev server proxies to `http://127.0.0.1:8002`).

## Security & Roles
- JWT (simplejwt) for API; session auth for the rendered frontend.
- Per-role queryset scoping: students/parents only see their own records; teachers see assigned students; HR sees everything.
- `IsHROrReadOnly`, `IsOwnerOrHR`, `IsOwnerOrHROrTeacher` permission classes.
- Audit logging on create/delete and every portfolio review action.