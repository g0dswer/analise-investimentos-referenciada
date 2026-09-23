"""Testes dos helpers de cálculo. Executar: python3 -m unittest discover -s tests"""
import random
import sys
import unittest
from decimal import Decimal
from fractions import Fraction
from math import floor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
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

    def test_dcf_exemplo_proximo_do_valor_exato(self):
        result = calculos.calculate(dict(mode='dcf', cashflows=[24, 28, 32],
                                         discount_rate=Decimal('0.10'), terminal_value=0))
        # Valor exato 91840/1331 (lean/Analise/Dcf.lean).
        self.assertLess(abs(Fraction(result['present_value']) - Fraction(91840, 1331)),
                        Fraction(1, 10**25))


if __name__ == '__main__':
    unittest.main()
