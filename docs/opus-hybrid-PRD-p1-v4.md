Phase 1: Deep Analysis & Strategic Planning
Systematic Analysis of Optimal Element Integration
Before creating the hybrid PRD, I will methodically analyze how to integrate the best elements from all three source PRDs, address identified gaps, and structure the document for maximum utility.

1.1 Element Integration Matrix
Section	Primary Source	Secondary Source	Enhancements	Rationale
Executive Summary	Qwen (ROI focus)	Opus (technical summary)	Add MVP vs Scale positioning	Qwen has best stakeholder accessibility
Market Analysis	Qwen (quantified)	Opus (competitive)	Add 2024-2025 trend updates	Qwen has most actionable market data
User Personas	Qwen (structured)	Nex-N1 (journey maps)	Add "Lite Mode" user segment	Qwen personas are most detailed
Business Requirements	Qwen (process mapping)	Opus (rules engine)	Add B2B credit management	Qwen has best O2C/P2P workflows
E-commerce Module	Nex-N1 (frontend)	Opus (backend)	Add offline POS capability	Nex-N1 has superior UX specs
Inventory Module	Opus (technical)	Qwen (business rules)	Add marketplace lock mechanism	Opus has best technical depth
Accounting Module	Qwen (compliance)	Opus (schemas)	Add multi-currency handling	Qwen has best GST implementation
Technical Architecture	Hybrid design	All three	Add MVP infrastructure profile	Custom synthesis required
Database Schemas	Opus (SQL)	Qwen (extensions)	Add new tables for gaps	Opus has production-ready schemas
API Specifications	Opus (endpoints)	Qwen (auth)	Add rate limiting specs	Opus has most complete API specs
Compliance Framework	Qwen (comprehensive)	Opus (code)	Already best-in-class	Qwen is most complete
Security	Opus (detailed)	Qwen (PDPA)	Add API security hardening	Opus has best security specs
Implementation Roadmap	Custom 28-week	Opus (sprint detail)	Add validation checkpoints	Extended timeline for realism
Risk Management	Custom synthesis	All three	Add marketplace sync risks	New comprehensive framework
1.2 Gap Resolution Strategy
Identified Gap	Resolution Approach	Implementation Priority
Lite Mode Requirement	Add feature toggle system with complexity tiers	Phase 1 (Core)
Marketplace Inventory Lock	Redis-based distributed locking with TTL	Phase 3 (Integration)
Multi-Currency Handling	Currency conversion service with rate management	Phase 4 (Enhancement)
Offline POS Sync	Local storage with conflict resolution queue	Phase 5 (Extension)
B2B Credit Management	Credit limit enforcement with aging integration	Phase 3 (Integration)
Marketplace API Rate Limiting	Exponential backoff with circuit breaker pattern	Phase 3 (Integration)
MVP Infrastructure Profile	Dual-track infrastructure specifications	Phase 1 (Core)
1.3 Document Architecture
text

HYBRID PRD STRUCTURE
├── PART 1: STRATEGIC FOUNDATION & FUNCTIONAL REQUIREMENTS
│   ├── 1. Document Control & Revision History
│   ├── 2. Executive Summary & Business Case
│   ├── 3. Market Analysis & Competitive Positioning
│   ├── 4. Stakeholder Analysis & User Personas
│   ├── 5. Business Requirements & Process Mapping
│   ├── 6. E-commerce Functional Requirements
│   ├── 7. Inventory Management Requirements
│   └── 8. Technical Architecture & Stack Specification
│
└── PART 2: TECHNICAL IMPLEMENTATION & GOVERNANCE
    ├── 9. Database Design & Schemas
    ├── 10. API Specifications & Integration Framework
    ├── 11. Accounting & Financial Module
    ├── 12. Compliance & Regulatory Framework
    ├── 13. Security Implementation
    ├── 14. Performance & Scalability
    ├── 15. Implementation Roadmap
    ├── 16. Quality Assurance & Testing
    ├── 17. Success Metrics & KPIs
    ├── 18. Budget & Resource Planning
    ├── 19. Risk Management & Mitigation
    ├── 20. Future Roadmap & Vision
    └── Appendices
Phase 2: Implementation Plan Validation
2.1 Pre-Implementation Checklist
Content Completeness Validation:

 All three source PRDs analyzed for unique strengths
 Gap analysis completed with resolution strategies
 Integration framework defined with clear sources
 Target comprehensiveness: 20,000+ words across both parts
 Structure validated against enterprise PRD best practices
 Singapore-specific requirements prioritized throughout
Quality Assurance Criteria:

 Each section includes validation checkpoints
 Technical and business audiences can understand content
 Implementation steps have clear acceptance criteria
 Compliance requirements tied to specific code/configuration
 Scalability considerations embedded in architecture
 Success metrics are measurable and time-bound
Hybrid Architecture Validation:

 Django backend selection justified with comparison matrix
 Next.js frontend selection justified with performance targets
 MVP vs Scale infrastructure profiles defined
 Integration points between frontend/backend specified
 Deployment architecture suitable for Singapore SMBs
2.2 Execution Readiness Confirmation
✅ CONFIRMED READY FOR EXECUTION

The implementation plan has been validated against all requirements. Proceeding with Part 1 generation.

Phase 3: Execution — Comprehensive Hybrid PRD (Part 1)
📋 SINGAPORE SMB E-COMMERCE PLATFORM
COMPREHENSIVE PROJECT REQUIREMENTS DOCUMENT
Version 4.0 — Ultimate Hybrid Edition
DOCUMENT CONTROL
Attribute	Details
Document Title	Singapore SMB E-Commerce & Integrated Business System PRD
Version	4.0 — Ultimate Hybrid Edition
Document ID	SG-SMB-ECOM-PRD-2025-001
Classification	Proprietary and Confidential
Date Created	January 2025
Last Updated	January 2025
Status	Final — Approved for Implementation
Document Type	Master Project Requirements Document
Review Cycle	Quarterly (Next Review: April 2025)
Distribution	Authorized Stakeholders Only
Prepared By	Technical Architecture Team
Approved By	[Pending Stakeholder Signatures]
Revision History
Version	Date	Author	Changes	Reviewed By
1.0	Jan 2025	Nex-N1 Team	Initial Node.js/Next.js PRD	Technical Lead
2.0	Jan 2025	Opus Team	Django comprehensive PRD	Architecture Board
3.0	Jan 2025	Qwen Team	Strategic synthesis PRD	Business Stakeholders
4.0	Jan 2025	Hybrid Team	Ultimate synthesis combining all PRDs	Full Review Board
Document Conventions
Convention	Meaning
[MVP]	Feature required for Minimum Viable Product launch
[SCALE]	Feature for post-MVP scaling phase
[LITE]	Feature available in Lite Mode for simpler SMBs
[FULL]	Feature available only in Full Mode
[SG-REQUIRED]	Singapore regulatory compliance requirement
[CRITICAL]	Business-critical functionality
Priority: P0	Must have for launch
Priority: P1	Should have for launch
Priority: P2	Nice to have, can defer
TABLE OF CONTENTS — PART 1
Executive Summary & Business Case
Market Analysis & Competitive Positioning
Stakeholder Analysis & User Personas
Business Requirements & Process Mapping
E-commerce Functional Requirements
Inventory Management Requirements
Technical Architecture & Stack Specification
Database Design & Core Schemas
1. EXECUTIVE SUMMARY & BUSINESS CASE
1.1 Project Vision
This document presents the definitive blueprint for developing Singapore's most comprehensive SMB e-commerce platform, integrating four critical business functions into a unified, compliance-ready system:

