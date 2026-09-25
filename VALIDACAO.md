# Validação da entrega

- `node --check web/app.js`: passou.
- Renderização das 16 rotas principais em ambiente JavaScript com DOM simulado: passou.
- Criação e edição de registros, serialização de persistência, escape de HTML e vínculo de manutenção com equipamento: passaram.
- Arquivos servidos localmente por HTTP: resposta 200.
- Revisão automatizada em navegador e inspeção visual: não realizadas. O download do Chromium falhou neste ambiente. O teste de DOM simulado não substitui teste no navegador.
- Build Docker e execução na VPS: não realizados; exigem o ambiente de destino.

Ao abrir na VPS, conferir: entrada na demonstração, criação/edição/conclusão de chamado, recarregamento da página, modo escuro, navegação móvel, exportação CSV e vínculo da manutenção. Usar dados fictícios.
