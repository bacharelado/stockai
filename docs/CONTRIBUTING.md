# Contributing to StockAI

## Development flow

Keep changes small and focused.

```text
Issue / observed behavior
        ↓
Investigation
        ↓
Feature or bugfix branch
        ↓
Implementation + tests
        ↓
Pull Request
        ↓
Review / validation
        ↓
main
```

## Guidelines

- Prefer focused pull requests over mixed changes.
- Add regression coverage for bugs that can recur.
- Keep security-sensitive behavior enforced on the backend.
- Do not commit secrets, local `.env` files or credentials.
- Describe validation steps clearly in pull requests.
- Treat the live application as a validation target, not as a substitute for tests.

## AI-assisted development

AI tools may be used to accelerate investigation, implementation and test design. Generated changes must still be understood, reviewed and validated by the contributor.

## Commit style

Use concise, action-oriented commit messages such as:

```text
fix: preserve product fields during update
feat: add supplier management
security: harden session validation
test: cover concurrent stock exits
```
