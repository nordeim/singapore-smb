# Phase 1 Remediation Plan — Audit Log

**Repository**: `nordeim/singapore-smb`

**Scope**: Phase 1 remediation to align the codebase with the latest project design specifications and to make the backend runnable end-to-end (local Docker DB, migrations, seed, tests) with Django-friendly schema choices.

**Notes on format**
- This is an **audit log of concrete file-level changes** (adds/updates) made during Phase 1 remediation.
- Where applicable, each item includes:
  - **What changed**
  - **Why** (design/spec alignment or runtime fix)
  - **Verification** performed

---

## 1) Local Docker DB (Postgres/Redis) + Backend containerization

### 1.1 Added `docker-compose.yml`
- **File**: `docker-compose.yml`
- **Change type**: Added
- **What changed**
  - Added services:
    - `postgres` using `postgres:16-alpine`
    - `redis` using `redis:7.4-alpine`
  - Added:
    - container names (`singapore_smb_postgres`, `singapore_smb_redis`)
    - `env_file: .env.docker` so compose consistently reads repo env
    - port mappings controlled by `.env.docker` (`POSTGRES_PORT`, `REDIS_PORT`)
    - named volumes `postgres_data`, `redis_data`
    - healthchecks for both services
- **Why**
  - Provide a reproducible local dev DB matching the Phase 1 backend stack.
- **Verification**
  - User ran:
    - `docker compose --env-file .env.docker up -d postgres redis`
    - `docker ps` confirmed both containers healthy.

### 1.2 Added backend `Dockerfile` (optional backend image)
- **File**: `Dockerfile`
- **Change type**: Added
- **What changed**
  - Base image: `python:3.12-slim-bookworm`
  - Installed `uv`
  - `uv sync --frozen` using `backend/pyproject.toml` and `backend/uv.lock`
  - Default CMD runs: `uv run python manage.py runserver 0.0.0.0:8000`
- **Why**
  - Provide a minimal container image path for the backend consistent with `uv` and Python 3.12.
- **Verification**
  - Not deployed; added for parity and future CI/local usage.

### 1.3 Updated `.dockerignore` to include Python ignores
- **File**: `.dockerignore`
- **Change type**: Updated
- **What changed**
  - Added Python/Django related ignores:
    - `__pycache__/`, `*.py[cod]`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `.venv/`, `backend/.venv/`, `*.egg-info/`
- **Why**
  - Prevent large or environment-specific Python artifacts from bloating Docker build context.
- **Verification**
  - Manual review of `.dockerignore` content.

### 1.4 Updated `.env.docker` for Django + Postgres + Redis consistency
- **File**: `.env.docker`
- **Change type**: Updated
- **What changed**
  - Standardized Postgres credentials for local use:
    - `POSTGRES_USER=postgres`
    - `POSTGRES_PASSWORD=postgres`
    - `POSTGRES_DB=singapore_smb`
  - Set Django-friendly `DATABASE_URL`:
    - `DATABASE_URL=postgres://postgres:postgres@localhost:5432/singapore_smb`
  - Added DB parameters used by backend settings:
    - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
  - Added Redis parameters:
    - `REDIS_URL=redis://localhost:6379/0`
    - `REDIS_PORT=6379`
- **Why**
  - Ensure docker-compose container env, Django settings, and local CLI usage are aligned.
- **Verification**
  - Migrations and seed executed successfully using:
    - `set -a && source ../.env.docker && set +a && uv run python manage.py migrate`
    - `set -a && source ../.env.docker && set +a && uv run python manage.py seed`

### 1.5 Added helper scripts for migrations + seeding
- **Files**:
  - `docker/scripts/migrate.sh` (Added)
  - `docker/scripts/seed.sh` (Added)
- **What changed**
  - Each script:
    - loads `.env.docker`
    - runs `uv run python manage.py migrate` or `uv run python manage.py seed`
- **Why**
  - Provide repeatable one-liners for local dev.
- **Verification**
  - Core commands succeeded in the same environment.

---

## 2) Django database bootstrap + seed data

### 2.1 Added Django management command `seed`
- **File**: `backend/apps/accounts/management/commands/seed.py`
- **Change type**: Added
- **Supporting files**:
  - `backend/apps/accounts/management/__init__.py` (Added)
  - `backend/apps/accounts/management/commands/__init__.py` (Added)
