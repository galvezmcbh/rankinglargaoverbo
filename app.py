import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import re

# ─────────────────────────────────────────────
# CONFIGURAÇÕES GERAIS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Larga o Verbo | Dashboard",
    layout="wide"
)

# ─────────────────────────────────────────────
# ESTILO GLOBAL (verde + roxo LV)
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    body {
        background-color: #0f0f0f;
        color: #eaeaea;
    }

    /* Chip do multiselect */
    span[data-testid="stMultiSelectTag"] {
        background-color: #7A1FA2 !important;
        color: white !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }

    span[data-testid="stMultiSelectTag"] span {
        color: white !important;
    }

    span[data-testid="stMultiSelectTag"] svg {
        fill: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# MAPEAMENTO DOS INDICADORES
# ─────────────────────────────────────────────
result_map = {
    "VT (4)": "Vitórias",
    "VC (3)": "Vices",
    "SM (2)": "Semifinais",
    "2x0 (1)": "Vitórias 2x0",
    "2x0": "Vitórias 2x0"
}

ordem_resultados = [
    "Vitórias",
    "Vices",
    "Semifinais",
    "Vitórias 2x0"
]

# ─────────────────────────────────────────────
# MAPA DE ANOS → PLANILHAS
# ─────────────────────────────────────────────
arquivos_anos = {
    "2024": "RANKING_LARGA_O_VERBO_2024.xlsx",
    "2025": "RANKING_LARGA_O_VERBO_2025.xlsx",
    # "2026": "RANKING_LARGA_O_VERBO_2026.xlsx"
}

# ─────────────────────────────────────────────
# TOPO · FILTRO DE ANO
# ─────────────────────────────────────────────
st.title("💚 Ranking Larga o Verbo")
st.caption("Memória, performance e evolução histórica dos MCs")

ano_selecionado = st.selectbox(
    "📅 Selecione o ano do ranking",
    list(arquivos_anos.keys()),
    index=len(arquivos_anos) - 1
)

# ─────────────────────────────────────────────
# CARREGAMENTO DOS DADOS
# ─────────────────────────────────────────────
df = pd.read_excel(arquivos_anos[ano_selecionado])
df["Ano"] = int(ano_selecionado)
df.fillna(0, inplace=True)

# histórico completo
dfs_historicos = []
for ano, arquivo in arquivos_anos.items():
    temp = pd.read_excel(arquivo)
    temp["Ano"] = int(ano)
    temp.fillna(0, inplace=True)
    dfs_historicos.append(temp)

df_historico = pd.concat(dfs_historicos, ignore_index=True)

# ─────────────────────────────────────────────
# MÉTRICAS GERAIS
# ─────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

col1.metric("MCs no Ranking", len(df))
col2.metric("Líder do Ano", df.iloc[0]["MC"])
col3.metric("Mais Vitórias", df.loc[df["VT (4)"].idxmax()]["MC"])
col4.metric("Mais 2x0", df.loc[df["2x0 (1)"].idxmax()]["MC"])

st.divider()

# ─────────────────────────────────────────────
# RANKING GERAL
# ─────────────────────────────────────────────
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

# ─────────────────────────────────────────────
# ANÁLISE INDIVIDUAL
# ─────────────────────────────────────────────
st.subheader("🧬 Análise Individual")

mc_selected = st.selectbox(
    "Selecione um MC",
    sorted(df["MC"].unique())
)

mc_data = df[df["MC"] == mc_selected]

col1, col2 = st.columns(2)

# ── Gráfico de indicadores
with col1:
    valid_cols = [c for c in result_map if c in mc_data.columns]

    fig_mc = px.bar(
        mc_data.melt(id_vars="MC", value_vars=valid_cols),
        x="variable",
        y="value",
        text="value",
        color_discrete_sequence=["#7A1FA2"]
    )

    fig_mc.update_xaxes(
        tickvals=valid_cols,
        ticktext=[result_map[c] for c in valid_cols]
    )

    st.plotly_chart(fig_mc, use_container_width=True)

# ── Card de trajetória (edições)
with col2:
    texto = str(mc_data["Pontos contabilizados"].iloc[0]).lower()

    edicoes = sorted(
        set(int(e) for e in re.findall(r"\b\d{1,3}\b", texto))
    )

    total_edicoes = len(edicoes)
    primeira = min(edicoes) if edicoes else None
    ultima = max(edicoes) if edicoes else None
    intervalo = (ultima - primeira) if edicoes else 0

    if total_edicoes >= 8 and intervalo >= 15:
        perfil = "🎖️ MC Veterano"
    elif total_edicoes >= 6:
        perfil = "🔥 MC Constante"
    elif total_edicoes <= 4:
        perfil = "🌱 MC em Ascensão"
    else:
        perfil = "🌒 Participação Pontual"

    st.markdown(
        f"""
        <div style="
            display:flex;
            gap:24px;
            padding:24px;
            border-radius:18px;
            background:linear-gradient(135deg,#1DB95422,#6A0DAD22);
            border:2px solid #6A0DAD55;
        ">
            <div>
                <h3 style="color:#6A0DAD">{perfil}</h3>
                <p><strong>🎤 Edições:</strong> {total_edicoes}</p>
                <p><strong>📍 Primeira:</strong> {primeira}</p>
                <p><strong>📍 Última:</strong> {ultima}</p>
                <p><strong>⏱️ Intervalo:</strong> {intervalo}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# 📈 EVOLUÇÃO HISTÓRICA DO MC
# ─────────────────────────────────────────────
st.subheader("📈 Evolução Histórica do MC")

hist_mc = df_historico[df_historico["MC"] == mc_selected]

fig_hist = px.line(
    hist_mc,
    x="Ano",
    y="PTS",
    markers=True,
    color_discrete_sequence=["#1DB954"]
)

fig_hist.update_layout(
    yaxis_title="Pontuação",
    xaxis_title="Ano"
)

st.plotly_chart(fig_hist, use_container_width=True)

# ─────────────────────────────────────────────
# ⚔️ COMPARAÇÃO ENTRE MCs
# ─────────────────────────────────────────────
st.subheader("⚔️ Comparação entre MCs")

mc_compare = st.multiselect(
    "Selecione dois MCs",
    df["MC"].unique(),
    max_selections=2
)

if len(mc_compare) == 2:
    compare = df[df["MC"].isin(mc_compare)]

    cols = [c for c in result_map if c in compare.columns]

    long = compare.melt(
        id_vars="MC",
        value_vars=cols,
        var_name="Resultado",
        value_name="Quantidade"
    )

    long["Resultado"] = long["Resultado"].map(result_map)
    long["Resultado"] = pd.Categorical(long["Resultado"], ordem_resultados, True)

    fig_compare = px.bar(
        long,
        x="Resultado",
        y="Quantidade",
        color="MC",
        barmode="group",
        color_discrete_sequence=["#1DB954", "#7A1FA2"]
    )

    fig_compare.update_layout(bargap=0.35)
    st.plotly_chart(fig_compare, use_container_width=True)

# ─────────────────────────────────────────────
# RODAPÉ
# ─────────────────────────────────────────────
st.markdown("---")

components.html(
    """
    <div style="display:flex;justify-content:center;gap:24px;margin-top:30px;">
        <a href="https://www.instagram.com/largaoverbo" target="_blank">
            <button style="background:#1DB954;color:white;padding:18px 32px;
            border:none;border-radius:14px;font-size:18px;font-weight:bold;">
            📲 Instagram · Larga o Verbo
            </button>
        </a>
        <a href="https://www.youtube.com/@largaoverbolv" target="_blank">
            <button style="background:#7A1FA2;color:white;padding:18px 32px;
            border:none;border-radius:14px;font-size:18px;font-weight:bold;">
            ▶️ YouTube · Larga o Verbo
            </button>
        </a>
    </div>
    """,
    height=140
)
