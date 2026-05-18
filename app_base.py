import pandas as pd
import streamlit as st
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Gestão de chamados - SAU", layout="wide")
st.title("📊 Painel Estratégico de Ordens de Serviço (SAU)")
st.markdown("Tratamento de dados e inteligência visual para fechamento de chamados.")

DATA_FILE_XLS = Path(__file__).parent / "Chamados fevereiro abertos.xls"
DATA_FILE_CSV = Path(__file__).parent / "Chamados fevereiro abertos.xls - chamadosDT.csv"

@st.cache_data
def carregar_dados():
    # Tenta carregar .xls primeiro, depois tenta o CSV de fallback
    if DATA_FILE_XLS.exists():
        try:
            df = pd.read_excel(DATA_FILE_XLS)
        except Exception as e:
            msg = str(e).lower()
            # Se o erro indicar que o xlrd não está disponível, tenta o CSV de fallback se houver
            if 'xlrd' in msg or 'install xlrd' in msg or isinstance(e, ImportError):
                if DATA_FILE_CSV.exists():
                    try:
                        df = pd.read_csv(DATA_FILE_CSV, encoding='utf-8')
                    except Exception as e2:
                        return None, f"Falha ao ler o arquivo Excel e falha ao ler o CSV de fallback: {e2}"
                else:
                    # Retorna mensagem de erro para ser tratada pela UI em vez de levantar exceção
                    return None, ("Leitura do arquivo .xls requer o pacote 'xlrd'.\n"
                                  "Opções:\n"
                                  "  - Instale localmente: pip install xlrd\n"
                                  "  - Converta o arquivo para .xlsx ou CSV e coloque na raiz do projeto\n"
                                  "  - Ou use o botão abaixo para enviar o arquivo manualmente via este app")
            else:
                return None, f"Falha ao ler o arquivo Exatualizar o arquivo .cscel: {e}"
    elif DATA_FILE_CSV.exists():
        try:
            df = pd.read_csv(DATA_FILE_CSV, encoding='utf-8')
        except Exception as e:
            return None, f"Falha ao ler o arquivo CSV de fallback: {e}"
    else:
        return None, "Nenhum dos arquivos de dados foi encontrado. Coloque 'Chamados fevereiro abertos.xls' ou 'Chamados fevereiro abertos.xls - chamadosDT.csv' na raiz do projeto."

    # Normaliza nomes de colunas: remove espaços extremos
    df.columns = [str(c).strip() for c in df.columns]

    # Detecta a coluna de data de abertura
    possible_date_cols = ['Ab.', 'Abertura', 'Data Abertura', 'Data', 'Data de Abertura']
    date_col = None
    for c in possible_date_cols:
        if c in df.columns:
            date_col = c
            break
    # se nenhum encontrada, tenta detectar coluna com data inferindo por dtype
    if date_col is None:
        for c in df.columns:
            sample = df[c].dropna().astype(str).head(10).to_list()
            if any('/' in s or '-' in s for s in sample):
                date_col = c
                break

    if date_col is None:
        # não temos coluna de data, criamos uma com NaT para não quebrar o fluxo
        df['Ab.'] = pd.NaT
    else:
        # padroniza para coluna 'Ab.'
        if date_col != 'Ab.':
            df = df.rename(columns={date_col: 'Ab.'})
        # tenta parse com formatos comuns
        df['Ab.'] = pd.to_datetime(df['Ab.'], dayfirst=True, errors='coerce')

    # Calcula dias em aberto onde possível
    df['Dias em Aberto'] = (pd.Timestamp.now() - df['Ab.']).dt.days

    # Garante colunas textuais e trata espaços
    for col in ['Status', 'Objeto', 'OM', 'Solicitante', 'Solucionador']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        else:
            # cria coluna vazia para manter consistência
            df[col] = ''

    # Garante coluna 'Nº' e 'Descrição do Problema' existam
    if 'Nº' not in df.columns:
        if 'Numero' in df.columns:
            df = df.rename(columns={'Numero': 'Nº'})
        else:
            df['Nº'] = ''
    if 'Descrição do Problema' not in df.columns:
        # tenta alternativas
        for alt in ['Descrição', 'Descrição Problema', 'Descrição do chamado']:
            if alt in df.columns:
                df = df.rename(columns={alt: 'Descrição do Problema'})
                break
        else:
            df['Descrição do Problema'] = ''

    return df, None

