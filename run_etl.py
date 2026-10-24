from src.extract import Extract
from src.load import Load
from src.transform import Transform


DB_NAME = "IBGE"

COLLECTION_POPULACAO = "RECIFE_POPULACAO_BAIRROS"
COLLECTION_SANEAMENTO_TOTAL = "RECIFE_SANEAMENTO_TOTAL"
COLLECTION_SANEAMENTO_REDE = "RECIFE_SANEAMENTO_REDE_GERAL"

NEON_TABLE = "recife_populacao_saneamento"


def main():

    ext = Extract()
    load = Load()
    transform = Transform()

    try:

        # ==========================================================
        # ETAPA 1 - EXTRAÇÃO DA POPULAÇÃO
        # ==========================================================

        print("=" * 60)
        print("ETL SMART CITY RECIFE")
        print("=" * 60)

        print()
        print("Etapa 1: extraindo população da API do IBGE...")

        populacao = ext.bairros_recife("recife")

        print(
            "População: "
            f"{sum(1 for item in populacao if str(item.get('D1C', '')).strip().isdigit())} "
            "bairros encontrados."
        )

        # ==========================================================
        # ETAPA 2 - MONGODB ATLAS
        # ==========================================================

        print()
        print("Etapa 2: salvando população no MongoDB Atlas...")

        load.load_mongo(
            populacao,
            DB_NAME,
            COLLECTION_POPULACAO
        )

        # ==========================================================
        # EXTRAÇÃO DO SANEAMENTO
        # ==========================================================

        print()
        print("Extraindo dados de saneamento da API do IBGE...")

        saneamento = ext.saneamento_recife("recife")

        saneamento_total = saneamento["total"]
        saneamento_rede = saneamento["rede_geral"]

        print(
            f"Saneamento total: "
            f"{sum(1 for item in saneamento_total if str(item.get('D1C', '')).strip().isdigit())} "
            "bairros encontrados."
        )

        print(
            f"Rede geral de esgoto: "
            f"{sum(1 for item in saneamento_rede if str(item.get('D1C', '')).strip().isdigit())} "
            "bairros encontrados."
        )

        print()
        print("Salvando saneamento no MongoDB Atlas...")

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
        # ETAPA 3 - LEITURA DO MONGODB ATLAS
        # ==========================================================

        print()
        print(
            "Etapa 3: recuperando dados "
            "do MongoDB Atlas..."
        )

        populacao_mongo = ext.extract_collection_from_mongo(
            DB_NAME,
            COLLECTION_POPULACAO
        )

        saneamento_total_mongo = (
            ext.extract_collection_from_mongo(
                DB_NAME,
                COLLECTION_SANEAMENTO_TOTAL
            )
        )

        saneamento_rede_mongo = (
            ext.extract_collection_from_mongo(
                DB_NAME,
                COLLECTION_SANEAMENTO_REDE
            )
        )

        print("Dados recuperados do MongoDB Atlas com sucesso.")

        # ==========================================================
        # ETAPA 4 - TRANSFORMAÇÃO
        # ==========================================================

        print()
        print("Etapa 4: transformando os dados com Pandas...")

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

        bronze_pop = sum(
            1 for item in populacao_mongo
            if str(item.get("D1C", "")).strip().isdigit()
        )
        print(f"Bronze população (última carga): {bronze_pop} registros")
        if len(df) != bronze_pop:
            raise RuntimeError(
                f"Contagem divergente: bronze={bronze_pop}, final={len(df)}"
            )

        # ==========================================================
        # ETAPA 5 - NEONDB
        # ==========================================================

        print()
        print("Etapa 5: salvando dados transformados no NeonDB...")

        load.load_neondb(
            df,
            NEON_TABLE
        )

        neon_count = load.count_neondb(NEON_TABLE)
        print(f"NeonDB tabela final: {neon_count} registros")
        if neon_count != bronze_pop:
            raise RuntimeError(
                f"Contagem divergente após a carga: bronze={bronze_pop}, "
                f"tabela final={neon_count}"
            )

        # ==========================================================
        # FINALIZAÇÃO
        # ==========================================================

        print()
        print("=" * 60)
        print("Pipeline concluído com sucesso!")
        print(f"{len(df)} bairros carregados no NeonDB.")
        print("=" * 60)

    finally:
        load.close()


if __name__ == "__main__":
    main()
