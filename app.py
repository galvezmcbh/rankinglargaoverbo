
import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import os
import re
import streamlit as st
# ─────────────────────────────────────────────
# 🎯 DETECTOR CENTRALIZADO DE COLUNAS
# ─────────────────────────────────────────────
class DetectorColunas:
    """
    CLASSE ÚNICA para detectar e mapear todas as colunas do ranking.
    Substitui TODAS as detecções espalhadas pelo código.
    """
    
    # Padrões de busca organizados por prioridade
    PADROES = {
        'VITORIAS': ['VT', 'VITÓRIA', 'VITÓRIAS', 'VITORIA'],
        'VICES': ['VC', 'VICE', 'VICES'],
        'SEMIFINAIS': ['SM', 'SEMIFINAL', 'SEMIFINAIS', 'SF'],
        'QUARTAS': ['QF', 'QUARTA', 'QUARTAS', 'QUARTAFINAL'],
        'DOIS_X_ZERO': ['2X0', '2-0', 'DOIS A ZERO', '2X0'],
        'SEGUNDA_FASE': ['2ªF', '2AF', 'SEGUNDA FASE', 'SEGUNDAFASE'],
        'PONTOS': ['PTS', 'PONTOS', 'PONTUAÇÃO', 'SCORE', 'PONTUACAO'],
        'EDICOES': ['EDIÇÕES', 'PARTICIPAÇÕES', 'APARIÇÕES', 'PARTICIPACOES']
    }
    
    @staticmethod
    def detectar_todas(df):
        """
        Retorna dicionário {tipo: nome_da_coluna_real} para todas as colunas detectadas.
        Exemplo: {'VITORIAS': 'VT (4)', 'VICES': 'VC (3)'}
        """
        resultado = {}
        colunas_processadas = set()
        
        for tipo, padroes in DetectorColunas.PADROES.items():
            for padrao in padroes:
                encontrou = False
                for coluna_real in df.columns:
                    if coluna_real in colunas_processadas:
                        continue
                    
                    col_str = str(coluna_real).upper().strip()
                    if padrao in col_str:
                        resultado[tipo] = coluna_real
                        colunas_processadas.add(coluna_real)
                        encontrou = True
                        break
                
                if encontrou:
                    break
        
        return resultado
    
    @staticmethod
    def get_nome_amigavel(tipo_coluna):
        """Converte tipo técnico para nome amigável (ex: 'VITORIAS' → 'Vitórias')."""
        traducao = {
            'VITORIAS': 'Vitórias',
            'VICES': 'Vices', 
            'SEMIFINAIS': 'Semifinais',
            'QUARTAS': 'Quartas',
            'DOIS_X_ZERO': 'Vitórias 2x0',
            'SEGUNDA_FASE': '2ª Fase',
            'PONTOS': 'Pontos',
            'EDICOES': 'Edições'
        }
        return traducao.get(tipo_coluna, tipo_coluna)
    
    @staticmethod  
    def get_colunas_para_grafico(df, tipos=None):
        """
        Retorna (colunas_reais, nomes_amigaveis) para gráficos.
        Se 'tipos' for None, usa ordem padrão: Vitorias, Vices, Semifinais, 2x0
        """
        detectadas = DetectorColunas.detectar_todas(df)
        
        # Ordem padrão para gráficos (pode personalizar)
        if tipos is None:
            tipos = ['VITORIAS', 'VICES', 'SEMIFINAIS', 'DOIS_X_ZERO']
        
        colunas_grafico = []
        nomes_amigaveis = []
        
        for tipo in tipos:
            if tipo in detectadas:
                colunas_grafico.append(detectadas[tipo])
                nomes_amigaveis.append(DetectorColunas.get_nome_amigavel(tipo))
        
        return colunas_grafico, nomes_amigaveis
    
    @staticmethod
    def get_valor_mc(df, mc_nome, tipo_coluna):
        """Pega o valor de uma coluna específica para um MC."""
        detectadas = DetectorColunas.detectar_todas(df)
        
        if tipo_coluna not in detectadas:
            return 0
        
        coluna_real = detectadas[tipo_coluna]
        mc_data = df[df['MC'] == mc_nome]
        
        if mc_data.empty:
            return 0
        
        valor = mc_data.iloc[0].get(coluna_real, 0)
        return float(valor) if not pd.isna(valor) else 0

