import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os
import importlib.util

# Este arquivo é o seu dashboard principal.

# --- Configuração da Página ---
st.set_page_config(page_title="Auditoria Cidadã Peruíbe - Orçamento Simplificado", layout="wide", page_icon="🎯")

# --- CONTEÚDO PRINCIPAL DO DASHBOARD ---
st.title("Auditoria Cidadã Peruíbe - Orçamento Simplificado")

# Frase de missão
st.markdown("""
O objetivo deste portal independente é simplificar o orçamento da cidade de Peruíbe, para que seus cidadãos possam entender, e **fiscalizar** e cobrar o poder público.
""")

# Aviso/Disclaimer em caixa de cor
st.info("Esse portal cruza os dados da LOA (Lei Orçamentária Anual) com as despesas publicadas no Portal da Transparência da cidade.")

st.markdown("---")

# Link para as explicações no menu lateral
st.markdown("Saiba como ler estas informações no menu lateral.")

# --- FUNÇÃO PARA COLORIR A TABELA ---
def color_estouro_percent(val):
    if val > 5.0:
        return 'background-color: #ffcccb'  # Vermelho claro
    elif val > 0 and val <= 5.0:
        return 'background-color: #ffffcc'  # Amarelo claro
    else:
        return 'background-color: #c4f7c4'  # Verde claro

# --- Carregamento e Tratamento dos Dados ---
@st.cache_data
def carregar_dados_executados(ano):
    caminho_dados = f'dados_limpos/despesas_limpo_{ano}.csv'
    try:
        df = pd.read_csv(caminho_dados, delimiter=';', decimal=',')
        cols_monetarias = ['Empenhado', 'Anulado', 'Liquidado', 'Pago', 'Saldo']
        for col in cols_monetarias:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['Data Emissão'] = pd.to_datetime(df['Data Emissão'], errors='coerce')
        return df
    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{caminho_dados}' não encontrado. Certifique-se de ter executado a limpeza de dados.")
        return pd.DataFrame()

@st.cache_data
def carregar_dados_loa_orgaos():
    caminho = 'loa_por_orgaos.csv'
    try:
        # 🚨 CORREÇÃO APLICADA AQUI: Usando o motor de leitura robusto
        df_loa = pd.read_csv(
            caminho, 
            sep=',', 
            engine='python', 
            on_bad_lines='skip' 
        )

        # A coluna 'Valor' já está limpa (float) nos CSVs recentes, mas garantimos a conversão
        df_loa['Valor'] = pd.to_numeric(df_loa['Valor'], errors='coerce')
        
        # O código LOA agora é lido como está no CSV, sem extração de regex
        df_loa.rename(columns={'Codigo': 'Código LOA', 'Especificacao': 'Especificacao'}, inplace=True)
        df_loa = df_loa.dropna(subset=['Especificacao'])

        return df_loa
    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{caminho}' (LOA 2024) não encontrado. Verifique se ele está na raiz do projeto.")
        return pd.DataFrame()

@st.cache_data
def carregar_mapeamento():
    caminho = 'mapeamento_orgaos.csv'
    try:
        return pd.read_csv(caminho)
    except FileNotFoundError:
        st.error(f"Erro: Arquivo '{caminho}' não encontrado.")
        return pd.DataFrame()

# Carregamento dos dados
df_executado = carregar_dados_executados("2024") # Assume-se 2024 como o ano de execução
df_loa_orgaos = carregar_dados_loa_orgaos()
df_mapeamento = carregar_mapeamento()

