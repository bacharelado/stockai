# StockAI

<p align="center">
  <strong>Inventory management SaaS for small businesses</strong><br>
  Practical inventory control today, data-driven decisions tomorrow.
</p>

<p align="center">
  <a href="https://stockai-6yw7.onrender.com">Live Demo</a> ·
  <a href="https://github.com/bacharelado/stockai/pulls">Pull Requests</a> ·
  <a href="https://github.com/bacharelado/stockai/blob/portfolio-showcase-2026/docs/PORTFOLIO.md">Engineering Case Study</a> ·
  <a href="https://github.com/bacharelado/stockai/tree/portfolio-showcase-2026/docs">Documentation</a>
</p>

<p align="center">
  <img src="https://github.com/bacharelado/stockai/actions/workflows/tests.yml/badge.svg?branch=main" alt="Tests">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/FastAPI-application-009688" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-production-4169E1" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Deployment-Render-46E3B7" alt="Render">
</p>

---

## Overview

StockAI is a web-based inventory platform designed for small businesses that need a simple way to manage products, stock movements and operational visibility without depending on scattered spreadsheets.

The project combines a real product with an engineering case study: problems are investigated from observed behavior, isolated in focused Git branches, corrected with regression tests and delivered through GitHub pull requests.

## What the product does

| Area | Current capabilities |
|---|---|
| **Inventory** | Products, entries, exits, stock levels, low-stock alerts and movement history |
| **Dashboard** | Indicators, search, filters, sorting, pagination and responsive views |
| **Reports** | Inventory metrics, category values, recent movements and CSV export |
| **Companies** | Multi-tenant data isolation by company |
| **Access control** | Sessions with `operador`, `gerente` and `admin` roles |
| **Security** | CSRF protection, password hashing, backend authorization, validation and security headers |
| **Operations** | Company-scoped branches and suppliers |
| **Commercial foundation** | Centralized plan rules and subscription-status fields |

## Engineering highlights

### Production bug fixed through a focused pull request

A product-edit regression could cause the product cost or barcode to be lost when an unrelated field was changed.

The fix tightened the update contract, exposed the missing fields in the forms and added regression coverage.

→ [PR #4 — preserve product cost and barcode on edit](https://github.com/bacharelado/stockai/pull/4)

### Security work kept isolated

Security hardening was handled as a separate workstream so unrelated production changes remained focused and reviewable.

→ [PR #3 — harden authentication and preserve inventory history](https://github.com/bacharelado/stockai/pull/3)

## Technology stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.10+, FastAPI, SQLAlchemy |
| Validation | Pydantic |
| Database | PostgreSQL in production, SQLite locally |
| Migrations | Alembic |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Testing | Python `unittest` and regression tests |
| Version control | Git + GitHub |
| Deployment | Render |

## Architecture

```text
Browser
   │
   ▼
FastAPI
   │
   ├── Session authentication
   ├── CSRF validation
   ├── Role checks
   ├── Pydantic validation
   │
   ▼
Application / service logic
   │
   ▼
SQLAlchemy
   │
   ▼
PostgreSQL
```

The backend is the authorization boundary: UI visibility is not treated as permission. Company and role checks are enforced server-side.

→ [Architecture documentation](docs/ARCHITECTURE.md)

## AI-assisted software engineering

AI is used as an engineering accelerator rather than as a substitute for validation.

The workflow includes repository exploration, debugging, root-cause analysis, test design, focused implementation, Git branching, pull requests, diff review and live validation.

The goal is software that can be understood, tested and maintained—not simply generated.

## Engineering workflow

```text
Observe
  ↓
Reproduce
  ↓
Inspect
  ↓
Find root cause
  ↓
Create focused branch
  ↓
Implement + test
  ↓
Open Pull Request
  ↓
Validate
  ↓
Merge to main
  ↓
Deploy
```

## Repository structure

```text
stockai/
├── app/             # application code
├── migrations/      # Alembic migrations
├── tests/            # automated tests
├── docs/             # product, engineering and support documentation
│   └── product/      # pitches and positioning
├── .github/          # CI and security configuration
├── .env.example      # local environment template
├── alembic.ini
├── requirements.txt
└── README.md
```

The root is intentionally small. Detailed product and engineering material lives under `docs/` so visitors, contributors and recruiters can find the main project entry point quickly.

## Documentation

- [Documentation index](docs/README.md)
- [Engineering case study](docs/PORTFOLIO.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Security](docs/SECURITY.md)
- [Operations and validation](docs/OPERATIONS.md)
- [Roadmap](docs/ROADMAP.md)
- [Engineering decisions](docs/DECISIONS.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Support](docs/SUPPORT.md)
- [Product pitch](docs/product/PITCH.md)
- [Elevator pitch](docs/product/ELEVATOR_PITCH.md)

## Roadmap

### Platform

- Super Admin and global company management
- Automatic enforcement of plan limits
- Billing and subscriptions
- Invitations, recovery and notifications
- Stronger observability

### Operations

- Stock transfers between branches
- Purchase orders and deeper supplier workflows
- Barcode scanning
- Sales / POS
- Customers and orders
- Operational finance

### Intelligence

- Demand forecasting
- Days-to-stockout estimation
- Smart replenishment recommendations
- Stagnant-inventory detection
- Seasonality and profitability insights
- Natural-language business assistant

## Local development

### Requirements

- Python 3.10+
- pip

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

For Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

### Environment

Keep credentials in environment variables and never commit secrets.

For production PostgreSQL:

```text
STOCKAI_DATABASE_URL=postgresql+psycopg://user:password@host:5432/stockai
STOCKAI_AUTO_CREATE_SCHEMA=false
```

## Testing

Every push and pull request targeting `main` runs the automated test suite through GitHub Actions.

Run locally with:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Regression-focused checks are expanded as new failure modes are discovered.

## Project status

**StockAI 2.0.0 — functional foundation for a multi-tenant inventory SaaS.**

The current version includes inventory operations, authentication, roles, company isolation, security controls, reports, branches, suppliers, plan foundations and cloud deployment.

Billing, automatic commercial limits, Super Admin and advanced intelligence modules remain roadmap work.

## Live application

**https://stockai-6yw7.onrender.com**

## License

See the repository contents for the current project licensing terms.
