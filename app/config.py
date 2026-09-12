"""Configuracoes centralizadas do StockAI."""

import os

from dotenv import load_dotenv


load_dotenv()

ENVIRONMENT = os.getenv("STOCKAI_ENV", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"
REQUIRE_AUTH = os.getenv("STOCKAI_REQUIRE_AUTH", "true").lower() == "true"
ADMIN_USERNAME = os.getenv("STOCKAI_ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("STOCKAI_ADMIN_PASSWORD")
SESSION_SECRET = os.getenv("STOCKAI_SESSION_SECRET")
INITIAL_COMPANY_NAME = os.getenv("STOCKAI_INITIAL_COMPANY_NAME", "Empresa principal")
AUTO_CREATE_SCHEMA = os.getenv("STOCKAI_AUTO_CREATE_SCHEMA", "true").lower() == "true"
DATABASE_URL = os.getenv("STOCKAI_DATABASE_URL", "sqlite:///./stockai.db")
ALLOWED_HOSTS = [host.strip() for host in os.getenv(
    "STOCKAI_ALLOWED_HOSTS", "127.0.0.1,localhost,testserver"
).split(",") if host.strip()]


def validate_settings() -> None:
    """Falha de forma segura quando a autenticacao nao foi configurada."""
    if REQUIRE_AUTH and (not ADMIN_USERNAME or not ADMIN_PASSWORD or not SESSION_SECRET):
        raise RuntimeError(
            "Defina STOCKAI_ADMIN_USERNAME, STOCKAI_ADMIN_PASSWORD e "
            "STOCKAI_SESSION_SECRET antes de iniciar o StockAI."
        )
