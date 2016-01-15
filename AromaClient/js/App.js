'use strict';

var BASE_URL = 'http://localhost:5000'

/* Main module */
var app = angular.module('Main', ['ngCookies', 'ngRoute']);

/* Configure app routes */
app.config(function($routeProvider, $locationProvider){
    $locationProvider.hashPrefix('!');
    $routeProvider.
        when('/', {templateUrl: 'templates/login.html'}).
        when('/home', {templateUrl: 'templates/home.html'}).
        when('/venda', {templateUrl: 'templates/venda.html'}).
        when('/compra', {templateUrl: 'templates/compra.html'}).
        when('/produtos', {templateUrl: 'templates/produtos.html'}).
        when('/erro', {templateUrl: 'templates/erro.html'}).
        otherwise({redirectTo: '/erro'});
});

/* Service to handle all the requests to the API */
app.factory('json_request', ['$http',
function($http){
    return function(metodo, url, dados){
        if(typeof dados === 'undefined'){
            dados = {};
        }

        url = BASE_URL + url;
        console.log('Fazendo request para ' + url);

        return $http({
                method: metodo, url: url,
                headers: {'Content-Type': 'application/json'},
                data: dados
        });
    }
}]);

/* Returns now in unix time */
app.factory('now_in_unix', [
function(){
    return function(){
        return Math.round((new Date()).getTime() / 1000);
    }
}]);

/* Controller for the '/compra' page */
app.controller('CompraController', ['$scope', '$location', 'json_request',
function($scope, $location, json_request){
    json_request('GET', '/produtos').then(
        function sucesso(response){
            console.log('Recebida lista de produtos');
            $scope.todos_produtos = response.data.data;
        },
        function erro(response){
            console.log('Erro ao buscar a lista os produtos');
        }
    );

    $scope.itens_comprados = [];
    $scope.itens_comprados.push({produto: {}, quantidade: 0});

    $scope.total = 0;

    $scope.adicionaEntrada = function(){
        $scope.itens_comprados.push({produto: {}, quantidade: 0});
    }

    $scope.removeEntrada = function(produto_quantidade){

        var chave_a_ser_removida = 0;

        for(var i = 0; i < $scope.itens_comprados.length; i++){
            if($scope.itens_comprados[i].produto.id === produto_quantidade.produto.id){
                chave_a_ser_removida = i;
                i = $scope.itens_comprados.length;
            }
        }

        if($scope.itens_comprados.length > 1){
            $scope.itens_comprados.splice(chave_a_ser_removida, 1);
        }
        else if($scope.itens_comprados.length == 1){
            produto_quantidade.produto = {};
            produto_quantidade.quantidade = 0;
        }

        $scope.recalculaTotal();
    }

    $scope.finalizaCompra = function(){
        json_request('POST', '/compra', {data: $scope.itens_comprados}).then(
            function sucesso(response){
                console.log('Compra feita com sucesso');
                $scope.itens_comprados = [];
                $scope.itens_comprados.push({produto: {}, quantidade: 0});

                $scope.total = 0;
            },
            function erro(response){
                console.log('Erro ao fazer a compra');
            }
        );
    }

    $scope.gotoHome = function(){
        $location.path('/home');
    }

    $scope.recalculaTotal = function(){
        var total = 0;
        var preco;
        var quantidade;

        $scope.total = total;
        for(var i = 0; i < $scope.itens_comprados.length; i++){
            preco = $scope.itens_comprados[i].produto.preco_compra;
            quantidade = $scope.itens_comprados[i].quantidade;

            if(preco === 'undefined')
                preco = 0;

            if(quantidade === 'undefined')
                quantidade = 0;

            total += preco * quantidade;
        }

        if(isNaN(total)){
            $scope.total = 0;
        }
        else {
            $scope.total = total;
        }
    }

}]);

