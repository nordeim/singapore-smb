import os

# Define file contents
gitignore_content = """# General
.DS_Store
.vscode/
.idea/
*.log
*.sqlite3

# Python / Django
__pycache__/
*.py[cod]
*$py.class
backend/venv/
backend/.env
backend/staticfiles/
backend/media/
backend/celerybeat-schedule
backend/celerybeat.pid

# Node / Next.js
frontend/node_modules/
frontend/.next/
frontend/out/
frontend/.env*.local
frontend/npm-debug.log*
frontend/yarn-debug.log*
frontend/yarn-error.log*
frontend/.pnpm-debug.log*

# Docker
.docker_data/
"""

backend_pyproject_content = """[project]
name = "singapore-smb-backend"
version = "0.1.0"
description = "Django backend for Singapore SMB E-commerce Platform"
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "Django>=5.2,<6.0",
    "djangorestframework>=3.16.0",
    "django-cors-headers>=4.3.1",
    "django-environ>=0.11.2",
    "django-allauth>=0.61.1",
    "celery>=5.3.6",
    "redis>=5.0.1",
    "psycopg[binary]>=3.1.18",
    "gunicorn>=21.2.0",
    "Pillow>=10.2.0",
    "drf-spectacular>=0.27.1",  # For API Documentation
    "stripe>=8.4.0",            # Payment Processing
    "weasyprint>=61.0",         # Invoice PDF Generation
    "python-jose[cryptography]>=3.3.0", # JWT Handling
    "sentry-sdk>=1.40.0"        # Error Monitoring
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-django>=4.8.0",
    "black>=24.2.0",
    "isort>=5.13.2",
    "flake8>=7.0.0",
    "factory-boy>=3.3.0"
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["config", "apps"]
"""

frontend_package_json_content = """{
  "name": "singapore-smb-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "next": "16.0.10",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "axios": "^1.7.9",
    "@tanstack/react-query": "^5.66.0",
    "zod": "^3.24.1",
    "react-hook-form": "^7.54.2",
    "lucide-react": "^0.475.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^3.0.1",
    "tailwindcss": "^4.0.0",
    "@radix-ui/react-dialog": "^1.1.6",
    "@radix-ui/react-dropdown-menu": "^2.1.6",
    "@radix-ui/react-label": "^2.1.2",
    "@radix-ui/react-popover": "^1.1.6",
    "@radix-ui/react-select": "^2.1.6",
    "@radix-ui/react-separator": "^1.1.2",
    "@radix-ui/react-slot": "^1.1.2",
    "@radix-ui/react-tabs": "^1.1.3",
    "@radix-ui/react-tooltip": "^1.1.8",
    "date-fns": "^4.1.0",
    "react-day-picker": "^9.5.1"
  },
  "devDependencies": {
    "@types/node": "^22.13.1",
    "@types/react": "^19.0.8",
    "@types/react-dom": "^19.0.3",
    "@tailwindcss/postcss": "^4.0.0",
    "postcss": "^8.5.1",
    "typescript": "^5.7.3",
    "eslint": "^9.19.0",
    "eslint-config-next": "16.0.10",
    "prettier": "^3.4.2",
    "prettier-plugin-tailwindcss": "^0.6.11"
  }
}
"""

readme_content = """# Singapore SMB E-commerce Platform (Hybrid Architecture)

## Overview
A comprehensive e-commerce and inventory management system designed for Singapore SMBs, featuring:
- **Backend**: Django 5.2+ (Python) for financial precision, GST compliance, and admin operations.
- **Frontend**: Next.js 16+ (React) for a high-performance, mobile-first PWA storefront.
- **Compliance**: Built-in support for Singapore GST (F5), InvoiceNow (PEPPOL), and PDPA.

## Project Structure
- `backend/`: Django API, Celery workers, and Business Logic.
- `frontend/`: Next.js PWA, Customer Storefront.

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+

### Backend Setup
```bash
cd backend
pip install -e .
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
"""

# Create directory structure
os.makedirs("backend", exist_ok=True)
os.makedirs("frontend", exist_ok=True)

# Write files
with open(".gitignore", "w") as f:
    f.write(gitignore_content)

with open("backend/pyproject.toml", "w") as f:
    f.write(backend_pyproject_content)

with open("frontend/package.json", "w") as f:
    f.write(frontend_package_json_content)

with open("README.md", "w") as f:
    f.write(readme_content)

print("Scaffolding completed: .gitignore, backend/pyproject.toml, frontend/package.json, README.md created.")
