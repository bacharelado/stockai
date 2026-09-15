# StockAI — Architecture Overview

## Runtime flow

```text
Browser
   │
   ▼
FastAPI application
   │
   ├── Session authentication
   ├── CSRF validation
   ├── Role/permission checks
   ├── Pydantic validation
   │
   ▼
Service / domain logic
   │
   ▼
SQLAlchemy
   │
   ▼
PostgreSQL (production)
```

## Tenant isolation

Every authenticated operation is evaluated in the context of the active company. Products, users and stock movements are associated with that company, and backend queries respect the tenant boundary.

## Data integrity approach

Inventory changes are treated as business operations rather than simple UI edits. Stock entries and exits update the current quantity and create corresponding movement records and audit information.

Product editing also uses an explicit update contract so important fields cannot silently fall back to unintended defaults.

## Security layers

- Session-based authentication
- Password hashing
- CSRF protection on state-changing operations
- Backend authorization checks
- Input validation
- Security response headers
- Request-size limits
- Safe CSV output handling
- Tenant-level data isolation

## Delivery model

```text
feature / bug
     │
     ▼
feature branch
     │
     ▼
focused commit(s)
     │
     ▼
Pull Request
     │
     ▼
validation / review
     │
     ▼
main
     │
     ▼
automatic deployment
```

This architecture is intentionally documented at the level a reviewer or recruiter can understand quickly, while the source code remains the authoritative implementation.
