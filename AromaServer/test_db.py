import unittest
import logging

from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import call

from db import _sql_to_dict as sql_to_dict
from db import _new_id as new_id
from db import _get_connection as get_connection
from db import comprar as comprar_produtos

LOGGER = logging.getLogger(__name__)


class DummyConnection:

    def cursor(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


CONN = DummyConnection()


class DbTest(unittest.TestCase):

    def test_sql_to_dict(self):
        keys_given = ['a', 'b', 'c', 'd']
        sql_result_given = [('AA', 'BB', 'CC', 'DD')]
        expected = {'data': [{'a': 'AA', 'b': 'BB', 'c': 'CC', 'd': 'DD'}]}
        self.assertEqual(sql_to_dict(keys_given, sql_result_given), expected)

        keys_given = []
        sql_result_given = [('asdasd', 'asdasdad')]
        self.assertRaises(ValueError, sql_to_dict, keys_given, sql_result_given)

        keys_given = ['a', 'b']
        sql_result_given = [('asdasd', 'asdasdad'), ('adasd',)]
        self.assertRaises(ValueError, sql_to_dict, keys_given, sql_result_given)

        keys_given = ['a', 'b', 'c', 'd']
        sql_result_given = [['AA', 'BB', 'CC', 'DD']]
        expected = {'data': [{'a': 'AA', 'b': 'BB', 'c': 'CC', 'd': 'DD'}]}
        self.assertEqual(sql_to_dict(keys_given, sql_result_given), expected)

        keys_given = 'abcd'
        sql_result_given = [['AA', 'BB', 'CC', 'DD']]
        self.assertRaises(TypeError, sql_to_dict, keys_given, sql_result_given)

    def test_new_id(self):
        for time in range(20):
            self.assertIsInstance(new_id(), str)

    def test_get_connection(self):
        for i in range(20):
            with get_connection() as con:
                self.assertIsNot(con, None)

    @patch('db._get_connection')
    def test_comprar_produtos(self, mock_connection):
        mock_connection.return_value = CONN
        CONN.execute = MagicMock(return_value='Something')

        given = {'data':[
            {'produto': {'id': 'coxinha'}, 'quantidade': 2},
            {'produto': {'id': 'esfiha'}, 'quantidade': 5},
            {'produto': {'id': 'bauru'}, 'quantidade': 1},
        ]}

        first_arg = 'UPDATE Produtos SET estoque = estoque + ?\n                           WHERE id = ?'
        expected = []
        expected.append(call(first_arg, (2, 'coxinha')))
        expected.append(call(first_arg, (5, 'esfiha')))
        expected.append(call(first_arg, (1, 'bauru')))

        # LOGGER.warning(expected)
        comprar_produtos(given)
        # LOGGER.warning(CONN.execute.call_args_list)

        self.assertEqual(expected, CONN.execute.call_args_list)

if __name__ == '__main__':
    unittest.main()
