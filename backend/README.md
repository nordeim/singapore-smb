# Singapore SMB E-commerce Platform (Hybrid Architecture)

## Overview
A comprehensive e-commerce and inventory management system designed for Singapore SMBs, featuring:
- **Backend**: Django 6.0+ (Python 3.12+) for financial precision, GST compliance, and admin operations.
- **Frontend**: Next.js 14.2+ (React) for a high-performance, mobile-first PWA storefront.
- **Compliance**: Built-in support for Singapore GST (F5), InvoiceNow (PEPPOL), and PDPA.

## Project Structure
- `backend/`: Django API, Celery workers, and Business Logic.
- `frontend/`: Next.js PWA, Customer Storefront.

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7.4+

### Backend Setup
```bash
docker compose --env-file .env.docker up -d postgres redis

cd backend
uv sync

set -a && source ../.env.docker && set +a
uv run python manage.py migrate
uv run python manage.py seed
uv run python manage.py runserver
```

### Backend Tests
```bash
cd backend
set -a && source ../.env.docker && set +a
uv run python -m pytest -q
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
