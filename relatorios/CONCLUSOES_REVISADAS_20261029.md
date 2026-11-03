# Conclusoes cientificas revisadas — revisao de escopo integral
Data: 29/10/2026. Estado: **conclusoes metodologicas e documentais**, nao resultado de nova reanalise de microdados eleitorais. Referencias: auditoria transversal, protocolos/REGISTRO.md, PLANEJAMENTO.md e resultados placebos documentados.

## C1 — Hipotese do mesario pianista (escopo integral)
O desenho de janelas J0–J3 permite testar **somente intervalos selecionados**. Nao constitui investigacao abrangente de todo o periodo eleitoral e nao autoriza concluir ausencia de padroes ao longo do dia. O diagnostico de poder concentrado em J1 tem alcance restrito. E necessario pré-especificar e validar um detector com cobertura da jornada inteira, incluindo 08–09, 15–16 e periodos posteriores a 19h, antes de nova analise confirmatoria.

## C2 — Piloto TO documentado
O planejamento registra um piloto TO e declara que suas hipoteses nao foram sustentadas **no modelo aplicado**. Esta revisao nao reabriu as saidas do 2T2026; a afirmacao deve permanecer atribuida ao relatorio do piloto e restrita ao seu escopo, data e configuracao. Um resultado nulo nas janelas antigas nao refuta uma hipotese ainda nao examinada sobre o dia completo, nem a possibilidade generica de comprometimento interno.

## C3 — Modo de habilitacao nao determinado
A conversao generalizada de `DESC` para `NB_SEM` em 2026 depende de cobertura documental empirica e verificacao de que o mapeamento corresponde ao evento real de todas as amostras analisadas. Ate que isso seja demonstrado, estimativas baseadas nessa conversao sao **condicionais**; taxas de desconhecidos e cenarios de sensibilidade devem ser relatados.

## C4 — Placebo Palmas 2024
Conforme relatorio ja existente (nao reproduzido nesta revisao), 629 secoes foram avaliadas; 112 tiveram ultimo voto interno depois de 17h e nenhuma depois de 17h10. O contraste local do vencedor foi de +0,40 p.p. (IC95% -0,44 a +1,24 p.p.), sem evidencia de diferenca para aquela especificacao. Nao extrapolar isso como comprovacao de integridade, ausencia de fraude ou padrao geral nacional; Palmas nao calibra corte >19h.

## C5 — Coortes administrativas versus ultimo voto
Quantidades nacionais de seções encerradas administrativamente depois de 17h10/19h NAO sao quantidades verificadas de secoes cujo ultimo voto ocorreu depois desses horarios. Qualquer estimativa de materialidade que aplique votos medios a tais contagens e **ilustrativa, nao inferencia sobre a populacao-alvo**.

## C6 — Materialidade e potencia
Aritmetica da margem e detectabilidade estatistica sao conceitos independentes. A ocorrencia de um efeito material nao garante que a comparacao dentro de local o detecte. Testes de poder devem considerar estrutura de selecao e mecanismos alternativos, sem afirmar que efeitos grandes necessariamente apareceriam como anomalias.

## C7 — Integridade documental
Concordancia entre log, RDV e BU prova coerencia entre registros sob regras de validacao adequadas, mas nao basta para demonstrar, isoladamente, a correspondencia com a intencao de cada eleitor. Inversamente, essa dependencia logica nao demonstra adulteracao ou fraude.

## C8 — Independencia dos tempos
Horario de recepcao central do BU e limite temporal de procedimento anterior, condicionado a integridade dos registros e cadeia de sequencia, nao e medida direta do horario do ultimo voto. Evidencia externa deve observar o evento correto. Na ausencia de referencia externa suficiente, resultados sao condicionais ao relogio da urna ou nao identificaveis.

## C9 — Codigo reconstruido
A reconstrucao C++ do simulador VOTA serve para perguntas tecnicas, analise de fluxo e mapeamento de dependencias. Nao e prova de identidade com o binario homologado, nem demonstracao de falha real.

## C10 — Preservacao historica de 2026
Metadata HTTP/CKAN atualizado em 26/10 nao prova alteracao de conteudo. Para comparar versoes sao necessarias copias autenticas, hashes, datas de captura independentes, identidade de recurso e comparacao dos bytes/estrutura. Pacote de 5/10 preserva derivados, nao originals TSE.

## C11 — Estado cientifico geral
**Nenhuma nova evidencia de fraude ou de ausencia universal de fraude foi produzida por esta revisao.** O resultado defensavel e que ha lacunas documentais, de escopo temporal e de identificabilidade que precisam ser corrigidas antes de interpretacoes gerais. Novas hipoteses surgidas apos exposicao a amostras-alvo sao exploratorias no material ja exposto.

## C12 — Status do site
A pasta site desapareceu da branch do PR #3 observada em 29/10, embora estivesse em um commit anterior; a restauracao nesse PR depende de revisao do diff, CI e garantia de que nao ha trabalho concorrente perdido. A existencia do site original publicado e distinta da existencia do codigo reconstituido no Git.

## Conclusao institucional do projeto
O Pianista deve concentrar-se na verificabilidade independente, com testes completos de cobertura temporal, relogios, documentos e estados de hardware/software. Se nao houver evidencia capaz de distinguir duas hipoteses, registrar **NAO IDENTIFICAVEL**. Nenhuma analise estatistica isolada demonstra que fraude ocorreu, e nenhum resultado nulo autoriza a conclusao de integridade absoluta do sistema.
