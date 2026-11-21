import unittest
from unittest.mock import MagicMock, call, patch

from banco import BancoComLimite, BancoNeon


class TestBanco(unittest.TestCase):
    def test_url_obrigatoria(self):
        with self.assertRaises(ValueError):
            BancoNeon("")

    def test_heranca_e_limite(self):
        banco = BancoComLimite("postgresql://teste")
        self.assertIsInstance(banco, BancoNeon)
        for quantidade in (0, 3, 10, 25):
            with self.subTest(quantidade=quantidade):
                linhas = [{"id": i} for i in range(quantidade)]
                with patch.object(banco, "_executar", return_value=linhas):
                    self.assertEqual(banco.consultar("SELECT * FROM exemplo"), linhas[:10])

    def test_banco_base_sem_limite(self):
        banco = BancoNeon("postgresql://teste")
        linhas = [{"id": i} for i in range(25)]
        with patch.object(banco, "_executar", return_value=linhas):
            self.assertEqual(len(banco.consultar("SELECT * FROM exemplo")), 25)

    def test_rejeita_comandos_de_escrita_antes_de_conectar(self):
        banco = BancoComLimite("postgresql://teste")
        with patch.object(banco, "_executar") as executar:
            for comando in ("DELETE FROM exemplo", "DROP TABLE exemplo", "SET transaction_read_only=off", ""):
                with self.subTest(comando=comando), self.assertRaises(ValueError):
                    banco.consultar(comando)
            executar.assert_not_called()

    def test_contagem_total_e_identificador_escapado(self):
        banco = BancoComLimite("postgresql://teste")
        tabela = 'nome " especial'
        with patch.object(banco, "listar_tabelas", return_value=[tabela]):
            with patch.object(banco, "_executar", return_value=[{"total": 94}]) as executar:
                self.assertEqual(banco.contar_linhas(tabela), 94)
                self.assertEqual(
                    executar.call_args.args[0].as_string(),
                    'SELECT COUNT(*) AS total FROM "public"."nome "" especial"',
                )

    def test_rejeita_tabela_inexistente_ou_injecao(self):
        banco = BancoNeon("postgresql://teste")
        with patch.object(banco, "listar_tabelas", return_value=["exemplo"]):
            with patch.object(banco, "_executar") as executar:
                with self.assertRaises(ValueError):
                    banco.contar_linhas("exemplo; DROP TABLE exemplo")
                executar.assert_not_called()

    def test_metadados_completos_apesar_do_limite(self):
        banco = BancoComLimite("postgresql://teste")
        tabelas = [{"table_name": f"t{i}"} for i in range(12)]
        colunas = [{"coluna": f"c{i}", "tipo": "integer"} for i in range(15)]
        with patch.object(banco, "_executar", side_effect=[tabelas, colunas]) as executar:
            self.assertEqual(len(banco.listar_tabelas()), 12)
            self.assertEqual(len(banco.descrever_tabela("t0")), 15)
            self.assertEqual(executar.call_args.args[1], ("t0",))

    def test_conexao_somente_leitura_e_fechamento(self):
        conexao = MagicMock()
        conexao.__enter__.return_value = conexao
        cursor = conexao.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value = [{"n": 1}]
        with patch("banco.psycopg.connect", return_value=conexao) as conectar:
            self.assertEqual(BancoNeon("postgresql://teste").consultar("SELECT 1 AS n"), [{"n": 1}])

        conectar.assert_called_once_with("postgresql://teste", connect_timeout=10)
        self.assertIs(conexao.read_only, True)
        self.assertEqual(cursor.execute.call_args_list, [
            call("SET LOCAL statement_timeout = '15s'"),
            call("SET LOCAL search_path = public"),
            call("SELECT 1 AS n", None, prepare=True),
        ])
        conexao.__exit__.assert_called_once()

    def test_fecha_conexao_se_configuracao_da_transacao_falhar(self):
        conexao = MagicMock()
        conexao.__enter__.return_value = conexao
        cursor = conexao.cursor.return_value.__enter__.return_value
        cursor.execute.side_effect = RuntimeError("Configuração indisponível")
        with patch("banco.psycopg.connect", return_value=conexao):
            with self.assertRaises(RuntimeError):
                BancoNeon("postgresql://teste").consultar("SELECT 1 AS n")
        conexao.__exit__.assert_called_once()


if __name__ == "__main__":
    unittest.main()