if not df_executado.empty and not df_loa_orgaos.empty and not df_mapeamento.empty:
    # 1. Aplicar o mapeamento para padronizar os nomes dos órgãos
    mapeamento_dict = df_mapeamento.set_index('Unidade Orcamentaria')['Especificacao'].to_dict()
    df_executado['Unidade Orcamentaria Mapeada'] = df_executado['Unidade Orcamentaria'].replace(mapeamento_dict)

    # 2. Agrupar os gastos executados por órgão, incluindo Empenhado e Liquidado
    gastos_executados_por_orgao = df_executado.groupby('Unidade Orcamentaria Mapeada')[['Empenhado', 'Liquidado']].sum().reset_index()

    # 3. Juntar com os dados do LOA para ter o valor orçado
    # Usamos 'Especificacao' (que é o nome do órgão no LOA 2024)
    df_comparacao = pd.merge(
        gastos_executados_por_orgao,
        df_loa_orgaos.rename(columns={'Especificacao': 'Unidade Orcamentaria Mapeada', 'Valor': 'Valor Orçado'}),
        on='Unidade Orcamentaria Mapeada',
        how='left'
    )
    df_comparacao = df_comparacao.rename(columns={'Unidade Orcamentaria Mapeada': 'Órgão'})
    
    # Remove totais e consolidações
    orgaos_excluidos = ['TOTAL', 'Poder Executivo', 'Poder Legislativo', 'AUTARQUIA (PERUIBEPREV)']
    df_comparacao = df_comparacao[~df_comparacao['Órgão'].isin(orgaos_excluidos)]
    
    df_comparacao = df_comparacao.dropna(subset=['Órgão'])

    # Calcular a coluna 'Estouro %'
    df_comparacao['Estouro %'] = np.where(
        (df_comparacao['Empenhado'] > df_comparacao['Valor Orçado']) & (df_comparacao['Valor Orçado'] > 0),
        ((df_comparacao['Empenhado'] - df_comparacao['Valor Orçado']) / df_comparacao['Valor Orçado']) * 100,
        0
    )
    
    # Seleção final de colunas
    df_comparacao = df_comparacao[['Código LOA', 'Órgão', 'Valor Orçado', 'Empenhado', 'Liquidado', 'Estouro %']]

    # --- Visualização: Gráfico de Barras ---
    st.subheader("Gráfico: Orçamento vs. Gasto por Órgão")
    st.info("O gráfico abaixo mostra a comparação entre o valor orçado (LOA 2024) e os valores empenhado e liquidado (Execução 2024).")
    
    df_long = pd.melt(df_comparacao, id_vars=['Órgão', 'Código LOA'], value_vars=['Empenhado', 'Liquidado', 'Valor Orçado'],
                      var_name='Tipo de Gasto', value_name='Valor')
    fig_bar = px.bar(df_long, x='Valor', y='Órgão', color='Tipo de Gasto', barmode='group', orientation='h',
                     title='Comparação de Gasto Executado e Orçamento Planejado (R$)',
                     labels={'Órgão': 'Órgão / Unidade Orçamentária', 'Valor': 'Valor (R$)'},
                     color_discrete_map={
                         'Valor Orçado': 'rgb(120, 120, 120)', 'Empenhado': 'rgb(34, 139, 34)', 'Liquidado': 'rgb(0, 191, 255)'
                     })
    fig_bar.update_layout(height=800, yaxis_categoryorder='total ascending', xaxis_tickformat='R$,.0f')
    fig_bar.update_traces(marker_line_width=1, marker_line_color="white")
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Visualização: Tabela e Detalhamento ---
    st.subheader("Tabela de Detalhes do Orçamento")
    df_styled = df_comparacao.copy()
    styled_table = df_styled.style.applymap(color_estouro_percent, subset=pd.IndexSlice[:, ['Estouro %']])
    styled_table = styled_table.format({
        'Valor Orçado': 'R$ {:,.2f}', 'Empenhado': 'R$ {:,.2f}', 'Liquidado': 'R$ {:,.2f}', 'Estouro %': '{:.2f}%'
    })
    st.dataframe(styled_table, use_container_width=True, hide_index=True)
    st.divider()
    orgaos_unicos = df_comparacao['Órgão'].unique()
    orgao_selecionado = st.selectbox("Selecione um órgão para ver as despesas detalhadas:", orgaos_unicos)
    
    if orgao_selecionado:
        st.subheader(f"Despesas Detalhadas para: {orgao_selecionado}")
        df_detalhes = df_executado[df_executado['Unidade Orcamentaria Mapeada'] == orgao_selecionado]
        st.dataframe(df_detalhes, use_container_width=True)

else:
    st.error("Não foi possível carregar os dados. Verifique os arquivos e as funções de carregamento.")