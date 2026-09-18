# Pitch — StockAI

## Em uma frase

**StockAI é uma plataforma de gestão de estoque para pequenos negócios que transforma controle de produtos em decisões mais simples sobre a operação.**

## O problema

Muitos pequenos negócios ainda controlam estoque em papel, planilhas ou sistemas difíceis de usar. Isso gera problemas simples, mas caros:

- falta de visibilidade do estoque real;
- produtos que acabam sem aviso;
- dinheiro parado em mercadoria;
- dificuldade para saber o que precisa ser reposto;
- histórico de entradas e saídas espalhado;
- pouca clareza sobre quem pode alterar informações.

O problema não é apenas cadastrar produtos. É **saber o que está acontecendo no estoque e agir antes que vire prejuízo**.

## A solução

O StockAI reúne em um único painel:

- produtos e quantidades;
- entradas e saídas;
- histórico de movimentações;
- alertas de estoque baixo;
- sugestões de reposição;
- relatórios e indicadores;
- usuários e permissões;
- empresas isoladas em uma arquitetura multi-tenant;
- auditoria e proteções de segurança.

A experiência foi pensada para ser simples o suficiente para um pequeno negócio começar rapidamente, mas estruturada para crescer junto com a operação.

## O diferencial

O StockAI começa resolvendo o básico de forma simples e tem uma direção clara para evoluir de **controle** para **inteligência**.

Na apresentação comercial, o diferencial é comunicado em quatro frentes:

- **preço previsível:** proposta de valor mensal fixa, sem cobrança surpresa por quantidade de produtos;
- **inteligência:** evolução para recomendações de compra e uso dos dados do estoque para apoiar decisões;
- **simplicidade:** experiência pensada para pequenos negócios e para usuários acostumados a controles manuais;
- **proximidade:** proposta de atendimento e suporte próximo ao cliente.

Os detalhes comerciais apresentados como proposta devem ser distinguidos do que já está implementado no produto.

A próxima camada do produto pode responder perguntas como:

> “O que está acabando?”

> “Quanto dinheiro está parado no estoque?”

> “O que eu preciso comprar esta semana?”

> “Quais produtos estão parados?”

> “Em quantos dias este produto deve acabar?”

A ideia é fazer a plataforma sair de um sistema que apenas registra o que aconteceu para um sistema que **ajuda o dono do negócio a decidir o que fazer**.

## Produto hoje

A versão atual já possui:

- dashboard responsivo;
- CRUD de produtos;
- controle de entradas e saídas;
- histórico;
- alertas de estoque mínimo;
- sugestões de reposição;
- relatórios com dados reais;
- exportação CSV;
- login e sessão;
- proteção CSRF;
- perfis operador, gerente e admin;
- cadastro público de empresas;
- isolamento de dados por empresa;
- auditoria;
- SQLite no desenvolvimento;
- PostgreSQL em produção;
- deploy em nuvem.

## Visão de futuro

O roadmap do StockAI é transformar a solução em uma plataforma SaaS completa para pequenos negócios.

### Plataforma

- Super Admin;
- gestão de empresas;
- planos e limites;
- status de assinatura;
- métricas globais;
- convites de funcionários;
- recuperação de senha;
- notificações e e-mails;
- PWA e experiência mobile.

### Operação

- fornecedores;
- filiais;
- transferências entre filiais;
- código de barras;
- vendas e PDV;
- clientes e pedidos;
- compras;
- financeiro operacional básico.

### Inteligência

- previsão de demanda;
- previsão de ruptura;
- recomendação de compra;
- identificação de estoque parado;
- análise de sazonalidade;
- produtos mais rentáveis;
- assistente de IA;
- alertas inteligentes.

## Modelo de negócio

A direção comercial é um modelo SaaS, com cobrança recorrente e proposta de entrada simples para pequenos negócios.

Para a apresentação comercial, a equipe pode trabalhar com uma **proposta de mensalidade fixa de R$ 300**, sem cobrança adicional por quantidade de produtos. Esse valor deve ser tratado como **proposta comercial da apresentação**, não como preço definitivo do produto.

A definição final de planos, preços, limites e recursos comerciais permanece sujeita à decisão da equipe.

Exemplo de estrutura futura:

| Plano | Perfil | Objetivo |
|---|---|---|
| Gratuito | negócio começando | controle básico |
| Pro | negócio em crescimento | relatórios, automações e mais usuários |
| Empresa | operação maior | filiais, limites maiores e recursos avançados |

**Os planos e preços definitivos ainda fazem parte da definição comercial do produto.**

## Público-alvo

- pequenos comércios;
- lojas de bairro;
- mercados e mercearias;
- depósitos;
- pequenos distribuidores;
- negócios com estoque próprio;
- empreendedores que precisam substituir planilhas por uma solução organizada.

## Por que agora?

Pequenos negócios precisam de tecnologia, mas nem sempre conseguem adotar ferramentas grandes, caras ou complexas. O StockAI busca ocupar esse espaço com uma proposta direta:

**menos complicação, mais controle e decisões melhores.**

## Pitch de 30 segundos

> “O StockAI é uma plataforma de gestão de estoque criada para pequenos negócios. Em vez de depender de papel ou planilhas, o empresário acompanha produtos, entradas, saídas, alertas e relatórios em um único painel. A plataforma já trabalha com usuários, permissões, isolamento por empresa e PostgreSQL em produção. O próximo passo é transformar esses dados em inteligência: prever quando um produto vai acabar, sugerir quanto comprar e alertar o empresário antes que falte mercadoria. A ideia é transformar o estoque de uma tarefa operacional em uma ferramenta de decisão para o negócio.”

## Pitch para apresentação acadêmica

> “O StockAI é uma aplicação web multi-tenant para gestão de estoque de pequenos negócios. O sistema possui autenticação baseada em sessão, controle de acesso por papéis, isolamento de dados por empresa, auditoria, proteção CSRF, validação de entradas, controle transacional das movimentações e suporte a SQLite no desenvolvimento e PostgreSQL em produção. Além do controle operacional, a aplicação possui relatórios e indicadores de estoque. Como evolução, o projeto foi estruturado para receber recursos de plataforma SaaS e inteligência de dados, como previsão de demanda, recomendações de reposição e um assistente de IA.”

## Pitch comercial

> “Seu estoque não deveria ser uma planilha que você confere depois do problema. O StockAI mostra o que você tem, o que está acabando e onde precisa prestar atenção. E a próxima evolução é fazer a própria plataforma analisar seus dados e recomendar o que comprar e quando comprar. É gestão de estoque simples hoje, inteligência para o negócio amanhã.”

## Frase de impacto

**StockAI — controle o estoque hoje. Tome decisões melhores amanhã.**

## Observação de posicionamento

O StockAI atual é uma **base funcional de produto**, não uma promessa de que todos os recursos do roadmap já estão disponíveis. Super Admin completo, planos comerciais definitivos, vendas, filiais, código de barras e inteligência avançada devem ser tratados como etapas futuras de desenvolvimento.

Na comunicação da apresentação, recursos futuros devem ser apresentados como **proposta ou evolução do produto**, enquanto dashboard, produtos, entradas e saídas, histórico, alertas, sugestões de reposição, relatórios, usuários, permissões, isolamento por empresa e segurança podem ser apresentados como recursos da versão atual.