- **What changed**
  - Implemented `manage.py seed` to create Phase 1 baseline data:
    - a Company (by UEN)
    - default roles via `CompanyService.create_default_roles`
    - an owner user (email/password)
  - Designed to be idempotent:
    - creates company if missing
    - otherwise ensures default roles exist
    - creates owner if missing
- **Why**
  - Provide consistent baseline data for local dev and QA.
- **Verification**
  - `uv run python manage.py seed` succeeded and printed:
    - `Created company 201812345A and owner owner@demo.local`

---

## 3) Admin system check + auth model compatibility

### 3.1 Fixed Django admin inline ambiguity (multiple FKs)
- **File**: `backend/apps/accounts/admin.py`
- **Change type**: Updated
- **What changed**
  - `UserRoleInline` now specifies:
    - `fk_name = 'user'`
- **Why**
  - `accounts.UserRole` has more than one FK to `accounts.User` (`user` and `assigned_by`).
  - Django admin requires `fk_name` to disambiguate.
- **Verification**
  - Previously failing `manage.py migrate` system check:
    - `admin.E202` resolved.
  - `uv run python manage.py migrate` succeeded.

### 3.2 Added minimal Django permission hooks to custom User model
- **File**: `backend/apps/accounts/models.py`
- **Change type**: Updated
- **What changed**
  - Added:
    - `has_perm(self, perm, obj=None)`
    - `has_module_perms(self, app_label)`
  - Both return `True` for `is_superuser`.
- **Why**
  - The custom user model does not include `PermissionsMixin`, but Django admin/auth expects permission hooks.
- **Verification**
  - `manage.py check` and `manage.py migrate` completed without errors.

---

## 4) Celery Beat schedule drift hardening (Phase 1)

### 4.1 Disabled periodic scheduling by default to avoid missing-task errors
- **File**: `backend/config/celery.py`
- **Change type**: Updated
- **What changed**
  - `app.conf.beat_schedule` is now `{}` by default.
  - Beat schedule entries are only populated when:
    - `ENABLE_CELERY_BEAT=1`
- **Why**
  - Phase 1 currently does not include `apps.inventory`, `apps.commerce`, `apps.accounting`, `apps.compliance` task modules.
  - Celery Beat would otherwise enqueue tasks that do not exist.
- **Verification**
  - Import sanity check executed:
    - `uv run python -c "import config.celery; print('celery import OK')"`

---

## 5) django-allauth deprecation remediation

### 5.1 Updated allauth settings keys to modern equivalents
- **File**: `backend/config/settings/base.py`
- **Change type**: Updated
- **What changed**
  - Replaced deprecated settings:
    - removed: `ACCOUNT_AUTHENTICATION_METHOD`, `ACCOUNT_USERNAME_REQUIRED`, `ACCOUNT_EMAIL_REQUIRED`
  - Added modern settings:
    - `ACCOUNT_LOGIN_METHODS = {'email'}`
    - `ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']`
- **Why**
  - Remove runtime warnings and align with current allauth configuration patterns.
- **Verification**
  - `uv run python manage.py check` returned:
    - `System check identified no issues (0 silenced).`

---

## 6) GST rate assumption neutralization

### 6.1 Made GST rate configurable and removed embedded rate from labels
- **File**: `backend/config/settings/base.py`
- **Change type**: Updated
- **What changed**
  - Added:
    - `GST_DEFAULT_RATE = env('GST_DEFAULT_RATE', default=Decimal('0.09'), cast=Decimal)`
  - Set:
    - `GST_RATE = GST_DEFAULT_RATE` (backward-compatible alias)
  - Updated GST code labels:
    - `('SR', 'Standard Rated')` (removed `(9%)`)
    - `('ZR', 'Zero Rated')` (removed `(0%)`)
- **Why**
  - Avoid treating a specific GST percentage as an immutable constant.
  - Preserve Phase 1 operability while allowing environment-driven configuration.
- **Verification**
  - `uv run python manage.py check` succeeded.
  - Full test suite succeeded:
    - `uv run python -m pytest -q` => `61 passed`.

---

## 7) Test reliability fixes (Postgres strictness)

### 7.1 Fixed factories generating invalid phone strings for CharField(max_length=20)
- **File**: `backend/apps/accounts/tests/factories.py`
- **Change type**: Updated
- **What changed**
  - Replaced `factory.Faker('phone_number')` for `CompanyFactory.phone` and `UserFactory.phone` with bounded Singapore-style `+65...` strings within 20 chars.