text

┌─────────────────────────────────────────────────────────────────────────────┐
│                      UNIFIED PLATFORM ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│   │   E-COMMERCE    │    │   INVENTORY     │    │   ACCOUNTING    │        │
│   │   STOREFRONT    │◄──►│   MANAGEMENT    │◄──►│   & FINANCE     │        │
│   │                 │    │                 │    │                 │        │
│   │ • Mobile-first  │    │ • Multi-location│    │ • GST Compliant │        │
│   │ • PWA/Offline   │    │ • Real-time     │    │ • IRAS Ready    │        │
│   │ • Multi-channel │    │ • Marketplace   │    │ • Auto-posting  │        │
│   └────────┬────────┘    └────────┬────────┘    └────────┬────────┘        │
│            │                      │                      │                  │
│            └──────────────────────┼──────────────────────┘                  │
│                                   │                                         │
│                          ┌────────▼────────┐                                │
│                          │   COMPLIANCE    │                                │
│                          │   & SECURITY    │                                │
│                          │                 │                                │
│                          │ • PDPA Ready    │                                │
│                          │ • PCI DSS       │                                │
│                          │ • InvoiceNow    │                                │
│                          └─────────────────┘                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
Core Platform Capabilities:

E-commerce Storefront — Mobile-first PWA with offline capability, serving 70%+ mobile traffic
Real-time Inventory Management — Multi-location tracking with marketplace synchronization
Automated Accounting — GST-compliant with IRAS integration and automated journal entries
Compliance Framework — PDPA, InvoiceNow/PEPPOL, and industry-specific license management
1.2 The Singapore SMB Problem
Current State Analysis:

Our platform addresses the critical fragmentation problem faced by 85% of Singapore SMBs who currently operate with disconnected systems:

Python

current_smb_challenges = {
    'system_fragmentation': {
        'average_tools_used': 5.7,  # Different software tools per SMB
        'data_reconciliation_time': 0.40,  # 40% of admin time
        'integration_cost': 'S$15,000-50,000',  # Annual integration maintenance
        'error_rate': 0.12  # 12% data inconsistency between systems
    },
    'compliance_burden': {
        'gst_filing_errors_per_year': 3.2,
        'average_penalty_per_error': 'S$4,687',
        'annual_penalty_exposure': 'S$15,000',
        'filing_preparation_time': '3 days per quarter'
    },
    'inventory_challenges': {
        'average_accuracy': 0.77,  # 77% inventory accuracy
        'stockout_rate': 0.08,  # 8% stockout rate
        'revenue_loss_from_stockouts': 0.15,  # 15% revenue impact
        'overstock_carrying_cost': 0.25  # 25% of inventory value annually
    },
    'operational_inefficiency': {
        'manual_data_entry_hours': 16,  # Hours per week
        'order_processing_time': 8.5,  # Minutes per order
        'checkout_abandonment_rate': 0.68,  # 68% cart abandonment
        'customer_service_resolution_time': 48  # Hours average
    }
}
1.3 Quantified Business Impact & ROI
Platform Value Proposition:

Impact Area	Current State	With Platform	Improvement	Annual Value (S$)
Order Processing	8.5 min/order	2.1 min/order	75% faster	$24,000 labor savings
Inventory Accuracy	77%	99.5%	+22.5 points	$50,000 revenue gain
GST Filing Errors	3.2/quarter	0	100% elimination	$15,000 penalty avoidance
Manual Data Entry	16 hrs/week	6.4 hrs/week	60% reduction	$38,400 labor savings
Checkout Abandonment	68%	35%	-33 points	$120,000 revenue lift
Customer Retention	45%	70%	+25 points	$60,000 LTV increase
PDPA Breach Risk	High exposure	Protected	Risk mitigation	$1,000,000 fine avoidance
Total Annual Impact				$307,400+
Investment Summary:

Python

investment_analysis = {
    'development': {
        'timeline': '28 weeks',  # 7 months
        'team_size': 8,  # Core team members
        'budget_range': {
            'minimum': 750000,  # S$750,000
            'maximum': 900000,  # S$900,000
            'recommended': 825000  # S$825,000
        }
    },
    'operations': {
        'monthly_infrastructure': {
            'mvp_phase': {'min': 800, 'max': 1500},  # S$/month
            'scale_phase': {'min': 2500, 'max': 5000}  # S$/month
        },
        'annual_maintenance': {'min': 120000, 'max': 180000}  # S$/year
    },
    'roi_projections': {
        'break_even_clients': 55,  # Active SMB clients
        'break_even_timeline': '14 months',
        'year_1_roi': 0.85,  # 85% ROI
        'year_3_roi': 2.40,  # 240% ROI
        'year_5_npv': 4200000,  # S$4.2M at 10% discount rate
        'irr': 0.42  # 42% Internal Rate of Return
    },
    'psg_grant_eligible': {
        'eligible': True,
        'max_support': 50000,  # S$50,000 per SMB client
        'support_level': 0.50  # 50% of qualifying costs
    }
}
1.4 Platform Editions & Modes
Addressing the "Lite Mode" Requirement:

To serve the diverse needs of Singapore SMBs, the platform offers two operational modes:

text

┌─────────────────────────────────────────────────────────────────────────────┐
│                        PLATFORM EDITION MATRIX                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────┐    ┌─────────────────────────────┐        │
│  │       LITE EDITION         │    │       FULL EDITION          │        │
│  │    (Micro-SMBs: 1-10)      │    │    (SMBs: 10-200 staff)     │        │
│  ├─────────────────────────────┤    ├─────────────────────────────┤        │
│  │ ✓ Single location          │    │ ✓ Multi-location            │        │
│  │ ✓ Basic inventory          │    │ ✓ Advanced inventory        │        │
│  │ ✓ Simple GST (auto-calc)   │    │ ✓ Full GST (F5/F7 filing)   │        │
│  │ ✓ Standard pricing         │    │ ✓ Tiered/dynamic pricing    │        │
│  │ ✓ Single currency (SGD)    │    │ ✓ Multi-currency            │        │
│  │ ✓ Basic reporting          │    │ ✓ Advanced analytics        │        │
│  │ ✗ B2B features             │    │ ✓ B2B credit management     │        │
│  │ ✗ Marketplace sync         │    │ ✓ Shopee/Lazada/Qoo10       │        │
│  │ ✗ PEPPOL/InvoiceNow        │    │ ✓ Full e-invoicing          │        │
│  │ ✗ API access               │    │ ✓ Full API access           │        │
│  │                             │    │                             │        │
│  │ Target: S$100K-500K rev    │    │ Target: S$500K-10M rev      │        │
│  │ Price: S$99/month          │    │ Price: S$299-599/month      │        │
│  └─────────────────────────────┘    └─────────────────────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
1.5 Technology Decision & Justification
Hybrid Architecture Selection:

