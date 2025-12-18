# COMPLETE REPLACEMENT PRD
## Integrated E-Commerce Platform for Singapore SMBs
### Version 1.0 - Synthesized from Nex-N1, Opus, and Qwen PRDs

---

# DOCUMENT CONTROL

**Document Version:** 1.0  
**Document Status:** Final - Ready for Implementation  
**Last Updated:** December 18, 2025  
**Classification:** Internal - Project Team & Stakeholders  
**Supersedes:** Nex-N1 PRD, Opus-Revised-PRD-2, Qwen-Revised-PRD  

**Approval Signatures:**
- [ ] Project Sponsor
- [ ] Technical Lead
- [ ] Compliance Officer
- [ ] Project Manager

---

# TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Project Overview & Business Context](#2-project-overview--business-context)
3. [User Personas & Success Metrics](#3-user-personas--success-metrics)
4. [System Architecture & Technical Design](#4-system-architecture--technical-design)
5. [Database Schema](#5-database-schema)
6. [API Specifications](#6-api-specifications)
7. [Frontend Specifications](#7-frontend-specifications)
8. [Singapore Compliance Framework](#8-singapore-compliance-framework)
9. [Integration Requirements](#9-integration-requirements)
10. [Security Implementation](#10-security-implementation)
11. [Infrastructure & Operations](#11-infrastructure--operations)
12. [Implementation Roadmap](#12-implementation-roadmap)
13. [Risk Management](#13-risk-management)
14. [Quality Assurance](#14-quality-assurance)
15. [Appendices](#15-appendices)

---

# 1. EXECUTIVE SUMMARY

## 1.1 Project Overview

This document specifies requirements for a **comprehensive e-commerce platform** designed specifically for Singapore small and medium businesses (SMBs), integrating online storefront, backend order management, accounting automation, and regulatory compliance into a single unified system.

## 1.2 Business Problem

Singapore SMBs face significant challenges in digital commerce:

- **Manual Processes:** 60-80% of order processing and accounting is manual
- **Compliance Burden:** GST F5 filing, PDPA requirements, industry licensing require specialized knowledge
- **Multi-Channel Complexity:** Managing inventory across online store, Shopee, Lazada creates race conditions
- **Cash Flow Gaps:** Average 7-12 days from order to cash receipt
- **Regulatory Penalties:** GST errors result in S$5K-S$100K annual penalties per business

## 1.3 Proposed Solution

A **unified e-commerce platform** combining:

✅ **Django Backend** with PostgreSQL for accounting-grade decimal precision  
✅ **Next.js Storefront** with PWA capabilities for mobile-first experience  
✅ **Singapore Compliance Engine** automating GST, PDPA, PEPPOL, industry licenses  
✅ **Multi-Channel Sync** with Redis-based inventory locking  
✅ **Automated Accounting** with journal entry generation and F5 return preparation  

## 1.4 Expected Business Value (Quantified ROI)

| Metric | Current State | Target State | Annual Value |
|--------|--------------|--------------|--------------|
| **Data Entry Time** | 12 hours/week | 4.8 hours/week | **S$38,400 savings** |
| **Order Processing Speed** | 2-3 days | 4-8 hours | **75% faster** |
| **Inventory Accuracy** | 92-95% | 99.5% | **S$15K stockout avoidance** |
| **Checkout Completion** | 32% (industry avg) | 65% | **S$180K revenue impact** |
| **GST Penalty Avoidance** | S$5K-60K/year | Zero penalties | **S$60K direct savings** |
| **Cash Conversion Cycle** | 10-14 days | 5-7 days | **S$120K working capital improvement** |

**Total 5-Year NPV:** S$4.2 million (average SMB with S$2M annual revenue)

## 1.5 Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend** | Django 5.x + Django REST Framework | Decimal precision, admin panel, ORM integrity |
| **Database** | PostgreSQL 15.x | ACID compliance, DECIMAL type, strong consistency |
| **Frontend** | Next.js 14 + React 18 + TypeScript | SSR/SSG for SEO, PWA capabilities, mobile-first |
| **Cache & Sessions** | Redis 7.x | Inventory locks, session management, rate limiting |
| **Background Jobs** | Celery + Redis | Async processing (invoices, marketplace sync) |
| **Infrastructure (MVP)** | AWS ECS Fargate | Lite Mode: Low overhead, auto-scaling |
| **Infrastructure (Scale)** | AWS EKS 1.28+ | Enterprise: Upgrade at 1,000 orders/day |
| **Payment Gateway** | Stripe + HitPay | Multi-gateway for redundancy |
| **Logistics** | Ninja Van API | Singapore-specific fulfillment |

## 1.6 Implementation Timeline

**Total Duration:** 28 weeks (not 24) - Adjusted for integration complexity

- **Phase 1:** Foundation (Weeks 1-6) - Authentication, core models, admin
- **Phase 2:** Compliance Core (Weeks 7-10) - GST, PDPA, accounting engine
- **Phase 3:** E-Commerce Backend (Weeks 11-16) - Cart, checkout, payments
- **Phase 4:** Next.js Frontend (Weeks 17-22) - Storefront, PWA, mobile UX
- **Phase 5:** Integration & Launch (Weeks 23-28) - Marketplace sync, testing, deployment

---

# 2. PROJECT OVERVIEW & BUSINESS CONTEXT

## 2.1 Business Objectives

**Primary Goal:** Enable Singapore SMBs to compete effectively in digital commerce while maintaining full regulatory compliance with minimal overhead.

**Specific Objectives:**

1. **Revenue Growth:** Increase online sales by 65% through improved checkout completion and mobile experience
2. **Operational Efficiency:** Reduce manual order processing from 12 hours/week to <5 hours/week
3. **Compliance Automation:** Eliminate GST filing errors, automate F5 returns, maintain PDPA compliance
4. **Multi-Channel Sync:** Seamlessly manage inventory across e-commerce site, Shopee, Lazada without overselling
5. **Cash Flow Optimization:** Reduce cash conversion cycle from 10-14 days to 5-7 days

## 2.2 Target Market

**Primary:** Singapore SMBs with S$500K - S$10M annual revenue in:
- Food & Beverage (SFA licensed)
- Health & Beauty (HSA regulated)
- Retail & Consumer Goods
- Wholesale Distribution
- B2B Services

**Secondary:** Expanding to Malaysia, Indonesia markets within 18 months.

## 2.3 Key Success Metrics

| Category | Metric | Baseline | Target | Timeline |
|----------|-------|----------|--------|----------|
| **Revenue** | Monthly online sales | S$50K | S$150K | Month 6 |
| **Efficiency** | Order processing time | 2-3 days | 4-8 hours | Month 3 |
| **Accuracy** | Inventory accuracy | 92% | 99.5% | Month 4 |
| **Compliance** | GST F5 filing errors | 8-12/month | 0 | Immediately |
| **Customer** | Checkout completion rate | 32% | 65% | Month 6 |
| **Technical** | Page load speed (mobile) | 4.2s | <2.0s | Month 4 |
| **Operational** | Cash conversion cycle | 10-14 days | 5-7 days | Month 6 |

## 2.4 Scope & Boundaries

### In Scope

✅ Complete e-commerce platform (backend + frontend)  
✅ Multi-channel marketplace synchronization (Shopee, Lazada, Qoo10)  
✅ Singapore compliance automation (GST, PDPA, PEPPOL, industry licenses)  
✅ B2B wholesale tier with credit management  
✅ Multi-currency support (SGD, USD, MYR, IDR, CNY)  
✅ PWA mobile experience with offline capability  
✅ Automated accounting & journal entries  
✅ API-first architecture for future integrations  
✅ Admin dashboard for internal operations  
✅ Customer self-service portal  

### Out of Scope

❌ Mobile native apps (iOS/Android) - PWA provides equivalent functionality  
❌ Custom hardware/POS terminals - Focus on web-based solution  
❌ Advanced AI/ML personalization - Future Phase 6 consideration  
❌ Cryptocurrency payments - Regulatory uncertainty  
❌ Multi-tenant SaaS architecture - Single-tenant for security (upgradeable)  
❌ Complex supply chain logistics - Integrate with Ninja Van, not custom build  
❌ Advanced BI/analytics - Basic reporting + export to Excel  

---

# 3. USER PERSONAS & SUCCESS METRICS

## 3.1 Primary Persona: SMB Owner "Sarah Chen"

**Demographics:**
- Age: 35-55
- Role: Founder/Owner, S$2M annual revenue F&B business
- Tech Comfort: Moderate (uses WhatsApp, Excel, basic website)
- Pain Points: Manual order processing, GST filing stress, inventory sync issues

**Goals:**
- Reduce administrative workload from 20 hours/week to <10 hours/week
- Eliminate GST penalties (paid S$12K last year for late filing)
- Expand to online sales without hiring additional staff
- Maintain SFA compliance (food shop license, halal certification)

**Success Metrics for Sarah:**
```yaml
Success Indicators:
  - Time Saved: < 10 hours/week on admin tasks
  - Penalty Avoidance: Zero GST penalties (S$12K savings)
  - Revenue Growth: 65% increase in online sales
  - Compliance Confidence: 100% automated F5 filing
  - Work-Life Balance: Dashboard shows everything on track
```

### Primary User Journey: Sarah Processes Daily Orders

**Current Process (Painful):**
```
1. 8:00 AM - Check email for 15-20 new orders → 30 min
2. 9:00 AM - Manually enter orders into Excel → 45 min
3. 10:00 AM - Check inventory, identify 3 backorders → 20 min
4. 10:30 AM - Contact suppliers for backorder stock → 30 min
5. 11:00 AM - Update inventory spreadsheet → 15 min
6. 2:00 PM - Generate invoices, send to customers → 60 min
7. 3:00 PM - Update accounting software → 30 min
Total: 3.5 hours/day × 6 days = 21 hours/week ❌
```

**Proposed Process (Automated):**
```
1. 8:00 AM - Check dashboard: 18 new orders, 3 pending approval → 5 min
2. 8:05 AM - Approve 3 high-value orders (>S$5K) → 3 min
3. 8:08 AM - System automatically:
   - Reserves inventory (prevents overselling)
   - Generates invoices with GST
   - Submits InvoiceNow for B2B customers
   - Updates accounting system
   - Syncs with Shopee/Lazada
   - Sends notifications to customers
4. 9:00 AM - Focus on business growth, not admin ← 15 hours/week saved ✅
```

## 3.2 Persona: Finance Manager "David Wong"

**Demographics:**
- Age: 30-45
- Role: Finance Manager, handles accounting, GST, payroll
- Tech Comfort: High (Excel advanced, accounting software)
- Pain Points: Manual journal entries, GST calculation errors, month-end stress

**Goals:**
- Automate journal entry creation (currently 200 manual entries/month)
- Eliminate GST calculation errors (5-8 errors per F5 filing)
- Reduce month-end closing from 5 days to 1 day
- Maintain audit trail for IRAS compliance

**Success Metrics for David:**
```yaml
Success Indicators:
  - Journal Entry Automation: > 95% automated (vs. 0% now)
  - GST Accuracy: Zero calculation errors in F5 returns
  - Closing Time: 1 day vs. 5 days currently
  - Audit Readiness: Always audit-ready (real-time reports)
  - Stress Level: Month-end is uneventful
```

## 3.3 Persona: Operations Manager "Priya Sharma"

**Demographics:**
- Age: 25-40
- Role: Operations Manager, inventory, fulfillment, logistics
- Tech Comfort: Moderate-High (uses multiple systems)
- Pain Points: Inventory sync issues, overselling, manual fulfillment

**Goals:**
- Prevent overselling across online store + marketplaces
- Automate fulfillment workflow (pick lists, shipping labels)
- Track inventory across 3 locations (warehouse + 2 retail stores)
- Receive automated reorder alerts

**Success Metrics for Priya:**
```yaml
Success Indicators:
  - Oversell Prevention: < 0.1% oversell rate (vs. 3% now)
  - Fulfillment Speed: Same-day fulfillment for 2 PM orders
  - Inventory Accuracy: 99.5% accuracy (vs. 92% now)
  - Reorder Alerts: 7-10 days before stockout
  - Location Tracking: Real-time multi-location visibility
```

## 3.4 Persona: Customer "Emma Tan" (Needs WCAG 2.1 AA Compliance)

**Demographics:**
- Age: 25-40
- Profile: Busy professional, shops via mobile, accessibility needs
- Tech Comfort: High (expects app-like experience)
- Pain Points: Slow mobile sites, complex checkout, can't save cart

**Goals:**
- Fast mobile browsing (expects <2 seconds loading)
- Simple 3-step checkout (not 8-step)
- Save cart across devices (logged in or not)
- Track orders in real-time
- Receive push notifications

**Accessibility Requirements (WCAG 2.1 AA):**
```yaml
Accessibility Standards:
  - Screen Reader Support: Full NVDA/JAWS compatibility
  - Keyboard Navigation: Complete keyboard-only operation
  - Color Contrast: 4.5:1 minimum for text
  - Font Size: Adjustable to 200% without breaking layout
  - Alt Text: All images have descriptive alt text
  - Form Labels: All input fields properly labeled
  - Error Messages: Clear, descriptive, and programmatically associated
  - Focus Management: Visible focus indicators throughout
```

**Success Metrics for Emma:**
```yaml
Success Indicators:
  - Mobile Page Load: < 2.0 seconds (mobile 4G)
  - Checkout Completion: Single-session checkout
  - Cart Persistence: Cart saved across devices/browsers
  - Order Tracking: Real-time SMS/WhatsApp updates
  - PWA Installation: Can "install" app to home screen
```

---

# 4. SYSTEM ARCHITECTURE & TECHNICAL DESIGN

## 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Web       │  │   Mobile    │  │   Admin     │            │
│  │  Browser    │  │   PWA       │  │  Django     │            │
│  │  (Next.js)  │  │  (Next.js)  │  │   Admin     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│         │                 │                 │                  │
│         └─────────────────┴─────────────────┘                  │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │ HTTPS/REST API
┌────────────────────────────┼────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │          Django 5.x + Django REST Framework              │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │ │
│  │  │  Auth    │  │  Order   │  │ Payment  │  │  GST    │ │ │
│  │  │ Service  │  │ Service  │  │ Service  │  │ Engine  │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │ │
│  │  │ Inventory│  │ Marketplace│ │ PDPA    │  │ Invoice │ │ │
│  │  │ Service  │  │ Sync      │  │ Service │  │ Now API │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ PostgreSQL  │  │    Redis    │  │   Celery    │            │
│  │  15.x       │  │  7.x        │  │   (Jobs)    │            │
│  │  (Primary)  │  │  (Cache)    │  │             │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│         │                                                        │
│         └──────────────────────────────────────────────────────┘
│
┌─────────────────────────────────────────────────────────────────┐
│                   INTEGRATION LAYER                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Stripe/  │  │  Shopee  │  │  Lazada  │  │   IRAS   │      │
│  │  HitPay  │  │   API    │  │   API    │  │   API    │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  Ninja   │  │ XE.com   │  │InvoiceNow│  │   SMS    │      │
│  │   Van    │  │ (Rates)  │  │  Access  │  │ Gateway  │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## 4.2 Technology Justification

### Backend: Django 5.x

**Core Advantages:**
1. **Decimal Precision:** Django's `DecimalField` uses PostgreSQL `NUMERIC` type (no float errors)
   ```python
   # Decimal precision critical for GST calculations
   price = models.DecimalField(max_digits=10, decimal_places=2)
   gst_amount = price * Decimal('0.08')  # Exact precision maintained
   ```

2. **Built-in Admin Panel:** Saves 200-250 hours of development
   ```python
   @admin.register(Order)
   class OrderAdmin(admin.ModelAdmin):
       list_display = ['order_number', 'total_amount', 'status']
       search_fields = ['order_number', 'customer__email']
       list_filter = ['status', 'created_at']
   ```

3. **ORM Data Integrity:** Prevents SQL injection, ensures foreign key consistency
   ```python
   class OrderItem(models.Model):
       order = models.ForeignKey(Order, on_delete=models.PROTECT)
       product = models.ForeignKey(Product, on_delete=models.PROTECT)
       # PROTECT prevents deletion if order references exist
   ```

4. **Security Features:** CSRF protection, XSS prevention, SQL injection prevention built-in

5. **Mature Ecosystem:** Django REST Framework for APIs, Celery for async jobs, Django-allauth for auth

**Evidence:** Industry consensus confirms Django's superiority for financial/accounting applications requiring decimal precision

### Database: PostgreSQL 15.x

**Core Advantages:**
1. **ACID Compliance:** Full transaction integrity (Atomic, Consistent, Isolated, Durable)
2. **DECIMAL/NUMERIC Type:** Exact precision for financial calculations (not approximate like FLOAT)
3. **Foreign Key Constraints:** Prevents orphaned records, maintains referential integrity
4. **Concurrency:** MVCC (Multi-Version Concurrency Control) handles simultaneous transactions
5. **Full-Text Search:** Built-in `tsvector` for product search (no Elasticsearch needed for MVP)

```sql
-- PostgreSQL ensures GST calculations remain exact
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    subtotal DECIMAL(10, 2),
    gst_amount DECIMAL(10, 2),
    total_amount DECIMAL(10, 2) GENERATED ALWAYS AS (subtotal + gst_amount) STORED
);
```

### Frontend: Next.js 14 + React 18

**Core Advantages:**
1. **Server-Side Rendering (SSR):** Critical for SEO, Google crawls content immediately
2. **Static Site Generation (SSG):** Instant page loads for product catalog
3. **PWA Capabilities:** Installable app, offline mode, push notifications
4. **Performance Optimization:** Automatic code splitting, image optimization, lazy loading
5. **TypeScript Support:** Type safety reduces bugs, improves developer experience
6. **Mobile-First:** Tailwind CSS enables responsive design without custom CSS

**Evidence:** Industry research confirms "eCommerce platforms that need custom solutions and high-performance optimizations will benefit from Next.js" and "PWAs are no longer a nice-to-have but a strategic necessity for user retention"

### Infrastructure: AWS ECS Fargate (Lite Mode)

**MVP Infrastructure (Lite Mode):**
```
Cost-Effective Stack:
├── Application: ECS Fargate (2-4 tasks) → S$200-400/month
├── Database: RDS PostgreSQL (db.t3.medium) → S$150/month
├── Cache: ElastiCache Redis (t3.micro) → S$30/month
├── Storage: S3 (100 GB) → S$5/month
├── CDN: CloudFront → S$50/month
└── Monitoring: CloudWatch → S$20/month
Total MVP Cost: S$455-655/month (~S$7K/year)
```

**Scale Infrastructure (Enterprise Mode @ 1K orders/day):**
```
Enterprise Stack:
├── Orchestration: EKS Kubernetes (3 nodes) → S$74 + S$300/month
├── Database: RDS PostgreSQL (db.r5.large multi-AZ) → S$500/month
├── Cache: ElastiCache Redis (cluster mode) → S$150/month
├── Storage: S3 (1 TB) → S$30/month
├── CDN: CloudFront → S$200/month
├── Monitoring: ELK Stack (Elasticsearch) → S$200/month
└── Queue: SQS for message processing → S$50/month
Total Enterprise Cost: S$1,504/month (~S$18K/year)
```

**Justification:** Fargate eliminates Kubernetes management overhead (saves 20-30 hours/month) and is 60-70% cheaper for MVP

## 4.3 Core System Components

### 4.3.1 Authentication & Authorization

**Framework:** Django-allauth + JWT for API

```python
# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True)
    role = models.CharField(max_length=20, choices=[
        ('owner', 'Owner'),
        ('finance_manager', 'Finance Manager'),
        ('operations_manager', 'Operations Manager'),
        ('customer_service', 'Customer Service'),
    ])
    
    # PDPA consent tracking
    consent_marketing = models.BooleanField(default=False)
    consent_analytics = models.BooleanField(default=True)
    consent_date = models.DateTimeField(auto_now_add=True)

class Company(models.Model):
    name = models.CharField(max_length=200)
    uen = models.CharField(max_length=20, unique=True)
    gst_registered = models.BooleanField(default=False)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    # ... (more fields below in Database Schema)
```

**Permissions Framework:**
```python
# permissions.py
from rest_framework import permissions

class IsCompanyOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.company == request.user.company and request.user.role == 'owner'

class IsFinanceOrAbove(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['owner', 'finance_manager']
```

### 4.3.2 Inventory Management System

**Core Principles:**
1. **Multi-Location Tracking:** Warehouse, retail stores, consignment
2. **Reservation System:** Prevents overselling during checkout
3. **Redis Locking:** Prevents race conditions in marketplace sync
4. **Automated Reordering:** Trigger PO creation at reorder point

```python
# models.py
class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    gst_code = models.CharField(max_length=10, choices=[
        ('SR', 'Standard Rated (8%)'),
        ('ZR', 'Zero Rated'),
        ('ES', 'Exempt Supplies'),
    ], default='SR')
    
    # Inventory tracking
    track_inventory = models.BooleanField(default=True)
    reorder_point = models.IntegerField(default=10)
    reorder_quantity = models.IntegerField(default=50)

class InventoryItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    location = models.ForeignKey('Location', on_delete=models.PROTECT)
    available_qty = models.IntegerField(default=0)
    reserved_qty = models.IntegerField(default=0)  # Locked during checkout
    
    @property
    def net_qty(self):
        return self.available_qty - self.reserved_qty

class Location(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=[
        ('warehouse', 'Warehouse'),
        ('retail', 'Retail Store'),
        ('consignment', 'Consignment'),
    ])
    address = models.TextField()
```

**Inventory Reservation Logic (Redis Lock):**
```python
# inventory/services.py
import redis
from django.conf import settings

redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

def reserve_inventory(order_item):
    """
    Reserve inventory with Redis distributed lock to prevent race conditions.
    Critical for marketplace sync where Shopee/Lazada orders arrive simultaneously.
    """
    lock_key = f"product_lock:{order_item.product_id}"
    lock = redis_client.lock(lock_key, timeout=30)  # 30-second lock
    
    try:
        with lock:
            inventory = InventoryItem.objects.select_for_update().get(
                product=order_item.product,
                location=order_item.order.fulfillment_location
            )
            
            if inventory.net_qty >= order_item.quantity:
                inventory.reserved_qty += order_item.quantity
                inventory.save()
                return True
            else:
                return False  # Insufficient inventory
    except Exception as e:
        logger.error(f"Inventory reservation failed: {e}")
        return False
```

### 4.3.3 Order Management System

**State Machine:** Order flows through lifecycle with audit trail

```python
# models.py
class Order(models.Model):
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved (Awaiting Payment)'),
        ('payment_received', 'Payment Received'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey('Customer', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    
    # Money fields - must use DECIMAL
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2)
    shipping_amount = models.DecimalField(max_digits=8, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Compliance tracking
    gst_f5_reference = models.CharField(max_length=50, blank=True, null=True)
    invoicenow_submission_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    
    def save(self, *args, **kwargs):
        """
        Auto-calculate GST and validate before save.
        Ensures GST compliance at database level.
        """
        from decimal import Decimal
        
        # Recalculate GST based on items
        self.gst_amount = sum(
            item.gst_amount for item in self.items.all()
        )
        
        # Validate GST rate (must be 8% for standard-rated supplies)
        for item in self.items.all():
            if item.product.gst_code == 'SR' and item.gst_rate != Decimal('0.08'):
                raise ValidationError(f"Invalid GST rate for standard-rated product: {item.product.name}")
        
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # GST tracking per item (required for F5 return)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.08'))
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Audit trail
    inventory_reserved = models.BooleanField(default=False)
    fulfilled = models.BooleanField(default=False)
```

### 4.3.4 Accounting Automation Engine

**Dual-Entry Accounting:** Every transaction creates balanced journal entries

```python
# models.py
class ChartOfAccounts(models.Model):
    """
    Singapore-specific chart of accounts for GST compliance.
    """
    ACCOUNT_TYPES = [
        ('asset', 'Asset'),
        ('liability', 'Liability'),
        ('equity', 'Equity'),
        ('revenue', 'Revenue'),
        ('expense', 'Expense'),
    ]
    
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    
    # GST mapping for F5 return
    gst_box = models.CharField(max_length=10, blank=True, null=True)
    
class JournalEntry(models.Model):
    """
    Automated double-entry accounting entries.
    Generated by system events (order placement, payment, refund).
    """
    entry_number = models.CharField(max_length=20, unique=True)
    entry_date = models.DateField()
    description = models.TextField()
    reference = models.CharField(max_length=100)  # e.g., order_number, invoice_number
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)
    is_auto_generated = models.BooleanField(default=True)
    
class JournalEntryLine(models.Model):
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='lines')
    account = models.ForeignKey(ChartOfAccounts, on_delete=models.PROTECT)
    
    # DECIMAL for exact precision
    debit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # GST tracking
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

def create_sales_journal_entry(order):
    """
    Auto-generate journal entries for order.
    Ensures accounting integrity for GST F5 preparation.
    """
    entry = JournalEntry.objects.create(
        entry_number=f"JE-{order.order_number}",
        entry_date=order.created_at.date(),
        description=f"Sale of products (Order {order.order_number})",
        reference=order.order_number,
        is_auto_generated=True
    )
    
    # Revenue line
    JournalEntryLine.objects.create(
        entry=entry,
        account=ChartOfAccounts.objects.get(code='4000'),  # Sales Revenue
        credit_amount=order.subtotal
    )
    
    # GST Output Tax (Box 6 of F5)
    JournalEntryLine.objects.create(
        entry=entry,
        account=ChartOfAccounts.objects.get(code='2100'),  # GST Output Tax
        credit_amount=order.gst_amount,
        gst_amount=order.gst_amount
    )
    
    # Accounts Receivable (debit for increase)
    JournalEntryLine.objects.create(
        entry=entry,
        account=ChartOfAccounts.objects.get(code='1100'),  # Accounts Receivable
        debit_amount=order.total_amount
    )
    
    # Verify double-entry balance
    total_debit = sum(line.debit_amount for line in entry.lines.all())
    total_credit = sum(line.credit_amount for line in entry.lines.all())
    
    if total_debit != total_credit:
        raise ValidationError("Journal entry is not balanced!")
    
    return entry
```

---

# 5. DATABASE SCHEMA

## 5.1 Complete Entity-Relationship Diagram (ERD)

```
┌─────────────────┐
│    Company      │
├─────────────────┤
│ PK id           │
│   name          │
│   uen (unique)  │
│   gst_number    │
│   industry_type │
└────────┬────────┘
         │ 1
         │
         │ ∞
    ┌────┴──────────────────┐
    │    CustomUser         │
    ├───────────────────────┤
    │ PK id                 │
    │ FK company_id         │
    │   email (unique)      │
    │   role                │
    │   consent_*           │
    └────────┬──────────────┘
             │
        ┌────┴────┐
        │         │
        │         │
    ┌───▼─────┐ ┌─▼──────────┐
    │ Product │ │  Customer  │
    ├─────────┤ ├────────────┤
    │PK id    │ │PK id       │
    │   sku   │ │   email    │
    │  price  │ │  UEN/TIN   │
    │ gst_code│ │ consent_*  │
    └────┬────┘ └─────┬──────┘
         │            │
         │            │
    ┌────▼──────────────────┐
    │    Order              │
    ├───────────────────────┤
    │PK id                  │
    │FK customer_id         │
    │   order_number (unique)
    │   status              │
    │   subtotal            │
    │   gst_amount          │
    │   total_amount        │
    └────┬──────────────────┘
         │
    ┌────▼──────────────────┐
    │  OrderItem            │
    ├───────────────────────┤
    │PK id                  │
    │FK order_id            │
    │FK product_id          │
    │   quantity            │
    │   unit_price          │
    │   gst_amount          │
    └───────────────────────┘
```

## 5.2 Core Tables with Sample Data

### Companies Table (Singapore SMBs)

```sql
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    uen VARCHAR(20) UNIQUE NOT NULL,  -- Unique Entity Number (Singapore)
    gst_registered BOOLEAN DEFAULT FALSE,
    gst_number VARCHAR(20),
    industry_type VARCHAR(50) NOT NULL CHECK (
        industry_type IN ('food_beverage', 'health_beauty', 'retail', 'wholesale', 'services')
    ),
    -- SFA license tracking (for F&B)
    sfa_license_number VARCHAR(50),
    sfa_license_expiry DATE,
    -- Contact info
    contact_email VARCHAR(254),
    contact_phone VARCHAR(20),
    address TEXT,
    -- Settings
    default_currency VARCHAR(3) DEFAULT 'SGD',
    timezone VARCHAR(50) DEFAULT 'Asia/Singapore',
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO companies (name, uen, gst_registered, gst_number, industry_type, sfa_license_number)
VALUES 
  ('Tasty Kitchen Pte Ltd', '200012345A', TRUE, 'M1234567X', 'food_beverage', 'SFA-LIC-001'),
  ('Beauty Haven', '201098765B', FALSE, NULL, 'health_beauty', NULL);
```

### Products Table (DECIMAL for Financial Precision)

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    
    -- Financial fields (DECIMAL for precision)
    cost DECIMAL(10, 2) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    
    -- GST tracking (required for F5 return)
    gst_code VARCHAR(10) NOT NULL CHECK (
        gst_code IN ('SR', 'ZR', 'ES', 'NR')
    ) DEFAULT 'SR',  -- SR=Standard Rated (8%), ZR=Zero Rated, ES=Exempt, NR=Not Registered
    
    -- Inventory management
    track_inventory BOOLEAN DEFAULT TRUE,
    reorder_point INTEGER DEFAULT 10,
    reorder_quantity INTEGER DEFAULT 50,
    
    -- Product details
    barcode VARCHAR(50),
    weight_kg DECIMAL(8, 3),
    dimensions_cm VARCHAR(50),  -- "10x20x30"
    
    -- SEO/tags
    meta_title VARCHAR(255),
    meta_description TEXT,
    
    -- Lifecycle
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_company ON products(company_id);
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_gst ON products(gst_code);

-- Sample data (demonstrates DECIMAL precision)
INSERT INTO products (company_id, sku, name, cost, price, gst_code)
VALUES 
  (1, 'TK-FOOD-001', 'Signature Chicken Rice', 3.50, 8.90, 'SR'),
  (1, 'TK-FOOD-002', 'Herbal Soup', 2.80, 6.50, 'SR'),
  (2, 'BH-BEAUTY-001', 'Facial Cleanser', 15.00, 38.00, 'SR');
```

### Inventory Items (Multi-Location Support)

```sql
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (
        type IN ('warehouse', 'retail', 'consignment')
    ),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE inventory_items (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    location_id INTEGER REFERENCES locations(id) ON DELETE CASCADE,
    
    -- Quantities (no decimals - discrete items)
    available_qty INTEGER NOT NULL DEFAULT 0,
    reserved_qty INTEGER NOT NULL DEFAULT 0,
    
    -- Calculated field
    net_qty INTEGER GENERATED ALWAYS AS (available_qty - reserved_qty) STORED,
    
    UNIQUE(product_id, location_id),
    CONSTRAINT positive_inventory CHECK (available_qty >= 0 AND reserved_qty >= 0)
);

CREATE INDEX idx_inventory_product ON inventory_items(product_id);
CREATE INDEX idx_inventory_location ON inventory_items(location_id);
CREATE INDEX idx_inventory_net ON inventory_items(net_qty) WHERE net_qty > 0;

-- Sample data
INSERT INTO locations (company_id, name, type)
VALUES (1, 'Main Warehouse', 'warehouse'), (1, 'ION Orchard Outlet', 'retail');

INSERT INTO inventory_items (product_id, location_id, available_qty, reserved_qty)
VALUES (1, 1, 500, 0), (1, 2, 50, 3), (2, 1, 300, 0);
```

### Customers Table (PDPA Compliant)

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    
    -- Contact info
    email VARCHAR(254),
    phone VARCHAR(20),
    name VARCHAR(200) NOT NULL,
    
    -- Identity (UEN for B2B, FIN/NRIC for individuals)
    identification_type VARCHAR(10) CHECK (
        identification_type IN ('UEN', 'NRIC', 'FIN', 'passport')
    ),
    identification_number VARCHAR(20),
    
    -- Address
    billing_address TEXT,
    shipping_address TEXT,
    
    -- B2B fields
    is_b2b BOOLEAN DEFAULT FALSE,
    company_name VARCHAR(200),
    is_gst_registered BOOLEAN DEFAULT FALSE,
    
    -- PDPA consent (explicit fields)
    consent_marketing BOOLEAN DEFAULT FALSE,
    consent_analytics BOOLEAN DEFAULT TRUE,
    consent_date TIMESTAMP,
    
    -- Retention policy tracking
    data_retention_until DATE,
    
    -- Lifecycle
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customers_company ON customers(company_id);
CREATE INDEX idx_customers_email ON customers(email);

-- Sample data (PDPA compliant)
INSERT INTO customers (company_id, email, name, identification_type, identification_number, consent_marketing)
VALUES 
  (1, 'john@email.com', 'John Tan', 'NRIC', 'S1234567A', TRUE),
  (1, 'procurement@bigcorp.com', 'BigCorp Pte Ltd', 'UEN', '199912345X', FALSE);
```

### Orders Table (GST Compliant)

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
    
    -- Order identification
    order_number VARCHAR(20) UNIQUE NOT NULL,
    order_type VARCHAR(20) NOT NULL CHECK (
        order_type IN ('online', 'pos', 'marketplace_shopee', 'marketplace_lazada', 'b2b_quote')
    ),
    
    -- Status tracking (state machine)
    status VARCHAR(20) NOT NULL CHECK (
        status IN ('pending', 'approved', 'payment_received', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')
    ) DEFAULT 'pending',
    
    -- Financial fields (DECIMAL for precision)
    subtotal DECIMAL(12, 2) NOT NULL,
    discount_amount DECIMAL(8, 2) DEFAULT 0.00,
    gst_amount DECIMAL(12, 2) NOT NULL,
    shipping_amount DECIMAL(8, 2) DEFAULT 0.00,
    total_amount DECIMAL(12, 2) NOT NULL,
    
    -- GST tracking (F5 return preparation)
    gst_box_1_amount DECIMAL(12, 2),  -- Standard-rated supplies
    gst_box_2_amount DECIMAL(12, 2),  -- Zero-rated supplies
    gst_f5_reference VARCHAR(50),
    
    -- InvoiceNow tracking
    invoicenow_submitted BOOLEAN DEFAULT FALSE,
    invoicenow_submission_id VARCHAR(100),
    
    -- Fulfillment
    fulfillment_location_id INTEGER REFERENCES locations(id),
    tracking_number VARCHAR(100),
    
    -- Payment
    payment_status VARCHAR(20) CHECK (
        payment_status IN ('pending', 'partial', 'paid', 'refunded')
    ) DEFAULT 'pending',
    payment_reference VARCHAR(100),
    
    -- Audit trail
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES custom_users(id)
);

CREATE INDEX idx_orders_company ON orders(company_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_gst_f5 ON orders(gst_f5_reference);

-- Sample GST-compliant order
INSERT INTO orders (
    company_id, customer_id, order_number, order_type, status,
    subtotal, gst_amount, shipping_amount, total_amount,
    gst_box_1_amount, gst_box_2_amount
)
VALUES (
    1, 1, 'TK-2025-001', 'online', 'payment_received',
    28.50, 2.28, 5.00, 35.78,
    28.50, 0.00  -- SG$28.50 standard-rated, SG$0 zero-rated
);
```

### Order Items (Line-Level GST Tracking)

```sql
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    
    -- Order line details
    line_number INTEGER NOT NULL,
    product_name VARCHAR(200) NOT NULL,  -- Snapshot at time of order
    product_sku VARCHAR(50),
    
    -- Quantities
    quantity INTEGER NOT NULL,
    
    -- Financial fields (DECIMAL for precision)
    unit_price DECIMAL(10, 2) NOT NULL,
    line_discount DECIMAL(8, 2) DEFAULT 0.00,
    
    -- GST tracking (required for F5 return)
    gst_code VARCHAR(10) CHECK (gst_code IN ('SR', 'ZR', 'ES', 'NR')),
    gst_rate DECIMAL(5, 4) NOT NULL,  -- e.g., 0.08 for 8%
    gst_amount DECIMAL(10, 2) NOT NULL,
    
    -- Totals
    line_total DECIMAL(10, 2) NOT NULL,
    
    -- Fulfillment tracking
    inventory_reserved BOOLEAN DEFAULT FALSE,
    fulfilled BOOLEAN DEFAULT FALSE,
    fulfilled_qty INTEGER DEFAULT 0
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- Sample order items with GST
INSERT INTO order_items (
    order_id, line_number, product_name, product_sku, quantity,
    unit_price, gst_code, gst_rate, gst_amount, line_total
)
VALUES 
  (1, 1, 'Signature Chicken Rice', 'TK-FOOD-001', 2,
   8.90, 'SR', 0.08, 1.78, 19.56),  -- SG$17.80 + SG$1.78 GST = SG$19.58 ❌ ERROR IN CALCULATION
  (1, 2, 'Herbal Soup', 'TK-FOOD-002', 1,
   6.50, 'SR', 0.08, 0.52, 7.02);

-- CORRECTED CALCULATION:
-- Item 1: 2 × SG$8.90 = SG$17.80 subtotal
-- GST 8%: 17.80 × 0.08 = 1.424 → 1.42 (rounded)
-- Line total: 17.80 + 1.42 = 19.22
UPDATE order_items SET gst_amount=1.42, line_total=19.22 WHERE id=1;
```

---

## 5.3 Database Constraints (Critical for Data Integrity)

```sql
-- Prevent GST calculation errors
ALTER TABLE order_items
ADD CONSTRAINT chk_gst_calculation
CHECK (
    (gst_code = 'SR' AND gst_rate = 0.08) OR
    (gst_code = 'ZR' AND gst_rate = 0.00) OR
    (gst_code = 'ES' AND gst_rate = 0.00)
);

-- Ensure Singapore GST rate is 8%
ALTER TABLE order_items
ADD CONSTRAINT chk_gst_rate_current
CHECK (
    (gst_code = 'SR' AND gst_rate = 0.08)
    OR
    (gst_code IN ('ZR', 'ES', 'NR') AND gst_rate = 0.00)
);

-- Prevent negative inventory
ALTER TABLE inventory_items
ADD CONSTRAINT chk_inventory_positive
CHECK (available_qty >= 0 AND reserved_qty >= 0 AND net_qty >= 0);

-- Double-entry accounting validation
ALTER TABLE journal_entry_lines
ADD CONSTRAINT chk_double_entry
CHECK (
    (debit_amount > 0 AND credit_amount = 0) OR
    (credit_amount > 0 AND debit_amount = 0) OR
    (debit_amount = 0 AND credit_amount = 0)
);

-- PDPA retention policy enforcement
ALTER TABLE customers
ADD CONSTRAINT chk_pdpa_retention
CHECK (
    data_retention_until IS NOT NULL
    AND data_retention_until <= CURRENT_DATE + INTERVAL '7 years'
);
```

---

## 5.4 Database Performance Indexes

```sql
-- Critical for order lookup
CREATE INDEX idx_orders_number ON orders(order_number);
CREATE INDEX idx_orders_date ON orders(created_at DESC);

-- Critical for inventory queries
CREATE INDEX idx_inventory_net_qty ON inventory_items(net_qty) WHERE net_qty > 0;
CREATE INDEX idx_inventory_product_location ON inventory_items(product_id, location_id);

-- Critical for customer queries
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_company ON customers(company_id);

-- Full-text search for products
CREATE INDEX idx_products_search ON products USING GIN(to_tsvector('english', name || ' ' || COALESCE(description, '')));

-- Inventory reorder alerts
CREATE INDEX idx_reorder_check ON products(track_inventory, reorder_point) WHERE track_inventory = TRUE;

-- GST F5 reporting
CREATE INDEX idx_orders_gst_period ON orders(created_at, gst_box_1_amount, gst_box_2_amount);
```

---

# 6. API SPECIFICATIONS

## 6.1 RESTful API Design Principles

**Core Principles:**
1. **Resource-Oriented:** `/products`, `/orders`, `/customers` (not `/getProducts`, `/createOrder`)
2. **HTTP Verbs:** GET (list/retrieve), POST (create), PUT/PATCH (update), DELETE (delete)
3. **JSON Only:** No XML, no form-encoded
4. **Consistent Error Handling:** Standardized error format with HTTP status codes
5. **Pagination:** All list endpoints paginated (limit/offset or cursor)
6. **Versioning:** `/api/v1/` prefix for future compatibility

## 6.2 Authentication: JWT-Based

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

**Auth Flow:**
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
  "email": "sarah@tastykitchen.com",
  "password": "secure_password"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "sarah@tastykitchen.com",
    "role": "owner",
    "company": {
      "id": 1,
      "name": "Tasty Kitchen Pte Ltd",
      "uen": "200012345A"
    }
  }
}
```

## 6.3 Core API Endpoints

### 6.3.1 Products API

```http
# List products (with search, filter, pagination)
GET /api/v1/products/
Headers: Authorization: Bearer <access_token>
Query Parameters:
  - search (string): Search product name/description
  - gst_code (string): Filter by GST code (SR, ZR, ES)
  - category (integer): Filter by product category
  - page (integer): Page number (default: 1)
  - page_size (integer): Items per page (default: 20, max: 100)

Response:
{
  "count": 120,
  "next": "http://api.example.com/api/v1/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "sku": "TK-FOOD-001",
      "name": "Signature Chicken Rice",
      "description": "Traditional Hainanese chicken rice...",
      "price": "8.90",
      "cost": "3.50",
      "gst_code": "SR",
      "inventory": {
        "total_available": 500,
        "locations": [
          {"location_id": 1, "name": "Main Warehouse", "qty": 450},
          {"location_id": 2, "name": "ION Orchard", "qty": 50}
        ]
      },
      "barcode": "1234567890123",
      "is_active": true,
      "created_at": "2025-01-15T08:30:00Z"
    }
  ]
}

# Create product (Admin only)
POST /api/v1/products/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "sku": "TK-FOOD = "N003",
  "name": "New Signature Dish",
  "description": "Description",
  "price": "12.50",
  "cost": "4.80",
  "gst_code": "SR",
  "track_inventory": true,
  "reorder_point": 15,
  "reorder_quantity": 60
}

Response: 201 Created
{
  "id": 123,
  "sku": "TK-FOOD-003",
  "name": "New Signature Dish",
  ...
}

# Update product
PATCH /api/v1/products/123/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "price": "13.50",
  "reorder_point": 20
}

Response: 200 OK
{
  "id": 123,
  "sku": "TK-FOOD-003",
  "name": "New Signature Dish",
  "price": "13.50",
  ...
}

# Delete product (soft delete - marks is_active=False)
DELETE /api/v1/products/123/
Authorization: Bearer <access_token>

Response: 204 No Content
```

### 6.3.2 Orders API

```http
# Create order (with inventory reservation)
POST /api/v1/orders/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "customer_id": 1,
  "order_type": "online",
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": "8.90"
    },
    {
      "product_id": 2,
      "quantity": 1,
      "unit_price": "6.50"
    }
  ],
  "shipping_amount": "5.00",
  "payment_method": "stripe"
}

Response: 201 Created
{
  "id": 456,
  "order_number": "TK-2025-0456",
  "status": "pending",
  "customer": {
    "id": 1,
    "name": "John Tan",
    "email": "john@email.com"
  },
  "items": [
    {
      "id": 789,
      "product_id": 1,
      "product_name": "Signature Chicken Rice",
      "quantity": 2,
      "unit_price": "8.90",
      "gst_code": "SR",
      "gst_rate": "0.08",
      "gst_amount": "1.42",
      "line_total": "19.22"
    }
  ],
  "subtotal": "24.30",
  "gst_amount": "1.94",
  "shipping_amount": "5.00",
  "total_amount": "31.24",
  "inventory_reserved": true,
  "created_at": "2025-01-20T14:30:00Z",
  "payment_url": "https://checkout.stripe.com/pay/..."
}

# List orders with filters
GET /api/v1/orders/
Authorization: Bearer <access_token>
Query Parameters:
  - status (string): pending, approved, payment_received, shipped, delivered, cancelled
  - customer_id (integer): Filter by customer
  - date_from (date): Orders from date (YYYY-MM-DD)
  - date_to (date): Orders to date (YYYY-MM-DD)
  - page (integer): Page number

Response:
{
  "count": 45,
  "results": [
    {
      "id": 456,
      "order_number": "TK-2025-0456",
      "customer_name": "John Tan",
      "status": "payment_received",
      "total_amount": "31.24",
      "created_at": "2025-01-20T14:30:00Z",
      "payment_status": "paid"
    }
  ]
}

# Update order status (with inventory update)
PATCH /api/v1/orders/456/status/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "shipped",
  "tracking_number": "SG-123456789"
}

Response: 200 OK
{
  "id": 456,
  "status": "shipped",
  "tracking_number": "SG-123456789",
  "inventory_updated": true,  // Deducted from available_qty, removed from reserved_qty
  "updated_at": "2025-01-21T08:15:00Z"
}
```

### 6.3.3 Inventory API

```http
# Get inventory across all locations
GET /api/v1/inventory/?product_id=1
Authorization: Bearer <access_token>

Response:
{
  "product": {
    "id": 1,
    "sku": "TK-FOOD-001",
    "name": "Signature Chicken Rice"
  },
  "total_available": 500,
  "total_reserved": 0,
  "total_net": 500,
  "locations": [
    {
      "location_id": 1,
      "location_name": "Main Warehouse",
      "available_qty": 450,
      "reserved_qty": 0,
      "net_qty": 450
    },
    {
      "location_id": 2,
      "location_name": "ION Orchard Outlet",
      "available_qty": 50,
      "reserved_qty": 0,
      "net_qty": 50
    }
  ]
}

# Adjust inventory (Admin only - for stocktakes, corrections)
POST /api/v1/inventory/adjust/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "product_id": 1,
  "location_id": 1,
  "adjustment_type": "adjustment",  // adjustment, stocktake, transfer
  "quantity_change": -5,  // Negative means decrease, positive means increase
  "reason": "Stocktake discrepancy"
}

Response: 201 Created
{
  "id": 789,
  "product_id": 1,
  "location_id": 1,
  "adjustment_type": "adjustment",
  "quantity_change": -5,
  "previous_qty": 450,
  "new_qty": 445,
  "reason": "Stocktake discrepancy",
  "created_by": 1,
  "created_at": "2025-01-20T16:45:00Z"
}

# Low stock alert
GET /api/v1/inventory/low-stock/
Authorization: Bearer <access_token>

Response:
{
  "low_stock_products": [
    {
      "product_id": 3,
      "sku": "TK-FOOD-004",
      "name": "Special Noodle Soup",
      "current_qty": 8,
      "reorder_point": 10,
      "reorder_quantity": 50,
      "locations": [
        {"location_id": 1, "qty": 8}
      ]
    }
  ],
  "critical_stock_products": [
    {
      "product_id": 5,
      "sku": "TK-DRINK-001",
      "name": "Homemade Barley",
      "current_qty": 0,
      "reorder_point": 5
    }
  ]
}
```

### 6.3.4 GST F5 Preparation API

```http
# Generate F5 return data
GET /api/v1/gst/f5-preparation/
Authorization: Bearer <access_token>
Query Parameters:
  - period_year (integer): 2025
  - period_month (integer): 1 (January)

Response:
{
  "company": {
    "id": 1,
    "name": "Tasty Kitchen Pte Ltd",
    "uen": "200012345A",
    "gst_number": "M1234567X"
  },
  "period": {
    "year": 2025,
    "month": 1,
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "f5_boxes": {
    "box_1": 28500.00,  // Standard-rated supplies (SG$28,500)
    "box_2": 0.00,      // Zero-rated supplies
    "box_3": 0.00,      // Exempt supplies
    "box_4": 28500.00,  // Total value of supplies
    "box_5": 12500.00,  // Total value of purchases
    "box_6": 2280.00,   // Output tax (8% of box 1)
    "box_7": 1000.00,   // Input tax (8% of box 5)
    "box_8": 1280.00,   // Net GST to pay (box 6 - box 7)
    "box_9": 0.00,      // GST refund (if negative in box 8)
    "box_12": 45        // Number of standard-rated invoices
  },
  "validation_errors": [],
  "supporting_documents": {
    "sales_register": "https://api.example.com/api/v1/reports/sales-register/?period=2025-01",
    "purchase_register": "https://api.example.com/api/v1/reports/purchase-register/?period=2025-01",
    "gst_f7": "https://api.example.com/api/v1/reports/gst-f7/?period=2025-01"
  },
  "iras_integration": {
    "ready_for_submission": true,
    "mytax_portal_url": "https://mytax.iras.gov.sg/...",
    "submission_instructions": "Verify data above, then click Submit to IRAS."
  }
}

# Submit to IRAS (auto-populates myTax Portal)
POST /api/v1/gst/f5-submit/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "period_year": 2025,
  "period_month": 1,
  "confirm_data_accuracy": true
}

Response: 201 Created
{
  "submission_id": "F5-2025-01-001",
  "submission_status": "submitted",
  "submitted_at": "2025-02-15T09:30:00Z",
  "f5_reference": "F5-2025-01-001234",
  "iras_acknowledgment": "ACCEPTED",
  "payment_deadline": "2025-03-15",
  "amount_payable": "1280.00"
}
```

### 6.3.5 PDPA Compliance API

```http
# Customer data access request (SAR - Subject Access Request)
POST /api/v1/pdpa/access-request/
Content-Type: application/json

{
  "customer_email": "john@email.com",
  "request_purpose": "access_personal_data",
  "identification_document": "S1234567A"
}

Response: 201 Created
{
  "request_id": "SAR-2025-001",
  "customer_email": "john@email.com",
  "status": "under_review",
  "estimated_completion": "2025-02-05T23:59:59Z",  // 30 days max
  "data_subject_rights": "You have the right to access, correct, or delete your personal data..."
}

# Consent management (opt-in/opt-out)
PATCH /api/v1/customers/1/consent/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "consent_marketing": false,  // Withdraw marketing consent
  "consent_analytics": true    // Keep analytics consent
}

Response: 200 OK
{
  "customer_id": 1,
  "consent_updated_at": "2025-01-20T14:30:00Z",
  "new_consents": {
    "marketing": false,
    "analytics": true
  },
  "actions_taken": [
    "Removed from email marketing list",
    "Retained for order processing (contractual necessity)"
  ]
}

# Data retention purge (automated per PDPA policy)
POST /api/v1/pdpa/purge-expired-data/
Authorization: Bearer <access_token>  // Admin only
Content-Type: application/json

{
  "confirm_purge": true,
  "retention_policy": "3_years_customer_data"
}

Response:
{
  "purge_id": "PURGE-2025-001",
  "purge_date": "2025-01-20T15:00:00Z",
  "records_deleted": 234,
  "summary": {
    "customers": 180,
    "order_history": 45,
    "marketing_data": 9
  },
  "backup_retained": true,
  "backup_expiry": "2025-02-20T15:00:00Z"  // 30-day backup retention
}
```

## 6.4 Error Handling Standard

**Consistent Error Response Format:**

```http
# 400 Bad Request (Validation Error)
POST /api/v1/products/
{
  "name": "",
  "price": -10
}

Response: 400 Bad Request
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The submitted data is invalid.",
    "details": {
      "name": ["This field may not be blank."],
      "price": ["Ensure this value is greater than or equal to 0.01."]
    }
  }
}

# 401 Unauthorized
GET /api/v1/products/

Response: 401 Unauthorized
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication credentials were not provided.",
    "details": "Include 'Authorization: Bearer <token>' in request headers."
  }
}

# 403 Forbidden (Permission Denied)
DELETE /api/v1/products/123/

Response: 403 Forbidden
{
  "error": {
    "code": "PERMISSION_DENIED",
}

---

# 7. FRONTEND SPECIFICATIONS

## 7.1 Next.js 14 Architecture Overview

The frontend will be built using **Next.js 14 with App Router** for optimal SEO, performance, and PWA capabilities.

```
Frontend Architecture:
├── app/                    # App Router (Next.js 14)
│   ├── (auth)/            # Authentication pages
│   ├── (customer)/        # Customer-facing pages
│   ├── (admin)/           # Admin dashboard
│   └── api/               # API routes (for client-side operations)
├── components/            # Reusable React components
│   ├── ui/                # Base UI components (Button, Input, etc.)
│   ├── forms/             # Form components
│   ├── layouts/           # Layout components
│   └── modules/           # Feature-specific components
├── lib/                   # Utilities and shared logic
│   ├── api.ts             # API client
│   ├── auth.ts            # Authentication logic
│   └── utils.ts           # Helper functions
├── hooks/                 # Custom React hooks
├── styles/                # Tailwind CSS and custom styles
├── types/                 # TypeScript type definitions
├── public/                # Static assets
│   ├── icons/             # App icons for PWA
│   └── images/            # Images
├── package.json
├── next.config.js         # Next.js configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration
```

---

## 7.2 PWA Implementation (Service Worker)

**Critical PWA Features:**

1. **Service Worker for Offline Capability**
2. **Web App Manifest for Installation**
3. **Push Notifications for Re-engagement**
4. **Background Sync for Reliable Data Submission**

### 7.2.1 Service Worker Configuration

```typescript
// public/sw.js - Service Worker Logic
const CACHE_NAME = 'ecommerce-cache-v1';
const urlsToCache = [
  '/',
  '/offline.html',
  '/static/css/main.css',
  '/static/js/main.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
  self.skipWaiting(); // Activate immediately
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Return cached version if available
        if (response) {
          return response;
        }
        
        // Try network request
        return fetch(event.request).then((response) => {
          // Cache successful responses (except API calls)
          if (!event.request.url.includes('/api/') && 
              event.request.method === 'GET' && 
              response.status === 200) {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });
          }
          return response;
        }).catch(() => {
          // If both cache and network fail, show offline page
          if (event.request.destination === 'document') {
            return caches.match('/offline.html');
          }
          return new Response('Offline', { status: 503 });
        });
      })
  );
});

// Background Sync for order submission
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-orders') {
    event.waitUntil(syncOrders());
  }
  if (event.tag === 'sync-inventory') {
    event.waitUntil(syncInventory());
  }
});

async function syncOrders() {
  try {
    const orders = await getStoredOrders();
    for (const order of orders) {
      await submitOrder(order);
      await removeStoredOrder(order.id);
    }
  } catch (error) {
    console.error('Order sync failed:', error);
  }
}

// Push notifications
self.addEventListener('push', (event) => {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: '/icons/icon-192x192.png',
      badge: '/icons/badge-72x72.png',
      vibrate: [200, 100, 200],
      data: {

}

# COMPLETE REPLACEMENT PRD - CONTINUED

## 7. CONTINUED: FRONTEND SPECIFICATIONS

### 7.2.2 Web App Manifest

```json
// public/manifest.json - PWA Manifest Configuration
{
  "name": "Tasty Kitchen Online Store",
  "short_name": "Tasty Kitchen",
  "description": "Order delicious meals from Tasty Kitchen with fast, reliable delivery",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#e11d48",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any maskable"
    },
    {
      "src": "/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ],
  "categories": ["food", "shopping", "e-commerce"],
  "screenshots": [
    {
      "src": "/screenshots/home-desktop.png",
      "type": "image/png",
      "sizes": "1280x720",
      "label": "Tasty Kitchen Home Page"
    }
  ],
  "edge_side_panel": {
    "preferred_width": 480
  }
}
```

### 7.2.3 Next.js Configuration for PWA

```javascript
// next.config.js - PWA and Performance Optimization
const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development',
  runtimeCaching: [
    {
      urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
      handler: 'CacheFirst',
      options: {
        cacheName: 'google-fonts',
        expiration: {
          maxEntries: 4,
          maxAgeSeconds: 365 * 24 * 60 * 60, // 1 year
        },
      },
    },
    {
      urlPattern: /^https:\/\/images\.unsplash\.com\/.*/i,
      handler: 'StaleWhileRevalidate',
      options: {
        cacheName: 'product-images',
        expiration: {
          maxEntries: 64,
          maxAgeSeconds: 24 * 60 * 60, // 1 day
        },
      },
    },
  ],
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  // App Router configuration
  experimental: {
    serverMinification: true,
    optimizeCss: true,
  },
  
  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'images.unsplash.com',
        port: '',
        pathname: '/**',
      },
    ],
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
  },
  
  // Performance optimization
  swcMinify: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // SEO optimization
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          // Add security headers
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          // Add preconnect for external domain
