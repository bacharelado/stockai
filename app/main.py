import csv
from contextlib import asynccontextmanager
import math
import secrets
import time
from io import StringIO
from pathlib import Path
from threading import Lock

from fastapi import Depends, FastAPI, Form, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import case, func, update
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth_signup import SignupRequest, criar_nova_empresa_com_admin
from app.config import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    AUTO_CREATE_SCHEMA,
    ALLOWED_HOSTS,
    INITIAL_COMPANY_NAME,
    IS_PRODUCTION,
    REQUIRE_AUTH,
    SESSION_SECRET,
    validate_settings,
)
from app.database import create_tables, get_db
from app.password_reset import router as password_reset_router
from app.rate_limit import shared_rate_limit
from app.security_headers import HSTS_VALUE
from app.services import (
    DUMMY_PASSWORD_HASH,
    buscar_produto_db,
    csv_seguro,
    listar_movimentacoes_db,
    listar_produtos_db,
    listar_produtos_paginado_db,
    produto_to_out,
    gerar_hash_senha,
    registrar_auditoria,
    validar_nome_e_categoria,
    verificar_senha,
)


validate_settings()


def bootstrap_conta_inicial() -> None:
    db = next(get_db())
    try:
        empresa = db.query(models.Empresa).order_by(models.Empresa.id).first()
        if not empresa:
            empresa = models.Empresa(nome=INITIAL_COMPANY_NAME)
            db.add(empresa)
            db.flush()
        usuario = db.query(models.Usuario).filter(models.Usuario.username == ADMIN_USERNAME).first()
        if not usuario:
            usuario = models.Usuario(
                empresa_id=empresa.id,
                nome="Administrador",
                username=ADMIN_USERNAME,
                password_hash=gerar_hash_senha(ADMIN_PASSWORD),
                perfil="admin",
                session_version=1,
            )
            db.add(usuario)
            db.flush()
        db.query(models.Produto).filter(models.Produto.empresa_id.is_(None)).update(
            {models.Produto.empresa_id: empresa.id}, synchronize_session=False
        )
        db.query(models.Movimentacao).filter(models.Movimentacao.empresa_id.is_(None)).update(
            {models.Movimentacao.empresa_id: empresa.id}, synchronize_session=False
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if AUTO_CREATE_SCHEMA:
        create_tables()
    bootstrap_conta_inicial()
    yield


app = FastAPI(
    title="StockAI",
    version="2.0.0",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
    description="Sistema de controle de estoque com dashboard, alertas e movimentacoes.",
    lifespan=lifespan,
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET or secrets.token_urlsafe(32),
    https_only=IS_PRODUCTION,
    same_site="lax",
    max_age=60 * 60 * 8,
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(password_reset_router)

RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 120
AUTH_RATE_LIMIT_WINDOW_SECONDS = 5 * 60
AUTH_RATE_LIMIT_MAX_IP_ATTEMPTS = 20
AUTH_RATE_LIMIT_MAX_USERNAME_ATTEMPTS = 10
_rate_limits: dict[str, list[float]] = {}
_auth_ip_attempts: dict[str, list[float]] = {}
_auth_username_attempts: dict[str, list[float]] = {}
_rate_limit_lock = Lock()


def api_response(payload, status_code=200):
    return JSONResponse(status_code=status_code, content={"success": status_code < 400, "data": payload})


def _limitar_login(ip: str, username: str) -> bool:
    chave_usuario = username.strip().lower()
    redis_ip = shared_rate_limit(f"login:ip:{ip}", AUTH_RATE_LIMIT_MAX_IP_ATTEMPTS, AUTH_RATE_LIMIT_WINDOW_SECONDS)
    redis_username = shared_rate_limit(f"login:username:{chave_usuario}", AUTH_RATE_LIMIT_MAX_USERNAME_ATTEMPTS, AUTH_RATE_LIMIT_WINDOW_SECONDS)
    if redis_ip is False or redis_username is False:
        return False
    if redis_ip is True and redis_username is True:
        return True
    agora = time.monotonic()
    with _rate_limit_lock:
        ip_attempts = [item for item in _auth_ip_attempts.get(ip, []) if agora - item < AUTH_RATE_LIMIT_WINDOW_SECONDS]
        username_attempts = [item for item in _auth_username_attempts.get(chave_usuario, []) if agora - item < AUTH_RATE_LIMIT_WINDOW_SECONDS]
        bloqueado = len(ip_attempts) >= AUTH_RATE_LIMIT_MAX_IP_ATTEMPTS or len(username_attempts) >= AUTH_RATE_LIMIT_MAX_USERNAME_ATTEMPTS
        if bloqueado:
            _auth_ip_attempts[ip] = ip_attempts
            _auth_username_attempts[chave_usuario] = username_attempts
            return False
        ip_attempts.append(agora)
        username_attempts.append(agora)
        _auth_ip_attempts[ip] = ip_attempts
        _auth_username_attempts[chave_usuario] = username_attempts
        return True


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login_page(request: Request):
    if request.session.get("authenticated"):
        return RedirectResponse(url="/dashboard", status_code=303)
    success = None
    if request.query_params.get("reset") == "success":
        success = "Senha redefinida com sucesso. Entre novamente com sua nova senha."
    elif request.query_params.get("password_changed") == "success":
        success = "Senha alterada com sucesso. Entre novamente."
    return templates.TemplateResponse(request=request, name="login.html", context={"success": success})


@app.post("/login", include_in_schema=False)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    client_ip = request.client.host if request.client else "unknown"
    username_normalized = username.strip().lower()
    if not _limitar_login(client_ip, username_normalized):
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "Muitas tentativas. Tente novamente em alguns minutos."}, status_code=429)
    db = next(get_db())
    valido = False
    try:
        usuario = db.query(models.Usuario).filter(models.Usuario.username == username_normalized).first()
        password_hash = usuario.password_hash if usuario else DUMMY_PASSWORD_HASH
        senha_valida = verificar_senha(password, password_hash)
        valido = bool(usuario and usuario.ativo and usuario.empresa.ativa and senha_valida)
        if valido:
            user_id = usuario.id
            empresa_id = usuario.empresa_id
            session_version = usuario.session_version or 1
            if usuario.session_version is None:
                usuario.session_version = session_version
            registrar_auditoria(db, usuario.empresa_id, usuario.id, "login", "sessao", usuario.id)
            db.commit()
    finally:
        db.close()
    if not valido:
        return templates.TemplateResponse(request=request, name="login.html", context={"error": "Credenciais invalidas."}, status_code=401)
    request.session.clear()
    request.session["authenticated"] = True
    request.session["user_id"] = user_id
    request.session["empresa_id"] = empresa_id
    request.session["session_version"] = session_version
    request.session["csrf_token"] = secrets.token_urlsafe(32)
    return RedirectResponse(url="/dashboard", status_code=303)


