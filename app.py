import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Larga o Verbo | Dashboard",
    layout="wide"
)

df = pd.read_excel("RANKING_LARGA_O_VERBO.xlsx")
df.fillna(0, inplace=True)

st.title("🎤 Larga o Verbo | Dashboard de Progressão")
st.caption("Análise de performance e evolução dos MCs")

col1, col2, col3, col4 = st.columns(4)
col1.metric("MCs no Ranking", len(df))
col2.metric("Líder Atual", df.iloc[0]["MC"])
col3.metric("Mais Títulos", df.loc[df["VT (4)"].idxmax()]["MC"])
col4.metric("Mais Semifinais", df.loc[df["SM (2)"].idxmax()]["MC"])

st.divider()

st.subheader("🏆 Ranking Geral")

fig_rank = px.bar(
    df.sort_values("PTS"),
    x="PTS",
    y="MC",
    orientation="h",
    text="PTS",
    height=600
)
fig_rank.update_layout(showlegend=False)
st.plotly_chart(fig_rank, use_container_width=True)

st.subheader("📊 Distribuição de Resultados")

result_cols = ["VT (4)", "VC (3)", "SM (2)", "2ªF (1)"]

df_results = df[result_cols].sum().reset_index()
df_results.columns = ["Resultado", "Quantidade"]

fig_results = px.pie(
    df_results,
    names="Resultado",
    values="Quantidade",
    hole=0.4
)
st.plotly_chart(fig_results, use_container_width=True)

st.subheader("🧬 Análise Individual")

mc_selected = st.selectbox(
    "Selecione um MC",
    df["MC"].unique()
)

mc_data = df[df["MC"] == mc_selected]

col1, col2 = st.columns(2)

with col1:
    fig_mc_bar = px.bar(
        mc_data.melt(
            id_vars="MC",
            value_vars=result_cols
        ),
        x="variable",
        y="value",
        text="value",
        title=f"Resultados de {mc_selected}"
    )
    st.plotly_chart(fig_mc_bar, use_container_width=True)

with col2:
    fig_mc_radar = px.line_polar(
        mc_data,
        r=result_cols,
        theta=result_cols,
        line_close=True,
        title="Perfil de Performance"
    )
    st.plotly_chart(fig_mc_radar, use_container_width=True)

st.subheader("⚔️ Comparação entre MCs")

mc_compare = st.multiselect(
    "Escolha até 2 MCs",
    df["MC"].unique(),
    max_selections=2
)

if len(mc_compare) > 0:
    df_compare = df[df["MC"].isin(mc_compare)]
    fig_compare = px.bar(
        df_compare,
        x="MC",
        y=result_cols,
        barmode="group",
        title="Comparação de Resultados"
    )
    st.plotly_chart(fig_compare, use_container_width=True)
