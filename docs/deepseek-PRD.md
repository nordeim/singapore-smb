# Project Requirements Document: Singapore SMB E‑Commerce Platform with Integrated Accounting & Inventory Management

## **Document Control**

| **Document Version** | 1.0 |
|----------------------|-----|
| **Date**            | 2025‑12‑17 |
| **Status**          | Draft for Review |
| **Author**          | AI Technical Partner |
| **Stakeholders**    | Business Owner, Development Team, Operations Team |

---

## **1. Executive Summary**

This document defines the comprehensive requirements for a **Singapore‑based Small‑Medium Business (SMB) e‑commerce platform** with **built‑in accounting and inventory management** capabilities. The solution is designed to address the unique regulatory, operational, and scalability needs of Singaporean SMEs, ensuring **GST compliance**, **real‑time inventory control**, and **seamless financial integration**. The recommended technology stack—**Django (Python)**—is selected for its “batteries‑included” philosophy, powerful built‑in admin panel, and strong data‑handling capabilities, which align perfectly with the project’s need for a robust, maintainable, and compliance‑ready system.

## **2. Business Requirements**

### **2.1. Business Objectives**
- **BO‑1:** Provide a unified platform for online sales, inventory tracking, and financial management to eliminate manual data entry and reduce errors.
- **BO‑2:** Ensure full compliance with Singapore’s tax regulations, including **GST filing** and the mandatory **InvoiceNow** e‑invoicing requirement[reference:0].
- **BO‑3:** Improve inventory turnover and reduce stock‑outs through real‑time tracking and automated re‑ordering alerts[reference:1].
- **BO‑4:** Enable business growth by supporting multi‑currency transactions, multiple sales channels, and scalable architecture.

### **2.2. Target Users**
- **SMB Owners/Managers** – need a holistic view of sales, stock, and finances.
- **Operations Staff** – manage orders, inventory, and supplier relations.
- **Accountants/Bookkeepers** – handle GST reporting, financial statements, and tax filings.
- **Customers** – browse, purchase, and track orders online.

### **2.3. Regulatory & Compliance Drivers**
| Requirement | Source | Implication |
|-------------|--------|-------------|
| **GST InvoiceNow Mandate** | IRAS mandatory phased adoption from 1 Nov 2025 for new voluntary GST registrants[reference:2]. | System must generate and transmit e‑invoices in the Peppol‑based InvoiceNow format via an accredited Access Point Provider. |
| **IRAS ASR+ Compliance** | IRAS Accounting Software Register Plus (ASR+) encourages software that supports Corporate Income Tax (Form C‑S) and GST returns (F5, F8)[reference:3]. | Accounting module should facilitate direct preparation and submission of tax returns. |
| **Productivity Solutions Grant (PSG)** | IMDA pre‑approved solutions eligible for up to $30,000 grant support[reference:4]. | Solution should aim to be PSG‑eligible by adhering to IMDA‑accredited standards. |
| **Data‑Privacy Regulations** | Singapore’s Personal Data Protection Act (PDPA). | Implement secure handling of customer, supplier, and financial data. |

## **3. Functional Requirements**

### **3.1. E‑Commerce Module**
| ID | Requirement | Priority |
|----|-------------|----------|
| **EC‑1** | Multi‑vendor/multi‑storefront support (optional). | Medium |
| **EC‑2** | Product catalog with categories, variants, images, descriptions, and SEO‑friendly URLs. | High |
| **EC‑3** | Shopping cart, checkout, and order‑management workflow. | High |
| **EC‑4** | Integration with popular payment gateways (e.g., Stripe, PayPal, local providers like GrabPay, PayNow). | High |
| **EC‑5** | Support for multi‑currency pricing and display. | High |
| **EC‑6** | Customer accounts, order history, and wishlists. | Medium |
| **EC‑7** | Basic marketing tools (discount coupons, promotional banners). | Medium |

