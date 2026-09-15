# StockAI — Engineering Case Study

StockAI is a production-oriented inventory management SaaS built with Python/FastAPI, SQLAlchemy, PostgreSQL and a lightweight HTML/CSS/JavaScript frontend.

This project is useful as a portfolio case study because it demonstrates more than feature development: it shows a real engineering workflow involving debugging, security hardening, automated tests, Git/GitHub pull requests and deployment to a cloud environment.

## What the project demonstrates

- Python backend development with FastAPI and SQLAlchemy
- REST-style application routes and server-rendered views
- Authentication, sessions, CSRF protection and role-based access
- Multi-tenant data isolation by company
- PostgreSQL production configuration and Alembic migrations
- Automated tests and regression-focused testing
- Git branching, pull requests, reviewable commits and controlled merges
- Debugging against a live deployment
- AI-assisted software engineering: using AI to inspect code, reason about regressions, design tests, implement focused changes and validate the result

## Engineering workflow used

```text
Real problem
    ↓
Inspect repository and production behavior
    ↓
Reproduce the issue
    ↓
Trace the data flow and identify the root cause
    ↓
Create an isolated Git branch
    ↓
Implement the smallest safe correction
    ↓
Add regression tests
    ↓
Validate locally and against the deployed application
    ↓
Open a GitHub Pull Request
    ↓
Review the diff and validation results
    ↓
Merge to main
    ↓
Automatic production deployment
```

## Example: product-edit data integrity regression

A concrete production bug was identified in the product-edit flow: the API model supported `custo` (cost) and `codigo_barras` (barcode), while the edit form did not send those fields consistently. Updating an unrelated product field could therefore reset the cost or erase the barcode.

The fix was implemented as a focused pull request:

- [PR #4 — preserve product cost and barcode on edit](https://github.com/bacharelado/stockai/pull/4)

The correction tightened the update contract, exposed the missing fields in the UI and added regression tests for the payload contract. The PR was merged into `main` and became part of the production code path.

## Example: security hardening

A separate security-focused workstream was kept isolated from the product-edit fix:

- [PR #3 — harden authentication and preserve inventory history](https://github.com/bacharelado/stockai/pull/3)

Keeping security work separate from a targeted bug fix makes the changes easier to review and reduces the risk of mixing unrelated production changes.

## Technology stack

| Area | Technologies |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy |
| Validation | Pydantic |
| Database | PostgreSQL, SQLite for local development |
| Migrations | Alembic |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Testing | Python `unittest` / regression tests |
| Version control | Git, GitHub |
| Deployment | Render |
| Engineering workflow | AI-assisted development, code review, automated validation |

## Why this is a useful portfolio project

This repository shows an end-to-end development loop:

1. A real application exists in production.
2. A defect can be reproduced from observed behavior.
3. The codebase is inspected before changing it.
4. The root cause is isolated instead of patching symptoms.
5. The fix is implemented in a dedicated branch.
6. Tests are added to prevent the same regression from returning.
7. The change is proposed through a pull request.
8. The validated change is merged into `main` and deployed.

That workflow is the core story behind the project—not simply the number of technologies used.

## Live application

**StockAI:** https://stockai-6yw7.onrender.com

The live environment is used to validate application behavior after deployment.
