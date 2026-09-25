# Implantação da versão oficial na Oracle

Esta etapa requer acesso SSH funcional à VPS, Docker/Compose, um subdomínio apontado para o IP e HTTPS válido. O Pages permanece como demonstração. Não execute os comandos dentro do projeto Elo Afiliados.

## 1. Pasta isolada

Na VPS, usando seu usuário de operação:

```bash
git clone --branch oficial-v1 https://github.com/clauberO/gestao-ti.git gestao-ti-oficial
cd gestao-ti-oficial
cp .env.example .env
chmod 600 .env
```

Edite `.env` no servidor. Defina domínio real em `ALLOWED_HOSTS` (sem protocolo) e URL HTTPS em `CSRF_TRUSTED_ORIGINS`. Gere valores independentes para `SECRET_KEY` e `POSTGRES_PASSWORD`, por exemplo com `openssl rand -hex 32`. Nunca envie esses valores por chat ou commit. O arquivo `.env` é carregado pelo Compose; o Django diretamente utiliza variáveis de ambiente, sem carregador automático de .env.

## 2. Construir e migrar

Confira se a porta 8090 está livre antes de prosseguir (`ss -ltn 'sport = :8090'`). O banco não publica porta para a internet. O volume chama-se `gestao-ti-oficial_postgres_data`.

```bash
docker compose -f compose.oficial.yaml build
docker compose -f compose.oficial.yaml up -d db
docker compose -f compose.oficial.yaml run --rm app python manage.py migrate
docker compose -f compose.oficial.yaml run --rm app python manage.py createsuperuser
docker compose -f compose.oficial.yaml up -d app
```

O `createsuperuser` solicita usuário, e-mail e senha de forma interativa. A senha não aparece durante a digitação. Use senha única de pelo menos 12 caracteres e não ignore alertas do validador. Não há senha padrão.

## 3. Proxy e HTTPS

`docs/nginx.oficial.conf.example` é apenas um modelo. Substitua o subdomínio e os caminhos do certificado pelos valores reais e instale em um arquivo próprio do Nginx. Não sobrescreva a configuração de outros sistemas. Valide com `sudo nginx -t` antes de recarregar.

A aplicação escuta somente em `127.0.0.1:8090`; Nginx no host encaminha para essa porta. Não exponha 8090/5432 na Oracle. As portas públicas do site são 80 e 443. Se usar proxy em container, adapte a rede de forma explícita: 127.0.0.1 dentro do container não aponta para o host.

`TRUST_PROXY=1` só é correto com o proxy controlado que sobrescreve X-Forwarded-Proto e X-Real-IP. Produção força HTTPS, cookies Secure e HSTS para o host do sistema; subdomínios/preload não são habilitados automaticamente.

## 4. Homologação

```bash
docker compose -f compose.oficial.yaml exec app python manage.py check --deploy
docker compose -f compose.oficial.yaml ps
docker compose -f compose.oficial.yaml logs --tail=80 app
```

Avisos sobre HSTS de subdomínios/preload devem ser avaliados com a política de domínio; não habilitar preload sem entender seus efeitos. Abra a URL HTTPS e confirme:

- Login inválido recusado; login correto entra; logout encerra acesso.
- Criar gestor e técnico em Equipe e permissões; atribuir um chamado.
- Técnico vê apenas seus chamados e não acessa outro por URL.
- Criar cliente/unidade/equipamento e atividade; recarregar em outro navegador autenticado.
- Alterar senha, tema, testar celular, exportar CSV e comentários.

## 5. Backup e recuperação

Antes de cada atualização, faça um backup. O backup contém dados da operação e deve ficar fora do repositório, com acesso restrito. Exemplo no host:

```bash
mkdir -p backups
chmod 700 backups
umask 077
docker compose -f compose.oficial.yaml exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "backups/gestao-ti-$(date +%Y%m%d-%H%M%S).dump"
```

Agende diariamente e mantenha cópia criptografada fora da VPS. Antes de aceitar dados reais, restaure um backup em um banco de homologação vazio e confira os registros com `pg_restore`. Não execute restauração sobre produção sem um plano específico de parada/recuperação. Um volume Docker sozinho não é backup.

Periodicamente rode:

```bash
docker compose -f compose.oficial.yaml exec app python manage.py clearsessions
docker compose -f compose.oficial.yaml exec app python manage.py cleanup_security
```

Para redefinir a senha de um usuário sem e-mail, o operador autorizado executa `python manage.py changepassword USUARIO` dentro do container. O comando solicita a nova senha interativamente. Não há função de recuperação por e-mail ainda.

## Atualização

Faça backup, pare a aplicação (mantenha o banco), atualize o código da branch revisada, reconstrua a imagem, aplique migrations com `run --rm app python manage.py migrate` e inicie novamente. Reverter código após migrations pode ser incompatível: planeje a reversão do esquema e o uso do backup antes da atualização. Nunca use `docker compose down -v` para atualizar: isso remove o banco.
