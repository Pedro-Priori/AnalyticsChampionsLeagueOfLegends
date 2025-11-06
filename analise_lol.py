import pandas as pd
import requests 

# -------------------------------------------------------------------
# FUNÇÃO 1: CARREGAR DADOS (Sem alterações)
# -------------------------------------------------------------------
def carregar_dados(caminho_do_ficheiro):
    """
    Função "mutável" atualizada para tentar ler .xlsx e .csv
    """
    if caminho_do_ficheiro.endswith('.xlsx'):
        print("A tentar ler como ficheiro Excel (.xlsx)...")
        try:
            df = pd.read_excel(caminho_do_ficheiro)
            print(f"Sucesso! Ficheiro '{caminho_do_ficheiro}' carregado.")
            return df
        except Exception as e:
            print(f"Ocorreu um erro ao ler o ficheiro Excel: {e}")
            return None
    elif caminho_do_ficheiro.endswith('.csv'):
        print("A tentar ler como ficheiro CSV (.csv)...")
        try:
            df = pd.read_csv(caminho_do_ficheiro)
            print(f"Sucesso! Ficheiro '{caminho_do_ficheiro}' carregado.")
            return df
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao ler o ficheiro CSV: {e}")
            return None
    else:
        print("Erro: Extensão de ficheiro não reconhecida (esperava .csv ou .xlsx).")
        return None

# -------------------------------------------------------------------
# FUNÇÃO 2: TRADUTOR DE ITENS (Sem alterações)
# -------------------------------------------------------------------
def carregar_mapeamento_itens():
    """
    Conecta-se ao Data Dragon (API da Riot) para descarregar
    o ficheiro JSON dos itens e criar um dicionário de tradução.
    """
    print("\n--- 🌍 A descarregar dicionário de itens da Riot (Data Dragon) ---")
    URL_API = "https://ddragon.leagueoflegends.com/cdn/15.1.1/data/en_US/item.json"
    
    try:
        resposta = requests.get(URL_API)
        resposta.raise_for_status() 
        dados_json = resposta.json()
        itens_data_dragon = dados_json['data']
        
        mapeamento_itens = {}
        for id_item_str, info_item in itens_data_dragon.items():
            id_item_int = int(id_item_str)
            mapeamento_itens[id_item_int] = info_item['name']
            
        print("Sucesso! Dicionário de itens carregado.")
        return mapeamento_itens
        
    except Exception as e:
        print(f"Erro ao tentar descarregar o ficheiro de itens: {e}")
        print("A análise de itens irá mostrar apenas os IDs.")
        return None

# -------------------------------------------------------------------
# FUNÇÃO 3: TAXA DE VITÓRIA (ATUALIZADA com min_jogos)
# -------------------------------------------------------------------
def analisar_taxa_vitoria(df, min_jogos):
    """
    Calcula a taxa de vitória para cada campeão.
    IGNORA campeões com menos de 'min_jogos'.
    
    :param df: O DataFrame com os dados JÁ FILTRADOS.
    :param min_jogos: O número mínimo de partidas para um campeão ser incluído.
    """
    print(f"\n--- 🏆 Análise: Taxa de Vitória (Mínimo de {min_jogos} jogos) ---")
    
    contagem_jogos = df.groupby('champion_name').size()
    campeoes_relevantes = contagem_jogos[contagem_jogos >= min_jogos].index
    df_relevante = df[df['champion_name'].isin(campeoes_relevantes)]
    
    if df_relevante.empty:
        print(f"Nenhum campeão foi jogado {min_jogos} ou mais vezes.")
        return None
    
    agrupado_por_campeao = df_relevante.groupby('champion_name')
    taxas_vitoria = agrupado_por_campeao['win'].mean()
    taxas_vitoria_perc = (taxas_vitoria * 100).sort_values(ascending=False)
    
    return taxas_vitoria_perc.round(2)

# -------------------------------------------------------------------
# FUNÇÃO 4: ITENS (Sem alterações)
# -------------------------------------------------------------------
def analisar_itens_campeao(df, nome_do_campeao, mapeamento_itens):
    """
    Encontra os itens mais comprados para um campeão específico.
    """
    print(f"\n--- 🗡️  Análise: Itens mais usados para '{nome_do_campeao}' ---")
    
    df_campeao = df[df['champion_name'] == nome_do_campeao]
    
    if df_campeao.empty:
        print(f"Atenção: Campeão '{nome_do_campeao}' não encontrado nos dados filtrados (para esta posição).")
        return None
        
    colunas_itens = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']
    todos_os_itens = df_campeao[colunas_itens].stack()
    contagem_itens = todos_os_itens.value_counts()
    
    if 0 in contagem_itens:
        contagem_itens = contagem_itens.drop(0)
        
    if mapeamento_itens:
        contagem_com_nomes = contagem_itens.rename(index=mapeamento_itens)
        return contagem_com_nomes
    else:
        return contagem_itens

