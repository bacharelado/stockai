from alembic import op
from sqlalchemy import inspect, text


revision = "20260912_02"
down_revision = "20260912_01"
branch_labels = None
depends_on = None


def _count(connection, statement):
    return connection.execute(text(statement)).scalar() or 0


def _create_missing_indexes(connection):
    inspector = inspect(connection)
    indexes = {
        table: {index["name"] for index in inspector.get_indexes(table)}
        for table in ("produtos", "movimentacoes")
    }
    expected = {
        "produtos": [("ix_produtos_empresa_id", ["empresa_id"])],
        "movimentacoes": [
            ("ix_movimentacoes_empresa_id", ["empresa_id"]),
            ("ix_movimentacoes_produto_id", ["produto_id"]),
            ("ix_movimentacoes_usuario_id", ["usuario_id"]),
        ],
    }
    for table, table_indexes in expected.items():
        for name, columns in table_indexes:
            if name not in indexes[table]:
                op.create_index(name, table, columns)


def upgrade():
    connection = op.get_bind()
    inspector = inspect(connection)

    if _count(connection, "SELECT COUNT(*) FROM produtos WHERE empresa_id IS NULL"):
        raise RuntimeError("Não foi possível tornar produtos.empresa_id obrigatório: existem registros sem empresa.")
    if _count(connection, "SELECT COUNT(*) FROM movimentacoes WHERE empresa_id IS NULL OR data IS NULL"):
        raise RuntimeError("Não foi possível corrigir movimentacoes: existem registros incompletos.")
    if _count(connection, """
        SELECT COUNT(*) FROM produtos
        WHERE codigo_barras IS NOT NULL
        GROUP BY empresa_id, codigo_barras
        HAVING COUNT(*) > 1
    """):
        raise RuntimeError("Não foi possível criar a unicidade de código de barras: existem duplicidades.")
    if _count(connection, """
        SELECT COUNT(*) FROM movimentacoes m
        LEFT JOIN empresas e ON e.id = m.empresa_id
        LEFT JOIN usuarios u ON u.id = m.usuario_id
        WHERE e.id IS NULL OR (m.usuario_id IS NOT NULL AND u.id IS NULL)
    """):
        raise RuntimeError("Não foi possível criar as relações de movimentações: existem referências inválidas.")

    produto_columns = {column["name"]: column for column in inspector.get_columns("produtos")}
    produto_constraints = inspector.get_unique_constraints("produtos")
    produto_foreign_keys = {tuple(key["constrained_columns"]) for key in inspector.get_foreign_keys("produtos")}
    produto_needs_rebuild = (
        produto_columns["empresa_id"]["nullable"]
        or produto_columns["preco"]["nullable"]
        or produto_columns["custo"]["nullable"]
        or produto_columns["estoque_atual"]["nullable"]
        or produto_columns["estoque_minimo"]["nullable"]
        or produto_columns["criado_em"]["nullable"]
        or not any(set(constraint["column_names"]) == {"empresa_id", "codigo_barras"} for constraint in produto_constraints)
        or ("empresa_id",) not in produto_foreign_keys
    )
    if produto_needs_rebuild:
        with op.batch_alter_table("produtos", recreate="always") as batch:
            batch.alter_column("empresa_id", nullable=False)
            batch.alter_column("preco", nullable=False)
            batch.alter_column("custo", nullable=False)
            batch.alter_column("estoque_atual", nullable=False)
            batch.alter_column("estoque_minimo", nullable=False)
            batch.alter_column("criado_em", nullable=False)
            if not any(set(constraint["column_names"]) == {"empresa_id", "codigo_barras"} for constraint in produto_constraints):
                batch.create_unique_constraint("uq_produto_empresa_codigo_barras", ["empresa_id", "codigo_barras"])
            if ("empresa_id",) not in produto_foreign_keys:
                batch.create_foreign_key("fk_produtos_empresa_id_empresas", "empresas", ["empresa_id"], ["id"])

    movimentacao_columns = {column["name"]: column for column in inspector.get_columns("movimentacoes")}
    movimentacao_foreign_keys = {tuple(key["constrained_columns"]) for key in inspector.get_foreign_keys("movimentacoes")}
    movimentacao_needs_rebuild = (
        movimentacao_columns["empresa_id"]["nullable"]
        or movimentacao_columns["data"]["nullable"]
        or ("empresa_id",) not in movimentacao_foreign_keys
        or ("usuario_id",) not in movimentacao_foreign_keys
    )
    if movimentacao_needs_rebuild:
        with op.batch_alter_table("movimentacoes", recreate="always") as batch:
            batch.alter_column("empresa_id", nullable=False)
            batch.alter_column("data", nullable=False)
            if ("empresa_id",) not in movimentacao_foreign_keys:
                batch.create_foreign_key("fk_movimentacoes_empresa_id_empresas", "empresas", ["empresa_id"], ["id"])
            if ("usuario_id",) not in movimentacao_foreign_keys:
                batch.create_foreign_key("fk_movimentacoes_usuario_id_usuarios", "usuarios", ["usuario_id"], ["id"])

    _create_missing_indexes(connection)


def downgrade():
    # A reversão automática poderia reintroduzir o schema legado sem necessidade.
    pass