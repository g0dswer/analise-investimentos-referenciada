#!/usr/bin/env python3
"""Gerar figura estática PNG e SVG de séries documentadas (requer matplotlib)."""
import argparse, json, math
from pathlib import Path

def render(data, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    labels = data['labels']
    series = data['series']
    if not labels or not series or len(set(map(str, labels))) != len(labels):
        raise ValueError('Rótulos únicos e séries não vazias são obrigatórios.')
    for key in ('title', 'unit', 'source'):
        if not str(data.get(key, '')).strip():
            raise ValueError(f'{key} é obrigatório.')
    kind = data.get('kind', 'line')
    if kind not in ('line', 'bar'):
        raise ValueError('kind deve ser line ou bar.')
    for s in series:
        if len(s['values']) != len(labels) or not s.get('name'):
            raise ValueError('Cada série exige nome e um valor por rótulo.')
        for v in s['values']:
            if v is not None and (isinstance(v, bool) or not math.isfinite(float(v))):
                raise ValueError('Valor não finito ou booleano.')
    if not any(v is not None for s in series for v in s['values']):
        raise ValueError('Não há observações numéricas.')
    forecast = data.get('forecast_start')
    if forecast is not None and (not isinstance(forecast, int) or isinstance(forecast, bool) or not 0 <= forecast < len(labels)):
        raise ValueError('forecast_start deve ser índice válido da primeira projeção.')
    colors = ['#146b57','#376ea6','#a85d20','#82589d','#ad4655','#527f2d']
    fig, ax = plt.subplots(figsize=(10,5.5),layout='constrained')
    x = list(range(len(labels)))
    for j,s in enumerate(series):
        values = [float(v) if v is not None else math.nan for v in s['values']]
        color=colors[j%len(colors)]
        if kind == 'bar':
            width=.8/len(series)
            pos=[i-.4+width*(j+.5) for i in x]
            bars=ax.bar(pos,values,width=width,label=s['name'],color=color)
            if forecast is not None:
                for i in range(forecast,len(bars)): bars[i].set_hatch('//');bars[i].set_edgecolor('#ffffff')
        elif forecast is None:
            ax.plot(x,values,label=s['name'],marker='o',markersize=4,color=color)
        else:
            ax.plot(x[:forecast],values[:forecast],label=s['name'],marker='o',markersize=4,color=color)
            start=max(0,forecast-1)
            ax.plot(x[start:],values[start:],linestyle='--',marker='o',markersize=4,color=color)
    if forecast is not None:
        ax.axvline(forecast-.5,color='#666666',linewidth=.8)
        ax.text(forecast-.45,.97,'Projeções',transform=ax.get_xaxis_transform(),va='top',fontsize=9)
    stride=max(1,math.ceil(len(labels)/12))
    tick_indices=sorted(set(list(range(0,len(labels),stride))+[len(labels)-1]))
    ax.set_xticks(tick_indices,[str(labels[i]) for i in tick_indices],rotation=30 if len(labels)>10 else 0)
    ax.set_ylabel(data['unit']); ax.set_xlabel(data.get('x_label','Período'))
    ax.set_title(data['title'],loc='left',fontweight='bold',pad=18)
    ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
    ax.spines[['top','right']].set_visible(False)
    if len(series)>1: ax.legend(frameon=False,ncol=min(3,len(series)),loc='best')
    elif series[0]['name']!=data['title']: ax.legend(frameon=False,loc='best')
    import textwrap
    caption='Fonte: '+data['source']
    if any(v is None for s in series for v in s['values']): caption+=' | Lacunas indicam dados indisponíveis, não zero.'
    if data.get('note'): caption+=' | '+data['note']
    fig.supxlabel('\n'.join(textwrap.wrap(caption,135)),fontsize=8,ha='left',x=.01)
    output=Path(output); output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(output.with_suffix('.png'),dpi=180)
    fig.savefig(output.with_suffix('.svg'))
    plt.close(fig)
    return str(output.with_suffix('.png'))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input');p.add_argument('output')
    args=p.parse_args()
    print(render(json.loads(Path(args.input).read_text()),args.output))