# -------------------------------------------------------------------
# FUNÇÃO 5: ANÁLISE DE OURO (Sem alterações)
# -------------------------------------------------------------------
def analisar_impacto_ouro(df):
    """
    Analisa a média de ouro ganho (gold_earned) em vitórias vs. derrotas.
    """
    print("\n--- 💰 Análise: Impacto do Ouro na Vitória ---")
    
    try:
        media_ouro = df.groupby('win')['gold_earned'].mean()
        media_ouro = media_ouro.round(2)
        media_ouro = media_ouro.rename(index={False: 'Derrota', True: 'Vitória'})
        return media_ouro
    except KeyError:
        print("Erro: A coluna 'gold_earned' não foi encontrada.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado na análise de ouro: {e}")
        return None

# -------------------------------------------------------------------
# FUNÇÃO 6: KDA (ATUALIZADA com min_jogos)
# -------------------------------------------------------------------
def analisar_kda_campeoes(df, min_jogos):
    """
    Calcula as médias de Kills, Deaths, Assists e o KDA para cada campeão.
    IGNORA campeões com menos de 'min_jogos'.
    
    :param df: O DataFrame com os dados JÁ FILTRADOS.
    :param min_jogos: O número mínimo de partidas para um campeão ser incluído.
    """
    print(f"\n--- ⚔️  Análise: KDA Médio (Mínimo de {min_jogos} jogos) ---")
    
    contagem_jogos = df.groupby('champion_name').size()
    campeoes_relevantes = contagem_jogos[contagem_jogos >= min_jogos].index
    df_relevante = df[df['champion_name'].isin(campeoes_relevantes)]

    if df_relevante.empty:
        print(f"Nenhum campeão foi jogado {min_jogos} ou mais vezes.")
        return None
    
    try:
        media_stats = df_relevante.groupby('champion_name')[['kills', 'deaths', 'assists']].mean()
        
        media_stats['deaths_para_kda'] = media_stats['deaths'].replace(0, 1)
        media_stats['kda'] = (media_stats['kills'] + media_stats['assists']) / media_stats['deaths_para_kda']
        
        media_stats = media_stats.round(2)
        media_stats = media_stats.sort_values(by='kda', ascending=False)
        
        return media_stats[['kills', 'deaths', 'assists', 'kda']]
        
    except KeyError:
        print("Erro: Colunas 'kills', 'deaths', or 'assists' não encontradas.")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado na análise de KDA: {e}")
        return None


# --- O TEU PROJETO COMEÇA AQUI ---

# 1. Define o caminho completo para o teu ficheiro
NOME_DO_FICHEIRO = r"C:\Users\raian.felipe\Desktop\analise escola\analise-pedro\lol_match_data_2024.xlsx"

# 2. Carrega os dados
dados_brutos = carregar_dados(NOME_DO_FICHEIRO)

# 3. Carrega o Dicionário de Itens
mapeamento_de_itens = carregar_mapeamento_itens()

