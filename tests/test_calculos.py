"""Testes dos helpers de cálculo. Executar: python3 -m unittest discover -s tests"""
import json
import random
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from fractions import Fraction
from math import floor
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import acoes  # noqa: E402
import calculos  # noqa: E402


def conversion(**kw):
    return calculos.calculate(dict(mode='conversion', **kw))


class ConversionTest(unittest.TestCase):
    def test_razao_exata_nao_perde_cota(self):
        # Antes: 99 cotas e residual 30,000 (= uma cota de destino).
        result = conversion(source_value=Decimal('10.00'), target_value=Decimal('30.00'),
                            cost_basis=Decimal('10.00'), tax_rate=Decimal('0.2'),
                            source_units=300)
        self.assertEqual(result['whole_units'], 100)
        self.assertEqual(result['residual_cash_at_target_value'], 0)

    def test_invariantes_contra_fracoes(self):
        # Mesmas propriedades provadas em lean/Analise/Conversao.lean.
        rng = random.Random(20260923)
        for _ in range(2000):
            source = Decimal(rng.randint(1, 50000)) / 100
            target = Decimal(rng.randint(1, 50000)) / 100
            basis = Decimal(rng.randint(0, 50000)) / 100
            rate = Decimal(rng.choice(['0', '0.15', '0.2', '1']))
            units = rng.randint(1, 10**6)
            result = conversion(source_value=source, target_value=target, cost_basis=basis,
                                tax_rate=rate, source_units=units)
            net = Fraction(source) - max(Fraction(source) - Fraction(basis), 0) * Fraction(rate)
            total = units * net
            whole = Fraction(result['whole_units'])
            residual = Fraction(result['residual_cash_at_target_value'])
            self.assertEqual(whole, floor(total / Fraction(target)))
            self.assertEqual(whole * Fraction(target) + residual, total)
            self.assertTrue(0 <= residual < Fraction(target))


class ExamplesTest(unittest.TestCase):
    def test_fcff_exemplo(self):
        result = acoes.calculate(dict(mode='fcff', unit='u', periods=[dict(
            period='Ano 1', ebit=120, tax_rate=Decimal('0.25'), da=15, capex=30,
            delta_working_capital=7)]))
        self.assertEqual(result['periods'][0]['fcff'], 68)

    def test_dcf_exemplo_arredondado_corretamente(self):
        result = calculos.calculate(dict(mode='dcf', cashflows=[24, 28, 32],
                                         discount_rate=Decimal('0.10'), terminal_value=0))
        # Valor exato 91840/1331 = 69,00075131480090157776108189|33… (lean/Analise/Dcf.lean).
        self.assertEqual(calculos.serialize(result['present_value']),
                         '69.00075131480090157776108189')
        self.assertEqual(calculos.serialize(result['pv_terminal']), '0')


def run(script, data, tmp):
    path = Path(tmp) / 'entrada.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    return subprocess.run([sys.executable, str(SCRIPTS / script), str(path)],
                          capture_output=True, text=True)


class ValidationTest(unittest.TestCase):
    def test_acoes_rejeita_sem_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = run('acoes.py', dict(mode='terminal_roic', nopat_next=1,
                                       discount_rate=0.1, growth=0.2, ronic=0.3), tmp)
        self.assertEqual(out.returncode, 2)
        self.assertIn('Entradas inválidas', out.stderr)
        self.assertNotIn('Traceback', out.stderr)

    def test_flags_exigem_booleano(self):
        period = dict(period='A', ebit=-10, tax_rate=Decimal('0.3'), da=0, capex=0,
                      delta_working_capital=0, loss_tax_shield='false')
        with self.assertRaises(ValueError):
            acoes.calculate(dict(mode='fcff', unit='u', periods=[period]))
        with self.assertRaises(ValueError):
            acoes.calculate(dict(mode='equity_bridge', cashflow_type='fcfe', present_value=10,
                                 shares=1, money_scale=1, unit_composition=2,
                                 equal_economic_rights='true'))

    def test_ronic_e_alias_roic(self):
        base = dict(mode='terminal_roic', nopat_next=100, discount_rate=Decimal('0.10'),
                    growth=Decimal('0.03'))
        novo = acoes.calculate(dict(base, ronic=Decimal('0.15')))
        antigo = acoes.calculate(dict(base, roic=Decimal('0.15')))
        self.assertEqual(novo, antigo)
        with self.assertRaises(ValueError):
            acoes.calculate(dict(base, ronic=Decimal('0.15'), roic=Decimal('0.15')))

    def test_coerencia_gordon_ronic(self):
        base = dict(mode='dcf', discount_rate=Decimal('0.10'), terminal_growth=Decimal('0.03'),
                    terminal_nopat=103, ronic=Decimal('0.15'))
        # 80 × 1,03 = 103 × (1 − 0,03/0,15) = 82,4
        ok = calculos.calculate(dict(base, cashflows=[60, 80]))
        self.assertEqual(ok['terminal_check']['status'], 'coerente')
        self.assertEqual(ok['terminal_check']['reinvestment_gap'], 0)
        # Fluxo arredondado: diferença de 0,05 p.p. no reinvestimento, dentro de 0,1 p.p.
        near = calculos.calculate(dict(base, cashflows=[60, Decimal('80.05')]))
        self.assertEqual(near['terminal_check']['reinvestment_gap'], Decimal('0.0005'))
        with self.assertRaises(ValueError):
            calculos.calculate(dict(base, cashflows=[60, Decimal('80.05')],
                                    terminal_tolerance=Decimal('0.0001')))
        with self.assertRaises(ValueError):  # 27,9% implícito contra 20% exigido
            calculos.calculate(dict(base, cashflows=[60, 70], terminal_nopat=100))

    def test_terminal_sem_verificacao_fica_marcado(self):
        result = calculos.calculate(dict(mode='dcf', cashflows=[60, 80],
                                         discount_rate=Decimal('0.10'),
                                         terminal_growth=Decimal('0.03')))
        self.assertEqual(result['terminal_check'], dict(status='não verificado'))
        with self.assertRaises(ValueError):
            calculos.calculate(dict(mode='dcf', cashflows=[60, 80],
                                    discount_rate=Decimal('0.10'),
                                    terminal_growth=Decimal('0.03'),
                                    terminal_tolerance=Decimal('0.01')))


if __name__ == '__main__':
    unittest.main()
