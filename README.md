# StockAI 2.0.0

StockAI é uma plataforma web de gestão de estoque pensada para pequenos negócios, lojas e operações que precisam de controle simples, seguro e acessível. A proposta é começar pelo estoque e evoluir para uma plataforma SaaS de operação e inteligência para pequenos negócios.

Hoje, o StockAI já centraliza produtos, quantidades, movimentações, alertas, usuários e relatórios em um painel responsivo, com autenticação, permissões e isolamento de dados por empresa. A landing page apresenta o produto, seus recursos e a visão de planos.

## O que já existe

### Estoque

- Dashboard responsivo para desktop e celular
- Cadastro, edição e exclusão de produtos
- Entrada e saída de estoque com histórico
- Alerta quando a quantidade chega ao mínimo definido
- Sugestões de reposição no painel
- Filtros, busca, ordenação e paginação
- Tema claro e escuro
- Exportação de produtos em CSV
- Relatórios de estoque com dados reais
- Indicadores de quantidade, valor e produtos que precisam de atenção

### Empresas e usuários

- Cadastro público de novas empresas
- Arquitetura multi-tenant com isolamento por empresa
- Perfis `operador`, `gerente` e `admin`
- Controle de acesso no backend e no menu
- Administração dos usuários da própria empresa
- Sessão de login e logout
- Auditoria de ações importantes
- Base preparada para administração da plataforma e planos

### Planos

O StockAI já possui uma estrutura centralizada para organizar os planos e preparar a evolução comercial da plataforma:

| Plano | Produtos | Usuários | Situação |
|---|---:|---:|---|
| **Grátis** | Até 50 | Até 2 | Disponível |
| **Pro** | Até 500 | Até 10 | Em breve |
| **Empresa** | Ilimitados | Ilimitados | Em breve |

O plano **Grátis** custa R$ 0/mês e é o ponto de entrada atual. Os preços dos planos pagos ainda não foram definidos e nenhuma cobrança é realizada nesta versão.

A landing page apresenta os planos e direciona novos usuários para o cadastro gratuito. A aplicação já possui campos de plano e status de assinatura no banco de dados, além de regras centralizadas em `app/plans.py`.

> Importante: os limites estão preparados como regra de produto, mas a cobrança e o bloqueio automático por limite ainda fazem parte da evolução comercial.

### Landing page

A página inicial funciona como apresentação comercial do StockAI e inclui:

- Hero com chamada para ação
- Apresentação dos principais recursos
- Seção de planos
- Explicação de como o produto funciona
- Posicionamento "Do Amazonas para o seu negócio"
- Links para cadastro e login
- Canal direto de suporte por WhatsApp e e-mail
- Layout responsivo

### Segurança

- Autenticação baseada em sessão
- Proteção CSRF nas operações que alteram dados
- Senhas armazenadas com hash
- Validação de dados com Pydantic e regras adicionais no servidor
- Escapamento de dados renderizados
- Proteção contra fórmulas maliciosas em CSV
- Limite de 1 MB por requisição
- Cabeçalhos de segurança
- Controle de sessão com duração limitada
- Isolamento de dados por empresa
- Saída de estoque protegida contra saldo insuficiente

## Visão da plataforma

O objetivo do StockAI não é parar em um simples cadastro de produtos. A evolução planejada é transformar o sistema em uma plataforma SaaS para pequenos negócios:

```text
                         STOCKAI
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
       ESTOQUE            VENDAS           COMPRAS
          │                 │                 │
     Produtos            Clientes        Fornecedores
     Entradas             Pedidos        Pedidos de compra
     Saídas               PDV            Reposição
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                           IA
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
       Previsão          Alertas          Sugestões
       de demanda        inteligentes     de compra
```

Essa visão representa o roadmap do produto. Nem todos esses módulos estão implementados na versão atual.

## Roadmap

### Plataforma SaaS

- Super Admin com visão global das empresas
- Gestão de planos e limites por plano
- Aplicação automática dos limites dos planos
- Cobrança e assinaturas
- Status e ativação de empresas
- Métricas gerais da plataforma
- Convites para funcionários
- Recuperação e troca de senha
- E-mails transacionais
- Domínio próprio por empresa
- PWA instalável no celular

### Operação

- Gestão de fornecedores
- Gestão de filiais
- Transferência de estoque entre filiais
- Código de barras e leitura pelo celular
- Módulo de vendas/PDV
- Clientes e pedidos
- Compras e pedidos de compra
- Financeiro operacional básico

### Inteligência

- Previsão de demanda
- Estimativa de dias até acabar o estoque
- Sugestões inteligentes de reposição
- Identificação de produtos parados
- Análise de sazonalidade
- Produtos mais rentáveis
- Assistente de IA para perguntas sobre o negócio
- Alertas inteligentes por e-mail e outros canais

## Tecnologias

