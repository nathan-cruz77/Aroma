import json
import logging

from flask import Flask
from flask import jsonify
from flask import request
from flask import render_template
from flask import send_from_directory

from db import recupera_produtos
from db import posta_produto as db_posta_produto
from db import remove_produto
from db import comprar as db_comprar_produto
from db import insere_venda
from db import vendas

app = Flask(__name__)
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/ultimas_vendas', methods=['GET'])
def ultimas_vendas():
    return jsonify(vendas())


@app.route('/login/<credenciais>')
def login(credenciais):
    return jsonify({'token': '3d2a1s32da65sd4asd'})


@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if request.method == 'GET':
        todos_produtos = recupera_produtos()
        logger.warn(json.dumps(todos_produtos))
        return jsonify(todos_produtos)
    json_request_as_str = request.data.decode()
    return posta_produto(json_request_as_str)


@app.route('/produtos/<prod_id>', methods=['DELETE'])
def produto(prod_id):
    return jsonify(remove_produto(prod_id))


@app.route('/compra', methods=['POST'])
def registra_compra():
    json_request_as_str = request.data.decode()
    return jsonify(db_comprar_produto(json.loads(json_request_as_str)))


@app.route('/venda', methods=['POST'])
def venda():
    def recupera_vendas():
        pass
    def registra_venda(request_data):
        return jsonify(insere_venda(request_data))

    resposta = {
        'GET': recupera_vendas,
        'POST': registra_venda
    }

    json_request_as_str = request.data.decode()
    return resposta[request.method](json.loads(json_request_as_str))


def posta_produto(produto):
    resp = db_posta_produto(json.loads(produto))
    return jsonify(resp)


@app.after_request
def acrescenta_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    return response

if __name__ == '__main__':
    app.run(debug=True)