# ─────────────────────────────────────────────
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

st.set_page_config(
    page_title="Larga o Verbo | Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",  # ← NOVO
    menu_items={                        # ← NOVO
        'Get Help': None,
        'Report a bug': None, 
        'About': None
    }
)

# ─────────────────────────────────────────────
# OCULTAR MENU LATERAL COMPLETAMENTE          ← NOVO TÍTULO
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* 1. Oculta o menu lateral... */        ← NOVO CSS
    ...
    /* 8. Seu estilo original */             ← SEU CSS MANTIDO
    body {
        background-color:#0f0f0f;
        color:#eaeaea;
    }
    ...
    </style>
    """,
    unsafe_allow_html=True
)

st.session_state.sidebar_state = "collapsed"  # ← NOVA LINHA
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
# 🗃️ FUNÇÃO COM CACHE PARA DADOS HISTÓRICOS
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)  # Cache válido por 1 hora (3600 segundos)
def carregar_historico_completo(_arquivos_anos):
    """
    Carrega todos os dados históricos com cache.
    O underscore (_arquivos_anos) é necessário para objetos não hashable.
    """
    import pandas as pd
    
    dfs = []
    for ano, arq in _arquivos_anos.items():
        try:
            # Carrega o arquivo Excel
            temp = pd.read_excel(arq)
            
            # Padroniza nomes das colunas
            temp.columns = temp.columns.str.strip()
            
            # Preenche valores nulos
            temp.fillna(0, inplace=True)
            
            # Adiciona coluna de ano
            temp["Ano"] = int(ano)
            
            dfs.append(temp)
            
            # Log opcional (aparece apenas na primeira execução)
            print(f"✅ Carregado: {arq} ({ano})")
            
        except Exception as e:
            print(f"⚠️ Erro ao carregar {arq}: {str(e)}")
            continue
    
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()  # Retorna DataFrame vazio se não houver dados
# ─────────────────────────────────────────────
# TOPO
# ─────────────────────────────────────────────
st.title("💚 Ranking Larga o Verbo")
st.caption("Memória, performance e evolução histórica dos MCs")

ano_selecionado = st.selectbox(
    "📅 Selecione o ano do ranking",
    sorted(arquivos_anos.keys()),
    key="ano_selector"  # ← ADICIONE ESTA LINHA
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

# 2. DETECTAR COLUNAS usando a classe centralizada
detector = DetectorColunas()
colunas_detectadas = detector.detectar_todas(df)

# 3. Calcular métricas com colunas detectadas
coluna_vitorias = colunas_detectadas.get('VITORIAS')
coluna_2x0 = colunas_detectadas.get('DOIS_X_ZERO')

mais_vitorias = "—"
if coluna_vitorias and coluna_vitorias in df.columns:
    mais_vitorias = df.loc[df[coluna_vitorias].idxmax()]["MC"]

mais_2x0 = "—"
if coluna_2x0 and coluna_2x0 in df.columns:
    mais_2x0 = df.loc[df[coluna_2x0].idxmax()]["MC"]
    
# 5. Mantenha a métrica de vices (não mudou entre anos)
mais_vices = (
    df.loc[df["VC (3)"].idxmax()]["MC"]
    if "VC (3)" in df.columns else "—"
)

# ─────────────────────────────────────────────
# 📊 CARREGAMENTO COM CACHE
# ─────────────────────────────────────────────
# Mostra spinner apenas na primeira execução ou quando o cache expira
if 'df_historico' not in st.session_state:
    with st.spinner("🔄 Carregando dados históricos (isso acontece apenas na primeira vez ou após 1 hora)..."):
        df_historico = carregar_historico_completo(arquivos_anos)
        st.session_state.df_historico = df_historico
else:
    df_historico = st.session_state.df_historico

# Verifica se temos dados
if df_historico.empty:
    st.warning("⚠️ Nenhum dado histórico foi carregado.")

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
    st.markdown(
        """
        <a href="./Perfis_dos_MCs" target="_self" style="text-decoration: none; display: block;">
            <div style="
                background-color: #7A1FA2;
                color: white;
                padding: 10px 16px;
                border-radius: 8px;
                text-align: center;
                font-weight: 600;
                cursor: pointer;
                width: 100%;
                border: none;
                font-size: 14px;
                margin-top: 8px;
            ">
                📋 Ver Perfis Completos
            </div>
        </a>
        """,
        unsafe_allow_html=True
    )
# ←←←←←←←←←←←←← **ESTE SELECTBOX DEVE EXISTIR AQUI!** ←←←←←←←←←←←←←
mc_selected = st.selectbox(
    "Selecione um MC",
    sorted(df["MC"].unique()),
    key=f"mc_selector_{ano_selecionado}"  # ← CHAVE DINÂMICA
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

# ── Gráfico de indicadores (USANDO DETECTOR CENTRALIZADO)
with col1:
    # 1. USAR DETECTOR (reutiliza o mesmo detector criado antes)
    # Se detector não existir nesta seção, crie novamente:
    if 'detector' not in locals():
        detector = DetectorColunas()
    
    # 2. PEGAR COLUNAS PARA GRÁFICO
    colunas_grafico, nomes_amigaveis = detector.get_colunas_para_grafico(df)
    
    # 3. CRIAR GRÁFICO
    if colunas_grafico:
        # Pega valores do MC selecionado
        valores = [mc_row.get(col, 0) for col in colunas_grafico]
        
        fig_mc = px.bar(
            pd.DataFrame({
                "Resultado": nomes_amigaveis,
                "Quantidade": valores
            }),
            x="Resultado",
            y="Quantidade",
            text="Quantidade",
            color_discrete_sequence=["#7A1FA2"]
        )
        
        st.plotly_chart(fig_mc, use_container_width=True)
        
        # Mostra colunas reais usadas (opcional, para debug)
        st.caption(f"🎯 Colunas usadas: {', '.join(colunas_grafico)}")
    else:
        st.warning("Nenhuma coluna de desempenho encontrada.")
# ── criar card (USANDO DETECTOR CENTRALIZADO)
with col2:
    # 1. CALCULAR AS NOVAS MÉTRICAS (USANDO DETECTOR)
    # Reutiliza ou cria detector
    if 'detector' not in locals():
        detector = DetectorColunas()
        colunas_detectadas = detector.detectar_todas(df)
    elif 'colunas_detectadas' not in locals():
        colunas_detectadas = detector.detectar_todas(df)
    
    # Usa valores do detector
    numero_vitorias = int(detector.get_valor_mc(df, mc_selected, 'VITORIAS'))
    numero_vices = int(detector.get_valor_mc(df, mc_selected, 'VICES'))
    numero_finais = numero_vitorias + numero_vices
    numero_2x0 = int(detector.get_valor_mc(df, mc_selected, 'DOIS_X_ZERO'))
    
    # Calcula participações de forma mais limpa
    participacoes = 0
    tipos_participacao = ['VITORIAS', 'VICES', 'SEMIFINAIS', 'SEGUNDA_FASE']
    for tipo in tipos_participacao:
        participacoes += int(detector.get_valor_mc(df, mc_selected, tipo))
    
    tem_participacao = participacoes > 0
    
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
    
    # 3. CRIAR O HTML DO CARD
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
        <!-- ... (COLE AQUI TODO O HTML DO CARD ORIGINAL) ... -->
    </div>
    """
    
    # 4. EXIBIR O CARD
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
    # 1. DETECTAR COLUNAS usando detector centralizado
    if 'detector' not in locals():
        detector = DetectorColunas()
    
    colunas_para_comparar, nomes_amigaveis = detector.get_colunas_para_grafico(
        df, 
        tipos=['VITORIAS', 'VICES', 'SEMIFINAIS', 'DOIS_X_ZERO']
    )
    
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














































































































