# StockAI — Roadmap Futuro de Inteligência Artificial

> Documento de visão e planejamento. As funcionalidades descritas aqui são propostas para evolução futura do StockAI e não devem ser interpretadas como funcionalidades já disponíveis no sistema.

## 1. Objetivo

Este documento registra uma visão futura para integração de Inteligência Artificial ao StockAI. A proposta é utilizar IA para reduzir o trabalho manual de cadastro, interpretação e análise de informações de estoque, mantendo as regras de negócio e o banco de dados sob controle da aplicação.

A IA deve funcionar como uma camada inteligente entre o usuário e os serviços do StockAI, e não como substituta da lógica de negócio.

## 2. Situação atual

O StockAI possui uma arquitetura baseada em frontend, API FastAPI, autenticação, regras de negócio, SQLAlchemy e persistência em banco de dados. O sistema já contempla operações relacionadas a produtos, estoque e movimentações.

A integração completa de IA ainda é uma evolução futura. Este documento serve como referência para desenvolvimento posterior e para apoiar o trabalho da equipe com ferramentas de IA.

## 3. Visão futura da arquitetura

Fluxo conceitual:

```text
Usuário
   ↓
Frontend StockAI
   ↓
FastAPI
   ├── Serviços de negócio
   └── Serviço de IA
          ↓
      Provedor de IA
   ↓
Dados validados pelo StockAI
   ↓
PostgreSQL
```

A IA não deverá acessar o PostgreSQL diretamente. O backend deverá selecionar e fornecer somente os dados necessários, sempre respeitando a empresa do usuário autenticado.

## 4. Princípio fundamental

```text
IA interpreta.
StockAI valida.
Banco de dados registra.
```

A IA poderá interpretar uma solicitação, sugerir uma ação ou gerar uma análise. A aplicação continuará responsável por validar permissões, produtos, quantidades, regras de estoque e demais regras de negócio antes de alterar os dados.

## 5. Funcionalidades planejadas

### 5.1 Cadastro inteligente de produtos

Permitir que o usuário forneça informações de produtos em linguagem natural para que a IA identifique e estruture campos como nome, categoria, unidade e outras informações disponíveis.

Exemplo conceitual:

> "Cadastrar Coca-Cola 2 litros, refrigerante, unidade."

A IA produziria uma estrutura para validação pelo StockAI antes do cadastro.

### 5.2 Importação e interpretação de documentos

Futuramente, a IA poderá auxiliar na leitura de documentos relacionados ao estoque, como notas fiscais, listas de produtos e outros arquivos estruturados ou semiestruturados.

O resultado deverá ser convertido em dados estruturados e submetido à validação da aplicação.

### 5.3 Entrada e saída de estoque por linguagem natural

O usuário poderá descrever uma movimentação sem precisar preencher manualmente todos os campos.

Exemplo conceitual:

> "Recebi 20 caixas de Coca-Cola 2L do fornecedor X."

A IA poderá identificar a intenção, o produto, a quantidade, a unidade e informações relacionadas. O StockAI deverá validar os dados e solicitar confirmação antes de efetivar uma movimentação quando necessário.

### 5.4 Análise inteligente de estoque

A IA poderá analisar os dados fornecidos pelo sistema para identificar situações como:

- produtos com estoque baixo;
- excesso de estoque;
- produtos sem movimentação;
- alterações relevantes nas movimentações;
- tendências de entrada e saída;
- possíveis necessidades de reposição.

As análises deverão ser baseadas nos dados reais disponibilizados pelo StockAI, sem criação de informações não existentes.

### 5.5 Alertas inteligentes

Além dos alertas baseados em regras fixas, uma evolução futura poderá utilizar IA para contextualizar situações importantes e explicar ao usuário por que determinado produto merece atenção.

### 5.6 Consultas em linguagem natural

O usuário poderá fazer perguntas sobre os dados disponíveis no StockAI, por exemplo:

> "Quais produtos estão com estoque baixo?"

> "Quais produtos não tiveram movimentação recentemente?"

> "Quais itens tiveram maior saída no período?"

A resposta deverá utilizar somente dados autorizados pelo backend.

### 5.7 Relatórios e insights

A IA poderá auxiliar na interpretação de relatórios, resumindo informações e destacando pontos relevantes para o usuário.

## 6. Estrutura de módulos sugerida

