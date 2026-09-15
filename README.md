# StockAI

<p align="center">
  <strong>Inventory management SaaS for small businesses</strong><br>
  Built with Python/FastAPI, SQLAlchemy and PostgreSQL, with a lightweight web frontend.
</p>

<p align="center">
  <a href="https://stockai-6yw7.onrender.com">Live Demo</a> ·
  <a href="https://github.com/bacharelado/stockai/pulls">Pull Requests</a> ·
  <a href="https://github.com/bacharelado/stockai/blob/main/docs/PORTFOLIO.md">Engineering Case Study</a>
</p>

---

## Why StockAI

StockAI starts with a practical problem: helping small businesses keep inventory under control without turning the software into an operational burden.

The current product covers products, quantities, stock movements, alerts, reports, users and company-level data isolation. The project is also an engineering case study: changes are investigated, isolated in Git branches, covered by regression tests and delivered through pull requests.

## Product capabilities

| Area | What is available |
|---|---|
| **Inventory** | Product management, entries, exits, low-stock alerts and movement history |
| **Dashboard** | Stock indicators, search, filters, sorting and responsive views |
| **Reports** | Real inventory data, category values, recent movements and CSV export |
| **Companies** | Multi-tenant architecture with company-level data isolation |
| **Access** | Authentication, sessions and `operador` / `gerente` / `admin` roles |
| **Security** | CSRF protection, password hashing, backend authorization, validation and security headers |
| **Operations** | Branches and suppliers with company-scoped data |
| **Commercial foundation** | Centralized plan rules and subscription status fields |

## Engineering highlights

### Real production debugging

A product-edit regression was found where an update could silently reset the product cost or erase its barcode because those fields were not consistently present in the edit payload.

The fix was handled as a focused pull request:

- [PR #4 — preserve product cost and barcode on edit](https://github.com/bacharelado/stockai/pull/4)

The correction tightened the update contract, exposed the missing fields in the UI and added regression tests. It was merged into `main` and deployed through the normal production flow.

### Security work

Security hardening is kept separate from unrelated product fixes so changes stay reviewable:

- [PR #3 — harden authentication and preserve inventory history](https://github.com/bacharelado/stockai/pull/3)

## Technology stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.10+, FastAPI, SQLAlchemy |
| Validation | Pydantic |
| Database | PostgreSQL in production, SQLite locally |
| Migrations | Alembic |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Testing | Python `unittest` and regression tests |
| Version control | Git, GitHub |
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

The important boundary is the backend: UI visibility is not treated as authorization. Company and role checks are enforced server-side.

More detail: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## AI-assisted software engineering

AI is used as an engineering accelerator, not as a substitute for validation.

The development workflow includes repository exploration, debugging, root-cause analysis, test design, focused implementation, Git branching, pull requests, diff review and live validation after deployment.

The goal is to produce software that can be explained, tested and maintained—not simply generated.

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

## Documentation

- [Engineering case study](docs/PORTFOLIO.md)
- [Architecture overview](docs/ARCHITECTURE.md)
- [Security notes](docs/SECURITY.md)
- [Operations and validation](docs/OPERATIONS.md)
- [Product roadmap](docs/ROADMAP.md)
- [Engineering decisions](docs/DECISIONS.md)
- [Contributing](docs/CONTRIBUTING.md)

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

Requirements: Python 3.10+

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

For Windows PowerShell, use the corresponding `.venv\\Scripts\\Activate.ps1` activation command.

### Production database

Production is configured for PostgreSQL with Psycopg 3. Keep credentials in environment variables and never commit secrets.

```text
STOCKAI_DATABASE_URL=postgresql+psycopg://user:password@host:5432/stockai
STOCKAI_AUTO_CREATE_SCHEMA=false
```

## Testing

Run the automated suite with:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Regression-focused checks are part of the development workflow and are expanded as new failure modes are discovered.

## Project status

**StockAI 2.0.0 — functional foundation for a multi-tenant inventory SaaS.**

The current version includes inventory operations, authentication, roles, company isolation, security controls, reports, branches, suppliers, plan foundations and cloud deployment. Billing, automated commercial limits, Super Admin and the intelligence modules remain roadmap work.

## Live application

**https://stockai-6yw7.onrender.com**

## License

See the repository contents for the current project licensing terms.
