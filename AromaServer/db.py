# Aroma DB Interface

import json
import sqlite3 as sql
import uuid
import logging
import collections
import datetime

_DB_FILE = 'AromaServer/aroma.db'
logger = logging.getLogger(__name__)


def _sql_to_dict(keys, sql_list):
    if not isinstance(keys, collections.Iterable) or isinstance(keys, str):
        raise TypeError('Unable to dictify with single key')

    if not isinstance(sql_list, collections.Iterable) or isinstance(sql_list, str):
        raise TypeError('Unable to dictify non iterable result list')

    result = {'data': []}

    for x in sql_list:

        if len(x) != len(keys):
            raise ValueError('Unable to dictify, keys list of different size than result list')

        aux = {keys[y]: elemento for y, elemento in enumerate(x)}
        result['data'].append(aux)

    return result


def _new_id():
    return str(uuid.uuid4())


def get_connection():
    return sql.connect(_DB_FILE)


def comprar(dados):
    with get_connection() as con:
        cursor = con.cursor()
        for par in dados['data']:
            cursor.execute('''UPDATE Produtos SET estoque = estoque + ?
                           WHERE id = ?''',
                           (par['quantidade'], par['produto']['id']))
    return {'transaction': 'done'}


def insere_venda(json_data):
    nova_venda_id = _new_id()

    # Este campo não está sendo gerado pela view
    data_hora = str(datetime.datetime.now())
    data_hora = data_hora.split(".")[0]

    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute('''INSERT INTO Vendas (id, data) VALUES (?, ?)''',
                       (nova_venda_id, data_hora))
        for par in json_data['data']:
            cursor.execute('''UPDATE Produtos SET estoque = estoque - ? WHERE id = ?''',
                        (par['quantidade'], par['produto']['id']))
            cursor.execute('''INSERT OR REPLACE INTO VendaProduto
                           (venda_id, produto_id, quantidade) VALUES
                           (
                            ?,
                            ?,
                            COALESCE((SELECT quantidade FROM VendaProduto WHERE
                                venda_id = ? AND produto_id = ?) + ?, ?)
                           )''', (nova_venda_id, par['produto']['id'],
                                  nova_venda_id, par['produto']['id'], par['quantidade'],
                                  par['quantidade'])
                            )

    return {'venda_id': nova_venda_id}



def recupera_produtos():
    with get_connection() as con:
        cursor = con.cursor()
        result = cursor.execute('''SELECT * FROM Produtos''').fetchall()
        keys = [description[0] for description in cursor.description]
    return _sql_to_dict(keys, result)


def recupera_produto(prod_id):
    with get_connection() as con:
        cursor = con.cursor()
        result = cursor.execute('''SELECT * FROM Produtos WHERE id = ?''', prod_id).fetchall()
        keys = [descricao[0] for description in cursor.description]
    return _sql_to_dict(keys, result)


def posta_produto(produto):

    def altera_produto(produto):
        with get_connection() as con:
            cursor = con.cursor()
            cursor.execute('''UPDATE Produtos SET nome = ?,
                                                  preco_compra = ?,
                                                  preco_venda = ?
                            WHERE id = ?''', (produto['nome'], produto['preco_compra'],
                            produto['preco_venda'], produto['id']))
        return {'product_id': produto['id']}

    def insere_produto(produto):
        new_id = _new_id()

        novo_produto = (
            new_id, produto['nome'],
            produto['preco_compra'],
            produto['preco_venda'],
            0
        )

        with get_connection() as con:
            cursor = con.cursor()
            cursor.execute(
                '''INSERT INTO Produtos (id, nome, preco_compra, preco_venda, estoque)
                    VALUES (?, ?, ?, ?, ?)''', novo_produto
            )
        return {'product_id': new_id}

    if 'id' not in produto.keys():
        produto['id'] = ''

    with get_connection() as con:
        cursor = con.cursor()
        result = cursor.execute('''SELECT * FROM Produtos WHERE id = ?''',
                                (produto['id'],)).fetchone()
    if result is None:
        return insere_produto(produto)

    return altera_produto(produto)


def remove_produto(prod_id):
    with get_connection() as con:
        cursor = con.cursor()
        cursor.execute('''DELETE FROM Produtos WHERE id = ?''', (prod_id,))

    return {'transaction': 'done'}

def vendas():
    with get_connection() as con:
        cursor = con.cursor()
        result = cursor.execute('''SELECT v.data, vp.quantidade*p.preco_venda
                                   FROM Vendas v
                                   JOIN VendaProduto vp, Produtos p
                                   ON v.id = vp.venda_id
                                   AND p.id = vp.produto_id
                                   ORDER BY data DESC LIMIT 10''').fetchall()
        keys = ['data', 'total']
        return _sql_to_dict(keys, result)
