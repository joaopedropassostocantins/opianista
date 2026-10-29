# Site editorial opianista

Aplicação independente do repositório, construída em TypeScript e Vite. O site explica a tese conceitual **O Paradoxo do Arquiteto-Fiscal**, acompanha os quatro estudos e remete aos protocolos canônicos do GitHub.

## Proveniência e limite de fidelidade

- Original publicado: https://arquiteto-fiscal-evidencia.hazyzebra6.chatgpt.site
- Código-fonte original **não disponibilizado**. Este projeto é uma **nova implementação editorial**, derivada do texto-base e da reconstrução estática incluídos no PR #2; não se anuncia cópia visual ou funcional fiel.
- Texto-base preservado sem edição em `public/arquivo/conteudo_base_20261026.md` e reconstrução anterior preservada em `public/arquivo/reconstrucao_estatica_pr2.html`.
- A nova interface aplica a arquitetura de pasta `site/`, módulos de conteúdo, componentes visuais, testes e tokens CSS. Nenhum protocolo foi alterado.

## Desenvolvimento

Requer Node.js 22+.

```sh
cd site
npm install
npm run dev
npm run typecheck
npm test
npm run build
```

O projeto usa dependências fixadas no package.json; o lockfile deve ser gerado e incorporado antes do deploy de produção e a CI deverá então usar `npm ci`.

## Estrutura

- `src/content/`: única fonte editorial de estudos, etapas, evidências, fontes e glossário.
- `src/components/`: apresentação e componentes sem lógica científica.
- `src/app/`: navegação, idioma e acessibilidade.
- `src/lib/`: criação de links e utilitários.
- `public/arquivo/`: preservação dos materiais de referência do PR #2.
- `tests/`: validação local de status, conteúdo, caminhos e acessibilidade estrutural.

## Transparência

A Etapa 0 é exibida como aprovada conforme `protocolos/REGISTRO.md`. O README do Estudo 03 tem um trecho posterior conflitante, identificado no painel como pendência editorial. O conteúdo do site é **snapshot em 2026-10-29**, não consulta automática ao estado do GitHub.

A página é um ensaio de teoria da prova e um painel de pesquisa em andamento. Não apresenta evidência empírica de fraude, tampouco demonstra inexistência de fraude.

## Publicação

Build: `npm run build` gera `site/dist`. Para GitHub Pages, usar `GITHUB_PAGES=true npm run build` para base `/opianista/`. O workflow incluído apenas **valida** o código; não altera o site original, não ativa Pages e não implanta automaticamente.

## Licença

Código MIT; textos CC BY 4.0, conforme README do repositório raiz.