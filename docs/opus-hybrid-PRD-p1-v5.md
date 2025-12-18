Phase 1: Deep Analysis & Synthesis Planning
1.1 Systematic Element Extraction
Before creating the hybrid PRD, I must methodically identify the optimal elements from each source document:

Element Extraction Matrix
PRD Section	Nex-N1 Contribution	Opus Contribution	Qwen Contribution	My Additions
Executive Summary	Basic structure	ROI timeline	✅ Best: Quantified business case, NPV	28-week timeline adjustment
Market Analysis	Mobile statistics	Market size data	✅ Best: Growth trajectory, competitive analysis	Multi-currency market context
User Personas	Basic personas	Stakeholder map	✅ Best: Python-structured personas with metrics	B2B buyer persona
Business Requirements	E-commerce features	Process automation	✅ Best: Business rules engine, process mapping	Lite Mode toggle
E-commerce Module	✅ Best: Mobile-first, PWA, UX	Cart/checkout specs	Pricing rules	Offline POS capability
Inventory Module	Real-time tracking	Multi-location models	✅ Best: Reordering algorithms, intelligence	Redis inventory locking
Accounting Module	Basic GST mention	GST engine, schemas	✅ Best: F5 validation, IRAS integration	Multi-currency accounting
Payment Module	Payment methods list	✅ Best: Multi-gateway architecture	PayNow implementation	Rate limiting, fallbacks
Logistics Module	Carrier list	✅ Best: Integration framework	Fulfillment workflow	Offline sync
Technical Architecture	Next.js frontend stack	✅ Best: Django backend, DB schemas	Technology justification	MVP vs Scale profiles
Compliance Framework	PDPA mention	InvoiceNow basic	✅ Best: Complete GST/PDPA/PEPPOL	Industry license automation
Security	PCI DSS mention	✅ Best: Complete security framework	Breach response	Enhanced threat modeling
Performance	Load time targets	✅ Best: Scalability architecture	—	Realistic benchmarks
Implementation	32-week timeline	✅ Best: 24-week sprint structure	Validation checkpoints	28-week adjusted timeline
Risk Management	Basic risks	Good coverage	✅ Best: Mitigation strategies	Marketplace sync risks
Budget	Cost estimates	✅ Best: Detailed budget	ROI analysis	PSG grant integration
1.2 Hybrid Architecture Decision Matrix
Backend Framework: Django (Confirmed)
Decision Factor	Weight	Django Score	Node.js Score	Winner
Financial Precision (Decimal)	25%	10/10	6/10	Django
Built-in Admin Panel	20%	10/10	2/10	Django
ORM Data Integrity	15%	10/10	7/10	Django
Compliance Libraries	15%	9/10	5/10	Django
Development Speed	15%	9/10	7/10	Django
AI/ML Integration	10%	10/10	6/10	Django
Weighted Total	100%	9.5/10	5.5/10	Django
Frontend Framework: Next.js (Confirmed)
Decision Factor	Weight	Next.js Score	Django Templates Score	Winner
Mobile Performance	25%	10/10	5/10	Next.js
SEO Capabilities	20%	10/10	7/10	Next.js
PWA Support	20%	10/10	4/10	Next.js
Developer Experience	15%	9/10	7/10	Next.js
Component Ecosystem	10%	10/10	5/10	Next.js
Real-time Features	10%	9/10	6/10	Next.js
Weighted Total	100%	9.7/10	5.5/10	Next.js
1.3 Document Structure Plan
text

HYBRID PRD STRUCTURE (28 Sections)
│
├── PART 1: FOUNDATION & CORE REQUIREMENTS (This Response)
│   ├── 1. Document Control
│   ├── 2. Executive Summary
│   ├── 3. Market Analysis & Business Context
│   ├── 4. Stakeholder Analysis & User Personas
│   ├── 5. Business Requirements
│   ├── 6. Functional Requirements: E-Commerce Module
│   ├── 7. Functional Requirements: Inventory Management Module
│   └── 8. Technical Architecture
│
└── PART 2: IMPLEMENTATION & OPERATIONS (Next Response)
    ├── 9. Functional Requirements: Accounting Module
    ├── 10. Functional Requirements: Payment Processing Module
    ├── 11. Functional Requirements: Logistics & Fulfillment Module
    ├── 12. Compliance & Regulatory Framework
    ├── 13. Security Implementation
    ├── 14. Performance & Scalability
    ├── 15. Implementation Roadmap
    ├── 16. Quality Assurance & Testing
    ├── 17. Budget & Resource Planning
    ├── 18. Risk Management & Mitigation
    ├── 19. Success Metrics & KPIs
    ├── 20. Future Roadmap & Vision
    └── Appendices
1.4 Implementation Plan Validation
Pre-Execution Checklist
Validation Criterion	Status	Notes
All three PRDs analyzed	✅ Complete	Strengths/weaknesses documented
Hybrid architecture justified	✅ Complete	Decision matrices above
Gap analysis incorporated	✅ Complete	7 gaps identified and addressed
Singapore compliance complete	✅ Planned	GST, PDPA, PEPPOL, industry licenses
Business value quantified	✅ Planned	ROI, NPV, payback period
Developer actionability	✅ Planned	Code samples, schemas, API specs
Stakeholder accessibility	✅ Planned	Executive summaries per section
MVP vs Scale profiles	✅ Planned	Infrastructure flexibility
Timeline realistic	✅ Planned	28 weeks with buffer
Document length appropriate	✅ Planned	~15,000 words Part 1, ~15,000 words Part 2
Quality Gates for Each Section
Python

quality_gates = {
    'technical_depth': {
        'code_samples': 'Required for all complex logic',
        'sql_schemas': 'Required for all data models',
        'api_specs': 'Required for all endpoints',
        'validation': 'Engineering team can implement directly'
    },
    'business_context': {
        'roi_metrics': 'Quantified for major features',
        'process_mapping': 'Visual diagrams for workflows',
        'success_criteria': 'Measurable KPIs defined',
        'validation': 'Business stakeholders can understand value'
    },
    'compliance_rigor': {
        'regulatory_mapping': 'IRAS, PDPC, ACRA requirements linked',
        'audit_support': 'Documentation generation specified',
        'penalty_avoidance': 'Risk quantified in SGD',
        'validation': 'Legal/compliance team can verify'
    },
    'implementation_clarity': {
        'timeline': 'Week-by-week breakdown',
        'dependencies': 'Clear sequencing',
        'validation_checkpoints': 'Go/no-go criteria defined',
        'validation': 'Project manager can execute'
    }
}
1.5 Execution Authorization
✅ VALIDATION COMPLETE — PROCEEDING TO EXECUTION

The synthesis approach has been validated against all quality criteria. I will now generate Part 1 of the comprehensive Hybrid PRD, incorporating:

