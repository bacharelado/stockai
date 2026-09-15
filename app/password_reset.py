from __future__ import annotations

import hashlib
import html
import logging
import secrets
import smtplib
import time
from datetime import timedelta
from email.message import EmailMessage
from threading import Lock

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app import models, services
from app.config import PUBLIC_BASE_URL, SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USE_TLS, SMTP_USER
from app.database import get_db
from app.rate_limit import shared_rate_limit

router = APIRouter()
logger = logging.getLogger(__name__)
RESET_TOKEN_TTL = timedelta(minutes=30)
RESET_RATE_WINDOW = 15 * 60
RESET_RATE_MAX = 5
_reset_attempts: dict[str, list[float]] = {}
_reset_lock = Lock()


def _agora():
    return models.agora_utc()


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _rate_limit_reset(identity: str) -> bool:
    chave = identity.strip().lower()
    redis_result = shared_rate_limit(f"password-reset:{chave}", RESET_RATE_MAX, RESET_RATE_WINDOW)
    if redis_result is False:
        return False
    if redis_result is True:
        return True
    agora = time.monotonic()
    with _reset_lock:
        tentativas = [item for item in _reset_attempts.get(chave, []) if agora - item < RESET_RATE_WINDOW]
        if len(tentativas) >= RESET_RATE_MAX:
            _reset_attempts[chave] = tentativas
            return False
        tentativas.append(agora)
        _reset_attempts[chave] = tentativas
        if len(_reset_attempts) > 10000:
            expiradas = [key for key, values in _reset_attempts.items() if not values or agora - values[-1] >= RESET_RATE_WINDOW]
            for key in expiradas[:5000]:
                _reset_attempts.pop(key, None)
    return True


def _enviar_email_recuperacao(destinatario: str, token: str) -> None:
    if not SMTP_HOST or not SMTP_FROM:
        raise RuntimeError("SMTP nao configurado para recuperacao de senha")
    mensagem = EmailMessage()
    mensagem["Subject"] = "Redefinição de senha — StockAI"
    mensagem["From"] = SMTP_FROM
    mensagem["To"] = destinatario
    mensagem.set_content(
        "Recebemos uma solicitação para redefinir sua senha do StockAI.\n\n"
        f"Use este link para criar uma nova senha:\n{PUBLIC_BASE_URL}/reset-password/{token}\n\n"
        "O link expira em 30 minutos e pode ser usado apenas uma vez.\n\n"
        "Se você não solicitou esta alteração, ignore esta mensagem."
    )
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
        if SMTP_USE_TLS:
            smtp.starttls()
        if SMTP_USER:
            smtp.login(SMTP_USER, SMTP_PASSWORD or "")
        smtp.send_message(mensagem)


def _usuario_por_sessao(request: Request, db: Session) -> models.Usuario:
    user_id = request.session.get("user_id")
    empresa_id = request.session.get("empresa_id")
    session_version = request.session.get("session_version", 1)
    if not user_id or not empresa_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    usuario = db.query(models.Usuario).filter(
        models.Usuario.id == user_id,
        models.Usuario.empresa_id == empresa_id,
        models.Usuario.ativo.is_(True),
        models.Usuario.session_version == session_version,
    ).first()
    if not usuario or not usuario.empresa.ativa:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Authentication required")
    return usuario


def _csrf(request: Request, form_token: str | None = None) -> None:
    token = request.headers.get("X-CSRF-Token") or form_token
    if not token or not secrets.compare_digest(token, request.session.get("csrf_token", "")):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(f"<!doctype html><html lang='pt-br'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{html.escape(title)} | StockAI</title><style>body{{font-family:Segoe UI,Arial,sans-serif;background:#eef3fb;min-height:100vh;display:grid;place-items:center;margin:0;padding:20px}}.card{{width:min(460px,100%);background:#fff;padding:32px;border-radius:18px;box-shadow:0 20px 50px #17255420}}h1{{margin:0 0 10px;color:#172554}}p{{color:#64748b;line-height:1.5}}label{{display:block;color:#334155;font-weight:700;font-size:13px;margin-top:18px}}input{{width:100%;box-sizing:border-box;margin-top:7px;padding:12px;border:1px solid #cbd5e1;border-radius:10px;font:inherit}}button{{width:100%;margin-top:22px;padding:13px;border:0;border-radius:10px;background:#245f9f;color:#fff;font-weight:700;cursor:pointer}}a{{color:#245f9f;text-decoration:none}}</style></head><body><main class='card'>{body}</main></body></html>")


@router.get("/forgot-password", response_class=HTMLResponse, include_in_schema=False)
def forgot_password_page(request: Request):
    return _page("Recuperar senha", "<h1>Recuperar senha</h1><p>Informe seu e-mail. Se existir uma conta associada, enviaremos instruções para redefinir a senha.</p><form method='post' action='/forgot-password'><label for='email'>E-mail<input id='email' name='email' type='email' autocomplete='email' required maxlength='254'></label><button type='submit'>Enviar instruções</button></form><p><a href='/login'>Voltar para o login</a></p>")