### **3.2. Inventory Management Module**
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| **INV‑1** | **Real‑time stock‑level tracking** across all locations[reference:5]. | High | |
| **INV‑2** | **Barcode‑scanning support** for receiving, picking, and stock‑take[reference:6]. | High | |
| **INV‑3** | **Automated low‑stock alerts** and re‑order suggestions[reference:7]. | High | |
| **INV‑4** | **Multi‑location inventory** (warehouse, store, online) with transfer tracking[reference:8]. | High | |
| **INV‑5** | **Purchase‑order management** with supplier tracking[reference:9]. | High | |
| **INV‑6** | **Inventory‑valuation methods** (FIFO, weighted average) for accurate COGS calculation. | High | |
| **INV‑7** | **Reporting dashboards** for stock‑turnover, dead‑stock, and sales‑by‑product[reference:10]. | Medium | |

### **3.3. Accounting Module**
| ID | Requirement | Priority | Source |
|----|-------------|----------|--------|
| **ACC‑1** | **GST‑compliant invoicing** with automatic GST calculation (standard‑rated, zero‑rated, exempt)[reference:11]. | High | |
| **ACC‑2** | **InvoiceNow‑Ready integration** – ability to generate and transmit e‑invoices in the required Peppol format[reference:12]. | High | |
| **ACC‑3** | **Accrual‑based accounting** (with cash‑based option for smaller businesses)[reference:13]. | High | |
| **ACC‑4** | **Automated bank‑feed reconciliation** for major Singapore banks. | High | |
| **ACC‑5** | **Financial statements**: Profit‑&‑Loss, Balance Sheet, Cash‑Flow statements[reference:14]. | High | |
| **ACC‑6** | **Multi‑currency transaction recording** and conversion[reference:15]. | High | |
| **ACC‑7** | **GST‑return preparation** (Form F5/F8) and submission readiness[reference:16]. | High | |
| **ACC‑8** | **Audit trail** for all financial transactions. | Medium | |
| **ACC‑9** | **Expense‑claim management** for staff. | Medium | |

### **3.4. Admin & Reporting Interface**
| ID | Requirement | Priority |
|----|-------------|----------|
| **ADM‑1** | **Unified admin dashboard** showing key KPIs: sales, inventory status, cash‑flow, pending orders. | High |
| **ADM‑2** | **Role‑based access control** (Owner, Operations, Accountant, Customer‑Support). | High |
| **ADM‑3** | **Customizable reports** with export to PDF/Excel. | Medium |
| **ADM‑4** | **Bulk‑operations** for product updates, order status changes, etc. | Medium |

### **3.5. Integration Requirements**
| ID | Requirement | Priority |
|----|-------------|----------|
| **INT‑1** | **Payment‑gateway APIs** (Stripe, PayPal, local providers). | High |
| **INT‑2** | **Logistics‑carrier APIs** for shipping labels and tracking. | Medium |
| **INT‑3** | **Email/SMS gateways** for order confirmations, alerts. | Medium |
| **INT‑4** | **Potential future integrations** with marketplaces (Shopee, Lazada), ERP, or CRM systems. | Low |

## **4. Non‑Functional Requirements**

| Category | Requirement |
|----------|-------------|
| **Performance** | - Page load times < 3 seconds for 95% of requests.<br>- Support for 100 concurrent users during peak sales (e.g., 11.11, Black Friday).<br>- Inventory‑update latency < 2 seconds after order placement. |
| **Security** | - PDPA‑compliant data handling; encryption of sensitive data at rest and in transit.<br>- Regular security patches; protection against OWASP Top‑10 vulnerabilities.<br>- Secure authentication (2FA optional for admin users). |
| **Reliability & Availability** | - Target 99.5% uptime (excluding maintenance windows).<br>- Automated backups (daily) with point‑in‑time recovery. |
| **Scalability** | - Architecture capable of horizontal scaling (adding more app servers, read‑replicas) as transaction volume grows. |
| **Maintainability** | - Code following best practices (modular, documented, version‑controlled).<br>- Comprehensive logging and monitoring (errors, performance metrics). |
| **Usability** | - Intuitive UI for non‑technical staff; mobile‑responsive storefront.<br>- Admin interface should require minimal training for daily operations. |