@app.post("/logout", include_in_schema=False)
def logout(request: Request):
    require_auth(request)
    request.session.clear()
    return api_response({"message": "Sessao encerrada"})


@app.get("/signup", response_class=HTMLResponse, include_in_schema=False)
def pagina_signup(request: Request):
    if request.session.get("authenticated"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="signup.html")


@app.post("/api/signup", include_in_schema=False)
def signup(request: Request, dados: SignupRequest, db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    resultado = criar_nova_empresa_com_admin(dados, db, rate_limit_identity=client_ip)
    return api_response(resultado.model_dump(), 201)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return api_response({"detail": exc.detail}, exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    erros_seguros = [{"loc": list(erro.get("loc", [])), "msg": erro.get("msg", "Dados invalidos"), "type": erro.get("type", "value_error")} for erro in exc.errors()]
    return JSONResponse(status_code=422, content={"success": False, "data": {"detail": "Dados invalidos", "errors": erros_seguros}})


@app.middleware("http")
async def protecoes_http(request: Request, call_next):
    client = request.client.host if request.client else "unknown"
    shared_result = shared_rate_limit(f"http:{client}", RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)
    if shared_result is False:
        return JSONResponse(status_code=429, content={"detail": "Muitas requisicoes. Tente novamente em instantes."})
    if shared_result is None:
        now = time.monotonic()
        with _rate_limit_lock:
            requests = [item for item in _rate_limits.get(client, []) if now - item < RATE_LIMIT_WINDOW_SECONDS]
            if len(requests) >= RATE_LIMIT_MAX_REQUESTS:
                return JSONResponse(status_code=429, content={"detail": "Muitas requisicoes. Tente novamente em instantes."})
            requests.append(now)
            _rate_limits[client] = requests
            if len(_rate_limits) > 10000:
                expirados = [key for key, values in _rate_limits.items() if not values or now - values[-1] >= RATE_LIMIT_WINDOW_SECONDS]
                for key in expirados[:5000]:
                    _rate_limits.pop(key, None)
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > 1_000_000:
                return JSONResponse(status_code=413, content={"detail": "Requisicao muito grande"})
        except ValueError:
            return JSONResponse(status_code=400, content={"detail": "Cabecalho invalido"})
    request.state.csp_nonce = secrets.token_urlsafe(16)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = HSTS_VALUE
    response.headers["Content-Security-Policy"] = ("default-src 'self'; " "script-src 'self' 'nonce-" + request.state.csp_nonce + "' https://cdn.jsdelivr.net; " "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; " "font-src 'self' https://fonts.gstatic.com; " "img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'")
    return response


def require_auth(request: Request):
    if not REQUIRE_AUTH:
        return
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Authentication required")
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token or not secrets.compare_digest(csrf_token, request.session.get("csrf_token", "")):
            raise HTTPException(status_code=403, detail="Invalid CSRF token")


def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.Usuario:
    user_id = request.session.get("user_id")
    empresa_id = request.session.get("empresa_id")
    session_version = request.session.get("session_version", 1)
    if not user_id or not empresa_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    usuario = db.query(models.Usuario).filter(models.Usuario.id == user_id, models.Usuario.empresa_id == empresa_id, models.Usuario.ativo.is_(True), models.Usuario.session_version == session_version).first()
    if not usuario or not usuario.empresa.ativa:
        request.session.clear()
        raise HTTPException(status_code=401, detail="Authentication required")
    return usuario


def require_admin(usuario: models.Usuario = Depends(get_current_user)) -> models.Usuario:
    if usuario.perfil != "admin":
        raise HTTPException(status_code=403, detail="Permissao insuficiente")
    return usuario


def require_management(usuario: models.Usuario = Depends(get_current_user)) -> models.Usuario:
    if usuario.perfil not in {"admin", "gerente"}:
        raise HTTPException(status_code=403, detail="Permissao insuficiente")
    return usuario


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def inicio(request: Request):
    if request.session.get("authenticated"):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(request=request, name="landing.html")


@app.get("/health")
def health_check():
    return api_response({"status": "ok", "app": "StockAI"})


@app.post("/produtos", dependencies=[Depends(require_auth)])
def criar_produto(produto: schemas.ProdutoCreate, usuario: models.Usuario = Depends(require_management), db: Session = Depends(get_db)):
    if not math.isfinite(produto.preco):
        raise HTTPException(status_code=400, detail="Valores do produto nao podem ser negativos")
    try:
        nome_limpo, categoria_limpa = validar_nome_e_categoria(produto.nome, produto.categoria)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    codigo_barras = (produto.codigo_barras or "").strip() or None
    if codigo_barras and db.query(models.Produto).filter(models.Produto.empresa_id == usuario.empresa_id, models.Produto.codigo_barras == codigo_barras, models.Produto.ativo.is_(True)).first():
        raise HTTPException(status_code=409, detail="Codigo de barras ja cadastrado")
    novo = models.Produto(empresa_id=usuario.empresa_id, nome=nome_limpo, categoria=categoria_limpa, preco=produto.preco, custo=produto.custo, codigo_barras=codigo_barras, estoque_atual=produto.estoque_atual, estoque_minimo=produto.estoque_minimo)
    db.add(novo)
    db.flush()
    registrar_auditoria(db, usuario.empresa_id, usuario.id, "criar", "produto", novo.id, {"nome": novo.nome})
    db.commit()
    db.refresh(novo)
    return api_response(produto_to_out(novo))


@app.put("/produtos/{produto_id}", dependencies=[Depends(require_auth)])
def atualizar_produto(produto_id: int, dados: schemas.ProdutoUpdate, usuario: models.Usuario = Depends(require_management), db: Session = Depends(get_db)):
    produto = buscar_produto_db(db, usuario.empresa_id, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    if not math.isfinite(dados.preco):
        raise HTTPException(status_code=400, detail="Dados do produto invalidos")
    try:
        nome_limpo, categoria_limpa = validar_nome_e_categoria(dados.nome, dados.categoria)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    codigo_barras = (dados.codigo_barras or "").strip() or None
    if codigo_barras and db.query(models.Produto).filter(models.Produto.empresa_id == usuario.empresa_id, models.Produto.codigo_barras == codigo_barras, models.Produto.id != produto_id, models.Produto.ativo.is_(True)).first():
        raise HTTPException(status_code=409, detail="Codigo de barras ja cadastrado")
    produto.nome = nome_limpo
    produto.categoria = categoria_limpa
    produto.preco = dados.preco
    produto.custo = dados.custo
    produto.codigo_barras = codigo_barras
    produto.estoque_minimo = dados.estoque_minimo
    registrar_auditoria(db, usuario.empresa_id, usuario.id, "atualizar", "produto", produto.id, {"nome": produto.nome})
    db.commit()
    db.refresh(produto)
    return api_response(produto_to_out(produto))


@app.delete("/produtos/{produto_id}", dependencies=[Depends(require_auth)])
def excluir_produto(produto_id: int, usuario: models.Usuario = Depends(require_management), db: Session = Depends(get_db)):
    produto = buscar_produto_db(db, usuario.empresa_id, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    produto.ativo = False
    registrar_auditoria(db, usuario.empresa_id, usuario.id, "excluir", "produto", produto.id, {"nome": produto.nome, "preservado": True})
    db.commit()
    return api_response({"message": "Produto arquivado com sucesso"})


@app.get("/produtos", dependencies=[Depends(require_auth)])
def listar_produtos(usuario: models.Usuario = Depends(get_current_user), db: Session = Depends(get_db), page: int = Query(1, ge=1, le=1_000_000), page_size: int = Query(20, ge=1, le=100), busca: str | None = Query(None, max_length=120), status: str = Query("todos", pattern="^(todos|ok|baixo)$"), categoria: str | None = Query(None, max_length=80), ordenar_por: str = Query("nome", pattern="^(nome|preco|estoque_atual)$"), ordem: str = Query("asc", pattern="^(asc|desc)$")):
    produtos, total = listar_produtos_paginado_db(db, usuario.empresa_id, page=page, page_size=page_size, busca=busca, status=status, categoria=categoria, ordenar_por=ordenar_por, ordem=ordem)
    total_pages = max(1, math.ceil(total / page_size))
    base = db.query(models.Produto).filter(models.Produto.empresa_id == usuario.empresa_id, models.Produto.ativo.is_(True))
    estoque_baixo = models.Produto.estoque_atual <= models.Produto.estoque_minimo
    aggregate = base.with_entities(func.count(models.Produto.id), func.coalesce(func.sum(case((estoque_baixo, 1), else_=0)), 0), func.coalesce(func.sum(models.Produto.estoque_atual), 0), func.coalesce(func.sum(models.Produto.estoque_atual * models.Produto.preco), 0), func.coalesce(func.sum(case((estoque_baixo, models.Produto.estoque_minimo - models.Produto.estoque_atual), else_=0)), 0)).one()
    low_items = base.filter(estoque_baixo).order_by((models.Produto.estoque_minimo - models.Produto.estoque_atual).desc(), models.Produto.nome.asc(), models.Produto.id.asc()).limit(8).all()
    categories = [categoria for (categoria,) in base.with_entities(models.Produto.categoria).filter(models.Produto.categoria.isnot(None), models.Produto.categoria != "").distinct().order_by(models.Produto.categoria.asc()).all()]
    total_products = int(aggregate[0] or 0)
    low_products = int(aggregate[1] or 0)
    summary = {
        "total_products": total_products,
        "low_products": low_products,
        "normal_products": total_products - low_products,
        "total_units": int(aggregate[2] or 0),
        "total_value": float(aggregate[3] or 0),
        "replenishment_units": int(aggregate[4] or 0),
        "low_items": [produto_to_out(p) for p in low_items],
        "categories": categories,
    }
    return api_response({"items": [produto_to_out(p) for p in produtos], "pagination": {"page": page, "page_size": page_size, "total": total, "total_pages": total_pages}, "summary": summary})


@app.post("/produtos/{produto_id}/entrada", dependencies=[Depends(require_auth)])
def registrar_entrada(produto_id: int, mov: schemas.MovimentacaoCreate, usuario: models.Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    produto = buscar_produto_db(db, usuario.empresa_id, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    if mov.quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")
    db.execute(update(models.Produto).where(models.Produto.id == produto_id, models.Produto.empresa_id == usuario.empresa_id, models.Produto.ativo.is_(True)).values(estoque_atual=models.Produto.estoque_atual + mov.quantidade))
    db.add(models.Movimentacao(empresa_id=usuario.empresa_id, produto_id=produto_id, usuario_id=usuario.id, tipo="entrada", quantidade=mov.quantidade, observacao=mov.observacao))
    registrar_auditoria(db, usuario.empresa_id, usuario.id, "entrada", "produto", produto_id, {"quantidade": mov.quantidade})
    db.commit()
    produto = buscar_produto_db(db, usuario.empresa_id, produto_id)
    return api_response(produto_to_out(produto))


@app.post("/produtos/{produto_id}/saida", dependencies=[Depends(require_auth)])
def registrar_saida(produto_id: int, mov: schemas.MovimentacaoCreate, usuario: models.Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    produto = buscar_produto_db(db, usuario.empresa_id, produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto nao encontrado")
    if mov.quantidade <= 0:
        raise HTTPException(status_code=400, detail="Quantidade deve ser maior que zero")
    result = db.execute(update(models.Produto).where(models.Produto.id == produto_id, models.Produto.empresa_id == usuario.empresa_id, models.Produto.ativo.is_(True), models.Produto.estoque_atual >= mov.quantidade).values(estoque_atual=models.Produto.estoque_atual - mov.quantidade))
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(status_code=400, detail="Estoque insuficiente")
    db.add(models.Movimentacao(empresa_id=usuario.empresa_id, produto_id=produto_id, usuario_id=usuario.id, tipo="saida", quantidade=mov.quantidade, observacao=mov.observacao))
    registrar_auditoria(db, usuario.empresa_id, usuario.id, "saida", "produto", produto_id, {"quantidade": mov.quantidade})
    db.commit()
    produto = buscar_produto_db(db, usuario.empresa_id, produto_id)
    return api_response(produto_to_out(produto))


@app.get("/movimentacoes", dependencies=[Depends(require_auth)])
def listar_movimentacoes(usuario: models.Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    movimentacoes = listar_movimentacoes_db(db, usuario.empresa_id)
    return api_response([{"id": mov.id, "produto_id": mov.produto_id, "produto": mov.produto.nome, "tipo": mov.tipo, "quantidade": mov.quantidade, "data": mov.data.isoformat()} for mov in movimentacoes])


@app.get("/produtos/exportar.csv", dependencies=[Depends(require_auth)])
def exportar_produtos(usuario: models.Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    arquivo = StringIO()
    escritor = csv.writer(arquivo)
    escritor.writerow(["ID", "Produto", "Categoria", "Preco", "Estoque atual", "Estoque minimo", "Status"])
    for produto in listar_produtos_db(db, usuario.empresa_id):
        dados = produto_to_out(produto)
        escritor.writerow([dados["id"], csv_seguro(dados["nome"]), csv_seguro(dados["categoria"]), f'{dados["preco"]:.2f}', dados["estoque_atual"], dados["estoque_minimo"], dados["status"]])
    arquivo.seek(0)
    return StreamingResponse(iter([arquivo.getvalue()]), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": "attachment; filename=stockai-produtos.csv"})


@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    if not request.session.get("user_id"):
        return RedirectResponse(url="/login", status_code=303)
    try:
        usuario = get_current_user(request, db)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=303)
    usuarios_admin = []
    if usuario.perfil == "admin":
        usuarios_admin = db.query(models.Usuario).filter(models.Usuario.empresa_id == usuario.empresa_id).order_by(models.Usuario.nome).all()
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"produtos": [], "csrf_token": request.session.get("csrf_token", ""), "empresa": usuario.empresa.nome, "usuario": usuario.nome, "perfil": usuario.perfil, "pode_gerenciar": usuario.perfil in {"admin", "gerente"}, "usuarios_admin": usuarios_admin, "csp_nonce": request.state.csp_nonce})


@app.get("/usuarios", dependencies=[Depends(require_auth)])
def listar_usuarios(usuario: models.Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    usuarios = db.query(models.Usuario).filter(models.Usuario.empresa_id == usuario.empresa_id).order_by(models.Usuario.nome).all()
    return api_response([{"id": item.id, "nome": item.nome, "username": item.username, "email": item.email, "perfil": item.perfil, "ativo": item.ativo} for item in usuarios])


@app.post("/usuarios", dependencies=[Depends(require_auth)])
def criar_usuario(dados: schemas.UsuarioCreate, usuario: models.Usuario = Depends(require_admin), db: Session = Depends(get_db)):
    username = dados.username.strip().lower()
    email = str(dados.email).strip().lower() if dados.email else None
    if db.query(models.Usuario).filter(models.Usuario.username == username).first():
        raise HTTPException(status_code=409, detail="Usuario ja existe")
    if email and db.query(models.Usuario).filter(models.Usuario.email == email).first():
        raise HTTPException(status_code=409, detail="E-mail ja esta em uso")
    novo = models.Usuario(empresa_id=usuario.empresa_id, nome=dados.nome.strip(), username=username, email=email, password_hash=gerar_hash_senha(dados.senha), perfil=dados.perfil, session_version=1)
    db.add(novo)
    db.flush()
    registrar_auditoria(db, usuario.empresa_id, usuario.id, "criar", "usuario", novo.id, {"username": novo.username, "perfil": novo.perfil})
    db.commit()
    return api_response({"id": novo.id, "nome": novo.nome, "username": novo.username, "email": novo.email, "perfil": novo.perfil, "ativo": novo.ativo}, 201)


@app.get("/filiais", dependencies=[Depends(require_auth)])
def listar_filiais(usuario: models.Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    filiais = db.query(models.Filial).filter(models.Filial.empresa_id == usuario.empresa_id).order_by(models.Filial.nome).all()
    return api_response([{"id": filial.id, "nome": filial.nome, "ativa": filial.ativa} for filial in filiais])


@app.post("/filiais", dependencies=[Depends(require_auth)])
def criar_filial(dados: schemas.FilialCreate, usuario: models.Usuario = Depends(require_management), db: Session = Depends(get_db)):
    nome = dados.nome.strip()
    if db.query(models.Filial).filter(models.Filial.empresa_id == usuario.empresa_id, models.Filial.nome == nome).first():
        raise HTTPException(status_code=409, detail="Filial ja cadastrada")
    filial = models.Filial(empresa_id=usuario.empresa_id, nome=nome)
    db.add(filial)
    db.flush()
    registrar_auditoria(db, usuario.empresa_id, usuario.id, "criar", "filial", filial.id, {"nome": filial.nome})
    db.commit()
    return api_response({"id": filial.id, "nome": filial.nome, "ativa": filial.ativa}, 201)


@app.get("/fornecedores", dependencies=[Depends(require_auth)])
def listar_fornecedores(usuario: models.Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    fornecedores = db.query(models.Fornecedor).filter(models.Fornecedor.empresa_id == usuario.empresa_id).order_by(models.Fornecedor.nome).all()
    return api_response([{"id": fornecedor.id, "nome": fornecedor.nome, "documento": fornecedor.documento, "email": fornecedor.email, "telefone": fornecedor.telefone, "ativo": fornecedor.ativo} for fornecedor in fornecedores])


@app.post("/fornecedores", dependencies=[Depends(require_auth)])
def criar_fornecedor(dados: schemas.FornecedorCreate, usuario: models.Usuario = Depends(require_management), db: Session = Depends(get_db)):
    documento = (dados.documento or "").strip() or None
    if documento and db.query(models.Fornecedor).filter(models.Fornecedor.empresa_id == usuario.empresa_id, models.Fornecedor.documento == documento).first():
        raise HTTPException(status_code=409, detail="Fornecedor com este documento ja existe")
    fornecedor = models.Fornecedor(empresa_id=usuario.empresa_id, nome=dados.nome.strip(), documento=documento, email=(dados.email or "").strip() or None, telefone=(dados.telefone or "").strip() or None)
    db.add(fornecedor)
    db.flush()
    registrar_auditoria(db, usuario.empresa_id, usuario.id, "criar", "fornecedor", fornecedor.id, {"nome": fornecedor.nome})
    db.commit()
    return api_response({"id": fornecedor.id, "nome": fornecedor.nome, "documento": fornecedor.documento, "email": fornecedor.email, "telefone": fornecedor.telefone, "ativo": fornecedor.ativo}, 201)
