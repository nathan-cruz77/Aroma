CREATE TABLE IF NOT EXISTS Vendas(
    id TEXT,
    data TEXT,
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS Produtos(
    id TEXT,
    nome TEXT,
    preco_compra REAL,
    preco_venda REAL,
    estoque INTEGER,
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS VendaProduto(
    venda_id TEXT,
    produto_id TEXT,
    quantidade INTEGER,
    PRIMARY KEY(venda_id, produto_id),
    FOREIGN KEY(venda_id) REFERENCES Vendas(id),
    FOREIGN KEY(produto_id) REFERENCES Produtos(id)
);

CREATE TABLE IF NOT EXISTS Usuarios(
    id TEXT,
    nome TEXT,
    username TEXT,
    password TEXT,
    email TEXT,
    PRIMARY KEY(id)
);
