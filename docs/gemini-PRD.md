# Role & Responsibilities Acknowledgement

I accept the **Meticulous Approach** framework. I understand that my role is to act as an elite technical partner who does not merely execute commands but analyzes, plans, and validates every step to ensure technical excellence.

I will:
1.  **Analyze** the specific Singaporean context (GST, PDPA, Logistics, Payments) and the user's specific need for integrated accounting/inventory.
2.  **Plan** the project requirements systematically.
3.  **Validate** the technology choice against the provided comparison matrix.
4.  **Deliver** a comprehensive Project Requirements Document (PRD) that is production-ready.

---

# Phase 1: Technology Stack Selection

Based on the comparison table provided and the specific requirement for a site with **"built-in accounting and inventory management features,"** I have selected **Django (Python)**.

### **The Rationale (Meticulous Analysis)**

| Decision Factor | Why Django Wins for this Specific Request |
| :--- | :--- |
| **Internal Tools Focus** | The request explicitly asks for "accounting and inventory management." These are data-heavy, back-office functions. The table identifies Django as **"Ideal if you need a built-in admin panel... [and for] internal tools."** |
| **Data Integrity** | Accounting requires absolute data precision. The table highlights Django's philosophy of **"Models as the single source of truth."** This strict ORM structure prevents data anomalies better than looser conventions. |
| **Admin Interface** | Building a custom accounting interface from scratch is expensive. Django provides a **"Powerful, auto-generated admin panel"** out of the box, drastically reducing the time to build the inventory/accounting backend views. |
| **Scalability** | As the SMB grows, data complexity will increase. The table notes Django is strong for **"complex, data-heavy growth,"** which fits the trajectory of an integrated ERP-lite system. |

---

# Phase 2: Project Requirements Document (PRD)

## **Project Title:** Singapore SMB Integrated Commerce Platform (SICP)
**Version:** 1.0
**Status:** Approved for Planning
**Target Market:** Singapore Small & Medium Businesses (Retail/F&B)

---

## **1. Executive Summary**
A unified web application designed for Singaporean SMBs that combines a public-facing e-commerce storefront with a robust backend for Inventory Management and Compliance-ready Accounting. The system is designed to automate the specific regulatory hurdles of Singapore (GST reporting, PDPA compliance) and local operations (PayNow, NinjaVan).

---

## **2. User Roles & Permissions**

| Role | Responsibilities | Key Access Areas |
| :--- | :--- | :--- |
| **Admin (Owner)** | Full access, financial reporting, tax filing. | Dashboard, Accounting, Users, Settings. |
| **Store Manager** | Inventory control, order fulfillment, pricing. | Inventory, Orders, Logistics APIs. |
| **Accountant** | Reconciliation, GST F5 report generation. | Accounting, Invoices, Bank Feeds. |
| **Customer** | Browsing, purchasing, tracking orders. | Storefront, User Profile, Order History. |

---

## **3. Functional Requirements**

### **3.1 Module A: E-Commerce Storefront**
*   **Product Catalog:** Support for variants (Size, Color) and bundles.
*   **Search & Filtering:** Elasticsearch or Postgres Full-text search integration.
*   **Singapore-Specific Checkout:**
    *   **Address Validation:** Integration with SLA (Singapore Land Authority) OneMap API for auto-complete (Block, Unit, Postal Code).
    *   **Delivery Slots:** Selection of delivery windows based on local logistics cut-off times.
*   **Authentication:**
    *   Email/Password.
    *   **SingPass Login** (Optional future scope for high-security verification).
    *   Guest Checkout (PDPA compliant data retention policy).

### **3.2 Module B: Inventory Management (Internal)**
*   **Real-time Stock Sync:** "Hard" reservation of stock upon checkout to prevent overselling.
*   **Multi-Location Support:** Track stock across "Warehouse" (e.g., Jurong) and "Retail Outlet" (e.g., Bugis).
*   **Stock Alerts:** Auto-email triggers when SKU hits `min_threshold`.
*   **Batch Tracking:** Essential for perishables/cosmetics (Expiry Date tracking).
*   **Stock-Take Mode:** Mobile-friendly view for staff to perform physical counts using barcode scanners.

### **3.3 Module C: Built-in Accounting (Singapore Standard)**
*   **Chart of Accounts:** Pre-configured for Singapore Financial Reporting Standards (SFRS).
*   **Invoicing:**
    *   Auto-generation of **Tax Invoices** (Required for GST registered businesses).
    *   Must display: GST Reg No, Date, Customer Name, Breakdown of Standard-Rated (9%) and Zero-Rated supplies.