## **5. System Architecture & Technology Stack**

### **5.1. Recommended Stack: Django (Python)**
Based on the comparative analysis provided, **Django** is the recommended framework for this project. The decision is driven by the following factors:

| Decision Factor | How Django Fits |
|-----------------|-----------------|
| **Built‑in Admin Panel** | Django provides a powerful, auto‑generated admin interface out‑of‑the‑box – a **major advantage** for internal tools like inventory and accounting management. |
| **“Batteries Included”** | Comes with ORM, authentication, security, and templating, reducing time spent on boilerplate and allowing focus on business logic. |
| **Data‑Heavy Applications** | Django ORM treats **models as the single source of truth**, ideal for complex inventory and accounting data relationships. |
| **Scalability** | Proven at scale (e.g., Instagram); supports horizontal scaling and can handle growth in data and traffic. |
| **Future‑Proofing** | Python’s ecosystem is strong in AI/ML, which could be leveraged later for demand forecasting or analytics. |

### **5.2. Alternative Stacks Considered**
- **Ruby on Rails**: Excellent for rapid CRUD development but requires third‑party gems for admin interface, adding complexity.
- **Laravel (PHP)**: Elegant and flexible, but built‑in admin (Nova) is paid, and the ecosystem is less “batteries‑included” than Django.

### **5.3. High‑Level Architecture**
```
[Client Browsers] ←→ [Load Balancer] ←→ [Django Application Servers] ←→ [PostgreSQL Database]
                                                         ↓
                                          [Redis Cache] | [Celery for Async Tasks]
                                                         ↓
                                          [External APIs: Payment, InvoiceNow Access Point, Logistics]
```

### **5.4. Key Components**
- **Frontend**: Django templates (or lightweight JavaScript framework like Vue.js for dynamic storefront).
- **Backend**: Django 4.x+ with REST API (Django REST Framework) for future mobile‑app readiness.
- **Database**: PostgreSQL (for ACID compliance, JSON‑field support for product variants).
- **Cache**: Redis (for session storage, product‑catalog caching).
- **Task Queue**: Celery (for asynchronous jobs like email sending, report generation, InvoiceNow transmission).
- **Hosting**: Cloud platform (e.g., AWS, Google Cloud) with containerization (Docker) for easy deployment.

## **6. Implementation Plan (Phased Approach)**

### **Phase 1: Foundation & Core E‑Commerce (Weeks 1‑6)**
- **Objectives**: Set up project, implement basic product catalog, shopping cart, checkout, and order management.
- **Deliverables**:
    - Django project with user authentication, product models, and order workflow.
    - Integrated payment gateway (Stripe/PayPal).
    - Basic admin interface for managing products and orders.
- **Success Criteria**: Customers can browse, add to cart, checkout, and pay; admin can view and update orders.

### **Phase 2: Inventory Management (Weeks 7‑12)**
- **Objectives**: Build real‑time inventory tracking, multi‑location support, purchase orders, and low‑stock alerts.
- **Deliverables**:
    - Inventory models with real‑time updates.
    - Barcode‑scanning support (via mobile‑friendly UI).
    - Purchase‑order module with supplier tracking.
    - Dashboard showing stock levels and alerts.
- **Success Criteria**: Inventory levels automatically adjust after sales; low‑stock alerts trigger; purchase orders can be created.

### **Phase 3: Accounting & Compliance (Weeks 13‑18)**
- **Objectives**: Implement GST‑compliant invoicing, InvoiceNow integration, financial reports, and tax‑return readiness.
- **Deliverables**:
    - Accounting module with GST calculation and invoicing.
    - Integration with an InvoiceNow‑Ready Access Point Provider.
    - Financial statements (P&L, Balance Sheet, Cash Flow).
    - Audit‑trail logging.
- **Success Criteria**: Invoices generated with correct GST; e‑invoices can be transmitted via InvoiceNow; financial reports are accurate.

