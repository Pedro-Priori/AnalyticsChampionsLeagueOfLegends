import pandas as pd
import requests 
import streamlit as st

# -------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------------------------------------------
st.set_page_config(layout="wide")

# -------------------------------------------------------------------
# FUNÇÕES DE CARREGAMENTO DE DADOS (Com @st.cache_data)
# -------------------------------------------------------------------
@st.cache_data
def carregar_dados(caminho_do_ficheiro):
    """
    Carrega os dados do ficheiro Excel ou CSV.
    """
    try:
        if caminho_do_ficheiro.endswith('.xlsx'):
            df = pd.read_excel(caminho_do_ficheiro)
            return df
        elif caminho_do_ficheiro.endswith('.csv'):
            df = pd.read_csv(caminho_do_ficheiro)
            return df
    except FileNotFoundError:
        print(f"Erro Ficheiro não encontrado: {caminho_do_ficheiro}")
        return None
    except Exception as e:
        print(f"Erro ao ler o ficheiro: {e}")
        return None

@st.cache_data
def carregar_mapeamento_itens():
    """
    Descarrega o dicionário de itens do Data Dragon.
    Retorna o mapeamento E a versão.
    """
    try:
        url_versoes = "https://ddragon.leagueoflegends.com/api/versions.json"
        resposta_versoes = requests.get(url_versoes)
        resposta_versoes.raise_for_status()
        versao_recente = resposta_versoes.json()[0]
        
        URL_API = f"https://ddragon.leagueoflegends.com/cdn/{versao_recente}/data/en_US/item.json"
        
        resposta_itens = requests.get(URL_API)
        resposta_itens.raise_for_status() 
        dados_json = resposta_itens.json()
        itens_data_dragon = dados_json['data']
        
        mapeamento_itens = {}
        for id_item_str, info_item in itens_data_dragon.items():
            id_item_int = int(id_item_str)
            mapeamento_itens[id_item_int] = info_item['name']
            
        return mapeamento_itens, versao_recente
        
    except Exception as e:
        print(f"Erro ao carregar itens: {e}") 
        return None, None

# -------------------------------------------------------------------
# FUNÇÕES DE ANÁLISE 
# -------------------------------------------------------------------
def analisar_taxa_vitoria(df, min_jogos):
    contagem_jogos = df.groupby('champion_name').size()
    campeoes_relevantes = contagem_jogos[contagem_jogos >= min_jogos].index
    df_relevante = df[df['champion_name'].isin(campeoes_relevantes)]
    if df_relevante.empty: return None, None
    agrupado_por_campeao = df_relevante.groupby('champion_name')
    taxas_vitoria = agrupado_por_campeao['win'].mean()
    taxas_vitoria_perc = (taxas_vitoria * 100).sort_values(ascending=False)
    return taxas_vitoria_perc.round(2), contagem_jogos

def analisar_itens_campeao(df, nome_do_campeao, mapeamento_itens):
    df_campeao = df[df['champion_name'] == nome_do_campeao]
    if df_campeao.empty: return None
    colunas_itens = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']
    todos_os_itens = df_campeao[colunas_itens].stack()
    contagem_itens = todos_os_itens.value_counts()
    if 0 in contagem_itens: contagem_itens = contagem_itens.drop(0)
    if mapeamento_itens:
        contagem_nomeada = contagem_itens.rename(index=mapeamento_itens)
        df_itens = contagem_nomeada.to_frame(name='Contagem')
        df_itens.index.name = 'Item'
        return df_itens
    else:
        return contagem_itens.to_frame(name='Contagem')

def analisar_kda_campeoes(df, min_jogos):
    contagem_jogos = df.groupby('champion_name').size()
    campeoes_relevantes = contagem_jogos[contagem_jogos >= min_jogos].index
    df_relevante = df[df['champion_name'].isin(campeoes_relevantes)]
    if df_relevante.empty: return None
    try:
        media_stats = df_relevante.groupby('champion_name')[['kills', 'deaths', 'assists']].mean()
        media_stats['deaths_para_kda'] = media_stats['deaths'].replace(0, 1)
        media_stats['kda'] = (media_stats['kills'] + media_stats['assists']) / media_stats['deaths_para_kda']
        media_stats = media_stats.round(2).sort_values(by='kda', ascending=False)
        return media_stats[['kills', 'deaths', 'assists', 'kda']]
    except Exception: return None

# -------------------------------------------------------------------
# DASHBOARD (LÓGICA PRINCIPAL)
# -------------------------------------------------------------------

st.title("🎮 Painel de Análise de League of Legends")

# --- 1. Carregar os Dados ---
with st.spinner('A carregar os dados das partidas (pode demorar)...'):
    NOME_DO_FICHEIRO = r"C:\Users\raian.felipe\Desktop\analise escola\analise-pedro\lol_match_data_2024.xlsx"
    dados_brutos = carregar_dados(NOME_DO_FICHEIRO)
    if dados_brutos is None:
        st.error(f"Falha ao carregar os dados. Verifica o caminho: {NOME_DO_FICHEIRO}")