Uma possível evolução da estrutura do projeto:

```text
app/
├── ai/
│   ├── __init__.py
│   ├── client.py
│   ├── prompts.py
│   ├── stock_assistant.py
│   ├── document_parser.py
│   └── inventory_agent.py
│
├── services/
├── models/
├── schemas.py
└── main.py
```

Os nomes acima são sugestões de organização e poderão ser alterados conforme a implementação real.

## 7. Responsabilidade de cada camada

### Frontend

Responsável pela interação com o usuário e pela apresentação das respostas e propostas geradas pela IA.

### FastAPI

Responsável por autenticação, autorização, validação, seleção dos dados e comunicação entre frontend, serviços de negócio e IA.

### Serviço de IA

Responsável por preparar contexto, instruções e solicitações para o provedor de IA e interpretar a resposta recebida.

### Serviços de negócio

Responsáveis pelas regras reais do StockAI e pela execução das operações permitidas.

### PostgreSQL

Continua sendo a fonte de verdade dos dados persistidos do sistema.

## 8. Segurança e isolamento de dados

A integração futura deverá respeitar a arquitetura de segurança existente.

Regras fundamentais:

1. A IA não deve receber dados de outras empresas.
2. O `empresa_id` do usuário autenticado deve determinar o escopo dos dados consultados.
3. Chaves de API e outros segredos devem permanecer em variáveis de ambiente ou mecanismo seguro equivalente.
4. Dados desnecessários não devem ser enviados ao provedor externo de IA.
5. A resposta da IA não deve ser tratada automaticamente como uma operação válida de banco de dados.
6. Operações que alterem estoque devem passar pelas regras de negócio existentes.
7. Entradas produzidas por IA devem ser validadas antes de qualquer persistência.

## 9. Como outras IAs poderão ajudar

Este documento também funciona como contexto para futuras sessões com ferramentas de IA.

Uma IA auxiliar poderá receber este roadmap junto com os arquivos relevantes do projeto para ajudar em tarefas como:

- analisar a arquitetura existente antes de alterar código;
- criar schemas Pydantic para dados produzidos pela IA;
- implementar clientes para provedores de IA;
- criar prompts estruturados;
- desenvolver endpoints FastAPI;
- criar testes unitários e de integração;
- revisar isolamento por `empresa_id`;
- melhorar a interface do dashboard;
- documentar novas decisões arquiteturais;
- revisar código sem substituir regras de negócio existentes.

Antes de alterar qualquer arquivo, a IA auxiliar deverá verificar a implementação atual do repositório e preservar os padrões já utilizados pelo projeto.

## 10. Ordem sugerida de implementação futura

Quando a equipe decidir implementar a IA de forma efetiva, uma sequência possível é:

1. Definir o provedor e a configuração de acesso.
2. Criar a camada de comunicação com o provedor de IA.
3. Implementar consultas em linguagem natural somente para leitura.
4. Adicionar análises de estoque.
5. Implementar interpretação de entradas e saídas.
6. Adicionar importação e interpretação de documentos.
7. Integrar as funcionalidades ao dashboard.
8. Criar testes e revisar segurança.
9. Atualizar a documentação da arquitetura.

A ordem poderá ser modificada conforme as necessidades do projeto.

## 11. Critérios para uma futura implementação

Uma funcionalidade de IA deverá ser considerada pronta somente quando:

- estiver integrada aos serviços corretos do StockAI;
- respeitar autenticação e isolamento por empresa;
- possuir validação das entradas e respostas relevantes;
- não alterar dados diretamente por decisão exclusiva da IA;
- possuir tratamento de erros do provedor;
- possuir testes adequados;
- estiver documentada;
- puder ser executada sem expor chaves ou outros segredos no código-fonte.

## 12. Visão de longo prazo

A visão futura é transformar o StockAI em um sistema no qual a inteligência artificial reduza a complexidade das tarefas de gerenciamento de estoque sem retirar do sistema o controle sobre os dados e as regras de negócio.

O objetivo não é simplesmente adicionar um chatbot. A IA deverá atuar como uma camada de interpretação, automação e análise, enquanto o StockAI continuará responsável pela consistência, segurança e persistência das informações.

---

**Status:** planejamento futuro  
**Implementação completa:** não realizada  
**Documento:** referência arquitetural para evolução do StockAI
