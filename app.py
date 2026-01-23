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
result_cols = [
    "VT (4)",
    "VICE (2)",
    "SEMIS (1)",
    "2x0 (1)"
]

df.fillna(0, inplace=True)

st.title("💚 Ranking Larga o Verbo")
st.caption("Análise de performance e evolução dos MCs")

col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
col1.metric("MCs no Ranking", len(df))
col2.metric("Líder Atual", df.iloc[0]["MC"])
col3.metric("Mais Títulos", df.loc[df["VT (4)"].idxmax()]["MC"])
col4.metric("Mais Vices", df.loc[df["VC (3)"].idxmax()]["MC"])
col5.metric(
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
    top5 = df.sort_values("PTS", ascending=False).head(5)

comentarios_curados = {
    top5.iloc[0]["MC"]: "Líder do ranking. MC com domínio competitivo claro, alto aproveitamento em fases decisivas e presença constante no topo. Atua com controle e regularidade.",
    
    top5.iloc[1]["MC"]: "Principal perseguidor do líder. Extremamente consistente, chega longe em praticamente todas as edições e mantém pressão constante na disputa pelo topo.",
    
    top5.iloc[2]["MC"]: "MC estrategicamente perigoso. Alterna picos de performance com quedas pontuais, mas sempre representa ameaça real nas fases finais.",
    
    top5.iloc[3]["MC"]: "Nome em consolidação no ranking. Demonstra evolução ao longo das edições e capacidade de disputar com MCs mais experientes.",
    
    top5.iloc[4]["MC"]: "MC competitivo e resiliente. Mesmo fora do topo imediato, sustenta presença relevante e pode surpreender em confrontos diretos."
}

st.subheader("🧠 Análise de desempenho · Top 5")

for _, row in top5.iterrows():
    with st.expander(f"{row['MC']} · {row['PTS']} pts"):
        st.write(comentarios_curados.get(row["MC"], ""))

st.subheader("🧬 Análise Individual")

mc_selected = st.selectbox(
    "Selecione um MC",
    df["MC"].unique()
)

mc_data = df[df["MC"] == mc_selected]

# colunas reais de resultados (PRECISAM existir no df)
result_cols = ["VT (4)", "VC (3)", "SM (2)", "2ªF (1)"]

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

mcs_compare = st.multiselect(
    "Selecione até dois MCs para comparar",
    df["MC"].unique(),
    max_selections=2
)

if len(mcs_compare) == 2:
    df_compare = df[df["MC"].isin(mcs_compare)]

    result_cols = ["VT (4)", "VC (3)", "SM (2)", "2ªF (1)"]

    fig_compare = px.bar(
        df_compare,
        x="MC",
        y=result_cols,
        barmode="group",
        title="Comparação de Resultados",
        color_discrete_sequence=["#1DB954", "#A3E635"]
    )

    st.plotly_chart(fig_compare, use_container_width=True)
else:
    st.info("Selecione exatamente dois MCs para visualizar a comparação.")
# ─────────────────────────────────────────────
# Rodapé · Sobre o Larga o Verbo
# ─────────────────────────────────────────────

st.markdown("---")

st.markdown(
    """
    <h3>
        💚 Sobre o 
        <a href="https://www.instagram.com/largaoverbo" target="_blank" 
           style="text-decoration:none; color:#1DB954;">
            Larga o Verbo
        </a>
    </h3>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    O **Larga o Verbo** é um movimento cultural que teve início em agosto de 2022, 
    originalmente como uma batalha de MCs. Ao longo de nossa trajetória, 
    percebemos que o LV vai além do elemento da rima, tornando-se um espaço de 
    fortalecimento e valorização das expressões culturais periféricas e marginais.

    Nosso foco é fomentar iniciativas que dialoguem diretamente com a juventude local, 
    promovendo ações que englobem tanto os elementos da cultura Hip Hop quanto 
    outras manifestações culturais relevantes.
    """
)

st.markdown(
    "> *Mais do que rima, o Larga o Verbo é espaço de voz, troca e construção cultural.*"
)

st.markdown(
    """
    <div style="display:flex; gap:20px; margin-top:30px; flex-wrap:wrap;">
        <a href="https://www.instagram.com/largaoverbo" target="_blank">
            <button style="
                background-color:#1DB954;
                color:white;
                border:none;
                padding:18px 28px;
                font-size:18px;
                font-weight:bold;
                border-radius:12px;
                cursor:pointer;
            ">
                📲 Instagram · Larga o Verbo
            </button>
        </a>

        <a href="https://www.youtube.com/@largaoverbolv" target="_blank">
            <button style="
                background-color:#FF0000;
                color:white;
                border:none;
                padding:18px 28px;
                font-size:18px;
                font-weight:bold;
                border-radius:12px;
                cursor:pointer;
            ">
                ▶️ YouTube · Larga o Verbo
            </button>
        </a>
    </div>
    """,
    unsafe_allow_html=True
)











