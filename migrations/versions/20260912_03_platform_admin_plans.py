"""add platform admin and subscription fields

Revision ID: 20260912_03
Revises: 20260912_02
"""

from alembic import op
import sqlalchemy as sa


revision = "20260912_03"
down_revision = "20260912_02"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("usuarios", sa.Column("plataforma_admin", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("empresas", sa.Column("plano", sa.String(length=24), nullable=False, server_default="gratuito"))
    op.add_column("empresas", sa.Column("status_assinatura", sa.String(length=24), nullable=False, server_default="ativa"))


def downgrade():
    op.drop_column("empresas", "status_assinatura")
    op.drop_column("empresas", "plano")
    op.drop_column("usuarios", "plataforma_admin")
