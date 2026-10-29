# Checklist da Etapa 0 — pré-registro

**Status geral:** rascunho pronto para revisão; execução e abertura de dados ainda não autorizadas.  
**Data:** 28/10/2026  
**Parâmetros fixados preservados:** todas as UFs; censo; comparadores 1T 2026, 2T 2022 e 2T 2018 somente se logs disponíveis; alfa 0,05; FDR BH q=0,05; efeito mínimo de 5 p.p. e 2 rajadas por seção; janelas 16h–17h e 17h–19h separadas; seed 20261025.

## 1. Itens cumpridos nesta redação

- [x] Pergunta de pesquisa formulada sem afirmar que exista fraude ou causalidade.
- [x] Escopo em todas as UFs registrado.
- [x] Amostra definida como censo.
- [x] Comparadores registrados sem presumir disponibilidade dos logs de 2022/2018.
- [x] Alfa, FDR, efeitos mínimos, janelas e seed preservados sem alteração.
- [x] Hipótese operacional da assinatura de pianista definida como hipótese, não como fato.
- [x] H0a/H1a para taxa de habilitação sem biometria incluídas.
- [x] H0b/H1b para rajadas temporais incluídas.
- [x] H0c/H1c para assinatura conjunta incluídas.
- [x] Limiar `dt` definido como percentil 1 dos intervalos entre habilitações biométricas de 09h–15h do 1T 2026, a ser congelado antes de abrir o 2T 2026.
- [x] Regras preliminares de rajada e de não sobreposição registradas.
- [x] Variáveis primárias, covariáveis e disponibilidade desconhecida distinguidas.
- [x] Regras de exclusão e sinalização documentadas sem imputação por suposição.
- [x] Plano de análise, FDR e reporte de estimativas incluídos.
- [x] Simetria entre candidatos estabelecida.
- [x] Controles de confundimento e explicações alternativas incluídos.
- [x] Robustez e separação entre confirmatório/exploratório incluídas.
- [x] Poder/precisão tratado como dependente da completude, apesar do censo.
- [x] Privacidade, pseudonimização, acesso e LGPD tratados.
- [x] Critérios de parada incluídos.
- [x] Fontes contextuais confirmadas atribuídas inline e referências ABNT simplificadas incluídas.
- [x] Limitações, inconsistências e fontes não confirmadas não foram convertidas em fatos.
- [x] Não foram criados scripts nem dados.

## 2. Itens pendentes de verificação técnica

- [ ] Baixar/inspecionar metadados dos conjuntos do TSE sem abrir ainda os desfechos do 2T 2026.
- [ ] Confirmar que há logs de habilitação com timestamps, seção e modalidade suficientes.
- [ ] Confirmar o dicionário/códigos que distinguem biometria reconhecida, ausência de biometria e biometria não reconhecida.
- [ ] Confirmar cobertura e comparabilidade do 1T 2026 para calibrar `dt`.
- [ ] Confirmar se os logs do 2T 2026 estão publicados, íntegros, completos e legalmente utilizáveis.
- [ ] Verificar disponibilidade dos logs do 2T 2022 e 2T 2018; se ausentes/incomparáveis, omitir esses comparadores.
- [ ] Validar hashes, duplicidades, fusos, timestamps simultâneos e status de totalização.
- [ ] Congelar método do percentil 1, regra para empates e regra final de rajadas antes de abrir o 2T 2026.
- [ ] Definir, após inspeção de metadados, a especificação estatística sem consultar resultados-alvo.
- [ ] Confirmar se candidato/cargo pode ser analisado com simetria e sem risco de reidentificação.
- [ ] Verificar licença dos logs do 2T 2026 antes de qualquer redistribuição ou derivação.
- [ ] Elaborar diagnóstico de precisão/poder usando a seed 20261025, sem ajustar parâmetros fixados.

## 3. Decisões humanas necessárias

- [ ] Aprovar explicitamente o protocolo antes de qualquer abertura do 2T 2026.
- [ ] Aprovar cargo(s), candidatos e nível de agregação/divulgação.
- [ ] Aprovar a interpretação de “habilitação sem biometria” quando a base agregar ausência de biometria e não reconhecimento.
- [ ] Aprovar a regra determinística final para timestamps empatados e rajadas contíguas.
- [ ] Aprovar a especificação estatística após a inspeção dos metadados.
- [ ] Aprovar bases, finalidade, controles de acesso, retenção e plano de descarte.
- [ ] Decidir se resultados exploratórios serão publicados separadamente dos confirmatórios.

## 4. Próximos passos autorizáveis somente após aprovação

1. Registrar a versão aprovada, data, hash do protocolo e responsável.
2. Inspecionar apenas catálogo, metadados, licenças e estrutura dos arquivos.
3. Registrar a disponibilidade real das bases e os motivos de qualquer exclusão.
4. Congelar regras técnicas e registrar `SEED = 20261025`.
5. Calibrar `dt` no 1T 2026, antes de abrir o 2T 2026.
6. Abrir e validar o 2T 2026 somente após o congelamento documentado.
7. Executar a análise confirmatória conforme o protocolo; rotular qualquer desvio como exploratório.
8. Produzir relatório com estimativas, intervalos, p-valores, q-valores, exclusões, limitações e auditoria de reprodutibilidade.

## 5. Blockers atuais

- Os arquivos ZIP/CSV e logs não foram baixados nem validados campo a campo nesta etapa.
- Não está confirmada a disponibilidade de registros completos de habilitação e timestamp para todas as UFs e janelas.
- Não está confirmada a comparabilidade dos logs de 1T 2026, 2T 2022 e 2T 2018.
- Não está confirmada a codificação necessária para separar ausência de biometria de biometria não reconhecida.
- A licença do conjunto de logs do 2T 2026 aparece como “Nenhuma Licença Fornecida” na pesquisa e requer verificação antes de uso derivado.
- Ainda falta aprovação humana explícita; sem ela, não se deve abrir dados-alvo nem executar a análise.

## GATE 0: aguardando aprovação humana explícita.
