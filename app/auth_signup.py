from __future__ import annotations

from fastapi import HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, services


class SignupRequest(BaseModel):
    empresa_nome: str = Field(..., min_length=2, max_length=120)
    admin_nome: str = Field(..., min_length=2, max_length=120)
    admin_username: str = Field(..., min_length=3, max_length=80)
    admin_senha: str = Field(..., min_length=12, max_length=255)


class SignupResponse(BaseModel):
    empresa_id: int
    usuario_id: int
    username: str


def criar_nova_empresa_com_admin(dados: SignupRequest, db: Session) -> SignupResponse:
    """Cria uma nova empresa e seu primeiro usuario admin, em uma unica transacao."""
    empresa_nome = dados.empresa_nome.strip()
    admin_nome = dados.admin_nome.strip()
    admin_username = dados.admin_username.strip().lower()

    if not empresa_nome:
        raise HTTPException(status_code=422, detail="Nome da empresa e obrigatorio")
    if not admin_nome:
        raise HTTPException(status_code=422, detail="Nome do administrador e obrigatorio")
    if not admin_username:
        raise HTTPException(status_code=422, detail="Nome de usuario e obrigatorio")

    usuario_existente = db.query(models.Usuario).filter(models.Usuario.username == admin_username).first()
    if usuario_existente:
        raise HTTPException(status_code=409, detail="Nome de usuario ja esta em uso")

    empresa = models.Empresa(nome=empresa_nome, ativa=True)
    db.add(empresa)

    try:
        db.flush()  # garante empresa.id sem fechar a transacao

        usuario = models.Usuario(
            empresa_id=empresa.id,
            nome=admin_nome,
            username=admin_username,
            password_hash=services.gerar_hash_senha(dados.admin_senha),
            perfil="admin",
            ativo=True,
        )
        db.add(usuario)
        db.flush()

        services.registrar_auditoria(
            db,
            empresa_id=empresa.id,
            usuario_id=usuario.id,
            acao="signup",
            entidade="empresa",
            entidade_id=empresa.id,
            detalhes={"origem": "cadastro_publico"},
        )

        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Nao foi possivel concluir o cadastro. Verifique os dados e tente novamente.")
    except Exception:
        db.rollback()
        raise

    db.refresh(empresa)
    db.refresh(usuario)

    return SignupResponse(empresa_id=empresa.id, usuario_id=usuario.id, username=usuario.username)
