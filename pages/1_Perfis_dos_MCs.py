import streamlit as st
import pandas as pd
import os
import re

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Larga o Verbo | Perfis dos MCs",
    layout="wide",
    initial_sidebar_state="collapsed",  # Menu fechado
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# ─────────────────────────────────────────────
# BOTÃO VOLTAR FIXO NO TOPO
# ─────────────────────────────────────────────
col_voltar, col_titulo = st.columns([1, 4])
with col_voltar:
   if st.button("⬅️ Voltar", type="primary"):
    # Use navegação por URL (sempre funciona)
    st.markdown('<meta http-equiv="refresh" content="0; url=./">', unsafe_allow_html=True)
with col_titulo:
    st.title("📋 Perfis dos MCs")

# ─────────────────────────────────────────────
# ESTILO (igual ao app principal)
# ─────────────────────────────────────────────
st.markdown("""
<style>
body { background-color:#0f0f0f; color:#eaeaea; }
.stButton>button { 
    background-color:#7A1FA2 !important; 
    color:white !important; 
    border-radius:8px !important;
    border:none !important; 
    padding:8px 16px !important; 
    font-weight:600 !important;
}
[data-testid="stExpander"] {
    background-color:#1a1a1a !important;
    border:1px solid #333 !important;
    border-radius:10px !important;
    margin-bottom:10px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DICIONÁRIO DE REDES SOCIAIS (FÁCIL DE EDITAR!)
# ─────────────────────────────────────────────
# AQUI VOCÊ ADICIONA AS REDES SOCIAIS DOS MCs
# Formato: "NOME_NO_EXCEL": [{"tipo": "Instagram", "url": "link", "emoji": "📱"}]
# Pode adicionar quantas redes quiser por MC

REDES_SOCIAIS = {
    "Galvez": [
        {"tipo": "Instagram", "url": "https://instagram.com/galvez_mc", "emoji": "📱"}
    ],
    "KVL": [
        {"tipo": "Instagram", "url": "https://instagram.com/kvl.mc", "emoji": "📱"}
    ],
     
    "Foco na Rima": [
        {"tipo": "Instagram", "url": "https://instagram.com/foconarima", "emoji": "📱"}
    ],
    "Gabriel Mirã": [
        {"tipo": "Instagram", "url": "https://instagram.com/gabrielmiralm", "emoji": "📱"}
    ],
    "Nobert": [
        {"tipo": "Instagram", "url": "https://instagram.com/nobertmc", "emoji": "📱"}
    ],
    "Xinim": [
        {"tipo": "Instagram", "url": "https://instagram.com/xinimmc", "emoji": "📱"}
    ],
    # ADICIONE MAIS MCs AQUI!
    # Formato:
    # "NOME DO MC": [
    #     {"tipo": "Instagram", "url": "link", "emoji": "📱"},
    #     {"tipo": "YouTube", "url": "link", "emoji": "▶️"},
    #     {"tipo": "TikTok", "url": "link", "emoji": "🎵"}
    # ]
}
# ─────────────────────────────────────────────
# DICIONÁRIO DE TEXTOS PERSONALIZADOS POR MC
# ─────────────────────────────────────────────
# Aqui você pode adicionar textos personalizados para cada MC
# Se um MC não estiver aqui, será usado o texto automático

TEXTOS_PERSONALIZADOS = {
    "Galvez": """
    **Lenda viva do Larga o Verbo!** Com múltiplos títulos e presença constante nas finais,
    Galvez é referência técnica e de postura dentro do circuito. Sua evolução ao longo das
    edições mostra um MC que veio para ficar e ditar o ritmo das batalhas.
    """,
    
    "KVL": """
    **Potência criativa em microfone!** KVL combina flow preciso com letras afiadas,
    sendo um dos nomes mais consistentes do ranking. Sua capacidade de se reinventar
    a cada batalha faz dele um adversário temido por todos.
    """,
    
    "Foco na Rima": """
    **Técnica apurada e entrega intensa!** Conhecido pela preparação impecável e
    performances eletrizantes, Foco na Rima é sinônimo de profissionalismo no cenário.
    Cada aparição é aula de construção de personagem e timing.
    """,
    
    # ADICIONE MAIS MCs AQUI!
    # Formato:
    # "NOME DO MC": """
    #     Seu texto personalizado aqui.
    #     Pode ter múltiplas linhas.
    #     Use **negrito** e *itálico* se quiser.
    # """
}
# ─────────────────────────────────────────────
# FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────
@st.cache_data
def carregar_dados_ano(ano):
    """Carrega dados de um ano específico"""
    try:
        arquivo = f"RANKING_LARGA_O_VERBO_{ano}.xlsx"
        df = pd.read_excel(arquivo)
        df.columns = df.columns.str.strip()
        df.fillna(0, inplace=True)
        
        # Garantir que Ranking e PTS são numéricos
        df["Ranking"] = pd.to_numeric(df["Ranking"], errors='coerce')
        df["PTS"] = pd.to_numeric(df["PTS"], errors='coerce')
        
        return df.sort_values("PTS", ascending=False)
    except Exception as e:
        st.error(f"Erro ao carregar dados de {ano}: {str(e)}")
        return None

