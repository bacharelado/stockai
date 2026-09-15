"""Add password recovery fields and tokens.

Revision ID: 20260915_password_recovery
Revises:
"""

from alembic import op
import sqlalchemy as sa


revision = "20260915_password_recovery"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    usuario_columns = {column["name"] for column in inspector.get_columns("usuarios")}

    if "email" not in usuario_columns:
        op.add_column("usuarios", sa.Column("email", sa.String(length=254), nullable=True))
    if "session_version" not in usuario_columns:
        op.add_column("usuarios", sa.Column("session_version", sa.Integer(), nullable=False, server_default="1"))
        op.alter_column("usuarios", "session_version", server_default=None)

    indexes = {index["name"] for index in inspector.get_indexes("usuarios")}
    if "ix_usuarios_email" not in indexes:
        op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)

    if "password_reset_tokens" not in inspector.get_table_names():
        op.create_table(
            "password_reset_tokens",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("usuario_id", sa.Integer(), nullable=False),
            sa.Column("token_hash", sa.String(length=64), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_password_reset_tokens_id", "password_reset_tokens", ["id"], unique=False)
        op.create_index("ix_password_reset_tokens_usuario_id", "password_reset_tokens", ["usuario_id"], unique=False)
        op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"], unique=True)
        op.create_index("ix_password_reset_tokens_expires_at", "password_reset_tokens", ["expires_at"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "password_reset_tokens" in inspector.get_table_names():
        op.drop_index("ix_password_reset_tokens_expires_at", table_name="password_reset_tokens")
        op.drop_index("ix_password_reset_tokens_token_hash", table_name="password_reset_tokens")
        op.drop_index("ix_password_reset_tokens_usuario_id", table_name="password_reset_tokens")
        op.drop_index("ix_password_reset_tokens_id", table_name="password_reset_tokens")
        op.drop_table("password_reset_tokens")

    indexes = {index["name"] for index in inspector.get_indexes("usuarios")}
    if "ix_usuarios_email" in indexes:
        op.drop_index("ix_usuarios_email", table_name="usuarios")
    usuario_columns = {column["name"] for column in inspector.get_columns("usuarios")}
    if "session_version" in usuario_columns:
        op.drop_column("usuarios", "session_version")
    if "email" in usuario_columns:
        op.drop_column("usuarios", "email")
