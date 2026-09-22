#!/usr/bin/env python3
"""Pontes de valuation de ações com premissas explícitas, sem estimar entradas ausentes."""
from decimal import Decimal, localcontext
import json, argparse
from pathlib import Path
from calculos import dec, positive, nonnegative

def calculate(data):
    mode=data['mode']
    if mode=='fcff':
        rows=[]
        for row in data['periods']:
            tax=nonnegative(row['tax_rate'])
            if tax>1: raise ValueError('tax_rate deve estar em [0,1]')
            ebit=dec(row['ebit'])
            # Tax shield for a loss must be explicitly modeled, not automatic.
            if ebit<0 and not row.get('loss_tax_shield',False): nopat=ebit
            else: nopat=ebit*(1-tax)
            flow=nopat+nonnegative(row['da'])-nonnegative(row['capex'])-dec(row['delta_working_capital'])
            rows.append({'period':row['period'],'nopat':nopat,'fcff':flow})
        if not rows: raise ValueError('Série vazia')
        if len({str(r['period']) for r in rows})!=len(rows): raise ValueError('Período duplicado')
        return {'periods':rows,'unit':data['unit']}
    if mode=='terminal_roic':
        nopat=nonnegative(data['nopat_next']);r=positive(data['discount_rate']);g=dec(data['growth']);roic=positive(data['roic'])
        if g<0 or g>=r or g>roic: raise ValueError('Exige 0 <= g < taxa e g <= ROIC; outro regime requer modelo explícito')
        reinvestment=g/roic
        fcff=nopat*(1-reinvestment)
        return {'reinvestment_rate':reinvestment,'terminal_fcff':fcff,'terminal_value':fcff/(r-g)}
    if mode=='equity_bridge':
        value=dec(data['present_value']);model=data['cashflow_type']
        if model=='fcff':
            # All terms are in the same total currency unit, e.g. R$ million.
            equity=value+nonnegative(data['cash'])+dec(data['other_nonoperating_assets'])-nonnegative(data['debt'])-nonnegative(data['minorities'])
        elif model in ('fcfe','dividends'):
            if any(k in data for k in ('cash','debt','minorities','other_nonoperating_assets')):
                raise ValueError('FCFE/DDM já valem o equity; não aplicar ponte de dívida/caixa automaticamente')
            equity=value
        else: raise ValueError('cashflow_type deve ser fcff, fcfe ou dividends')
        shares=positive(data['shares']);scale=positive(data['money_scale'])
        # shares is the actual number of economic shares, not number of market units.
        result={'equity_value':equity,'value_per_share':equity*scale/shares}
        if 'unit_composition' in data:
            count=positive(data['unit_composition'])
            if count!=count.to_integral_value(): raise ValueError('Composição da unit deve ser inteira')
            if not data.get('equal_economic_rights',False): raise ValueError('Exige equivalência econômica explícita entre classes; senão avaliar cada classe')
            result['value_per_unit']=result['value_per_share']*count
        return result
    raise ValueError('Modo desconhecido')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('input');args=parser.parse_args()
    with localcontext() as ctx:
        ctx.prec=40
        result=calculate(json.loads(Path(args.input).read_text(),parse_float=Decimal))
    print(json.dumps(result,default=str,ensure_ascii=False,indent=2))