def process_df(df):
    # Normaliza nomes de colunas: remove espaços extremos
    df.columns = [str(c).strip() for c in df.columns]

    # Detecta a coluna de data de abertura
    possible_date_cols = ['Ab.', 'Abertura', 'Data Abertura', 'Data', 'Data de Abertura']
    date_col = None
    for c in possible_date_cols:
        if c in df.columns:
            date_col = c
            break
    # se nenhum encontrada, tenta detectar coluna com data inferindo por amostra
    if date_col is None:
        for c in df.columns:
            sample = df[c].dropna().astype(str).head(10).to_list()
            if any('/' in s or '-' in s for s in sample):
                date_col = c
                break

    if date_col is None:
        df['Ab.'] = pd.NaT
    else:
        if date_col != 'Ab.':
            df = df.rename(columns={date_col: 'Ab.'})
        df['Ab.'] = pd.to_datetime(df['Ab.'], dayfirst=True, errors='coerce')

    # Calcula dias em aberto
    df['Dias em Aberto'] = (pd.Timestamp.now() - df['Ab.']).dt.days

    # Garante colunas textuais e trata espaços
    for col in ['Status', 'Objeto', 'OM', 'Solicitante', 'Solucionador']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        else:
            df[col] = ''

    # Garante coluna 'Nº' e 'Descrição do Problema' existam
    if 'Nº' not in df.columns:
        if 'Numero' in df.columns:
            df = df.rename(columns={'Numero': 'Nº'})
        else:
            df['Nº'] = ''
    if 'Descrição do Problema' not in df.columns:
        for alt in ['Descrição', 'Descrição Problema', 'Descrição do chamado']:
            if alt in df.columns:
                df = df.rename(columns={alt: 'Descrição do Problema'})
                break
        else:
            df['Descrição do Problema'] = ''

    return df


# Fonte de dados: uploader na sidebar ou arquivo no servidor
st.sidebar.header("📂 Fonte de dados")
fonte = st.sidebar.selectbox("Selecione a fonte de dados:", ("Enviar arquivo (recomendado)", "Usar arquivo no servidor (raiz)"))

df = None
load_err = None

if fonte == "Enviar arquivo (recomendado)":
    st.header("📥 Bem-vindo")
    st.write("Envie o arquivo de chamados (.xls, .xlsx ou .csv) pela barra lateral para começar.")
    uploaded = st.sidebar.file_uploader("Envie o arquivo de chamados:", type=['xls', 'xlsx', 'csv'])
    if uploaded is None:
        st.info("Aguardando arquivo. Use a barra lateral para enviar.")
        st.stop()

    # lê o arquivo enviado
    try:
        uploaded.seek(0)
        name = uploaded.name.lower()
        if name.endswith('.csv') or (hasattr(uploaded, 'type') and uploaded.type == 'text/csv'):
            df = pd.read_csv(uploaded)
        else:
            # tenta usar openpyxl para .xlsx e fallback para .xls (que pode requerer xlrd)
            if name.endswith('.xlsx'):
                df = pd.read_excel(uploaded, engine='openpyxl')
            else:
                df = pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"Falha ao ler o arquivo enviado: {e}")
        if 'xlrd' in str(e).lower():
            st.info("Leitura de .xls requer o pacote 'xlrd'. Instale com: pip install xlrd ou converta para .xlsx/.csv.")
        st.stop()

    # Normaliza e prepara o DataFrame carregado via upload
    try:
        df = process_df(df)
    except Exception as e:
        st.error(f"Erro ao processar o DataFrame enviado: {e}")
        st.stop()

