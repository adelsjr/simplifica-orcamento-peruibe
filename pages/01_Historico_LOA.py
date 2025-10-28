import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(page_title="Histórico LOA", layout="wide", page_icon="📅")

st.title("📅 Auditoria Cidadã Peruíbe")
st.markdown("---")

# --- Dados das Receitas Consolidado (Para Gráficos Históricos) ---
# NOTA: Os valores detalhados são consolidações e estimativas baseadas na estrutura geral.
RECEITA_COMPOSICAO = pd.DataFrame({
    'Tipo de Receita': [
        'Impostos, Taxas e Contribuições',
        'Contribuições Previdenciárias',
        'Receita Patrimonial e Serviços',
        'Transferências Correntes',
        'Receitas de Capital e Outras'
    ],
    '2024 (R$)': [
        180000000,
        35000000,
        10000000,
        260000000,
        6800000
    ],
    '2025 (R$)': [
        195000000,
        37000000,
        9500000,
        240000000,
        18100000
    ],
    '2026 (R$)': [
        209511009.23,
        38096600.00,
        8800895.00,
        312323199.00,
        53099306.00
    ]
})

# --- Dados Detalhados para a Tabela de Transparência Popular (LOA 2024, 2025, 2026) ---

# LOA 2024 - Total: R$ 491.800.000,00
DADOS_POPULAR_2024 = {
    "RECEITAS": {
        "Total de Receitas": 491800000.00,
        "--- RECEITAS CORRENTES PRÓPRIAS ---": None,
        "IPTU (Imposto sobre a Propriedade)": 60000000.00,
        "ISS (Imposto sobre Serviços)": 50000000.00,
        "ITBI (Imposto Transmissão de Bens)": 7500000.00,
        "Outras Receitas Próprias": 62500000.00,
        "--- TRANSFERÊNCIAS DE RECURSOS ---": None,
        "ICMS (Imposto sobre Circulação)": 100000000.00,
        "FPM (Fundo de Participação dos Municípios)": 80000000.00,
        "FUNDEB (Educação Básica)": 70000000.00,
        "SUS (Sistema Único de Saúde)": 35000000.00,
        "Demais Transferências": 18000000.00,
        "--- RECEITAS DE CAPITAL ---": None,
        "Transferências de Capital e Outras": 8800000.00,
    },
    "DESPESAS": {
        "Total de Despesas": 491800000.00,
        "SAÚDE (Função 10)": 122334195.00, 
        "EDUCAÇÃO (Função 12)": 130606500.00, 
        "ADMINISTRAÇÃO (Função 04)": 68000000.00,
        "SEGURANÇA PÚBLICA (Função 06)": 10000000.00,
        "ASSISTÊNCIA SOCIAL (Função 08)": 14000000.00,
        "Outras Despesas (Dívida, Urbanismo, etc)": 146859305.00
    }
}

# LOA 2025 - Total: R$ 499.600.000,00
DADOS_POPULAR_2025 = {
    "RECEITAS": {
        "Total de Receitas": 499600000.00,
        "--- RECEITAS CORRENTES PRÓPRIAS ---": None,
        "IPTU (Imposto sobre a Propriedade)": 65000000.00,
        "ISS (Imposto sobre Serviços)": 55000000.00,
        "ITBI (Imposto Transmissão de Bens)": 8000000.00,
        "Outras Receitas Próprias": 67000000.00,
        "--- TRANSFERÊNCIAS DE RECURSOS ---": None,
        "ICMS (Imposto sobre Circulação)": 105000000.00,
        "FPM (Fundo de Participação dos Municípios)": 90000000.00,
        "FUNDEB (Educação Básica)": 75000000.00,
        "SUS (Sistema Único de Saúde)": 35000000.00,
        "Demais Transferências": 106000000.00,
        "--- RECEITAS DE CAPITAL ---": None,
        "Transferências de Capital e Outras": 4000000.00,
    },
    "DESPESAS": {
        "Total de Despesas": 499600000.00,
        "SAÚDE (Função 10)": 170812200.00,
        "EDUCAÇÃO (Função 12)": 135000000.00,
        "ADMINISTRAÇÃO (Função 04)": 70000000.00,
        "SEGURANÇA PÚBLICA (Função 06)": 11000000.00,
        "ASSISTÊNCIA SOCIAL (Função 08)": 15000000.00,
        "Outras Despesas (Dívida, Urbanismo, etc)": 97787800.00
    }
}

