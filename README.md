# Singapore SMB E-Commerce Platform

[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0+-green.svg?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2+-black.svg?style=flat-square&logo=next.js)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7.4+-DC382D.svg?style=flat-square&logo=redis)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-24+-2496ED.svg?style=flat-square&logo=docker)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Backend_Tests-370%2B_passing-brightgreen?style=flat-square)](backend/apps)
![Phase Status](https://img.shields.io/badge/Phase-7%20%E2%9C%85%20(Frontend%20Complete)-0055FF?style=flat-square)
[![Singapore](https://img.shields.io/badge/Singapore-%F0%9F%87%B8%F0%9F%87%AC-orange?style=flat-square)](https://www.irs.gov.sg/)

✅ **Phase 7 Complete** - Full-stack e-commerce platform ready<br/>
🚀 **Next**: Phase 8 - Testing & Deployment<br/>
🇸🇬 **Built for Singapore** - GST compliance, PayNow, PDPA, InvoiceNow

[📋 Project Documentation](docs/) | [🗺️ Development Roadmap](docs/ROADMAP.md) | [🧩 Project Architecture](Project%20Architecture%20Document.md)

---

## ✨ Overview

A **compliance-first business platform** for Singapore Small and Medium Businesses that integrates e-commerce, inventory management, and automated accounting with Singapore-specific regulatory requirements.

**Phase 7 (Frontend Features) Complete**, this project now provides a full-stack solution with:
- **Backend**: Django 6.0+ REST API (370+ tests passing)
- **Frontend**: Next.js 14.2+ storefront with checkout flow
- **Database**: PostgreSQL 16+ with comprehensive schema

### 🇸🇬 Why Singapore SMBs Need This

Singapore SMBs face unique challenges:
- **Regulatory complexity**: GST filing errors average 3.2 per quarter
- **System fragmentation**: 5-7 disconnected tools for daily operations  
- **Mobile-first customers**: 70% of Singapore shoppers use smartphones
- **Compliance burden**: PDPA, ACRA, and IRAS requirements require specialized handling

Our solution provides:
- ✅ **Financial precision**: DECIMAL arithmetic, no floating-point errors
- ✅ **Multi-tenant isolation**: Company data completely separated via RLS
- ✅ **Singapore compliance**: GST engine, PDPA consent, PEPPOL/InvoiceNow ready
- ✅ **Full e-commerce flow**: Products, cart, checkout with Stripe & PayNow

---

## 🚀 Current Capabilities (Phase 7 Complete)

### ✅ Backend (Phases 1-5)
- **Multi-tenant architecture**: Companies isolated via PostgreSQL Row-Level Security
- **Authentication system**: JWT + django-allauth with email-based login
- **Commerce Domain**: Products, variants, categories, customers, orders
- **Inventory Domain**: Multi-location, Redis locks, reservations, movements
- **Accounting Domain**: Chart of accounts, journal entries, invoices, payments
- **GST Engine**: Historical rates, F5 preparation, PEPPOL fields
- **PDPA Compliance**: Consent tracking, data access requests, audit logging
- **Payment Gateways**: Stripe + HitPay integration
- **Logistics**: NinjaVan + SingPost multi-carrier support

### ✅ Frontend (Phases 6-7)
- **Next.js 14.2+ App Router**: Server and Client components
- **Product Pages**: Listing, detail, search, filters, pagination
- **Shopping Cart**: Add/remove items, quantity controls, GST display
- **Checkout Flow**: Multi-step (Address → Payment → Review)
- **Payment Integration**: Stripe Elements placeholder + PayNow QR
- **Account Pages**: Dashboard, order history, order detail
- **Auth Pages**: Login, registration with PDPA consent
- **UI Components**: Design system with Tailwind CSS 4

---

## 🏗️ Architecture

### Current Phase 1 Architecture
```mermaid
graph TD
    subgraph “Local Development”
        A[Docker Compose] --> B[PostgreSQL 16]
        A --> C[Redis 7.4]
        A --> D[Django 6.0 App]
    end
    
    subgraph “Application Layer”
        D --> E[Core Foundation]
        D --> F[Authentication]
        D --> G[Multi-tenancy]
        D --> H[Compliance Framework]
    end
    
    E --> I[Base Models]
    F --> J[JWT + django-allauth]
    G --> K[Company Isolation]
    H --> L[GST Engine Foundation]
    H --> M[PDPA Consent Framework]
```

### Technology Stack
| **Layer** | **Technology** | **Version** | **Purpose** |
|-----------|----------------|-------------|-------------|
| **Runtime** | Python | 3.12+ | Backend language |
| **Framework** | Django | 6.0+ | Web framework with built-in admin |
| **API** | Django REST Framework | 3.16+ | REST API endpoints |
| **Database** | PostgreSQL | 16+ | Primary data store with RLS |
| **Cache/Queue** | Redis | 7.4+ | Session cache, Celery broker |
| **Auth** | django-allauth + SimpleJWT | - | Authentication system |
| **Container** | Docker | 24+ | Reproducible development environment |
| **Dependency Mgmt** | uv | - | Fast dependency resolver |
| **Testing** | pytest | - | Test runner with factories |

---

## ⚡ Quick Start

### Prerequisites
- Docker 24+
- Python 3.12+ (for direct execution)
- Git

### One-Command Setup
```bash
# Clone repository
git clone https://github.com/nordeim/singapore-smb.git
cd singapore-smb

# Start development environment
docker compose --env-file .env.docker up -d postgres redis

# Install Python dependencies
uv sync --frozen

# Run migrations and seed data
./docker/scripts/migrate.sh
./docker/scripts/seed.sh

# Start development server
uv run python manage.py runserver 0.0.0.0:8000
```

### Access the Application
- **API Root**: http://localhost:8000/api/v1/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/
- **Default Credentials**: `owner@demo.local` / `ownerpassword123`

---

## 📦 Project Structure

```
singapore-smb/
├── backend/                    # Django application (Phases 1-5 complete)
│   ├── apps/
│   │   ├── accounts/          # ✅ Authentication, users, RBAC
│   │   ├── companies/         # ✅ Multi-tenancy foundation
│   │   ├── commerce/          # ✅ Products, orders, customers
│   │   ├── inventory/         # ✅ Stock management, reservations
│   │   ├── accounting/        # ✅ Chart of accounts, journals
│   │   ├── compliance/        # ✅ GST engine, PDPA, audit logs
│   │   ├── payments/          # ✅ Stripe, HitPay integration
│   │   └── integrations/      # ✅ Logistics (NinjaVan, SingPost)
│   ├── config/                # ✅ Django settings, URLs, Celery
│   ├── core/                  # ✅ Base models, permissions, exceptions
│   └── tests/                 # ✅ 370+ passing tests
├── frontend/                   # Next.js application (Phases 6-7 complete)
│   ├── src/
│   │   ├── app/               # ✅ App Router pages (12 routes)
│   │   ├── components/        # ✅ UI components, layouts
│   │   └── lib/               # ✅ API client, hooks, utilities
│   └── package.json           # React Query, Tailwind, Stripe
├── database/
│   └── schema.sql             # ✅ PostgreSQL 16 schema
├── docker/
│   └── docker-compose.yml     # ✅ Local DB containers
└── docs/                       # Project documentation
```

---

## 🧪 Testing

### Running Tests
```bash
# Run all tests
uv run pytest -q

# Run with coverage report
uv run pytest --cov=apps --cov-report=html

# Run specific test file
uv run pytest apps/accounts/tests/test_models.py -v
```

### Current Test Coverage
| **Module** | **Status** | **Tests** | **Coverage** |
|------------|------------|-----------|--------------|
| Accounts | ✅ Complete | 61 tests | 85%+ |
| Core Models | ✅ Complete | Comprehensive | 90%+ |
| Authentication | ✅ Complete | JWT + allauth | 85%+ |
| Multi-tenancy | ✅ Complete | RLS policies | 90%+ |
| GST Engine | ✅ Foundation | Historical rates | 80%+ |

**All tests pass** with PostgreSQL 16 strict data validation and Redis integration.

---

## 🗺️ Development Roadmap

| **Phase** | **Duration** | **Focus** | **Status** | **Key Deliverables** |
|-----------|--------------|-----------|------------|---------------------|
| **Phase 1** | Weeks 1-3 | Foundation | ✅ **COMPLETE** | Django setup, auth, multi-tenancy |
| **Phase 2** | Weeks 4-6 | Commerce Domain | ✅ **COMPLETE** | Products, categories, customers, orders |
| **Phase 3** | Weeks 7-9 | Inventory Domain | ✅ **COMPLETE** | Locations, stock levels, movements, reservations |
| **Phase 4** | Weeks 10-12 | Accounting Domain | ✅ **COMPLETE** | Chart of accounts, journals, invoices, GST engine |
| **Phase 5** | Weeks 13-15 | Compliance & Integrations | ✅ **COMPLETE** | PDPA, audit logs, Stripe/HitPay, NinjaVan/SingPost |
| **Phase 6** | Weeks 16-18 | Frontend Foundation | ✅ **COMPLETE** | Next.js setup, UI components, API client |
| **Phase 7** | Weeks 19-22 | Frontend Features | ✅ **COMPLETE** | Storefront, cart, checkout, account pages |
| **Phase 8** | Weeks 23-28 | Testing & Deployment | ⏳ Planned | E2E tests, security audit, production launch |

**Current Focus**: Phase 8 - Testing & Deployment. See [ROADMAP.md](docs/ROADMAP.md) for detailed sprint planning.

---

## 🔐 Security & Compliance

### Phase 1 Security Foundations
- **Row-Level Security**: PostgreSQL RLS policies prevent cross-company data access
- **JWT Authentication**: Short-lived tokens with refresh mechanism
- **Input Validation**: Strict field validation including UEN format checks
- **Audit Logging**: All data changes tracked with user context
- **Security Headers**: CSP-ready middleware configuration
- **Secrets Management**: Environment variables for sensitive configuration

### Singapore Compliance Foundation
- **GST Rate History**: Complete Singapore GST history from 1994 (3%) to 2024 (9%)
- **UEN Validation**: Singapore Unique Entity Number format validation
- **PDPA Consent Framework**: Explicit consent tracking with timestamps
- **Financial Precision**: DECIMAL arithmetic for all monetary calculations
- **Data Retention**: Framework for automated data purging per policy

---

## 🤝 Contributing

We welcome contributions that align with our **meticulous approach** to development. Before contributing:

### Contribution Guidelines
1. **Phase Alignment**: Focus on Phase 2 (Commerce Domain) features
2. **Quality Standards**: 
   - 100% test coverage for new functionality
   - Type hints for all Python code
   - Django 6.0+ best practices
   - Financial precision (no floats for money)
3. **Singapore Context**: Understand local compliance requirements
4. **Architecture Compliance**: Follow modular design patterns

### Development Workflow
```bash
# 1. Create feature branch
git checkout -b feature/amazing-feature

# 2. Install pre-commit hooks
pip install pre-commit
pre-commit install

# 3. Make changes with tests
# 4. Run tests before commit
uv run pytest

# 5. Commit with conventional commits
git commit -m "feat(commerce): add product catalog with variants"

# 6. Push and create PR
```

### Code Review Process
All PRs require:
- ✅ Passing tests (61+ existing tests must remain green)
- ✅ Code coverage maintained or improved
- ✅ Type hints complete
- ✅ Documentation updated
- ✅ Singapore compliance requirements met

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for detailed guidelines.

---

## 📚 Documentation

### Core Documentation
- [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) - Detailed system design decisions
- [**PHASE1_STATUS.md**](docs/PHASE1_STATUS.md) - ✅ Phase 1 completion report with verification
- [**ROADMAP.md**](docs/ROADMAP.md) - Complete implementation roadmap with timelines
- [**SCHEMA.md**](docs/SCHEMA.md) - Database schema design with PostgreSQL 16 features

### Developer Guides
- [**SETUP.md**](docs/SETUP.md) - Detailed environment setup
- [**TESTING.md**](docs/TESTING.md) - Testing strategy and coverage requirements
- [**COMPLIANCE.md**](docs/COMPLIANCE.md) - Singapore regulatory requirements
- [**DEPLOYMENT.md**](docs/DEPLOYMENT.md) - Production deployment strategy

---

## 🙏 Acknowledgments

This project builds upon the excellent work of:
- **Django Software Foundation** - For the robust, secure foundation
- **Singapore Government Digital Services** - For open APIs and documentation
- **Open Source Community** - For tools like PostgreSQL, Redis, and Celery
- **PSG Grant Framework** - For supporting Singapore SMB digital transformation

Built with ❤️ in Singapore 🇸🇬 by the team at Nordeim.

---

## 📧 Contact & Support

For development questions:
- **GitHub Issues**: [Create an issue](https://github.com/nordeim/singapore-smb/issues)
- **Discussions**: [Join the conversation](https://github.com/nordeim/singapore-smb/discussions)

For business inquiries:
- **Email**: hello@nordeim.com
- **Website**: https://nordeim.com

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Nordeim Pte Ltd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

**Ready to build the future of Singapore SMB commerce?** 🚀

[![Star on GitHub](https://img.shields.io/github/stars/nordeim/singapore-smb?style=social)](https://github.com/nordeim/singapore-smb)
[![Fork on GitHub](https://img.shields.io/github/forks/nordeim/singapore-smb?style=social)](https://github.com/nordeim/singapore-smb)
[![Watch on GitHub](https://img.shields.io/github/watchers/nordeim/singapore-smb?style=social)](https://github.com/nordeim/singapore-smb)
