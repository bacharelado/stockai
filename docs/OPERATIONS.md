# StockAI — Operations & Validation

## Production validation used during development

The application has been exercised through both automated HTTP checks and browser-driven validation.

### Authentication

A real signup/login flow was validated against the deployed service, including successful account creation and redirect into the dashboard.

### Product workflow

The product flow has been exercised end-to-end:

1. Create a product.
2. Confirm it appears in the dashboard.
3. Edit the product.
4. Validate that important fields remain intact after the update.

### Deployment

The production application is deployed at:

https://stockai-6yw7.onrender.com

Deployments follow the repository's Git workflow and can be validated against the live environment after changes reach `main`.

## Testing philosophy

The project favors small regression tests around real failure modes. A test should protect a behavior that could realistically break again, not simply increase a coverage number.

## Local test command

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Browser automation

Browser checks can be run separately with Playwright when a UI workflow needs verification. Credentials should always be supplied through environment variables rather than committed or embedded in scripts.