# 4. Executa as análises (APENAS se os dados foram carregados)
if dados_brutos is not None:
    
    # --- FILTRAGEM DE MODO ---
    MODO_ESCOLHIDO = 'CLASSIC'
    print(f"\n--- 🔍 A filtrar dados apenas para o modo: '{MODO_ESCOLHIDO}' ---")
    df_filtrado = dados_brutos[dados_brutos['game_mode'] == MODO_ESCOLHIDO]
    
    # --- EXPLORAÇÃO DE POSIÇÕES ---
    posicoes_existentes = df_filtrado['individual_position'].unique()
    print(f"\n--- 🗺️ Exploração: Posições Encontradas (no modo {MODO_ESCOLHIDO}) ---")
    print(f"Posições neste dataset: {posicoes_existentes}")

    # --- FILTRAGEM DE POSIÇÃO ---
    POSICAO_ESCOLHIDA = 'BOTTOM' # (Mantido 'BOTTOM' como escolheste)
    
    print(f"\n--- 🔍 A filtrar dados também para a posição: '{POSICAO_ESCOLHIDA}' ---")
    
    df_filtrado_final = df_filtrado[df_filtrado['individual_position'] == POSICAO_ESCOLHIDA]
    
    # *** ESTA É A LINHA CORRIGIDA ***
    print(f"Análise original (CLASSIC) tinha {len(df_filtrado)} partidas.")
    print(f"Nova análise (filtrada por posição) tem {len(df_filtrado_final)} partidas.") # <- CORRIGIDO

    # --- CONSTANTES DE ANÁLISE ---
    
    # Define o limite mínimo de jogos para uma análise ser "relevante"
    MIN_JOGOS_PARA_ANALISE = 20 # (Podes aumentar para 50, ou baixar para 10)
    
    # Define o campeão que queremos "inspecionar"
    CAMPEAO_PARA_ANALISAR = 'Sivir' # (Mantido 'Sivir' como escolheste)

    # --- TODAS AS ANÁLISE AGORA USAM O 'df_filtrado_final' ---
    
    print(f"\n--- RESULTADOS APENAS PARA: {MODO_ESCOLHIDO} / {POSICAO_ESCOLHIDA} ---")

    # --- Análise de Ouro (Específica da Posição) ---
    media_de_ouro = analisar_impacto_ouro(df_filtrado_final)
    if media_de_ouro is not None:
        print("Média de Ouro Ganho:")
        print(media_de_ouro)
    
    # --- Análise de Taxa de Vitória (Específica da Posição e COM FILTRO) ---
    taxas_de_vitoria_filtradas = analisar_taxa_vitoria(df_filtrado_final, MIN_JOGOS_PARA_ANALISE)
    
    if taxas_de_vitoria_filtradas is not None:
        print(f"\nTop 10 Campeões (Taxa de Vitória):")
        print(taxas_de_vitoria_filtradas.head(10))
        
        print(f"\nPiores 10 Campeões (Taxa de Vitória):")
        print(taxas_de_vitoria_filtradas.tail(10))
    
    # --- Análise de KDA (Específica da Posição e COM FILTRO) ---
    kda_campeoes = analisar_kda_campeoes(df_filtrado_final, MIN_JOGOS_PARA_ANALISE)
    
    if kda_campeoes is not None:
        print("\nTop 10 Campeões (KDA):")
        print(kda_campeoes.head(10))
        
        print("\nPiores 10 Campeões (KDA):")
        print(kda_campeoes.tail(10))

    # --- ANÁLISE ÚNICA (O TEU PEDIDO) ---
    print(f"\n--- 📈 Análise Única para: {CAMPEAO_PARA_ANALISAR} ({POSICAO_ESCOLHIDA}) ---")

    # 1. Procurar Taxa de Vitória Única
    try:
        if (taxas_de_vitoria_filtradas is not None) and (CAMPEAO_PARA_ANALISAR in taxas_de_vitoria_filtradas):
            taxa_vitoria_unica = taxas_de_vitoria_filtradas.loc[CAMPEAO_PARA_ANALISAR]
            print(f"Taxa de Vitória: {taxa_vitoria_unica}%")
        else:
            print(f"Taxa de Vitória: {CAMPEAO_PARA_ANALISAR} não tem jogos suficientes (min {MIN_JOGOS_PARA_ANALISE}) para esta análise.")
    except Exception as e:
        print(f"Não foi possível obter a Taxa de Vitória para {CAMPEAO_PARA_ANALISAR}: {e}")

    # 2. Procurar KDA Único
    try:
        if (kda_campeoes is not None) and (CAMPEAO_PARA_ANALISAR in kda_campeoes.index):
            kda_unico = kda_campeoes.loc[CAMPEAO_PARA_ANALISAR]
            print("Estatísticas Médias (K/D/A):")
            print(f"  Kills:   {kda_unico['kills']}")
            print(f"  Deaths:  {kda_unico['deaths']}")
            print(f"  Assists: {kda_unico['assists']}")
            print(f"  KDA:     {kda_unico['kda']}")
        else:
            print(f"KDA: {CAMPEAO_PARA_ANALISAR} não tem jogos suficientes (min {MIN_JOGOS_PARA_ANALISE}) para esta análise.")
    except Exception as e:
        print(f"Não foi possível obter o KDA para {CAMPEAO_PARA_ANALISAR}: {e}")
        
    # --- Análise de Itens (Específica da Posição) ---
    itens_populares = analisar_itens_campeao(df_filtrado_final, CAMPEAO_PARA_ANALISAR, mapeamento_de_itens)
    
    if itens_populares is not None:
        print(f"\nTop 10 Itens para {CAMPEAO_PARA_ANALISAR}:")
        print(itens_populares.head(10))
else:
    print("O carregamento dos dados falhou. O script não pode continuar.")