Structure: Qwen's accessible organization
Technical Depth: Opus's production-ready specifications
Frontend Excellence: Nex-N1's mobile-first approach
Enhancements: My identified gaps and recommendations
📋 SINGAPORE SMB E-COMMERCE & INTEGRATED BUSINESS PLATFORM
COMPREHENSIVE PROJECT REQUIREMENTS DOCUMENT
Version 4.0 — Hybrid Architecture Edition
SECTION 1: DOCUMENT CONTROL
1.1 Document Information
Attribute	Details
Document Title	Singapore SMB E-Commerce & Integrated Business Platform PRD
Version	4.0 — Hybrid Architecture Edition
Date	December 2024
Status	Final — Ready for Implementation
Document Type	Master Project Requirements Document
Confidentiality	Proprietary and Confidential
Review Cycle	Quarterly Updates
Distribution	Authorized Stakeholders Only
1.2 Version History
Version	Date	Author	Changes
1.0	Nov 2024	Nex-N1 Team	Initial Node.js/Next.js PRD
2.0	Nov 2024	Opus Team	Django comprehensive specification
3.0	Dec 2024	Qwen Team	Strategic synthesis with business context
4.0	Dec 2024	Hybrid Team	Ultimate synthesis: Django backend + Next.js frontend, all compliance frameworks, MVP/Scale profiles
1.3 Document Conventions
Convention	Meaning
MUST	Mandatory requirement — system will not be accepted without this
SHOULD	Strongly recommended — deviation requires documented justification
MAY	Optional enhancement — implement if time/budget permits
[MVP]	Required for Minimum Viable Product launch
[SCALE]	Required when system exceeds defined thresholds
[SG-COMPLIANCE]	Singapore regulatory requirement
[LITE-MODE]	Can be hidden/disabled for Micro-SMB users
1.4 Approval Signatures
Role	Name	Signature	Date
Project Sponsor			
Technical Director			
Finance Director			
Compliance Officer			
Operations Director			
SECTION 2: EXECUTIVE SUMMARY
2.1 Project Vision
This document presents the definitive blueprint for developing Singapore's most comprehensive SMB e-commerce platform, built on a Hybrid Architecture that combines:

Django (Python) Backend — For financial precision, compliance automation, and operational reliability
Next.js (React) Frontend — For consumer-grade mobile experience and SEO excellence
Unified Data Layer — Single source of truth across e-commerce, inventory, and accounting
The Three Pillars
text

┌─────────────────────────────────────────────────────────────────────────────┐
│                     PLATFORM INTEGRATION ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐          │
│   │   E-COMMERCE    │   │    INVENTORY    │   │   ACCOUNTING    │          │
│   │   STOREFRONT    │   │   MANAGEMENT    │   │    & FINANCE    │          │
│   ├─────────────────┤   ├─────────────────┤   ├─────────────────┤          │
│   │ • Next.js PWA   │   │ • Multi-location│   │ • Double-entry  │          │
│   │ • Mobile-first  │   │ • Real-time sync│   │ • GST automation│          │
│   │ • <2s load time │   │ • 99.5% accuracy│   │ • IRAS filing   │          │
│   │ • 70% mobile    │   │ • Barcode/QR    │   │ • PDPA compliant│          │
│   └────────┬────────┘   └────────┬────────┘   └────────┬────────┘          │
│            │                     │                     │                    │
│            └─────────────────────┼─────────────────────┘                    │
│                                  │                                          │
│                    ┌─────────────▼─────────────┐                            │
│                    │   DJANGO REST FRAMEWORK   │                            │
│                    │   Unified API Gateway     │                            │
│                    └─────────────┬─────────────┘                            │
│                                  │                                          │
│                    ┌─────────────▼─────────────┐                            │
│                    │      POSTGRESQL 15+       │                            │
│                    │   Single Source of Truth  │                            │
│                    └───────────────────────────┘                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
2.2 Problem Statement
Singapore SMBs face a fragmentation crisis:

Problem	Current State	Business Impact	Annual Cost
System Fragmentation	5-7 different software tools	40% time on data reconciliation	S$67,200/business
Inventory Inaccuracy	77% average accuracy	15% lost sales from stockouts	S$88,000 revenue loss
GST Compliance Errors	3.2 errors per quarter	IRAS penalties and audits	S$60,000 penalty costs
Manual Data Entry	16 hours/week	Limited growth capacity	S$38,400 opportunity cost
Poor Mobile Experience	68% checkout abandonment	Lost conversion opportunities	S$120,000 revenue potential
TOTAL ANNUAL COST			S$373,600/business
2.3 Solution Value Proposition
Quantified Business Impact
Python

value_proposition = {
    'operational_efficiency': {
        'metric': 'Manual Data Entry Reduction',
        'current': '16 hours/week',
        'target': '6.4 hours/week',
        'improvement': '60% reduction',
        'annual_savings': 'S$38,400',
        'calculation': '9.6 hours × S$25/hour × 52 weeks × 3 staff'
    },
    'inventory_optimization': {
        'metric': 'Inventory Accuracy',
        'current': '77%',
        'target': '99.5%',
        'improvement': '22.5 percentage points',
        'annual_value': 'S$88,000',
        'calculation': '15% revenue recovery from eliminated stockouts'
    },
    'compliance_automation': {
        'metric': 'GST Filing Errors',
        'current': '3.2 errors/quarter',
        'target': '0 errors',
        'improvement': '100% elimination',
        'annual_savings': 'S$60,000',
        'calculation': 'Average penalty avoidance + audit cost reduction'
    },
    'revenue_growth': {
        'metric': 'Checkout Completion Rate',
        'current': '32%',
        'target': '65%',
        'improvement': '33 percentage points',
        'annual_value': 'S$180,000',
        'calculation': 'Mobile conversion lift × average order value × traffic'
    },
    'order_processing': {
        'metric': 'Order Processing Time',
        'current': '8.5 minutes',
        'target': '2.1 minutes',
        'improvement': '75% reduction',
        'annual_savings': 'S$24,000',
        'calculation': 'Labor cost savings from automation'
    }
}

total_annual_value = 'S$390,400'  # Sum of all value components
Investment Summary
Investment Category	Amount	Notes
Development Budget	S$800,000 — S$950,000	28-week development cycle
Annual Operations	S$280,000 — S$360,000	Infrastructure + support + licenses
PSG Grant Eligible	Up to S$30,000	50% co-funding for qualifying SMBs
Break-even Point	50-60 active SMB clients	At S$500/month/client average
ROI Timeline	12-18 months	Full investment recovery
5-Year NPV	S$4.8 million	Discount rate: 10%
Payback Period	14 months	Conservative estimate
2.4 Strategic Objectives
Objective	Target Outcome	Success Metric	Measurement
Operational Excellence	60% reduction in manual processes	Time saved per transaction	Weekly automated reporting
Regulatory Compliance	100% GST and PDPA compliance	Zero penalties/violations	Quarterly compliance audit
Inventory Optimization	99.5% stock accuracy	Cycle count variance	Daily automated reconciliation
Mobile Experience	<2 second page load	Google PageSpeed >90	Real-time monitoring
Financial Visibility	Real-time P&L and cash flow	Dashboard refresh <5 seconds	Continuous monitoring
Market Capture	100 active SMBs in 12 months	Monthly active users	Monthly business review
2.5 Technology Decision Summary
Hybrid Architecture Justification
Layer	Technology Choice	Justification
Backend Framework	Django 5.0+ (Python 3.12+)	Financial precision (Decimal), built-in admin, ORM integrity, compliance libraries
API Layer	Django REST Framework 3.14+	Industry-standard REST APIs, OpenAPI documentation, authentication
Async Processing	Celery 5.3+ with Redis	Background tasks, scheduled jobs, webhook processing
Frontend Framework	Next.js 14+ (React 18+)	Mobile performance, SEO, PWA capabilities, developer ecosystem
Database	PostgreSQL 15+	ACID compliance, DECIMAL precision, PostGIS, JSON support
Cache Layer	Redis 7.0+	Session storage, caching, real-time inventory locks
Search Engine	PostgreSQL tsvector [MVP] / Elasticsearch [SCALE]	Cost-effective search with upgrade path
File Storage	AWS S3 with CloudFront CDN	Scalable media storage with global distribution
Infrastructure	AWS Singapore (ap-southeast-1)	Data residency compliance, low latency
SECTION 3: MARKET ANALYSIS & BUSINESS CONTEXT
3.1 Singapore E-Commerce Landscape
3.1.1 Market Size & Growth Trajectory
text

