from datetime import timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.password_reset import _agora, _token_hash, reset_password
from app.services import verificar_senha


def make_session():
    engine = create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def make_user(db):
    empresa = models.Empresa(nome="Empresa de teste")
    db.add(empresa)
    db.flush()
    usuario = models.Usuario(
        empresa_id=empresa.id,
        nome="Administrador",
        username="admin",
        email="admin@example.com",
        password_hash="$scrypt$ln=16,r=8,p=1$AAAAAAAAAAAAAAAAAAAAAA$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        session_version=1,
    )
    db.add(usuario)
    db.flush()
    return usuario


def test_reset_token_is_hashed_and_single_use():
    db = make_session()
    usuario = make_user(db)
    token = "token-super-seguro"
    registro = models.PasswordResetToken(
        usuario_id=usuario.id,
        token_hash=_token_hash(token),
        expires_at=_agora() + timedelta(minutes=30),
    )
    db.add(registro)
    db.commit()

    assert registro.token_hash != token
    assert _token_hash(token) == registro.token_hash
    assert registro.used_at is None

    reset_password(token=token, password="NovaSenha-Segura-123", confirm_password="NovaSenha-Segura-123", db=db)
    db.refresh(usuario)
    db.refresh(registro)

    assert registro.used_at is not None
    assert usuario.session_version == 2
    assert verificar_senha("NovaSenha-Segura-123", usuario.password_hash)
    db.close()


def test_expired_reset_token_is_rejected():
    db = make_session()
    usuario = make_user(db)
    token = "token-expirado"
    registro = models.PasswordResetToken(
        usuario_id=usuario.id,
        token_hash=_token_hash(token),
        expires_at=_agora() - timedelta(seconds=1),
    )
    db.add(registro)
    db.commit()

    try:
        reset_password(token=token, password="NovaSenha-Segura-123", confirm_password="NovaSenha-Segura-123", db=db)
        assert False, "Um token expirado deve ser rejeitado"
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 400

    db.close()
