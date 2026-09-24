"""Testes do verificador de entradas. Executar: python3 -m unittest discover -s tests"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / 'scripts'))
import entradas  # noqa: E402

EXEMPLO = json.loads((RAIZ / 'examples' / 'entradas.json').read_text(encoding='utf-8'))


def com(**alteracoes):
    """Exemplo com alterações em entradas[i]: com(i0={'data': ...})."""
    dados = copy.deepcopy(EXEMPLO)
    for chave, campos in alteracoes.items():
        item = dados['entradas'][int(chave[1:])]
        for campo, valor in campos.items():
            if valor is ...:
                del item[campo]
            else:
                item[campo] = valor
    return entradas.verificar(dados)


class EntradasTest(unittest.TestCase):
    def test_exemplo_aprovado(self):
        self.assertEqual(entradas.verificar(EXEMPLO), dict(erros=[], alertas=[]))

    def test_rejeita_campo_ausente_ou_vazio(self):
        for campo in entradas.CAMPOS:
            with self.subTest(campo=campo):
                self.assertTrue(com(i1={campo: ...})['erros'])
                self.assertTrue(com(i1={campo: '  '})['erros'])

    def test_rejeita_natureza_escala_data_e_valor_invalidos(self):
        self.assertTrue(com(i1={'natureza': 'chute'})['erros'])
        self.assertTrue(com(i1={'escala': 'dezenas'})['erros'])
        self.assertTrue(com(i1={'data': '31/12/2025'})['erros'])
        self.assertTrue(com(i1={'valor': '120'})['erros'])
        self.assertTrue(com(i1={'valor': float('nan')})['erros'])
        self.assertTrue(com(i1={'valor': ...})['erros'])
        self.assertTrue(com(i2={'nome': 'ebit_ano_1'})['erros'])

    def test_aceita_acentos_e_singular(self):
        resultado = com(i1={'natureza': 'Orientação', 'escala': 'Milhão'})
        self.assertEqual(resultado, dict(erros=[], alertas=[]))

    def test_alerta_preco_fora_da_data_base(self):
        resultado = com(i0={'data': '2026-06-29'})
        self.assertEqual(resultado['erros'], [])
        self.assertIn('diferente da data-base', resultado['alertas'][0])

    def test_alerta_escala_diferente_das_demonstracoes(self):
        resultado = com(i1={'escala': 'mil'})
        self.assertIn('diferente das demonstrações', resultado['alertas'][0])
        dados = copy.deepcopy(EXEMPLO)
        del dados['escala_demonstracoes']
        dados['entradas'][1]['escala'] = 'mil'
        self.assertIn('escalas diferentes', entradas.verificar(dados)['alertas'][0])

    def test_alerta_publicacao_posterior_a_data_base(self):
        # DFP de 2025 publicada em março de 2026 não existia em 31/01/2026.
        dados = copy.deepcopy(EXEMPLO)
        dados['data_base'] = '2026-01-31'
        dados['entradas'] = [dados['entradas'][1]]
        resultado = entradas.verificar(dados)
        self.assertEqual(resultado['erros'], [])
        self.assertIn('após a data-base', resultado['alertas'][0])

    def test_orientacao_sobre_periodo_futuro_nao_alerta(self):
        resultado = com(i1={'natureza': 'orientacao', 'data': '2027-12-31',
                            'publicacao': '2026-05-15'})
        self.assertEqual(resultado, dict(erros=[], alertas=[]))

    def test_publicacao_exigida_para_observado_e_orientacao(self):
        self.assertIn('exige publicacao', com(i1={'publicacao': ...})['erros'][0])
        self.assertIn('exige publicacao',
                      com(i1={'natureza': 'orientacao', 'publicacao': ...})['erros'][0])
        self.assertTrue(com(i1={'publicacao': '27/03/2026'})['erros'])
        self.assertEqual(com(i4={'data': '2026-07-01'})['erros'], [])  # premissa

    def test_observado_nao_publicado_antes_da_data(self):
        self.assertIn('antes da data observada', com(i1={'publicacao': '2025-11-30'})['erros'][0])

    def test_alerta_valor_nulo(self):
        self.assertIn('não substituir por zero', com(i4={'valor': None})['alertas'][0])

    def test_codigos_de_saida(self):
        def rodar(dados, *opcoes):
            with tempfile.TemporaryDirectory() as tmp:
                caminho = Path(tmp) / 'entradas.json'
                caminho.write_text(json.dumps(dados, ensure_ascii=False), encoding='utf-8')
                return subprocess.run([sys.executable, str(RAIZ / 'scripts' / 'entradas.py'),
                                       str(caminho), *opcoes], capture_output=True).returncode
        alerta = copy.deepcopy(EXEMPLO)
        alerta['entradas'][0]['data'] = '2026-06-29'
        erro = copy.deepcopy(EXEMPLO)
        del erro['entradas'][0]['fonte']
        self.assertEqual(rodar(EXEMPLO), 0)
        self.assertEqual(rodar(alerta), 0)
        self.assertEqual(rodar(alerta, '--estrito'), 1)
        self.assertEqual(rodar(erro), 2)


if __name__ == '__main__':
    unittest.main()
