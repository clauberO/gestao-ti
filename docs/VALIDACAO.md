# Validação da etapa inicial

Executado no ambiente de desenvolvimento em 25/09/2026:

- Django `check`: sem problemas.
- `makemigrations --check --dry-run`: sem alterações pendentes.
- `migrate`: esquema inicial criado com sucesso em SQLite.
- `collectstatic`: arquivos estáticos processados com sucesso.
- 17 testes automatizados em SQLite: aprovados, cobrindo login, escopo de técnico, gestão de equipe, CSRF, logout, senhas, conflitos de edição, comentários escapados, CSV e validação de cadastros.
- Dependências instaladas e versões fixadas em `server/requirements.txt`.

O workflow `Gestao TI oficial - testes` repete a suíte com PostgreSQL 17 no GitHub Actions. Consulte o resultado da execução na aba Actions; resultado de SQLite não prova o funcionamento dos bloqueios concorrentes de PostgreSQL.

Ainda não executados nesta entrega local: build Docker, implantação na Oracle, backup/restauração, inspeção visual em navegador e teste real de concorrência com múltiplas conexões. A documentação de implantação inclui a homologação necessária.

A versão oficial permanece em desenvolvimento e não substitui automaticamente a demonstração no Pages.
