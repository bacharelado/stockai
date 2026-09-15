from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.services import DUMMY_PASSWORD_HASH, listar_produtos_db, listar_produtos_paginado_db, verificar_senha


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


def test_product_pagination_is_server_side_and_company_scoped():
    db = make_session()
    empresa_a = models.Empresa(nome="Empresa A")
    empresa_b = models.Empresa(nome="Empresa B")
    db.add_all([empresa_a, empresa_b])
    db.flush()
    db.add_all([
        models.Produto(empresa_id=empresa_a.id, nome="Zeta", estoque_atual=1, estoque_minimo=2, ativo=True),
        models.Produto(empresa_id=empresa_a.id, nome="Alfa", estoque_atual=10, estoque_minimo=2, ativo=True),
        models.Produto(empresa_id=empresa_a.id, nome="Beta", estoque_atual=4, estoque_minimo=2, ativo=True),
        models.Produto(empresa_id=empresa_b.id, nome="Outro tenant", ativo=True),
        models.Produto(empresa_id=empresa_a.id, nome="Arquivado", ativo=False),
    ])
    db.commit()

    primeira, total = listar_produtos_paginado_db(db, empresa_a.id, page=1, page_size=2)
    segunda, total_segunda = listar_produtos_paginado_db(db, empresa_a.id, page=2, page_size=2)

    assert total == 3
    assert total_segunda == 3
    assert [produto.nome for produto in primeira] == ["Alfa", "Beta"]
    assert [produto.nome for produto in segunda] == ["Zeta"]

    baixos, total_baixos = listar_produtos_paginado_db(
        db,
        empresa_a.id,
        page=1,
        page_size=10,
        status="baixo",
    )
    assert total_baixos == 1
    assert [produto.nome for produto in baixos] == ["Zeta"]
    db.close()