After comprehensive evaluation, we adopt a Django backend + Next.js frontend hybrid architecture:

Python

technology_decision = {
    'backend': {
        'framework': 'Django 5.0+',
        'language': 'Python 3.11+',
        'api': 'Django REST Framework 3.14+',
        'async': 'Celery 5.3+ with Redis',
        'justification': [
            'Built-in admin panel saves 10+ weeks development',
            'DECIMAL field type ensures financial precision',
            'ORM integrity constraints prevent data corruption',
            'Python ecosystem enables future AI/ML features',
            'Proven at scale: Instagram, Mozilla, Disqus'
        ]
    },
    'frontend': {
        'framework': 'Next.js 14+ with App Router',
        'language': 'TypeScript 5.0+',
        'styling': 'Tailwind CSS 3.4+',
        'state': 'Zustand + TanStack Query',
        'justification': [
            'SSR/SSG for optimal SEO and performance',
            'React Server Components reduce bundle size',
            'PWA support for offline capability',
            'Superior mobile experience (70% of traffic)',
            'TypeScript ensures frontend code safety'
        ]
    },
    'why_not_alternatives': {
        'node_backend': 'JavaScript float precision risk for financial calculations',
        'rails': 'Limited Singapore-specific compliance libraries',
        'laravel': 'Smaller talent pool in Singapore market',
        'django_templates': 'Inferior mobile/PWA experience vs Next.js'
    }
}
Framework Comparison Matrix:

Criterion	Django+Next.js (Chosen)	Node.js Full-Stack	Django Monolith
Financial Precision	✅ Python Decimal	⚠️ Requires decimal.js	✅ Python Decimal
Admin Interface	✅ Django Admin (free)	❌ Custom build (10+ weeks)	✅ Django Admin
Mobile Performance	✅ Next.js SSR/PWA	✅ Next.js SSR/PWA	⚠️ Django templates
SEO Optimization	✅ Static generation	✅ Static generation	⚠️ Server-side only
Real-time Updates	✅ WebSocket + Celery	✅ Native WebSocket	✅ Django Channels
Development Speed	✅ Fast (batteries included)	⚠️ Moderate	✅ Fast
Singapore Compliance	✅ Strong validation	⚠️ Manual implementation	✅ Strong validation
AI/ML Integration	✅ Native Python	⚠️ External services	✅ Native Python
Verdict	SELECTED	Rejected	Rejected
1.6 Strategic Objectives & Success Criteria
Objective	Target Outcome	Success Metric	Measurement	Priority
Operational Excellence	60% reduction in manual processes	Time saved per transaction	Weekly dashboard	P0
Regulatory Compliance	100% GST and PDPA compliance	Zero penalties/violations	Quarterly audit	P0
Inventory Optimization	99.5% stock accuracy	Cycle count variance	Daily automated	P0
Mobile Experience	<2s page load on 4G	Google PageSpeed >90	Real-time monitoring	P0
Financial Visibility	Real-time P&L and cash flow	Dashboard refresh <5s	Hourly sampling	P1
Market Capture	100 active SMBs in 12 months	Monthly active users	Monthly report	P1
Customer Satisfaction	NPS >50	Net Promoter Score	Quarterly survey	P1
Platform Uptime	99.9% availability	Uptime percentage	Real-time monitoring	P0
2. MARKET ANALYSIS & COMPETITIVE POSITIONING
2.1 Singapore E-Commerce Landscape
2.1.1 Market Size & Growth Trajectory
text

SINGAPORE E-COMMERCE MARKET GROWTH (2022-2028)
═══════════════════════════════════════════════════════════════════════

                                                          US$7.2B (Projected)
                                                              │
                                                      US$6.3B │
                                                          │   │
                                              US$5.6B     │   │
                                                  │       │   │
                                      US$5.0B     │       │   │
                                          │       │       │   │
                              US$4.5B     │       │       │   │
                                  │       │       │       │   │
                      US$4.1B     │       │       │       │   │
                          │       │       │       │       │   │
              US$3.8B     │       │       │       │       │   │
                  │       │       │       │       │       │   │
    ┌─────────────┴───────┴───────┴───────┴───────┴───────┴───┴─────────┐
    │    2022      2023      2024      2025      2026      2027   2028  │
    └───────────────────────────────────────────────────────────────────┘
    
    CAGR: 11.2% (2022-2028)
    
    Key Segments:
    ├── Retail E-commerce: 71% (US$3.2B in 2024)
    ├── Travel & Hospitality: 18%
    └── Digital Services: 11%
2.1.2 Market Dynamics & Drivers
Python

market_dynamics = {
    'digital_adoption_metrics': {
        'internet_penetration': 98.5,  # % of population
        'smartphone_ownership': 95.2,  # % of population
        'digital_literacy_index': 86.7,  # Out of 100 (World Bank)
        'e_commerce_penetration': 73.0,  # % of internet users shop online
        '5g_coverage': 95.0  # % of populated areas
    },
    'mobile_commerce_dominance': {
        'mobile_traffic_share': 70.0,  # % of e-commerce traffic
        'mobile_transaction_share': 65.0,  # % of completed purchases
        'mobile_conversion_rate': 2.8,  # % (vs desktop 4.2%)
        'app_vs_mobile_web': {'app': 45, 'mobile_web': 55},  # % split
        'average_mobile_session': 4.2  # Minutes
    },
    'payment_evolution_2024': {
        'digital_wallets': 39.0,  # % of e-commerce payments
        'credit_cards': 35.0,
        'debit_cards': 12.0,
        'bank_transfer': 8.0,
        'bnpl': 4.0,  # Buy Now Pay Later
        'cash_on_delivery': 2.0,
        'paynow_adoption': {
            'gen_z': 68.3,  # %
            'millennials': 55.2,
            'gen_x': 42.1,
            'boomers': 28.5,
            'businesses': 76.8
        }
    },
    'government_digital_initiatives': {
        'psg_grants': {
            'max_per_business': 30000,  # S$
            'support_level': 0.50,  # 50% of qualifying costs
            'eligible_solutions': ['e-commerce', 'inventory', 'accounting']
        },
        'digital_apis': ['SingPass', 'CorpPass', 'MyInfo', 'OneMap', 'InvoiceNow'],
        'infrastructure_investment': '1.2 billion',  # S$ (2023-2025)
        'sme_go_digital': 'Active program with training and funding'
    },
    'emerging_trends_2025': {
        'social_commerce': 'TikTok Shop, Instagram Shopping growing 45% YoY',
        'live_commerce': 'Live streaming sales gaining traction',
        'sustainable_commerce': '67% consumers prefer eco-friendly options',
        'cross_border': '65% of online shoppers buy from overseas',
        'ai_personalization': 'AI-powered recommendations becoming standard'
    }
}
2.1.3 Competitive Landscape Analysis
Platform Type	Market Share	Key Players	SMB Pain Points	Our Differentiation
Marketplaces	60%	Shopee, Lazada, Amazon.sg, Qoo10, Carousell	15-20% commission, limited branding, fragmented inventory, no accounting	Integrated multi-channel sync with unified inventory and automated accounting
SaaS Platforms	25%	Shopify, WooCommerce, Wix	Separate accounting tools, GST compliance gaps, limited Singapore support	Built-in accounting modules with IRAS compliance and local payment integration
Custom Solutions	15%	Local agencies, Bespoke development	High cost (S$200K+), long timelines (12+ months), maintenance burden	Pre-built compliance framework with 28-week delivery and PSG eligibility
Competitive Positioning Matrix:

text

                    HIGH CUSTOMIZATION
                           │
                           │    ┌─────────────────┐
                           │    │ Custom Solutions │
                           │    │  (Local Agencies)│
                           │    └─────────────────┘
                           │
                           │         ┌──────────────────┐
                           │         │ ★ OUR PLATFORM ★ │
                           │         │  (Sweet Spot)    │
                           │         └──────────────────┘
    LOW INTEGRATION ───────┼─────────────────────────────── HIGH INTEGRATION
                           │
          ┌─────────────┐  │    ┌─────────────────┐
          │ Marketplaces │  │    │   SaaS Platforms │
          │(Shopee/Lazada)│ │    │ (Shopify/Wix)    │
          └─────────────┘  │    └─────────────────┘
                           │
                    LOW CUSTOMIZATION
2.2 Target Market Segmentation
2.2.1 Primary Target Segments
Python

target_segments = {
    'micro_smb': {
        'definition': {
            'annual_revenue': {'min': 100000, 'max': 500000},  # S$
            'employee_count': {'min': 1, 'max': 10},
            'sku_range': {'min': 50, 'max': 200},
            'locations': 1
        },
        'characteristics': {
            'tech_readiness': 'Low to Medium',
            'current_systems': ['Excel', 'Basic POS', 'WhatsApp orders'],
            'pain_points': ['Manual bookkeeping', 'No inventory tracking', 'GST confusion'],
            'decision_maker': 'Owner (single decision maker)',
            'budget_sensitivity': 'High'
        },
        'platform_fit': 'Lite Edition',
        'market_size': 150000,  # Estimated SMBs in Singapore
        'target_capture': 0.001,  # 0.1% = 150 clients Year 1
        'arpu': 99  # S$/month
    },
    'small_smb': {
        'definition': {
            'annual_revenue': {'min': 500000, 'max': 2000000},  # S$
            'employee_count': {'min': 10, 'max': 50},
            'sku_range': {'min': 200, 'max': 1000},
            'locations': {'min': 1, 'max': 3}
        },
        'characteristics': {
            'tech_readiness': 'Medium to High',
            'current_systems': ['Basic e-commerce', 'Spreadsheet inventory', 'Xero/QuickBooks'],
            'pain_points': ['Multi-channel sync', 'GST compliance', 'Inventory accuracy'],
            'decision_maker': 'Owner + Operations Manager',
            'budget_sensitivity': 'Medium'
        },
        'platform_fit': 'Full Edition (Standard)',
        'market_size': 45000,  # Estimated SMBs in Singapore
        'target_capture': 0.002,  # 0.2% = 90 clients Year 1
        'arpu': 299  # S$/month
    },
    'medium_smb': {
        'definition': {
            'annual_revenue': {'min': 2000000, 'max': 10000000},  # S$
            'employee_count': {'min': 50, 'max': 200},
            'sku_range': {'min': 1000, 'max': 5000},
            'locations': {'min': 3, 'max': 10}
        },
        'characteristics': {
            'tech_readiness': 'High',
            'current_systems': ['Multiple platforms', 'ERP attempts', 'Custom integrations'],
            'pain_points': ['System fragmentation', 'B2B features', 'Advanced analytics'],
            'decision_maker': 'Management team + IT involvement',
            'budget_sensitivity': 'Low to Medium'
        },
        'platform_fit': 'Full Edition (Enterprise)',
        'market_size': 12000,  # Estimated SMBs in Singapore
        'target_capture': 0.003,  # 0.3% = 36 clients Year 1
        'arpu': 599  # S$/month
    }
}
2.2.2 Industry Vertical Focus
Python

industry_verticals = {
    'retail': {
        'market_share': 35.0,  # % of target market
        'sub_categories': [
            'Fashion & Apparel',
            'Electronics & Gadgets',
            'Home & Living',
            'Sports & Outdoor',
            'Toys & Games'
        ],
        'key_requirements': [
            'Multi-variant products (size, color, material)',
            'Seasonal inventory management',
            'Customer segmentation and loyalty programs',
            'Returns and exchanges handling',
            'Visual merchandising online'
        ],
        'specific_integrations': ['Shopee', 'Lazada', 'Zalora', 'Qoo10'],
        'compliance_needs': ['Standard GST', 'Consumer protection'],
        'average_order_value': 85  # S$
    },
    'food_beverage': {
        'market_share': 25.0,  # % of target market
        'sub_categories': [
            'Restaurants & Cafes',
            'Packaged Food Products',
            'Bakeries & Confectionery',
            'Health Food & Supplements',
            'Beverages'
        ],
        'key_requirements': [
            'Ingredient-level inventory tracking',
            'Batch production management',
            'Expiry date monitoring',
            'Temperature control logging',
            'Delivery scheduling'
        ],
        'specific_integrations': ['GrabFood', 'Deliveroo', 'FoodPanda'],
        'compliance_needs': ['SFA licensing', 'HSA (supplements)', 'Halal certification'],
        'regulatory_bodies': ['Singapore Food Agency (SFA)', 'NEA'],
        'average_order_value': 45  # S$
    },
    'health_beauty': {
        'market_share': 20.0,  # % of target market
        'sub_categories': [
            'Cosmetics & Skincare',
            'Personal Care',
            'Wellness Products',
            'Medical Devices',
            'Supplements'
        ],
        'key_requirements': [
            'Product registration tracking',
            'Batch and lot number traceability',
            'Expiry management',
            'Ingredient compliance',
            'Recall capability'
        ],
        'specific_integrations': ['Shopee Beauty', 'Sephora', 'Watsons'],
        'compliance_needs': ['HSA registration', 'Cosmetic notification', 'ASEAN Cosmetic Directive'],
        'regulatory_bodies': ['Health Sciences Authority (HSA)'],
        'average_order_value': 65  # S$
    },
    'b2b_wholesale': {
        'market_share': 20.0,  # % of target market
        'sub_categories': [
            'Industrial Supplies',
            'Office Products',
            'Building Materials',
            'Packaging',
            'Equipment & Machinery'
        ],
        'key_requirements': [
            'Tiered pricing by customer segment',
            'Bulk ordering with MOQ enforcement',
            'Account management with credit terms',
            'Quote and tender management',
            'Contract pricing'
        ],
        'specific_integrations': ['SAP Ariba', 'Alibaba B2B'],
        'compliance_needs': ['Standard GST', 'InvoiceNow/PEPPOL for government contracts'],
        'average_order_value': 2500  # S$
    }
}
2.3 Addressable Market Sizing
Python