### **Phase 4: Polish & Integration (Weeks 19‑22)**
- **Objectives**: Enhance UI/UX, add advanced reporting, integrate with logistics carriers, and conduct user acceptance testing (UAT).
- **Deliverables**:
    - Refined storefront and admin UI.
    - Customizable reports.
    - Shipping‑carrier integration.
    - UAT feedback incorporated.
- **Success Criteria**: Platform is user‑friendly, reports meet business needs, and shipping labels can be generated.

### **Phase 5: Deployment & Go‑Live (Weeks 23‑24)**
- **Objectives**: Deploy to production, migrate existing data (if any), train end‑users, and monitor initial performance.
- **Deliverables**:
    - Production environment live.
    - Data‑migration scripts.
    - User‑training materials and sessions.
    - Monitoring dashboards.
- **Success Criteria**: Platform is live and stable; users can perform all core tasks; performance metrics meet targets.

## **7. Risks & Mitigations**

| Risk | Impact | Likelihood | Mitigation Strategy |
|------|--------|------------|---------------------|
| **InvoiceNow integration complexity** | High | Medium | Engage with an accredited Access Point Provider early; allocate extra time for testing and compliance validation. |
| **Data‑migration challenges** | High | Medium | Develop robust migration scripts; run multiple dry‑runs on a staging environment before cut‑over. |
| **Performance under peak load** | High | Low | Implement caching (Redis), database indexing, and load‑testing before major sales events. |
| **Regulatory changes** | Medium | Medium | Design accounting and invoicing modules to be configurable (e.g., tax rates, reporting formats). |
| **Team skill‑gap** | Medium | Low | Provide training on Django; consider hiring a Django‑experienced developer for the core team. |

## **8. Success Criteria**

The project will be considered successful if the following metrics are achieved within **three months of go‑live**:

1.  **Functional**: All high‑priority requirements in Sections 3.1‑3.4 are implemented and operational.
2.  **Compliance**: System passes IRAS ASR+ validation for GST‑return preparation and can transmit invoices via InvoiceNow.
3.  **Performance**: Page‑load times < 3s; inventory updates within 2s; system handles 100 concurrent users without degradation.
4.  **User Adoption**: >90% of daily operations (order processing, inventory updates, invoicing) are performed through the new platform.
5.  **Business Impact**: Reduction in manual data‑entry errors by ≥80%; improvement in inventory‑turnover ratio by ≥15%.

## **9. Appendices**

### **9.1. References**
1.  IRAS – GST InvoiceNow Requirement[reference:17].
2.  IRAS – Accounting Software Register Plus (ASR+)[reference:18].
3.  WLP – E‑commerce Accounting in Singapore: A Complete Guide[reference:19][reference:20].
4.  Genic Solutions – Key Features & Benefits of Inventory Management for SMEs[reference:21].
5.  Counto – E‑commerce Accounting Made Simple for Singapore SMEs[reference:22].

### **9.2. Glossary**
- **GST**: Goods and Services Tax (Singapore’s value‑added tax).
- **InvoiceNow**: Singapore’s nationwide e‑invoicing network based on the Peppol standard.
- **IRAS**: Inland Revenue Authority of Singapore.
- **PSG**: Productivity Solutions Grant (IMDA grant for IT solutions).
- **UEN**: Unique Entity Number (business registration number in Singapore).

---

## **Next Steps & Validation**

This PRD is the result of a deep analysis of Singapore SMB e‑commerce needs, regulatory requirements, and technology‑stack considerations. **Before proceeding to implementation**, please review and confirm the following:

- [ ] The business requirements (Section 2) accurately capture your goals.
- [ ] The functional requirements (Section 3) cover all necessary features.
- [ ] The recommended technology stack (Django) is acceptable.
- [ ] The implementation plan (Section 6) aligns with your timeline and resources.

**Upon your approval**, we will move to the **Detailed Design & Development** phase, following the meticulous workflow outlined in the framework.
