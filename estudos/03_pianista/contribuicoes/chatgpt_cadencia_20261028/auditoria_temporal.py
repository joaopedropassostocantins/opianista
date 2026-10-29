#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditoria de cadência temporal. Controle: APENAS 2º turno MUNICIPAL (prefeito).
Alvo: 2º turno presidencial de 2026. Nenhum turno presidencial anterior entra no controle.

Uso:
 python auditoria_temporal.py extrair --zip /caminho/arquivo_TSE_2024_2t_SP.zip --ano 2024 --tipo prefeito --data 2024-10-27 --abertura-local 08:00 --saida prefeito_2024_SP.csv
 python auditoria_temporal.py extrair --zip /caminho/arquivo_TSE_2026_2t_SP.zip --ano 2026 --tipo presidente --data 2026-10-25 --abertura-local 08:00 --saida presidente_2026_SP.csv
 python auditoria_temporal.py testar --referencias prefeito_2024_SP.csv --alvo presidente_2026_SP.csv --saida resultados

ATENÇÃO: zip pode ter dezenas de GB. Extrai logs de maneira incremental. Para .logjez
formato 7zip antigo, instalar py7zr. Valide manualmente 20 arquivos de cada ano,
logs de contingência e a reconciliação com BUs antes de interpretar os resultados.
Os horários de abertura são LOCAIS; --abertura-local deve ser ajustado conforme UF/ano.
"""
import argparse
import io
import json
import re
import zipfile
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t, betabinom
from statsmodels.stats.multitest import multipletests

# UF onde havia disputa estadual para governador no segundo turno de 2026:
# nesses lugares o eleitor teve 2 cargos e a cadência não é equivalente a prefeito 2024.
GOV_2026 = {'AC','AM','ES','RN','TO','DF'}
MSG_VOTO = 'O voto do eleitor foi computado'
RE_DATA = re.compile(r'(?P<data>\d{2}/\d{2}/\d{4})\s+(?P<hora>\d{2}:\d{2}:\d{2})')
RE_CHAVE1 = re.compile(r'[mM](\d{4,5})[-_][zZ](\d{1,4})[-_][sS](\d{1,4})')
RE_CHAVE2 = re.compile(r'(?<!\d)(\d{5})(\d{4})(\d{4})(?!\d)')
QCOLS = [f'q{j:02d}' for j in range(36)]


def chave_de_nome(nome):
    base = Path(nome).name
    m = RE_CHAVE1.search(base) or RE_CHAVE2.search(base)
    if not m:
        return None
    return tuple(str(int(x)) for x in m.groups())


def decode_log(b):
    try:
        return b.decode('utf-8')
    except UnicodeDecodeError:
        return b.decode('latin-1',errors='replace')

def texto_log(b):
    # Na geração 2026 o arquivo pode ser zip; nas anteriores é frequentemente 7z.
    if b[:2] == b'PK':
        with zipfile.ZipFile(io.BytesIO(b)) as z:
            nomes = [n for n in z.namelist() if n.lower().endswith('logd.dat')]
            if not nomes:
                raise ValueError('ZIP interno não possui logd.dat')
            return decode_log(z.read(nomes[0]))
    if b[:6] == b'7z\xbc\xaf\x27\x1c':
        try:
            import py7zr
            from py7zr.io import BytesIOFactory
        except ImportError as e:
            raise RuntimeError('pip install py7zr') from e
        with py7zr.SevenZipFile(io.BytesIO(b)) as z:
            fac = BytesIOFactory(limit=100 * 1024 * 1024)
            z.extractall(factory=fac)
            nomes = [n for n in fac.products if n.lower().endswith('logd.dat')]
            if not nomes:
                raise ValueError('7Z interno não possui logd.dat')
            obj = fac.products[nomes[0]]
            obj.seek(0)
            return decode_log(obj.read())
    # Para arquivos .logd.dat soltos
    return decode_log(b)


def extrair(args):
    if (args.ano, args.tipo) not in [(2016, 'prefeito'), (2020, 'prefeito'),(2024, 'prefeito'),
                                     (2014, 'governador'), (2018, 'governador'),(2022, 'governador'),
                                     (2026, 'presidente')]:
        raise SystemExit('Permitidos apenas segundos turnos municipais/estaduais históricos e presidencial 2026.')
    if args.tipo == 'presidente' and args.ano != 2026:
        raise SystemExit('Turnos presidenciais anteriores são proibidos como referência.')
    hora_abr = datetime.strptime(args.abertura_local, '%H:%M').time()
    dia = datetime.strptime(args.data, '%Y-%m-%d')
    inicio = datetime.combine(dia.date(), hora_abr)
    fim = inicio + timedelta(hours=9)
    limite_reconciliacao = fim + timedelta(hours=3)
    uf = args.uf.upper() if args.uf else (re.search(r'_2t_([a-zA-Z]{2})\.zip$', args.zip) or [None, ''])[1].upper()
    if len(uf) != 2:
        raise SystemExit('Informe --uf se não constar no nome do ZIP.')
    rows = []
    skip = Counter()
    with zipfile.ZipFile(args.zip) as outer:
        names = [n for n in outer.namelist() if n.lower().endswith(('.logjez','.log.jez','-log.jez','.logd.dat'))]
        print(f'Localizados {len(names)} arquivos de log. Processando...', flush=True)
        for i,name in enumerate(names):
            ch = chave_de_nome(name)
            if ch is None:
                skip['sem_chave'] += 1
                continue
            try:
                texto = texto_log(outer.read(name))
            except Exception as exc:
                skip['erro_descompactar'] += 1
                if skip['erro_descompactar'] <= 3:
                    print(f'AVISO: {name}: {exc}',flush=True)
                continue
            times = []
            posteriores = []
            tipos = []
            identificacao = 'desconhecida'
            for line in texto.splitlines():
                dat = RE_DATA.search(line[:45])
                if not dat:
                    if MSG_VOTO in line:
                        skip['hora_invalida'] += 1
                    continue
                try:
                    dt = datetime.strptime(dat.group('data')+' '+dat.group('hora'),'%d/%m/%Y %H:%M:%S')
                except ValueError:
                    continue
                if not (inicio <= dt < limite_reconciliacao):
                    continue
                if 'Tipo de habilitação do eleitor [biométrica]' in line:
                    identificacao = 'biometrica'
                elif 'O eleitor não possui biometria' in line:
                    identificacao = 'sem_cadastro'
                elif 'Solicitação de dado pessoal do eleitor para habilitação manual' in line:
                    identificacao = 'manual'
                if MSG_VOTO in line:
                    if dt < fim:
                        times.append(dt)
                        tipos.append(identificacao)
                    else:
                        posteriores.append(dt)
                    identificacao = 'desconhecida'
            if not times:
                skip['sem_votos_no_dia'] += 1
                continue
            pares = sorted(zip(times,tipos))
            times = [t for t,_ in pares]
            tipos = [m for _,m in pares]
            mins = [(t-inicio).total_seconds()/60 for t in times]
            quarters = np.bincount(np.array(mins,dtype=int)//15, minlength=36)[:36]
            # Medida exploratória de sequências rápidas. Não pressupõe impossibilidade física.
            intervals = np.diff(np.array([(t-inicio).total_seconds() for t in times]))
            tail_intervals = np.diff(np.array([(t-inicio).total_seconds() for t in times if t >= inicio+timedelta(hours=8)]))
            run = 1
            longest = 1
            for gap in tail_intervals:
                run = run + 1 if gap <= 15 else 1
                longest = max(longest,run)
            ultimos_modos = [m for (t,m) in pares if t >= inicio + timedelta(hours=8)]
            modos = Counter(ultimos_modos)
            rows.append(dict(ano=args.ano,tipo=args.tipo,turno=2,uf=uf,
                             municipio=ch[0],zona=ch[1],secao=ch[2],
                             n_8_17=len(times),n_depois_17=len(posteriores),
                             n_total_dia=len(times)+len(posteriores),
                             ultimo_voto=times[-1].isoformat(),
                             ultimo_voto_dia=max(times+posteriores).isoformat(),
                             n_manual_16_17=modos['manual'],
                             n_sem_cadastro_16_17=modos['sem_cadastro'],
                             n_biometrica_16_17=modos['biometrica'],
                             n_identificacao_indeterminada_16_17=modos['desconhecida'],
                             n_intervalos_ate15s=int(np.sum(intervals <= 15)),
                             sequencia_16_17_ate15s=int(longest),
                             **dict(zip(QCOLS,quarters.tolist()))))
            if (i+1)%10000==0:
                print(f'{i+1}/{len(names)} logs; {len(rows)} extraídos',flush=True)
    df = pd.DataFrame(rows)
    if df.empty:
        raise SystemExit('Nenhum log válido. Verifique --data, --abertura-local e formato dos arquivos.')
    dup = df.duplicated(['uf','municipio','zona','secao'],keep=False)
    if dup.any():
        # Contingência/recarregamento exigem reconstrução completa; não escolher um dos logs.
        print(f'ATENÇÃO: {dup.sum()} linhas de seções duplicadas. Todas excluídas até auditoria de contingência.')
        df = df[~dup].copy()
    df.to_csv(args.saida,index=False)
    Path(args.saida+'.qualidade.json').write_text(json.dumps(dict(
        origem=args.zip,ano=args.ano,tipo=args.tipo,turno=2,uf=uf,
        data=args.data,abertura_local=args.abertura_local,
        logs_no_zip=len(names),secoes_exportadas=len(df),exclusoes=dict(skip),
        secao_duplicada=int(dup.sum()),
        nota='Comparar n_total_dia com comparecimento BU; votos após 12 horas não são contados. Validar contingências.'),indent=2,ensure_ascii=False),encoding='utf8')
    print(f'{len(df):,} seções exportadas para {args.saida}')


def carregar_csv(caminhos, ano,tipo):
    frames=[]
    for path in caminhos:
        p=pd.read_csv(path,dtype={'uf':'string','municipio':'string','zona':'string','secao':'string'})
        for c in ['uf','municipio','zona','secao','ano','tipo','turno','n_8_17',*QCOLS]:
            if c not in p.columns:
                raise ValueError(f'{path}: falta coluna {c}')
        if not p['ano'].eq(ano).all() or not p['tipo'].eq(tipo).all() or not p['turno'].eq(2).all():
            raise ValueError(f'{path}: eleição errada (exigido {ano}, {tipo}, turno 2)')
        assert (p[QCOLS].sum(axis=1)==p['n_8_17']).all(), 'Intervalos não conciliam n_8_17'
        assert (p[QCOLS]>=0).all().all()
        frames.append(p)
    p=pd.concat(frames,ignore_index=True)
    p['uf']=p['uf'].str.upper()
    for c in ['municipio','zona','secao']:
        p[c]=p[c].apply(lambda x: str(int(x)))
    k=['uf','municipio','zona','secao']
    if p.duplicated(k).any():
        raise ValueError('Há duplicatas de seção entre os arquivos. Revisar contingências/duplicações.')
    p['n_16_17']=p[QCOLS[-4:]].sum(axis=1)
    p['p_16_17']=p['n_16_17']/p['n_8_17'].replace(0,np.nan)
    return p


def tteste_cluster(d, n_boot=3000,seed=20261028):
    # Cidade é o cluster de bootstrap; efeito primário é média dos efeitos médios municipais.
    c=d.groupby(['uf','municipio'],observed=True)['delta'].agg(['mean','count']).reset_index()
    vals=c['mean'].to_numpy(float)
    if len(vals)<5:
        return dict(erro='Menos de cinco municípios elegíveis; inferência populacional não sustentada.')
    dbar=vals.mean()
    se=vals.std(ddof=1)/np.sqrt(len(vals))
    p=float(2*student_t.sf(abs(dbar/se),len(vals)-1)) if se>0 else float('nan')
    crit=student_t.ppf(0.975,len(vals)-1)
    rng=np.random.default_rng(seed)
    bi=rng.integers(0,len(vals),size=(n_boot,len(vals)))
    boots=vals[bi].mean(axis=1)
    blo,bhi=np.percentile(boots,[2.5,97.5])
    return dict(municipios=len(c),secoes=len(d),media_delta_pp=round(100*dbar,5),
                erro_padrao_cluster_pp=round(100*se,5),p_teste_t_municipal=p,
                IC95_t_pp=[round(100*(dbar-crit*se),5),round(100*(dbar+crit*se),5)],
                IC95_bootstrap_municipio_pp=[round(100*blo,5),round(100*bhi,5)])


def sinalizadores_locais(ref,alvo,saida):
    # Comparação exploratória, não comprovação de fraude. Modelo heterogêneo por cidade,
    # centrado na média de 2026 e dispersão histórica municipal para evitar excesso de flags.
    key=['uf','municipio']
    stats = ref.groupby(key).apply(lambda g: pd.Series(dict(
        nsecoes=len(g), media=np.average(g.p_16_17,weights=g.n_8_17),
        variancia=g.p_16_17.var(ddof=1),
        ruido=np.mean(g.p_16_17.mean()*(1-g.p_16_17.mean())/g.n_8_17)
    )),include_groups=False).reset_index()
    stats=stats[stats.nsecoes>=30]
    stats['rho']=np.clip((stats.variancia-stats.ruido)/(stats.media*(1-stats.media)-stats.ruido).clip(lower=1e-6),0.0002,0.25)
    t=alvo.merge(stats[['uf','municipio','rho','nsecoes']],on=key,how='inner')
    if t.empty:
        return 0
    # O deslocamento geral de 2026 é captado no teste nacional, não atribuído a seções individuais.
    mean26=alvo.groupby(key).apply(lambda g: np.average(g.p_16_17,weights=g.n_8_17),include_groups=False)
    mean26=mean26.rename('p_cidade_26').reset_index()
    t=t.merge(mean26,on=key)
    a=t.p_cidade_26*(1-t.rho)/t.rho
    b=(1-t.p_cidade_26)*(1-t.rho)/t.rho
    k=t.n_16_17.astype(int)
    n=t.n_8_17.astype(int)
    pl=betabinom.cdf(k,n,a,b)
    pu=betabinom.sf(k-1,n,a,b)
    t['p_bilateral']=np.minimum(1,2*np.minimum(pl,pu))
    t['excesso_votos']=t.n_16_17 - t.n_8_17*t.p_cidade_26
    t['delta_cidade_pp']=100*(t.p_16_17-t.p_cidade_26)
    t['q_fdr']=multipletests(t.p_bilateral,method='fdr_bh')[1]
    t['triagem']=(t.q_fdr<0.01)&(t.excesso_votos>=15)&(t.delta_cidade_pp>=5)
    t.sort_values('q_fdr')[['uf','municipio','zona','secao','n_8_17','n_16_17',
        'p_cidade_26','delta_cidade_pp','excesso_votos','p_bilateral','q_fdr','triagem']].to_csv(
        saida/'triagem_exploratoria_secoes.csv',index=False)
    return int(t.triagem.sum())


def testar(args):
    if (args.tipo_referencia=='prefeito' and args.ano_referencia not in [2016,2020,2024]) or (args.tipo_referencia=='governador' and args.ano_referencia not in [2014,2018,2022]):
        raise SystemExit('Ano da referência incompatível com o cargo.')
    if args.tipo_referencia=='governador' and not args.secundario:
        raise SystemExit('Governador histórico coincide com votação presidencial. Use --secundario para declarar esse viés e não usar como paradigma primário.')
    ref=carregar_csv(args.referencias,args.ano_referencia,args.tipo_referencia)
    alvo=carregar_csv(args.alvo,2026,'presidente')
    ref=ref[ref.n_8_17>=50].copy()
    if args.tipo_referencia=='prefeito':
        alvo=alvo[(alvo.n_8_17>=50)&(~alvo.uf.isin(GOV_2026))].copy()
    else:
        alvo=alvo[(alvo.n_8_17>=50)&(alvo.uf.isin(GOV_2026))].copy()
    key=['uf','municipio','zona','secao']
    d=ref.merge(alvo,on=key,suffixes=('_24','_26'),how='inner',validate='one_to_one')
    if d.empty:
        raise SystemExit('Nenhuma seção pareada. Verifique zonas/municípios, UFs e 2024 2º turno.')
    d['delta']=d.p_16_17_26-d.p_16_17_24
    out=Path(args.saida)
    out.mkdir(parents=True,exist_ok=True)
    d[[*key,'n_8_17_24','n_8_17_26','n_16_17_24','n_16_17_26',
       'p_16_17_24','p_16_17_26','delta']].to_csv(out/'pares.csv',index=False)
    result=tteste_cluster(d)
    result.update(dict(
        contraste=f'2T {args.tipo_referencia.upper()} {args.ano_referencia} x 2T PRESIDENTE 2026',
        referencias_admitidas=[f'{args.ano_referencia}-{args.tipo_referencia}-2T'],
        controle_secundario_com_presidencia_simultanea=bool(args.tipo_referencia=='governador'),
        referencias_excluidas=['TODOS os turnos presidenciais anteriores',
                             'Governadores em pleitos gerais ocorrem simultaneamente à disputa presidencial',
                             'Grupos com número de cargos incompatível são separados'],
        definicao='share de votos entre hora 8 e hora 9 desde abertura; denominador votos durante nove horas',
        efeito_material_minimo_pp=0.5,
        alerta_identificacao=('No controle estadual, o eleitor vota também para presidente: este não é um padrão independente.'
                              if args.tipo_referencia=='governador' else
                              'Controle municipal com somente prefeito no segundo turno; 2020 sob pandemia.'),
        cobertura=dict(secoes_referencia=len(ref),secoes_alvo=len(alvo),secoes_pareadas=len(d),
                        municipios_pareados=d[['uf','municipio']].drop_duplicates().shape[0]),
        nota='Resultados observacionais; diferenças podem refletir mobilização/eleitorado/condições locais. Não provam votos fictícios.'))
    result['flag_material_0p5pp']=bool(abs(result.get('media_delta_pp',0))>=0.5)
    result['triagens_exploratorias']=sinalizadores_locais(ref,alvo,out)
    (out/'resultado.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(result,indent=2,ensure_ascii=False))


def main():
    ap=argparse.ArgumentParser(description='Auditoria temporal com referência EXCLUSIVAMENTE municipal')
    subs=ap.add_subparsers(dest='cmd',required=True)
    e=subs.add_parser('extrair',help='Extrair eventos de um ZIP oficial do TSE')
    e.add_argument('--zip',required=True)
    e.add_argument('--ano',required=True,type=int)
    e.add_argument('--tipo',required=True,choices=['prefeito','governador','presidente'])
    e.add_argument('--data',required=True,help='AAAA-MM-DD')
    e.add_argument('--abertura-local',required=True,help='HH:MM do relógio gravado no log')
    e.add_argument('--uf',required=False)
    e.add_argument('--saida',required=True)
    e.set_defaults(func=extrair)
    t=subs.add_parser('testar',help='Teste pareado histórico/2026')
    t.add_argument('--referencias',nargs='+',required=True)
    t.add_argument('--ano-referencia',type=int,default=2024,choices=[2016,2020,2024,2014,2018,2022])
    t.add_argument('--tipo-referencia',default='prefeito',choices=['prefeito','governador'])
    t.add_argument('--secundario',action='store_true',help='Obrigatório para controles de governador, que coincidem com pleito presidencial')
    t.add_argument('--alvo',nargs='+',required=True)
    t.add_argument('--saida',required=True)
    t.set_defaults(func=testar)
    args=ap.parse_args()
    args.func(args)
if __name__=='__main__':
    main()