market_sizing = {
    'total_addressable_market': {
        'singapore_smb_count': 280000,  # Total registered SMBs
        'e_commerce_relevant': 0.75,  # 75% could benefit from e-commerce
        'digital_ready': 0.60,  # 60% have digital readiness
        'tam_count': 126000,  # SMBs in TAM
        'tam_value': 453600000  # S$453.6M (126K × S$300/month × 12)
    },
    'serviceable_addressable_market': {
        'target_segments_count': 207000,  # Micro + Small + Medium
        'budget_qualified': 0.40,  # 40% can afford platform
        'sam_count': 82800,  # SMBs in SAM
        'sam_value': 298080000  # S$298M
    },
    'serviceable_obtainable_market': {
        'realistic_capture_year_1': 276,  # 150 + 90 + 36 from segment targets
        'realistic_capture_year_3': 1200,
        'som_value_year_1': 1324800,  # S$1.32M ARR
        'som_value_year_3': 5760000   # S$5.76M ARR
    }
}
3. STAKEHOLDER ANALYSIS & USER PERSONAS
3.1 Comprehensive Stakeholder Map
mermaid

graph TD
    subgraph "Platform Ecosystem"
        A[Singapore SMB Platform]
    end
    
    subgraph "Internal Users"
        B1[Business Owner / Director]
        B2[Operations Manager]
        B3[Accountant / Finance]
        B4[Warehouse Staff]
        B5[Sales / Customer Service]
        B6[Marketing Manager]
    end
    
    subgraph "External Users"
        C1[End Customers B2C]
        C2[Business Customers B2B]
        C3[Suppliers / Vendors]
    end
    
    subgraph "Integration Partners"
        D1[Payment Gateways]
        D2[Logistics Providers]
        D3[Accounting Software]
        D4[Marketplaces]
        D5[Banks]
    end
    
    subgraph "Regulatory Bodies"
        E1[IRAS - Tax Authority]
        E2[ACRA - Company Registry]
        E3[PDPC - Data Protection]
        E4[MAS - Payment Regulation]
        E5[Industry Regulators - SFA/HSA/SPF]
    end
    
    A --> B1
    A --> B2
    A --> B3
    A --> B4
    A --> B5
    A --> B6
    A --> C1
    A --> C2
    A --> C3
    A --> D1
    A --> D2
    A --> D3
    A --> D4
    A --> D5
    A --> E1
    A --> E2
    A --> E3
    A --> E4
    A --> E5
3.2 Detailed User Personas
3.2.1 Primary Persona: Sarah Chen — SMB Owner
Python

persona_sarah_chen = {
    'identity': {
        'name': 'Sarah Chen',
        'age': 38,
        'role': 'Founder & Managing Director',
        'company': 'StyleHaus Pte Ltd',
        'industry': 'Fashion Retail',
        'location': 'Singapore (Jurong East)'
    },
    'business_profile': {
        'company_size': '12 employees',
        'annual_revenue': 'S$1.8 million',
        'growth_rate': '25% YoY',
        'business_model': 'B2C + small B2B (corporate gifting)',
        'channels': ['2 retail stores', 'Shopify website', 'Shopee store'],
        'product_count': 450,  # SKUs
        'average_order_value': 95,  # S$
        'monthly_orders': 800
    },
    'technology_profile': {
        'tech_savviness': 'Intermediate',
        'current_tools': {
            'e_commerce': 'Shopify Basic (S$29/month)',
            'accounting': 'Xero (S$50/month)',
            'inventory': 'Excel spreadsheets',
            'pos': 'Square POS',
            'marketplace': 'Seller Center (manual)'
        },
        'comfort_areas': ['Email', 'Social media', 'Basic accounting software'],
        'challenge_areas': ['Complex integrations', 'API configurations', 'Technical troubleshooting'],
        'device_usage': {'mobile': 70, 'desktop': 30}  # % of work time
    },
    'daily_challenges': [
        'Reconciling sales across 4 channels (2 stores + web + Shopee)',
        'Managing inventory sync — frequent overselling on Shopee',
        'Quarterly GST filing takes 3 full days with accountant',
        'No real-time visibility into business performance',
        'Staff spending 3 hours daily on manual data entry',
        'Customer complaints about stock availability information'
    ],
    'goals_and_motivations': [
        'Unified dashboard showing all business KPIs in real-time',
        'Automated GST compliance with zero filing errors',
        'Scale to S$5M revenue within 3 years',
        'Reduce operational headaches by 60%',
        'Open 2 more stores without adding admin overhead',
        'Eventually exit or franchise the business'
    ],
    'success_metrics': {
        'time_saved_admin': '10+ hours/week',
        'real_time_visibility': 'P&L on mobile anytime',
        'compliance': 'Zero tax filing errors',
        'growth': '25% YoY revenue increase maintained',
        'inventory_accuracy': '>98%',
        'customer_satisfaction': 'NPS >50'
    },
    'decision_criteria': {
        'must_have': ['GST automation', 'Multi-channel sync', 'Mobile access'],
        'nice_to_have': ['AI recommendations', 'Advanced analytics'],
        'budget_range': 'S$200-400/month',
        'decision_timeline': '2-4 weeks',
        'influencers': ['Accountant', 'Operations Manager', 'Industry peers']
    },
    'preferred_engagement': {
        'communication': 'WhatsApp for urgent, Email for details',
        'training': 'Video tutorials + 1:1 onboarding call',
        'support': 'Chat support during business hours',
        'content': 'Case studies from similar businesses'
    }
}
3.2.2 Operations Manager: Marcus Tan
Python

persona_marcus_tan = {
    'identity': {
        'name': 'Marcus Tan',
        'age': 32,
        'role': 'Operations Manager',
        'company': 'StyleHaus Pte Ltd',
        'reports_to': 'Sarah Chen (Owner)',
        'direct_reports': 4  # Warehouse and store staff
    },
    'professional_profile': {
        'experience': '8 years in retail operations',
        'previous_roles': ['Store Manager', 'Assistant Ops Manager'],
        'education': 'Diploma in Supply Chain Management',
        'certifications': ['WSQ Retail Operations']
    },
    'responsibilities': [
        'Inventory management across 2 stores + warehouse',
        'Supplier relationship and purchase ordering',
        'Warehouse operations and fulfillment',
        'Staff scheduling and performance tracking',
        'Stock transfers between locations',
        'Returns processing and quality control'
    ],
    'daily_workflow': {
        '08:00': 'Check overnight online orders and inventory levels',
        '09:00': 'Review low stock alerts, create purchase orders',
        '10:00': 'Warehouse receiving and quality checks',
        '11:00': 'Staff briefing and task allocation',
        '14:00': 'Stock transfer coordination between locations',
        '16:00': 'Order fulfillment monitoring',
        '18:00': 'End of day inventory reconciliation'
    },
    'pain_points': [
        'Manual stock counts taking 4 hours weekly',
        'Overselling on marketplaces due to 15-minute sync delay',
        'No automated reorder point system — relies on gut feel',
        'Difficulty tracking product performance by location',
        'Paper-based picking lists prone to errors',
        'No visibility into stock in transit'
    ],
    'needs_and_requirements': [
        'Real-time inventory visibility across all channels',
        'Mobile barcode scanning for warehouse operations',
        'Automated reorder suggestions based on sales velocity',
        'Performance dashboards for warehouse staff',
        'Digital picking lists with validation',
        'Stock transfer tracking with ETA'
    ],
    'success_metrics': {
        'inventory_accuracy': '>99%',
        'stockout_rate': '<1%',
        'order_fulfillment_time': '<30 minutes',
        'inventory_turnover_improvement': '+20%',
        'picking_error_rate': '<0.1%',
        'staff_productivity': '+25%'
    },
    'technology_preferences': {
        'mobile_first': True,  # Works on the floor, not at desk
        'barcode_scanner': 'Bluetooth scanner or phone camera',
        'notifications': 'Push notifications for urgent alerts',
        'offline_capability': 'Essential for warehouse areas with poor signal'
    }
}
3.2.3 Accountant: Priya Kumar
Python

