# Emenda 02 ao protocolo v1.1 do Estudo 03 - Calibracao e execucao piloto em TO

Data: 2026-10-29
Protocolo de referencia: `estudos/03_pianista/etapas/00_protocolo/03_protocolo_preregistro_etapa0_v1.1_20261029.md`
(SHA-256 b75a5a502d1747518a238a36765a67c49afbecf454c8cccd29a4d9f81e71af2c), GATE 0 aprovado em 2026-10-29.
Situacao: registrada ANTES de qualquer download, leitura ou inspecao de log ou BU do 2o turno de 2026.
Autorizacao: o proponente determinou em 29/10/2026 a execucao completa ate o resultado das hipoteses.

## 1 Escopo: piloto no Tocantins

O protocolo v1.1 preve todas as UFs. Esta execucao cobre apenas TO, por dois motivos operacionais:
(i) os pacotes do 2o turno de 2026 nao estao no Portal de Dados Abertos (o conjunto
"Resultados 2026 - Arquivos transmitidos para totalizacao" tem apenas o 1o turno, atualizado em
07/10/2026) e precisam ser baixados secao por secao no Portal Resultados (pleito 3221);
(ii) o volume nacional exige processamento distribuido. Os resultados valem para TO e nao
podem ser generalizados ao pais. A execucao nacional usara o mesmo codigo e os mesmos
parametros, salvo o dt*, que sera recalculado com todas as UFs.

## 2 Fontes

| Periodo | Fonte | SHA-256 |
|---------|-------|---------|
| 1T 2026 TO | cdn.tse.jus.br .../eleicoes2026/arqurnatot/bu_imgbu_logjez_rdv_vscmr_2026_1t_TO.zip | 841a13abdca33404623397e64b1ac9fd3a36a4b7705515b1b07571125f5bc7de |
| 1T 2022 TO | cdn.tse.jus.br .../eleicoes2022/arqurnatot/bu_imgbu_logjez_rdv_vscmr_2022_1t_TO.zip | 6ba89216432b091b62744bbcbd700970a72af481fa63f570b3fd53abd9d45cfc |
| 2T 2022 TO | cdn.tse.jus.br .../eleicoes2022/arqurnatot/bu_imgbu_logjez_rdv_vscmr_2022_2t_TO.zip | 664855be4f7ddcffee6b0db50eb6c3ce827b96a0100bad53ff908cfc528a0a2f |
| 2T 2026 TO | resultados.tse.jus.br/oficial/ele2026/arquivo-urna/3221 (por secao; hash com situacao "Totalizado") | registrado no manifesto da coleta |

O 2o turno de 2018 nao tem conjunto equivalente no Portal de Dados Abertos e fica fora, como
o protocolo admite.

## 3 Mapeamento mensagem -> modo de habilitacao (revisado contra dados reais)

O catalogo das mensagens reais (2022 e 1T 2026) confirmou os eventos descritos na reconstrucao
publica do aplicativo VOTA. Instante da habilitacao: linha "Eleitor foi habilitado".

| Modo | 2022 | 2026 |
|------|------|------|
| BIO | "Tipo de habilitação do eleitor [biométrica]" | idem |
| NB_MAN (biografica: ano de nascimento + digital do mesario) | "Solicitação de dado pessoal do eleitor para habilitação manual" / "Capturada a digital do mesário" | idem |
| NB_SEM (sem biometria cadastrada) | "O eleitor não possui biometria" | sem marcador: habilitacao sem nenhum dos marcadores acima |

Validacao contra o BU oficial do 1T 2026 em TO (4.384 secoes, todas pareadas):
- votos computados no log iguais ao comparecimento do BU em 99,9% das secoes;
- habilitacoes sem marcador (NB_SEM em 2026): 27.448 no log contra 27.424 "sem biometria" no BU; correlacao por secao 0,9998;
- NB_MAN: 51.886 no log contra 50.978 "por biografia" no BU; correlacao por secao 0,994;
- total sem biometria (NB_SEM + NB_MAN) menos o total do BU, por secao: mediana 0.

## 4 Limiar dt*

dt* = **60 segundos**, percentil 1 (tipo 7) de 557.913 intervalos entre habilitacoes biometricas
consecutivas em J0 do 1T 2026 de TO (minimo exigido: 100.000). Quantis: 0,1% = 51 s; 0,5% = 57 s;
1% = 60 s; 5% = 68 s; mediana = 107 s.

