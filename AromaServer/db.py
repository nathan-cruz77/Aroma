# Aroma DB Interface

import json
import sqlite3 as sql
import uuid
import logging

_DB_FILE = 'aroma.db'
logger = logging.getLogger(__name__)


def _sql_to_dict(keys, sql_list):
    result = {'data': []}

    for x in sql_list:
        aux = {}
        for y, elemento in enumerate(x):
            aux[keys[y]] = elemento
        result['data'].append(aux)

    return result


def _new_id():
    return str(uuid.uuid4())


def _get_connection():
    return sql.connect(_DB_FILE)


def comprar(dados):
    with _get_connection() as con:
        cursor = con.cursor()
        par = dados['data'][0]
        for par in dados['data']:
            cursor.execute('''UPDATE Produtos SET estoque = estoque + ?
                           WHERE id = ?''',
                           (par['quantidade'], par['produto']['id']))
    return {'transaction': 'done'}


def insere_venda(json_data):
    nova_venda_id = _new_id()

    logger.warn('json_data[\'time\'] = {}'.format(json_data['time']))

    with _get_connection() as con:
        cursor = con.cursor()
        cursor.execute('''INSERT INTO Vendas (id, data) VALUES (?, ?)''',
                       (nova_venda_id, json_data['time']))
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
    with _get_connection() as con:
        cursor = con.cursor()
        result = cursor.execute('''SELECT * FROM Produtos''').fetchall()
        keys = [description[0] for description in cursor.description]
    return _sql_to_dict(keys, result)


def recupera_produto(prod_id):
    with _get_connection() as con:
        cursor = con.cursor()
        result = cursor.execute('''SELECT * FROM Produtos WHERE id = ?''', prod_id).fetchall()
        keys = [descricao[0] for description in cursor.description]
    return _sql_to_dict(keys, result)


def posta_produto(produto):

    def altera_produto(produto):
        with _get_connection() as con:
            cursor = con.cursor()
            cursor.execute('''UPDATE Produtos SET nome = ?,
                                                  preco_compra = ?,
                                                  preco_venda = ?
                            WHERE id = ?''', (produto['nome'], produto['preco_compra'],
                            produto['preco_venda'], produto['id']))
        return {'product_id': produto['id']}

    def insere_produto(produto):
        new_id = _new_id()
        with _get_connection() as con:
            cursor = con.cursor()
            cursor.execute(
                '''INSERT INTO Produtos (id, nome, preco_compra, preco_venda, estoque)
                    VALUES (?, ?, ?, ?, ?)''',
                    (new_id, produto['nome'],
                     produto['preco_compra'],
                     produto['preco_venda'], 0)
            )
        return {'product_id': new_id}

    if 'id' not in produto.keys():
        produto['id'] = ''

    with _get_connection() as con:
        cursor = con.cursor()
        result = cursor.execute('''SELECT * FROM Produtos WHERE id = ?''',
                                (produto['id'],)).fetchone()
    if result is None:
        return insere_produto(produto)

    return altera_produto(produto)


def remove_produto(prod_id):
    with _get_connection() as con:
        cursor = con.cursor()
        cursor.execute('''DELETE FROM Produtos WHERE id = ?''', (prod_id,))

    return {'transaction': 'done'}

def vendas():
    with _get_connection() as con:
        cursor = con.cursor()
        result = cursor.execute('''SELECT v.data, vp.quantidade*p.preco_venda
                                   FROM Vendas v
                                   JOIN VendaProduto vp, Produtos p
                                   ON v.id = vp.venda_id
                                   AND p.id = vp.produto_id
                                   ORDER BY data DESC LIMIT 10''').fetchall()
        keys = ['data', 'total']
        return _sql_to_dict(keys, result)