SINGAPORE E-COMMERCE MARKET GROWTH
│
│  US$5.6B ─────────────────────────────────────────────● 2026 (Projected)
│                                                      ╱
│  US$5.0B ────────────────────────────────────────●──╱  2025
│                                                 ╱
│  US$4.5B ────────────────────────────────●─────╱     2024 (Current)
│                                         ╱
│  US$4.1B ─────────────────────────●────╱             2023
│                                  ╱
│  US$3.8B ────────────────●──────╱                    2022
│                         ╱
│  US$3.2B ─────────●────╱                             2021
│                  ╱
│  US$2.5B ──●────╱                                    2020
│           ╱
└──────────┴──────────────────────────────────────────────────────▶ Year
           CAGR: 11.2%
3.1.2 Key Market Drivers
Python

market_drivers = {
    'digital_infrastructure': {
        'internet_penetration': 98.5,  # % of population
        'smartphone_ownership': 95.2,  # % of adults
        'avg_mobile_data_speed': '79.1 Mbps',  # 5th globally
        'digital_literacy_score': 86.7,  # out of 100
        '5g_coverage': 95.0  # % of population covered
    },
    'payment_evolution': {
        'paynow_adoption': {
            'total_registrations': '9.6 million',  # As of 2024
            'yoy_growth': 28.5,  # %
            'gen_z_preference': 68.3,  # % prefer PayNow
            'business_adoption': 76.8  # % of SMBs accept PayNow
        },
        'digital_wallets': {
            'e_commerce_share': 39.0,  # % of transactions
            'grabpay_users': '2.8 million',
            'shopeepay_users': '1.5 million'
        },
        'bnpl_growth': {
            'yoy_growth': 215.0,  # %
            'avg_transaction': 'S$180',
            'primary_demographic': '25-34 years'
        }
    },
    'mobile_commerce': {
        'mobile_traffic_share': 70.0,  # % of e-commerce traffic
        'mobile_conversion_rate': 2.8,  # % (vs desktop 4.2%)
        'mobile_conversion_gap': 'S$1.2B untapped revenue',
        'app_usage_growth': 45.0  # % YoY
    },
    'government_support': {
        'psg_grants': {
            'max_amount': 'S$30,000',
            'co_funding_rate': 50,  # %
            'eligible_solutions': 'Pre-approved digital solutions'
        },
        'digital_apis': ['SingPass', 'CorpPass', 'MyInfo', 'OneMap', 'PayNow Corporate'],
        'sme_go_digital': 'S$500M allocated (2023-2025)',
        'industry_transformation_maps': 23  # ITMs covering major sectors
    },
    'cross_border_trade': {
        'online_shoppers_buying_overseas': 65.0,  # %
        'primary_markets': ['China', 'USA', 'Japan', 'Korea'],
        'regional_e_commerce_hub': True,
        'asean_market_access': '680 million consumers'
    }
}
3.1.3 Competitive Landscape
Platform Type	Market Share	Key Players	Monthly Fees	Commission	SMB Pain Points
Marketplaces	60%	Shopee, Lazada, Amazon.sg, Qoo10	S$0-50	8-20%	High fees, limited branding, inventory fragmentation
SaaS Platforms	25%	Shopify, WooCommerce, Wix	S$30-300	0-2%	Separate accounting, GST gaps, integration costs
Custom Solutions	15%	Bespoke development	S$0	0%	S$200K+ development, 12+ month timeline
Our Competitive Position
text

┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPETITIVE DIFFERENTIATION MATRIX                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                          INTEGRATION DEPTH                                   │
│                               HIGH                                          │
│                                ▲                                            │
│                                │                                            │
│         [Custom ERP]           │           ★ [OUR PLATFORM]                 │
│         High cost              │           Best value                       │
│         Long timeline          │           Full integration                 │
│                                │           PSG eligible                     │
│     LOW ◄──────────────────────┼──────────────────────────► HIGH           │
│     AFFORDABILITY              │                           AFFORDABILITY    │
│                                │                                            │
│         [Marketplaces]         │           [SaaS Platforms]                 │
│         Commission-heavy       │           Partial integration              │
│         Limited control        │           Multiple tools needed            │
│                                │                                            │
│                               LOW                                           │
│                          INTEGRATION DEPTH                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
3.2 Target Market Definition
3.2.1 Primary Target Segments
Segment	Annual Revenue	Employees	SKU Range	Complexity	Platform Mode
Micro-SMB	S$100K — S$500K	1-10	50-200	Low	LITE MODE
Small SMB	S$500K — S$2M	10-50	200-1,000	Medium	STANDARD MODE
Medium SMB	S$2M — S$10M	50-200	1,000-5,000	High	ADVANCED MODE
3.2.2 Industry Vertical Focus
Python

