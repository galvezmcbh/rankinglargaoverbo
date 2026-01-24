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
# MÉTRICAS DO TOPO (COM DETECÇÃO INTELIGENTE)
# ─────────────────────────────────────────────

total_mcs = df["MC"].nunique()

# 1. Líder atual (mantido igual)
lider_atual = (
    df.sort_values("PTS", ascending=False)
    .iloc[0]["MC"]
)

# 2. DETECTAR COLUNA DE VITÓRIAS automaticamente
coluna_vitorias = None
for col in df.columns:
    if str(col).strip().upper().startswith('VT'):
        coluna_vitorias = col
        break

# 3. DETECTAR COLUNA DE VITÓRIAS 2x0 automaticamente  
coluna_2x0 = None
for col in df.columns:
    if '2x0' in str(col).lower():
        coluna_2x0 = col
        break

# 4. Calcular métricas com colunas detectadas
if coluna_vitorias:
    mais_vitorias = df.loc[df[coluna_vitorias].idxmax()]["MC"]
else:
    mais_vitorias = "—"

if coluna_2x0 and coluna_2x0 in df.columns:
    mais_2x0 = df.loc[df[coluna_2x0].idxmax()]["MC"]
else:
    mais_2x0 = "—"

# 5. Mantenha a métrica de vices (não mudou entre anos)
mais_vices = (
    df.loc[df["VC (3)"].idxmax()]["MC"]
    if "VC (3)" in df.columns else "—"
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
col1, col2, col3, col4 = st.columns(4)

with col1:
    card_lv("MCs no Ranking", total_mcs, "#2ecc71")

with col2:
    card_lv("Líder Atual", lider_atual, "#8e44ad")

with col3:
    card_lv("Mais Vitórias", mais_vitorias, "#2ecc71")

with col4:
    card_lv("Mais 2x0", mais_2x0, "#8e44ad")



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

# ── Gráfico de indicadores (DETECÇÃO FLEXÍVEL)
with col1:
    # 1. ENCONTRAR COLUNAS REAIS usando o mapeamento original
    colunas_encontradas = []
    nomes_amigaveis = []
    
    for col_original, nome_amigavel in result_map.items():
        if col_original in df.columns:
            colunas_encontradas.append(col_original)
            nomes_amigaveis.append(nome_amigavel)
        else:
            # Se não encontrar, tenta variações
            for col_real in df.columns:
                # Procura por padrões similares
                if 'VT' in col_original and 'VT' in str(col_real):
                    colunas_encontradas.append(col_real)
                    nomes_amigaveis.append('Vitórias')
                    break
                elif col_original in str(col_real):
                    colunas_encontradas.append(col_real)
                    nomes_amigaveis.append(nome_amigavel)
                    break
    
    # 2. CRIAR GRÁFICO (MANTENDO INFORMAÇÃO ORIGINAL)
    if colunas_encontradas:
        fig_mc = px.bar(
            pd.DataFrame({
                "Resultado": nomes_amigaveis,
                "Quantidade": [mc_row[c] for c in colunas_encontradas]
            }),
            x="Resultado",
            y="Quantidade",
            text="Quantidade",
            color_discrete_sequence=["#7A1FA2"]
        )
        
        # 3. MANTÉM A INFORMAÇÃO ORIGINAL ABAIXO DO GRÁFICO
        st.plotly_chart(fig_mc, use_container_width=True)
        
        # Esta parte mostra a informação interna (controle)
        st.caption(f"🎯 Colunas detectadas: {', '.join(colunas_encontradas)}")
    else:
        st.warning("Nenhuma coluna de desempenho encontrada.")

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
# ✨ FRASE DE DESTAQUE
# ─────────────────────────────────────────────
st.markdown(
    """
    <div style="
        margin-top:40px;
        text-align:center;
        font-size:15px;
        color:#bdbdbd;
        font-style:italic;
    ">
        Mais do que rima, o Larga o Verbo é espaço de voz, troca e construção cultural.
    </div>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# 📌 MINI BIO · LARGA O VERBO
# ─────────────────────────────────────────────
st.markdown(
    """
    <div style="
        margin-top:30px;
        max-width:900px;
        margin-left:auto;
        margin-right:auto;
        background:linear-gradient(135deg,#1DB95411,#7A1FA211);
        padding:28px;
        border-radius:18px;
        border:1px solid #7A1FA244;
    ">
        <h3 style="color:#1DB954;text-align:center;">
            💚 Larga o Verbo
        </h3>
        <p style="text-align:justify;">
            O Larga o Verbo é um movimento cultural que teve início em agosto de 2022,
            originalmente como uma batalha de MCs. Ao longo de nossa trajetória,
            percebemos que o LV vai além do elemento da rima, tornando-se um espaço de
            fortalecimento e valorização das expressões culturais periféricas e marginais.
        </p>
        <p style="text-align:justify;">
            Nosso foco é fomentar iniciativas que dialoguem diretamente com a juventude
            local, promovendo ações que englobem tanto os elementos da cultura Hip Hop
            quanto outras manifestações culturais relevantes.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────
# 🔗 BOTÕES CENTRALIZADOS (HTML PURO)
# ─────────────────────────────────────────────
components.html(
    """
    <div style="
        display:flex;
        justify-content:center;
        align-items:center;
        gap:16px;
        margin-top:30px;
    ">
        <a href="https://www.instagram.com/largaoverbo" target="_blank">
            <button style="
                background-color:#1DB954;
                color:white;
                padding:14px 26px;
                border:none;
                border-radius:12px;
                font-size:16px;
                font-weight:600;
                cursor:pointer;
            ">
                📲 Instagram
            </button>
        </a>

        <a href="https://www.youtube.com/@largaoverbolv" target="_blank">
            <button style="
                background-color:#7A1FA2;
                color:white;
                padding:14px 26px;
                border:none;
                border-radius:12px;
                font-size:16px;
                font-weight:600;
                cursor:pointer;
            ">
                ▶️ YouTube
            </button>
        </a>
    </div>
    """,
    height=120
)




















