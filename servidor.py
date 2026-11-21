import os
from pathlib import Path

from dotenv import load_dotenv
from fastmcp import FastMCP

from assistente import AssistenteGPT
from banco import BancoComLimite


load_dotenv(Path(__file__).resolve().parent / ".env")

banco = BancoComLimite(os.getenv("DATABASE_URL") or os.getenv("NEON"))
mcp = FastMCP("Smart City Recife — Neon + GPT")


@mcp.tool(description="Lista as tabelas existentes no schema public do banco da disciplina.")
def listar_tabelas() -> list[str]:

    return banco.listar_tabelas()


@mcp.tool(description="Mostra todas as colunas e os tipos de uma tabela do schema public.")
def descrever_tabela(tabela: str) -> list[dict]:

    return banco.descrever_tabela(tabela)


@mcp.tool(description="Executa um SELECT somente leitura e devolve no máximo 10 linhas.")
def executar_select(sql: str) -> list[dict]:

    return banco.consultar(sql)


@mcp.tool(description="Conta o total de linhas de uma tabela, sem o limite de 10 resultados.")
def contar_linhas(tabela: str) -> int:

    return banco.contar_linhas(tabela)


@mcp.tool(description="Responde em português: a IA gera SQL, consulta o Neon e explica os dados.")
def perguntar_ao_banco(pergunta: str) -> dict:


    gpt = AssistenteGPT(
        os.getenv("GPT") or os.getenv("OPENAI_API_KEY"),
        modelo=os.getenv("MODELO") or "gpt-6-luna",
        base_url=os.getenv("BASE_URL") or os.getenv("OPENAI_BASE_URL"),
    )
    sql = gpt.gerar_sql(pergunta, banco.esquema_completo())
    dados = banco.consultar(sql)
    resposta = gpt.explicar_resultado(pergunta, dados)
    return {"sql": sql, "dados": dados, "resposta": resposta}


if __name__ == "__main__":
    mcp.run()