industry_verticals = {
    'retail_general': {
        'market_share': 35.0,  # % of target market
        'sub_categories': [
            'Fashion & Apparel',
            'Electronics & Gadgets', 
            'Home & Living',
            'Sports & Outdoor'
        ],
        'key_requirements': [
            'Multi-variant products (size, color, material)',
            'Seasonal inventory management',
            'Customer segmentation and loyalty',
            'Returns management'
        ],
        'avg_order_value': 'S$85',
        'mobile_traffic': 75.0,  # %
        'priority_features': ['Quick checkout', 'Visual search', 'Size guides']
    },
    'food_beverage': {
        'market_share': 25.0,  # % of target market
        'sub_categories': [
            'Restaurants & Cafes',
            'Packaged Food Products',
            'Bakeries & Confectionery',
            'Health Foods & Supplements'
        ],
        'key_requirements': [
            'Ingredient/batch inventory tracking',
            'Expiry date management',
            'Temperature-sensitive logistics',
            'HSA/SFA compliance'
        ],
        'regulatory_bodies': [
            'Singapore Food Agency (SFA)',
            'Health Sciences Authority (HSA)',
            'National Environment Agency (NEA)'
        ],
        'special_licenses': ['Food Shop License', 'Import Permit', 'Halal Certification'],
        'priority_features': ['Batch tracking', 'Expiry alerts', 'Recipe costing']
    },
    'health_beauty': {
        'market_share': 20.0,  # % of target market
        'sub_categories': [
            'Cosmetics & Skincare',
            'Health Supplements',
            'Personal Care',
            'Wellness Products'
        ],
        'key_requirements': [
            'Product registration tracking',
            'Batch/lot traceability',
            'Recall management capability',
            'HSA notification compliance'
        ],
        'regulatory_bodies': ['Health Sciences Authority (HSA)'],
        'compliance_requirements': [
            'ASEAN Cosmetic Directive',
            'Product notification before sale',
            'Adverse event reporting (15 days)'
        ],
        'priority_features': ['Ingredient lists', 'Batch recall', 'Expiry tracking']
    },
    'b2b_wholesale': {
        'market_share': 20.0,  # % of target market
        'sub_categories': [
            'Industrial Supplies',
            'Office Products',
            'Building Materials',
            'Packaging Supplies'
        ],
        'key_requirements': [
            'Tiered/volume pricing',
            'Bulk ordering workflows',
            'Account management with credit terms',
            'Purchase order integration'
        ],
        'payment_terms': ['Net 30', 'Net 45', 'Net 60', 'COD'],
        'credit_limits': 'S$5,000 - S$500,000',
        'priority_features': ['Quote requests', 'Credit management', 'Reorder automation']
    }
}
SECTION 4: STAKEHOLDER ANALYSIS & USER PERSONAS
4.1 Comprehensive Stakeholder Map
text

                                    ┌─────────────────┐
                                    │    PLATFORM     │
                                    └────────┬────────┘
                                             │
            ┌────────────────────────────────┼────────────────────────────────┐
            │                                │                                │
            ▼                                ▼                                ▼
    ┌───────────────┐               ┌───────────────┐               ┌───────────────┐
    │   INTERNAL    │               │   EXTERNAL    │               │   ECOSYSTEM   │
    │    USERS      │               │    USERS      │               │   PARTNERS    │
    └───────┬───────┘               └───────┬───────┘               └───────┬───────┘
            │                                │                                │
    ┌───────┴───────┐               ┌───────┴───────┐               ┌───────┴───────┐
    │               │               │               │               │               │
    ▼               ▼               ▼               ▼               ▼               ▼
┌─────────┐   ┌─────────┐     ┌─────────┐   ┌─────────┐     ┌─────────┐   ┌─────────┐
│ Business│   │Operations│     │End      │   │B2B      │     │Payment  │   │Logistics│
│ Owner   │   │ Manager │     │Customers│   │ Buyers  │     │Gateways │   │Partners │
└─────────┘   └─────────┘     └─────────┘   └─────────┘     └─────────┘   └─────────┘
                │                                                   │
        ┌───────┴───────┐                               ┌───────────┴───────────┐
        ▼               ▼                               ▼                       ▼
  ┌─────────┐     ┌─────────┐                     ┌─────────┐             ┌─────────┐
  │Accountant│    │Warehouse│                     │Government│            │Accounting│
  │         │     │ Staff   │                     │ (IRAS,   │            │ Software │
  └─────────┘     └─────────┘                     │  PDPC)   │            │ (Xero)   │
                        │                         └─────────┘             └─────────┘
                        ▼
                  ┌─────────┐
                  │  Sales  │
                  │  Staff  │
                  └─────────┘
4.2 Detailed User Personas
4.2.1 Primary Persona: Sarah Chen — SMB Owner
Python

persona_sarah_chen = {
    'identity': {
        'name': 'Sarah Chen',
        'age': 38,
        'role': 'Founder & Managing Director',
        'company': 'Urban Threads Pte Ltd',
        'industry': 'Fashion Retail',
        'location': 'Singapore (Tanjong Pagar)'
    },
    'business_profile': {
        'annual_revenue': 'S$1.8 million',
        'growth_rate': '22% YoY',
        'employees': 12,
        'channels': ['2 retail stores', 'Shopify website', 'Shopee', 'Lazada'],
        'product_range': '450 SKUs across 8 collections',
        'customer_base': '8,500 registered customers',
        'avg_order_value': 'S$95'
    },
    'technology_profile': {
        'tech_savviness': 'Intermediate',
        'current_tools': [
            'Shopify (e-commerce)',
            'Xero (accounting)',
            'Google Sheets (inventory)',
            'WhatsApp Business (customer service)',
            'Mailchimp (email marketing)'
        ],
        'pain_with_current_tools': [
            'Manual sync between Shopify and Xero (2 hours/day)',
            'Inventory discrepancies between channels (3.2% average)',
            'GST calculation errors during quarterly filing',
            'No real-time visibility across all channels'
        ],
        'device_usage': {
            'primary': 'MacBook Pro (office)',
            'secondary': 'iPhone 14 Pro (on-the-go)',
            'tertiary': 'iPad (store operations)'
        }
    },
    'daily_challenges': [
        {
            'challenge': 'Reconciling sales across 4 channels',
            'time_spent': '2 hours/day',
            'frustration_level': 'High',
            'current_workaround': 'Manual spreadsheet consolidation'
        },
        {
            'challenge': 'Inventory sync between locations',
            'time_spent': '45 minutes/day',
            'frustration_level': 'Critical',
            'current_workaround': 'Morning stock calls to each store'
        },
        {
            'challenge': 'Quarterly GST filing',
            'time_spent': '3 full days/quarter',
            'frustration_level': 'Very High',
            'current_workaround': 'External accountant at S$800/quarter'
        },
        {
            'challenge': 'Overselling on marketplaces',
            'frequency': '2-3 times/week',
            'frustration_level': 'Critical',
            'current_workaround': 'Refunds and apology emails'
        }
    ],
    'goals': {
        'short_term': [
            'Unified dashboard for all channels (1 month)',
            'Automated inventory sync (2 months)',
            'Zero overselling incidents (3 months)'
        ],
        'medium_term': [
            'Self-service GST filing (6 months)',
            'Real-time P&L visibility (6 months)',
            'Expand to 3rd retail location (12 months)'
        ],
        'long_term': [
            'Scale to S$5M revenue (3 years)',
            'Regional expansion to Malaysia (4 years)',
            'Exit-ready business operations (5 years)'
        ]
    },
    'success_metrics': {
        'time_saved': '15+ hours/week on administration',
        'inventory_accuracy': '>99% across all channels',
        'gst_compliance': 'Zero filing errors',
        'revenue_growth': '25% YoY',
        'customer_satisfaction': 'NPS >50'
    },
    'platform_mode': 'STANDARD MODE',
    'budget_for_solution': 'S$500-800/month',
    'decision_factors': [
        'Ease of use (can train staff in 1 day)',
        'Singapore-specific (GST, PayNow built-in)',
        'Shopee/Lazada integration',
        'Mobile app for on-the-go management'
    ]
}
4.2.2 Operations Manager: Marcus Tan
Python