# LOA 2026 - Total: R$ 621.832.000,00
DADOS_POPULAR_2026 = {
    "RECEITAS": {
        "Total de Receitas": 621832000.00,
        "--- RECEITAS CORRENTES PRÓPRIAS ---": None,
        "IPTU (Imposto sobre a Propriedade)": 80000000.00,
        "ISS (Imposto sobre Serviços)": 68000000.00,
        "ITBI (Imposto Transmissão de Bens)": 9500000.00,
        "Outras Receitas Próprias": 70000000.00,
        "--- TRANSFERÊNCIAS DE RECURSOS ---": None,
        "ICMS (Imposto sobre Circulação)": 130000000.00,
        "FPM (Fundo de Participação dos Municípios)": 100000000.00,
        "FUNDEB (Educação Básica)": 90000000.00,
        "SUS (Sistema Único de Saúde)": 40000000.00,
        "Demais Transferências": 23000000.00,
        "--- RECEITAS DE CAPITAL ---": None,
        "Transferências de Capital e Outras": 10000000.00,
    },
    "DESPESAS": {
        "Total de Despesas": 621832000.00,
        "SAÚDE (Função 10)": 174796510.00,
        "EDUCAÇÃO (Função 12)": 143767115.00,
        "ADMINISTRAÇÃO (Função 04)": 66061210.00,
        "SEGURANÇA PÚBLICA (Função 06)": 12221000.00,
        "ASSISTÊNCIA SOCIAL (Função 08)": 14763179.00,
        "Outras Despesas (Dívida, Urbanismo, etc)": 210222986.00
    }
}

DADOS_POPULAR_ANUAL = {
    2024: DADOS_POPULAR_2024,
    2025: DADOS_POPULAR_2025,
    2026: DADOS_POPULAR_2026,
}

# Função de formatação para R$ (Padrão BR)
def formatar_br(valor):
    if pd.isna(valor) or valor is None:
        return ""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# --- Funções de Carregamento ---
@st.cache_data
def carregar_dados_loa_por_ano(ano):
    caminho = f'loa_por_orgaos_{ano}.csv'
    if ano == 2024:
        caminho = 'loa_por_orgaos.csv'
    
    try:
        df_loa = pd.read_csv(
            caminho, 
            sep=',', 
            engine='python', 
            on_bad_lines='skip' 
        ) 
        
        df_loa['Valor'] = pd.to_numeric(df_loa['Valor'], errors='coerce')
        
        df_loa.rename(columns={'Valor': f'Orçado {ano}', 'Especificacao': 'Órgão', 'Codigo': 'Código LOA'}, inplace=True)
        
        orgaos_excluidos = ['TOTAL', 'Poder Executivo', 'Poder Legislativo', 'AUTARQUIA (PERUIBEPREV)']
        df_loa = df_loa[~df_loa['Órgão'].isin(orgaos_excluidos)]
        df_loa.dropna(subset=['Órgão'], inplace=True)
        
        df_loa = df_loa[['Código LOA', 'Órgão', f'Orçado {ano}']].copy()

        return df_loa.drop_duplicates(subset=['Código LOA'], keep='first')
    except FileNotFoundError:
        return pd.DataFrame()

# --- Carregamento de Dados (Para Seções 2 e 3) ---
df_2024 = carregar_dados_loa_por_ano(2024)
df_2025 = carregar_dados_loa_por_ano(2025)
df_2026 = carregar_dados_loa_por_ano(2026)

df_list = [df_2024, df_2025, df_2026]
df_list = [df for df in df_list if not df.empty]


# =========================================================================
# SEÇÃO 1: ORÇAMENTO COM TRANSPARÊNCIA POPULAR (VERSÃO SIMPLIFICADA)
# =========================================================================
st.header("1. Orçamento Simplificado (LOA 2024-2026)")
st.markdown("Apresentação resumida e simplificada das principais Receitas e Despesas do orçamento para fácil entendimento do cidadão.")