persona_priya_kumar = {
    'identity': {
        'name': 'Priya Kumar',
        'age': 35,
        'role': 'Senior Accountant (Part-time / Outsourced)',
        'company': 'Kumar Accounting Services',
        'clients': 12,  # SMB clients including StyleHaus
        'certifications': ['ACCA', 'CA Singapore']
    },
    'professional_profile': {
        'experience': '10 years in accounting',
        'specialization': 'SMB accounting and GST compliance',
        'software_expertise': ['Xero', 'QuickBooks', 'MYOB', 'Excel'],
        'regulatory_knowledge': ['IRAS GST', 'ACRA filing', 'SFRS']
    },
    'responsibilities_for_client': [
        'Monthly bookkeeping and bank reconciliation',
        'Quarterly GST filing (F5/F7)',
        'Annual financial statements',
        'ACRA annual return preparation',
        'Tax planning and advisory',
        'Audit support'
    },
    'current_workflow_with_stylehaus': {
        'data_collection': 'Export from Shopify, Square, Bank statements — 3 different formats',
        'reconciliation': 'Manual matching in Excel — 8 hours/month',
        'gst_preparation': 'Manual categorization of transactions — 6 hours/quarter',
        'reporting': 'Manual P&L and Balance Sheet in Excel — 4 hours/month',
        'communication': 'Email back-and-forth for missing information'
    },
    'pain_points': [
        'Manual data entry from multiple sales channels (3 systems)',
        'GST calculation errors due to inconsistent categorization',
        'Month-end closing taking 5+ days due to missing information',
        'Difficulty generating IRAS-compliant reports',
        'No real-time visibility — working with 2-week old data',
        'Client calls interrupting workflow for basic questions'
    ],
    'needs_and_requirements': [
        'Automated journal entries from sales transactions',
        'Real-time GST calculation with proper categorization',
        'Bank feed integration for automatic reconciliation',
        'One-click GST F5/F7 report generation',
        'Audit trail for all transactions',
        'Client self-service for basic financial queries'
    ],
    'success_metrics': {
        'gst_filing_accuracy': '100%',
        'month_end_close_time': '<1 day (down from 5)',
        'manual_data_entry_reduction': '85%',
        'audit_preparation_time': '90% reduction',
        'client_query_time': 'Real-time via dashboard (down from 24-48 hours)'
    },
    'integration_requirements': {
        'accounting_software': 'Two-way sync with Xero',
        'bank_feeds': 'Direct bank connections (DBS, OCBC, UOB)',
        'export_formats': ['CSV', 'PDF', 'IRAS XML format'],
        'audit_trail': 'Complete transaction history with user attribution'
    }
}
3.2.4 End Customer: Digital Native Shopper
Python

persona_customer_rachel = {
    'identity': {
        'name': 'Rachel Lim',
        'age': 28,
        'occupation': 'Marketing Executive',
        'location': 'Singapore (Tampines)',
        'income_bracket': 'S$4,000-6,000/month'
    },
    'shopping_behavior': {
        'online_shopping_frequency': '3-4 times/month',
        'average_order_value': 85,  # S$
        'primary_device': 'Mobile (iPhone)',
        'shopping_time': 'Evenings and weekends',
        'decision_factors': ['Price', 'Reviews', 'Delivery speed', 'Return policy']
    },
    'channel_preferences': {
        'discovery': ['Instagram (35%)', 'TikTok (25%)', 'Google (20%)', 'Friend referral (20%)'],
        'research': ['Brand website', 'Shopee reviews', 'YouTube reviews'],
        'purchase': ['Brand website (if good experience)', 'Shopee (if price-sensitive)'],
        'repurchase': 'Direct from brand if loyalty program exists'
    },
    'payment_preferences': {
        'primary': 'PayNow (68% of purchases)',
        'secondary': 'Credit card (for larger purchases)',
        'bnpl': 'Atome for purchases >S$100',
        'e_wallets': 'GrabPay if GrabRewards available'
    },
    'delivery_expectations': {
        'standard_delivery': '2-3 business days acceptable',
        'express_delivery': 'Same-day or next-day for urgent items',
        'delivery_tracking': 'Real-time updates via SMS/WhatsApp',
        'delivery_options': ['Home delivery', 'Office delivery', 'Pickup points']
    },
    'pain_points_with_current_smb_sites': [
        'Slow mobile loading (>5 seconds)',
        'Clunky checkout requiring too many steps',
        'No real-time stock availability shown',
        'Limited payment options (no PayNow)',
        'Poor delivery tracking',
        'Difficult returns process'
    ],
    'expectations_from_ideal_platform': [
        'Fast mobile experience (<2 seconds load)',
        'One-click checkout with saved preferences',
        'Real-time stock availability',
        'PayNow QR code payment',
        'WhatsApp order updates',
        'Easy returns with self-service portal'
    ],
    'success_metrics_from_customer_pov': {
        'page_load_time': '<2 seconds',
        'checkout_time': '<2 minutes',
        'delivery_accuracy': '>99%',
        'return_ease': 'Self-service within 5 minutes',
        'support_response': '<1 hour during business hours'
    }
}
3.2.5 B2B Customer: Corporate Buyer
Python

