Phase 1: Deep Systematic Analysis — Combining Best Elements
🔍 Meticulous Element Integration Strategy
Before creating the PRD, I need to systematically analyze how to optimally combine elements from all three source documents while addressing identified gaps.

1.1 Source Document Contribution Matrix
text

┌─────────────────────────────────────────────────────────────────────────────┐
│              ELEMENT CONTRIBUTION BY SOURCE DOCUMENT                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  QWEN CONTRIBUTIONS (Business Layer):                                       │
│  ├── Executive Summary with quantified ROI (S$4.2M NPV)                     │
│  ├── Market Analysis with growth projections                                │
│  ├── User Personas with pain points & success metrics                       │
│  ├── Process Mapping (O2C, P2P) with KPIs                                   │
│  ├── GST F5 validation rules & IRAS API integration                         │
│  ├── InvoiceNow/PEPPOL BIS 3.0 complete specification                       │
│  ├── PDPA Framework with consent management                                 │
│  ├── Industry License Framework (SFA, HSA, SPF)                             │
│  └── Business rules engine (pricing, inventory)                             │
│                                                                             │
│  OPUS CONTRIBUTIONS (Technical Layer):                                      │
│  ├── Database schema with DECIMAL precision                                 │
│  ├── Django/DRF architecture specifications                                 │
│  ├── Security framework (authentication, encryption)                        │
│  ├── API design patterns with versioning                                    │
│  ├── Implementation roadmap with sprint structure                           │
│  ├── Performance monitoring specifications                                  │
│  └── Celery/Redis async processing patterns                                 │
│                                                                             │
│  NEX-N1 CONTRIBUTIONS (Frontend Layer):                                     │
│  ├── Mobile-first design specifications                                     │
│  ├── PWA architecture with offline capability                               │
│  ├── Touch-optimized UX patterns                                            │
│  ├── Next.js App Router implementation                                      │
│  ├── Payment gateway UI/UX flows                                            │
│  ├── Performance targets (PageSpeed > 90)                                   │
│  └── Accessibility standards (WCAG 2.1 AA)                                  │
│                                                                             │
│  NEW ADDITIONS (Gap Resolution):                                            │
│  ├── MVP-appropriate infrastructure (ECS vs K8s)                            │
│  ├── Marketplace sync with conflict resolution                              │
│  ├── Multi-currency handling                                                │
│  ├── Offline POS synchronization                                            │
│  ├── B2B credit management                                                  │
│  └── API rate limiting patterns                                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
1.2 Integration Decision Framework
Section	Primary Source	Secondary Source	Enhancements
Executive Summary	Qwen (ROI focus)	Opus (tech summary)	Updated timeline (28 weeks)
Market Analysis	Qwen (quantified)	Nex-N1 (citations)	2025 data updates
User Personas	Qwen (detailed)	Opus (roles)	Success metrics per persona
Business Requirements	Qwen (process maps)	Opus (rules)	Gap resolutions added
E-commerce Functional	Nex-N1 (UX)	Opus (backend)	Hybrid checkout flow
Inventory Functional	Qwen (rules)	Opus (code)	Offline sync added
Accounting Functional	Qwen (GST)	Opus (journal)	Multi-currency added
Technical Architecture	Opus (Django)	Nex-N1 (Next.js)	MVP infrastructure
Database Design	Opus (schema)	Qwen (constraints)	Performance indexes
API Specifications	Opus (complete)	Qwen (validation)	Rate limiting added
Compliance Framework	Qwen (comprehensive)	Opus (code)	Audit documentation
Security	Opus (enterprise)	—	MVP-appropriate
Implementation Roadmap	Opus (sprints)	Qwen (validation)	28-week refined
Risk Management	New (comprehensive)	Qwen (partial)	All gaps addressed
1.3 Architecture Integration Diagram
mermaid

graph TB
    subgraph "HYBRID ARCHITECTURE"
        subgraph "Frontend Layer (Nex-N1)"
            A[Next.js 14+ App Router]
            B[React 18+ TypeScript]
            C[Tailwind CSS + DaisyUI]
            D[PWA Service Workers]
            E[Mobile-First Design]
        end
        
        subgraph "Backend Layer (Opus/Qwen)"
            F[Django 5.0+ REST Framework]
            G[Celery + Redis Async]
            H[Django Admin + Jazzmin]
            I[GSTEngine from Qwen]
            J[PDPAFramework from Qwen]
        end
        
        subgraph "Data Layer (Opus)"
            K[(PostgreSQL 15+ DECIMAL)]
            L[(Redis Cache)]
            M[PostgreSQL tsvector Search]
        end
        
        subgraph "Infrastructure (Simplified)"
            N[AWS ECS Fargate]
            O[CloudFront CDN]
            P[CloudWatch Monitoring]
            Q[S3 Storage]
        end
        
        subgraph "Integrations"
            R[Stripe + HitPay]
            S[Ninja Van + SingPost]
            T[Shopee + Lazada APIs]
            U[IRAS + InvoiceNow]
        end
    end
    
    A --> F
    B --> F
    F --> K
    F --> L
    F --> I
    F --> J
    F --> R
    F --> S
    F --> T
    F --> U
    N --> F
    O --> A
📋 Phase 2: Implementation Plan — PRD Creation
2.1 Document Structure Plan
text

COMPREHENSIVE HYBRID PRD STRUCTURE
├── PART 1 (First Half) - This Response
│   ├── Document Control & Table of Contents
│   ├── Section 1: Executive Summary
│   ├── Section 2: Market Analysis & Business Context
│   ├── Section 3: Stakeholder Analysis & User Personas
│   ├── Section 4: Business Requirements
│   ├── Section 5: Functional Requirements
│   │   ├── 5.1 E-Commerce Module
│   │   ├── 5.2 Inventory Management Module
│   │   ├── 5.3 Accounting Module
│   │   └── 5.4 Payment Processing Module
│   ├── Section 6: Technical Architecture
│   └── Section 7: Database Design
│
└── PART 2 (Second Half) - Next Response
    ├── Section 8: API Specifications
    ├── Section 9: Compliance & Regulatory Framework
    ├── Section 10: Security Implementation
    ├── Section 11: Performance & Scalability
    ├── Section 12: Implementation Roadmap (28 Weeks)
    ├── Section 13: Quality Assurance & Testing
    ├── Section 14: Risk Management & Mitigation
    ├── Section 15: Budget & Resource Planning
    ├── Section 16: Success Metrics & KPIs
    ├── Section 17: Future Roadmap & Vision
    └── Appendices
