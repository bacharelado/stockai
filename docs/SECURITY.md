# StockAI — Security Notes

StockAI treats security as part of the application design, not as a separate afterthought.

## Current controls

- Session-based authentication
- Password hashing
- CSRF protection for state-changing operations
- Backend permission checks for protected actions
- Pydantic and server-side input validation
- Tenant isolation by company
- Security response headers
- Request-size limits
- Safe CSV handling to reduce spreadsheet formula injection risk
- Stock-out validation to prevent negative inventory

## Engineering practice

Security-sensitive changes are kept reviewable through focused branches and pull requests. A dedicated security hardening workstream is tracked separately from functional bug fixes.

See [PR #3](https://github.com/bacharelado/stockai/pull/3).

## Production notes

Production deployments use PostgreSQL and Alembic migrations. Secrets and environment-specific credentials belong in the deployment environment and must not be committed to Git.

This document is a project overview, not a claim of formal security certification or a complete penetration-test report.
