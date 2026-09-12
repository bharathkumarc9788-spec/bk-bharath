# API Documentation

Base URL: `http://127.0.0.1:8002/api`

## Authentication

| Method | Endpoint | Body | Returns |
|--------|----------|------|---------|
| POST | `/auth/login/` | `{username, password}` | `{access, refresh, user}` |
| POST | `/auth/refresh/` | `{refresh}` | `{access}` |
| GET | `/auth/me/` | — | current user + student id |

Protected endpoints use `Authorization: Bearer <access>`.

## Students

| Method | Endpoint | Notes |
|--------|----------|-------|
| GET | `/students/?search=&department=&status=&year=` | search name/register/email/dept/skills/project |
| POST | `/students/` | HR only, auto-links a login user (password `student123`) |
| GET/PUT/PATCH/DELETE | `/students/{id}/` | owners + HR |
| POST | `/students/bulk-upload/` | multipart CSV/XLSX → preview; then `{preview:false, rows:[...]}` to import |

### 360° sections (nested under a student)

`/students/{id}/{section}/` with `GET` / `POST` and `/students/{id}/{section}/{item_id}/` `DELETE`
for: `education`, `skills`, `projects`, `internships`, `certifications`, `achievements`, `activities`.
Plus `/api/goals/`, `/api/feedback/teacher-feedback/`, `/api/feedback/parent-feedback/`.

## Portfolio workflow

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/portfolio/templates/` | list templates |
| POST | `/portfolio/generate/` | `{student_id, template_id?}` → builds snapshot + completion %, saves a version |
| POST | `/portfolio/{id}/submit/` | DRAFT → SUBMITTED (notifies HR) |
| POST | `/portfolio/{id}/start_review/` | → UNDER_REVIEW |
| POST | `/portfolio/{id}/approve/` | → APPROVED |
| POST | `/portfolio/{id}/reject/` | → REJECTED |
| POST | `/portfolio/{id}/revision/` | → REVISION_REQUIRED |
| POST | `/portfolio/{id}/publish/` | APPROVED → PUBLISHED (generates slug + timestamp) |
| GET | `/portfolio/{id}/qr/` | downloadable PNG pointing to public URL |
| GET | `/portfolio/{id}/public_url/` | `{public_url, slug}` |
| GET | `/portfolio/{id}/versions/` `/approvals/` | history |

Every approval step appends a `PortfolioApproval` row (reviewer, status, comments, dates).

## Public (no login)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/portfolio/public/{slug}/` | sanitised public portfolio; increments `views_count` + logs a `PortfolioView` |

## Dashboard & analytics (authenticated)

| Method | Endpoint | Returns |
|--------|----------|---------|
| GET | `/dashboard/` | KPIs (students, portfolios, pending, published, incomplete, views, avg completion), completion bins, department analysis, portfolio status, support list, approval queue, recent activity |
| GET | `/dashboard/data/` | views over 30 days, published by department, avg completion by department, bins, status |

## Notifications

| Method | Endpoint |
|--------|----------|
| GET | `/notifications/` |
| POST | `/notifications/mark_all_read/` |
| DELETE | `/notifications/{id}/` |

## Response shape (non-paginated)

List endpoints return plain JSON arrays (pagination disabled in dev settings).