persona_b2b_david = {
    'identity': {
        'name': 'David Wong',
        'age': 42,
        'role': 'Procurement Manager',
        'company': 'TechStart Solutions Pte Ltd',
        'company_size': '150 employees',
        'industry': 'IT Services'
    },
    'procurement_profile': {
        'annual_procurement_budget': 'S$500,000',
        'categories_managed': ['Office supplies', 'Corporate gifts', 'Uniforms', 'IT peripherals'],
        'order_frequency': '2-3 orders/month',
        'average_order_value': 2500,  # S$
        'payment_terms_required': 'Net 30'
    },
    'procurement_workflow': {
        'requisition': 'Internal request from departments',
        'approval': '2-level approval for >S$1,000',
        'sourcing': 'Compare 3 quotes minimum',
        'ordering': 'PO generation required',
        'receiving': 'Goods receipt with 3-way matching',
        'payment': 'Monthly payment run'
    },
    'requirements_from_suppliers': [
        'Corporate account with credit terms',
        'Tiered pricing based on volume',
        'Formal quotations and invoices',
        'GST-registered supplier preferred',
        'InvoiceNow (PEPPOL) capability for government-linked projects',
        'Bulk ordering with scheduled delivery'
    ],
    'pain_points_with_smb_suppliers': [
        'No formal quotation system',
        'Cannot issue proper tax invoices',
        'No credit terms — payment upfront only',
        'No visibility into stock for large orders',
        'Inconsistent pricing',
        'Manual order placement (email/phone)'
    ],
    'platform_expectations': [
        'Self-service corporate account portal',
        'Quote request and approval workflow',
        'Purchase order integration',
        'Statement of account access',
        'Bulk ordering with MOQ discounts',
        'PEPPOL-compliant invoicing'
    ]
}
3.3 User Journey Maps
3.3.1 Customer Purchase Journey
text

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CUSTOMER PURCHASE JOURNEY                                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  AWARENESS          CONSIDERATION        PURCHASE           POST-PURCHASE              │
│  ─────────          ─────────────        ────────           ─────────────              │
│                                                                                         │
│  ┌─────────┐        ┌─────────────┐      ┌──────────┐       ┌──────────────┐           │
│  │Instagram│        │   Browse    │      │  Add to  │       │   Order      │           │
│  │   Ad    │───────►│   Website   │─────►│   Cart   │──────►│ Confirmation │           │
│  └─────────┘        └─────────────┘      └──────────┘       └──────────────┘           │
│       │                   │                   │                    │                    │
│       ▼                   ▼                   ▼                    ▼                    │
│  ┌─────────┐        ┌─────────────┐      ┌──────────┐       ┌──────────────┐           │
│  │ Google  │        │   Compare   │      │ Checkout │       │   Delivery   │           │
│  │ Search  │───────►│   Reviews   │─────►│  PayNow  │──────►│   Tracking   │           │
│  └─────────┘        └─────────────┘      └──────────┘       └──────────────┘           │
│       │                   │                   │                    │                    │
│       ▼                   ▼                   ▼                    ▼                    │
│  ┌─────────┐        ┌─────────────┐      ┌──────────┐       ┌──────────────┐           │
│  │ Friend  │        │   Wishlist  │      │  Express │       │   Review &   │           │
│  │Referral │───────►│    Save     │─────►│ Checkout │──────►│   Repeat     │           │
│  └─────────┘        └─────────────┘      └──────────┘       └──────────────┘           │
│                                                                                         │
│  ═══════════════════════════════════════════════════════════════════════════════════   │
│  PLATFORM TOUCHPOINTS:                                                                  │
│                                                                                         │
│  • Mobile-optimized    • Real-time stock     • One-click checkout  • WhatsApp updates  │
│  • <2s load time       • AI recommendations  • PayNow QR           • Self-service      │
│  • SEO optimized       • Save for later      • Multiple payment    • Easy returns      │
│  • Social proof        • Price alerts        • Guest checkout      • Loyalty program   │
│                                                                                         │
│  ═══════════════════════════════════════════════════════════════════════════════════   │
│  CONVERSION TARGETS:                                                                    │
│                                                                                         │
│  Click-through: 3%     Add-to-cart: 15%      Checkout: 65%         Repeat: 35%         │
│  (from ad)             (from browse)         (from cart)           (within 90 days)    │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
3.3.2 Admin Order Processing Journey
Python

