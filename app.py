import streamlit as st
import pandas as pd
import plotly.express as px
st.markdown("""
<style>
    body {
        background-color: #0f0f0f;
        color: #eaeaea;
    }
    .stMetric {
        background-color: #1a1a1a;
        border-left: 4px solid #1DB954;
        padding: 10px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)
st.set_page_config(
    page_title="Larga o Verbo | Dashboard",
    layout="wide"
)

df = pd.read_excel("RANKING_LARGA_O_VERBO.xlsx")
df.fillna(0, inplace=True)

st.title("💚 Ranking Larga o Verbo")
st.caption("Análise de performance e evolução dos MCs")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("MCs no Ranking", len(df))
col2.metric("Líder Atual", df.iloc[0]["MC"])
col3.metric("Mais Títulos", df.loc[df["VT (4)"].idxmax()]["MC"])
col4.metric("Mais Vices", df.loc[df["VC (3)"].idxmax()]["MC"])
col4.metric(
    "Mais 2x0 ",
    df.loc[df["2x0 (1)"].idxmax()]["MC"]
)
st.divider()

st.subheader("🏆 Ranking Geral")

fig_rank = px.bar(
    df.sort_values("PTS"),
    x="PTS",
    y="MC",
    orientation="h",
    text="PTS",
    height=600,
    color_discrete_sequence=["#1DB954"]
)
fig_rank.update_layout(showlegend=False)
st.plotly_chart(fig_rank, use_container_width=True)

st.subheader("📝 Leituras de Desempenho")

for _, row in df.iterrows():
    with st.expander(f"{row['MC']} · {row['PTS']} pts"):
        comentario = ""

        if row["VT (4)"] >= 3:
            comentario = "MC com histórico forte de títulos, presença dominante nas edições."
        elif row["VC (3)"] >= 3:
            comentario = "MC muito consistente, chega em finais com frequência."
        elif row["SM (2)"] >= 4:
            comentario = "MC regular, presença constante nas fases finais."
        elif row["PTS"] < 15:
            comentario = "MC em fase de construção de trajetória no ranking."
        else:
            comentario = "MC competitivo, com participações relevantes no evento."

        st.write(comentario)
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
    title=f"Resultados de {mc_selected}",
    color_discrete_sequence=["#1DB954"]
)
    st.plotly_chart(fig_mc_bar, use_container_width=True)

with col2:
    st.subheader("📋 Resumo do Desempenho")
    st.table(
        mc_data[result_cols].rename(columns={
            "VT (4)": "Títulos",
            "VC (3)": "Vices",
            "SM (2)": "Semifinais",
            "2ªF (1)": "Segunda Fase"
        })
    )
st.subheader("⚔️ Comparação entre MCs")

mc_compare = st.multiselect(
    "Escolha até 2 MCs",
    df["MC"].unique(),
    max_selections=2
)

if len(mc_compare) > 0:
    df_compare = df[df["MC"].isin(mc_compare)]
    ig_compare = px.bar(
    df_compare,
    x="MC",
    y=result_cols,
    barmode="group",
    title="Comparação de Resultados",
    color_discrete_sequence=["#1DB954", "#A3E635"]
)
    st.plotly_chart(fig_compare, use_container_width=True)


