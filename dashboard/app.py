import pandas as pd
import psycopg
import streamlit as st

from src.config import DATABASE_URL, require_config


st.set_page_config(page_title="Smart City Recife", page_icon="🌆", layout="wide")
st.title("Smart City Recife")
st.caption("População e cobertura de esgotamento sanitário por bairro · Censo 2010")


@st.cache_data(ttl=300)
def carregar_dados() -> pd.DataFrame:
    database_url = require_config("DATABASE_URL", DATABASE_URL)
    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT codigo_bairro, bairro, populacao, domicilios_total,
                          domicilios_rede_geral, percentual_rede_esgoto, ano
                   FROM recife_populacao_saneamento
                   ORDER BY bairro"""
            )
            rows = cursor.fetchall()
            columns = [column.name for column in cursor.description]
    return pd.DataFrame(rows, columns=columns)


try:
    dados = carregar_dados()
except Exception as exc:
    st.error(f"Não foi possível carregar a tabela do Neon: {exc}")
    st.stop()

if dados.empty:
    st.info("A tabela final ainda não tem registros. Execute `python run_etl.py` primeiro.")
    st.stop()

bairros = ["Todos os bairros", *dados["bairro"].dropna().sort_values().tolist()]
selecionado = st.selectbox("Filtrar bairro", bairros)
filtrados = dados if selecionado == "Todos os bairros" else dados[dados["bairro"] == selecionado]

populacao_total = int(filtrados["populacao"].sum())
cobertura = filtrados["percentual_rede_esgoto"].mean()
left, middle, right = st.columns(3)
left.metric("Bairros", f"{len(filtrados):,}".replace(",", "."))
middle.metric("População", f"{populacao_total:,}".replace(",", "."))
right.metric("Cobertura média de esgoto", "—" if pd.isna(cobertura) else f"{cobertura:.2f}%")

st.subheader("Cobertura de esgoto por bairro")
chart_data = filtrados.dropna(subset=["percentual_rede_esgoto"]).set_index("bairro")[
    "percentual_rede_esgoto"
]
st.bar_chart(chart_data, y_label="Cobertura (%)")
st.subheader("Dados do recorte")
st.dataframe(filtrados, hide_index=True, use_container_width=True)
