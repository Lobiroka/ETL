import pandas as pd


MISSING_VALUES = {"", "-", "...", "..", "…", "N/A", "NA", "NULL"}


def _numeric_or_missing(value):
    if value is None or str(value).strip().upper() in MISSING_VALUES:
        return pd.NA
    return pd.to_numeric(value, errors="coerce")


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

        for column in ("populacao", "domicilios_total", "domicilios_rede_geral"):
            df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

        df["percentual_rede_esgoto"] = pd.NA
        mask = (
            df["domicilios_total"].notna()
            & (df["domicilios_total"] > 0)
            & df["domicilios_rede_geral"].notna()
        )

        df.loc[mask, "percentual_rede_esgoto"] = (
            df.loc[mask, "domicilios_rede_geral"]
            / df.loc[mask, "domicilios_total"]
            * 100
        ).round(2)

        df["ano"] = 2010
        extraction_dates = [
            pd.to_datetime(item.get("data_extracao"), utc=True, errors="coerce")
            for item in populacao
        ]
        valid_dates = [date for date in extraction_dates if not pd.isna(date)]
        df["data_extracao"] = (
            max(valid_dates) if valid_dates else pd.Timestamp.now(tz="UTC")
        )

        colunas = [
            "codigo_bairro",
            "bairro",
            "populacao",
            "domicilios_total",
            "domicilios_rede_geral",
            "percentual_rede_esgoto",
            "ano",
            "data_extracao",
        ]

        result = (
            df[colunas]
            .sort_values("bairro")
            .reset_index(drop=True)
            .astype(object)
        )
        return result.where(pd.notna(result), None)

    @staticmethod
    def _normalizar_populacao(data):

        if not data:
            raise ValueError(
                "A API não retornou dados de população."
            )

        rows = []

        for item in data:
            codigo = str(item.get("D1C", "")).strip()
            if not codigo.isdigit():
                continue
            rows.append({
                "codigo_bairro": codigo,
                "bairro": item.get("D1N", ""),
                "populacao": _numeric_or_missing(item.get("V")),
            })

        df = pd.DataFrame(rows)

        df = df[
            df["codigo_bairro"] != ""
        ]

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

        for item in data:
            codigo = str(item.get("D1C", "")).strip()
            if not codigo.isdigit():
                continue
            rows.append({
                "codigo_bairro": codigo,
                nome_coluna: _numeric_or_missing(item.get("V")),
            })

        df = pd.DataFrame(rows)

        df = df[
            df["codigo_bairro"] != ""
        ]

        return df.drop_duplicates(
            "codigo_bairro"
        )