@router.post("/forgot-password", response_class=HTMLResponse, include_in_schema=False)
def forgot_password(request: Request, email: str = Form(...), db: Session = Depends(get_db)):
    email_normalized = email.strip().lower()
    client_ip = request.client.host if request.client else "unknown"
    if not _rate_limit_reset(f"ip:{client_ip}") or not _rate_limit_reset(f"email:{email_normalized}"):
        raise HTTPException(status_code=429, detail="Muitas solicitações. Tente novamente em alguns minutos.")
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email_normalized, models.Usuario.ativo.is_(True)).first()
    if usuario:
        agora = _agora()
        db.query(models.PasswordResetToken).filter(models.PasswordResetToken.usuario_id == usuario.id, models.PasswordResetToken.used_at.is_(None)).delete(synchronize_session=False)
        token = secrets.token_urlsafe(32)
        registro = models.PasswordResetToken(usuario_id=usuario.id, token_hash=_token_hash(token), expires_at=agora + RESET_TOKEN_TTL)
        db.add(registro)
        db.commit()
        try:
            _enviar_email_recuperacao(usuario.email, token)
        except Exception:
            logger.exception("Falha ao enviar e-mail de recuperação; token invalidado")
            db.delete(registro)
            db.commit()
    return _page("Verifique seu e-mail", "<h1>Confira seu e-mail</h1><p>Se existir uma conta associada ao endereço informado, você receberá as instruções para redefinir a senha.</p><p><a href='/login'>Voltar para o login</a></p>")


@router.get("/reset-password/{token}", response_class=HTMLResponse, include_in_schema=False)
def reset_password_page(token: str, db: Session = Depends(get_db)):
    registro = db.query(models.PasswordResetToken).filter(models.PasswordResetToken.token_hash == _token_hash(token), models.PasswordResetToken.used_at.is_(None), models.PasswordResetToken.expires_at > _agora()).first()
    if not registro or not registro.usuario.ativo:
        raise HTTPException(status_code=400, detail="Link de recuperação inválido ou expirado.")
    safe_token = html.escape(token, quote=True)
    return _page("Nova senha", f"<h1>Nova senha</h1><p>Escolha uma senha forte com pelo menos 12 caracteres.</p><form method='post' action='/reset-password'><input type='hidden' name='token' value='{safe_token}'><label for='password'>Nova senha<input id='password' name='password' type='password' autocomplete='new-password' minlength='12' maxlength='256' required></label><label for='confirm_password'>Confirmar senha<input id='confirm_password' name='confirm_password' type='password' autocomplete='new-password' minlength='12' maxlength='256' required></label><button type='submit'>Redefinir senha</button></form>")


@router.post("/reset-password", response_class=HTMLResponse, include_in_schema=False)
def reset_password(token: str = Form(...), password: str = Form(...), confirm_password: str = Form(...), db: Session = Depends(get_db)):
    if password != confirm_password:
        raise HTTPException(status_code=422, detail="As senhas não coincidem.")
    if len(password) < 12:
        raise HTTPException(status_code=422, detail="A senha deve ter pelo menos 12 caracteres.")
    registro = db.query(models.PasswordResetToken).filter(models.PasswordResetToken.token_hash == _token_hash(token), models.PasswordResetToken.used_at.is_(None), models.PasswordResetToken.expires_at > _agora()).first()
    if not registro or not registro.usuario.ativo:
        raise HTTPException(status_code=400, detail="Link de recuperação inválido ou expirado.")
    usuario = registro.usuario
    usuario.password_hash = services.gerar_hash_senha(password)
    usuario.session_version = (usuario.session_version or 1) + 1
    registro.used_at = _agora()
    db.query(models.PasswordResetToken).filter(models.PasswordResetToken.usuario_id == usuario.id, models.PasswordResetToken.id != registro.id, models.PasswordResetToken.used_at.is_(None)).delete(synchronize_session=False)
    services.registrar_auditoria(db, usuario.empresa_id, usuario.id, "redefinir_senha", "usuario", usuario.id, {"origem": "recuperacao_email"})
    db.commit()
    return RedirectResponse(url="/login?reset=success", status_code=303)


@router.get("/change-password", response_class=HTMLResponse, include_in_schema=False)
def change_password_page(request: Request, db: Session = Depends(get_db)):
    usuario = _usuario_por_sessao(request, db)
    return _page("Alterar senha", f"<h1>Alterar senha</h1><p>Conta: {html.escape(usuario.username)}</p><form method='post' action='/change-password'><input type='hidden' name='csrf_token' value='{html.escape(request.session.get('csrf_token', ''), quote=True)}'><label for='current_password'>Senha atual<input id='current_password' name='current_password' type='password' autocomplete='current-password' required></label><label for='new_password'>Nova senha<input id='new_password' name='new_password' type='password' autocomplete='new-password' minlength='12' maxlength='256' required></label><label for='confirm_password'>Confirmar nova senha<input id='confirm_password' name='confirm_password' type='password' autocomplete='new-password' minlength='12' maxlength='256' required></label><button type='submit'>Alterar senha</button></form><p><a href='/dashboard'>Voltar ao painel</a></p>")


@router.post("/change-password", response_class=HTMLResponse, include_in_schema=False)
def change_password(request: Request, current_password: str = Form(...), new_password: str = Form(...), confirm_password: str = Form(...), csrf_token: str = Form(...), db: Session = Depends(get_db)):
    _csrf(request, csrf_token)
    usuario = _usuario_por_sessao(request, db)
    if not services.verificar_senha(current_password, usuario.password_hash):
        raise HTTPException(status_code=400, detail="Senha atual inválida.")
    if new_password != confirm_password:
        raise HTTPException(status_code=422, detail="As senhas não coincidem.")
    if len(new_password) < 12:
        raise HTTPException(status_code=422, detail="A nova senha deve ter pelo menos 12 caracteres.")
    if services.verificar_senha(new_password, usuario.password_hash):
        raise HTTPException(status_code=400, detail="A nova senha deve ser diferente da atual.")
    usuario.password_hash = services.gerar_hash_senha(new_password)
    usuario.session_version = (usuario.session_version or 1) + 1
    services.registrar_auditoria(db, usuario.empresa_id, usuario.id, "alterar_senha", "usuario", usuario.id, {"origem": "sessao_autenticada"})
    db.commit()
    request.session.clear()
    return RedirectResponse(url="/login?password_changed=success", status_code=303)
