from __future__ import annotations

import time
from threading import Lock

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


SIGNUP_RATE_WINDOW_SECONDS = 10 * 60
SIGNUP_RATE_MAX_ATTEMPTS = 5
_signup_attempts: dict[str, list[float]] = {}
_signup_lock = Lock()


def _registrar_tentativa_signup(chave: str) -> None:
    """Reduz tentativas repetidas de cadastro por identidade solicitada."""
    agora = time.monotonic()
    with _signup_lock:
        expiradas = [
            item for item in _signup_attempts.get(chave, [])
            if agora - item < SIGNUP_RATE_WINDOW_SECONDS
        ]
        if len(expiradas) >= SIGNUP_RATE_MAX_ATTEMPTS:
            _signup_attempts[chave] = expiradas
            raise HTTPException(
                status_code=429,
                detail="Muitas tentativas de cadastro. Tente novamente em alguns minutos.",
            )
        expiradas.append(agora)
        _signup_attempts[chave] = expiradas
        if len(_signup_attempts) > 10000:
            expiradas_chaves = [
                key for key, values in _signup_attempts.items()
                if not values or agora - values[-1] >= SIGNUP_RATE_WINDOW_SECONDS
            ]
            for key in expiradas_chaves[:5000]:
                _signup_attempts.pop(key, None)


def _limpar_tentativas_signup(chave: str) -> None:
    with _signup_lock:
        _signup_attempts.pop(chave, None)


def criar_nova_empresa_com_admin(dados: SignupRequest, db: Session, rate_limit_identity: str | None = None) -> SignupResponse:
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

    identidade = (rate_limit_identity or "global").strip().lower()
    chave_rate_limit = f"{identidade}::{admin_username}"
    _registrar_tentativa_signup(chave_rate_limit)

    usuario_existente = db.query(models.Usuario).filter(models.Usuario.username == admin_username).first()
    if usuario_existente:
        raise HTTPException(status_code=409, detail="Nome de usuario ja esta em uso")

    empresa = models.Empresa(nome=empresa_nome, ativa=True)
    db.add(empresa)

    try:
        db.flush()

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

    _limpar_tentativas_signup(chave_rate_limit)
    db.refresh(empresa)
    db.refresh(usuario)

    return SignupResponse(empresa_id=empresa.id, usuario_id=usuario.id, username=usuario.username)