- Python 3.10+
- FastAPI
- SQLAlchemy
- Alembic
- SQLite para uso local
- PostgreSQL para produção
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

Novas empresas podem se cadastrar de forma independente pela rota `/signup`, sem editar o `.env`.

## PostgreSQL e migrações

Para produção, defina uma URL PostgreSQL compatível com Psycopg 3:

```text
STOCKAI_DATABASE_URL=postgresql+psycopg://usuario:senha@host:5432/stockai
STOCKAI_AUTO_CREATE_SCHEMA=false
```

Aplique as migrações antes de iniciar o serviço:

```powershell
python -m alembic upgrade head
```

Nunca publique o arquivo `.env` e nunca coloque senhas, tokens ou URLs com credenciais no repositório.

## Execução

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Use `--reload` somente durante desenvolvimento local. Em produção, use HTTPS e configure `STOCKAI_ALLOWED_HOSTS` com o domínio público.

Abra no navegador:

- http://localhost:8000/ — landing page
- http://localhost:8000/login — login
- http://localhost:8000/dashboard — painel
- http://localhost:8000/signup — cadastro de empresa
- http://localhost:8000/static/relatorios.html — relatórios

Em desenvolvimento, a documentação da API fica em `/docs`. Ela é desativada em produção.

## Regras de negócio

- Produtos não aceitam preço ou estoque negativo.
- Entradas e saídas aceitam somente quantidades inteiras maiores que zero.
- Uma saída é bloqueada quando supera o saldo disponível.
- O alerta é aplicado quando o estoque está igual ou abaixo do mínimo.
- Ao excluir um produto, as movimentações vinculadas a ele também são removidas após confirmação.

## Perfis e menus

- `operador`: acessa resumo, produtos, alertas e histórico; pode registrar entradas e saídas.
- `gerente`: possui as funções do operador e também gerencia produtos.
- `admin`: possui as funções do gerente e acessa a administração de usuários da empresa.

As permissões também são verificadas no backend. Ocultar uma ação no menu não substitui a autorização das rotas da API.

## Arquitetura multi-tenant

Cada empresa possui seus próprios usuários, produtos e movimentações. O usuário autenticado é associado à empresa ativa e as consultas e operações do backend respeitam esse vínculo.

A base de dados também já possui campos para plano, status de assinatura e identificação de administrador da plataforma. Esses campos preparam a evolução para um painel de Super Admin, mas o painel global ainda faz parte do roadmap.

## Relatórios

A área de relatórios usa os dados reais do estoque e apresenta:

- produtos cadastrados
- produtos com estoque baixo
- unidades em estoque
- valor do estoque
- produtos que precisam de atenção
- valor por categoria
- movimentações recentes
- exportação do relatório em CSV

## Testes

As regras de planos já possuem testes automatizados com `unittest` em `tests/test_plans.py`.

Para executar:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

A cobertura automatizada será ampliada conforme novos módulos comerciais e operacionais forem implementados.

## Deploy

O StockAI pode rodar localmente com SQLite e em produção com PostgreSQL. No ambiente de produção, o processo de build deve executar as migrações do Alembic antes de iniciar o servidor.

Exemplo de build:

```text
pip install -r requirements.txt && python -m alembic upgrade head
```

Exemplo de start:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Estrutura

```text
app/
  __init__.py
  auth_signup.py
  config.py
  database.py
  main.py
  models.py
  plans.py
  schemas.py
  services.py
  static/
    dashboard.css
    dashboard.js
    dashboard-insights.js
    relatorios.html
    relatorios.js
    stockai-logo.svg
  templates/
    partials/
    dashboard.html
    landing.html
    login.html
    signup.html
migrations/
  versions/
tests/
  test_plans.py
.env.example
requirements.txt
README.md
PITCH.md
```

## Próximos marcos

1. Consolidar a experiência SaaS com Super Admin, empresas e planos.
2. Aplicar limites de produtos e usuários conforme o plano contratado.
3. Integrar cobrança e assinaturas dos planos Pro e Empresa.
4. Adicionar recuperação de senha, convites e notificações.
5. Transformar o controle de estoque em operação completa com compras, vendas e filiais.
6. Evoluir os indicadores para previsão e recomendações inteligentes.
7. Ampliar os testes automatizados e fortalecer observabilidade antes de escalar comercialmente.

## Contato e suporte

StockAI · Controle de estoque

- WhatsApp: (92) 8166-0856
- E-mail: agstarker@gmail.com

## Status do projeto

**StockAI 2.0.0 — base funcional de uma plataforma SaaS de gestão de estoque.**

A versão atual já possui operação de estoque, multi-tenancy, autenticação, perfis, auditoria, relatórios, landing comercial, estrutura inicial de planos e deploy em nuvem. A cobrança, a aplicação automática dos limites comerciais e o painel global de Super Admin ainda estão em evolução.
