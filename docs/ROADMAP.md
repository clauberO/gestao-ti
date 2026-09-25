# Plano de entregas

## Etapa 1 · Base funcional (esta branch)

Autenticação, perfis, equipe, clientes/unidades, chamados/atividades, equipamentos, agenda em lista, histórico operacional, CSV, testes e configuração de implantação. Requer homologação antes de produção.

## Etapa 2 · Implantação

Restabelecer SSH da Oracle, definir subdomínio, configurar TLS/proxy, executar migrations, criar administrador interativamente, testar PostgreSQL e restauração, revisar telas desktop/celular e acompanhar logs. A URL definitiva depende do domínio informado pelo proprietário.

## Etapa 3 · Atendimento

SLA com calendário e feriados; fila, tags e categorias; histórico detalhado de alterações; encerramento com diagnóstico; anexos com limites e validação; modelos de atendimento; recuperação de senha via provedor de e-mail e expiração de tokens.

## Etapa 4 · Gestão

Agenda em calendário; manutenção vinculada a equipamentos; documentos e garantias; indicadores por período e técnico; notificações e integrações aprovadas. Cada integração exige credenciais e configuração próprias.

## Etapa 5 · Operação contínua

MFA/SSO conforme necessidade; monitoramento e alertas; atualização de dependências; backup externo com testes de restauração; revisão de acesso, desempenho e acessibilidade. Multiempresa somente após introduzir isolamento por organização em consultas, permissões e testes.
