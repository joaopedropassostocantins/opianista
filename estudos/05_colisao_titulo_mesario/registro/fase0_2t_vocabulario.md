# FASE 0 - VOCABULARIO DO LOG, 2o TURNO DE 2026 (25/10/2026)

Amostra: 30 secoes de TO, SP, BA, RS, AM (semente 20261025); 30 arquivos de log. Titulos mascarados nos exemplos.

Formato da linha (separador TAB): campo 1 = data e hora (dd/mm/aaaa hh:mm:ss); campo 2 = nivel (INFO, ALERTA, ERRO); campo 3 = identificador da urna; campo 4 = aplicacao (VOTA, GAP, SCUE, ATUE, LOGD); campo 5 = mensagem; campo 6 = hash da linha. O titulo, quando presente, e a sequencia de 12 digitos dentro do campo 5.

| Evento | Aplicacao | No dia do 2T? | Ocorrencias | Arquivo:linha | Exemplo |
|---|---|---|---|---|---|
| biometria_coincide | VOTA | nao | 49 | o03221to9521400180010-log.jez:558 | `04/10/2026 08:01:57	INFO	02029762	VOTA	Realizada a conferência da biometria do mesário	2CD174EBCDFE5398` |
| biometria_coincide | VOTA | sim | 54 | o03221to9521400180010-log.jez:6082 | `25/10/2026 07:28:10	INFO	02029762	VOTA	Realizada a conferência da biometria do mesário	B3947B34D92EB226` |
| biometria_eleitor_nao_e_do_mesario | VOTA | nao | 835 | o03221to9521400180010-log.jez:734 | `04/10/2026 08:31:06	INFO	02029762	VOTA	Biometria coletada não é do mesário XX637109XXXX (213578)	C986F60269424DDE` |
| biometria_eleitor_nao_e_do_mesario | VOTA | sim | 1043 | o03221to9521400180010-log.jez:6132 | `25/10/2026 08:04:37	INFO	02029762	VOTA	Biometria coletada não é do mesário XX637109XXXX (912543)	D62F126FFD6AB3FB` |
| biometria_nao_coincide | VOTA | nao | 19 | o03221sp6961200530279-log.jez:592 | `04/10/2026 07:31:49	INFO	01760539	VOTA	Digital capturada não corresponde a digital do eleitor: Polegar Direito [score 6], Polegar Esquerdo [score 10], Indicador` |
| biometria_nao_coincide | VOTA | sim | 16 | o03221to9521400180010-log.jez:6067 | `25/10/2026 07:23:22	INFO	02029762	VOTA	Digital capturada não corresponde a digital do eleitor: Polegar Direito [score 4], Polegar Esquerdo [score 4], Indicador ` |
| bloqueio_ja_registrado | VOTA | nao | 1 | o03221ba3803200590053-log.jez:545 | `04/10/2026 07:34:44	INFO	02052606	VOTA	Mesário XX376549XXXX já registrado	79B8C267F89C85F4` |
| bloqueio_ja_registrado | VOTA | sim | 8 | o03221to9241000010098-log.jez:9231 | `25/10/2026 13:48:36	INFO	02153097	VOTA	Mesário XX179070XXXX já registrado	2C9C649DAB5F43FA` |
| contingencia_ou_troca | ATUE | nao | 63 | o03221to9521400180010-log.jez:172 | `23/09/2026 15:22:55	INFO	02029762	ATUE	Identificação do Modelo de Urna: UE2020	77C832749498ADB7` |
| contingencia_ou_troca | GAP | nao | 482 | o03221to9521400180010-log.jez:96 | `23/09/2026 15:21:31	INFO	02029762	GAP	Identificação do Modelo de Urna: UE2020	49710AD2E783D9A2` |
| contingencia_ou_troca | GAP | sim | 64 | o03221to9521400180010-log.jez:5952 | `25/10/2026 06:53:11	INFO	02029762	GAP	Identificação do Modelo de Urna: UE2020	6D2E504BA29A0F54` |
| contingencia_ou_troca | SCUE | nao | 30 | o03221to9521400180010-log.jez:50 | `23/09/2026 15:18:26	INFO	02029762	SCUE	Identificação do Modelo de Urna: UE2020	23AB5D29F7566AAC` |
| digitacao_titulo_mesario | VOTA | nao | 239 | o03221to9521400180010-log.jez:547 | `04/10/2026 08:00:29	INFO	02029762	VOTA	Pedido de leitura da biometria do mesário XX506960XXXX	EDE057E8AC0DDE95` |
| digitacao_titulo_mesario | VOTA | sim | 244 | o03221to9521400180010-log.jez:6055 | `25/10/2026 07:20:49	INFO	02029762	VOTA	Pedido de leitura da biometria do mesário XX506960XXXX	3AAD9C3D67E7D01E` |
| e_eleitor_da_secao | VOTA | nao | 69 | o03221to9521400180010-log.jez:559 | `04/10/2026 08:01:57	INFO	02029762	VOTA	Mesário XX736866XXXX é eleitor da seção	6F3A980521CA7FE9` |
| e_eleitor_da_secao | VOTA | sim | 72 | o03221to9521400180010-log.jez:6068 | `25/10/2026 07:23:22	INFO	02029762	VOTA	Mesário XX736866XXXX é eleitor da seção	29515657D2FAED8D` |
| encerramento_titulo | VOTA | nao | 30 | o03221to9521400180010-log.jez:5447 | `04/10/2026 17:43:11	INFO	02029762	VOTA	Título digitado para encerramento: XX506960XXXX	925F53D56490CF5D` |
| encerramento_titulo | VOTA | sim | 30 | o03221to9521400180010-log.jez:9491 | `25/10/2026 17:02:40	INFO	02029762	VOTA	Título digitado para encerramento: XX506960XXXX	45465E99285030E7` |
| fase_ue | GAP | nao | 241 | o03221to9521400180010-log.jez:104 | `23/09/2026 15:21:42	INFO	02029762	GAP	Fase da UE: Oficial	B72DABFB06DF3959` |
| fase_ue | GAP | sim | 32 | o03221to9521400180010-log.jez:5959 | `25/10/2026 06:53:22	INFO	02029762	GAP	Fase da UE: Oficial	1215426E2957895D` |
| habilitacao_eleitor | VOTA | nao | 6967 | o03221to9521400180010-log.jez:582 | `04/10/2026 08:09:09	INFO	02029762	VOTA	Eleitor foi habilitado	DBE7091C50577205` |
| habilitacao_eleitor | VOTA | sim | 7077 | o03221to9521400180010-log.jez:6108 | `25/10/2026 08:02:03	INFO	02029762	VOTA	Eleitor foi habilitado	42CEC0504A998D66` |
| identificador_eleitor | VOTA | nao | 7325 | o03221to9521400180010-log.jez:577 | `04/10/2026 08:08:15	INFO	02029762	VOTA	Identificador digitado pelo mesário foi: (CPF)	A4DB5E1EE3811DF6` |
| identificador_eleitor | VOTA | sim | 7333 | o03221to9521400180010-log.jez:6103 | `25/10/2026 08:01:47	INFO	02029762	VOTA	Identificador digitado pelo mesário foi: (Título de eleitor)	606803685767CC0D` |
| inicio_registro_mesario | VOTA | nao | 129 | o03221to9521400180010-log.jez:528 | `04/10/2026 07:29:51	INFO	02029762	VOTA	Operador indagado se ocorrerá registro de mesários	8D3CB778E5AE8C69` |
| inicio_registro_mesario | VOTA | sim | 131 | o03221to9521400180010-log.jez:6052 | `25/10/2026 07:07:20	INFO	02029762	VOTA	Operador indagado se ocorrerá registro de mesários	1BA6C1716C9A75A8` |
| mesario_habilitou_eleitor | VOTA | nao | 291 | o03221to9521400180010-log.jez:741 | `04/10/2026 08:31:10	INFO	02029762	VOTA	Mesário XX506960XXXX habilitou o eleitor	ED86E9A6A68D8330` |
| mesario_habilitou_eleitor | VOTA | sim | 329 | o03221to9521400180010-log.jez:6139 | `25/10/2026 08:04:42	INFO	02029762	VOTA	Mesário XX506960XXXX habilitou o eleitor	259092A1F8C56474` |
| nao_e_eleitor_da_secao | VOTA | nao | 146 | o03221to9521400180010-log.jez:548 | `04/10/2026 08:00:37	INFO	02029762	VOTA	Mesário XX506960XXXX não é eleitor da seção	CD014842BE785C0D` |
| nao_e_eleitor_da_secao | VOTA | sim | 150 | o03221to9521400180010-log.jez:6056 | `25/10/2026 07:21:04	INFO	02029762	VOTA	Mesário XX506960XXXX não é eleitor da seção	B64D27DAEE452A8C` |
| partida_do_sistema | LOGD | nao | 426 | o03221to9521400180010-log.jez:1 | `23/09/2026 15:17:12	INFO	02029762	LOGD	Início das operações do logd	C4D0D1AD83027D6E` |
| partida_do_sistema | LOGD | sim | 64 | o03221to9521400180010-log.jez:5947 | `25/10/2026 06:52:45	INFO	02029762	LOGD	Início das operações do logd	AED453FB2BC712C2` |
| registro_presenca_mesario | VOTA | nao | 215 | o03221to9521400180010-log.jez:549 | `04/10/2026 08:00:38	INFO	02029762	VOTA	Mesário XX506960XXXX registrado	10709B1D0B8D1556` |
| registro_presenca_mesario | VOTA | sim | 222 | o03221to9521400180010-log.jez:6057 | `25/10/2026 07:21:04	INFO	02029762	VOTA	Mesário XX506960XXXX registrado	7108CDA8285938F8` |
| titulo_invalido_eleitor | VOTA | nao | 327 | o03221to9521400180010-log.jez:574 | `04/10/2026 08:07:19	ALERTA	02029762	VOTA	Identificador do eleitor digitado inválido	BA9390798D4B29EB` |
| titulo_invalido_eleitor | VOTA | sim | 313 | o03221to9521400180010-log.jez:6100 | `25/10/2026 08:01:25	ALERTA	02029762	VOTA	Identificador do eleitor digitado inválido	56A9C3E2411C11BD` |
| titulo_invalido_mesario | VOTA | nao | 35 | o03221to9521400180010-log.jez:531 | `04/10/2026 07:32:33	ALERTA	02029762	VOTA	Digitado título inválido para o registro de mesário	C9164E48D1E46FF4` |
| titulo_invalido_mesario | VOTA | sim | 36 | o03221to9241000010098-log.jez:6546 | `25/10/2026 07:42:31	ALERTA	02153097	VOTA	Digitado título inválido para o registro de mesário	599F96915A09BDD4` |
| urna_pronta | VOTA | nao | 34 | o03221to9521400180010-log.jez:542 | `04/10/2026 08:00:01	INFO	02029762	VOTA	Urna pronta para receber votos	CE6FE3878446A7E5` |
| urna_pronta | VOTA | sim | 32 | o03221to9521400180010-log.jez:6097 | `25/10/2026 08:00:02	INFO	02029762	VOTA	Urna pronta para receber votos	41FC97F8EA7C5F44` |
| voto_computado | VOTA | nao | 6962 | o03221to9521400180010-log.jez:612 | `04/10/2026 08:12:34	INFO	02029762	VOTA	O voto do eleitor foi computado	936F419C057D5ACB` |
| voto_computado | VOTA | sim | 7076 | o03221to9521400180010-log.jez:6111 | `25/10/2026 08:02:16	INFO	02029762	VOTA	O voto do eleitor foi computado	48F7EA10D662B9B5` |
| zeresima | VOTA | nao | 30 | o03221to9521400180010-log.jez:522 | `04/10/2026 07:29:13	INFO	02029762	VOTA	Imprimindo relatório [ZERÉSIMA] via nº [1]	8036FE00DAD78486` |
| zeresima | VOTA | sim | 30 | o03221to9521400180010-log.jez:6046 | `25/10/2026 07:07:03	INFO	02029762	VOTA	Imprimindo relatório [ZERÉSIMA] via nº [1]	6E3F629633A12550` |

Datas presentes nos logs do 2T (linhas por data):

- 14/09/2026: 62
- 19/09/2026: 377
- 21/09/2026: 341
- 22/09/2026: 1173
- 23/09/2026: 1809
- 24/09/2026: 1744
- 25/09/2026: 1319
- 26/09/2026: 1064
- 27/09/2026: 447
- 28/09/2026: 1122
- 29/09/2026: 1068
- 30/09/2026: 552
- 01/10/2026: 863
- 02/10/2026: 986
- 03/10/2026: 1458
- 04/10/2026: 156416
- 05/10/2026: 73
- 14/10/2026: 983
- 15/10/2026: 806
- 16/10/2026: 2048
- 18/10/2026: 547
- 19/10/2026: 2280
- 20/10/2026: 749
- 21/10/2026: 1380
- 22/10/2026: 937
- 23/10/2026: 1277
- 24/10/2026: 1520
- 25/10/2026: 105140

Partidas do sistema no dia do 2T, por arquivo (1 = so a partida normal da manha):

- 1 partida(s): 28 arquivo(s)
- 2 partida(s): 2 arquivo(s)