persona_marcus_tan = {
    'identity': {
        'name': 'Marcus Tan',
        'age': 32,
        'role': 'Operations Manager',
        'reports_to': 'Sarah Chen (Owner)',
        'direct_reports': 4,  # 2 warehouse staff, 2 retail staff
        'tenure': '3 years'
    },
    'responsibilities': [
        'Inventory management across 2 warehouse locations',
        'Supplier relationship management (15 active suppliers)',
        'Order fulfillment and shipping coordination',
        'Staff scheduling and performance tracking',
        'Receiving and quality control'
    ],
    'daily_workflow': {
        '8:00 AM': 'Review overnight orders and stock levels',
        '9:00 AM': 'Morning call with retail stores for stock issues',
        '10:00 AM': 'Process marketplace orders (Shopee, Lazada)',
        '11:00 AM': 'Coordinate with logistics partners',
        '2:00 PM': 'Supplier calls and PO management',
        '4:00 PM': 'Physical stock counts (2x weekly)',
        '5:00 PM': 'End-of-day reporting to owner'
    },
    'pain_points': {
        'critical': [
            {
                'issue': 'Inventory sync delays between channels',
                'impact': '2-3 overselling incidents per week',
                'cost': 'S$150/incident in refunds + reputation damage'
            },
            {
                'issue': 'Manual stock counts',
                'time_spent': '4 hours/week',
                'accuracy': 'Still 3-4% variance'
            }
        ],
        'high': [
            {
                'issue': 'No automated reorder alerts',
                'impact': 'Stockouts on bestsellers (12% revenue loss)',
                'current_workaround': 'Weekly spreadsheet review'
            },
            {
                'issue': 'No barcode scanning',
                'impact': 'Slow receiving process (45 min/delivery)',
                'current_workaround': 'Manual counting and data entry'
            }
        ],
        'medium': [
            {
                'issue': 'Difficulty tracking product performance by location',
                'impact': 'Suboptimal stock allocation',
                'current_workaround': 'End-of-month Excel analysis'
            }
        ]
    },
    'needs': {
        'must_have': [
            'Real-time inventory visibility across ALL channels',
            'Mobile barcode scanning for warehouse operations',
            'Automated reorder point alerts',
            'Shopee/Lazada inventory sync (< 5 minute delay)'
        ],
        'should_have': [
            'Performance dashboards for warehouse staff',
            'Supplier lead time tracking',
            'Automated PO generation',
            'Cycle counting schedules'
        ],
        'nice_to_have': [
            'Demand forecasting',
            'Warehouse layout optimization',
            'Pick path optimization'
        ]
    },
    'success_metrics': {
        'inventory_accuracy': '>99.5%',
        'stockout_rate': '<1%',
        'order_fulfillment_time': '<30 minutes',
        'receiving_time': '<15 minutes/delivery',
        'inventory_turnover': '20% improvement YoY'
    },
    'technology_comfort': {
        'mobile_apps': 'High',
        'barcode_scanners': 'High',
        'spreadsheets': 'Expert',
        'erp_systems': 'Low (no experience)'
    }
}
4.2.3 Accountant: Priya Kumar
Python

persona_priya_kumar = {
    'identity': {
        'name': 'Priya Kumar',
        'age': 45,
        'role': 'Finance Manager (Part-time, 3 days/week)',
        'qualifications': 'ACCA Certified',
        'experience': '18 years in SMB accounting',
        'other_clients': 4  # Manages accounting for 5 SMBs total
    },
    'responsibilities': [
        'Monthly financial reporting',
        'Quarterly GST filing (F5/F7)',
        'Bank reconciliation',
        'Accounts payable management',
        'Annual filing (ACRA, IRAS)',
        'Audit preparation'
    ],
    'pain_points': {
        'critical': [
            {
                'issue': 'Manual data entry from multiple sources',
                'time_spent': '6 hours/week',
                'error_rate': '2-3 errors per 100 entries',
                'impact': 'GST miscalculations'
            },
            {
                'issue': 'GST calculation complexity',
                'challenge': 'Different rates for different product types',
                'error_frequency': '1-2 errors per quarterly filing',
                'penalty_risk': 'S$5,000-15,000 per error'
            }
        ],
        'high': [
            {
                'issue': 'Month-end close takes too long',
                'current_time': '5 business days',
                'target_time': '1 business day',
                'bottleneck': 'Waiting for sales data consolidation'
            },
            {
                'issue': 'Audit preparation',
                'current_time': '3 weeks',
                'pain': 'Chasing down supporting documents'
            }
        ]
    },
    'needs': {
        'must_have': [
            'Automated journal entries from sales transactions',
            'Real-time GST calculation with supply type classification',
            'One-click GST F5/F7 report generation',
            'Bank feed integration for automatic reconciliation',
            'Complete audit trail for all transactions'
        ],
        'should_have': [
            'XBRL report generation for ACRA filing',
            'Multi-currency support for overseas purchases',
            'Supplier payment scheduling with cash flow forecast',
            'Automated bad debt write-off workflows'
        ],
        'nice_to_have': [
            'Predictive cash flow analysis',
            'Tax planning scenarios',
            'Integration with other client systems'
        ]
    },
    'success_metrics': {
        'gst_accuracy': '100% (zero errors)',
        'month_end_close': '<1 business day',
        'data_entry_automation': '85% reduction',
        'audit_prep_time': '90% reduction',
        'client_time_per_month': '50% reduction'
    },
    'software_experience': {
        'xero': 'Expert',
        'quickbooks': 'Proficient',
        'myob': 'Familiar',
        'sap': 'Basic',
        'excel': 'Expert'
    },
    'regulatory_knowledge': {
        'gst_act': 'Expert',
        'companies_act': 'Proficient',
        'income_tax_act': 'Expert',
        'pdpa': 'Familiar'
    }
}
4.2.4 End Customer: Digital Native Shopper
Python

persona_customer = {
    'identity': {
        'name': 'Jessica Lim',
        'age': 29,
        'occupation': 'Marketing Executive',
        'location': 'Singapore (Tampines)',
        'household_income': 'S$8,000-12,000/month'
    },
    'shopping_behavior': {
        'primary_device': 'iPhone 13',  # 85% of shopping
        'secondary_device': 'MacBook Air',  # 15% of shopping
        'shopping_frequency': '3-4 times/month online',
        'avg_basket_size': 'S$120',
        'preferred_categories': ['Fashion', 'Beauty', 'Home Decor'],
        'discovery_channels': ['Instagram', 'TikTok', 'Google Search', 'Friends']
    },
    'payment_preferences': {
        'primary': 'PayNow (68% of transactions)',
        'secondary': 'Credit Card (Apple Pay)',
        'bnpl_usage': 'Occasional (Atome for larger purchases)',
        'reasons_for_paynow': ['Instant', 'No card details needed', 'Cashback']
    },
    'expectations': {
        'page_load': '<2 seconds',
        'checkout_steps': '≤3 steps',
        'delivery_options': ['Same-day', 'Next-day', 'Click & Collect'],
        'tracking': 'Real-time with SMS/WhatsApp updates',
        'returns': 'Free returns within 14 days',
        'support': 'Live chat response <5 minutes'
    },
    'frustrations': {
        'critical': [
            'Slow mobile sites (will abandon if >3 seconds)',
            'Out of stock after adding to cart',
            'No PayNow option'
        ],
        'high': [
            'Having to create account before checkout',
            'No delivery time window options',
            'Cannot track order in real-time'
        ],
        'medium': [
            'Limited product photos',
            'No size guide',
            'Complicated return process'
        ]
    },
    'loyalty_triggers': [
        'Personalized recommendations',
        'Birthday discounts',
        'Free shipping over S$50',
        'Exclusive member pricing',
        'Easy reorder of past purchases'
    ]
}
4.2.5 B2B Buyer: Corporate Procurement (New Persona)
Python

