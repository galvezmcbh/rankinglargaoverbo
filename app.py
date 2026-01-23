import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import os
import re
def card_lv(titulo, valor, cor):
    st.markdown(
        f"""
        <div style="
            background-color:#1a1a1a;
            border-left:6px solid {cor};
            padding:16px 18px;
            border-radius:12px;
            height:100%;
        ">
            <p style="
                margin:0;
                font-size:14px;
                color:#bdbdbd;
                font-weight:600;
            ">
                {titulo}
            </p>
            <h2 style="
                margin:4px 0 0 0;
                color:white;
                font-size:28px;
            ">
                {valor}
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )

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

df = pd.read_excel(arquivos_anos[ano_selecionado])
df.columns = df.columns.str.strip()
df.fillna(0, inplace=True)
# ─────────────────────────────────────────────
# MÉTRICAS DO TOPO (AGORA DEFINIDAS)
# ─────────────────────────────────────────────

total_mcs = df["MC"].nunique()

lider_atual = (
    df.sort_values("PTS", ascending=False)
    .iloc[0]["MC"]
)

mais_vitorias = (
    df.loc[df["VT (4)"].idxmax()]["MC"]
    if "VT (4)" in df.columns else "—"
)

mais_vices = (
    df.loc[df["VC (3)"].idxmax()]["MC"]
    if "VC (3)" in df.columns else "—"
)

mais_2x0 = (
    df.loc[df["2x0 (1)"].idxmax()]["MC"]
    if "2x0 (1)" in df.columns else "—"
)

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
# MÉTRICAS DO TOPO (5 COLUNAS)
# ─────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    card_lv("MCs no Ranking", total_mcs, "#2ecc71")

with col2:
    card_lv("Líder Atual", lider_atual, "#8e44ad")

with col3:
    card_lv("Mais Vitórias", mais_vitorias, "#2ecc71")

with col4:
    card_lv("Mais 2x0", mais_2x0, "#8e44ad")

with col5:
    card_lv("Edições no Ano", df.shape[0], "#2ecc71")


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

mc_row = df[df["MC"] == mc_selected].iloc[0]

col1, col2 = st.columns(2)
import re

with col2:
    if "Pontos contabilizados" in df.columns:
        texto = " ".join(
            df[df["MC"] == mc_selected]["Pontos contabilizados"]
            .dropna()
            .astype(str)
            .tolist()
        )
    else:
        texto = ""

    texto_lower = texto.lower()

    # captura QUALQUER número solto (edições)
    edicoes_raw = re.findall(r"\b\d{1,3}\b", texto_lower)
    edicoes = sorted(set(int(e) for e in edicoes_raw))

    total_edicoes = len(edicoes)
    primeira_edicao = min(edicoes) if edicoes else "—"
    ultima_edicao = max(edicoes) if edicoes else "—"
    intervalo = (ultima_edicao - primeira_edicao) if total_edicoes >= 2 else 0

    # classificação
    if total_edicoes == 0:
        perfil_mc = "Sem histórico registrado"
    elif total_edicoes <= 2:
        perfil_mc = "MC iniciante"
    elif total_edicoes >= 8 and intervalo >= 10:
        perfil_mc = "MC veterano"
    elif total_edicoes >= 5:
        perfil_mc = "MC constante"
    else:
        perfil_mc = "MC em ascensão"


# métricas semânticas
vitorias = texto_lower.count("vitória")
vices = texto_lower.count("vice")
semifinais = texto_lower.count("semifinal")
especiais = texto_lower.count("especial")
if total_edicoes >= 8 and intervalo >= 15:
    perfil_mc = "Veterano"
elif total_edicoes >= 6:
    perfil_mc = "Constante"
elif total_edicoes >= 3:
    perfil_mc = "Em ascensão"
else:
    perfil_mc = "Participação pontual"

# ── Gráfico de indicadores
with col1:
    valid_cols = [c for c in result_map if c in df.columns]

    fig_mc = px.bar(
        pd.DataFrame({
            "Resultado": [result_map[c] for c in valid_cols],
            "Quantidade": [mc_row[c] for c in valid_cols]
        }),
        x="Resultado",
        y="Quantidade",
        text="Quantidade",
        color_discrete_sequence=["#7A1FA2"]
    )

    st.plotly_chart(fig_mc, use_container_width=True)

# ── Card de trajetória (corrigido)
with col2:
    texto = str(mc_row.get("Pontos contabilizados", "")).lower()

    numeros = [int(n) for n in re.findall(r"\b\d{1,3}\b", texto)]
    edicoes = sorted(set(n for n in numeros if 1 <= n <= 300))

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
            <p><strong>📍 Primeira edição:</strong> {primeira}</p>
            <p><strong>📍 Última edição:</strong> {ultima}</p>
            <p><strong>⏱️ Intervalo:</strong> {intervalo} edições</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# 📊 EVOLUÇÃO HISTÓRICA (GRÁFICO MELHOR)
# ─────────────────────────────────────────────
st.subheader("Evolução histórica do MC")
# ─────────────────────────────────────────────
# SELEÇÃO DO MC (ANÁLISE INDIVIDUAL)
# ─────────────────────────────────────────────

lista_mcs = sorted(df["MC"].unique())

mc_selecionado = st.selectbox(
    "🎤 Selecione o MC para análise individual",
    lista_mcs
)

df_mc_hist = df_historico[df_historico["MC"] == mc_selecionado]

st.line_chart(
    df_mc_hist.set_index("Ano")["Pontuação"],
    height=300
)


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

# ─────────────────────────────────────────────
# RODAPÉ · SOBRE O LARGA O VERBO
# ─────────────────────────────────────────────
st.markdown("---")

st.markdown(
    """
    > *Mais do que rima, o Larga o Verbo é espaço de voz, troca e construção cultural.*
    """
)

st.markdown(
    """
    O **Larga o Verbo** nasce como batalha de MCs e se consolida como um espaço de 
    formação, expressão e fortalecimento da cultura periférica, conectando arte, 
    juventude e território.
    """
)

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







