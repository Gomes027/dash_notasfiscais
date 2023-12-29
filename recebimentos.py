import pandas as pd
import streamlit as st
from time import sleep

# Configuração da página
st.set_page_config(layout="wide", page_title="Entregas Pendentes")

# Baixar e ler os arquivos Excel
df_recebimento = pd.read_excel(r"recebimento_do_dia.xlsx", engine='openpyxl')
df_nfs_recebidas = pd.read_excel(r"nfs_recebidas.xlsx", engine='openpyxl')

# Processamento do DataFrame df_recebimento
mapeamento_lojas = {1: 'SMJ', 2: 'STT', 3: 'VIX', 4: 'MCP'}
df_recebimento['Loja'] = df_recebimento['Loja'].replace(mapeamento_lojas)
df_recebimento['Nota'] = df_recebimento['Nota'].apply(lambda x: f'{int(x):09d}' if pd.notnull(x) else '')
df_recebimento = df_recebimento.rename(columns={'Fornecedor': 'FORNECEDOR', 'Nota': 'NÚMERO DA NF'})

# Widget de seleção para escolher uma loja
loja_selecionada = st.sidebar.selectbox('Escolha uma Loja:', sorted(df_recebimento['Loja'].unique()))

# Filtragem dos dados para a loja selecionada
df_filtrado = df_recebimento[(df_recebimento['WMS'] == 'L') & (df_recebimento['Loja'] == loja_selecionada)].sort_values('FORNECEDOR')

# Filtragem dos dados para a loja selecionada no df_nfs_recebidas
df_nfs_recebidas_filtrado = df_nfs_recebidas[df_nfs_recebidas['Loja'] == loja_selecionada].sort_values('FORNECEDOR')

# Dicionário mapeando lojas para suas respectivas imagens
imagens_lojas = {
    'SMJ': 'tresmann_Prancheta_1-removebg-preview.png',
    'STT': 'tresmann_Prancheta_1-removebg-preview.png',
    'VIX': 'Agoraa-removebg-preview.png',
    'MCP': 'WhatsApp_Image_2023-10-17_at_18.58.15__2_-removebg-preview.png'
}

# Linha para adicionar título e imagem
col_titulo, col_imagem = st.columns([4, 2])  # Ajuste as proporções conforme necessário
with col_titulo:
    st.title(f"RECEBIMENTO - {loja_selecionada}")
with col_imagem:
    # Exibe a imagem correspondente à loja selecionada
    st.image(imagens_lojas[loja_selecionada], width=180)

# Espaço usando HTML
st.markdown("<br><br>", unsafe_allow_html=True)

# Exibição dos DataFrames lado a lado
col1, col2 = st.columns(2)
with col1:
    st.subheader("NFS RECEBIDAS")
    st.dataframe(df_nfs_recebidas_filtrado["FORNECEDOR"], use_container_width=True, hide_index=True, height=700)

with col2:
    st.subheader("ENTREGAS LIBERADAS")
    colunas_relatorio = ['FORNECEDOR', 'NÚMERO DA NF']
    st.dataframe(df_filtrado[colunas_relatorio], use_container_width=True, hide_index=True, height=700)