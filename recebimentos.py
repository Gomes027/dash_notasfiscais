import os
import pandas as pd
import streamlit as st
from time import sleep

# Configuração da página
st.set_page_config(layout="wide", page_title="Entregas Pendentes")

# Baixar e ler os arquivos Excel
df_recebimento = pd.read_excel(r"recebimento_do_dia.xlsx", engine='openpyxl')
df_nfs_recebidas = pd.read_excel(r"nfs_recebidas.xlsx", engine='openpyxl')

# Obtendo a data da última atualização do arquivo
caminho_arquivo = r"recebimento_do_dia.xlsx"
timestamp = os.path.getmtime(caminho_arquivo)
ultima_atualizacao = pd.to_datetime(timestamp, unit='s')

# Processamento do DataFrame df_recebimento
mapeamento_lojas = {1: 'SMJ', 2: 'STT', 3: 'VIX', 4: 'MCP'}
df_recebimento['Loja'] = df_recebimento['Loja'].replace(mapeamento_lojas)
df_recebimento['Nota'] = df_recebimento['Nota'].apply(lambda x: f'{int(x):09d}' if pd.notnull(x) else '')
df_recebimento = df_recebimento.rename(columns={'Fornecedor': 'FORNECEDOR', 'Nota': 'NÚMERO DA NF'})

# Widget de seleção para escolher uma loja
loja_selecionada = st.sidebar.selectbox('Escolha uma Loja:', sorted(df_recebimento['Loja'].unique()))

# Função para concatenar com quebras de linha
def concatenar_com_quebras_de_linha(lista_nfs, max_chars=50):
    resultado = ""
    linha_atual = ""
    for nf in lista_nfs:
        if len(linha_atual) + len(nf) > max_chars:
            resultado += linha_atual.rstrip(", ") + "<br>"
            linha_atual = nf + ", "
        else:
            linha_atual += nf + ", "
    resultado += linha_atual.rstrip(", ")
    return resultado

# Filtragem dos dados para a loja selecionada
df_filtrado = df_recebimento[(df_recebimento['WMS'] == 'L') & (df_recebimento['Loja'] == loja_selecionada)].sort_values('FORNECEDOR')

# Agrupar por fornecedor e aplicar a função personalizada
df_agrupado = df_filtrado.groupby('FORNECEDOR').agg({'NÚMERO DA NF': lambda x: concatenar_com_quebras_de_linha(x)}).reset_index()

# Filtragem dos dados para a loja selecionada no df_nfs_recebidas
df_nfs_recebidas_filtrado = df_nfs_recebidas[df_nfs_recebidas['Loja'] == loja_selecionada].sort_values('FORNECEDOR')

# Exibindo a data da última atualização no Streamlit
st.sidebar.markdown(f"Última atualização do arquivo: {ultima_atualizacao.strftime('%d/%m/%Y %H:%M:%S')}")

# Dicionário mapeando lojas para suas respectivas imagens
imagens_lojas = {
    'SMJ': 'tresmann_Prancheta_1-removebg-preview.png',
    'STT': 'tresmann_Prancheta_1-removebg-preview.png',
    'VIX': 'Agoraa-removebg-preview.png',
    'MCP': 'WhatsApp_Image_2023-10-17_at_18.58.15__2_-removebg-preview.png'
}

# Linha para adicionar título e imagem
col_titulo, col_imagem = st.columns([8, 2])  # Ajuste as proporções conforme necessário
with col_titulo:
    st.title(f"RECEBIMENTO - {loja_selecionada}")
with col_imagem:
    # Exibe a imagem correspondente à loja selecionada
    st.image(imagens_lojas[loja_selecionada], width=180)

# Espaço usando HTML
st.markdown("<br>", unsafe_allow_html=True)

# Função para dividir a lista em subconjuntos de tamanho específico
def dividir_em_grupos(lista, tamanho_grupo):
    for i in range(0, len(lista), tamanho_grupo):
        yield lista[i:i + tamanho_grupo]

# Preparação dos dados para "ENTREGAS LIBERADAS"
dados_fornecedores = df_agrupado.groupby('FORNECEDOR')['NÚMERO DA NF'].apply(lambda x: "<br>".join(x)).reset_index()
grupos_fornecedores = list(dividir_em_grupos(dados_fornecedores, 8))

# Exibição dos DataFrames lado a lado
col1, col2 = st.columns([4, 6])
with col1:
    st.subheader("NFS RECEBIDAS")
    fornecedores = df_nfs_recebidas_filtrado["FORNECEDOR"].unique()
    st.markdown("<br>".join(f"**{fornecedor}**" for fornecedor in fornecedores), unsafe_allow_html=True)

with col2:
    st.subheader("ENTREGAS LIBERADAS")
    if not dados_fornecedores.empty:
        colunas_entregas = len(grupos_fornecedores)
        cols = st.columns(colunas_entregas)
        for i in range(colunas_entregas):
            grupo = grupos_fornecedores[i]
            with cols[i]:
                for index, row in grupo.iterrows():
                    fornecedor, nfs = row
                    st.markdown(f"**{fornecedor}:**<br>{nfs}", unsafe_allow_html=True)