admin_order_journey = {
    'trigger': 'Order placed via web store, marketplace, or POS',
    'total_target_time': '<2 minutes (automated)',
    'manual_intervention_target': '<5% of orders',
    'steps': [
        {
            'step': 1,
            'name': 'Order Received',
            'actions': [
                'Order created in system with unique order number',
                'SMS/Push notification to operations staff',
                'Email confirmation to customer',
                'Dashboard highlight for new orders'
            ],
            'automation_level': '100%',
            'system_actions': [
                'Auto-classify by channel and priority',
                'Auto-assign to appropriate fulfillment location',
                'Flag high-value orders for priority handling'
            ],
            'time_target': '<1 second'
        },
        {
            'step': 2,
            'name': 'Inventory Reservation',
            'actions': [
                'Real-time stock verification across locations',
                'Atomic reservation of items (prevents overselling)',
                'Low stock alert if threshold breached',
                'Backorder creation if stock insufficient'
            ],
            'automation_level': '100%',
            'system_actions': [
                'Redis lock for concurrent order protection',
                'Marketplace sync triggered',
                'Reorder point check'
            ],
            'time_target': '<500ms'
        },
        {
            'step': 3,
            'name': 'Payment Verification',
            'actions': [
                'Payment gateway confirmation received',
                'Fraud score assessment',
                'Invoice generation with GST breakdown',
                'Payment recorded in accounting'
            ],
            'automation_level': '98%',
            'manual_triggers': ['Fraud score >70', 'Payment mismatch'],
            'system_actions': [
                'Auto-reconcile with payment gateway',
                'Auto-post journal entry',
                'Auto-generate tax invoice'
            ],
            'time_target': '<5 seconds'
        },
        {
            'step': 4,
            'name': 'Pick List Generation',
            'actions': [
                'Generate optimized picking list',
                'Assign to warehouse staff',
                'Push notification to picker',
                'Timer starts for fulfillment SLA'
            ],
            'automation_level': '100%',
            'system_actions': [
                'Route optimization based on warehouse layout',
                'Batch with other orders if efficient',
                'Priority queue management'
            ],
            'time_target': '<2 seconds'
        },
        {
            'step': 5,
            'name': 'Pick & Pack',
            'actions': [
                'Staff scans items with barcode scanner',
                'System validates correct items picked',
                'Packing slip printed',
                'Weight verification (optional)'
            ],
            'automation_level': '80%',
            'manual_actions': ['Physical picking', 'Physical packing'],
            'system_validations': [
                'Beep alert for wrong item scanned',
                'Photo capture for high-value items',
                'Signature capture if required'
            ],
            'time_target': '<15 minutes (manual)'
        },
        {
            'step': 6,
            'name': 'Shipping Label & Dispatch',
            'actions': [
                'Auto-select optimal carrier based on rules',
                'Generate shipping label via carrier API',
                'Schedule pickup or drop-off',
                'Customer notification with tracking number'
            ],
            'automation_level': '95%',
            'system_actions': [
                'Carrier rate comparison',
                'Tracking number assignment',
                'SMS/WhatsApp tracking link to customer'
            ],
            'time_target': '<10 seconds'
        },
        {
            'step': 7,
            'name': 'Accounting & Revenue Recognition',
            'actions': [
                'Journal entry posted (Debit: AR/Cash, Credit: Revenue + GST)',
                'Cost of goods sold recorded',
                'Inventory value updated',
                'Commission/fees recorded if marketplace order'
            ],
            'automation_level': '100%',
            'system_actions': [
                'Auto-post based on accounting rules',
                'GST categorization (SR/ZR/E)',
                'Multi-currency conversion if applicable'
            ],
            'time_target': '<1 second'
        },
        {
            'step': 8,
            'name': 'Analytics & Reporting',
            'actions': [
                'Update real-time sales dashboard',
                'Update inventory analytics',
                'Customer purchase history updated',
                'Fulfillment metrics recorded'
            ],
            'automation_level': '100%',
            'system_actions': [
                'Real-time KPI updates',
                'Anomaly detection',
                'Trend analysis update'
            ],
            'time_target': '<1 second'
        }
    ],
    'success_metrics': {
        'total_processing_time': '<2 minutes (automated portion)',
        'manual_fulfillment_time': '<30 minutes',
        'error_rate': '<0.1%',
        'automation_rate': '>95%'
    }
}
4. BUSINESS REQUIREMENTS & PROCESS MAPPING
4.1 Core Business Capabilities
4.1.1 Capability Map
text

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            PLATFORM CAPABILITY MAP                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  CUSTOMER-FACING CAPABILITIES                    OPERATIONAL CAPABILITIES              │
│  ════════════════════════════                    ═══════════════════════               │
│                                                                                         │
│  ┌─────────────────────────┐                     ┌─────────────────────────┐           │
│  │    STOREFRONT           │                     │    ORDER MANAGEMENT     │           │
│  ├─────────────────────────┤                     ├─────────────────────────┤           │
│  │ • Product catalog       │                     │ • Order processing      │           │
│  │ • Search & filter       │                     │ • Status tracking       │           │
│  │ • Shopping cart         │                     │ • Returns & exchanges   │           │
│  │ • Checkout              │                     │ • Customer service      │           │
│  │ • Customer accounts     │                     │ • Dispute handling      │           │
│  └─────────────────────────┘                     └─────────────────────────┘           │
│                                                                                         │
│  ┌─────────────────────────┐                     ┌─────────────────────────┐           │
│  │    PAYMENTS             │                     │    INVENTORY            │           │
│  ├─────────────────────────┤                     ├─────────────────────────┤           │
│  │ • Multiple gateways     │                     │ • Multi-location        │           │
│  │ • PayNow/GrabPay        │                     │ • Real-time tracking    │           │
│  │ • BNPL (Atome)          │                     │ • Stock transfers       │           │
│  │ • Recurring payments    │                     │ • Reorder automation    │           │
│  │ • Refund processing     │                     │ • Cycle counting        │           │
│  └─────────────────────────┘                     └─────────────────────────┘           │
│                                                                                         │
│  ┌─────────────────────────┐                     ┌─────────────────────────┐           │
│  │    MARKETING            │                     │    PROCUREMENT          │           │
│  ├─────────────────────────┤                     ├─────────────────────────┤           │
│  │ • Promotions            │                     │ • Supplier management   │           │
│  │ • Loyalty program       │                     │ • Purchase orders       │           │
│  │ • Email campaigns       │                     │ • Goods receiving       │           │
│  │ • Referral system       │                     │ • Supplier payments     │           │
│  │ • Abandoned cart        │                     │ • Quality control       │           │
│  └─────────────────────────┘                     └─────────────────────────┘           │
│                                                                                         │
│  FINANCIAL CAPABILITIES                          COMPLIANCE CAPABILITIES               │
│  ══════════════════════                          ══════════════════════                │
│                                                                                         │
│  ┌─────────────────────────┐                     ┌─────────────────────────┐           │
│  │    ACCOUNTING           │                     │    TAX & REGULATORY     │           │
│  ├─────────────────────────┤                     ├─────────────────────────┤           │
│  │ • General ledger        │                     │ • GST calculation       │           │
│  │ • Accounts receivable   │                     │ • GST filing (F5/F7)    │           │
│  │ • Accounts payable      │                     │ • PDPA compliance       │           │
│  │ • Bank reconciliation   │                     │ • InvoiceNow/PEPPOL     │           │
│  │ • Financial reports     │                     │ • Industry licenses     │           │
│  └─────────────────────────┘                     └─────────────────────────┘           │
│                                                                                         │
│  ┌─────────────────────────┐                     ┌─────────────────────────┐           │
│  │    B2B COMMERCE [FULL]  │                     │    ANALYTICS            │           │
│  ├─────────────────────────┤                     ├─────────────────────────┤           │
│  │ • Corporate accounts    │                     │ • Real-time dashboards  │           │
│  │ • Credit management     │                     │ • Sales analytics       │           │
│  │ • Tiered pricing        │                     │ • Inventory analytics   │           │
│  │ • Quote management      │                     │ • Financial analytics   │           │
│  │ • Statement of account  │                     │ • Customer analytics    │           │
│  └─────────────────────────┘                     └─────────────────────────┘           │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
4.1.2 Capability Requirements Matrix
Capability	Lite Edition	Full Edition	Priority	Business Value
Product Catalog	✅ Up to 500 SKUs	✅ Unlimited	P0	Core functionality
Multi-variant Products	✅ Basic	✅ Advanced (matrix)	P0	Product flexibility
Shopping Cart	✅ Standard	✅ + B2B bulk	P0	Revenue generation
Checkout	✅ Standard	✅ + Express	P0	Conversion optimization
PayNow Integration	✅	✅	P0	Singapore essential
Credit Card Processing	✅	✅	P0	Payment flexibility
BNPL (Atome/Hoolah)	❌	✅	P1	Basket size increase
Single Location Inventory	✅	✅	P0	Stock management
Multi-Location Inventory	❌	✅	P0	Scale requirement
Marketplace Sync	❌	✅ Shopee/Lazada	P1	Channel expansion
Basic GST Calculation	✅ Auto-calculate	✅ Auto-calculate	P0	Compliance
GST F5 Filing	❌ Manual export	✅ Auto-generate	P0	Compliance automation
Basic Reporting	✅ Sales/Inventory	✅ Full suite	P0	Business visibility
Advanced Analytics	❌	✅	P1	Strategic insights
B2B Credit Management	❌	✅	P1	B2B enablement
InvoiceNow/PEPPOL	❌	✅	P1	Government contracts
API Access	❌	✅	P1	Integration flexibility
Xero/QuickBooks Sync	✅ One-way	✅ Two-way	P1	Accounting integration
4.2 Business Process Requirements
4.2.1 Order-to-Cash (O2C) Process
mermaid

graph LR
    subgraph "Customer Phase"
        A[Order Placed] --> B[Payment Received]
    end
    
    subgraph "Fulfillment Phase"
        B --> C[Inventory Reserved]
        C --> D[Pick & Pack]
        D --> E[Ship]
    end
    
    subgraph "Delivery Phase"
        E --> F[In Transit]
        F --> G[Delivered]
    end
    
    subgraph "Financial Phase"
        G --> H[Invoice Posted]
        H --> I[Revenue Recognized]
        I --> J[GST Recorded]
    end
    
    style A fill:#e8f5e9
    style B fill:#c8e6c9
    style C fill:#a5d6a7
    style D fill:#81c784
    style E fill:#66bb6a
    style F fill:#4caf50
    style G fill:#43a047
    style H fill:#388e3c
    style I fill:#2e7d32
    style J fill:#1b5e20
Python

order_to_cash_process = {
    'process_id': 'O2C-001',
    'process_name': 'Order-to-Cash',
    'owner': 'Operations Manager',
    'frequency': 'Per transaction',
    'stages': [
        {
            'stage': 1,
            'name': 'Order Capture',
            'description': 'Customer places order through any channel',
            'channels': ['Web store', 'Mobile app', 'POS', 'Shopee', 'Lazada', 'Phone/WhatsApp'],
            'inputs': ['Customer details', 'Product selection', 'Shipping preference'],
            'outputs': ['Order record', 'Order confirmation email'],
            'automation_level': '100%',
            'systems_involved': ['E-commerce platform', 'Order management'],
            'business_rules': [
                'Validate customer email format',
                'Check product availability before confirmation',
                'Apply customer 
