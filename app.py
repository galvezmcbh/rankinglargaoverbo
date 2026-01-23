import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
st.markdown(
    """
    <style>
    /* Chip selecionado no multiselect */
    span[data-testid="stMultiSelectTag"] {
        background-color: #7A1FA2 !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }

    /* Texto interno do chip */
    span[data-testid="stMultiSelectTag"] span {
        color: white !important;
    }

    /* Ícone de remover (x) */
    span[data-testid="stMultiSelectTag"] svg {
        fill: white !important;
    }

    /* Hover */
    span[data-testid="stMultiSelectTag"]:hover {
        background-color: #6A1B9A !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ─────────────────────────────────────────────
# Mapeamento dos indicadores do ranking
# ─────────────────────────────────────────────
result_map = {
    "VT (4)": "Títulos",
    "VC (3)": "Vices",
    "SM (2)": "Semifinais",
    "2x0 (1)": "Vitórias 2x0",
    "2x0": "Vitórias 2x0"
}
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

# detecta automaticamente quais colunas existem
valid_cols = [col for col in result_map.keys() if col in mc_data.columns]

col1, col2 = st.columns(2)

with col1:
    fig_mc_bar = px.bar(
        mc_data.melt(
            id_vars="MC",
            value_vars=valid_cols
        ),
        x="variable",
        y="value",
        text="value",
        title=f"Resultados de {mc_selected}",
        color_discrete_sequence=["#1DB954"]
    )

    # troca nomes técnicos por nomes legíveis
    fig_mc_bar.update_xaxes(
        ticktext=[result_map[c] for c in valid_cols],
        tickvals=valid_cols
    )

    st.plotly_chart(fig_mc_bar, use_container_width=True)

import re

with col2:
    st.subheader("📊 Trajetória no Larga o Verbo")

    texto = mc_data["Pontos contabilizados"].iloc[0]
    texto_lower = texto.lower()

    # 🔎 Captura edições numeradas
    edicoes_raw = re.findall(r"(\d+)\s*ª?\s*ed", texto_lower)
    edicoes = sorted([int(e) for e in edicoes_raw])

    total_edicoes = len(edicoes)
    primeira_edicao = min(edicoes) if edicoes else None
    ultima_edicao = max(edicoes) if edicoes else None
    intervalo = (ultima_edicao - primeira_edicao) if edicoes else 0

    # Contagens semânticas
    vitorias = texto_lower.count("vitória")
    semifinais = texto_lower.count("semifinal")
    especiais = texto_lower.count("especial")

    # 🎭 Classificação simbólica
    if total_edicoes >= 8 and intervalo >= 15:
        perfil = "🎖️ MC Veterano"
        descricao = "Presença histórica, atravessando várias fases do Larga o Verbo."
    elif total_edicoes >= 6 and intervalo < 10:
        perfil = "🔥 MC Constante"
        descricao = "Participação frequente e recorrente nas edições."
    elif total_edicoes <= 4 and ultima_edicao and ultima_edicao >= max(edicoes) - 3:
        perfil = "🌱 MC em Ascensão"
        descricao = "Chegada recente, com crescimento e presença atual."
    else:
        perfil = "🌒 Participação Pontual"
        descricao = "Atuação mais espaçada ou seletiva ao longo do projeto."

    # 🟩🟪 CARD HORIZONTAL
    st.markdown(
        f"""
        <div style="
            display:flex;
            flex-direction:row;
            gap:24px;
            padding:24px;
            border-radius:18px;
            background:linear-gradient(135deg, #1DB95422, #6A0DAD22);
            border:2px solid #6A0DAD55;
            align-items:center;
            margin-top:16px;
        ">

        <div style="flex:1;">
                <h3 style="margin:0; color:#6A0DAD;">{perfil}</h3>
                <p style="margin:6px 0 0 0; color:#1DB954; font-weight:600;">
                    {descricao}
                </p>
            </div>

         <div style="flex:1; color:white;">
                <p><strong>🎤 Edições:</strong> {total_edicoes}</p>
                <p><strong>🏆 Vitórias:</strong> {vitorias}</p>
                <p><strong>🥈 Semifinais:</strong> {semifinais}</p>
                <p><strong>📍 Primeira edição:</strong> {primeira_edicao if primeira_edicao else "—"}</p>
                <p><strong>📍 Última edição:</strong> {ultima_edicao if ultima_edicao else "—"}</p>
                <p><strong>⏱️ Intervalo:</strong> {intervalo} edições</p>
                {"<p><strong>✨ Edição especial:</strong> sim</p>" if especiais > 0 else ""}
          </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    
st.subheader("⚔️ Comparação entre MCs")

mc_compare = st.multiselect(
    "Selecione dois MCs para comparar",
    df["MC"].unique(),
    max_selections=2
)

if len(mc_compare) == 2:
    compare_data = df[df["MC"].isin(mc_compare)]

    # colunas esperadas para comparação
    compare_cols = [
        "VT (4)",
        "VC (3)",
        "SM (2)",
        "2x0 (1)",
        "2x0"
    ]

    # usa apenas as colunas que realmente existem na planilha
    valid_compare_cols = [c for c in compare_cols if c in compare_data.columns]

    compare_long = compare_data.melt(
        id_vars="MC",
        value_vars=valid_compare_cols,
        var_name="Resultado",
        value_name="Quantidade"
    )

    # traduz os nomes técnicos para leitura humana
    compare_long["Resultado"] = compare_long["Resultado"].map(result_map)

    # ordem fixa para leitura correta
    ordem_resultados = [
        "Títulos",
        "Vices",
        "Semifinais",
        "Vitórias 2x0"
    ]
    compare_long["Resultado"] = pd.Categorical(
    compare_long["Resultado"],
    categories=ordem_resultados,
    ordered=True
)

    fig_compare = px.bar(
        compare_long,
        x="Resultado",
        y="Quantidade",
        color="MC",
        barmode="group",
        text="Quantidade",
        category_orders={"Resultado": ordem_resultados},
        title="Comparação de Desempenho entre MCs",
        color_discrete_sequence=["#1DB954", "#7A1FA2"]  # verde + roxo LV
    )

    # ajustes visuais para melhorar leitura
    fig_compare.update_layout(
        bargap=0.35,
        bargroupgap=0.15,
        legend_title_text="MC",
        yaxis_title="Quantidade",
        xaxis_title="Resultado"
    )

    fig_compare.update_traces(
        textposition="outside"
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

components.html(
    """
    <div style="
        display:flex;
        justify-content:center;
        align-items:center;
        gap:24px;
        margin-top:30px;
        flex-wrap:wrap;
    ">

        <a href="https://www.instagram.com/largaoverbo" target="_blank" style="text-decoration:none;">
            <button style="
                background-color:#1DB954;
                color:white;
                border:none;
                padding:18px 32px;
                font-size:18px;
                font-weight:bold;
                border-radius:14px;
                cursor:pointer;
            ">
                📲 Instagram · Larga o Verbo
            </button>
        </a>

        <a href="https://www.youtube.com/@largaoverbolv" target="_blank" style="text-decoration:none;">
            <button style="
                background-color:#FF0000;
                color:white;
                border:none;
                padding:18px 32px;
                font-size:18px;
                font-weight:bold;
                border-radius:14px;
                cursor:pointer;
            ">
                ▶️ YouTube · Larga o Verbo
            </button>
        </a>

    </div>
    """,
    height=130
)





























