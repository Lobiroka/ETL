from prefect import flow, task, get_run_logger

from src.extract import Extract
from src.load import Load
from src.transform import Transform


DB_NAME = "IBGE"
COLLECTION_POPULACAO = "RECIFE_POPULACAO_BAIRROS"
COLLECTION_SANEAMENTO_TOTAL = "RECIFE_SANEAMENTO_TOTAL"
COLLECTION_SANEAMENTO_REDE = "RECIFE_SANEAMENTO_REDE_GERAL"
NEON_TABLE = "recife_populacao_saneamento"


@task(name="Extrair população do IBGE", retries=3, retry_delay_seconds=10)
def extract_population() -> list[dict]:
    logger = get_run_logger()
    extractor = Extract()
    data = extractor.bairros_recife("recife")
    logger.info("%s registros de população recebidos da API.", sum(
        1 for item in data if str(item.get("D1C", "")).strip().isdigit()
    ))
    return data


@task(name="Extrair saneamento do IBGE", retries=3, retry_delay_seconds=10)
def extract_sanitation() -> dict[str, list[dict]]:
    logger = get_run_logger()
    extractor = Extract()
    data = extractor.saneamento_recife("recife")
    logger.info(
        "Saneamento extraído: total=%s, rede geral=%s registros.",
        sum(1 for item in data["total"] if str(item.get("D1C", "")).strip().isdigit()),
        sum(1 for item in data["rede_geral"] if str(item.get("D1C", "")).strip().isdigit()),
    )
    return data


@task(name="Carregar dados brutos no MongoDB", retries=3, retry_delay_seconds=10)
def load_raw_data(population: list[dict], sanitation: dict[str, list[dict]]) -> bool:
    logger = get_run_logger()
    loader = Load()
    try:
        loader.load_mongo(population, DB_NAME, COLLECTION_POPULACAO)
        loader.load_mongo(sanitation["total"], DB_NAME, COLLECTION_SANEAMENTO_TOTAL)
        loader.load_mongo(sanitation["rede_geral"], DB_NAME, COLLECTION_SANEAMENTO_REDE)
        logger.info("Dados brutos armazenados no MongoDB Atlas.")
    finally:
        loader.close()
    return True


@task(name="Ler dados brutos do MongoDB", retries=3, retry_delay_seconds=10)
def read_mongodb(_raw_loaded: bool) -> dict:
    logger = get_run_logger()
    loader = Load()
    try:
        extractor = Extract()
        population = extractor.extract_collection_from_mongo(
            DB_NAME, COLLECTION_POPULACAO
        )
        sanitation_total = extractor.extract_collection_from_mongo(
            DB_NAME, COLLECTION_SANEAMENTO_TOTAL
        )
        sanitation_network = extractor.extract_collection_from_mongo(
            DB_NAME, COLLECTION_SANEAMENTO_REDE
        )
    finally:
        loader.close()

    logger.info(
        "Dados lidos do MongoDB: população=%s, saneamento total=%s, rede geral=%s.",
        len(population), len(sanitation_total), len(sanitation_network)
    )
    return {
        "population": population,
        "sanitation": {
            "total": sanitation_total,
            "rede_geral": sanitation_network,
        },
    }


@task(name="Transformar e integrar dados", retries=1, retry_delay_seconds=5)
def transform_data(data: dict):
    logger = get_run_logger()
    transformer = Transform()
    dataframe = transformer.transform_recife(
        data["population"],
        data["sanitation"],
    )
    bronze_population_count = sum(
        1 for item in data["population"]
        if str(item.get("D1C", "")).strip().isdigit()
    )
    if len(dataframe) != bronze_population_count:
        raise RuntimeError(
            f"Contagem divergente: bronze={bronze_population_count}, "
            f"final={len(dataframe)}"
        )
    logger.info("%s bairros preparados para carga no NeonDB.", len(dataframe))
    return dataframe.to_dict(orient="records")


@task(name="Carregar dados tratados no NeonDB", retries=3, retry_delay_seconds=10)
def load_neondb(records: list[dict]) -> int:
    import pandas as pd

    logger = get_run_logger()
    dataframe = pd.DataFrame(records)
    loader = Load()
    try:
        loader.load_neondb(dataframe, NEON_TABLE)
        final_count = loader.count_neondb(NEON_TABLE)
        if final_count != len(records):
            raise RuntimeError(
                f"Contagem divergente após a carga: registros da carga={len(records)}, "
                f"tabela final={final_count}"
            )
    finally:
        loader.close()
    logger.info("%s bairros existentes na tabela final do NeonDB.", final_count)
    return final_count


@flow(name="ETL Smart City Recife", log_prints=True)
def etl_recife_flow():
    population = extract_population()
    sanitation = extract_sanitation()
    raw_loaded = load_raw_data(population, sanitation)
    mongo_data = read_mongodb(raw_loaded)
    transformed_records = transform_data(mongo_data)
    total = load_neondb(transformed_records)
    return total


if __name__ == "__main__":
    etl_recife_flow()