persona_b2b_buyer = {
    'identity': {
        'name': 'David Wong',
        'age': 42,
        'role': 'Procurement Manager',
        'company': 'Singapore General Hospital (SGH)',
        'department': 'Facilities Management',
        'purchasing_authority': 'Up to S$50,000'
    },
    'procurement_profile': {
        'annual_spend': 'S$2.5 million (with various suppliers)',
        'order_frequency': 'Weekly bulk orders',
        'avg_order_value': 'S$5,000-15,000',
        'payment_terms': 'Net 30 (government standard)',
        'approval_workflow': '2-level (Manager → Director for >S$10,000)'
    },
    'requirements': {
        'must_have': [
            'Tiered pricing (volume discounts)',
            'Credit terms (Net 30/45/60)',
            'GST invoice with breakdown',
            'Purchase order integration',
            'Delivery to multiple locations'
        ],
        'should_have': [
            'Quote request workflow',
            'Approval routing',
            'Contract pricing agreements',
            'Scheduled/recurring orders',
            'Statement of account'
        ],
        'nice_to_have': [
            'EDI integration',
            'Punch-out catalog',
            'Budget tracking per cost center'
        ]
    },
    'pain_points': [
        'Manual quote requests via email',
        'No visibility into order history',
        'Inconsistent pricing across orders',
        'Difficulty tracking deliveries to multiple sites'
    ],
    'success_metrics': {
        'order_processing_time': '<10 minutes',
        'price_consistency': '100%',
        'invoice_accuracy': '100%',
        'on_time_delivery': '>98%'
    },
    'platform_mode': 'B2B MODE (Advanced)',
    'features_needed': ['Quote system', 'Credit management', 'Multi-location delivery', 'Invoice portal']
}
SECTION 5: BUSINESS REQUIREMENTS
5.1 Core Business Capabilities
5.1.1 Unified Commerce Platform
Capability	Description	Business Value	Success Metric	Mode
Omnichannel Sales	Sell across web, mobile, POS, Shopee, Lazada from single platform	30% revenue increase from channel expansion	Channel revenue growth rate	[MVP]
Centralized Inventory	Single source of truth for stock across all locations and channels	60% reduction in stockouts	Inventory accuracy >99.5%	[MVP]
Integrated Accounting	Automated financial recording with GST compliance	40% time savings on accounting	Month-end close <1 day	[MVP]
Customer 360° View	Unified customer profile with purchase history across channels	25% customer retention improvement	Customer lifetime value	[MVP]
Real-time Analytics	Live business intelligence with predictive capabilities	Data-driven decisions	Dashboard load <5 seconds	[MVP]
B2B Commerce	Tiered pricing, credit terms, quote workflows	Access to B2B market segment	B2B revenue share	[LITE-MODE OFF]
5.1.2 Platform Mode Configuration
Python

platform_modes = {
    'lite_mode': {
        'target_users': 'Micro-SMBs (S$100K-500K revenue)',
        'hidden_features': [
            'Multi-location inventory',
            'Advanced accounting (journal entries)',
            'B2B features (credit terms, quotes)',
            'FIFO/LIFO costing methods',
            'Purchase order 3-way matching',
            'Advanced reporting (custom reports)',
            'API access',
            'Multi-currency'
        ],
        'simplified_ui': {
            'dashboard': 'Single KPI panel (Sales, Orders, Low Stock)',
            'inventory': 'Simple in/out tracking',
            'accounting': 'Revenue and expense summary only',
            'gst': 'Automated calculation, simplified F5'
        },
        'upgrade_triggers': [
            'Revenue exceeds S$500K',
            'SKUs exceed 200',
            'Second location added',
            'Staff exceeds 5'
        ],
        'monthly_price': 'S$99'
    },
    'standard_mode': {
        'target_users': 'Small SMBs (S$500K-2M revenue)',
        'all_features': True,
        'advanced_features_available': [
            'Multi-location inventory (up to 3)',
            'Full double-entry accounting',
            'Standard B2B features',
            'Average cost method',
            'Standard reporting suite'
        ],
        'monthly_price': 'S$299'
    },
    'advanced_mode': {
        'target_users': 'Medium SMBs (S$2M-10M revenue)',
        'all_features': True,
        'enterprise_features': [
            'Unlimited locations',
            'FIFO/LIFO/Weighted Average costing',
            'Full B2B suite with credit management',
            'Custom reporting and BI',
            'API access',
            'Multi-currency accounting',
            'Advanced forecasting',
            'Dedicated support'
        ],
        'monthly_price': 'S$599'
    }
}
5.2 Business Process Requirements
5.2.1 Order-to-Cash Process
text

┌─────────────────────────────────────────────────────────────────────────────┐
│                         ORDER-TO-CASH WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐     │
│  │ORDER │───▶│STOCK │───▶│PAYMENT│───▶│ PICK │───▶│ PACK │───▶│ SHIP │     │
│  │PLACED│    │RESERVE│   │VERIFY │    │      │    │      │    │      │     │
│  └──────┘    └──────┘    └──────┘    └──────┘    └──────┘    └──────┘     │
│      │           │           │           │           │           │         │
│      ▼           ▼           ▼           ▼           ▼           ▼         │
│  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐     │
│  │Notify│    │Lock  │    │Auto- │    │Picklist│   │Label │    │Track │     │
│  │Staff │    │Redis │    │Reconcile│  │Generated│ │Print │    │Update│     │
│  └──────┘    └──────┘    └──────┘    └──────┘    └──────┘    └──────┘     │
│                                                                             │
│      ┌──────┐    ┌──────┐    ┌──────┐                                      │
│      │DELIVER│───▶│INVOICE│───▶│REVENUE│                                    │
│      │      │    │ POST │    │RECOGNIZE│                                    │
│      └──────┘    └──────┘    └──────┘                                      │
│          │           │           │                                          │
│          ▼           ▼           ▼                                          │
│      ┌──────┐    ┌──────┐    ┌──────┐                                      │
│      │POD   │    │GST   │    │P&L   │                                      │
│      │Capture│   │Calculate│ │Update│                                      │
│      └──────┘    └──────┘    └──────┘                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

AUTOMATION LEVEL: 95%
MANUAL INTERVENTION: <5% of orders (exceptions only)
TOTAL PROCESS TIME: <2 minutes (order to fulfillment start)
5.2.2 Procure-to-Pay Process
Python