/* Contoller for the '/home' page */
app.controller('HomeController', ['$scope', 'json_request',
function($scope, json_request){
    json_request('GET', '/ultimas_vendas').then(
        function sucesso(response){
            var date;
            var dia, mes, ano;
            var hora, minuto;
            var aux;
            var total;
            $scope.ultimas_vendas = [];

            for(var i = 0; i<  response.data.data.length; i++){
                date = new Date(response.data.data[i].data*1000);

                dia = date.getDate();
                mes = date.getMonth();
                ano = date.getFullYear();

                hora = date.getHours();
                minuto = date.getMinutes();

                if(dia <= 9)
                    dia = '0' + dia;

                if(mes <= 9)
                    mes = '0' + mes;

                if(hora <= 9)
                    hora = '0' + hora;

                if(minuto <= 9)
                    minuto = '0' + minuto;

                aux = {
                    data: dia + '/' + mes + '/' + ano,
                    hora_min: hora + ':' + minuto,
                    total: response.data.data[i].total
                }

                $scope.ultimas_vendas.push(aux);
            }
        },
        function error(response){
            console.log('Erro na mensagem');
        }
    );
}]);

/* Controller for the '/produtos' page */
app.controller('ProdutosController', ['$scope', 'json_request',
function($scope, json_request){

    json_request('GET', '/produtos').then(
        function sucesso(response){
            console.log('Recebida lista de proutos');
            $scope.todos_produtos = response.data.data;
        },
        function erro(response){
            console.log('Erro');
        }
    );

    $scope.novoProduto = {};
    $scope.sortBy = 'nome';

    function remove_entrada(produto){

        var chave_a_ser_removida = 0;

        for(var i = 0; i < $scope.todos_produtos.length; i++){
            if($scope.todos_produtos[i].id === produto.id){
                chave_a_ser_removida = i;
                i = $scope.todos_produtos.length;
            }
        }

        if($scope.todos_produtos.length > 1){
            $scope.todos_produtos.splice(chave_a_ser_removida, 1);
        }

    }

    $scope.adicionaProduto = function(produto){

        json_request('POST', '/produtos', produto).then(
            function(response){
                console.log('Adicionado produto:' +
                    '{ id = ' + produto.id + ', ' +
                    ' nome = ' + produto.nome + ', ' +
                    ' preco_compra = ' + produto.preco_compra + ', ' +
                    ' preco_venda = ' + produto.preco_venda + ', ' +
                    ' estoque = ' + produto.estoque + '}'
                );

                if(typeof produto.id === 'undefined'){
                    produto.estoque = 0;
                    produto.id = response.data.product_id;
                    $scope.todos_produtos.push(produto);
                }
                else{
                    for(var i = 0; i < $scope.todos_produtos.length; i++){
                        if($scope.todos_produtos[i].id === produto.id){
                            produto.estoque = $scope.todos_produtos[i].estoque;
                            $scope.todos_produtos[i] = produto;
                        }
                    }
                }
            },
            function(response) {
                console.log('Erro adicionando novo produto: ' + produto);
            }
        );

        $scope.novoProduto = {}
    }

    $scope.edita_produto = function(produto){

        $scope.novoProduto.id = produto.id;
        $scope.novoProduto.nome = produto.nome;
        $scope.novoProduto.preco_compra = produto.preco_compra;
        $scope.novoProduto.preco_venda = produto.preco_venda;

        $window.document.getElementById('form_produtos').focus();

    }

    $scope.remove_produto = function(produto){

        json_request('DELETE', '/produtos/' + produto.id, {}).then(
            function sucesso(response){
                console.log('Produto removido com sucesso');
            },
            function erro(response){
                console.log('Erro ao remover produto');
            }
        );

        remove_entrada(produto);
    }

    $scope.get_sortBy = function(){
        return $scope.sortBy;
    }

}]);

