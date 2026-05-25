# SRTAPP — College Management System

Production-oriented college stack: Django 5.x, Next.js, and Expo React Native.

## Architecture

- **Backend**: Django + DRF + PostgreSQL + Redis + Celery (+ Celery Beat)
- **Frontend**: Next.js (App Router)
- **Mobile**: Expo Router + React Native
- **Ops**: Docker Compose + Nginx reverse proxy

## Prerequisites

- Docker Engine with Compose v2 (`docker compose`)
- Node.js 20+ (optional, for running web/mobile outside Docker)
- Python 3.12+ (optional, for running the API locally)

## Run everything locally (recommended hybrid)

Infrastructure (PostgreSQL + Redis + MinIO + Meilisearch) stays in Docker; you run Django, Next.js, and Expo on the host — fast reloads.

1. **Dependencies in Docker**

   ```bash
   bash scripts/start-local-deps.sh
   ```

   Optional: `cp .env.example .env` at repo root if you customize compose passwords.

2. **Backend `.env`** — copy template and align with Compose defaults (`DB_PASSWORD=srtapp_pass`, Redis URLs with `:redis_pass@127.0.0.1:6379`; see comments in `backend/.env.example`).

   ```bash
   cd backend && cp -n .env.example .env
   ```

   Activate venv, migrate, API:

   ```bash
   source venv/bin/activate
   pip install -r requirements/dev.txt   # first time only
   python manage.py migrate
   python manage.py runserver 0.0.0.0:8000
   ```

   API: http://localhost:8000/api/v1 — Admin: http://localhost:8000/manage-portal/

3. **Frontend**

   ```bash
   cd frontend && npm install
   cp -n .env.local.example .env.local
   npm run dev
   ```

   App: http://localhost:3000

4. **Mobile (Expo)**

   ```bash
   cd mobile && npm install && npx expo install --fix
   cp -n .env.example .env
   npx expo start
   ```

   Use `http://10.0.2.2:8000/api/v1` as `EXPO_PUBLIC_API_URL` on Android emulator; device on LAN needs your PC’s LAN IP instead of `127.0.0.1`.

**Celery (optional)** — async tasks need a worker:

```bash
cd backend && source venv/bin/activate && celery -A srtapp worker -l info
```

**Compose v2**: use `docker compose` (plugin). The legacy Python `docker-compose` 1.x can fail when recreating containers with `KeyError: 'ContainerConfig'`. If `sudo apt install docker-compose-plugin` is missing, run **`bash scripts/install-docker-compose-v2.sh`** once (downloads the official Compose v2 binary into `~/.docker/cli-plugins/`), or add Docker’s APT repo ([install guide](https://docs.docker.com/engine/install/ubuntu/)). Confirm with `docker compose version`.

**Container name conflict** after switching from Compose v1: run **`bash scripts/reset-local-deps.sh`** then **`bash scripts/start-local-deps.sh`** again.

**Migration error `InconsistentMigrationHistory` (admin before accounts, etc.)**: local DB history is out of sync — stop `runserver`, then **`bash scripts/reset_local_postgres_db.sh`**, then **`python manage.py migrate`** (dev only; erases `srtapp_db` data).

## Quick start (Docker)

```bash
cd srtapp
cp .env.example .env   # edit secrets before sharing environments
docker compose up --build -d
```

### URLs

| Service | URL |
|--------|-----|
| Web app | http://localhost:3000 |
| API | http://localhost:8000/api/v1 |
| Via Nginx | http://localhost (proxies Next + `/api/`, `/manage-portal/`, `/static/`, `/media/`) |
| Optional API host | http://api.localhost |
| Django admin | http://localhost:8000/manage-portal/ |
| MinIO console | http://localhost:9001 |
| Meilisearch | http://localhost:7700 |

### Superuser

```bash
docker compose exec backend python manage.py createsuperuser
```

### Mobile (local)

```bash
cd mobile
npm install
npx expo start
```

## Project layout

```
srtapp/
├── backend/           # Django project
├── frontend/          # Next.js app
├── mobile/            # Expo app
├── nginx/             # nginx.conf (+ optional tls under nginx/ssl/)
├── docker-compose.yml
└── .env.example
```

## Design tokens (web/mobile)

Institutional palette: primary **#1A1A2E**, accent **#E94560**, gold **#F5A623**, success **#10B981** (no primary blues).

## Roles (high level)

Super admin, college admin, HoD, teacher, student, parent, accountant, librarian, security — enforced in the API and UI.

## Testing

```bash
# Backend
cd backend && pytest

# Frontend (when a test script exists)
cd frontend && npm test

# Mobile typecheck
cd mobile && npm run lint
```

## License

Proprietary — all rights reserved.
