import type { Localized } from "../types/content.ts";
export const cases: { title: string; year: string; description: Localized; caution: Localized }[] = [
  {
    title: "Volkswagen — Dieselgate", year: "2015",
    description: { pt: "Caso documentado de software que reconhecia condições de teste de emissões e alterava seu comportamento.", en: "Documented case of software recognizing emissions-test conditions and changing its behavior." },
    caution: { pt: "Analogia de risco arquitetural; não é evidência sobre eleições no Brasil.", en: "Architectural-risk analogy, not evidence concerning elections in Brazil." }
  },
  {
    title: "SolarWinds", year: "2020",
    description: { pt: "Comprometimento de cadeia de fornecimento por atualização de software legítima em aparência.", en: "Supply-chain compromise through an apparently legitimate software update." },
    caution: { pt: "Demonstra um vetor geral de ameaça, não uma ocorrência eleitoral específica.", en: "Illustrates a general threat vector, not a specific electoral occurrence." }
  },
  {
    title: "Horizon — Post Office", year: "1999–2015",
    description: { pt: "Controvérsia sobre confiabilidade de registros informatizados usados como prova.", en: "Dispute over reliability of computerized records used as evidence." },
    caution: { pt: "Exige exame das decisões e documentação primária antes de atribuir mecanismos concretos.", en: "Requires review of primary rulings and documentation before specific mechanism claims." }
  }
];
