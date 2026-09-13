from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app import models
from app.database import get_db


def _get_current_user_for_platform(
    request: Request,
    db: Session = Depends(get_db),
) -> models.Usuario:
    user_id = request.session.get("user_id")
    empresa_id = request.session.get("empresa_id")
    if not user_id or not empresa_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == user_id,
        models.Usuario.empresa_id == empresa_id,
        models.Usuario.ativo.is_(True),
    ).first()
    if not usuario or not usuario.empresa.ativa:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Authentication required")
    return usuario


def require_platform_admin(
    usuario: models.Usuario = Depends(_get_current_user_for_platform),
) -> models.Usuario:
    """Permite acesso apenas ao administrador da plataforma, não a admins de empresas."""
    if not usuario.plataforma_admin:
        raise HTTPException(status_code=403, detail="Permissao de plataforma insuficiente")
    return usuario


def listar_empresas_plataforma(
    db: Session,
    usuario: models.Usuario,
) -> list[dict]:
    """Retorna um resumo das empresas sem depender do tenant da sessao."""
    if not usuario.plataforma_admin:
        raise HTTPException(status_code=403, detail="Permissao de plataforma insuficiente")

    empresas = db.query(models.Empresa).order_by(models.Empresa.id).all()
    resultado = []
    for empresa in empresas:
        total_usuarios = db.query(models.Usuario).filter(
            models.Usuario.empresa_id == empresa.id
        ).count()
        total_produtos = db.query(models.Produto).filter(
            models.Produto.empresa_id == empresa.id
        ).count()
        resultado.append({
            "id": empresa.id,
            "nome": empresa.nome,
            "ativa": empresa.ativa,
            "plano": empresa.plano,
            "status_assinatura": empresa.status_assinatura,
            "total_usuarios": total_usuarios,
            "total_produtos": total_produtos,
        })
    return resultado