# -------------------------------------------------------------
# SELETOR DE ANO
# -------------------------------------------------------------
ano_selecionado_popular = st.selectbox(
    "Selecione o Ano para ver o Orçamento Simplificado:",
    options=[2026, 2025, 2024],
    index=0,
    key='select_ano_popular'
)

dados_ano = DADOS_POPULAR_ANUAL[ano_selecionado_popular]
TOTAL_LOA = dados_ano["RECEITAS"]["Total de Receitas"]

st.subheader(f"Visão Simplificada do Orçamento (LOA {ano_selecionado_popular})")

col_grafico_receita, col_grafico_despesa = st.columns(2)

# --- FUNÇÕES PARA TABELAS E GRÁFICOS ---

# Função para gerar DataFrame de Receita para o gráfico
def gerar_receita_pop_data(dados_ano, TOTAL_LOA):
    dados_receita_lista = []
    for conta, valor in dados_ano["RECEITAS"].items():
        if valor is not None and "Total de Receitas" not in conta and "---" not in conta:
            dados_receita_lista.append({
                "CONTA": conta, 
                "VALOR ORÇADO": valor, 
                "PERCENTUAL": (valor / TOTAL_LOA) * 100
            })
    return pd.DataFrame(dados_receita_lista)

# Função para gerar DataFrame de Despesa para o gráfico
def gerar_despesa_pop_data(dados_ano, TOTAL_LOA):
    dados_despesa_lista = []
    for conta, valor in dados_ano["DESPESAS"].items():
        if "Total de Despesas" not in conta:
            dados_despesa_lista.append({
                "ÁREA DE GASTO": conta, 
                "VALOR ORÇADO": valor, 
                "PERCENTUAL": (valor / TOTAL_LOA) * 100
            })
    return pd.DataFrame(dados_despesa_lista)

# -------------------------------------------------------------
# GRÁFICOS DE PIZZA (RECEITA E DESPESA)
# -------------------------------------------------------------
df_receita_data = gerar_receita_pop_data(dados_ano, TOTAL_LOA)
df_despesa_data = gerar_despesa_pop_data(dados_ano, TOTAL_LOA)

with col_grafico_receita:
    st.markdown("#### COMPOSIÇÃO DA RECEITA")
    
    fig_pizza_receita = px.pie(
        df_receita_data,
        values='VALOR ORÇADO',
        names='CONTA',
        title=f'Fontes de Receita (Total: {formatar_br(TOTAL_LOA)})',
        hole=.4
    )
    fig_pizza_receita.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
    st.plotly_chart(fig_pizza_receita, use_container_width=True)

with col_grafico_despesa:
    st.markdown("#### COMPOSIÇÃO DA DESPESA")
    
    fig_pizza_despesa = px.pie(
        df_despesa_data,
        values='VALOR ORÇADO',
        names='ÁREA DE GASTO',
        title=f'Destinação da Despesa (Total: {formatar_br(TOTAL_LOA)})',
        hole=.4
    )
    fig_pizza_despesa.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
    st.plotly_chart(fig_pizza_despesa, use_container_width=True)


# -------------------------------------------------------------
# TABELAS DE DETALHAMENTO
# -------------------------------------------------------------
st.markdown("---")
st.subheader("Tabelas Detalhadas da Visão Simplificada")
col_tabela_receita, col_tabela_despesa = st.columns(2)