else:
    # tenta carregar do servidor/raiz
    df, load_err = carregar_dados()
    if df is None:
        st.error(load_err)
        st.info("Se preferir, envie o arquivo pela barra lateral (opção 'Enviar arquivo').")
        st.stop()

try:
    st.sidebar.header("⚙️ Filtros do Sistema")

    # Preparar opções para filtros
    lista_objetos = sorted(df['Objeto'].dropna().unique().tolist())
    objetos_selecionados = st.sidebar.multiselect("Especialidade (Objeto):", options=lista_objetos, default=lista_objetos)

    lista_oms = sorted(df['OM'].dropna().unique().tolist())
    oms_selecionadas = st.sidebar.multiselect("OM Solicitante:", options=lista_oms, default=lista_oms)

    # Filtro por intervalo de dias em aberto
    max_dias = int(df['Dias em Aberto'].dropna().max()) if df['Dias em Aberto'].dropna().size > 0 else 0
    dias_intervalo = st.sidebar.slider("Dias em Aberto (até)", min_value=0, max_value=max(365, max_dias), value=max_dias)

    # Aplica filtros
    df_filtrado = df.copy()
    if lista_objetos:
        df_filtrado = df_filtrado[df_filtrado['Objeto'].isin(objetos_selecionados)]
    if lista_oms:
        df_filtrado = df_filtrado[df_filtrado['OM'].isin(oms_selecionadas)]
    if 'Dias em Aberto' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Dias em Aberto'] <= dias_intervalo]

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de OS Abertas", len(df_filtrado))
    with col2:
        media_dias = df_filtrado['Dias em Aberto'].dropna().mean()
        st.metric("Média de Tempo de Espera", f"{media_dias:.0f} dias" if not pd.isna(media_dias) else "0 dias")
    with col3:
        criticos = len(df_filtrado[df_filtrado['Dias em Aberto'] > 90])
        st.metric("🔴 OS Críticas (>90 dias)", criticos)
    with col4:
        nao_atribuidos = len(df_filtrado[df_filtrado['Solucionador'].str.lower() == 'não atribuído']) if 'Solucionador' in df_filtrado.columns else 0
        st.metric("⚠️ Sem Distribuição", nao_atribuidos)

    st.markdown("---")

    col_grafico1, col_grafico2 = st.columns(2)
    with col_grafico1:
        st.subheader("📋 Acúmulo por Especialidade (Onde está o gargalo?)")
        grafico_objeto = df_filtrado['Objeto'].value_counts()
        st.bar_chart(grafico_objeto)
    with col_grafico2:
        st.subheader("🏢 Maiores Solicitantes (Quem mais demanda?)")
        grafico_om = df_filtrado['OM'].value_counts().head(10)
        st.bar_chart(grafico_om)

    st.markdown("---")

    st.subheader("🔍 Lista de Trabalho Priorizada (Ordenada por mais antigas)")
    colunas_visao = ['Nº', 'Dias em Aberto', 'Objeto', 'OM', 'Solicitante', 'Solucionador', 'Descrição do Problema']
    # Garantir que todas as colunas estejam presentes
    colunas_visao = [c for c in colunas_visao if c in df_filtrado.columns]
    df_visao = df_filtrado[colunas_visao].sort_values(by='Dias em Aberto', ascending=False)

    st.dataframe(df_visao, use_container_width=True, hide_index=True)

except FileNotFoundError as fnf:
    st.error(str(fnf))
    st.info("Coloque o arquivo 'Chamados fevereiro abertos.xls' ou 'Chamados fevereiro abertos.xls - chamadosDT.csv' na raiz deste projeto.")
except Exception as e:
    st.error(f"Erro ao processar o arquivo de chamados: {e}")
    st.info("Verifique o formato do arquivo e os nomes das colunas esperadas (ex.: 'Ab.', 'Objeto', 'OM', 'Solicitante', 'Solucionador').")