def calcular_metricas_mc(mc_nome, df):
    """Calcula métricas resumidas para um MC"""
    if df is None or mc_nome not in df["MC"].values:
        return None
    
    dados_mc = df[df["MC"] == mc_nome].iloc[0]
    
    # Detectar colunas automaticamente
    metricas = {
        "nome": mc_nome,
        "pontos": int(dados_mc["PTS"]) if pd.notna(dados_mc.get("PTS")) else 0,
        "ranking": int(dados_mc["Ranking"]) if pd.notna(dados_mc.get("Ranking")) else None,
        "anos": []  # Será preenchido depois
    }
    
    # Detectar colunas de resultados
    for prefixo, nome_amigavel in [("VT", "vitórias"), ("VC", "vices"), ("SM", "semifinais"), ("2x0", "2x0 (1)")]:
        valor = 0
        for col in df.columns:
            if str(col).upper().startswith(prefixo):
                val = dados_mc.get(col, 0)
                if pd.notna(val):
                    valor = int(val)
                break
        metricas[nome_amigavel] = valor
    
    # Calcular finais
    metricas["finais"] = metricas.get("vitórias", 0) + metricas.get("vices", 0)
    
    return metricas

def gerar_texto_desempenho(metricas):
    """Gera texto descritivo sobre o desempenho do MC"""
    
    # 1. PRIMEIRO: Verificar se tem texto personalizado
    mc_nome = metricas["nome"]
    if mc_nome in TEXTOS_PERSONALIZADOS:
        return TEXTOS_PERSONALIZADOS[mc_nome]
    
    # 2. SE NÃO: Gerar texto automático baseado nas métricas
    textos = []
    
    if metricas["pontos"] > 40:
        textos.append(f"**Potência do ranking** com **{metricas['pontos']} pontos** acumulados.")
    elif metricas["pontos"] > 20:
        textos.append(f"Presença sólida com **{metricas['pontos']} pontos** no histórico.")
    else:
        textos.append(f"**{metricas['pontos']} pontos** registrados no circuito.")
    
    if metricas["finais"] >= 5:
        textos.append(f"Finalista experiente com **{metricas['finais']} finais** disputadas.")
    elif metricas["finais"] >= 1:
        textos.append(f"Já chegou na final **{metricas['finais']} vez(es)**, mostrando potencial.")
    
    if metricas.get("2x0", 0) >= 3:
        textos.append(f"Estilo dominante com **{metricas['2x0']} vitórias 2x0**.")
    
    if metricas.get("vitórias", 0) >= 3:
        textos.append(f"Vencedor nato com **{metricas['vitórias']} conquistas**.")
    
    if metricas["ranking"] == 1:
        textos.append("**Já liderou o ranking**, mostrando superioridade técnica.")
    elif metricas["ranking"] and metricas["ranking"] <= 3:
        textos.append(f"Já esteve no **top {metricas['ranking']}** do ranking.")
    
    return " ".join(textos) if textos else "Em construção no Larga o Verbo, escrevendo sua história."

# ─────────────────────────────────────────────
# INTERFACE PRINCIPAL
# ─────────────────────────────────────────────
st.title("📋 Perfis dos MCs")
st.caption("Conheça os artistas do Larga o Verbo • Clique em cada MC para ver detalhes")

# Filtro por ano
anos_disponiveis = [2024, 2025]
ano_selecionado = st.selectbox(
    "📅 Selecione o ano para visualizar o ranking",
    anos_disponiveis,
    index=len(anos_disponiveis)-1
)

# Carregar dados
df_ano = carregar_dados_ano(ano_selecionado)

