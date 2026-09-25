# GESTÃO TI · versão oficial em desenvolvimento

Primeira etapa funcional do sistema, com autenticação, dados no servidor e perfis de acesso. Projeto de uma única organização: clientes são cadastros da operação, não organizações isoladas. Não usar como SaaS multiempresa sem implementar isolamento por organização.

## Dois ambientes

- `main` / `index.html`: demonstração pública já publicada no GitHub Pages.
- `oficial-v1` / `server/`: aplicação Django com PostgreSQL, preparada para implantação própria na VPS. Não é executada pelo GitHub Pages.

Os arquivos Docker antigos da raiz pertencem à demonstração anterior. Para esta versão, use somente `compose.oficial.yaml` e `server/Dockerfile`.

## Entrega inicial

- Login real por usuário e senha; logout por POST e alteração de senha.
- Cadastro e desativação de contas por administradores, sem senha padrão.
- Perfis de administrador, gestor e técnico verificados no servidor.
- Chamados e atividades com responsável, prioridade, prazo, status e comentários.
- Clientes, unidades, equipamentos e agenda em lista.
- Pesquisa, paginação e exportação CSV de chamados.
- Histórico das alterações operacionais e proteção contra sobrescrita concorrente de chamados/atividades.
- Layout responsivo com modo claro e escuro.
- Migrations, testes automatizados e workflow de CI com PostgreSQL.

## Desenvolvimento local

Python 3.12. No terminal, dentro de `server/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DEBUG=1
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

PowerShell: ative com `.\.venv\Scripts\Activate.ps1` e use `$env:DEBUG="1"` no lugar de `export DEBUG=1`.
Abra http://127.0.0.1:8000. O login e a senha são os que você definir no `createsuperuser`. Não existe conta inicial embutida no código.

O ambiente local usa SQLite por conveniência; a configuração de produção exige PostgreSQL. Somente a preferência de tema utiliza localStorage; os cadastros e as sessões ficam no servidor.

## Validação

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
python manage.py test --noinput
```

Resultados e limitações da execução: [docs/VALIDACAO.md](docs/VALIDACAO.md).

## Documentação

- [Instalação na VPS, conta de administrador e backup](docs/IMPLANTACAO.md)
- [Arquitetura e regras de acesso](docs/ARQUITETURA.md)
- [Próximas entregas](docs/ROADMAP.md)

## Estado da implantação

Código inicial para revisão e homologação. Ainda é necessário configurar a VPS, domínio/HTTPS, criar a conta inicial, testar o backup e validar a interface em navegador antes de colocar dados reais. A aplicação não foi instalada automaticamente no servidor Oracle.

Recuperação de senha por e-mail, anexos, SLA por calendário útil, integrações, notificações e manutenção de equipamentos continuam no roadmap. Nenhuma dessas funções é simulada como se estivesse ativa nesta versão.
