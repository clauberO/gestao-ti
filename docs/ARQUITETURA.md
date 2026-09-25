# Arquitetura e acesso

## Decisões

Monólito Django 5.2 com templates HTML: autenticação, autorização, validação e gravação permanecem no servidor. PostgreSQL em produção; Gunicorn atende a aplicação; WhiteNoise serve arquivos estáticos; Nginx termina TLS. Evita a complexidade inicial de uma API e de autenticação duplicadas no navegador.

As dependências instaladas estão fixadas em `server/requirements.txt`. `requirements.in` registra as faixas para futuras atualizações controladas. Nenhum segredo ou banco local deve ser versionado.

## Matriz de permissões

| Recurso | Administrador | Gestor | Técnico |
|---|---|---|---|
| Chamados e atividades | Todos; criar e editar | Todos; criar e editar | Ver os atribuídos a si ou criados por si; atualizar status e comentar |
| Clientes, unidades, equipamentos | Consultar, criar e editar | Consultar, criar e editar | Consultar |
| Agenda | Todos; criar e editar | Todos; criar e editar | Consultar os próprios compromissos |
| Relatórios e CSV | Sim | Sim | Não |
| Contas e perfis | Criar, editar e desativar | Não | Não |
| Alterar a própria senha | Sim | Sim | Sim |
| Administração técnica Django | Superusuário do servidor | Não | Não |

A conta criada via `createsuperuser` é administradora independentemente do campo perfil. Apenas superusuários podem editar outras contas de superusuário. Administradores comuns não podem criar superusuários ou conceder acesso ao admin técnico. Não é permitido desativar a própria conta ou mudar o próprio perfil pela tela de equipe.

Não há exclusão de registros nas telas da primeira entrega. Clientes e usuários podem ser inativados. As relações usam PROTECT para preservar referências históricas. Contas inativas não autenticam. Técnicos veem o catálogo completo de clientes/unidades/equipamentos da organização; isso é uma regra deliberada, não isolamento multiempresa.

## Controles implementados

- Hash de senha pelo Django, validadores e mínimo de 12 caracteres.
- Sessões no banco; cookie HttpOnly, SameSite e Secure em produção.
- CSRF em formulários; templates escapam conteúdo; CSP na aplicação.
- Limites de login no banco compartilhado: 10 tentativas por usuário e 40 por IP a cada 15 minutos, abrangendo também /admin/login/. Tentativas corretas também contam.
- Usuário desativado perde acesso na próxima requisição autenticada.
- Transações ao gravar e registrar auditoria. Eventos de usuários no admin técnico também ficam no LogEntry nativo do Django.
- Controle de versão e bloqueio de linha em alterações de chamados/atividades.
- CSV neutraliza células que podem ser interpretadas como fórmulas.
- Catálogos e agenda usam última gravação; ainda não possuem controle de versão.

## Limites

Auditoria operacional registra autor, instante, ação e objeto, mas não armazena um diff completo e não é um log inviolável contra administradores do banco. MFA, SSO, recuperação por e-mail e gestão visual de sessões ainda não foram entregues. Não há upload de arquivos nesta etapa.

O proxy deve sobrescrever cabeçalhos encaminhados; Gunicorn fica apenas na interface de loopback do host. Controles de transporte não substituem configuração real do domínio e do certificado TLS.

Referências utilizadas: https://docs.djangoproject.com/en/5.2/topics/auth/default/ e https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/.