procure_to_pay_workflow = {
    'stages': [
        {
            'stage': '1. Reorder Trigger',
            'trigger_conditions': [
                'Stock falls below reorder point',
                'Forecast predicts stockout within lead time',
                'Manual request from operations'
            ],
            'automation': 'System generates PO suggestion with quantities',
            'human_action': 'Manager reviews and approves/modifies',
            'sla': 'Suggestion generated within 5 minutes of trigger'
        },
        {
            'stage': '2. Purchase Order Creation',
            'automation': [
                'Auto-populate supplier details from master data',
                'Apply contract pricing if available',
                'Calculate landed cost estimate',
                'Set expected delivery date based on lead time'
            ],
            'approval_workflow': {
                'under_5000': 'Auto-approve',
                '5000_to_20000': 'Operations Manager approval',
                'over_20000': 'Owner approval required'
            },
            'sla': 'PO created within 10 minutes of approval'
        },
        {
            'stage': '3. Supplier Confirmation',
            'automation': [
                'Email PO to supplier automatically',
                'Track confirmation status',
                'Auto-escalate if no response in 24 hours'
            ],
            'integration': 'Supplier portal for self-service confirmation',
            'sla': 'Confirmation expected within 24 hours'
        },
        {
            'stage': '4. Goods Receipt',
            'automation': [
                'Barcode scanning against PO',
                'Quantity validation',
                'Quality check routing (if configured)',
                'Automatic stock level update'
            ],
            'exception_handling': {
                'short_shipment': 'Flag for supplier follow-up',
                'over_shipment': 'Require manager authorization',
                'quality_issue': 'Route to QC hold area'
            },
            'sla': 'Receiving completed within 15 minutes of delivery'
        },
        {
            'stage': '5. Invoice Matching',
            'automation': [
                '3-way match: PO ↔ GRN ↔ Invoice',
                'Auto-approve if variance < 2%',
                'Flag discrepancies for review'
            ],
            'tolerance_settings': {
                'quantity': '±2%',
                'price': '±1%',
                'tax': 'Exact match required'
            },
            'sla': 'Matching completed within 1 hour of invoice receipt'
        },
        {
            'stage': '6. Payment Scheduling',
            'automation': [
                'Calculate optimal payment date (cash flow)',
                'Apply early payment discount if beneficial',
                'Generate payment batch for approval'
            ],
            'payment_terms_support': ['Immediate', 'Net 7', 'Net 30', 'Net 45', 'Net 60'],
            'sla': 'Payment scheduled within payment terms'
        },
        {
            'stage': '7. Payment Execution',
            'automation': [
                'Bank API integration for payment',
                'Automatic reconciliation on confirmation',
                'Supplier notification of payment'
            ],
            'payment_methods': ['PayNow Corporate', 'GIRO', 'Telegraphic Transfer'],
            'sla': 'Payment executed on scheduled date'
        }
    ],
    'success_metrics': {
        'cycle_time': '<5 days from reorder to payment',
        'automation_rate': '>90% of POs processed without intervention',
        'matching_accuracy': '>98% first-time match rate',
        'early_payment_capture': '>80% of available discounts captured'
    }
}
5.3 Business Rules Engine
5.3.1 Pricing Rules
Python

class PricingRulesEngine:
    """Comprehensive pricing rules for all customer segments"""
    
    def __init__(self):
        self.customer_tiers = {
            'retail': {
                'formula': lambda base_price: base_price,
                'min_order': Decimal('0'),
                'payment_terms': 'immediate',
                'description': 'Standard retail pricing'
            },
            'member': {
                'formula': lambda base_price: base_price * Decimal('0.95'),
                'min_order': Decimal('0'),
                'payment_terms': 'immediate',
                'description': '5% member discount'
            },
            'vip': {
                'formula': lambda base_price: base_price * Decimal('0.90'),
                'min_order': Decimal('200'),
                'payment_terms': 'immediate',
                'description': '10% VIP discount, min order S$200'
            },
            'wholesale': {
                'formula': lambda base_price: base_price * Decimal('0.70'),
                'min_order': Decimal('1000'),
                'payment_terms': 'net_30',
                'description': '30% wholesale discount, min order S$1,000'
            },
            'distributor': {
                'formula': lambda base_price: base_price * Decimal('0.55'),
                'min_order': Decimal('5000'),
                'payment_terms': 'net_45',
                'description': '45% distributor discount, min order S$5,000'
            }
        }
        
        self.promotion_types = {
            'percentage_discount': {
                'application': 'Apply percentage off line item or order total',
                'stackable': False,
                'max_discount': Decimal('0.50'),  # Cap at 50% off
                'examples': ['10OFF', 'SUMMER20', 'FLASH30']
            },
            'fixed_amount': {
                'application': 'Fixed dollar amount off order total',
                'stackable': False,
                'min_order_required': True,
                'examples': ['SAVE10', 'MINUS20']
            },
            'buy_x_get_y': {
                'application': 'Buy X items, get Y items free/discounted',
                'stackable': False,
                'examples': ['BUY2GET1', 'BUY3GET1FREE']
            },
            'bundle_pricing': {
                'application': 'Fixed price for product combination',
                'stackable': False,
                'examples': [
                    {'bundle': ['shirt_white', 'tie_blue', 'cufflinks'], 'price': Decimal('89.00')}
                ]
            },
            'volume_discount': {
                'application': 'Discount based on quantity purchased',
                'tiers': [
                    {'min_qty': 10, 'discount': Decimal('0.05')},
                    {'min_qty': 25, 'discount': Decimal('0.10')},
                    {'min_qty': 50, 'discount': Decimal('0.15')},
                    {'min_qty': 100, 'discount': Decimal('0.20')}
                ]
            },
            'flash_sale': {
                'application': 'Time-limited discount',
                'duration': 'Configurable (hours/days)',
                'auto_revert': True,
                'notification': 'Push notification to subscribers'
            },
            'first_purchase': {
                'application': 'New customer first order discount',
                'one_time_use': True,
                'typical_discount': Decimal('0.15')
            }
        }
        
        self.gst_rules = {
            'standard_rated': {
                'rate': Decimal('0.09'),
                'applicable_to': 'Local sales of taxable goods/services',
                'gst_f5_box': 'Box 1'
            },
            'zero_rated': {
                'rate': Decimal('0.00'),
                'applicable_to': 'Exports, international services',
                'gst_f5_box': 'Box 2',
                'documentation_required': ['Export permit', 'Bill of lading']
            },
            'exempt': {
                'rate': None,  # No GST charged or claimed
                'applicable_to': 'Financial services, residential property',
                'gst_f5_box': 'Box 3'
            },
            'out_of_scope': {
                'rate': None,
                'applicable_to': 'Private transactions, government services',
                'gst_f5_box': 'Not reported'
            }
        }
    
    def calculate_price(self, product, quantity, customer, promotions=None):
        """Calculate final price with all applicable rules"""
        
        # Start with base price
        base_price = product.base_price
        
        # Apply customer tier pricing
        tier = self.customer_tiers.get(customer.tier, self.customer_tiers['retail'])
        tier_price = tier['formula'](base_price)
        
        # Apply volume discount if applicable
        volume_discount = self.get_volume_discount(quantity)
        after_volume = tier_price * (1 - volume_discount)
        
        # Calculate line total
        line_total = after_volume * quantity
        
        # Apply promotional discounts (one at a time, best for customer)
        if promotions:
            best_promo_price = self.apply_best_promotion(line_total, promotions)
            line_total = best_promo_price
        
        # Calculate GST
        gst_type = product.gst_type
        gst_amount = self.calculate_gst(line_total, gst_type)
        
        return {
            'base_price': base_price,
            'tier_price': tier_price,
            'quantity': quantity,
            'subtotal': line_total,
            'gst_type': gst_type,
            'gst_rate': self.gst_rules[gst_type]['rate'],
            'gst_amount': gst_amount,
            'total': line_total + (gst_amount or Decimal('0'))
        }
