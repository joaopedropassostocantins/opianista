# PROPOSTA DE EMENDA — Estudo 03: jornada integral do mesario pianista
Data de elaboracao: 29/10/2026. Estado: **PROPOSTA NAO APROVADA**.
Versao anterior: protocolo v1.1 (GATE 0, ja aprovado), com Emenda 02 de calibracao restrita a TO.
Este texto **nao reescreve, nao substitui e nao torna retroativamente confirmatoria** a analise original.
A presente proposta incorpora a determinacao do proponente de investigar **o dia inteiro**, nao apenas o intervalo 17h–19h.

## 1. Correcao do objeto
A hipotese do mesario pianista diz respeito a eventuais habilitacoes ou sequencias de registros sem base operacional no **periodo completo de funcionamento da secao**, incluindo abertura, periodo ordinario, filas e eventuais prorrogacoes. O evento temporal de elegibilidade e **cada habilitacao documentada**, nao um recorte unico 17h–19h.

## 2. Amostragem temporal
A unidade primaria e a **secao-dia completo**. Para cada secao, delimitar o intervalo entre a abertura real documentada e o ultimo evento de votacao/habilitacao documentado, sem teto artificial de 17h, 19h ou 20h. Caso o log normalize apenas segundos desde meia-noite sem data, qualquer evento que atravesse a meia-noite exige resolver a data original; caso contrario, classificar indeterminado. Os registros anteriores a abertura ou posteriores ao encerramento nao sao apagados: auditar separadamente a inconsistencia.

Janelas horarias por hora civil servem como **diagnostico secundario**, inclusive 08h–09h, 15h–16h e depois das 19h; uma janela nao pode ser excluida sem justificativa previa. Os cortes 17h/17h10/17h49/19h sao apenas covariaveis ou estratos predefinidos, nunca filtros do universo analisado.

## 3. Variaveis por secao, dia e faixa horaria
Registrar N_H (habilitacoes), N_BIO, N_NB_confirmadas, N_DESC (modo indeterminado), K (sequencias de tres ou mais habilitacoes NB), fracao NB entre eventos **com modo classificavel**, percentagem de modo indeterminado, quantidade de eventos no mesmo segundo, lacunas e duracao observada. Reconciliar N_H com outros eventos e BU somente quando o dicionario de logs comprovar a identidade das contagens. **Nao converter automaticamente DESC em NB_SEM**: recalibrar regras documentais, apresentar limites inferior e superior de NB sob classificacoes alternativas e taxa de ausentes.

## 4. Detector de sequencias de dia inteiro
Calibrar dt* **com base historica permitida e sem acesso a dados-alvo ainda bloqueados**, considerando intervalos ao longo da jornada completa. Comparar distribuições por horario e zona para evitar que duracao, carga da urna e fluxo por hora invalidem a referencia. Uma sequencia pode atravessar uma fronteira horaria sem ser interrompida pelo parser; deve ser contada **uma vez**. Hora registrada em segundos nao identifica, isoladamente, tempo de operacao fisica.

## 5. Comparadores e inferencia
Principal periodo historico para cadencia e comportamento do final da votacao: **segundo turno municipal**; 2022 pode funcionar como placebo tecnico ja previsto, mas nao como paradigma principal da cadencia. Ajustar heterogeneidade de secao, tamanho, fluxo de eleitores, fila, biometria, modelo de urna e relogio. Antes de testes confirmatorios, fixar as estatisticas e os limiares de sinalizacao, potencia, conjunto de hipoteses, multiplicidade e variaveis faltantes.

As analises por janelas J0–J3 continuam historicas e **nao equivalem ao dia integral**. A proposta integral requer novos testes de poder com eventos sinteticos distribuidos em horas distintas, rajadas curtas e longas, taxas de faltantes, deriva de relogio e controle negativo.

## 6. Estado e governanca
Aprovacao registrada do item 1.6 para TO/Emenda 02 e piloto ja realizado no escopo anterior **nao autorizam** qualificar a nova hipotese integral como pre-registrada prospectivamente para TO. O TO possui exposicao previa e deve ser tratado como exploratorio para as novas hipoteses. Para outras UFs, verificar individualmente o gate e a ausencia de exposicao antes de qualquer processamento. Nenhum 2T2026 sera aberto pelo modulo novo ate aprovacao formal especifica da nova emenda; o script integral bloqueia esse periodo.

Nao reprocessar os dados ja expostos com novos limiares e anunciar um p-valor como confirmatorio. Publicar resultados positivos, nulos e nao identificaveis com o mesmo rigor.

## 7. Aceitacao proposta
- Universo coberto sem lacunas programadas (8h–9h, 15h–16h, >19h).
- Dados de diferentes dias e turnos nunca sao misturados.
- Auditoria de data, fuso, abertura e encerramento antes de qualquer conclusao cronologica.
- Modo DESC mantido como desconhecido, salvo verificacao empirica local formalizada.
- Sensibilidade e falsos positivos simulados para **todas** as faixas.
- Pareamento e inferencia apenas se dados e potencia forem adequados.
- Gate aprovado por humano antes de uso confirmatorio em novas UFs.

**Nota:** o novo arquivo `dia_integral.py` implementa diagnostico **descritivo/exploratorio**, nao os testes confirmatorios desta proposta. `pianista.py` original e os protocolos congelados permanecem inalterados para preservar o historico.
