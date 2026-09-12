"""
Módulo de autenticação e signup para multi-tenant real.
Permite que novos clientes se registrem sem precisar reiniciar o sistema.
"""

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app import models
from app.services import gerar_hash_senha, registrar_auditoria


class SignupRequest(BaseModel):
    """Dados de entrada para criar uma nova conta multi-tenant."""
    nome_empresa: str = Field(..., min_length=2, max_length=120)
    nome_admin: str = Field(..., min_length=2, max_length=120)
    username_admin: str = Field(..., min_length=3, max_length=80, pattern=r"^[a-zA-Z0-9._-]+$")
    senha: str = Field(..., min_length=12, max_length=256)


class SignupResponse(BaseModel):
    """Resposta após signup bem-sucedido."""
    empresa_id: int
    empresa_nome: str
    admin_id: int
    admin_username: str
    mensagem: str


def validar_credenciais_signup(nome_empresa: str, nome_admin: str, username_admin: str, senha: str) -> tuple[str, str, str, str]:
    """
    Valida dados de signup e retorna valores normalizados.
    
    Raises:
        ValueError: Se algum campo estiver inválido
    """
    nome_empresa_limpo = (nome_empresa or "").strip()
    nome_admin_limpo = (nome_admin or "").strip()
    username_limpo = (username_admin or "").strip().lower()
    
    if not nome_empresa_limpo or len(nome_empresa_limpo) < 2:
        raise ValueError("Nome da empresa deve ter pelo menos 2 caracteres")
    if len(nome_empresa_limpo) > 120:
        raise ValueError("Nome da empresa não pode exceder 120 caracteres")
    
    if not nome_admin_limpo or len(nome_admin_limpo) < 2:
        raise ValueError("Nome do administrador deve ter pelo menos 2 caracteres")
    if len(nome_admin_limpo) > 120:
        raise ValueError("Nome do administrador não pode exceder 120 caracteres")
    
    if not username_limpo or len(username_limpo) < 3:
        raise ValueError("Username deve ter pelo menos 3 caracteres")
    if len(username_limpo) > 80:
        raise ValueError("Username não pode exceder 80 caracteres")
    if not all(c.isalnum() or c in "._-" for c in username_limpo):
        raise ValueError("Username só pode conter letras, números, ponto, hífen e underscore")
    
    if not senha or len(senha) < 12:
        raise ValueError("Senha deve ter pelo menos 12 caracteres")
    if len(senha) > 256:
        raise ValueError("Senha não pode exceder 256 caracteres")
    
    return nome_empresa_limpo, nome_admin_limpo, username_limpo, senha


def criar_nova_empresa_com_admin(
    db: Session,
    nome_empresa: str,
    nome_admin: str,
    username_admin: str,
    senha: str
) -> models.Empresa:
    """
    Cria uma nova empresa e seu primeiro usuário administrador.
    
    Transação atômica: ou ambos são criados, ou nada é criado.
    
    Args:
        db: Sessão do banco de dados
        nome_empresa: Nome da empresa
        nome_admin: Nome do usuário administrador
        username_admin: Username (único globalmente)
        senha: Senha em texto plano
    
    Returns:
        Objeto Empresa criado
    
    Raises:
        ValueError: Se o username já existe ou outro erro de validação
    """
    try:
        # Verifica se username já existe (chave única global)
        usuario_existente = db.query(models.Usuario).filter(
            models.Usuario.username == username_admin
        ).first()
        
        if usuario_existente:
            raise ValueError(f"Username '{username_admin}' já está registrado no sistema")
        
        # Cria a empresa
        empresa = models.Empresa(nome=nome_empresa)
        db.add(empresa)
        db.flush()  # Gera o ID da empresa sem commitar
        
        # Cria o usuário admin
        admin = models.Usuario(
            empresa_id=empresa.id,
            nome=nome_admin,
            username=username_admin,
            password_hash=gerar_hash_senha(senha),
            perfil="admin",
        )
        db.add(admin)
        db.flush()
        
        # Registra auditoria do signup
        registrar_auditoria(
            db,
            empresa_id=empresa.id,
            usuario_id=admin.id,
            acao="signup",
            entidade="empresa",
            entidade_id=empresa.id,
            detalhes={"nome_empresa": empresa.nome, "admin_username": admin.username}
        )
        
        db.commit()
        db.refresh(empresa)
        return empresa
        
    except Exception:
        db.rollback()
        raise
