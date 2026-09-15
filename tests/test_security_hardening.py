from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.services import DUMMY_PASSWORD_HASH, listar_produtos_db, verificar_senha


def make_session():
    engine = create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_dummy_password_hash_is_a_valid_scrypt_hash():
    assert verificar_senha("StockAI-dummy-password", DUMMY_PASSWORD_HASH)
    assert not verificar_senha("wrong-password", DUMMY_PASSWORD_HASH)


def test_product_listing_excludes_archived_products():
    db = make_session()
    empresa = models.Empresa(nome="Empresa de teste")
    db.add(empresa)
    db.flush()
    db.add_all([
        models.Produto(empresa_id=empresa.id, nome="Ativo", ativo=True),
        models.Produto(empresa_id=empresa.id, nome="Arquivado", ativo=False),
    ])
    db.commit()

    produtos = listar_produtos_db(db, empresa.id)

    assert [produto.nome for produto in produtos] == ["Ativo"]
    db.close()
