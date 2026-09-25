# GESTÃO TI — Protótipo para Oracle VPS

Primeira etapa de implementação do visual aprovado. Aplicação web estática em HTML, CSS e JavaScript, servida por Nginx em Docker. Não requer Node na VPS. O código está em `web/` e não depende de CDNs.

## O que funciona

- Tema claro/escuro, layout adaptado para celular e navegação por módulos.
- Visão geral com indicadores e quadro de atividades calculados dos registros.
- Criar, editar e consultar chamados, atividades, agendamentos, equipamentos, clientes, unidades e usuários demonstrativos.
- Concluir chamados e atividades; registrar manutenção vinculada ao equipamento.
- Buscar e filtrar registros; exportar chamados em CSV.
- Editar preferências, perfil e parâmetros visuais de SLA.
- Telas de acesso, recuperação e redefinição com simulação explícita.

Os dados ficam em localStorage, separados por navegador e endereço. Não são compartilhados entre usuários e podem ser perdidos ao limpar dados do navegador. Use somente dados de teste. O botão de entrada não autentica. Senhas digitadas na simulação não são armazenadas. Nenhum convite, e-mail ou integração é executado.

## Instalação na VPS (Ubuntu com Docker e Compose)

Este projeto usa uma pasta própria e porta 8088, sem alterar o projeto Elo Afiliados. Os comandos abaixo são para executar manualmente; a VPS ainda não foi acessada por esta entrega.

1. Baixe `gestao-ti-oracle-prototipo.zip` para seu computador.
2. No PowerShell, na pasta do arquivo, substitua `CAMINHO_DA_CHAVE` e `IP_DA_VPS`:

```powershell
scp -i "CAMINHO_DA_CHAVE" .\gestao-ti-oracle-prototipo.zip ubuntu@IP_DA_VPS:/home/ubuntu/
ssh -i "CAMINHO_DA_CHAVE" ubuntu@IP_DA_VPS
```

3. No terminal da VPS, confirme os pré-requisitos:

```bash
docker --version
docker compose version
ss -ltn 'sport = :8088'
```

Se Docker ou Compose não estiverem instalados, siga https://docs.docker.com/engine/install/ubuntu/ antes de continuar. Se a porta já estiver ocupada, escolha outra no `compose.yaml` e no túnel abaixo. Se o usuário não tiver acesso ao Docker, execute os comandos Docker com `sudo`.

4. Extraia e inicie (use uma pasta vazia; não sobrescreva uma versão modificada):

```bash
sudo apt-get update
sudo apt-get install -y unzip
mkdir -p /home/ubuntu/gestao-ti-preview
unzip -n /home/ubuntu/gestao-ti-oracle-prototipo.zip -d /home/ubuntu/gestao-ti-preview
cd /home/ubuntu/gestao-ti-preview/gestao-ti
docker compose config
docker compose up -d --build
docker compose ps
curl -fsS http://127.0.0.1:8088/health
```

A resposta de saúde deve ser `ok`. A primeira construção precisa baixar a imagem Nginx. A configuração não fixa arquitetura, permitindo que Docker escolha a imagem compatível com a VPS.

5. Abra OUTRA janela do PowerShell e mantenha este túnel ativo:

```powershell
ssh -i "CAMINHO_DA_CHAVE" -N -L 8088:127.0.0.1:8088 ubuntu@IP_DA_VPS
```

Abra no navegador do seu computador: http://localhost:8088

A porta foi vinculada a 127.0.0.1 para revisar o protótipo pelo túnel SSH. Não é necessário abrir a porta 8088 na Oracle. Esta configuração segue a publicação de portas do Docker: https://docs.docker.com/engine/network/port-publishing/

## Operação

Na pasta do projeto:

```bash
docker compose logs --tail=100 web
docker compose stop
```

Para iniciar novamente:

```bash
docker compose up -d
```

Para reconstruir após editar `web/`:

```bash
docker compose up -d --build
```

## Teste local sem Docker

Com Python instalado, na pasta do projeto:

```bash
python3 -m http.server 8088 --bind 127.0.0.1 --directory web
```

No Windows, use `py -m http.server 8088 --bind 127.0.0.1 --directory web`. Abra http://localhost:8088. O endpoint `/health` pertence ao Nginx e não existe no servidor Python.

## Próxima etapa: sistema funcional

Implementar backend e PostgreSQL com migrations; autenticação e autorização no servidor; usuários e permissões; upload de documentos; e-mails de recuperação com token e validade; cálculo de SLA; integrações; backups; domínio e HTTPS. As telas atuais serão adaptadas a essa API. O protótipo não deve ser tratado como sistema de produção.

Esta entrega traduz a identidade visual em componentes reutilizáveis. Formulários e detalhes compartilham componentes; não é uma reprodução pixel a pixel de cada imagem aprovada. Agenda é uma lista de compromissos nesta etapa, sem grade de calendário.