with st.spinner('A descarregar nomes dos itens da Riot...'):
    mapeamento_de_itens, versao_itens = carregar_mapeamento_itens()
    if mapeamento_de_itens is not None:
        st.toast(f"Nomes dos itens carregados (Versão LoL: {versao_itens})")
    else:
        st.error("Erro ao descarregar nomes dos itens. A análise mostrará IDs.")


if dados_brutos is not None and mapeamento_de_itens is not None:
    # --- 2. A Barra Lateral (Sidebar) com TODOS os Filtros ---
    st.sidebar.header("🔧 Filtros da Análise")
    
    MODO_ESCOLHIDO = st.sidebar.selectbox(
        'Escolha o Modo de Jogo:',
        options=dados_brutos['game_mode'].unique(),
        index=0 
    )
    df_filtrado = dados_brutos[dados_brutos['game_mode'] == MODO_ESCOLHIDO]

    posicoes_validas = [p for p in df_filtrado['individual_position'].unique() if p not in ['Invalid', 'NONE']]
    POSICAO_ESCOLHIDA = st.sidebar.selectbox(
        'Escolha a Posição:',
        options=posicoes_validas,
        index=posicoes_validas.index('UTILITY') if 'UTILITY' in posicoes_validas else 0 
    )
    df_filtrado_final = df_filtrado[df_filtrado['individual_position'] == POSICAO_ESCOLHIDA]

    # --- Quantidade de Jogos minimos ---
    MIN_JOGOS_PARA_ANALISE = 1 
    st.sidebar.info(f"A analisar todos os campeões com 1 ou mais jogos.")
    
    st.sidebar.info(f"A analisar {len(df_filtrado_final)} partidas para '{MODO_ESCOLHIDO}' / '{POSICAO_ESCOLHIDA}'.")
    
    # --- 3. Calcular as Estatísticas Gerais  ---
    taxas_de_vitoria_geral, contagem_jogos_geral = analisar_taxa_vitoria(df_filtrado_final, MIN_JOGOS_PARA_ANALISE)
    kda_campeoes_geral = analisar_kda_campeoes(df_filtrado_final, MIN_JOGOS_PARA_ANALISE)
    media_ouro_geral = df_filtrado_final.groupby('champion_name')['gold_earned'].mean().round(2)
    
    if taxas_de_vitoria_geral is None or kda_campeoes_geral is None:
        st.warning(f"Nenhum campeão encontrado para esta combinação de filtros.")
    else:
        # --- 4. Filtro do Campeão  ---
        lista_campeoes_analisaveis = kda_campeoes_geral.index.sort_values().unique()
        
        CAMPEAO_ESCOLHIDO = st.sidebar.selectbox(
            f"Escolha um Campeão:",
            options=lista_campeoes_analisaveis
        )

        # --- 5. O Painel Principal  ---
        st.header(f"📈 Análise Específica: {CAMPEAO_ESCOLHIDO}")
        st.markdown(f"**Modo:** `{MODO_ESCOLHIDO}` | **Posição:** `{POSICAO_ESCOLHIDA}`")

        col_stats, col_itens = st.columns([1, 1])

        with col_stats:
            st.subheader("Estatísticas Principais")
            
            if (CAMPEAO_ESCOLHIDO in taxas_de_vitoria_geral) and \
               (CAMPEAO_ESCOLHIDO in kda_campeoes_geral.index) and \
               (CAMPEAO_ESCOLHIDO in media_ouro_geral.index):
                try:
                    winrate = taxas_de_vitoria_geral.loc[CAMPEAO_ESCOLHIDO]
                    kda_stats = kda_campeoes_geral.loc[CAMPEAO_ESCOLHIDO]
                    jogos = contagem_jogos_geral.loc[CAMPEAO_ESCOLHIDO]
                    ouro = media_ouro_geral.loc[CAMPEAO_ESCOLHIDO]
                    
                    data = {
                        'Partidas Analisadas': [jogos],
                        'Taxa de Vitória (%)': [winrate],
                        'KDA Médio': [kda_stats['kda']],
                        'Ouro (Médio)': [ouro],
                        'Kills (Médio)': [kda_stats['kills']],
                        'Deaths (Médio)': [kda_stats['deaths']],
                        'Assists (Médio)': [kda_stats['assists']]
                    }
                    df_stats = pd.DataFrame(data)
                    df_stats_transposta = df_stats.T
                    df_stats_transposta.columns = ['Valor']
                    
                    st.dataframe(df_stats_transposta, use_container_width=True)
                
                except Exception as e:
                    st.error(f"Ocorreu um erro ao mostrar dados para {CAMPEAO_ESCOLHIDO}: {e}")
            
            else:
                st.warning(f"O campeão {CAMPEAO_ESCOLHIDO} não foi encontrado nas listas de análise.")

        with col_itens:
            st.subheader(f"Itens Populares para {CAMPEAO_ESCOLHIDO}")
            itens_populares = analisar_itens_campeao(df_filtrado_final, CAMPEAO_ESCOLHIDO, mapeamento_de_itens)
            
            if itens_populares is not None:
                st.dataframe(itens_populares.head(10), use_container_width=True)
            else:
                st.warning("Não foram encontrados dados de itens.")
else:
    st.error("Os dados ou o mapeamento de itens não puderam ser carregados. O dashboard não pode continuar.")