Desvio declarado: o protocolo preve dt* nacional; aqui ele e de TO (piloto).

Confundidor estrutural registrado: o 1T 2026 teve cinco cargos e o 2T 2026 em TO teve dois
(Presidente e Governador); o 2T 2022 em TO teve so Presidente. Ciclos de votacao mais curtos no
2T tornam intervalos abaixo de 60 s mais frequentes sem qualquer anomalia. A comparacao com 2022
(2T menos 1T) absorve parte disso, mas o 2T 2026 de TO, com dois cargos, tende a ter ciclos mais
longos que o 2T 2022, o que reduz, e nao aumenta, a chance de rajadas em 2026.

## 5 Diagnostico de poder (sem dados de 2026)

Injecoes sinteticas de k habilitacoes NB_MAN em J1 de 300 secoes do 2T 2022 de TO, com o 1T 2022
como turno anterior, dt* = 60 s, seed 20261025.

| k | H1a (sinalizacao) | H1b bloco unico | H1b fragmentado (grupos de 4) | conjunta (fragmentado) |
|---|-------------------|-----------------|-------------------------------|------------------------|
| 5 | 0,71 | 0,00 | 0,00 | 0,00 |
| 10 | 0,90 | 0,04 | 0,28 | 0,24 |
| 20 | 0,97 | 0,04 | 0,96 | 0,93 |
| 50 | 0,99 | 0,04 | 1,00 | 0,99 |

Falsos positivos em secoes sem injecao: H1a 1,3%; H1b 0,0%.

Consequencias:
1. A sinalizacao de H1a detecta, com poder de 0,80 ou mais, insercoes de 10 ou mais habilitacoes sem biometria em J1.
2. H1b, como definida no v1.1 (pelo menos 2 rajadas nao sobrepostas), nao detecta um bloco unico e continuo de insercoes, qualquer que seja o tamanho, porque um bloco conta como uma rajada. Detecta insercoes fragmentadas a partir de cerca de 20 habilitacoes.
3. Sem alterar H1b, acrescenta-se a analise **exploratoria** H1b-L: comprimento maximo de sequencia de habilitacoes sem biometria com intervalos <= dt*, por secao e janela, comparado entre turnos e com 2022, sem valor confirmatorio.

## 6 Detalhes de implementacao fixados antes da abertura

1. NB = NB_SEM + NB_MAN; o denominador inclui todas as habilitacoes.
2. Teste nacional so e estimavel com pelo menos 30 secoes e 10 zonas; caso contrario, "nao estimavel".
3. Bootstrap: reamostragem de zonas com reposicao, independente em cada ano, 10.000 replicas; p-valor unilateral pela aproximacao normal com erro-padrao do bootstrap.
4. Modelo hierarquico de H1a: beta-binomial empirico, com hiperparametros estimados por metodo dos momentos em cada zona eleitoral, e 4.000 sorteios por secao para P(D >= 5 p.p.).
5. J3 (17h49-19h00): o 2T 2022 de TO nao tem nenhuma habilitacao nessa janela; a comparacao de J3 com 2022 fica rebaixada a exploratoria, como o protocolo preve.
6. Lista de municipios com denuncia de transporte em 25/10/2026: nenhum municipio de TO consta dos relatos usados (Salvador e outras capitais; 17 municipios de SP, PR e SC por chuva). A exclusao de robustez nao se aplica ao piloto.
7. Amostra exposta de 2,1%: as secoes nao podem ser reconstituidas a partir do material disponivel; os resultados sao reportados apenas com todas as secoes, e isso fica declarado como limitacao.
8. H1c: votos por secao decodificados do BU (ASN.1, especificacao da reconstrucao publica do VOTA, validada no 1T 2026 pela igualdade comparecimento do BU = votos computados no log); Lula = 13, Flavio = 22; variacao medida sobre o comparecimento; efeitos fixos de local de votacao se o cadastro de locais do Eleitorado 2026 estiver disponivel, senao de zona (declarado no relatorio); covariaveis: comparecimento nos dois turnos, eleitores aptos e proporcao sem biometria no 1T (BU).
