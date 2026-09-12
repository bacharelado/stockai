# StockAI 2.0.0

StockAI é um sistema web de controle de estoque para pequenos negócios, lojas e operações pessoais. Ele centraliza produtos, quantidades, alertas e movimentações em um painel simples, responsivo e protegido por login.

## Destaques da V2

- Dashboard responsivo para desktop e celular
- Identidade visual StockAI integrada ao painel
- Cadastro, edição e exclusão de produtos
- Entrada e saída de estoque com histórico
- Alerta quando a quantidade está no mínimo definido ou abaixo dele
- Confirmação antes de excluir produto e histórico
- Filtros, busca, ordenação e paginação de produtos
- Tema claro e escuro
- Exportação da lista de produtos em CSV
- Login administrativo com sessão e proteção CSRF
- Cadastro público de novas empresas (multi-tenant)
- Menus e ações condicionados ao perfil do usuário
- Área administrativa com usuários da empresa
- Encerramento de sessão pelo botão Sair
- Proteções contra XSS, CSV injection, payloads grandes e valores inválidos

## Tecnologias

- Python 3.10+
- FastAPI
- SQLAlchemy
- SQLite para uso local e PostgreSQL para produção
- Jinja2
- JavaScript, HTML e CSS puros

## Requisitos

- Python 3.10 ou superior
- pip

## Instalação

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite o arquivo `.env` e defina valores fortes e exclusivos para:

- `STOCKAI_ADMIN_USERNAME`
- `STOCKAI_ADMIN_PASSWORD`
- `STOCKAI_SESSION_SECRET`

O primeiro início cria a empresa principal e migra os produtos e movimentações existentes para ela. O administrador informado no `.env` é convertido em um usuário persistido com senha armazenada em hash.

Novas empresas também podem se cadastrar de forma independente pela rota `/signup`, sem precisar reiniciar o sistema ou editar o `.env` (veja a seção "Execução").

## PostgreSQL e migrações

Para produção, crie o banco PostgreSQL e defina no `.env`:

```text
STOCKAI_DATABASE_URL=postgresql+psycopg://usuario:senha@host:5432/stockai
STOCKAI_AUTO_CREATE_SCHEMA=false
```

Em seguida, aplique a estrutura versionada antes de iniciar o serviço:

```powershell
alembic upgrade head
```

Nunca use `STOCKAI_AUTO_CREATE_SCHEMA=true` em produção. Faça um backup do banco antes de qualquer atualização de versão.

Por padrão, a autenticação está ativa. Não publique o arquivo `.env`.

## Execução

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Use `--reload` somente durante desenvolvimento local. Para publicar atrás de
um proxy ou túnel, defina `STOCKAI_ENV=production`, mantenha a autenticação
ativa e inclua o domínio público em `STOCKAI_ALLOWED_HOSTS`. Em produção, a
sessão exige HTTPS.

Abra no navegador:

- http://localhost:8000/login
- http://localhost:8000/dashboard
- http://localhost:8000/signup (cadastro de nova empresa)

Em desenvolvimento, a documentação da API fica em `http://localhost:8000/docs`.
Ela é desativada em produção.

## Regras de negócio

- Produtos não aceitam preço ou estoque negativo.
- Entradas e saídas aceitam somente quantidades inteiras maiores que zero.
- Uma saída é bloqueada quando supera o saldo disponível.
- O status de atenção é aplicado ao produto com estoque igual ou menor que o mínimo.
- Ao excluir um produto, as movimentações vinculadas a ele também são removidas após confirmação no painel.

## Perfis e menus

O sistema possui três perfis de acesso, com menus e ações compatíveis com cada função:

- `operador`: acessa resumo, produtos, alertas e histórico; pode registrar entradas e saídas de estoque.
- `gerente`: possui as funções do operador e também acessa os cadastros e o gerenciamento de produtos.
- `admin`: possui as funções do gerente e acessa a área administrativa com a lista de usuários da empresa.

As permissões também são verificadas no backend. Ocultar uma ação no menu não substitui a autorização das rotas da API.

## Segurança aplicada

- Validação de dados com Pydantic e regras adicionais no servidor
- Escapamento de dados renderizados no dashboard
- Proteção para fórmulas maliciosas em CSV
- Limite de 1 MB por requisição
- Cabeçalhos de segurança para conteúdo, frames, referrer e permissões do navegador
- Respostas de validação seguras para valores especiais, como `NaN`
- Sessão administrativa com duração de oito horas e token CSRF para operações que alteram dados
- Logout protegido por CSRF, com limpeza da sessão no servidor

## Estrutura

```text
app/
  __init__.py
  auth_signup.py
  config.py
  static/
    dashboard.css
    dashboard.js
    stockai-logo.jpeg
  templates/
    partials/
    dashboard.html
    signup.html
  database.py
  main.py
  models.py
  schemas.py
  services.py
.env.example
stockai.db
requirements.txt
README.md
```

## Próximos passos

- Gestão de filiais, fornecedores e vendas
- Relatórios e indicadores avançados
