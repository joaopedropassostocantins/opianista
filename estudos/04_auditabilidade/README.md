# Estudo 04 - Auditabilidade da urna e poder de deteccao

## Pergunta

Que tamanho de adulteracao o sistema atual de verificacao consegue detectar?
Em particular, qual o poder do Teste de Integridade e das comparacoes entre
log, BU e RDV contra um atacante interno?

## Argumento central

1. Log, BU e RDV sao gerados pelo mesmo software na mesma urna. Compara-los
   entre si, ou comparar o BU impresso com o publicado, protege contra
   adulteracao na transmissao e na totalizacao, mas nao contra adulteracao
   dentro da urna. A assinatura digital prova autenticidade, nao a correcao do
   conteudo anterior a assinatura.
2. Simetria epistemica: contra um ataque indetectavel por construcao,
   P(dados | fraude) = P(dados | sem fraude). Os dados nao confirmam nem
   refutam a fraude. "O sistema nao e verificavel contra um insider perfeito"
   e defensavel; "logo houve fraude em 2026" e um non sequitur.
3. Sem trilha em papel, a evidencia disponivel limita o tamanho maximo de
   fraude indetectavel, mas nao prova sua ausencia. Isso conecta o estudo ao
   conceito de independencia de software (software independence) e a
   auditorias de limitacao de risco.

## Material de base

- Fichamento de ARANHA, D. F. et al. (2019), Computers & Security, sobre as
  vulnerabilidades encontradas no Teste Publico de Seguranca de 2017.
  [VERIFICAR titulo, volume e paginas antes de citar.] Ponto essencial: a
  manipulacao da contagem foi tentada, mas nao validada em hardware real antes
  do fim do teste.
- Referencias a conferir na fonte: RIVEST e WACK (2006) sobre independencia de
  software; LINDEMAN e STARK (2012) sobre auditorias de limitacao de risco.

## Proposta de artigo

Quantificar o poder de deteccao do Teste de Integridade sob cenarios de ataque
(proporcao de urnas adulteradas, tamanho da adulteracao, capacidade de
reconhecer o ambiente de teste), por simulacao. Formato ABNT.

## Pendencias

- Enviar o DOCX do fichamento (gerado em sessao anterior; nao recuperavel
  automaticamente).
