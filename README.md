# SmartCOD AI — Intelligent COD Risk & RTO Prevention System

[![Tests](https://img.shields.io/badge/pytest-13%20passed%20(100%25)-10b981.svg)](backend/tests/)
[![Vite Build](https://img.shields.io/badge/vite%20build-passing-10b981.svg)](frontend/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61dafb.svg)](https://react.dev)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](#)

> **Autonomous AI Software Engineering Take-Home Assignment Implementation**  
> An intelligent, locally runnable COD decision engine and RTO prevention system for high-growth D2C ecommerce brands on Shopify.

---

## 1. Executive Summary & Problem Context

In Indian D2C ecommerce, **Cash on Delivery (COD)** accounts for over 50–60% of all orders, but suffers from a crippling **25–35% Return-to-Origin (RTO)** rate.

For a fast-growing D2C haircare brand processing **3,000 monthly orders (55% COD, 28.4% COD RTO rate)**, reverse logistics destroys bottom-line profitability:
- **Verified Direct Cash Loss per RTO:** **₹169.40**  
  $$\text{₹}65 \text{ (forward shipping)} + \text{₹}65 \text{ (return shipping)} + \text{₹}25 \text{ (packaging)} + (0.08 \times \text{₹}180 \text{ damage}) = \text{₹}169.40$$
- **The Cancellation Trap (False Positive Cost):**  
  Cancelling a genuine order sacrifices **₹402.38** in gross profit (62% gross margin on ₹649 AOV) plus **₹300+** in sunk Meta Ad acquisition cost (CAC), totaling **₹702.38 lost per false cancellation**.
- **The Economic Breakeven Ratio:**  
  $$\frac{\text{₹}702.38 \text{ (Lost profit + CAC)}}{\text{₹}169.40 \text{ (Saved RTO cash)}} = 4.14$$
  **It takes over 4 correct RTO catches to pay for a single genuine customer incorrectly cancelled!**

**SmartCOD AI** resolves this tension by replacing blunt order cancellations with a 4-tier autonomous economic triage:
1. **`SHIP_AS_IS`**: Immediate automated fulfillment for trusted repeat buyers ($14\%$ baseline RTO).
2. **`SHIP_AFTER_CONFIRMATION`**: Two-way interactive WhatsApp verification for first-time or moderately ambiguous orders.
3. **`NUDGE_TO_PREPAID`**: WhatsApp 8% instant discount incentive (converting COD to UPI/Cards drops RTO from 28% to 4%, saving ₹15 net cash per order).
4. **`HOLD_OR_CANCEL`**: Strict surgical intervention reserved for confirmed test orders, broken addresses, and chronic return abusers.

---

## 2. Core Features & Capabilities

- **4-Tier Autonomous Decision Engine (`backend/services/risk_engine.py`):**
  Calibrated multi-factor risk assessment combining Empirical Bayes smoothed pincode priors across 461 pincodes, historical customer return rates, address completeness, and acquisition channel risk.
- **Explainable Plain-English Decisions:**
  Every decision returns plain-English reasoning, directional risk factors (positive trust vs negative risk), expected financial contribution, and recommended operational next steps.
- **Interactive WhatsApp Simulator (`frontend/src/pages/WhatsAppSimulator.jsx`):**
  Full smartphone mockup simulating:
  - **Workflow A (Confirmation):** YES (Confirms dispatch) / NO (Cancels dispatch) / Unclear responses.
  - **Workflow B (Prepaid Nudge):** Instant UPI discount link, simulated one-click checkout, and live status upgrade to `PREPAID`.
  - **SLA Time Stepper:** Test +1h, +6h, and +24h response timeouts.
- **Executive Founder Dashboard (`frontend/src/pages/FounderDashboard.jsx`):**
  Real-time KPI monitor with dynamic period selector ("All 1,988 Orders", "Yesterday", "Last 7 Days", "Last 30 Days"), 4 decision bucket triage, and live **Net Economic Benefit (₹)** tracking.
- **Editable Operational Thresholds (`frontend/src/pages/SettingsPanel.jsx`):**
  Operations team can adjust risk cutoffs, discount percentages, timeout windows, and financial constants via sliders and inputs with live SQLite persistence.
- **Empirical Findings Explorer (`frontend/src/pages/RiskFindings.jsx`):**
  Visual analysis of the 1,988 historical dataset, highlighting the 3.22x prior RTO risk multiplier and 61.75% defective address failure rate.

---

## 3. Quickstart Guide (Run Locally in < 5 Minutes)

### Prerequisites
- **Python:** 3.10 or higher
- **Node.js:** v18 or higher (with npm)

### Step 1: Clone and Navigate to Project
```bash
git clone <repository_url>
cd COD-RTO-AI-Automation
```

### Step 2: Backend Setup & Launch
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Start the FastAPI server (auto-seeds SQLite database from cleaned_orders.csv on startup)
uvicorn backend.main:app --reload --port 8000
```
*The backend API is now live at `http://127.0.0.1:8000` (Interactive Swagger Docs at `http://127.0.0.1:8000/docs`).*

### Step 3: Frontend Setup & Launch
Open a second terminal window:
```bash
# Navigate to frontend
cd frontend

# Install dependencies (only needed once)
npm install

# Start Vite development server
npm run dev
```
*Open your browser and navigate to `http://localhost:5173`.*

---

## 4. Automated Testing & Verification

The project includes an end-to-end automated test suite covering all 4 decision actions, financial formulas, WhatsApp state transitions, threshold validation, and frontend production bundling:

```bash
# Execute Backend Pytest Suite (13 passing tests)
python -m pytest -v

# Validate Frontend Production Bundle (Vite)
cd frontend
npm run build
```

---

## 5. Project Directory Structure

```text
COD-RTO-AI-Automation/
├── analysis/
│   ├── analyze_orders.py          # Data analysis script
│   ├── generate_memo_pdf.py       # PDF generator script
│   └── findings.json              # Statistical findings from 1,988 orders
├── backend/
│   ├── config.py                  # Pydantic settings & financial constants
│   ├── database.py                # SQLAlchemy engine & session factory
│   ├── main.py                    # FastAPI application & DB seeder
│   ├── models.py                  # SQLAlchemy ORM models (Order, Decision, Settings, etc.)
│   ├── requirements.txt           # Python dependencies
│   ├── schemas.py                 # Pydantic request/response schemas
│   ├── routes/
│   │   ├── analysis.py            # Analysis findings endpoint
│   │   ├── dashboard.py           # Founder KPI & financial summary endpoints
│   │   ├── orders.py              # Order evaluation & registry endpoints
│   │   ├── settings.py            # Editable threshold endpoints
│   │   └── whatsapp.py            # WhatsApp state machine endpoints
│   ├── services/
│   │   ├── financial_model.py     # Unit economics & discount optimizer
│   │   ├── llm_service.py         # NLP address parser & deterministic fallback
│   │   ├── risk_engine.py         # Multi-factor COD risk scoring engine
│   │   └── whatsapp_service.py    # Conversational state machine
│   └── tests/
│       ├── conftest.py            # Pytest test fixtures
│       ├── test_api_and_whatsapp.py # API & WhatsApp flow tests
│       └── test_risk_engine.py    # Risk engine & financial formula tests
├── data/
│   ├── cleaned_orders.csv         # 1,988 deduplicated orders with features
│   └── orders_sample.csv          # Raw 2,018 baseline records
├── docs/
│   ├── AI_USAGE_LOG.md            # Transparent record of AI assistance & caught bugs
│   ├── ARCHITECTURE.md            # System architecture, Mermaid diagrams & schemas
│   ├── BUSINESS_MEMO.pdf          # 2-Page Publication-ready Executive Memo for Founder
│   └── DECISION_LOG.md            # Engineering, modeling, and economic trade-offs
├── frontend/
│   ├── src/
│   │   ├── components/            # Navbar, layout components
│   │   ├── pages/                 # Dashboard, Evaluator, WhatsApp, Orders, Settings
│   │   ├── services/api.js        # Axios API client
│   │   ├── styles/index.css       # Complete modern design system
│   │   ├── App.jsx                # Main controller & state
│   │   └── main.jsx               # React entry point
│   ├── package.json
│   └── vite.config.js
├── .env.example
├── .gitignore
└── README.md
```

---

## 6. Deliverables Reference

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Executive Business Memo** | [`docs/BUSINESS_MEMO.pdf`](docs/BUSINESS_MEMO.pdf) | 2-page publication-ready PDF for founder with findings, trade-offs, and 2-week plan. |
| **Architectural Decision Log** | [`docs/DECISION_LOG.md`](docs/DECISION_LOG.md) | In-depth justification of models, thresholds, tech stack, and unit economics. |
| **AI Usage & Verification Log**| [`docs/AI_USAGE_LOG.md`](docs/AI_USAGE_LOG.md) | Transparent accounting of tools, prompts, and verification steps. |
| **System Architecture Guide** | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Complete component diagrams, Mermaid schemas, and API contracts. |
| **Cleaned Historical Dataset** | [`data/cleaned_orders.csv`](data/cleaned_orders.csv) | Deduplicated, feature-engineered dataset of 1,988 unique historical orders. |
| **Empirical Analysis Findings**| [`analysis/findings.json`](analysis/findings.json) | Comprehensive statistical distributions and backtest findings. |