/* Controller for the '/venda' page */
app.controller('VendaController', ['$scope', 'json_request', 'now_in_unix',
function($scope, json_request, now_in_unix){

    function carrega_produtos(){
        json_request('GET', '/produtos').then(
            function sucesso(response){
                console.log('Recebida lista de produtos');
                $scope.todos_produtos = response.data.data;
            },
            function erro(response){
                console.log('Erro ao buscar a lista os produtos');
            }
        );
    }

    carrega_produtos();

    $scope.itens_vendidos = [];
    $scope.itens_vendidos.push({produto: {}, quantidade: 0});

    $scope.total = 0;

    $scope.adicionaEntrada = function(){
        $scope.itens_vendidos.push({produto: {}, quantidade: 0});
    }

    $scope.removeEntrada = function(produto_quantidade){

        var chave_a_ser_removida = 0;

        for(var i = 0; i < $scope.itens_vendidos.length; i++){
            if($scope.itens_vendidos[i].produto.id === produto_quantidade.produto.id){
                chave_a_ser_removida = i;
                i = $scope.itens_vendidos.length;
            }
        }

        if($scope.itens_vendidos.length > 1){
            $scope.itens_vendidos.splice(chave_a_ser_removida, 1);
        }
        else if($scope.itens_vendidos.length == 1){
            produto_quantidade.produto = {};
            produto_quantidade.quantidade = 0;
        }

        $scope.recalculaTotal();
    }

    $scope.finalizaVenda = function(){
        var venda_dados = {data: $scope.itens_vendidos, time: now_in_unix()};
        console.log("venda_dados = {data: " + venda_dados.data + ", time" + venda_dados.time + "}");
        json_request('POST', '/venda', venda_dados).then(
            function sucesso(response){
                console.log('Venda feita com sucesso');
                $scope.itens_vendidos = [];
                $scope.itens_vendidos.push({produto: {}, quantidade: 0});
                $scope.total = 0;

                carrega_produtos();
            },
            function erro(response){
                console.log('Erro ao fazer a compra');
            }
        );
    }

    $scope.gotoHome = function(){
        $location.path('/home');
    }

    $scope.recalculaTotal = function(){
        var total = 0;
        var preco;
        var quantidade;

        $scope.total = total;
        for(var i = 0; i < $scope.itens_vendidos.length; i++){
            preco = $scope.itens_vendidos[i].produto.preco_compra;
            quantidade = $scope.itens_vendidos[i].quantidade;

            if(preco === 'undefined')
                preco = 0;

            if(quantidade === 'undefined')
                quantidade = 0;

            total += preco * quantidade;
        }

        if(isNaN(total)){
            $scope.total = 0;
        }
        else {
            $scope.total = total;
        }
    }

}]);

/* Controlle for the '/login' page */
app.controller('Auth', ['$cookies', '$scope', '$location',
function($scope, $cookies){

    function cookie_validity(){
        var now = Number(Date());

        if($scope.keep_on)
            return now + (180 * 24 * 60 * 60); // 6 months ahead
        return now + (30 * 24 * 60 * 60); // 1 month ahead
    }

    function credentials_encode(usuario, senha){
        // Return string in format 'login:password' encoded in base64
        // with url_safe
        console.log('Running Base64.encode(' + usuario + ':' + senha + ')');
        return Base64.encode(usuario + ':' + senha);
    }

    // Should be the function being used, lol
    $scope.login_test = function(){
        /*
        var test = credentials_encode($scope.usuario, $scope.senha);
        console.log(test);
        var login_url = 'http://localhost:5000/login/' + test;

        $http.get(login_url).then(
            function success(response){
                if(response.data.token != ''){
                    console.log('response: ' + response.data.token);
                    $cookies.put('token', response.data.token,
                                {expires: cookie_validity * 1000});
                    //$location.path('/home');
                }
                else{
                    // Unable to login with given credentials
                    //$location.path('/login')
                    console.log('Unable to login with given credentials');
                }
            },
            function error(response){
                console.log('A network error happened. request: ' + response.data);
            }
        );*/
    }

    $scope.login = function(){
        $location.path('/home');
    }

}]);
