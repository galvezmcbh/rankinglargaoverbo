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
    page_icon="🎤"
)

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
        {"tipo": "Instagram", "url": "https://instagram.com/galvezmcbh", "emoji": "📱"}
    ],
    "KVL": [
        {"tipo": "Instagram", "url": "https://instagram.com/kvl.mc", "emoji": "📱"},
        {"tipo": "YouTube", "url": "https://youtube.com/@kvl", "emoji": "▶️"}
    ],
    "Foco na Rima": [
        {"tipo": "Instagram", "url": "https://instagram.com/foconarima", "emoji": "📱"}
    ],
    "Gabriel Mirã": [
        {"tipo": "Instagram", "url": "https://instagram.com/gabrielmira", "emoji": "📱"}
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
    for prefixo, nome_amigavel in [("VT", "vitórias"), ("VC", "vices"), ("SM", "semifinais"), ("2x0", "2x0")]:
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
    """Gera um texto descritivo sobre o desempenho do MC"""
    textos = []
    
    if metricas["pontos"] > 40:
        textos.append(f"Potência do ranking com **{metricas['pontos']} pontos** acumulados.")
    elif metricas["pontos"] > 20:
        textos.append(f"Presença sólida com **{metricas['pontos']} pontos**.")
    else:
        textos.append(f"**{metricas['pontos']} pontos** no histórico.")
    
    if metricas["finais"] >= 5:
        textos.append(f"Finalista experiente com **{metricas['finais']} finais** disputadas.")
    elif metricas["finais"] >= 1:
        textos.append(f"Já chegou na final **{metricas['finais']} vez(es)**.")
    
    if metricas.get("2x0", 0) >= 3:
        textos.append(f"Estilo dominante: **{metricas['2x0']} vitórias 2x0**.")
    
    if metricas.get("vitórias", 0) >= 3:
        textos.append(f"Vencedor nato com **{metricas['vitórias']} vitórias**.")
    
    if metricas["ranking"] == 1:
        textos.append("**Já liderou o ranking!**")
    elif metricas["ranking"] and metricas["ranking"] <= 3:
        textos.append(f"Já esteve no **top {metricas['ranking']}** do ranking.")
    
    return " ".join(textos) if textos else "Em construção no Larga o Verbo."

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
                    
                    # Redes sociais
                    if row["MC"] in REDES_SOCIAIS:
                        st.divider()
                        st.markdown("#### 🔗 Redes Sociais")
                        for rede in REDES_SOCIAIS[row["MC"]]:
                            st.markdown(f"{rede['emoji']} [{rede['tipo']}]({rede['url']})")
    
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
                    
                    # Redes sociais
                    if row["MC"] in REDES_SOCIAIS:
                        st.divider()
                        st.markdown("#### 🔗 Redes Sociais")
                        for rede in REDES_SOCIAIS[row["MC"]]:
                            st.markdown(f"{rede['emoji']} [{rede['tipo']}]({rede['url']})")
    
    # Botão para adicionar redes sociais
    st.divider()
    with st.expander("✏️ Como adicionar redes sociais de um MC", expanded=False):
        st.markdown("""
        **Para adicionar redes sociais de um MC:**
        
        1. **Encontre o nome exato** do MC como aparece no ranking
        2. **No código acima**, localize o dicionário `REDES_SOCIAIS`
        3. **Adicione uma nova entrada** seguindo este formato:
        
        ```python
        "NOME DO MC": [
            {"tipo": "Instagram", "url": "https://instagram.com/usuario", "emoji": "📱"},
            {"tipo": "YouTube", "url": "https://youtube.com/@canal", "emoji": "▶️"},
            {"tipo": "TikTok", "url": "https://tiktok.com/@usuario", "emoji": "🎵"}
        ]
        ```
        
        **Dica:** Você pode adicionar quantas redes sociais quiser para cada MC!
        """)
        
else:
    st.error("Não foi possível carregar os dados do ranking. Verifique se os arquivos Excel existem.")

# ─────────────────────────────────────────────
# BOTÃO VOLTAR
# ─────────────────────────────────────────────
st.divider()
col_voltar, col_espaco = st.columns([1, 3])
with col_voltar:
    if st.button("⬅️ Voltar para o Dashboard Principal", type="primary"):
        st.switch_page("app.py")

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
