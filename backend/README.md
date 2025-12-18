# Singapore SMB E-commerce Platform (Hybrid Architecture)

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
- PostgreSQL 16+
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
