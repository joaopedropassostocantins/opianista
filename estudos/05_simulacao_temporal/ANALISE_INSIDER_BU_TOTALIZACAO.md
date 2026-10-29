# Estudo 05 — prioridade máxima: insider, BU e totalização

**29/10/2026 — investigação exploratória e modelagem de ameaças.** Não modifica pré-registros congelados dos Estudos 01 e 03. Não constitui conclusão de fraude ou demonstração de vulnerabilidade.

## Esclarecimento obrigatório de escopo

A amostra prioritária compreende seções com encerramento registrado tardiamente. **O resultado sob análise é a TOTALIDADE dos votos de cada seção selecionada, ainda que tenham sido lançados antes de 17h.** Eventos registrados após 17h, usados anteriormente no simulador, são apenas material explicativo sobre a sequência de procedimentos. O estudo deve validar a classificação das seções diante da hipótese de relógio/log não confiável; não presumir que houve adulteração dos horários. Especificação: [COORTES_HORARIO_NAO_CONFIAVEL.md](COORTES_HORARIO_NAO_CONFIAVEL.md).

## Pergunta principal

A extensão excepcional de votação até 19h nas seções ainda abertas às 17h permitiria, ou coincidiria com, uma condição de software em que:
1. a apuração fosse comprometida **antes da emissão e assinatura** do BU;
2. dados da **totalização central** divergissem dos BUs efetivamente emitidos; ou
3. registros de auditoria compartilhassem a mesma origem e fossem coerentes, mesmo sem prova independente da ocorrência material dos votos?

A possibilidade lógica desses eventos não significa que ocorreram ou que tenham sido facilitados por 19h. A extensão não prova enfraquecimento de controles.

## Separação por domínio e controles

| Domínio | Fonte | O que verificar | Limite |
| --- | --- | --- | --- |
| Origem na urna | RDV, estado, log | Coerência interna, sequência, correspondência por cargo | Registros têm potencial dependência comum |
| Emissão | BU, impressão, arquivo assinado | Valor fixado ao encerrar seção | Autenticidade não equivale automaticamente a intenção do eleitor |
| Custódia independente | BU impresso ou QR registrado por terceiro | Igualdade BU local × BU divulgado | Requer autenticidade, preservação, mapeamento correto de seção |
| Recepção e centralização | BU recebido, totalização | Soma e distribuição dos votos por seção | Validar agregações, contingência, substituição, retificações |
| Observação externa | Teste de integridade autorizado, cópias externas | Avaliação da correção sob condições conhecidas | Não reconstitui cada voto secreto real |

O TSE descreve que a **apuração ocorre na urna**, enquanto o **sistema central totaliza** resultados provenientes das seções. Em 25/10/2026, o TSE informou a suspensão temporária de recepção e totalização com retomada após 19h; isso não implica interrupção dos mecanismos de segurança de urnas já abertas ou fechadas.

## Prioridades de revisão — ordem vinculante

1. **Habilitação:** quais pré-condições autorizam nova sessão? Referência reconstruída: \`vota/operador/leidentidade/cpedeidentidade.cpp\`.
2. **Terminal do mesário:** quais eventos exigem intervenção, estado e controle temporal? Referência reconstruída: \`vota/operador/comum/cinformacaothreadoperador.cpp\`.
3. **Contabilização:** tratamento de nominais, brancos, nulos, suspensões, persistência e RDV. Referência reconstruída: \`comum/dados/crdvvota.cpp\`.
4. **Geração do BU:** estruturas de origem e transição ao relatório, impressão e arquivos. Referência reconstruída: \`vota/eleitor/fimvotacao/cgerabu.cpp\`.
5. **Logs/persistência:** catálogo dos eventos realmente emitidos e operações invisíveis ao log público. Referência reconstruída: \`comum/log/ieventoslog.u35.cpp\`.

Todos os caminhos são relativos a \`src/uenux2/src/app/\` do projeto externo https://github.com/igoroalonge/urna-vota-decompiled . Seu WASM é de **desenvolvimento**, reconstruído, não o binário lacrado. A thread do operador não funciona normalmente no simulador web. **Os sistemas centrais de recepção e totalização não pertencem ao VOTA**: exigem exame próprio.

## Hipóteses defensivas a testar

**H0:** BUs locais preservados coincidem com os arquivos divulgados; soma independente por seção reproduz os totais centrais; regras de encerramento são respeitadas.

**H1 — origem comprometida, antes do BU:** um registro incorreto produzido a montante poderia resultar em RDV, BU e log coerentes entre si. Testes documentais internos podem detectar inconsistências, mas não garantem observação independente do voto real. Precisaria de ambiente de teste autorizado, validação da versão e controle externo.

**H2 — alteração na totalização:** dados originais divulgados pela seção diferem dos totais atribuídos à seção e aos agregados do sistema central. Evidência potencial: somatório dos BUs originais preservados por terceiros, verificação de identidade seção–arquivo e conferência de relatórios oficiais.

**H3 — fronteira 17h/19h:** sinais de horário anormal podem refletir fila, autorização excepcional, diferenças de fuso ou processamento posterior; identificar precisamente **hora do último voto**, **encerramento**, **geração do BU**, **transmissão**, **recepção** e **totalização**.

**H4 — não identificabilidade:** quando fontes públicas não permitem distinguir hipóteses, registrar conclusão inconclusiva, nunca suprir lacuna com suposição.

## Experimento de consistência no site

Novo painel contém quatro **fixtures de laboratório**:
- Controle: registro, BU e totalização coincidem.
- Hipótese origem comprometida: documentos simulados concordam, mas uma referência externa **inventada** diverge.
- Hipótese totalizador divergente: BU publicado difere da contagem atribuída à seção.
- Recebimento tardio: BU emitido antes de 19h, recebido após 19h e sem alteração de valor.

Todos os números são sintéticos. A referência externa é **apenas um controle pedagógico**, e não existe fonte que revele a intenção secreta individual de todos os eleitores numa eleição real. O painel não executa VOTA, não altera arquivos oficiais, não testa assinaturas reais e não ensina a contornar controles.

## Critérios para passar à análise empírica

Obter e registrar origens, hashes, modelo e versão dos BUs, RDVs, logs e assinaturas; documentar tratamento de seções agregadas, contingências e totalizações; confrontar cópias independentes; testar controles negativos. Respeitar pré-registros e limitação de dados-alvo já examinados. Afirmar vulnerabilidade somente mediante reprodução autorizada na **mesma versão** e revisão independente.

## Referências

- https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/esclarecimento-sobre-prorrogacao-da-votacao
- https://www.tse.jus.br/comunicacao/noticias/2026/Outubro/saiba-como-foi-a-totalizacao-dos-votos-no-1o-turno-das-eleicoes-2026
- https://www.tse.jus.br/eleicoes/urna-eletronica/seguranca-da-urna/auditoria-da-totalizacao
- https://github.com/igoroalonge/urna-vota-decompiled
