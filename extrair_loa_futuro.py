import pandas as pd
import os
import tabula 

def extrair_tabela_orgaos(caminho_pdf, ano):
    """
    Tenta extrair a Tabela de Órgãos do LOA, focando em layouts variáveis e limpeza de valores.
    """
    print(f"➡️  Extraindo Tabela de Órgãos do LOA {ano}...")
    
    try:
        # Tenta a extração focando na página 2 com modo stream (melhor para PDFs com poucas linhas divisórias)
        tabelas_list = tabula.read_pdf(
            caminho_pdf,
            pages="2-5",
            guess=True,
            stream=True,  # Tenta modo stream
            multiple_tables=True
        )

        df_selecionado = pd.DataFrame()
        
        # Tenta encontrar a tabela principal (Classificação por Órgãos)
        for df in tabelas_list:
            if df.shape[1] >= 3:
                # Se a tabela tiver 3 ou mais colunas (Código, Especificação, Valor, etc.)
                df_temp = df.copy()
                
                # Tenta padronizar o cabeçalho, assumindo que as primeiras linhas são lixo
                if df_temp.iloc[0].astype(str).str.contains('Código|Órgão|Valor', case=False).any():
                     df_temp = df_temp.iloc[1:].reset_index(drop=True)

                # Tenta padronizar para o formato (Codigo, Especificacao, Valor)
                df_selecionado = df_temp.iloc[:, :3]
                df_selecionado.columns = ['Codigo', 'Especificacao', 'Valor']
                
                # Critério de seleção: a coluna 'Valor' deve ter pelo menos um número
                if df_selecionado['Valor'].astype(str).str.contains(r'[\d,]').any():
                    break
                else:
                    df_selecionado = pd.DataFrame() # Reseta se o critério não for atendido


        if df_selecionado.empty:
            raise ValueError("Não foi possível identificar a Tabela de Classificação por Órgãos com valores monetários.")

        df = df_selecionado.copy()
        df = df.dropna(subset=['Especificacao', 'Valor'])
        
        # 🚨 LIMPEZA AGRESSIVA DE VALORES: Remove R$, quebras de linha e trata a vírgula
        df['Valor'] = df['Valor'].astype(str).str.replace('R$', '', regex=False)
        df['Valor'] = df['Valor'].str.replace('\n', '', regex=False)
        df['Valor'] = df['Valor'].str.replace('.', '', regex=False) # Remove separador de milhares
        df['Valor'] = df['Valor'].str.replace(',', '.', regex=False) # Substitui vírgula por ponto decimal
        
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        
        df = df.dropna(subset=['Valor'])
        
        if df.empty:
            raise ValueError("A extração encontrou a tabela, mas a limpeza resultou em zero valores numéricos válidos.")

        # Salva o arquivo com o nome específico do ano
        nome_arquivo = f'loa_por_orgaos_{ano}.csv'
        df.to_csv(nome_arquivo, index=False)
        print(f"✅ Tabela de Órgãos do LOA {ano} extraída e salva em '{nome_arquivo}'.")
    
    except Exception as e:
        print(f"❌ Erro ao extrair Tabela de Órgãos do LOA {ano}: {e}")

if __name__ == '__main__':
    
    # --- Extração LOA 2025 ---
    caminho_pdf_2025 = 'LOA_2025.pdf'
    if os.path.exists(caminho_pdf_2025):
        extrair_tabela_orgaos(caminho_pdf_2025, 2025)
    else:
        print(f"AVISO: Arquivo '{caminho_pdf_2025}' não encontrado. Pulando 2025.")

    # --- Extração LOA 2026 (Comentado para focar em 2025) ---
    # caminho_pdf_2026 = 'LOA_2026.pdf' 
    # if os.path.exists(caminho_pdf_2026):
    #     extrair_tabela_orgaos(caminho_pdf_2026, 2026)
    # else:
    #     print(f"AVISO: Arquivo '{caminho_pdf_2026}' não encontrado. Pulando 2026.")