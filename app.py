
import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import os
import re
import streamlit as st

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

    /* COR ROXA PARA CARDS SELECIONADOS - VERSÃO CORRIGIDA */
    div[data-baseweb="select"] span[role="button"] {
        background-color:#7A1FA2 !important;
        color:white !important;
        border-radius:12px !important;
        font-weight:600 !important;
        border:none !important;
        padding:4px 10px !important;
        margin:2px 4px !important;
    }
    
    /* Efeito hover */
    div[data-baseweb="select"] span[role="button"]:hover {
        background-color:#6A0DAD !important;
    }
    
    /* Remove qualquer estilo antigo */
    span[data-testid="stMultiSelectTag"] {
        background-color:transparent !important;
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
col_titulo, col_botao = st.columns([4, 1])
with col_titulo:
    st.subheader("🧬 Análise Individual")
with col_botao:
    # Botão que navega para a página de perfis
    if st.button("📋 Ver Perfis Completos", use_container_width=True, key="btn_perfis"):
        # Navegação direta sem mostrar menu lateral
        st.markdown('<meta http-equiv="refresh" content="0; url=/1_Perfis_dos_MCs">', 
                   unsafe_allow_html=True)

# ←←←←←←←←←←←←← **ESTE SELECTBOX DEVE EXISTIR AQUI!** ←←←←←←←←←←←←←
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

# ── CARD FINAL: Perfil Poético do MC
with col2:
    # 1. CALCULAR AS NOVAS MÉTRICAS
    coluna_vt = None
    for col in df.columns:
        if str(col).strip().upper().startswith('VT'):
            coluna_vt = col
            break
    
    numero_vitorias = int(mc_row.get(coluna_vt, 0)) if coluna_vt else 0
    numero_vices = int(mc_row.get("VC (3)", 0))
    numero_finais = numero_vitorias + numero_vices
    
    coluna_2x0 = None
    for col in df.columns:
        if '2x0' in str(col).lower():
            coluna_2x0 = col
            break
    numero_2x0 = int(mc_row.get(coluna_2x0, 0)) if coluna_2x0 else 0
    
    participacoes = 0
    for col in ["VT", "VC", "SM", "2ªF"]:
        for col_real in df.columns:
            if col in str(col_real):
                valor = mc_row.get(col_real, 0)
                participacoes += int(valor) if not pd.isna(valor) else 0
    
    tem_participacao = False
    for col in ["VT", "VC", "SM", "2ªF"]:
        for col_real in df.columns:
            if col in str(col_real):
                valor = mc_row.get(col_real, 0)
                if not pd.isna(valor) and int(valor) > 0:
                    tem_participacao = True
                    break
        if tem_participacao:
            break
    
       # 2. SISTEMA DE CLASSIFICAÇÃO COM LÍDER GARANTIDO COMO LENDA
    # Verificar se é o LÍDER DO RANKING ATUAL
    lider_do_ranking = df.sort_values("PTS", ascending=False).iloc[0]["MC"]
    eh_lider = mc_selected == lider_do_ranking
    
    # LÓGICA DE CLASSIFICAÇÃO (LÍDER TEM PRIORIDADE ABSOLUTA)
    if eh_lider:
        perfil = "🏆 Líder Atual - Lenda Consagrada"
        descricao = "Líder do ranking! Microfone que dita a lei, referência absoluta do circuito."
        cor_titulo = "#FFD700"
        emoji = "🏆"
    elif numero_finais >= 8:
        perfil = "🏆 Dono do Pódio - Lenda Consagrada"
        descricao = "Microfone que dita a lei, referência absoluta do circuito."
        cor_titulo = "#FFD700"
        emoji = "🏆"
    elif numero_finais >= 6:
        perfil = "🎤 Voz da Final - Pressão Constante"
        descricao = "Sempre no embate decisivo, pressiona os grandes."
        cor_titulo = "#1DB954"
        emoji = "🎤"
    elif numero_2x0 >= 4:
        perfil = "🔊 Dominador Absoluto - Aplica o 2x0"
        descricao = "Quando sobe no palco, a plateia já sabe: vai ser arraso."
        cor_titulo = "#7A1FA2"
        emoji = "🔊"
    elif numero_vitorias >= 1 and participacoes <= 3:  # NOVA CATEGORIA
        perfil = "⚡ Vitorioso de Passagem - Impacto Imediato"
        descricao = "Poucas aparições, mas quando veio, veio pra vencer. Deixou marca."
        cor_titulo = "#FF6B00"  # Laranja forte
        emoji = "⚡"
    elif participacoes >= 9:
        perfil = "📀 Guerreiro da Roda - Construção Diária"
        descricao = "Presença que fortalece o coletivo, base do movimento."
        cor_titulo = "#3498db"
        emoji = "📀"
    elif numero_finais >= 3:
        perfil = "💿 Promessa Concretizada - Sangue de Finalista"
        descricao = "Provou que tem o sangue, chegou onde poucos chegam."
        cor_titulo = "#e74c3c"
        emoji = "💿"
    elif participacoes >= 4:
        perfil = "🎚️ Voz em Ascensão - Crescendo no Ritmo"
        descricao = "Frequência que aumenta, aprendizado em cada batalha."
        cor_titulo = "#2ecc71"
        emoji = "🎚️"
    elif tem_participacao:
        perfil = "💚 Semente na Roda - Brotando no Microfone"
        descricao = "Já entrou na roda, construindo sua história no coletivo."
        cor_titulo = "#1DB954"
        emoji = "💚"
    else:
        perfil = "🎧 Presença no Radar - Olho no Talento"
        descricao = "Nome no ranking, potencial sendo observado pelo coletivo."
        cor_titulo = "#f39c12"
        emoji = "🎧"
    
     # 3. CRIAR E EXIBIR O CARD (VERSÃO CORRIGIDA)
    import streamlit.components.v1 as components
    
    card_html = f"""
    <div style="
        padding:24px;
        border-radius:20px;
        background: linear-gradient(145deg, #0f0f0f, #1a1a1a);
        border: 2px solid {cor_titulo}55;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        height:380px;
        font-family: Arial, sans-serif;
    ">
        <div style="text-align:center; font-size:36px; margin-bottom:10px;">
            {emoji}
        </div>
        
        <h3 style="
            color:{cor_titulo};
            margin-top:0;
            margin-bottom:14px;
            font-size:22px;
            text-align:center;
            font-weight:800;
            line-height:1.2;
        ">
            {perfil}
        </h3>
        
        <p style="
            color:#bdbdbd;
            font-style:italic;
            text-align:center;
            margin-bottom:28px;
            font-size:15px;
            line-height:1.5;
            padding:0 8px;
        ">
            {descricao}
        </p>
        
        <div style="
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
            margin-top: 20px;
        ">
            <div style="text-align:center;">
                <div style="font-size:14px;color:#aaa;margin-bottom:6px;font-weight:600;">🎤 FINAIS</div>
                <div style="font-size:32px;font-weight:bold;color:#1DB954;line-height:1;">{numero_finais}</div>
                <div style="font-size:12px;color:#777;margin-top:4px;">(VITÓRIAS + VICES)</div>
            </div>
            
            <div style="text-align:center;">
                <div style="font-size:14px;color:#aaa;margin-bottom:6px;font-weight:600;">🔊 2x0</div>
                <div style="font-size:32px;font-weight:bold;color:#7A1FA2;line-height:1;">{numero_2x0}</div>
                <div style="font-size:12px;color:#777;margin-top:4px;">DOMINÂNCIA</div>
            </div>
            
            <div style="text-align:center;">
                <div style="font-size:14px;color:#aaa;margin-bottom:6px;font-weight:600;">🏆 VITÓRIAS</div>
                <div style="font-size:32px;font-weight:bold;color:#FFD700;line-height:1;">{numero_vitorias}</div>
                <div style="font-size:12px;color:#777;margin-top:4px;">NO TOPO</div>
            </div>
            
            <div style="text-align:center;">
                <div style="font-size:14px;color:#aaa;margin-bottom:6px;font-weight:600;">📀 EDIÇÕES</div>
                <div style="font-size:32px;font-weight:bold;color:#3498db;line-height:1;">{participacoes}</div>
                <div style="font-size:12px;color:#777;margin-top:4px;">PRESENÇAS</div>
            </div>
        </div>
        
        <div style="
            margin-top:28px;
            padding-top:18px;
            border-top:1px solid #333;
            text-align:center;
        ">
            <div style="font-size:13px;color:#888;font-style:italic;font-weight:500;">
                {mc_selected} • Larga o Verbo {ano_selecionado}
            </div>
        </div>
    </div>
    """
    
    # 4. EXIBIR O CARD - NOME DA VARIÁVEL CORRIGIDO
    components.html(card_html, height=420)

# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# ⚔️ COMPARAÇÃO ENTRE MCs (ATUALIZADO)
# ─────────────────────────────────────────────
st.subheader("⚔️ Comparação entre MCs")

mc_compare = st.multiselect(
    "Selecione até 4 MCs para comparar",
    df["MC"].unique(),
    max_selections=4
)

if len(mc_compare) >= 2:
    # 1. DETECTAR COLUNAS DINAMICAMENTE (igual ao gráfico individual)
    colunas_para_comparar = []
    nomes_amigaveis = []
    
    # Mapeamento flexível (mesma lógica do gráfico individual)
    mapeamento_flex = {
        'Vitórias': ['VT', 'VITÓRIA', 'VITÓRIAS'],
        'Vices': ['VC', 'VICE', 'VICES'],
        'Semifinais': ['SM', 'SEMIFINAL', 'SEMIFINAIS'],
        '2ª Fase': ['2ªF', '2ª FASE', 'SEGUNDA FASE'],
        'Vitórias 2x0': ['2x0', '2X0']
    }
    
    # Encontrar colunas reais
    for nome_amigavel, padroes in mapeamento_flex.items():
        encontrou = False
        for padrao in padroes:
            for coluna_real in df.columns:
                if padrao in str(coluna_real).upper():
                    colunas_para_comparar.append(coluna_real)
                    nomes_amigaveis.append(nome_amigavel)
                    encontrou = True
                    break
            if encontrou:
                break
    
    if colunas_para_comparar:
        # 2. PREPARAR DADOS
        comp = df[df["MC"].isin(mc_compare)]
        
        # Transformar para formato longo
        dados_longos = []
        for _, row in comp.iterrows():
            for col_real, nome_amig in zip(colunas_para_comparar, nomes_amigaveis):
                dados_longos.append({
                    "MC": row["MC"],
                    "Resultado": nome_amig,
                    "Quantidade": row.get(col_real, 0)
                })
        
        df_long = pd.DataFrame(dados_longos)
        
        # 3. CRIAR GRÁFICO (mantendo a estética original)
        fig_compare = px.bar(
            df_long,
            x="Resultado",
            y="Quantidade",
            color="MC",
            barmode="group",
            color_discrete_sequence=["#1DB954", "#7A1FA2", "#FF6B00", "#3498db"][:len(mc_compare)]
        )
        
        # Configurações visuais (iguais ao original)
        fig_compare.update_layout(
            xaxis_title=None,
            yaxis_title="Quantidade",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#eaeaea',
            legend_title_text="MCs"
        )
        
        st.plotly_chart(fig_compare, use_container_width=True)
    else:
        st.warning("Não foi possível detectar colunas para comparação.")

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






























































