*   **GST F5 Helper:**
    *   Auto-calculate `Box 1` (Total Supplies), `Box 6` (Output Tax), and `Box 7` (Input Tax).
    *   Export data in IRAS-compliant format.
*   **Expense Claims:** Staff submission of receipt photos for reimbursement.

### **3.4 Module D: Integrations (The "Singapore Stack")**

| Integration | Purpose | API / Provider Details |
| :--- | :--- | :--- |
| **Payments** | Local Payments | **HitPay** or **Stripe** (Must support **PayNow** QR dynamic generation). |
| **Logistics** | Shipping | **NinjaVan** or **J&T Express** API (Order creation, Waybill generation, Webhook tracking). |
| **Notifications** | SMS / WhatsApp | **Twilio** or **SleekFlow** (For order updates: "Your parcel is arriving today"). |
| **Address** | Validation | **OneMap API** (GovTech Singapore free API for accurate postal codes). |

---

## **4. Technical Architecture (Django Stack)**

### **4.1 Core Components**
*   **Backend Framework:** Django 5.0 (Python).
*   **Database:** PostgreSQL (Robust for transactional data and accounting ledgers).
*   **Task Queue:** Celery + Redis (For async tasks like sending invoice emails or syncing inventory with 3PL).
*   **Frontend:**
    *   *Storefront:* Django Templates + HTMX (for dynamic interactions without React complexity) OR Vue.js.
    *   *Admin:* Django Admin (Customized with **Jazzmin** or **Unfold** for modern UI).

### **4.2 Data Models (Key Entities)**
```python
# Conceptual Schema

class Product(models.Model):
    sku = models.CharField(unique=True)
    gst_rate = models.DecimalField(default=0.09) # 9% GST

class InventoryItem(models.Model):
    product = models.ForeignKey(Product, ...)
    location = models.ForeignKey(Warehouse, ...)
    quantity = models.IntegerField()
    batch_code = models.CharField()

class Invoice(models.Model):
    invoice_number = models.CharField() # Format: INV-2024-0001
    gst_registration_no = models.CharField()
    subtotal = models.DecimalField(...)
    gst_amount = models.DecimalField(...) # Critical for IRAS
    total = models.DecimalField(...)
```

---

## **5. Compliance & Security (Critical for Singapore)**

### **5.1 PDPA (Personal Data Protection Act)**
*   **Consent Layer:** Explicit checkbox at checkout: *"I consent to the collection of my address for delivery purposes."*
*   **Data Retention:** Automated cron job to anonymize customer data after 7 years (standard financial record keeping requirement) or upon request (if no pending transactions).
*   **DNC Registry:** Check "Do Not Call" registry via API before sending marketing SMS.

### **5.2 Security Standards**
*   **PCI-DSS:** Do not store credit card info. Use Tokenization via Payment Gateway.
*   **CSRF/XSS:** Utilize Django’s built-in middleware protection.
*   **Backups:** Hourly incremental backups to S3 (Singapore Region `ap-southeast-1`) to ensure data sovereignty.

---

## **6. Implementation Plan**

### **Phase 1: Foundation (Weeks 1-2)**
- [ ] Setup Django project with PostgreSQL.
- [ ] Implement User Models (Custom User model).
- [ ] Configure OneMap API for address standardization.

### **Phase 2: Inventory & Products (Weeks 3-4)**
- [ ] Build Product Information Management (PIM).
- [ ] Implement Inventory logic (FIFO/LIFO support).
- [ ] Create Django Admin views for warehouse staff.

### **Phase 3: Commerce & Payments (Weeks 5-6)**
- [ ] Develop Storefront (Cart, Checkout).
- [ ] Integrate PayNow (via HitPay/Stripe).
- [ ] Implement "Lock Stock" logic during payment processing.

### **Phase 4: Accounting & Logistics (Weeks 7-8)**
- [ ] Build General Ledger & Tax Invoice generation.
- [ ] Integrate NinjaVan API for automatic waybill printing.
- [ ] Build GST F5 Reporting dashboard.

### **Phase 5: QA & Compliance (Week 9)**
- [ ] PDPA Audit (Data access logs).
- [ ] Load Testing (Simulate 11.11 sale traffic).
- [ ] UAT (User Acceptance Testing) with store owner.

---

## **7. Validation Check**
*   **Does this meet the user's need?** Yes, it combines sales with deep internal management.
*   **Is the Tech Stack appropriate?** Yes, Django handles the complex relationships between Inventory $\leftrightarrow$ Sales $\leftrightarrow$ Accounting better than a NoSQL or lightweight solution.
*   **Is it Singapore localized?** Yes, specifically addresses GST (9%), PayNow, and PDPA.

This PRD is ready for the development phase.