- **Why**
  - Postgres enforces column size; Faker-generated phone numbers exceeded `VARCHAR(20)`.
  - This caused `django.db.utils.DataError: value too long for type character varying(20)`.
- **Verification**
  - Previously failing tests passed after update.
  - Full suite:
    - `uv run python -m pytest -q` => `61 passed`.

---

## 8) Documentation alignment

### 8.1 Updated backend README to match real workflow and versions
- **File**: `backend/README.md`
- **Change type**: Updated
- **What changed**
  - Updated stated versions:
    - Backend: Django 6.0+ / Python 3.12+
    - Frontend: Next.js 14.2+
    - Redis: 7.4+
  - Updated commands to match real workflow:
    - start DB via docker-compose
    - `uv sync`
    - `uv run python manage.py migrate/seed/runserver`
    - `uv run python -m pytest -q`
- **Why**
  - Ensure docs match the actual Phase 1 dev and QA procedure.
- **Verification**
  - Commands used during remediation match the documented steps.

---

## 9) Schema drift remediation: align `database/schema.sql` with Phase 1 Django migrations

### 9.1 Updated Phase 1 core accounts tables to Django-friendly structure
- **File**: `database/schema.sql`
- **Change type**: Updated
- **Authoritative reference**
  - Django migration: `backend/apps/accounts/migrations/0001_initial.py`
- **What changed** (Phase 1 scope)
  - `core.user_roles`
    - Changed from composite PK `(user_id, role_id)` to:
      - `id UUID PRIMARY KEY ...`
    - Added `CONSTRAINT unique_user_role UNIQUE(user_id, role_id)`
    - Added `created_at`, `updated_at`
    - Set `assigned_by` FK to `ON DELETE SET NULL`
    - Added indexes:
      - `idx_user_roles_user`, `idx_user_roles_role`, `idx_user_roles_assigned_by`
  - `core.roles`
    - Added `updated_at`
    - Added `CONSTRAINT unique_role_per_company UNIQUE(company_id, name)`
    - Added `idx_roles_company`
    - Ensured `company_id` FK uses `ON DELETE CASCADE`
  - `core.users`
    - Ensured `company_id` FK uses `ON DELETE CASCADE`
    - Added `idx_users_deleted_at`
    - Tightened defaults/nullability on booleans/timestamps to match Phase 1 expectations
    - Changed `email` to `VARCHAR(254)` to match Django `EmailField(max_length=254)`
  - `core.companies`
    - Added `idx_companies_deleted_at`
    - Changed `email` to `VARCHAR(254)` to match Django `EmailField(max_length=254)`
    - Tightened defaults/nullability on selected fields to match Phase 1 expectations
- **Why**
  - Align `schema.sql` with Django migration reality for Phase 1 QA/auditing, avoiding schema contradictions.
- **Verification**
  - Confirmed the old composite PK signature is removed:
    - `PRIMARY KEY (user_id, role_id)` no longer exists in `schema.sql`.

---

## 10) End-to-end verification summary (commands executed during remediation)

### 10.1 Docker services
- `docker compose --env-file .env.docker up -d postgres redis`
  - Result: both containers started and were healthy.

### 10.2 Django migrations
- `set -a && source ../.env.docker && set +a && uv run python manage.py migrate`
  - Result: succeeded after fixing admin inline ambiguity.

### 10.3 Seed
- `set -a && source ../.env.docker && set +a && uv run python manage.py seed`
  - Result: created default company + owner user.

### 10.4 System checks
- `set -a && source ../.env.docker && set +a && uv run python manage.py check`
  - Result: `System check identified no issues (0 silenced).`

### 10.5 Tests
- `set -a && source ../.env.docker && set +a && uv run python -m pytest -q`
  - Result: `61 passed`.

---

## 11) File change index (for QA traceability)

### Added files
- `docker-compose.yml`
- `Dockerfile`
- `docker/scripts/migrate.sh`
- `docker/scripts/seed.sh`
- `backend/apps/accounts/management/__init__.py`
- `backend/apps/accounts/management/commands/__init__.py`
- `backend/apps/accounts/management/commands/seed.py`

### Modified files
- `.env.docker`
- `.dockerignore`
- `backend/apps/accounts/admin.py`
- `backend/apps/accounts/models.py`
- `backend/apps/accounts/tests/factories.py`
- `backend/config/celery.py`
- `backend/config/settings/base.py`
- `backend/README.md`
- `database/schema.sql`
