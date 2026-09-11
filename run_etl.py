from src.extract import Extract
from src.load import Load
from src.transform import Transform


DB_NAME = "IBGE"

COLLECTION_POPULACAO = "RECIFE_POPULACAO_BAIRROS"
COLLECTION_SANEAMENTO_TOTAL = "RECIFE_SANEAMENTO_TOTAL"
COLLECTION_SANEAMENTO_REDE = "RECIFE_SANEAMENTO_REDE_GERAL"

SQLITE_DB = "ibge.db"
SQLITE_TABLE = "recife_populacao_saneamento"


def main():
    ext = Extract()
    load = Load()
    transform = Transform()

    try:
        # ==========================================================
        # ETAPA 1 - EXTRAÇÃO DA POPULAÇÃO
        # ==========================================================

        print(
            "Etapa 1: extraindo população dos bairros do Recife..."
        )

        populacao = ext.bairros_recife("recife")

        print(
            f"População: {len(populacao) - 1} bairros encontrados."
        )

        load.load_mongo(
            populacao,
            DB_NAME,
            COLLECTION_POPULACAO
        )

        # ==========================================================
        # ETAPA 2 - EXTRAÇÃO DO SANEAMENTO
        # ==========================================================

        print(
            "Etapa 2: extraindo dados de saneamento..."
        )

        saneamento = ext.saneamento_recife("recife")

        saneamento_total = saneamento["total"]
        saneamento_rede = saneamento["rede_geral"]

        print(
            f"Saneamento total: "
            f"{len(saneamento_total) - 1} bairros encontrados."
        )

        print(
            f"Rede geral de esgoto: "
            f"{len(saneamento_rede) - 1} bairros encontrados."
        )

        load.load_mongo(
            saneamento_total,
            DB_NAME,
            COLLECTION_SANEAMENTO_TOTAL
        )

        load.load_mongo(
            saneamento_rede,
            DB_NAME,
            COLLECTION_SANEAMENTO_REDE
        )

        # ==========================================================
        # ETAPA 3 - LEITURA DOS DADOS DO MONGODB
        # ==========================================================

        print(
            "Etapa 3: lendo dados brutos do MongoDB..."
        )

        populacao_mongo = ext.extract_collection_from_mongo(
            load.mongo_uri,
            DB_NAME,
            COLLECTION_POPULACAO
        )

        saneamento_total_mongo = (
            ext.extract_collection_from_mongo(
                load.mongo_uri,
                DB_NAME,
                COLLECTION_SANEAMENTO_TOTAL
            )
        )

        saneamento_rede_mongo = (
            ext.extract_collection_from_mongo(
                load.mongo_uri,
                DB_NAME,
                COLLECTION_SANEAMENTO_REDE
            )
        )

        # ==========================================================
        # ETAPA 4 - TRANSFORMAÇÃO
        # ==========================================================

        print(
            "Etapa 4: transformando os dados..."
        )

        saneamento_mongo = {
            "total": saneamento_total_mongo,
            "rede_geral": saneamento_rede_mongo
        }

        df = transform.transform_recife(
            populacao_mongo,
            saneamento_mongo
        )

        print()
        print("Resultado da transformação:")
        print(df.head(10).to_string(index=False))
        print()

        print(
            f"Total de bairros processados: {len(df)}"
        )

        # ==========================================================
        # ETAPA 5 - SQLITE
        # ==========================================================

        print(
            "Etapa 5: salvando no SQLite..."
        )

        load.load_sqlite(
            df,
            SQLITE_DB,
            SQLITE_TABLE
        )

        print()
        print("Pipeline concluído com sucesso!")

    finally:
        load.close()


if __name__ == "__main__":
    main()