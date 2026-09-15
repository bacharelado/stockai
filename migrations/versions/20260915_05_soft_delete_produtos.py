"""preserve product history with soft delete

Revision ID: 20260915_05
Revises: 20260912_04
"""

from alembic import op
import sqlalchemy as sa

revision = "20260915_05"
down_revision = "20260912_04"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("produtos", sa.Column("ativo", sa.Boolean(), nullable=True, server_default=sa.true()))
    op.execute(sa.text("UPDATE produtos SET ativo = TRUE WHERE ativo IS NULL"))
    op.alter_column("produtos", "ativo", nullable=False, server_default=None)
    op.create_index("ix_produtos_ativo", "produtos", ["ativo"])


def downgrade():
    op.drop_index("ix_produtos_ativo", table_name="produtos")
    op.drop_column("produtos", "ativo")