with col_tabela_receita:
    st.markdown("#### RECEITAS")
    dados_receita_tabela = []
    
    for conta, valor in dados_ano["RECEITAS"].items():
        if valor is None:
            dados_receita_tabela.append([conta, "", ""])
        else:
            perc = (valor / TOTAL_LOA) * 100
            dados_receita_tabela.append([conta, formatar_br(valor), f"{perc:.2f}%"])
    
    df_receita_popular = pd.DataFrame(
        dados_receita_tabela, 
        columns=["CONTA", "VALOR ORÇADO", "% DO TOTAL GERAL"]
    )

    def highlight_total_e_titulo_receita(row):
        is_total = row['CONTA'] == 'Total de Receitas'
        is_titulo = row['VALOR ORÇADO'] == ""
        if is_total:
            return ['font-weight: bold; background-color: #d3f9d3'] * len(row)
        elif is_titulo:
            return ['font-weight: bold; background-color: #e0f0ff'] * len(row)
        return [''] * len(row)

    styled_receita = (
        df_receita_popular.style
        .apply(highlight_total_e_titulo_receita, axis=1)
    )
    st.dataframe(styled_receita, use_container_width=True, hide_index=True)


with col_tabela_despesa:
    st.markdown("#### DESPESAS")
    
    dados_despesa_tabela = []
    for conta, valor in dados_ano["DESPESAS"].items():
        if conta == "Total de Despesas":
            perc = 100.00
        else:
            perc = (valor / TOTAL_LOA) * 100

        dados_despesa_tabela.append([conta, formatar_br(valor), f"{perc:.2f}%"])

    df_despesa_popular = pd.DataFrame(
        dados_despesa_tabela, 
        columns=["ÁREA DE GASTO", "VALOR ORÇADO", "% DO TOTAL GERAL"]
    )

    def highlight_total_despesa(row):
        is_total = row['ÁREA DE GASTO'] == 'Total de Despesas'
        if is_total:
            return ['font-weight: bold; background-color: #f9d3d3'] * len(row)
        return [''] * len(row)

    styled_despesa = (
        df_despesa_popular.style
        .apply(highlight_total_despesa, axis=1)
    )
    st.dataframe(styled_despesa, use_container_width=True, hide_index=True)


st.markdown("---")
st.warning(f"""
⚠️ **Atenção:** Os valores detalhados de Receitas (IPTU, FPM, etc.) e as Despesas por Área para a LOA {ano_selecionado_popular} são **consolidações e estimativas** baseadas na estrutura geral do orçamento e nos dados de Receita de cada LOA. O modelo de transparência popular exige essa simplificação e estimativa. **Recomenda-se a verificação e ajuste destes valores** com o detalhamento completo dos documentos originais.
""")


# =========================================================================
# SEÇÃO 2: HISTÓRICO DE DESPESAS POR ÓRGÃO 
# =========================================================================
st.markdown("---")
st.header("2. Histórico de Despesas por Órgão")
st.markdown("Comparação dos valores **Orçados** por unidade orçamentária (2024, 2025 e 2026).")

