#!/usr/bin/env python3
"""Verificar a proveniência das entradas de uma análise. Não acessa a rede nem corrige dados."""
import argparse
import json
import re
import unicodedata
from datetime import date
from decimal import Decimal
from pathlib import Path

CAMPOS = ('fonte', 'data', 'unidade', 'escala', 'natureza')
NATUREZAS = ('observado', 'orientacao', 'premissa', 'calculado')
ESCALAS = ('unidade', 'mil', 'milhoes', 'bilhoes')
TIPOS = ('preco', 'demonstracao', 'taxa', 'quantidade', 'outro')
SINONIMOS = {'milhao': 'milhoes', 'bilhao': 'bilhoes'}


def normalizar(texto):
    """Minúsculas sem acentos: "Milhões" → "milhoes", "orientação" → "orientacao"."""
    sem_acento = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode()
    chave = sem_acento.strip().lower()
    return SINONIMOS.get(chave, chave)


def data_iso(texto):
    if not isinstance(texto, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', texto):
        raise ValueError
    return date.fromisoformat(texto)


def numero_finito(valor):
    if isinstance(valor, bool) or not isinstance(valor, (int, float, Decimal)):
        return False
    return Decimal(str(valor)).is_finite()


def verificar(dados):
    erros, alertas = [], []
    if not isinstance(dados, dict):
        return dict(erros=['O arquivo deve conter um objeto JSON'], alertas=[])
    try:
        data_base = data_iso(dados.get('data_base'))
    except ValueError:
        erros.append('data_base ausente ou fora do formato AAAA-MM-DD')
        data_base = None
    escala_ref = dados.get('escala_demonstracoes')
    if escala_ref is not None:
        escala_ref = normalizar(escala_ref) if isinstance(escala_ref, str) else escala_ref
        if escala_ref not in ESCALAS:
            erros.append(f'escala_demonstracoes deve ser uma de {", ".join(ESCALAS)}')
            escala_ref = None
    entradas = dados.get('entradas')
    if not isinstance(entradas, list) or not entradas:
        erros.append('entradas deve ser uma lista não vazia')
        return dict(erros=erros, alertas=alertas)

    nomes = set()
    escalas_demonstracoes = {}
    for i, item in enumerate(entradas):
        rotulo = f'entradas[{i}]'
        if not isinstance(item, dict):
            erros.append(f'{rotulo}: deve ser um objeto')
            continue
        nome = item.get('nome')
        if not isinstance(nome, str) or not nome.strip():
            erros.append(f'{rotulo}: falta nome')
        else:
            rotulo = f'{rotulo} ({nome})'
            if nome in nomes:
                erros.append(f'{rotulo}: nome repetido')
            nomes.add(nome)

        if 'valor' not in item:
            erros.append(f'{rotulo}: falta valor; usar null para dado indisponível')
        elif item['valor'] is None:
            alertas.append(f'{rotulo}: valor indisponível (null); não substituir por zero')
        elif not numero_finito(item['valor']):
            erros.append(f'{rotulo}: valor deve ser número finito ou null')

        faltando = [c for c in CAMPOS
                    if not isinstance(item.get(c), str) or not item[c].strip()]
        if faltando:
            erros.append(f'{rotulo}: falta {", ".join(faltando)}')

        data = None
        if 'data' not in faltando:
            try:
                data = data_iso(item['data'])
            except ValueError:
                erros.append(f'{rotulo}: data fora do formato AAAA-MM-DD')
        natureza = normalizar(item['natureza']) if 'natureza' not in faltando else None
        if natureza is not None and natureza not in NATUREZAS:
            erros.append(f'{rotulo}: natureza deve ser uma de {", ".join(NATUREZAS)}')
        escala = normalizar(item['escala']) if 'escala' not in faltando else None
        if escala is not None and escala not in ESCALAS:
            erros.append(f'{rotulo}: escala deve ser uma de {", ".join(ESCALAS)}')
            escala = None
        tipo = item.get('tipo')
        if tipo is not None:
            tipo = normalizar(tipo) if isinstance(tipo, str) else tipo
            if tipo not in TIPOS:
                erros.append(f'{rotulo}: tipo deve ser um de {", ".join(TIPOS)}')

        # `data` é o período ou dia a que o valor se refere; a disponibilidade de um
        # documento é a data de publicação, que pode ser meses depois do período.
        publicacao = None
        if natureza in ('observado', 'orientacao'):
            try:
                publicacao = data_iso(item.get('publicacao'))
            except ValueError:
                erros.append(f'{rotulo}: dado {natureza} exige publicacao no formato AAAA-MM-DD')
        elif 'publicacao' in item:
            try:
                publicacao = data_iso(item['publicacao'])
            except ValueError:
                erros.append(f'{rotulo}: publicacao fora do formato AAAA-MM-DD')
        if natureza == 'observado' and data is not None and publicacao is not None \
                and publicacao < data:
            erros.append(f'{rotulo}: publicação em {publicacao}, antes da data observada {data}')

        if data is not None and data_base is not None:
            if tipo == 'preco' and data != data_base:
                alertas.append(f'{rotulo}: preço de {data}, diferente da data-base {data_base}')
        if publicacao is not None and data_base is not None and publicacao > data_base:
            alertas.append(f'{rotulo}: publicado em {publicacao}, após a data-base '
                           f'{data_base}; indisponível na data-base')
        if tipo == 'demonstracao' and escala is not None:
            if escala_ref is not None and escala != escala_ref:
                alertas.append(f'{rotulo}: escala {escala}, diferente das demonstrações '
                               f'({escala_ref})')
            escalas_demonstracoes.setdefault(escala, []).append(nome)
    if escala_ref is None and len(escalas_demonstracoes) > 1:
        detalhe = '; '.join(f'{e}: {", ".join(map(str, n))}'
                            for e, n in sorted(escalas_demonstracoes.items()))
        alertas.append(f'Demonstrações em escalas diferentes ({detalhe}); '
                       'informar escala_demonstracoes')
    return dict(erros=erros, alertas=alertas)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='JSON com data_base, escala_demonstracoes e entradas')
    parser.add_argument('--estrito', action='store_true', help='também falhar com alertas')
    args = parser.parse_args()
    try:
        dados = json.loads(Path(args.input).read_text(encoding='utf-8'), parse_float=Decimal)
    except (OSError, ValueError) as exc:
        parser.exit(2, f'Arquivo inválido: {exc}\n')
    relatorio = verificar(dados)
    relatorio['situacao'] = ('rejeitado' if relatorio['erros']
                             else 'com alertas' if relatorio['alertas'] else 'aprovado')
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))
    if relatorio['erros']:
        raise SystemExit(2)
    if args.estrito and relatorio['alertas']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
