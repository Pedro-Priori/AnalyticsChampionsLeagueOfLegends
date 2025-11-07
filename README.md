# 🎮 Painel de Análise de Dados de League of Legends

Este projeto é um *dashboard*  interativo para a análise de dados de partidas de League of Legends. O que começou como um simples script de terminal (`analise_lol.py`) evoluiu para uma aplicação web completa (`dashboard_lol.py`) usando Python, Pandas e Streamlit.

O objetivo principal deste *dashboard* é permitir a um utilizador filtrar uma grande base de dados de partidas e obter estatísticas detalhadas sobre o desempenho de campeões, incluindo Taxa de Vitória (Winrate), KDA e builds de itens mais populares, com um foco especial na performance "centrada no campeão".

Este projeto também serve como um *template* para provar como um *pipeline* de análise de dados pode ser "mutável" e adaptado para outros temas (como a análise de chamados de suporte).

---

## ✨ Funcionalidades Principais

* **Dashboard Interativo:** Uma interface web amigável criada com [Streamlit](https://streamlit.io/) que permite a análise sem necessidade de alterar o código.
* **Filtragem Dinâmica:** Permite ao utilizador filtrar todas as análises por Modo de Jogo (ex: 'CLASSIC') e Posição/Rota (ex: 'UTILITY', 'BOTTOM').
* **Análise Específica de Campeão:** O foco principal do *dashboard*. O utilizador escolhe um campeão na barra lateral e vê imediatamente as suas estatísticas principais.
* **Métricas Detalhadas:**
    * Taxa de Vitória (Winrate)
    * KDA Médio (Kills / Deaths / Assists)
    * Build de Itens mais populares (Top 10)
    * Número total de partidas analisadas para esse campeão.
* **Filtro de Relevância:** Um controlo deslizante (slider) para definir o "Nº Mínimo de Partidas" e excluir campeões com poucas partidas (ex: Sejuani Support com 1 jogo e 100% de vitória).
* **Atualização Dinâmica de Itens:** O *dashboard* liga-se automaticamente ao Data Dragon (API da Riot) para descarregar a versão mais recente dos nomes dos itens, garantindo que o painel está sempre atualizado com os *patches* de cada *season*.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.x**
* **Pandas:** Para o carregamento, limpeza, filtragem e agregação dos dados.
* **Streamlit:** Para a criação e execução da interface web (o *dashboard*).
* **Requests:** Para fazer os pedidos HTTP à API do Data Dragon e obter os nomes dos itens.
* **Openpyxl:** A biblioteca necessária para que o Pandas consiga ler ficheiros `.xlsx` (Excel).

---

## 🚀 Como Instalar e Executar

Para executar este projeto no teu computador, segue estes passos.

### 1. Obter os Dados

Este projeto **não** inclui o ficheiro de dados.
1.  Descarrega um ficheiro de dados de partidas (ex: do Kaggle).
2.  Coloca o ficheiro (`.xlsx` ou `.csv`) na mesma pasta que os scripts.
3.  O nosso *dashboard* está atualmente configurado para o `lol_match_data_2024.xlsx`.

### 2. Instalar as Dependências

Este projeto requer várias bibliotecas Python. Podes instalá-las usando o `pip` (recomenda-se usar o lançador `py` no Windows):

```bash
# Instalar a biblioteca principal de análise
py -m pip install pandas

# Instalar a biblioteca da interface web
py -m pip install streamlit

# Instalar a biblioteca para ler ficheiros Excel
py -m pip install openpyxl

# Instalar a biblioteca para pedidos de internet (nomes dos itens)
py -m pip install requests