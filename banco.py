import re

import psycopg
from psycopg import sql
from psycopg.rows import dict_row


class BancoNeon:
    def __init__(self, url_conexao: str):
        if not url_conexao:
            raise ValueError("Defina DATABASE_URL (ou NEON) no arquivo .env.")
        self.url_conexao = url_conexao

    def _conectar(self):

        conexao = psycopg.connect(
            self.url_conexao,
            connect_timeout=10,
        )
        conexao.read_only = True
        return conexao

    def _executar(self, consulta, parametros=None, limite=None) -> list[dict]:
        with self._conectar() as conexao:
            with conexao.cursor(row_factory=dict_row) as cursor:


                cursor.execute("SET LOCAL statement_timeout = '15s'")
                cursor.execute("SET LOCAL search_path = public")

                cursor.execute(consulta, parametros, prepare=True)
                return cursor.fetchall() if limite is None else cursor.fetchmany(limite)

    def consultar(self, sql: str) -> list[dict]:

        if not re.match(r"^\s*(SELECT|WITH)\b", sql, re.IGNORECASE):
            raise ValueError("Envie somente uma consulta SELECT ou WITH ... SELECT.")
        return self._executar(sql)

    def listar_tabelas(self) -> list[str]:

        linhas = self._executar("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        return [linha["table_name"] for linha in linhas]

    def descrever_tabela(self, tabela: str) -> list[dict]:

        return self._executar("""
            SELECT column_name AS coluna, data_type AS tipo
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (tabela,))

    def esquema_completo(self) -> str:
        texto = []
        for tabela in self.listar_tabelas():
            colunas = self.descrever_tabela(tabela)
            lista = ", ".join(f"{c['coluna']} ({c['tipo']})" for c in colunas)
            texto.append(f"- {tabela}: {lista}")
        return "\n".join(texto)

    def contar_linhas(self, tabela: str) -> int:

        if tabela not in self.listar_tabelas():
            raise ValueError(f"Tabela '{tabela}' não existe no schema public.")
        consulta = sql.SQL("SELECT COUNT(*) AS total FROM {}.{}").format(
            sql.Identifier("public"), sql.Identifier(tabela)
        )
        return int(self._executar(consulta)[0]["total"])


class BancoComLimite(BancoNeon):


    def consultar(self, sql: str) -> list[dict]:
        linhas = super().consultar(sql)
        return linhas[:10]
