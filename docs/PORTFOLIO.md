# StockAI — Engineering Case Study

StockAI is a production-oriented inventory SaaS built for small businesses that need simple, secure and accessible stock control.

This repository is also a practical software-engineering case study: it documents how a real application is inspected, debugged, tested, changed through Git/GitHub, and deployed to a live environment.

## Product at a glance

| Area | Current capability |
|---|---|
| Inventory | Products, stock entries/exits, low-stock alerts and history |
| Operations | Dashboard, reports, CSV export, suppliers and branches |
| Access | Authentication, sessions, roles and company-level isolation |
| Security | CSRF protection, password hashing, validation and security headers |
| Database | PostgreSQL in production, SQLite for local development, Alembic migrations |
| Engineering | Automated tests, focused pull requests and regression fixes |
| Deployment | Cloud deployment with Render |

## Engineering workflow

```text
Observed behavior
      ↓
Inspect repository and production behavior
      ↓
Reproduce and isolate the problem
      ↓
Trace the data flow to the root cause
      ↓
Create an isolated Git branch
      ↓
Implement a focused correction
      ↓
Add regression coverage
      ↓
Validate locally and against the live application
      ↓
Open a GitHub Pull Request
      ↓
Review the change
      ↓
Merge to main
      ↓
Automatic production deployment
```

## A real production bug that was fixed

The product model and API supported `custo` (cost) and `codigo_barras` (barcode), but the product-edit form did not consistently submit those values. Because the update schema supplied defaults, editing an unrelated field could silently reset the cost or erase the barcode.

The correction was delivered through a dedicated pull request:

- [PR #4 — preserve product cost and barcode on edit](https://github.com/bacharelado/stockai/pull/4)

The fix tightened the update contract, exposed the fields in the product forms and added regression tests for the payload contract. The change was then merged into `main` and became part of the production code path.

## Security engineering work

A separate security-focused workstream was kept isolated from the product-edit fix:

- [PR #3 — harden authentication and preserve inventory history](https://github.com/bacharelado/stockai/pull/3)

Separating security hardening from a focused functional fix keeps changes reviewable and reduces the chance of mixing unrelated production changes.

## AI-assisted software engineering

AI is used as an engineering accelerator rather than as a replacement for validation.

The workflow includes:

- Repository exploration and architectural reading
- Root-cause analysis and debugging support
- Test design and regression analysis
- Focused implementation proposals
- Git branch and pull-request workflow
- Review of diffs and validation results
- Live-application verification after deployment

The important skill is not simply generating code with AI. It is being able to inspect, question, test, correct and ship the resulting software responsibly.

## Technology stack

| Layer | Technologies |
|---|---|
| Backend | Python 3.10+, FastAPI, SQLAlchemy |
| Validation | Pydantic |
| Database | PostgreSQL, SQLite |
| Migrations | Alembic |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Testing | Python `unittest` and regression tests |
| Version control | Git and GitHub |
| Deployment | Render |

## What this project demonstrates

- Working on an actual application rather than a tutorial-only repository
- Debugging from observed behavior to root cause
- Safe, focused changes instead of broad rewrites
- Regression-oriented testing
- Pull-request based delivery
- Security-aware backend development
- Multi-tenant application design
- Production database and migration practices
- Deployment-aware development
- AI-assisted software engineering with human validation

## Live application

**StockAI:** https://stockai-6yw7.onrender.com

The live environment is used to verify behavior after changes are deployed.

## Portfolio material

- [Engineering case study](https://github.com/bacharelado/stockai/blob/main/docs/PORTFOLIO.md)
- [Pull requests](https://github.com/bacharelado/stockai/pulls)
- [Project README](https://github.com/bacharelado/stockai/blob/main/README.md)
