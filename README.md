# GESTÃO TI — GitHub Pages

Versão de demonstração preparada para publicação no GitHub Pages.
Todo o visual e JavaScript estão incorporados em `index.html`. Não precisa de pasta web, Docker, instalação de pacotes ou arquivos CSS/JS separados.

## Publicar pelo navegador

1. Extraia `gestao-ti-github.zip` no Windows.
2. Abra seu repositório `gestao-ti` no GitHub.
3. Clique em **Add file → Upload files**.
4. Envie os dois arquivos extraídos: **index.html** e **README.md**, diretamente na raiz do repositório, sem uma pasta envolvendo os arquivos. O novo README substitui as instruções anteriores da Oracle.
5. Clique em **Commit changes**, na branch **main**.
6. Abra **Settings → Pages**.
7. Em **Source**, escolha **Deploy from a branch**.
8. Selecione **main** e **/(root)**, depois **Save**.
9. Aguarde a publicação. O link aparecerá nessa mesma página em **Visit site**.

Não envie o ZIP fechado para publicar o site: envie os dois arquivos de dentro dele. Os arquivos Docker anteriores podem permanecer; não são usados pelo Pages. Se já houver app.js e style.css no repositório, não são necessários para este index.html, que é independente.

## Funcionalidades da prévia

Modo claro/escuro; painel; chamados; atividades; agenda em lista; equipamentos; clientes; unidades; manutenção; relatórios CSV e configurações demonstrativas. Navegação usa URLs com #, compatíveis com a pasta do projeto no GitHub Pages.

Dados armazenados somente no navegador. Login, recuperação e integrações são simulações; nenhum e-mail é enviado e nenhuma senha é gravada. Não há banco de dados compartilhado ou controle de acesso real. Use dados fictícios.

## Validação

Empacotamento e referências internas verificados. CSS e JavaScript incorporados sem alterações de comportamento. Sintaxe JavaScript verificada. A versão anterior passou por verificações de lógica em DOM simulado; não houve teste visual em navegador neste ambiente. Publicação e execução na sua conta GitHub ainda precisam ser verificadas após o envio.

Documentação oficial: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
