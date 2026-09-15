import os

import requests
from dotenv import load_dotenv
from pymongo import MongoClient


class Extract:
    """
    Classe responsável pela extração de dados da API do IBGE
    e pela leitura dos dados brutos armazenados no MongoDB.
    """

    CIDADES = {
        "recife": "2611606"
    }

    TABELAS = {
        "populacao": "202",
        "saneamento": "1394"
    }

    POPULACAO = {
        "variavel": "93",
        "sexo": "0",
        "situacao": "0",
        "ano": "2010"
    }

    SANEAMENTO = {
        "variavel": "96",
        "situacao": "0",
        "banheiro": "0",
        "tipo_domicilio": "0",
        "condicao_ocupacao": "0",
        "total_esgoto": "0",
        "rede_geral": "92855",
        "ano": "2010"
    }

    NIVEL_BAIRRO = "n102"

    def __init__(self):
        """
        Inicializa as configurações utilizadas na extração.
        """

        load_dotenv()

        self.base_url = (
            "https://apisidra.ibge.gov.br/values"
        )

        self.codigo_recife = self.CIDADES["recife"]
        self.cidade = "Recife"

    def _get(self, url: str) -> list[dict]:
        """
        Realiza uma requisição GET para a API do IBGE.

        Parâmetros:
            url: URL completa da consulta.

        Retorna:
            Lista de dicionários retornada pela API.
        """

        response = requests.get(
            url,
            timeout=60
        )

        response.raise_for_status()

        return response.json()

    def bairros_recife(
        self,
        cidade: str = "recife"
    ) -> list[dict]:
        """
        Extrai a população residente dos bairros do Recife
        no Censo Demográfico de 2010.

        Parâmetros:
            cidade: Nome da cidade cadastrada nas opções válidas.

        Retorna:
            Lista com os dados brutos de população.
        """

        cidade = cidade.lower()

        if cidade not in self.CIDADES:
            raise ValueError(
                "Cidade inválida. Utilize 'recife'."
            )

        codigo = self.CIDADES[cidade]

        url = (
            f"{self.base_url}/"
            f"t/{self.TABELAS['populacao']}/"
            f"{self.NIVEL_BAIRRO}/"
            f"IN%20N6%20{codigo}/"
            f"v/{self.POPULACAO['variavel']}/"
            f"c2/{self.POPULACAO['sexo']}/"
            f"c1/{self.POPULACAO['situacao']}/"
            f"p/{self.POPULACAO['ano']}"
        )

        return self._get(url)

    def saneamento_recife(
        self,
        cidade: str = "recife"
    ) -> dict[str, list[dict]]:
        """
        Extrai dados de saneamento dos bairros do Recife.

        Parâmetros:
            cidade: Nome da cidade cadastrada nas opções válidas.

        Retorna:
            Dicionário contendo os dados totais de domicílios
            e os dados de domicílios ligados à rede geral
            de esgoto ou pluvial.
        """

        cidade = cidade.lower()

        if cidade not in self.CIDADES:
            raise ValueError(
                "Cidade inválida. Utilize 'recife'."
            )

        codigo = self.CIDADES[cidade]

        url_total = (
            f"{self.base_url}/"
            f"t/{self.TABELAS['saneamento']}/"
            f"{self.NIVEL_BAIRRO}/"
            f"IN%20N6%20{codigo}/"
            f"v/{self.SANEAMENTO['variavel']}/"
            f"c1/{self.SANEAMENTO['situacao']}/"
            f"c458/{self.SANEAMENTO['banheiro']}/"
            f"c125/{self.SANEAMENTO['tipo_domicilio']}/"
            f"c63/{self.SANEAMENTO['condicao_ocupacao']}/"
            f"c11558/{self.SANEAMENTO['total_esgoto']}/"
            f"p/{self.SANEAMENTO['ano']}"
        )

        url_rede = (
            f"{self.base_url}/"
            f"t/{self.TABELAS['saneamento']}/"
            f"{self.NIVEL_BAIRRO}/"
            f"IN%20N6%20{codigo}/"
            f"v/{self.SANEAMENTO['variavel']}/"
            f"c1/{self.SANEAMENTO['situacao']}/"
            f"c458/{self.SANEAMENTO['banheiro']}/"
            f"c125/{self.SANEAMENTO['tipo_domicilio']}/"
            f"c63/{self.SANEAMENTO['condicao_ocupacao']}/"
            f"c11558/{self.SANEAMENTO['rede_geral']}/"
            f"p/{self.SANEAMENTO['ano']}"
        )

        total = self._get(url_total)
        rede_geral = self._get(url_rede)

        return {
            "total": total,
            "rede_geral": rede_geral
        }

    def extract_collection_from_mongo(
        self,
        mongo_uri: str,
        database: str,
        collection: str
    ) -> list[dict]:
        """
        Lê os documentos de uma coleção do MongoDB.

        Parâmetros:
            mongo_uri: URI de conexão com o MongoDB.
            database: Nome do banco de dados.
            collection: Nome da coleção.

        Retorna:
            Lista de documentos encontrados.
        """

        client = MongoClient(mongo_uri)

        try:
            db = client[database]

            return list(
                db[collection].find(
                    {},
                    {"_id": 0}
                )
            )

        finally:
            client.close()