if df_list:
    
    df_historico = df_list[0]
    
    for df_ano in df_list[1:]:
        df_historico = pd.merge(df_historico, df_ano, on=['Código LOA', 'Órgão'], how='outer')

    cols_monetarias = [col for col in df_historico.columns if col.startswith('Orçado')]
    
    # --- GRÁFICO DE BARRAS DESPESA ---
    st.subheader("Gráfico: Evolução do Orçamento de Despesa por Órgão")
    
    df_plot_long = pd.melt(
        df_historico.drop(columns=['Código LOA']), 
        id_vars='Órgão',
        value_vars=cols_monetarias,
        var_name='Ano',
        value_name='Valor Orçado'
    )
    
    df_plot_long['Valor Orçado (Milhões)'] = df_plot_long['Valor Orçado'] / 1_000_000 
    df_plot_long.dropna(subset=['Valor Orçado'], inplace=True)

    fig_bar = px.bar(
        df_plot_long,
        x='Valor Orçado (Milhões)',
        y='Órgão',
        color='Ano',
        barmode='group',
        orientation='h',
        title='Comparação Orçamentária Anual por Órgão (R$ Milhões)',
        labels={'Órgão': 'Órgão / Unidade Orçamentária', 'Valor Orçado (Milhões)': 'Valor Orçado (R$ Milhões)'},
        height=800
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- TABELA DETALHADA DESPESA ---
    st.subheader("Tabela: Detalhamento Histórico da Despesa")

    df_soma = pd.DataFrame(df_historico[cols_monetarias].sum(skipna=True)).T
    df_soma['Órgão'] = 'TOTAL GERAL DA TABELA'
    df_soma['Código LOA'] = ''
    
    df_tabela = pd.concat([df_historico, df_soma], ignore_index=True)
    df_tabela = df_tabela[['Código LOA', 'Órgão'] + cols_monetarias]

    def highlight_total_row(row):
        is_total = row['Órgão'] == 'TOTAL GERAL DA TABELA'
        styles = ['font-weight: bold; background-color: #f0f0f0'] * len(row) if is_total else [''] * len(row)
        return styles

    styled_table = (
        df_tabela.style
        .apply(highlight_total_row, axis=1)
        .format({col: 'R$ {:,.2f}' for col in cols_monetarias})
    )

    st.dataframe(
        styled_table,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("---")
    st.caption("Fonte: Tabela I - Classificação por Órgãos e Unidades Orçamentárias dos Projetos de LOA.")

else:
    st.error("Nenhum arquivo LOA de Despesa foi encontrado. Certifique-se de que os arquivos necessários estão presentes.")


# =========================================================================
# SEÇÃO 3: HISTÓRICO E COMPOSIÇÃO DA RECEITA 
# =========================================================================
st.markdown("---")
st.header("3. Análise da Receita Orçamentária")
st.markdown("Evolução do total da receita e detalhamento de sua composição (Tabela Resumida do LOA).")

# 3.1. Gráfico de Histórico do Total da Receita
st.subheader("Evolução Histórica da Receita Geral Orçada (2024-2026)")

df_receita_total = RECEITA_COMPOSICAO.sum(numeric_only=True).to_frame(name='Receita Geral (R$)').reset_index()
df_receita_total.columns = ['Ano', 'Receita Geral (R$)']
df_receita_total['Ano'] = df_receita_total['Ano'].str.replace(' \(R\$\)', '', regex=True).astype(int)
df_receita_total['Receita (Milhões)'] = df_receita_total['Receita Geral (R$)'] / 1_000_000

fig_linha_total = px.line(
    df_receita_total,
    x='Ano',
    y='Receita (Milhões)',
    title='Evolução da Receita Geral Orçada (R$ Milhões)',
    markers=True,
    labels={'Receita (Milhões)': 'Valor Orçado (R$ Milhões)'}
)
fig_linha_total.update_layout(xaxis=dict(tickmode='array', tickvals=df_receita_total['Ano'].unique()))
fig_linha_total.update_traces(hovertemplate='Ano: %{x}<br>Receita: R$ %{y:.2f} Milhões')

st.plotly_chart(fig_linha_total, use_container_width=True)

# 3.2. Gráfico de Evolução da Composição da Receita por Fonte (Linhas)
st.subheader("Gráfico: Evolução da Composição da Receita por Fonte")

df_receita_long = pd.melt(
    RECEITA_COMPOSICAO,
    id_vars='Tipo de Receita',
    value_vars=['2024 (R$)', '2025 (R$)', '2026 (R$)'],
    var_name='Ano',
    value_name='Valor Orçado'
)

df_receita_long['Ano'] = df_receita_long['Ano'].str.replace(' \(R\$\)', '', regex=True).astype(int)
df_receita_long['Valor (Milhões)'] = df_receita_long['Valor Orçado'] / 1_000_000

fig_linha_fonte = px.line(
    df_receita_long,
    x='Ano',
    y='Valor (Milhões)',
    color='Tipo de Receita',
    title='Evolução Anual das Principais Fontes de Receita (R$ Milhões)',
    markers=True,
    labels={'Valor (Milhões)': 'Valor (R$ Milhões)', 'Tipo de Receita': 'Fonte de Receita'}
)

fig_linha_fonte.update_layout(xaxis=dict(tickmode='array', tickvals=df_receita_long['Ano'].unique()))
fig_linha_fonte.update_traces(hovertemplate='Ano: %{x}<br>Fonte: %{customdata[0]}<br>Orçado: R$ %{y:.2f} Milhões', customdata=df_receita_long[['Tipo de Receita']])

st.plotly_chart(fig_linha_fonte, use_container_width=True)