5.3.2 Inventory Rules
Python

inventory_rules = {
    'stock_classification': {
        'abc_analysis': {
            'a_items': {
                'criteria': 'Top 20% by revenue contribution',
                'service_level': 99,  # % target
                'review_frequency': 'Daily',
                'safety_stock_days': 14,
                'reorder_method': 'Fixed interval + safety stock'
            },
            'b_items': {
                'criteria': 'Next 30% by revenue',
                'service_level': 95,  # %
                'review_frequency': 'Weekly',
                'safety_stock_days': 10,
                'reorder_method': 'Reorder point'
            },
            'c_items': {
                'criteria': 'Remaining 50%',
                'service_level': 90,  # %
                'review_frequency': 'Monthly',
                'safety_stock_days': 7,
                'reorder_method': 'Economic order quantity'
            }
        }
    },
    'reorder_point_formula': {
        'formula': '(Lead Time × Average Daily Usage) + Safety Stock',
        'safety_stock_formula': 'Z-score × σ × √Lead Time',
        'z_scores': {
            90: 1.28,
            95: 1.65,
            99: 2.33
        },
        'seasonal_adjustment': {
            'peak_months': ['November', 'December'],  # 11.11, 12.12
            'adjustment_factor': 1.5
        }
    },
    'dead_stock_management': {
        'identification_criteria': {
            'warning': 'No sales in 90 days',
            'critical': 'No sales in 180 days',
            'write_off_candidate': 'No sales in 270 days'
        },
        'automated_actions': {
            'at_90_days': 'Alert operations manager',
            'at_120_days': 'Suggest 15% markdown',
            'at_150_days': 'Suggest 30% markdown',
            'at_180_days': 'Suggest 50% markdown or bundling',
            'at_270_days': 'Suggest donation or write-off'
        },
        'markdown_approval': {
            'up_to_20_percent': 'Auto-approve',
            '20_to_50_percent': 'Manager approval',
            'over_50_percent': 'Owner approval'
        }
    },
    'multi_location_allocation': {
        'priority_order': [
            'Primary warehouse (default source)',
            'Nearest warehouse to delivery address',
            'Any warehouse with available stock'
        ],
        'transfer_rules': {
            'auto_transfer_trigger': 'Location stock < min AND another location > max',
            'minimum_transfer_qty': 10,  # units
            'transfer_cost_threshold': 'S$50 minimum to justify transfer'
        }
    },
    'marketplace_sync': {
        'buffer_percentage': 10,  # Reserve 10% for own channel
        'sync_frequency': 'Real-time (webhook-based)',
        'oversell_prevention': {
            'method': 'Redis distributed lock',
            'lock_duration': 30,  # seconds
            'retry_attempts': 3
        }
    }
}
SECTION 6: FUNCTIONAL REQUIREMENTS — E-COMMERCE MODULE
6.1 Storefront Requirements
6.1.1 Product Catalog Management
Python

class Product(models.Model):
    """Core product model with full Singapore e-commerce requirements"""
    
    # ─────────────────────────────────────────────────────────────
    # CORE IDENTIFICATION
    # ─────────────────────────────────────────────────────────────
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='products')
    sku = models.CharField(max_length=50, db_index=True)
    barcode = models.CharField(max_length=50, blank=True, null=True)  # EAN-13 or UPC
    
    # ─────────────────────────────────────────────────────────────
    # PRODUCT INFORMATION
    # ─────────────────────────────────────────────────────────────
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    tags = models.ManyToManyField('Tag', blank=True)
    
    # ─────────────────────────────────────────────────────────────
    # PRICING (Using Decimal for financial precision) [SG-COMPLIANCE]
    # ─────────────────────────────────────────────────────────────
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # GST Configuration [SG-COMPLIANCE]
    GST_TYPE_CHOICES = [
        ('standard_rated', 'Standard Rated (9%)'),
        ('zero_rated', 'Zero Rated (0%)'),
        ('exempt', 'Exempt'),
        ('out_of_scope', 'Out of Scope'),
    ]
    gst_type = models.CharField(max_length=20, choices=GST_TYPE_CHOICES, default='standard_rated')
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('9.00'))
    
    # ─────────────────────────────────────────────────────────────
    # INVENTORY SETTINGS
    # ─────────────────────────────────────────────────────────────
    track_inventory = models.BooleanField(default=True)
    allow_backorder = models.BooleanField(default=False)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    
    # For perishable goods (F&B, Health & Beauty) [INDUSTRY-SPECIFIC]
    is_perishable = models.BooleanField(default=False)
    shelf_life_days = models.PositiveIntegerField(null=True, blank=True)
    requires_refrigeration = models.BooleanField(default=False)
    
    # ─────────────────────────────────────────────────────────────
    # SHIPPING & LOGISTICS
    # ─────────────────────────────────────────────────────────────
    weight_kg = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    dimensions = models.JSONField(default=dict, blank=True)  # {"length": 10, "width": 5, "height": 2, "unit": "cm"}
    requires_special_handling = models.BooleanField(default=False)
    shipping_class = models.CharField(max_length=50, default='standard')
    
    # ─────────────────────────────────────────────────────────────
    # SEO & MARKETING
    # ─────────────────────────────────────────────────────────────
    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    canonical_url = models.URLField(blank=True)
    schema_markup = models.JSONField(default=dict, blank=True)  # JSON-LD structured data
    
    # ─────────────────────────────────────────────────────────────
    # MOBILE OPTIMIZATION [CRITICAL - 70% MOBILE TRAFFIC]
    # ─────────────────────────────────────────────────────────────
    mobile_featured = models.BooleanField(default=False)
    quick_buy_enabled = models.BooleanField(default=True)
    swipe_gallery_enabled = models.BooleanField(default=True)
    
    # ─────────────────────────────────────────────────────────────
    # STATUS & VISIBILITY
    # ─────────────────────────────────────────────────────────────
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('discontinued', 'Discontinued'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visible_on_storefront = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    
    # Scheduled publishing
    publish_date = models.DateTimeField(null=True, blank=True)
    unpublish_date = models.DateTimeField(null=True, blank=True)
    
    # ─────────────────────────────────────────────────────────────
    # COMPLIANCE & AUDIT [SG-COMPLIANCE]
    # ─────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='products_created')
    last_modified_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='products_modified')
    
    # Industry-specific compliance
    hsa_notification_number = models.CharField(max_length=50, blank=True)  # Health products
    sfa_license_required = models.BooleanField(default=False)  # Food products
    age_restricted = models.BooleanField(default=False)  # Alcohol, tobacco
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'sku']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['featured', 'status']),
            models.Index(fields=['gst_type']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['company', 'sku'], 
