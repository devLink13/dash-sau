# ==================================================
# MÓDULO PARA PROCESSAMENTO DE DADOS E CHAMADOS
# ==================================================

import pandas as pd
import re

# ==================================================================================
# função de processamento final do dataframe, para deixar ele pronto para o banco de dados
# ==================================================================================
def processar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    
    """

    try:
        # mapear as colunas da planilha para o banco de dados
        mapa_colunas = {
            'Nº': 'numero_os',
            'Objeto': 'objeto',
            'OM': 'om',
            'Solicitante': 'solicitante',
            'Status': 'status',
            'Ab.': 'data_abertura',
            'Mod.': 'data_modificacao',
            'Descrição do Problema': 'descricao',
            'Soluc.': 'solucionador', # Ajuste isso caso o nome venha cortado na planilha
            'Celular': 'celular',
            'Telefone': 'telefone',
            'E-mail': 'email'
        }

        # filtrar e renomear as colunas que importam
        df = df.rename(columns=mapa_colunas)

        # Colunas esperadas no banco (para garantir que só elas passem)
        colunas_esperadas = list(mapa_colunas.values())
        df = df[[col for col in colunas_esperadas if col in df.columns]].copy()

        # 2. Limpeza da coluna "Objeto"
        # Regex para extrair apenas o texto dentro dos colchetes, ou descartar o "BACG ["
        if 'objeto' in df.columns:
            # Ex: "BACG [ELÉTRICA]" -> "ELÉTRICA"
            df['objeto'] = df['objeto'].apply(
                lambda x: re.search(r'\[(.*?)\]', str(x)).group(1) if pd.notnull(x) and '[' in str(x) else x
            )
        
        # 3. Tratamento de Datas (Converte string de data para o padrão datetime)
        if 'data_abertura' in df.columns:
            df['data_abertura'] = pd.to_datetime(df['data_abertura'], format='%d/%m/%Y', errors='coerce').dt.date
        if 'data_modificacao' in df.columns:
            df['data_modificacao'] = pd.to_datetime(df['data_modificacao'], format='%d/%m/%Y', errors='coerce').dt.date

        # 4. Tratamentos de valores em branco e nulos
        # Preenche vazios ou "#VALOR!" com None, que o banco entende como NULL
        df = df.replace({'#VALOR!': None, '': None, pd.NA: None})
        df = df.where(pd.notnull(df), None)

        return df

    except Exception as e:
        return str(e)
    
# ==================================================================================
# função de pré processamento para visualização e pré aceite da tabela
# ==================================================================================
def pre_processar_dataframe(df: pd.DataFrame) -> dict:
    """
    """
    n_rows, n_cols = df.shape
    n_duplicados = int(df.duplicated().sum())
    faltantes_por_coluna = df.isna().sum().sort_values(ascending=False)
    
    # Processar detalhes individuais de cada coluna para inspeção
    detalhes_colunas = {}
    for col in df.columns:
        vc = df[col].value_counts(dropna=True).head(6).reset_index()
        vc.columns = [col, "quantidade"]
        detalhes_colunas[col] = {
            "nulos": int(df[col].isna().sum()),
            "unicos": int(df[col].nunique(dropna=True)),
            "amostra": vc
        }


    return {
        "n_rows": n_rows,
        "n_cols": n_cols,
        "n_duplicados": n_duplicados,
        "faltantes_por_coluna": faltantes_por_coluna,
        "colunas": list(df.columns),
        "detalhes_colunas": detalhes_colunas
    }
    