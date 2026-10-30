# Estudo 05 — matriz de verificação e incerteza

| Domínio | Evidências desejadas | Teste defensivo | Explicação alternativa |
|---|---|---|---|
| Relógio e configuração do encerramento | Documentação oficial e perícia autorizada da versão usada | Coerência das transições com horários autorizados | Fuso, fila, decisão excepcional |
| Habilitação e confirmação | Log público e manual de eventos | Sequência compatível com estado e modelo de urna | Contingência, falha de biometria ou omissão de linha |
| Fechamento e impressão | Log, ata e BU | Distinção entre último voto e elaboração do boletim | Impressão e armazenamento ocorrem mais tarde |
| Relatórios e BU | BU e documentação; log quando observável | Reconciliação dos agregados declarados | Logs podem não registrar cada ação com a granularidade esperada |
| RDV e assinatura | RDV, hashes e arquivos assinados públicos | Verificação de integridade e recontagem independente | Fontes podem compartilhar o mesmo domínio de controle |
| Transmissão e totalização | Documentos e sistemas de divulgação públicos | Separar horário de recepção do horário de voto | Logística e filas de transmissão |

## Critérios mínimos

- Em caso de voto após 17h, examinar **fila** e **extensão excepcional** antes de marcar anomalia.
- BU emitido após 19h não é, isoladamente, irregular: o encerramento tem procedimentos posteriores.
- Conferir se um suposto evento de log existe na versão e no modelo sob exame; não inventar campos.
- Resultado sintético nunca é teste da urna real.
- Só afirmar vulnerabilidade demonstrada após reprodução controlada e revisão adequada da **mesma versão** do sistema.

Fontes: TSE (Resolução nº 23.759/2026, art. 29); TRE-DF (27/10/2026); urna-vota-decompiled (código reconstruído do simulador, não binário lacrado); DataUrnas-BR (análise independente de artefatos públicos, não código-fonte oficial).
