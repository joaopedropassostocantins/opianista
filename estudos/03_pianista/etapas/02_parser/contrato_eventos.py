"""Contrato comum para os Estudos 03 e 05. NÃO decodifica .logjez do TSE.

Opera APENAS sobre eventos já NORMALIZADOS e auditados do 1T2026 ou 2T2024.
A tradução de mensagens oficiais depende de uma amostra real legalmente obtida
do período autorizado e revisão manual. Campos inexistentes não são inferidos.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, time

ALLOWED_PERIODS = frozenset({"1T2026", "2T2024"})
J0_START, J0_END = time(9, 0, 0), time(14, 59, 59)
OFFICIAL_KINDS = frozenset({"BIO_VALID", "HAB_MANUAL", "VOTO_FIM", "SESSAO_FIM",
                             "BU_INICIO", "BU_FIM", "DESCONHECIDO"})

@dataclass(frozen=True)
class NormalizedEvent:
    period: str
    section_id: str
    timestamp: datetime
    kind: str
    source_line: int

    def __post_init__(self):
        if self.period not in ALLOWED_PERIODS:
            raise ValueError("2T2026 e outros períodos não autorizados bloqueados.")
        if not self.section_id:
            raise ValueError("Seção obrigatória.")
        if self.kind not in OFFICIAL_KINDS:
            raise ValueError("Classificação não faz parte do dicionário aprovado.")
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("Timestamp deve ter fuso explícito.")

def catalog(events: list[NormalizedEvent]) -> dict[str,int]:
    return dict(sorted(Counter(e.kind for e in events).items()))

def linear_quantile(values: list[float], q: float) -> float:
    """Quantil Hyndman–Fan tipo 7, sem dependências; inclui empates."""
    if not 0 <= q <= 1 or not values:
        raise ValueError("Quantil exige dados e 0<=q<=1.")
    a = sorted(values)
    h = (len(a)-1)*q
    lo = int(h)
    hi = min(len(a)-1, lo+1)
    frac = h-lo
    return a[lo]*(1-frac)+a[hi]*frac

def biometric_intervals_j0(events: list[NormalizedEvent]) -> list[float]:
    """Intervalos entre eventos biométricos consecutivos no J0 de uma mesma seção.

    Não presume que um evento genérico de habilitação seja biométrico.
    Usa ordenação estável para preservar empates. Horários locais precisam
    ter sido normalizados corretamente ANTES desta etapa.
    """
    by_section: dict[str, list[NormalizedEvent]] = defaultdict(list)
    for ev in events:
        if ev.period != "1T2026":
            raise ValueError("dt* só usa 1T2026, bloqueio fail-closed.")
        if ev.kind == "BIO_VALID" and J0_START <= ev.timestamp.timetz().replace(tzinfo=None) <= J0_END:
            by_section[ev.section_id].append(ev)
    intervals: list[float] = []
    for section_events in by_section.values():
        ordered = sorted(section_events, key=lambda e:e.timestamp)
        for prev, curr in zip(ordered, ordered[1:]):
            seconds = (curr.timestamp-prev.timestamp).total_seconds()
            if seconds < 0:
                raise ValueError("Intervalo negativo: problema de fuso/ordenação.")
            intervals.append(seconds)
    return intervals

def dt_star(events: list[NormalizedEvent], minimum: int = 100_000) -> dict:
    if minimum < 1:
        raise ValueError("Mínimo deve ser positivo.")
    intervals = biometric_intervals_j0(events)
    return {"n_intervals":len(intervals),
            "dt_star_seconds":linear_quantile(intervals,0.01) if len(intervals)>=minimum else None,
            "status":"ESTIMADO" if len(intervals)>=minimum else "NAO_ESTIMAVEL",
            "method":"Hyndman-Fan tipo 7; P01, J0 09:00:00-14:59:59, 1T2026"}
