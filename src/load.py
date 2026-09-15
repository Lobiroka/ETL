import os

import pandas as pd
import psycopg
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi


load_dotenv()


class Load:
    """
    Responsável por armazenar os dados brutos no MongoDB Atlas
    e os dados transformados no NeonDB.
    """

    def __init__(self):
        self.mongo_uri = os.getenv("MONGODB_URI")
        self.database_url = os.getenv("DATABASE_URL")

        if not self.mongo_uri:
            raise ValueError(
                "A variável MONGODB_URI não foi definida no .env"
            )

        if not self.database_url:
            raise ValueError(
                "A variável DATABASE_URL não foi definida no .env"
            )

        self.client = MongoClient(
            self.mongo_uri,
            server_api=ServerApi("1")
        )

    def close(self) -> None:
        """
        Encerra a conexão com o MongoDB Atlas.
        """
        self.client.close()

    def load_mongo(
        self,
        data: list[dict],
        db_name: str,
        collection_name: str
    ) -> None:
        """
        Insere os dados brutos em uma coleção do MongoDB Atlas.

        Parâmetros:
            data: lista de dicionários retornada pela API.
            db_name: nome do banco de dados.
            collection_name: nome da coleção.
        """

        collection = self.client[db_name][collection_name]

        if data:
            collection.delete_many({})
            collection.insert_many(data)

        print(
            f"MongoDB Atlas: coleção "
            f"'{collection_name}' atualizada com sucesso."
        )

    def load_neondb(
        self,
        df: pd.DataFrame,
        nome_tabela: str = "recife_populacao_saneamento"
    ) -> None:
        """
        Salva o DataFrame transformado no NeonDB.

        Parâmetros:
            df: DataFrame resultante da transformação.
            nome_tabela: tabela de destino no NeonDB.
        """

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {nome_tabela} (
            codigo_bairro VARCHAR(20) PRIMARY KEY,
            bairro VARCHAR(255),
            populacao INTEGER,
            domicilios_total INTEGER,
            domicilios_rede_geral INTEGER,
            percentual_rede_esgoto NUMERIC(5, 2),
            ano INTEGER
        );
        """

        insert_sql = f"""
        INSERT INTO {nome_tabela} (
            codigo_bairro,
            bairro,
            populacao,
            domicilios_total,
            domicilios_rede_geral,
            percentual_rede_esgoto,
            ano
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (codigo_bairro)
        DO UPDATE SET
            bairro = EXCLUDED.bairro,
            populacao = EXCLUDED.populacao,
            domicilios_total = EXCLUDED.domicilios_total,
            domicilios_rede_geral = EXCLUDED.domicilios_rede_geral,
            percentual_rede_esgoto = EXCLUDED.percentual_rede_esgoto,
            ano = EXCLUDED.ano;
        """

        with psycopg.connect(self.database_url) as conn:

            with conn.cursor() as cursor:

                cursor.execute(create_table_sql)

                for _, row in df.iterrows():

                    cursor.execute(
                        insert_sql,
                        (
                            row["codigo_bairro"],
                            row["bairro"],
                            int(row["populacao"]),
                            int(row["domicilios_total"]),
                            int(row["domicilios_rede_geral"]),
                            float(row["percentual_rede_esgoto"]),
                            int(row["ano"])
                        )
                    )

            conn.commit()

        print(
            f"NeonDB: tabela '{nome_tabela}' "
            f"atualizada com sucesso."
        )