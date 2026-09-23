#!/usr/bin/env python3
"""Cálculos transparentes com entradas explícitas. Não coleta dados nem escolhe premissas."""
import argparse
import json
from datetime import date
from decimal import Decimal, Inexact, InvalidOperation, localcontext

# Contas com 40 dígitos significativos; resultados impressos com 28, todos corretos.
PRECISION = 40
OUTPUT_DIGITS = 28


def serialize(value):
    """Conversor JSON: Decimal arredondado a OUTPUT_DIGITS, zero sempre como "0"."""
    if isinstance(value, Decimal):
        with localcontext() as ctx:
            ctx.prec = OUTPUT_DIGITS
            value = +value
        return '0' if value == 0 else str(value)
    raise TypeError(f'Tipo não serializável: {type(value).__name__}')


def flag(data, key):
    value = data.get(key, False)
    if not isinstance(value, bool):
        raise ValueError(f'{key} deve ser true ou false')
    return value


def dec(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('Número inválido') from exc
    if not result.is_finite():
        raise ValueError('Entradas devem ser finitas')
    return result


def positive(value):
    result = dec(value)
    if result <= 0:
        raise ValueError('Valor deve ser positivo')
    return result


def nonnegative(value):
    result = dec(value)
    if result < 0:
        raise ValueError('Valor deve ser não negativo')
    return result


def terminal_check(data, last_flow, growth):
    """Gordon usa CF_N(1+g); o terminal por RONIC usa NOPAT_{N+1}(1 − g/RONIC).
    Os dois só coincidem se esses fluxos forem iguais (lean/Analise/TerminalRoic.lean)."""
    if 'terminal_nopat' not in data or 'ronic' not in data:
        raise ValueError('Informe terminal_nopat e ronic juntos')
    nopat = positive(data['terminal_nopat'])
    ronic = positive(data['ronic'])
    tolerance = nonnegative(data.get('terminal_tolerance', Decimal('0.0001')))
    gordon_flow = last_flow * (1 + growth)
    driver_flow = nopat * (1 - growth / ronic)
    check = dict(gordon_next_flow=gordon_flow, value_driver_next_flow=driver_flow,
                 implied_reinvestment_rate=1 - gordon_flow / nopat,
                 required_reinvestment_rate=growth / ronic)
    if abs(gordon_flow - driver_flow) > tolerance * abs(driver_flow):
        raise ValueError(
            'Terminal incoerente: CF_N(1+g) = {} e NOPAT(1−g/RONIC) = {}; reinvestimento '
            'implícito {} versus exigido {}. Ajustar o último fluxo ou usar terminal_roic.'.format(
                *(serialize(check[k]) for k in ('gordon_next_flow', 'value_driver_next_flow',
                                                'implied_reinvestment_rate',
                                                'required_reinvestment_rate'))))
    return check


def calculate(data):
    with localcontext() as ctx:
        ctx.prec = PRECISION
        return _calculate(data)


def _calculate(data):
    mode = data['mode']
    if mode == 'dcf':
        # t=1..N, mesma unidade de tempo para taxa, crescimento e fluxos.
        rate = dec(data['discount_rate']) if 'discount_rate' in data else None
        if rate is not None and rate <= -1:
            raise ValueError('Taxa deve ser maior que -1')
        flows = [dec(x) for x in data['cashflows']]
        if not flows:
            raise ValueError('Forneça ao menos um fluxo')
        if 'discount_factors' in data:
            if rate is not None:
                raise ValueError('Escolha fatores explícitos ou taxa constante')
            factors = [positive(x) for x in data['discount_factors']]
            if len(factors) != len(flows):
                raise ValueError('Um fator acumulado por fluxo é necessário')
        elif rate is not None:
            factors = [(1 + rate) ** t for t in range(1, len(flows) + 1)]
        else:
            raise ValueError('Forneça taxa constante ou fatores explícitos')
        terminal = nonnegative(data.get('terminal_value', 0))
        check = None
        if ('terminal_nopat' in data or 'ronic' in data) and 'terminal_growth' not in data:
            raise ValueError('terminal_nopat e ronic verificam terminal_growth; '
                             'para valor terminal explícito, usar terminal_roic em acoes.py')
        if 'terminal_growth' in data:
            if 'terminal_value' in data:
                raise ValueError('Escolha valor terminal ou crescimento terminal')
            if rate is None:
                raise ValueError('Com fatores explícitos, forneça valor terminal explícito')
            growth = dec(data['terminal_growth'])
            if growth <= -1 or rate <= growth or flows[-1] < 0:
                raise ValueError('Perpetuidade exige -1 < g < taxa e fluxo final não negativo')
            terminal = flows[-1] * (1 + growth) / (rate - growth)
            if 'terminal_nopat' in data or 'ronic' in data:
                check = terminal_check(data, flows[-1], growth)
        pv_flows = sum((flow / factor for flow, factor in zip(flows, factors)), Decimal(0))
        pv_terminal = terminal / factors[-1]
        result = dict(pv_cashflows=pv_flows, terminal_value=terminal, pv_terminal=pv_terminal,
                      present_value=pv_flows + pv_terminal)
        if check is not None:
            result['terminal_check'] = check
        return result
    if mode == 'cap_rate':
        noi = nonnegative(data['annual_noi'])
        cap = positive(data['cap_rate'])
        gross = noi / cap
        equity = gross + dec(data.get('other_net_assets', 0)) - nonnegative(data.get('debt', 0))
        return dict(property_value=gross, equity_value=equity,
                    value_per_unit=equity / positive(data['units']))
    if mode == 'conversion':
        source = positive(data['source_value'])
        target = positive(data['target_value'])
        basis = nonnegative(data['cost_basis'])
        tax_rate = nonnegative(data['tax_rate'])
        if tax_rate > 1:
            raise ValueError('Alíquota deve estar entre 0 e 1')
        units = positive(data['source_units'])
        if units != units.to_integral_value():
            raise ValueError('Quantidade de cotas deve ser inteira')
        # Cotas inteiras e residual saem de divisão inteira exata; a razão arredondada
        # (1/3 → 0,333…3) perderia uma cota. Ver lean/Analise/Conversao.lean.
        with localcontext() as ctx:
            ctx.traps[Inexact] = True
            try:
                tax = max(source - basis, Decimal(0)) * tax_rate
                net = source - tax
                whole, residual = divmod(units * net, target)
            except Inexact as exc:
                raise ValueError('Valores exigem arredondamento; reduza as casas decimais') from exc
        ratio = net / target
        theoretical_units = units * net / target
        result = dict(tax_per_unit=tax, net_per_unit=net, conversion_ratio=ratio,
                      theoretical_units=theoretical_units, whole_units=whole,
                      residual_cash_at_target_value=residual)
        if 'old_dividend' in data and 'new_dividend' in data:
            old = nonnegative(data['old_dividend'])
            new = nonnegative(data['new_dividend'])
            result.update(old_income=units * old, new_whole_unit_income=whole * new,
                          new_proportional_income=theoretical_units * new)
        return result
    if mode == 'reinvested_return':
        initial = positive(data['initial_price'])
        observations = data['observations']
        if not observations:
            raise ValueError('Forneça observações cronológicas')
        units = Decimal(1)
        previous_date = None
        history = []
        for obs in observations:
            current_date = date.fromisoformat(obs['date'])
            if previous_date is not None and current_date <= previous_date:
                raise ValueError('Datas devem ser estritamente crescentes')
            previous_date = current_date
            price = positive(obs['price'])
            dividend = nonnegative(obs.get('dividend', 0))
            cash = units * dividend
            units += cash / price
            history.append(dict(date=obs['date'], units=units, value=units * price))
        return dict(final_units=units, final_value=units * price,
                    total_return=units * price / initial - 1, history=history)
    if mode == 'metrics':
        price = positive(data['price'])
        result = {}
        if 'target_price' in data:
            target = positive(data['target_price'])
            result.update(upside=target / price - 1, margin_to_fair_value=1 - price / target)
        if 'nav_per_unit' in data:
            result['price_to_nav'] = price / positive(data['nav_per_unit'])
        if 'monthly_dividend' in data:
            dy = nonnegative(data['monthly_dividend']) / price
            result.update(monthly_yield=dy, annualized_simple_yield=12 * dy,
                          annualized_compound_yield=(1 + dy) ** 12 - 1)
        if 'entry_price' in data:
            result['holding_return_without_reinvestment'] = (
                price + nonnegative(data.get('distributions_received', 0))
            ) / positive(data['entry_price']) - 1
        if not result:
            raise ValueError('Forneça métricas a calcular')
        return result
    raise ValueError('Modo desconhecido')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='JSON com mode e premissas, taxas em frações: 0.10 = 10%%')
    args = parser.parse_args()
    try:
        with open(args.input, encoding='utf-8') as handle:
            result = calculate(json.load(handle, parse_float=Decimal))
        print(json.dumps(result, default=serialize, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, TypeError, ArithmeticError) as exc:
        parser.exit(2, f'Entradas inválidas: {exc}\n')


if __name__ == '__main__':
    main()
