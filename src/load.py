import os
import sqlite3

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()


class Load:
    """Persiste dados brutos no MongoDB e dados transformados no SQLite."""

    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI")
        if not self.mongo_uri:
            raise ValueError("A variável MONGODB_URI não foi definida no .env")
        self.client = MongoClient(self.mongo_uri, server_api=ServerApi("1"))

    def close(self) -> None:
        """Encerra a conexão com o MongoDB."""
        self.client.close()

    def load_mongo(
        self, data: list[dict], db_name: str, collection_name: str
    ) -> None:
        """
        Insere dados brutos em uma coleção do MongoDB.

        Parâmetros:
            data: lista de dicionários retornada pela API.
            db_name: banco de dados do MongoDB.
            collection_name: coleção própria da fonte consultada.
        """
        collection = self.client[db_name][collection_name]
        if data:
            collection.delete_many({})
            collection.insert_many(data)
        print(f"MongoDB: coleção '{collection_name}' atualizada com sucesso.")

    def load_sqlite(
        self,
        df: pd.DataFrame,
        nome_banco: str = "ibge.db",
        nome_tabela: str = "recife_populacao_saneamento",
    ) -> None:
        """
        Salva o DataFrame transformado em uma tabela SQLite.

        Parâmetros:
            df: DataFrame pronto para carga.
            nome_banco: arquivo do banco SQLite.
            nome_tabela: tabela de destino.
        """
        with sqlite3.connect(nome_banco) as conn:
            df.to_sql(nome_tabela, conn, if_exists="replace", index=False)
        print(f"SQLite: tabela '{nome_tabela}' atualizada com sucesso.")
