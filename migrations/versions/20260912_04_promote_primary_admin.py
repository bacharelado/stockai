"""promote the primary administrator to platform admin

Revision ID: 20260912_04
Revises: 20260912_03
"""

from alembic import op
import sqlalchemy as sa


revision = "20260912_04"
down_revision = "20260912_03"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "UPDATE usuarios SET plataforma_admin = TRUE "
            "WHERE id = (SELECT MIN(id) FROM usuarios WHERE perfil = 'admin')"
        )
    )


def downgrade():
    bind = op.get_bind()
    bind.execute(sa.text("UPDATE usuarios SET plataforma_admin = FALSE"))