if df_ano is not None:
    # Estatísticas rápidas
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("Total de MCs", len(df_ano))
    with col_stats2:
        st.metric("Maior Pontuação", int(df_ano["PTS"].max()))
    with col_stats3:
        st.metric("Média de Pontos", f"{df_ano['PTS'].mean():.1f}")
    
    st.divider()
    
       # Lista de MCs em duas colunas
    st.subheader(f"🏆 Ranking {ano_selecionado}")
    
    # Dividir MCs em duas colunas
    col_esquerda, col_direita = st.columns(2)
    total_mcs = len(df_ano)
    metade = total_mcs // 2 + total_mcs % 2  # Arredonda para cima
    
    with col_esquerda:
        for idx, row in df_ano.head(metade).iterrows():
            metricas = calcular_metricas_mc(row["MC"], df_ano)
            
            with st.expander(f"**#{int(row['Ranking'])} {row['MC']}** - {int(row['PTS'])} pts", expanded=False):
                if metricas:
                    # Métricas em grid
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Pontuação", metricas["pontos"])
                        st.metric("Vitórias", metricas.get("vitórias", 0))
                    with col2:
                        st.metric("Finais", metricas["finais"])
                        st.metric("2x0", metricas.get("2x0", 0))
                    
                    # Texto de desempenho
                    st.divider()
                    st.markdown("#### 🎤 Desempenho")
                    st.write(gerar_texto_desempenho(metricas))
                    
                    # Redes sociais (se configuradas)
                    if row["MC"] in REDES_SOCIAIS:
                        st.divider()
                        st.markdown("#### 🔗 Conecte-se com o artista:")
                        
                        # Criar botões para cada rede social
                        col_redes = st.columns(len(REDES_SOCIAIS[row["MC"]]))
                        
                        for idx, rede in enumerate(REDES_SOCIAIS[row["MC"]]):
                            with col_redes[idx]:
                                # Botão estilizado
                                st.markdown(
                                    f"""
                                    <a href="{rede['url']}" target="_blank" style="text-decoration: none;">
                                        <div style="
                                            background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
                                            border: 1px solid #7A1FA255;
                                            border-radius: 10px;
                                            padding: 12px 8px;
                                            text-align: center;
                                            color: white;
                                            cursor: pointer;
                                            transition: all 0.3s ease;
                                            height: 100%;
                                        "
                                        onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(122, 31, 162, 0.3)';"
                                        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';"
                                        >
                                            <div style="font-size: 24px; margin-bottom: 6px;">
                                                {rede['emoji']}
                                            </div>
                                            <div style="font-size: 12px; font-weight: 600;">
                                                {rede['tipo']}
                                            </div>
                                        </div>
                                    </a>
                                    """,
                                    unsafe_allow_html=True
                                )
    
    # 🔴 🔴 🔴 AQUI ESTAVA FALTANDO - COLUNA DIREITA 🔴 🔴 🔴
    with col_direita:
        for idx, row in df_ano.tail(total_mcs - metade).iterrows():
            metricas = calcular_metricas_mc(row["MC"], df_ano)
            
            with st.expander(f"**#{int(row['Ranking'])} {row['MC']}** - {int(row['PTS'])} pts", expanded=False):
                if metricas:
                    # Métricas em grid
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Pontuação", metricas["pontos"])
                        st.metric("Vitórias", metricas.get("vitórias", 0))
                    with col2:
                        st.metric("Finais", metricas["finais"])
                        st.metric("2x0", metricas.get("2x0", 0))
                    
                    # Texto de desempenho
                    st.divider()
                    st.markdown("#### 🎤 Desempenho")
                    st.write(gerar_texto_desempenho(metricas))
                    
                    # Redes sociais (se configuradas)
                    if row["MC"] in REDES_SOCIAIS:
                        st.divider()
                        st.markdown("#### 🔗 Conecte-se com o artista:")
                        
                        # Criar botões para cada rede social
                        col_redes = st.columns(len(REDES_SOCIAIS[row["MC"]]))
                        
                        for idx, rede in enumerate(REDES_SOCIAIS[row["MC"]]):
                            with col_redes[idx]:
                                # Botão estilizado
                                st.markdown(
                                    f"""
                                    <a href="{rede['url']}" target="_blank" style="text-decoration: none;">
                                        <div style="
                                            background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
                                            border: 1px solid #7A1FA255;
                                            border-radius: 10px;
                                            padding: 12px 8px;
                                            text-align: center;
                                            color: white;
                                            cursor: pointer;
                                            transition: all 0.3s ease;
                                            height: 100%;
                                        "
                                        onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(122, 31, 162, 0.3)';"
                                        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';"
                                        >
                                            <div style="font-size: 24px; margin-bottom: 6px;">
                                                {rede['emoji']}
                                            </div>
                                            <div style="font-size: 12px; font-weight: 600;">
                                                {rede['tipo']}
                                            </div>
                                        </div>
                                    </a>
                                    """,
                                    unsafe_allow_html=True
                                )
    
    # ─────────────────────────────────────────────
    # RODAPÉ
    # ─────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align:center; color:#888; font-size:12px;">
            💚 Larga o Verbo • Dashboard Oficial • {ano}<br>
            <small>Atualizado automaticamente a partir das planilhas oficiais</small>
        </div>
        """.format(ano=ano_selecionado),
        unsafe_allow_html=True
    )
