from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

engine_options = {"future": True, "pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _adicionar_colunas_legadas() -> None:
    inspector = inspect(engine)
    tabelas = set(inspector.get_table_names())
    colunas_por_tabela = {
        "produtos": {"empresa_id": "INTEGER", "codigo_barras": "VARCHAR(64)", "custo": "FLOAT"},
        "movimentacoes": {"empresa_id": "INTEGER", "usuario_id": "INTEGER", "observacao": "VARCHAR(500)"},
    }
    with engine.begin() as connection:
        for tabela, colunas in colunas_por_tabela.items():
            if tabela not in tabelas:
                continue
            existentes = {coluna["name"] for coluna in inspector.get_columns(tabela)}
            for nome, tipo in colunas.items():
                if nome not in existentes:
                    connection.execute(text(f"ALTER TABLE {tabela} ADD COLUMN {nome} {tipo}"))


def create_tables():
    _adicionar_colunas_legadas()
    Base.metadata.create_all(bind=engine)
