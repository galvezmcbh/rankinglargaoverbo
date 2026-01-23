import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import os
import re

# ─────────────────────────────────────────────
# CONFIGURAÇÕES GERAIS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Larga o Verbo | Dashboard",
    layout="wide"
)

# ─────────────────────────────────────────────
# ESTILO GLOBAL
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    body {
        background-color:#0f0f0f;
        color:#eaeaea;
    }
    span[data-testid="stMultiSelectTag"] {
        background-color:#7A1FA2 !important;
        color:white !important;
        border-radius:12px;
        font-weight:600;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# 🔍 DETECÇÃO AUTOMÁTICA DE PLANILHAS
# ─────────────────────────────────────────────
arquivos_anos = {}

for arq in os.listdir("."):
    if arq.lower().endswith(".xlsx"):
        match = re.search(r"(20\d{2})", arq)
        if match:
            arquivos_anos[match.group(1)] = arq

if not arquivos_anos:
    st.error("Nenhuma planilha .xlsx com ano no nome foi encontrada.")
    st.stop()

# ─────────────────────────────────────────────
# TOPO
# ─────────────────────────────────────────────
st.title("💚 Ranking Larga o Verbo")
st.caption("Memória, performance e evolução histórica dos MCs")

ano_selecionado = st.selectbox(
    "📅 Selecione o ano do ranking",
    sorted(arquivos_anos.keys())
)

arquivo_atual = arquivos_anos[ano_selecionado]

# ─────────────────────────────────────────────
# CARREGAMENTO DOS DADOS
# ─────────────────────────────────────────────
df = pd.read_excel(arquivo_atual)
df.columns = df.columns.str.strip()
df.fillna(0, inplace=True)
df["Ano"] = int(ano_selecionado)

# histórico completo
dfs = []
for ano, arq in arquivos_anos.items():
    temp = pd.read_excel(arq)
    temp.columns = temp.columns.str.strip()
    temp.fillna(0, inplace=True)
    temp["Ano"] = int(ano)
    dfs.append(temp)

df_historico = pd.concat(dfs, ignore_index=True)

# ─────────────────────────────────────────────
# MAPEAMENTO DE INDICADORES
# ─────────────────────────────────────────────
result_map = {
    "VT (4)": "Vitórias",
    "VC (3)": "Vices",
    "SM (2)": "Semifinais",
    "2x0 (1)": "Vitórias 2x0",
    "2x0": "Vitórias 2x0"
}

ordem_resultados = list(result_map.values())

# ─────────────────────────────────────────────
# RANKING
# ─────────────────────────────────────────────
st.subheader("🏆 Ranking Geral")

fig_rank = px.bar(
    df.sort_values("PTS"),
    x="PTS",
    y="MC",
    orientation="h",
    text="PTS",
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

mc_data = df[df["MC"] == mc_selected].iloc[0]

col1, col2 = st.columns(2)

# ── Gráfico
with col1:
    valid_cols = [c for c in result_map if c in df.columns]

    fig_mc = px.bar(
        pd.DataFrame({
            "Resultado": [result_map[c] for c in valid_cols],
            "Quantidade": [mc_data[c] for c in valid_cols]
        }),
        x="Resultado",
        y="Quantidade",
        text="Quantidade",
        color_discrete_sequence=["#7A1FA2"]
    )

    st.plotly_chart(fig_mc, use_container_width=True)

# ── Card de trajetória
with col2:
    texto = ""
    if "Pontos contabilizados" in df.columns:
        texto = str(mc_data["Pontos contabilizados"]).lower()

    edicoes = sorted(set(map(int, re.findall(r"\b\d{1,3}\b", texto))))

    total_edicoes = len(edicoes)
    primeira = min(edicoes) if edicoes else "—"
    ultima = max(edicoes) if edicoes else "—"
    intervalo = (ultima - primeira) if edicoes else 0

    if total_edicoes == 0:
        perfil = "Sem histórico"
    elif total_edicoes <= 2:
        perfil = "MC iniciante"
    elif total_edicoes >= 8 and intervalo >= 15:
        perfil = "MC veterano"
    elif total_edicoes >= 5:
        perfil = "MC constante"
    else:
        perfil = "MC em ascensão"

    st.markdown(
        f"""
        <div style="
            padding:24px;
            border-radius:18px;
            background:linear-gradient(135deg,#1DB95422,#6A0DAD22);
            border:2px solid #6A0DAD55;
        ">
            <h3 style="color:#6A0DAD">{perfil}</h3>
            <p><strong>🎤 Edições:</strong> {total_edicoes}</p>
            <p><strong>📍 Primeira:</strong> {primeira}</p>
            <p><strong>📍 Última:</strong> {ultima}</p>
            <p><strong>⏱️ Intervalo:</strong> {intervalo}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# 📈 EVOLUÇÃO HISTÓRICA
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

st.plotly_chart(fig_hist, use_container_width=True)

# ─────────────────────────────────────────────
# ⚔️ COMPARAÇÃO
# ─────────────────────────────────────────────
st.subheader("⚔️ Comparação entre MCs")

mc_compare = st.multiselect(
    "Selecione dois MCs",
    df["MC"].unique(),
    max_selections=2
)

if len(mc_compare) == 2:
    comp = df[df["MC"].isin(mc_compare)]
    cols = [c for c in result_map if c in df.columns]

    long = comp.melt(
        id_vars="MC",
        value_vars=cols,
        var_name="Resultado",
        value_name="Quantidade"
    )

    long["Resultado"] = long["Resultado"].map(result_map)

    fig_compare = px.bar(
        long,
        x="Resultado",
        y="Quantidade",
        color="MC",
        barmode="group",
        color_discrete_sequence=["#1DB954", "#7A1FA2"]
    )

    st.plotly_chart(fig_compare, use_container_width=True)
