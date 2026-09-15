# StockAI — Portfolio Case Study

**Production-oriented inventory SaaS | Python | FastAPI | SQLAlchemy | PostgreSQL | Git/GitHub | Render**

## What this project demonstrates

StockAI is a real web application used to demonstrate an end-to-end software engineering workflow: understand a production problem, inspect the codebase, reproduce the behavior, identify the root cause, implement a focused fix, add regression tests, review the change through GitHub, merge it into `main` and deploy it.

The development workflow also uses **AI-assisted software engineering**: AI is used as an engineering copilot for repository exploration, debugging, test design, implementation, review and validation while the resulting changes remain controlled through Git and code review.

## Real engineering work

### Product data-integrity regression

A bug was identified in the product-edit flow: the application supported product **cost** and **barcode**, but the edit form did not consistently send those fields. An unrelated edit could therefore reset the cost or remove the barcode.

The correction:

- tightened the `ProdutoUpdate` contract;
- exposed cost and barcode in product forms;
- preserved existing values during edits;
- added regression tests;
- was delivered through a dedicated GitHub Pull Request;
- was merged into `main` and included in the production deployment path.

**Pull Request:** [#4 — fix: preserve product cost and barcode on edit](https://github.com/bacharelado/stockai/pull/4)

### Security-focused engineering

A separate security hardening workstream was kept isolated from the product bug fix to keep changes reviewable and reduce unrelated production risk.

**Pull Request:** [#3 — security: harden authentication and preserve inventory history](https://github.com/bacharelado/stockai/pull/3)

## Engineering workflow

```text
Production behavior
      ↓
Repository inspection
      ↓
Bug reproduction
      ↓
Root-cause analysis
      ↓
Focused Git branch
      ↓
Implementation
      ↓
Regression tests
      ↓
GitHub Pull Request
      ↓
Review / validation
      ↓
Merge to main
      ↓
Automatic deployment
```

## Technical stack

| Area | Stack |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL production / SQLite local |
| Migrations | Alembic |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Testing | Python automated/regression tests |
| Version control | Git, GitHub, Pull Requests |
| Deployment | Render |
| Development style | AI-assisted / AI-native software workflow |

## Production features

- Multi-tenant company isolation
- Authentication and sessions
- Role-based permissions
- CSRF protection and security headers
- Product and inventory management
- Inventory movement history
- Low-stock alerts
- Reports and CSV export
- PostgreSQL migrations
- Cloud deployment

## Live project

**https://stockai-6yw7.onrender.com**

## Why it belongs in a portfolio

The important part of StockAI is not only the technology stack. It demonstrates the ability to work on a living application and move from **problem → diagnosis → implementation → testing → Pull Request → merge → deployment**.
