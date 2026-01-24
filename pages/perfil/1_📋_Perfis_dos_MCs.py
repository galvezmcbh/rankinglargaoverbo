import streamlit as st
import pandas as pd
import os
import re

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Larga o Verbo | Perfis dos MCs",
    layout="wide"
)

# ─────────────────────────────────────────────
# ESTILO (igual ao app principal)
# ─────────────────────────────────────────────
st.markdown("""
<style>
body { background-color:#0f0f0f; color:#eaeaea; }
.stButton>button { 
    background-color:#7A1FA2; color:white; border-radius:8px;
    border:none; padding:8px 16px; font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARREGAR DADOS
# ─────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    """Carrega todos os dados dos anos disponíveis"""
    arquivos_anos = {}
    for arq in os.listdir("."):
        if arq.lower().endswith(".xlsx"):
            match = re.search(r"(20\d{2})", arq)
            if match:
                arquivos_anos[match.group(1)] = arq
    
    dfs = []
    for ano, arquivo in arquivos_anos.items():
        df = pd.read_excel(arquivo)
        df.columns = df.columns.str.strip()
        df.fillna(0, inplace=True)
        df["Ano"] = int(ano)
        dfs.append(df)
    
    return pd.concat(dfs, ignore_index=True), arquivos_anos

df_completo, arquivos = carregar_dados()

# ─────────────────────────────────────────────
# DICIONÁRIO DE REDES SOCIAIS (FÁCIL DE EDITAR!)
# ─────────────────────────────────────────────
# AQUI VOCÊ ADICIONA AS REDES SOCIAIS DOS MCs
# Formato: "NOME_NO_EXCEL": {"tipo": "Instagram", "url": "link"}
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
def calcular_metricas_mc(mc_nome, df_filtrado):
    """Calcula métricas resumidas para um MC"""
    if mc_nome not in df_filtrado["MC"].values:
        return None
    
    dados_mc = df_filtrado[df_filtrado["MC"] == mc_nome]
    
    # Encontrar colunas automaticamente
    metricas = {
        "nome": mc_nome,
        "pontos_totais": int(dados_mc["PTS"].iloc[0]) if "PTS" in dados_mc.columns else 0,
        "anos_ativos": list(dados_mc["Ano"].unique()),
        "melhor_posicao": int(dados_mc["Ranking"].min()) if "Ranking" in dados_mc.columns else None,
        "pior_posicao": int(dados_mc["Ranking"].max()) if "Ranking" in dados_mc.columns else None
    }
    
    # Detectar colunas de resultados
    for prefixo, nome_amigavel in [("VT", "Vitórias"), ("VC", "Vices"), ("SM", "Semifinais"), ("2x0", "2x0")]:
        for col in dados_mc.columns:
            if prefixo in str(col):
                metricas[nome_amigavel.lower()] = int(dados_mc[col].iloc[0])
                break
        else:
            metricas[nome_amigavel.lower()] = 0
    
    # Calcular finais
    metricas["finais"] = metricas.get("vitórias", 0) + metricas.get("vices", 0)
    
    return metricas

def gerar_texto_desempenho(metricas):
    """Gera um texto descritivo sobre o desempenho do MC"""
    textos = []
    
    if metricas["pontos_totais"] > 40:
        textos.append(f"Potência do ranking com **{metricas['pontos_totais']} pontos** acumulados.")
    elif metricas["pontos_totais"] > 20:
        textos.append(f"Presença sólida com **{metricas['pontos_totais']} pontos**.")
    else:
        textos.append(f"**{metricas['pontos_totais']} pontos** no histórico.")
    
    if metricas["finais"] >= 5:
        textos.append(f"Finalista experiente com **{metricas['finais']} finais** disputadas.")
    elif metricas["finais"] >= 1:
        textos.append(f"Já chegou na final **{metricas['finais']} vez(es)**.")
    
    if metricas.get("2x0", 0) >= 3:
        textos.append(f"Estilo dominante: **{metricas['2x0']} vitórias 2x0**.")
    
    if len(metricas["anos_ativos"]) >= 2:
        textos.append(f"Ativo desde **{min(metricas['anos_ativos'])}**.")
    
    if metricas["melhor_posicao"] == 1:
        textos.append("**Já liderou o ranking!**")
    elif metricas["melhor_posicao"] and metricas["melhor_posicao"] <= 3:
        textos.append(f"Já esteve no **top {metricas['melhor_posicao']}** do ranking.")
    
    return " ".join(textos) if textos else "Em construção no Larga o Verbo."

# ─────────────────────────────────────────────
# INTERFACE PRINCIPAL
# ─────────────────────────────────────────────
st.title("📋 Perfis dos MCs")
st.caption("Conheça os artistas do Larga o Verbo")

# Filtro por ano
anos_disponiveis = sorted(df_completo["Ano"].unique())
ano_selecionado = st.selectbox(
    "📅 Selecione o ano para visualizar o ranking",
    anos_disponiveis,
    index=len(anos_disponiveis)-1  # Último ano por padrão
)

# Filtrar dados
df_ano = df_completo[df_completo["Ano"] == ano_selecionado].copy()
df_ano = df_ano.sort_values("PTS", ascending=False)

# Lista de MCs
st.subheader(f"🏆 Ranking {ano_selecionado}")

# Criar colunas para a lista
col1, col2 = st.columns(2)
mcs_por_coluna = len(df_ano) // 2 + (len(df_ano) % 2)

with col1:
    for idx, row in df_ano.head(mcs_por_coluna).iterrows():
        with st.expander(f"**#{int(row['Ranking'])} {row['MC']}** - {int(row['PTS'])} pts", expanded=False):
            metricas = calcular_metricas_mc(row["MC"], df_ano)
            
            if metricas:
                # Métricas básicas
                st.markdown(f"**Pontuação:** {metricas['pontos_totais']} pts")
                st.markdown(f"**Vitórias:** {metricas.get('vitórias', 0)}")
                st.markdown(f"**Vices:** {metricas.get('vices', 0)}")
                st.markdown(f"**Finais:** {metricas['finais']}")
                st.markdown(f"**2x0:** {metricas.get('2x0', 0)}")
                
                # Texto de desempenho
                st.divider()
                st.markdown("### 🎤 Desempenho")
                st.write(gerar_texto_desempenho(metricas))
                
                # Redes sociais
                if row["MC"] in REDES_SOCIAIS:
                    st.divider()
                    st.markdown("### 🔗 Redes Sociais")
                    for rede in REDES_SOCIAIS[row["MC"]]:
                        st.markdown(f"{rede['emoji']} [{rede['tipo']}]({rede['url']})")

with col2:
    for idx, row in df_ano.tail(len(df_ano) - mcs_por_coluna).iterrows():
        with st.expander(f"**#{int(row['Ranking'])} {row['MC']}** - {int(row['PTS'])} pts", expanded=False):
            metricas = calcular_metricas_mc(row["MC"], df_ano)
            
            if metricas:
                # Métricas básicas
                st.markdown(f"**Pontuação:** {metricas['pontos_totais']} pts")
                st.markdown(f"**Vitórias:** {metricas.get('vitórias', 0)}")
                st.markdown(f"**Vices:** {metricas.get('vices', 0)}")
                st.markdown(f"**Finais:** {metricas['finais']}")
                st.markdown(f"**2x0:** {metricas.get('2x0', 0)}")
                
                # Texto de desempenho
                st.divider()
                st.markdown("### 🎤 Desempenho")
                st.write(gerar_texto_desempenho(metricas))
                
                # Redes sociais
                if row["MC"] in REDES_SOCIAIS:
                    st.divider()
                    st.markdown("### 🔗 Redes Sociais")
                    for rede in REDES_SOCIAIS[row["MC"]]:
                        st.markdown(f"{rede['emoji']} [{rede['tipo']}]({rede['url']})")

# ─────────────────────────────────────────────
# ESTATÍSTICAS GERAIS
# ─────────────────────────────────────────────
st.divider()
col_stats1, col_stats2, col_stats3 = st.columns(3)

with col_stats1:
    st.metric("Total de MCs", len(df_ano))

with col_stats2:
    media_pontos = df_ano["PTS"].mean()
    st.metric("Média de Pontos", f"{media_pontos:.1f}")

with col_stats3:
    mc_mais_pontos = df_ano.loc[df_ano["PTS"].idxmax(), "MC"]
    st.metric("Maior Pontuação", mc_mais_pontos)

# ─────────────────────────────────────────────
# BOTÃO VOLTAR
# ─────────────────────────────────────────────
st.divider()
if st.button("⬅️ Voltar para o Dashboard Principal"):
    st.switch_page("app.py")
