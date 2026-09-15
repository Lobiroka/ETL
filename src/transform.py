import pandas as pd


class Transform:
    """Limpa e integra os dados do IBGE."""

    def transform_recife(
        self,
        populacao: list[dict],
        saneamento: dict
    ) -> pd.DataFrame:

        df_pop = self._normalizar_populacao(populacao)

        df_total = self._normalizar_saneamento(
            saneamento["total"],
            "domicilios_total"
        )

        df_rede = self._normalizar_saneamento(
            saneamento["rede_geral"],
            "domicilios_rede_geral"
        )

        df_san = df_total.merge(
            df_rede,
            on="codigo_bairro",
            how="left"
        )

        df = df_pop.merge(
            df_san,
            on="codigo_bairro",
            how="left"
        )

        df["domicilios_total"] = (
            df["domicilios_total"]
            .fillna(0)
            .astype(int)
        )

        df["domicilios_rede_geral"] = (
            df["domicilios_rede_geral"]
            .fillna(0)
            .astype(int)
        )

        df["percentual_rede_esgoto"] = 0.0

        mask = df["domicilios_total"] > 0

        df.loc[mask, "percentual_rede_esgoto"] = (
            df.loc[mask, "domicilios_rede_geral"]
            / df.loc[mask, "domicilios_total"]
            * 100
        ).round(2)

        df["ano"] = 2010

        colunas = [
            "codigo_bairro",
            "bairro",
            "populacao",
            "domicilios_total",
            "domicilios_rede_geral",
            "percentual_rede_esgoto",
            "ano"
        ]

        return (
            df[colunas]
            .sort_values("bairro")
            .reset_index(drop=True)
        )

    @staticmethod
    def _normalizar_populacao(data):

        if not data:
            raise ValueError(
                "A API não retornou dados de população."
            )

        rows = []

        for item in data[1:]:
            rows.append({
                "codigo_bairro": str(
                    item.get("D1C", "")
                ),
                "bairro": item.get("D1N", ""),
                "populacao": pd.to_numeric(
                    item.get("V"),
                    errors="coerce"
                )
            })

        df = pd.DataFrame(rows)

        df = df[
            df["codigo_bairro"] != ""
        ]

        df["populacao"] = (
            df["populacao"]
            .fillna(0)
            .astype(int)
        )

        return df.drop_duplicates(
            "codigo_bairro"
        )

    @staticmethod
    def _normalizar_saneamento(data, nome_coluna):

        if not data:
            raise ValueError(
                "A API não retornou dados de saneamento."
            )

        rows = []

        for item in data[1:]:
            rows.append({
                "codigo_bairro": str(
                    item.get("D1C", "")
                ),
                nome_coluna: pd.to_numeric(
                    item.get("V"),
                    errors="coerce"
                )
            })

        df = pd.DataFrame(rows)

        df = df[
            df["codigo_bairro"] != ""
        ]

        return df.drop_duplicates(
            "codigo_bairro"
        )