2.2 Quality Validation Checklist
Before proceeding, I validate that this PRD will:

 Combine best elements from all three source PRDs
 Address all 7 identified gaps (3 original + 4 additional)
 Maintain stakeholder accessibility (Qwen's strength)
 Provide developer actionability (Opus's strength)
 Optimize for mobile-first (Nex-N1's strength)
 Simplify infrastructure for MVP (addressing over-engineering)
 Include quantified business case (ROI, NPV)
 Provide complete compliance frameworks (GST, PDPA, InvoiceNow)
 Specify production-ready code samples
 Include validation gates throughout implementation
2.3 Execution Readiness Confirmation
text

┌─────────────────────────────────────────────────────────────────────────────┐
│              IMPLEMENTATION PLAN VALIDATION                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  COMPLETENESS CHECK:                                                        │
│  [✓] All source PRD elements catalogued                                     │
│  [✓] Integration decisions documented                                       │
│  [✓] Gap resolutions planned                                                │
│  [✓] Document structure finalized                                           │
│  [✓] Quality criteria established                                           │
│                                                                             │
│  RISK MITIGATION:                                                           │
│  [✓] Over-engineering addressed (MVP infrastructure)                        │
│  [✓] Stakeholder accessibility maintained                                   │
│  [✓] Developer actionability preserved                                      │
│  [✓] Compliance rigor enhanced                                              │
│                                                                             │
│  EXECUTION READINESS: ✅ CONFIRMED                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
Phase 3: Execution — Comprehensive Hybrid PRD (Part 1 of 2)
📋 SINGAPORE SMB E-COMMERCE PLATFORM
COMPREHENSIVE PROJECT REQUIREMENTS DOCUMENT
Version 4.0 — Hybrid Architecture Edition
DOCUMENT CONTROL
Attribute	Details
Version	4.0 — Hybrid Architecture (Django Backend + Next.js Frontend)
Date	January 2025
Status	Final — Ready for Implementation
Document Type	Master Project Requirements Document
Confidentiality	Proprietary and Confidential
Review Cycle	Quarterly Updates
Target Audience	Business Stakeholders, Development Team, Project Management
Prepared By	AI Coding Agent (Meticulous Approach Framework)
Source Documents	Nex-N1 PRD, Opus-Revised-PRD-2, Qwen-Revised-PRD
Document Change History
Version	Date	Author	Changes
1.0	Nov 2024	Original Team	Nex-N1 PRD (Node.js/Next.js)
2.0	Dec 2024	Original Team	Opus-Revised-PRD-2 (Django)
3.0	Dec 2024	Original Team	Qwen-Revised-PRD (Django)
4.0	Jan 2025	AI Agent	Hybrid synthesis combining best elements
Key Changes in Version 4.0
Category	Change Description
Architecture	Hybrid Django backend + Next.js frontend
Infrastructure	MVP-appropriate (ECS Fargate, not Kubernetes)
Timeline	Extended to 28 weeks (from 24) for integration complexity
Compliance	Enhanced GST F5 validation, complete InvoiceNow/PEPPOL
Gap Resolution	Added marketplace sync, multi-currency, offline POS, B2B credit
Business Case	Preserved Qwen's quantified ROI framework
TABLE OF CONTENTS
Part 1 (This Document)
Executive Summary
Market Analysis & Business Context
Stakeholder Analysis & User Personas
Business Requirements
Functional Requirements
Technical Architecture
Database Design
Part 2 (Next Document)
API Specifications
Compliance & Regulatory Framework
Security Implementation
Performance & Scalability
Implementation Roadmap
Quality Assurance & Testing
Risk Management & Mitigation
Budget & Resource Planning
Success Metrics & KPIs
Future Roadmap & Vision
Appendices
1. EXECUTIVE SUMMARY
1.1 Project Vision
This document presents the definitive blueprint for developing Singapore's most comprehensive SMB e-commerce platform, integrating three critical business functions into a unified, compliance-ready system:

Core Function	Description	Key Differentiator
E-Commerce Storefront	Mobile-first (70% of traffic) consumer experience	PWA with offline capability
Inventory Management	Real-time multi-location tracking	Marketplace sync with conflict resolution
Automated Accounting	GST compliance with IRAS integration	InvoiceNow/PEPPOL ready
The Problem We Solve:
85% of Singapore SMBs currently use 5-7 different software tools, resulting in:

40% of operational time wasted on manual data entry and reconciliation
23% inventory discrepancy rates causing lost sales
S$15,000 average annual penalties from GST filing errors
68% checkout abandonment on mobile devices
Our Solution:
A unified platform that eliminates system fragmentation while ensuring full regulatory compliance with Singapore's GST, PDPA, and industry-specific requirements.

1.2 Technology Decision: Hybrid Architecture
After comprehensive evaluation of three alternative approaches, we adopt a Hybrid Architecture:

text

┌─────────────────────────────────────────────────────────────────────────────┐
│                         HYBRID ARCHITECTURE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  FRONTEND: Next.js 14+ (from Nex-N1 PRD)                                    │
│  ├── Mobile-first responsive design                                         │
│  ├── PWA with offline catalog browsing                                      │
│  ├── Touch-optimized checkout (< 2 minutes)                                 │
│  ├── React 18+ with TypeScript                                              │
│  └── Tailwind CSS for rapid styling                                         │
│                                                                             │
│  BACKEND: Django 5.0+ (from Opus/Qwen PRDs)                                 │
│  ├── Django REST Framework for APIs                                         │
│  ├── Django Admin for internal tools (30% dev time savings)                 │
│  ├── PostgreSQL with DECIMAL for financial precision                        │
│  ├── Celery + Redis for async processing                                    │
│  └── Built-in security and validation frameworks                            │
│                                                                             │
│  INFRASTRUCTURE: MVP-Appropriate (Simplified)                               │
│  ├── AWS ECS Fargate (not Kubernetes)                                       │
│  ├── PostgreSQL tsvector (not Elasticsearch)                                │
│  ├── CloudWatch (not ELK Stack)                                             │
│  └── Scale to K8s/ES when >1000 daily orders                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
Why This Architecture:

Decision	Rationale	Alternative Rejected
Django Backend	Built-in admin saves 10+ weeks; DECIMAL for money; proven at Instagram scale	Node.js (JavaScript float precision issues)
Next.js Frontend	Best mobile-first framework; PWA support; SEO-friendly	Django templates (limited interactivity)
ECS Fargate	Simpler than K8s; auto-scaling; cost-effective for MVP	Kubernetes (over-engineered for <1000 orders/day)
PostgreSQL tsvector	Built-in full-text search; no additional infrastructure	Elasticsearch (unnecessary complexity)
1.3 Market Opportunity & ROI Analysis
Market Size & Growth:

text

Singapore E-Commerce Market Trajectory
├── 2023: US$4.1 billion
├── 2024: US$4.5 billion (+9.8% YoY)
├── 2025: US$5.0 billion (+11.1% YoY)
└── 2026: US$5.6 billion (projected)

Key Market Characteristics:
├── Mobile commerce: 70% of transactions
├── Digital wallet adoption: 39% of payments
├── PayNow usage (Gen Z): 68%
└── Cross-border shopping: 65% of online shoppers
Quantified Business Impact:

Metric	Current SMB Average	With Our Platform	Improvement	Annual Value
Order Processing Time	8.5 minutes	2.1 minutes	75% reduction	S$24,000 savings
Inventory Accuracy	77%	99.5%	22.5% improvement	S$50,000 revenue gain
GST Filing Errors	3.2 per quarter	0	100% elimination	S$15,000 penalty avoidance
Manual Data Entry	16 hours/week	6.4 hours/week	60% reduction	S$38,400 labor savings
Checkout Abandonment	68%	35%	33% reduction	S$120,000 revenue lift
Total Annual Value				S$247,400 per SMB
Investment Summary:

Investment Category	Amount	Notes
Development (28 weeks)	S$780,000 - S$880,000	Extended from 24 weeks for integration
Annual Operations	S$320,000 - S$400,000	Infrastructure, support, maintenance
ROI Timeline	12-18 months	Faster with PSG grant support
Break-even Point	50-60 active SMB clients	Subscription model
5-Year NPV	S$4.2 million	10% discount rate
1.4 Strategic Objectives & Success Metrics
Objective	Target	Metric	Measurement
Operational Excellence	60% reduction in manual processes	Time saved per transaction	Weekly tracking
Regulatory Compliance	100% GST/PDPA compliance	Zero penalties or violations	Quarterly audit
Inventory Optimization	99.5% stock accuracy	Cycle count variance	Daily monitoring
Mobile Experience	< 2 second load time	Google PageSpeed score > 90	Real-time
Financial Visibility	Real-time dashboards	Refresh < 5 seconds	Continuous
Market Adoption	100 active SMBs in 6 months	Monthly active users	Monthly
Customer Satisfaction	NPS > 50	Net Promoter Score	Quarterly survey
1.5 Project Timeline Overview
text

PHASE 1: Foundation (Weeks 1-6)
├── Infrastructure setup
├── Core Django models
├── Admin customization
└── CI/CD pipeline

PHASE 2: Compliance Core (Weeks 7-10)
├── GST engine with F5 validation
├── PDPA framework
├── Chart of Accounts
└── Audit trail system

PHASE 3: E-Commerce Backend (Weeks 11-16)
├── Order management
├── Payment integration
├── Logistics integration
└── Inventory operations

PHASE 4: Next.js Storefront (Weeks 17-22)
├── Product catalog (SSR/SSG)
├── Mobile-optimized checkout
├── PWA implementation
└── Performance optimization

PHASE 5: Integration & Launch (Weeks 23-28)
├── Marketplace sync (Shopee/Lazada)
├── InvoiceNow/PEPPOL
├── Security audit
└── Go-live

TOTAL: 28 WEEKS
2. MARKET ANALYSIS & BUSINESS CONTEXT
2.1 Singapore E-Commerce Landscape
2.1.1 Market Size & Growth Dynamics
Current Market State (2024-2025):

Metric	Value	Source
Total E-Commerce Market	US$4.5 billion (2024)	Statista
Retail E-Commerce	US$3.2 billion (71%)	IMDA
Mobile Commerce Share	70% of transactions	Google Singapore
Digital Wallet Adoption	39% of payments	JP Morgan Payments
YoY Growth Rate	9.8%	eMarketer
Growth Drivers:

Python

market_drivers = {
    'digital_infrastructure': {
        'internet_penetration': 98.5,  # % of population
        'smartphone_ownership': 95.2,  # %
        'digital_literacy_score': 86.7,  # Out of 100
        '5g_coverage': 95.0  # % of island
    },
    'payment_evolution': {
        'paynow_adoption': {
            'gen_z': 68.3,  # %
            'millennials': 55.2,  # %
            'gen_x': 42.1,  # %
            'businesses': 76.8  # %
        },
        'bnpl_growth': 215.0,  # % YoY growth
        'contactless_preference': 78.5  # % prefer contactless
    },
    'government_support': {
        'psg_grants': 'Up to S$30,000 per business',
        'digital_apis': ['SingPass', 'CorpPass', 'MyInfo', 'OneMap'],
        'invoicenow_mandate': 'Phased rollout for B2G, B2B'
    }
}
2.1.2 Competitive Landscape
Platform Type	Market Share	Key Players	SMB Pain Points	Our Solution
Marketplaces	60%	Shopee, Lazada, Amazon.sg	15-20% commission, limited branding, fragmented inventory	Multi-channel sync with unified inventory
SaaS Platforms	25%	Shopify, WooCommerce	Separate accounting, GST compliance gaps	Built-in GST engine, IRAS integration
Custom Solutions	15%	Bespoke development	S$200K+ cost, 12+ months timeline	28-week delivery, PSG eligible
Competitive Differentiation:

text

┌─────────────────────────────────────────────────────────────────────────────┐
│                    OUR COMPETITIVE ADVANTAGES                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. UNIFIED SYSTEM                                                          │
│     └── Single platform for e-commerce + inventory + accounting            │
│         (vs. competitors requiring 5-7 separate tools)                      │
│                                                                             │
│  2. COMPLIANCE-FIRST DESIGN                                                 │
│     ├── Automated GST F5 filing with validation                             │
│     ├── InvoiceNow/PEPPOL ready for B2B/B2G                                 │
│     └── PDPA compliance built-in (not an afterthought)                      │
│                                                                             │
│  3. MOBILE-OPTIMIZED                                                        │
│     ├── < 2 second load time on 4G                                          │
│     ├── PWA with offline catalog browsing                                   │
│     └── Touch-optimized checkout (< 2 minutes)                              │
│                                                                             │
│  4. COST-EFFECTIVE                                                          │
│     ├── 70% cost reduction vs. custom development                           │
│     ├── PSG grant eligible (up to S$30,000)                                 │
│     └── SaaS pricing aligned with SMB budgets                               │
│                                                                             │
│  5. MARKETPLACE INTEGRATION                                                 │
│     ├── Shopee + Lazada inventory sync                                      │
│     ├── Conflict resolution for concurrent updates                          │
│     └── Single dashboard for all channels                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
2.2 Target Market Definition
2.2.1 Primary Target Segments
Segment	Annual Revenue	Employees	SKUs	Tech Readiness	Primary Needs
Micro SMB	S$100K - S$500K	1-10	50-200	Low-Medium	Basic e-commerce, simple accounting
Small SMB	S$500K - S$2M	10-50	200-1,000	Medium	Multi-channel, GST compliance, inventory sync
Medium SMB	S$2M - S$10M	50-200	1,000-5,000	High	Advanced analytics, B2B features, multi-location
Primary Focus: Small SMB segment (S$500K - S$2M revenue)

Large enough to need comprehensive solution
Small enough to lack in-house IT resources
Most likely to benefit from GST automation
Best fit for PSG grant eligibility
2.2.2 Industry Vertical Analysis
Python

industry_verticals = {
    'retail': {
        'market_share': 35.0,  # % of target market
        'sub_categories': ['Fashion', 'Electronics', 'Home Goods', 'Sporting Goods'],
        'key_requirements': [
            'Multi-variant products (size, color)',
            'Seasonal inventory management',
            'Customer segmentation',
            'Loyalty programs',
            'Returns management'
        ],
        'compliance_needs': ['GST standard-rated', 'Consumer protection']
    },
    'food_beverage': {
        'market_share': 25.0,
        'sub_categories': ['Restaurants', 'Cafes', 'Food Products', 'Bakeries'],
        'key_requirements': [
            'Ingredient inventory (batch tracking)',
            'Expiry date management',
            'Recipe costing',
            'Delivery integration'
        ],
        'compliance_needs': ['SFA Food License', 'MUIS Halal (optional)', 'NEA Health Certificate'],
        'regulatory_bodies': ['Singapore Food Agency (SFA)', 'National Environment Agency (NEA)']
    },
    'health_beauty': {
        'market_share': 20.0,
        'sub_categories': ['Cosmetics', 'Supplements', 'Wellness Products', 'Personal Care'],
        'key_requirements': [
            'Product registration tracking',
            'Batch recall capability',
            'Expiry management',
            'Import license tracking'
        ],
        'compliance_needs': ['HSA Product Registration', 'Cosmetic Notification'],
        'regulatory_bodies': ['Health Sciences Authority (HSA)']
    },
    'b2b_wholesale': {
        'market_share': 20.0,
        'sub_categories': ['Industrial Supplies', 'Office Products', 'Building Materials'],
        'key_requirements': [
            'Tiered pricing (wholesale vs. retail)',
            'Credit terms (NET30/NET45)',
            'Bulk ordering',
            'Account management',
            'Statement of account'
        ],
        'compliance_needs': ['InvoiceNow/PEPPOL', 'Credit management'],
        'unique_features': ['B2B portal', 'Quote management', 'Credit limits']
    }
}
2.3 Business Case & Problem Statement
2.3.1 Quantified Pain Points
Problem Area	Current State	Business Impact	Annual Cost per SMB
System Fragmentation	5-7 different software tools	40% time on data reconciliation	S$67,200
Inventory Inaccuracy	23% average discrepancy	15% lost sales from stockouts	S$88,000
GST Compliance	3.2 errors per quarter	Penalties, audit risk	S$60,000
Manual Processes	16 hours/week data entry	Limited growth capacity	S$38,400
Mobile Experience	68% checkout abandonment	Lost conversion opportunities	S$120,000
Marketplace Sync	Manual updates across channels	Overselling, customer complaints	S$25,000
TOTAL ANNUAL COST			S$398,600
2.3.2 Solution Value Proposition
Python

value_proposition = {
    'operational_efficiency': {
        'data_entry_reduction': 60.0,  # % reduction
        'order_processing_speed': 75.0,  # % faster
        'inventory_accuracy': 99.5,  # % target
        'time_saved_per_week': 9.6,  # hours
        'annual_value': 'S$105,600'  # S$38,400 labor + S$67,200 reconciliation
    },
    'compliance_security': {
        'gst_errors_eliminated': 100.0,  # %
        'penalty_avoidance': 'S$60,000',  # annual
        'pdpa_breach_protection': 'S$1,000,000',  # max fine avoided
        'audit_preparation_time': 90.0  # % reduction
    },
    'revenue_growth': {
        'checkout_completion': 65.0,  # % (up from 32%)
        'stockout_reduction': 90.0,  # %
        'cross_sell_revenue': 15.0,  # % increase
        'customer_retention': 25.0,  # % improvement
        'annual_revenue_impact': 'S$233,000'  # S$120,000 + S$88,000 + S$25,000
    },
    'total_annual_value': 'S$398,600',  # Recoverable from pain point costs
    'payback_period': '8-10 months'  # At subscription rate of S$500-800/month
}
3. STAKEHOLDER ANALYSIS & USER PERSONAS
3.1 Stakeholder Map
mermaid

graph TD
    A[Platform] --> B[Internal Users]
    A --> C[External Users]
    A --> D[Partners]
    A --> E[Regulators]
    
    B --> B1[Business Owner]
    B --> B2[Operations Manager]
    B --> B3[Accountant]
    B --> B4[Warehouse Staff]
    B --> B5[Sales/CS Team]
    
    C --> C1[Retail Customers]
    C --> C2[B2B Customers]
    C --> C3[Suppliers]
    
    D --> D1[Payment Providers]
    D --> D2[Logistics Partners]
    D --> D3[Marketplace Platforms]
    D --> D4[Accounting Software]
    
    E --> E1[IRAS]
    E --> E2[ACRA]
    E --> E3[PDPC]
    E --> E4[Industry Bodies]
3.2 Detailed User Personas
3.2.1 Primary Persona: Sarah Chen — SMB Owner
Python

persona_sarah = {
    'demographics': {
        'age': '38',
        'education': 'Bachelor\'s in Business',
        'location': 'Singapore (Tanjong Pagar)',
        'business': 'Fashion retail — 2 stores + online'
    },
    'professional_profile': {
        'role': 'Founder & Managing Director',
        'experience': '12 years in retail',
        'team_size': '8 full-time + 4 part-time',
        'annual_revenue': 'S$1.2 million',
        'growth_stage': 'Scaling from offline to omnichannel',
        'channels': ['Physical stores (2)', 'Shopify website', 'Shopee', 'Instagram']
    },
    'tech_profile': {
        'savviness': 'Intermediate',
        'current_tools': ['Shopify', 'Excel', 'QuickBooks', 'WhatsApp Business'],
        'comfort_areas': ['Email', 'Social media', 'Basic accounting'],
        'challenges': ['Complex integrations', 'Technical jargon', 'System administration'],
        'device_preference': 'Mobile (iPhone) for 60% of work'
    },
    'daily_pain_points': [
        'Spends 3 hours/day reconciling sales across 4 channels',
        'Inventory discrepancies cause weekly stockouts (5-8 SKUs)',
        'GST filing takes 3 full days each quarter',
        'No real-time visibility — must wait for month-end reports',
        'Shopee orders sometimes oversell due to sync delays'
    ],
    'goals': [
        'Single dashboard showing all business KPIs on mobile',
        'Automated GST compliance with zero manual filing',
        'Scale to S$3M revenue within 2 years',
        'Reduce operational admin by 50%',
        'Expand to Malaysia market'
    ],
    'success_metrics': [
        {'metric': 'Time on admin', 'current': '20 hrs/week', 'target': '8 hrs/week'},
        {'metric': 'GST filing time', 'current': '3 days/quarter', 'target': '1 hour/quarter'},
        {'metric': 'Inventory accuracy', 'current': '82%', 'target': '99%'},
        {'metric': 'Order processing', 'current': '8 min/order', 'target': '2 min/order'}
    ],
    'quote': "I started this business to design clothes, not to do data entry. I need a system that lets me focus on growth, not operations."
}
3.2.2 Operations Manager: Marcus Tan
Python

persona_marcus = {
    'demographics': {
        'age': '32',
        'education': 'Diploma in Supply Chain',
        'role': 'Operations Manager'
    },
    'responsibilities': [
        'Inventory management across 2 stores + warehouse',
        'Supplier relationship management',
        'Warehouse operations and fulfillment',
        'Staff scheduling and performance',
        'Logistics coordination'
    ],
    'daily_workflow': {
        'morning': 'Check overnight online orders, plan picking routes',
        'midday': 'Manage supplier deliveries, quality checks',
        'afternoon': 'Process shipments, update inventory',
        'evening': 'Reconcile stock levels, prepare next-day picks'
    },
    'pain_points': [
        'Manual stock counts take 4 hours weekly',
        'Overselling on Shopee due to 15-minute sync delays',
        'No automated reorder suggestions',
        'Cannot track product performance by location',
        'Warehouse staff use paper-based picking lists'
    ],
    'needs': [
        'Real-time inventory visibility on mobile',
        'Barcode scanning for warehouse operations',
        'Automated reorder point calculations',
        'Performance dashboards by location',
        'Digital picking lists with route optimization'
    ],
    'success_metrics': [
        {'metric': 'Inventory accuracy', 'target': '> 99%'},
        {'metric': 'Stockout rate', 'target': '< 1%'},
        {'metric': 'Order fulfillment time', 'target': '< 30 minutes'},
        {'metric': 'Inventory turnover', 'target': '20% improvement'}
    ],
    'device_preference': 'Android tablet in warehouse, mobile when visiting stores'
}
3.2.3 Accountant: Priya Kumar
Python

persona_priya = {
    'demographics': {
        'age': '45',
        'education': 'ACCA Qualified',
        'role': 'Part-time Accountant (3 days/week)'
    },
    'responsibilities': [
        'Monthly financial close',
        'GST quarterly filing',
        'Bank reconciliation',
        'Accounts payable/receivable',
        'Annual audit preparation',
        'Cash flow management'
    },
    'current_workflow': {
        'data_sources': ['Shopify export', 'Bank statements', 'Supplier invoices', 'POS reports'],
        'manual_entry': '8 hours/week data entry into QuickBooks',
        'reconciliation': '6 hours/week matching transactions',
        'gst_filing': '3 full days per quarter'
    },
    'pain_points': [
        'Manual data entry from 4 different systems',
        'GST calculation errors (average 2-3 per quarter)',
        'Month-end close takes 5+ days',
        'Audit preparation requires weeks of document gathering',
        'No real-time financial visibility for owner'
    ],
    'needs': [
        'Automated journal entries from sales',
        'Real-time GST calculation with audit trail',
        'Bank feed integration for auto-reconciliation',
        'One-click GST F5 report generation',
        'InvoiceNow integration for B2B invoices'
    ],
    'success_metrics': [
        {'metric': 'GST filing accuracy', 'target': '100%'},
        {'metric': 'Month-end close', 'target': '< 1 day'},
        {'metric': 'Manual data entry', 'target': '85% reduction'},
        {'metric': 'Audit preparation', 'target': '90% reduction'}
    ],
    'compliance_priorities': ['IRAS GST', 'ACRA filing', 'SFRS compliance']
}
3.2.4 End Customer: Wei Ling — Digital Native Shopper
Python

persona_weiling = {
    'demographics': {
        'age': '28',
        'occupation': 'Marketing Executive',
        'location': 'Singapore (Tampines)',
        'income': 'S$4,500/month'
    },
    'shopping_behavior': {
        'device': 'Mobile (95% of shopping)',
        'discovery': ['Instagram', 'TikTok', 'Shopee', 'Google Search'],
        'purchase_frequency': '3-4 times/month online',
        'average_order': 'S$80-150',
        'preferred_payment': ['PayNow', 'GrabPay', 'Credit card installments']
    },
    'expectations': [
        'Page loads in < 2 seconds',
        'Easy checkout without creating account',
        'PayNow QR code for instant payment',
        'Real-time delivery tracking with SMS updates',
        'Easy returns process',
        'Responsive WhatsApp support'
    ],
    'frustrations': [
        'Slow mobile websites',
        'Forced account creation',
        'No PayNow option',
        'Unclear delivery dates',
        'Complicated return process'
    ],
    'decision_factors': [
        {'factor': 'Price', 'weight': 25},
        {'factor': 'Convenience', 'weight': 30},
        {'factor': 'Reviews', 'weight': 20},
        {'factor': 'Delivery speed', 'weight': 15},
        {'factor': 'Return policy', 'weight': 10}
    ]
}
3.2.5 B2B Customer: Ahmad — Wholesale Buyer
Python

persona_ahmad = {
    'demographics': {
        'age': '42',
        'role': 'Procurement Manager',
        'company': 'Retail chain (15 outlets)',
        'purchase_volume': 'S$50,000-100,000/month'
    },
    'requirements': [
        'Wholesale pricing (30% off retail)',
        'NET30 payment terms',
        'Monthly statement of account',
        'Bulk ordering capabilities',
        'Dedicated account manager'
    ],
    'workflow': {
        'ordering': 'Biweekly bulk orders via email/WhatsApp',
        'payment': 'Bank transfer within 30 days',
        'delivery': 'Consolidated delivery to central warehouse',
        'documentation': 'Tax invoice with GST breakdown'
    },
    'pain_points': [
        'Manual order process (email back-and-forth)',
        'No online account with order history',
        'Credit limit not visible',
        'Delayed invoice delivery',
        'No InvoiceNow integration'
    ],
    'needs': [
        'B2B portal with wholesale pricing',
        'Credit limit visibility and management',
        'Online ordering with saved items',
        'Automated invoice via InvoiceNow',
        'Order history and reorder functionality'
    ]
}
3.3 User Journey Maps
3.3.1 Customer Purchase Journey
text

┌─────────────────────────────────────────────────────────────────────────────┐
│                    CUSTOMER PURCHASE JOURNEY                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  AWARENESS (Entry Points)                                                   │
│  ├── Instagram/TikTok → Product Discovery                                   │
│  ├── Google Search → SEO-optimized product pages (SSR)                      │
│  └── Shopee/Lazada → Marketplace listing (synced inventory)                 │
│                                                                             │
│  CONSIDERATION                                                              │
│  ├── Browse Catalog → Fast loading (< 2s), high-quality images              │
│  ├── Product Details → Swipe gallery, reviews, stock availability          │
│  ├── Compare Products → Side-by-side comparison feature                     │
│  └── Add to Wishlist → Saved for later (synced across devices)              │
│                                                                             │
│  DECISION                                                                   │
│  ├── Add to Cart → Real-time inventory check, reservation                   │
│  ├── View Cart → Persistent across sessions, price updates                  │
│  └── Apply Promo → Automatic discount calculation with GST                  │
│                                                                             │
│  PURCHASE                                                                   │
│  ├── Checkout → One-page, mobile-optimized (< 2 min completion)             │
│  ├── Address → OneMap integration for SG address validation                 │
│  ├── Shipping → Real-time carrier rates, estimated delivery                 │
│  ├── Payment → PayNow QR, GrabPay, Credit Card (3D Secure)                  │
│  └── Confirmation → Instant email/SMS with order number                     │
│                                                                             │
│  POST-PURCHASE                                                              │
│  ├── Tracking → Real-time status via SMS/WhatsApp                           │
│  ├── Delivery → Proof of delivery with photo                                │
│  ├── Review → Post-delivery review request (email)                          │
│  └── Support → WhatsApp/live chat for issues                                │
│                                                                             │
│  RETENTION                                                                  │
│  ├── Reorder → Quick reorder from order history                             │
│  ├── Loyalty → Points accumulation (future phase)                           │
│  └── Referral → Share referral code for discount                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
3.3.2 Admin Order Processing Journey
Python

admin_order_journey = {
    'trigger': 'Order placed via any channel (web, mobile, Shopee, Lazada)',
    'steps': [
        {
            'step': '1. Order Received',
            'trigger': 'Webhook from payment gateway or marketplace',
            'actions': [
                'Create order record with unique order number',
                'Send push notification to admin mobile app',
                'Update real-time dashboard',
                'Classify order by channel and priority'
            ],
            'automation_level': '100%',
            'time': 'Instant'
        },
        {
            'step': '2. Inventory Reservation',
            'trigger': 'Order created event',
            'actions': [
                'Check real-time stock across all locations',
                'Reserve items (atomic transaction)',
                'Select optimal fulfillment location',
                'Generate low stock alert if threshold reached'
            ],
            'automation_level': '100%',
            'time': '< 1 second'
        },
        {
            'step': '3. Payment Verification',
            'trigger': 'Payment webhook received',
            'actions': [
                'Confirm payment amount matches order total',
                'Check for fraud flags (Stripe Radar)',
                'Generate GST-compliant invoice',
                'Create accounting journal entry'
            ],
            'automation_level': '100%',
            'time': '< 5 seconds'
        },
        {
            'step': '4. Fulfillment Assignment',
            'trigger': 'Payment confirmed',
            'actions': [
                'Generate digital picking list',
                'Assign to warehouse staff based on load',
                'Calculate optimal picking route',
                'Send mobile notification to picker'
            ],
            'automation_level': '95%',
            'manual_step': 'Staff accepts assignment',
            'time': '< 1 minute'
        },
        {
            'step': '5. Pick & Pack',
            'trigger': 'Assignment accepted',
            'actions': [
                'Display picking list on mobile device',
                'Scan barcodes to confirm items',
                'Weigh package for shipping calculation',
                'Print packing slip and shipping label'
            ],
            'automation_level': '70%',
            'manual_step': 'Physical picking and packing',
            'time': '10-20 minutes'
        },
        {
            'step': '6. Shipping Handoff',
            'trigger': 'Packing completed',
            'actions': [
                'Generate carrier-specific shipping label',
                'Update order status to "Shipped"',
                'Send tracking number to customer (SMS/email)',
                'Deduct inventory from on-hand'
            ],
            'automation_level': '100%',
            'time': '< 1 minute'
        },
        {
            'step': '7. Accounting Posting',
            'trigger': 'Order shipped',
            'actions': [
                'Recognize revenue (if not already)',
                'Update GST output tax ledger',
                'Record COGS if using perpetual inventory',
                'Update real-time P&L dashboard'
            ],
            'automation_level': '100%',
            'time': 'Instant'
        },
        {
            'step': '8. Delivery & Completion',
            'trigger': 'Carrier webhook (delivered)',
            'actions': [
                'Update order status to "Delivered"',
                'Capture proof of delivery',
                'Send delivery confirmation to customer',
                'Trigger review request email (24h delay)'
            ],
            'automation_level': '100%',
            'time': 'Triggered by carrier'
        }
    ],
    'total_processing_time': '< 30 minutes (automated steps)',
    'manual_intervention_rate': '< 5%',
    'error_rate_target': '< 0.1%'
}
4. BUSINESS REQUIREMENTS
4.1 Core Business Capabilities
4.1.1 Unified Commerce Platform
Capability	Description	Business Value	Success Metric
Omnichannel Sales	Single platform for web, mobile, POS, marketplaces	30% revenue increase from channel expansion	Sales per channel
Centralized Inventory	Single source of truth across all locations	60% reduction in stockouts	Inventory accuracy > 99%
Integrated Accounting	Automated financial recording with GST	40% time savings on accounting	Month-end close < 1 day
Marketplace Sync	Real-time sync with Shopee/Lazada	Eliminate overselling	Sync latency < 5 minutes
Customer 360° View	Unified customer data across channels	25% retention improvement	Customer lifetime value
Real-time Analytics	Dashboards updated in real-time	Data-driven decisions	Dashboard refresh < 5s
4.1.2 Compliance Automation
Requirement	Description	Regulatory Basis	Automation Level
GST Calculation	Auto-calculate 9% GST on taxable supplies	IRAS GST Act	100% automated
GST F5 Filing	Generate quarterly GST return	IRAS requirement	98% automated (approval manual)
PDPA Consent	Track customer consent for data use	PDPA 2012	100% automated
Data Retention	Auto-delete data per retention policy	PDPA + IRAS	100% automated
InvoiceNow	E-invoicing for B2B/B2G transactions	IMDA mandate	100% automated
Industry Licenses	Track renewal dates and compliance	SFA/HSA/SPF	90% automated
4.2 Business Process Requirements
4.2.1 Order-to-Cash (O2C) Process
mermaid

graph LR
    A[Order Placed] --> B[Inventory Reserved]
    B --> C[Payment Verified]
    C --> D[Order Picked]
    D --> E[Order Packed]
    E --> F[Shipped]
    F --> G[Delivered]
    G --> H[Invoice Posted]
    H --> I[Revenue Recognized]
    I --> J[GST Recorded]
O2C Process Specifications:

Python

order_to_cash_process = {
    'order_placement': {
        'channels': ['Web', 'Mobile PWA', 'Shopee', 'Lazada', 'POS'],
        'validation': [
            'Real-time inventory check',
            'Customer credit limit (B2B)',
            'Shipping address validation (OneMap)',
            'Payment method availability'
        ],
        'sla': 'Order confirmed within 5 seconds'
    },
    'inventory_reservation': {
        'mechanism': 'Atomic database transaction with row-level locking',
        'timeout': '30 minutes for unpaid orders',
        'conflict_resolution': 'First-come-first-served with queue',
        'multi_location': 'Auto-select nearest location with stock'
    },
    'payment_processing': {
        'gateways': {
            'cards': 'Stripe (3D Secure mandatory)',
            'local_wallets': 'HitPay (PayNow, GrabPay, ShopeePay)',
            'bnpl': 'Atome, Hoolah',
            'b2b': 'Bank transfer with credit terms'
        },
        'reconciliation': 'Automated daily matching with bank feed',
        'refunds': 'Processed within 3-5 business days'
    },
    'fulfillment': {
        'picking': 'Digital pick list with barcode scanning',
        'packing': 'Weight verification, packing slip generation',
        'shipping': 'Auto-select cheapest carrier meeting SLA',
        'tracking': 'Real-time tracking via carrier webhooks'
    },
    'accounting': {
        'revenue_recognition': 'Upon shipment (accrual basis)',
        'gst_recording': 'Output tax recorded at invoice date',
        'cogs_recognition': 'Perpetual inventory method',
        'journal_automation': '100% automated posting'
    },
    'success_metrics': {
        'order_to_ship': '< 24 hours (same-day for orders before 2 PM)',
        'automation_rate': '> 95%',
        'error_rate': '< 0.1%',
        'customer_satisfaction': 'NPS > 50'
    }
}
4.2.2 Procure-to-Pay (P2P) Process
Python

procure_to_pay_process = {
    'reorder_trigger': {
        'automatic': 'Stock falls below reorder point',
        'manual': 'Manager initiates PO for new products',
        'forecast_based': 'ML prediction for seasonal items',
        'safety_stock': 'Based on lead time + demand variability'
    },
    'purchase_order': {
        'creation': 'Auto-generated from reorder trigger',
        'approval_workflow': {
            'under_5000': 'Operations Manager approval',
            'over_5000': 'Owner approval required',
            'new_supplier': 'Dual approval required'
        },
        'supplier_notification': 'Email + supplier portal',
        'confirmation_tracking': 'Auto-escalate if no response in 24h'
    },
    'goods_receipt': {
        'receiving': 'Barcode scan against PO',
        'quality_check': 'Sample inspection for new suppliers',
        'variance_handling': {
            'under_2%': 'Auto-accept',
            'over_2%': 'Manager review required'
        },
        'stock_update': 'Real-time inventory increase'
    },
    'invoice_matching': {
        'three_way_match': 'PO vs. Goods Receipt vs. Supplier Invoice',
        'auto_match': 'Within 2% variance auto-approved',
        'exceptions': 'Routed to AP for manual review'
    },
    'payment': {
        'scheduling': 'Based on payment terms (NET30/NET45)',
        'early_payment_discount': 'Auto-calculate and recommend',
        'payment_methods': ['Bank transfer', 'PayNow (for small suppliers)'],
        'reconciliation': 'Auto-match with bank feed'
    },
    'accounting': {
        'ap_recording': 'At goods receipt (accrual basis)',
        'gst_input_tax': 'Claimed at supplier invoice date',
        'payment_posting': 'AP reduction upon payment',
        'expense_classification': 'Auto-categorize by supplier type'
    },
    'success_metrics': {
        'po_to_receipt': '< 7 days average',
        'invoice_processing': '< 2 days',
        'payment_on_time': '> 98%',
        'early_payment_savings': '2-3% of procurement spend'
    }
}
4.2.3 Marketplace Synchronization Process (New — Gap Resolution)
Python

marketplace_sync_process = {
    'inventory_sync': {
        'direction': 'Bidirectional',
        'frequency': 'Real-time (webhook) + 15-minute polling backup',
        'platforms': ['Shopee', 'Lazada', 'Qoo10', 'Amazon.sg'],
        'conflict_resolution': {
            'strategy': 'Last-write-wins with timestamp comparison',
            'priority': 'Platform with latest sale takes precedence',
            'deadlock_prevention': 'Optimistic locking with retry'
        },
        'oversell_prevention': {
            'buffer_stock': 'Reserve 5% of stock for safety',
            'sync_lock': 'Lock SKU during checkout across all platforms',
            'rollback': 'Release reservation if payment fails within 30 min'
        }
    },
    'order_import': {
        'trigger': 'Platform webhook (order.created)',
        'validation': [
            'Deduplicate by platform order ID',
            'Verify inventory availability',
            'Map platform SKU to internal SKU'
        ],
        'status_sync': 'Push status updates back to platform',
        'tracking_sync': 'Push tracking number when shipped'
    },
    'product_sync': {
        'direction': 'Outbound (platform ← our system)',
        'attributes': ['Name', 'Description', 'Price', 'Stock', 'Images'],
        'pricing_rules': 'Platform-specific markup supported',
        'image_optimization': 'Auto-resize for platform requirements'
    },
    'rate_limiting': {
        'shopee': {
            'calls_per_minute': 100,
            'strategy': 'Token bucket with burst allowance',
            'retry_policy': 'Exponential backoff (1s, 2s, 4s, 8s, max 60s)'
        },
        'lazada': {
            'calls_per_minute': 60,
            'strategy': 'Sliding window',
            'retry_policy': 'Exponential backoff with jitter'
        }
    },
    'error_handling': {
        'api_unavailable': 'Queue requests, retry when available',
        'rate_limited': 'Backoff and batch requests',
        'data_mismatch': 'Log and alert for manual review',
        'circuit_breaker': 'Open after 5 consecutive failures, retry after 5 min'
    },
    'success_metrics': {
        'sync_latency': '< 5 minutes',
        'oversell_rate': '< 0.1%',
        'sync_success_rate': '> 99.5%',
        'api_error_rate': '< 1%'
    }
}
4.3 Business Rules Engine
4.3.1 Pricing & Promotion Rules
Python

class PricingRulesEngine:
    """Business rules for pricing, discounts, and GST calculation"""
    
    def __init__(self, company):
        self.company = company
        self.gst_rate = Decimal('0.09')  # 9% as of 2024
        
    # Customer Tier Pricing
    customer_tiers = {
        'retail': {
            'discount': Decimal('0.00'),
            'minimum_order': Decimal('0'),
            'payment_terms': 'Immediate',
            'gst_treatment': 'standard_rated'
        },
        'vip': {
            'discount': Decimal('0.10'),  # 10% off
            'minimum_order': Decimal('0'),
            'payment_terms': 'Immediate',
            'gst_treatment': 'standard_rated'
        },
        'wholesale': {
            'discount': Decimal('0.30'),  # 30% off
            'minimum_order': Decimal('1000'),
            'payment_terms': 'NET30',
            'credit_limit': Decimal('50000'),
            'gst_treatment': 'standard_rated'
        },
        'distributor': {
            'discount': Decimal('0.40'),  # 40% off
            'minimum_order': Decimal('5000'),
            'payment_terms': 'NET45',
            'credit_limit': Decimal('100000'),
            'gst_treatment': 'standard_rated'
        },
        'export': {
            'discount': Decimal('0.25'),
            'minimum_order': Decimal('2000'),
            'payment_terms': 'Advance payment',
            'gst_treatment': 'zero_rated'  # 0% GST for exports
        }
    }
    
    # Promotion Types
    promotions = {
        'percentage_discount': {
            'calculation': 'subtotal * discount_percentage',
            'stackable': False,
            'gst_applied_after': True
        },
        'fixed_amount': {
            'calculation': 'subtotal - fixed_discount',
            'stackable': False,
            'gst_applied_after': True
        },
        'buy_x_get_y': {
            'calculation': 'Buy X items, get Y items free',
            'stackable': False,
            'gst_on_paid_items_only': True
        },
        'bundle': {
            'calculation': 'Fixed price for product set',
            'gst_applied_to_bundle': True
        },
        'free_shipping': {
            'threshold': Decimal('80'),  # Free shipping over S$80
            'stackable': True
        }
    }
    
    def calculate_order_total(self, order):
        """Calculate order total with all pricing rules applied"""
        
        # 1. Get base prices
        subtotal = sum(item.product.base_price * item.quantity for item in order.items)
        
        # 2. Apply customer tier discount
        tier = order.customer.tier
        tier_discount = subtotal * self.customer_tiers[tier]['discount']
        subtotal_after_tier = subtotal - tier_discount
        
        # 3. Apply promotional discount (if any)
        promo_discount = Decimal('0')
        if order.promo_code:
            promo_discount = self.calculate_promotion(order, subtotal_after_tier)
        subtotal_after_promo = subtotal_after_tier - promo_discount
        
        # 4. Calculate shipping
        shipping = self.calculate_shipping(order, subtotal_after_promo)
        
        # 5. Calculate GST
        gst_treatment = self.customer_tiers[tier]['gst_treatment']
        if gst_treatment == 'standard_rated':
            gst_amount = (subtotal_after_promo + shipping) * self.gst_rate
        else:
            gst_amount = Decimal('0')  # Zero-rated or exempt
        
        # 6. Calculate total
        total = subtotal_after_promo + shipping + gst_amount
        
        return {
            'subtotal': subtotal,
            'tier_discount': tier_discount,
            'promo_discount': promo_discount,
            'shipping': shipping,
            'gst_rate': self.gst_rate if gst_treatment == 'standard_rated' else Decimal('0'),
            'gst_amount': gst_amount,
            'total': total,
            'gst_treatment': gst_treatment
        }
4.3.2 Inventory Rules Engine
Python

class InventoryRulesEngine:
    """Business rules for inventory management"""
    
    # Stock Classification (ABC Analysis)
    stock_classification = {
        'A': {
            'description': 'Top 20% revenue contribution',
            'service_level': 0.99,  # 99% availability target
            'count_frequency': 'daily',
            'safety_stock_days': 14,
            'reorder_frequency': 'weekly'
        },
        'B': {
            'description': 'Next 30% revenue contribution',
            'service_level': 0.95,  # 95% availability
            'count_frequency': 'weekly',
            'safety_stock_days': 10,
            'reorder_frequency': 'biweekly'
        },
        'C': {
            'description': 'Remaining 50% revenue',
            'service_level': 0.90,  # 90% availability
            'count_frequency': 'monthly',
            'safety_stock_days': 7,
            'reorder_frequency': 'monthly'
        }
    }
    
    # Reorder Point Calculation
    def calculate_reorder_point(self, product, location):
        """
        Reorder Point = (Lead Time × Daily Usage) + Safety Stock
        Safety Stock = Z-score × Std Dev × √Lead Time
        """
        
        # Get historical data
        daily_usage = self.get_average_daily_usage(product, days=90)
        std_dev = self.get_usage_std_dev(product, days=90)
        lead_time = product.supplier.lead_time_days
        
        # Get service level Z-score based on classification
        classification = self.get_classification(product)
        service_level = self.stock_classification[classification]['service_level']
        z_score = self.get_z_score(service_level)  # e.g., 2.33 for 99%
        
        # Calculate safety stock
        safety_stock = z_score * std_dev * Decimal(str(math.sqrt(lead_time)))
        
        # Calculate reorder point
        reorder_point = (Decimal(str(lead_time)) * daily_usage) + safety_stock
        
        # Apply seasonal adjustment
        if self.is_peak_season(product.category):
            reorder_point *= Decimal('1.3')  # 30% buffer
        
        return max(reorder_point, product.minimum_stock_level)
    
    # Dead Stock Rules
    dead_stock_rules = {
        'warning': {
            'days_no_sale': 120,
            'action': 'Alert operations manager',
            'markdown': Decimal('0')
        },
        'markdown_1': {
            'days_no_sale': 180,
            'action': 'Auto-markdown 25%',
            'markdown': Decimal('0.25')
        },
        'markdown_2': {
            'days_no_sale': 270,
            'action': 'Auto-markdown 50%',
            'markdown': Decimal('0.50')
        },
        'write_off': {
            'days_no_sale': 365,
            'action': 'Flag for write-off or donation',
            'markdown': Decimal('1.00')
        }
    }
    
    # Multi-Location Allocation Rules
    allocation_rules = {
        'online_orders': {
            'priority': 1,
            'source_preference': ['central_warehouse', 'secondary_warehouse', 'store_1', 'store_2'],
            'split_order': False  # Ship from single location
        },
        'store_orders': {
            'priority': 2,
            'source_preference': ['local_store', 'nearby_store', 'central_warehouse'],
            'split_order': False
        },
        'marketplace_orders': {
            'priority': 1,  # Same as online
            'source_preference': ['central_warehouse', 'secondary_warehouse'],
            'split_order': False
        },
        'b2b_orders': {
            'priority': 3,
            'source_preference': ['central_warehouse'],
            'split_order': True  # Can ship from multiple locations
        }
    }
    
    # Stock Transfer Rules
    transfer_rules = {
        'auto_transfer_trigger': {
            'condition': 'Location A < min_level AND Location B > max_level',
            'transfer_quantity': 'min(B_excess, A_shortfall)',
            'approval_required': False  # Auto-approved
        },
        'manual_transfer': {
            'approval_workflow': 'Operations Manager',
            'min_quantity': 10,
            'documentation': 'Transfer Order required'
        },
        'inter_company_transfer': {
            'gst_treatment': 'Self-billing (no GST if same UEN)',
            'documentation': 'Delivery Order + Invoice',
            'approval_required': True
        }
    }
5. FUNCTIONAL REQUIREMENTS
5.1 E-Commerce Module
5.1.1 Product Catalog Management
Product Data Model:

Python

class Product(models.Model):
    """
    Core product model with GST compliance and mobile optimization.
    Combines best elements from Opus (technical) and Qwen (business rules).
    """
    
    # Identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    barcode = models.CharField(max_length=50, blank=True, db_index=True)
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=255, blank=True)
    
    # Categorization
    category = models.ForeignKey('Category', on_delete=models.PROTECT, related_name='products')
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    
    # Pricing (DECIMAL for financial precision)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # GST Configuration (Singapore-specific)
    GST_TYPES = [
        ('standard_rated', 'Standard Rated (9%)'),
        ('zero_rated', 'Zero Rated (0%)'),
        ('exempt', 'Exempt'),
        ('out_of_scope', 'Out of Scope'),
    ]
    gst_type = models.CharField(max_length=20, choices=GST_TYPES, default='standard_rated')
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('9.00'))
    
    # Inventory Settings
    track_inventory = models.BooleanField(default=True)
    allow_backorder = models.BooleanField(default=False)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    
    # Physical Attributes (for shipping)
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    length_cm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    width_cm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    # Compliance (Industry-specific)
    requires_age_verification = models.BooleanField(default=False)
    requires_prescription = models.BooleanField(default=False)
    license_type = models.CharField(max_length=50, blank=True)  # SFA, HSA, SPF
    batch_tracking_required = models.BooleanField(default=False)
    expiry_tracking_required = models.BooleanField(default=False)
    
    # SEO (for Next.js SSR/SSG)
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    canonical_url = models.URLField(blank=True)
    
    # Mobile Optimization (from Nex-N1)
    mobile_featured = models.BooleanField(default=False)
    quick_buy_enabled = models.BooleanField(default=True)
    swipe_gallery_enabled = models.BooleanField(default=True)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discontinued', 'Discontinued'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='products_created')
    
    class Meta:
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['gst_type']),
        ]
        ordering = ['-created_at']
    
    def get_display_price(self, customer_tier='retail', include_gst=True):
        """Calculate display price with tier discount and GST"""
        
        # Apply tier discount
        tier_discount = CUSTOMER_TIERS.get(customer_tier, {}).get('discount', Decimal('0'))
        price_after_discount = self.base_price * (1 - tier_discount)
        
        # Apply GST if required
        if include_gst and self.gst_type == 'standard_rated':
            price_with_gst = price_after_discount * (1 + self.gst_rate / 100)
            return price_with_gst.quantize(Decimal('0.01'))
        
        return price_after_discount.quantize(Decimal('0.01'))
    
    def get_available_quantity(self, location=None):
        """Get available quantity across all or specific location"""
        
        queryset = self.stock_levels.filter(quantity_available__gt=0)
        
        if location:
            queryset = queryset.filter(location=location)
        
        return queryset.aggregate(total=Sum('quantity_available'))['total'] or 0
Product Variant Model:

Python

class ProductVariant(models.Model):
    """
    Product variants for size, color, etc.
    Each variant has its own SKU, pricing, and inventory.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    
    # Identification
    sku = models.CharField(max_length=50, unique=True, db_index=True)
    barcode = models.CharField(max_length=50, blank=True, db_index=True)
    
    # Variant Attributes (flexible JSON)
    attributes = models.JSONField(default=dict)  # e.g., {"size": "M", "color": "Blue"}
    
    # Pricing (can override base product price)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Physical 
