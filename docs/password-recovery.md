# Recuperação de senha

O StockAI agora possui um fluxo de recuperação de senha por e-mail e de troca de senha autenticada.

## Fluxo

1. O usuário acessa `/forgot-password`.
2. Informa o e-mail cadastrado.
3. A resposta é genérica, independentemente de a conta existir.
4. Para uma conta válida, o sistema gera um token aleatório de uso único.
5. Somente o hash SHA-256 do token é armazenado no banco.
6. O token expira em 30 minutos.
7. Ao redefinir a senha, o token é marcado como usado e tokens pendentes anteriores são invalidados.
8. A versão da sessão do usuário é incrementada, invalidando sessões anteriores.

## Configuração SMTP

Defina no ambiente:

- `STOCKAI_SMTP_HOST`
- `STOCKAI_SMTP_PORT`
- `STOCKAI_SMTP_USER`
- `STOCKAI_SMTP_PASSWORD`
- `STOCKAI_SMTP_FROM`
- `STOCKAI_SMTP_USE_TLS`
- `STOCKAI_PUBLIC_BASE_URL`

Em produção, `STOCKAI_PUBLIC_BASE_URL` deve ser HTTPS e apontar para o endereço público real do StockAI.

## Segurança

- Rate limit por IP e por e-mail.
- Não há armazenamento de token em texto puro.
- Não há exposição de token nos logs de aplicação.
- Respostas de solicitação não revelam se o e-mail está cadastrado.
- A nova senha precisa ter pelo menos 12 caracteres.
- A troca autenticada exige a senha atual e proteção CSRF.
- Alteração ou recuperação de senha incrementa `session_version` para invalidar sessões antigas.
- Eventos de alteração/redefinição são registrados na auditoria.

## Migração

A estrutura pode ser criada automaticamente pelo mecanismo de schema do StockAI ou aplicada pelo Alembic com a revisão `20260915_password_recovery`.
