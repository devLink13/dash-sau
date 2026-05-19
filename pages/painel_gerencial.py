import pandas as pd
import streamlit as st
from datetime import datetime
from pathlib import Path

st.set_page_config(layout="wide")
st.title("📊 Painel Estratégico de Ordens de Serviço (SAU)")
st.subheader("Bem vindo, admin!")
st.markdown("Tratamento de dados e inteligência visual para fechamento de chamados.")
st.markdown("<br>", unsafe_allow_html=True)
# consante global para o arquivo
DATA_FILE_XLS = Path("data/data_uploaded.xls")

# função para carregar os dados
@st.cache_data # <--- Esta linha é fundamental para otimizar a performance, evitando recarregamentos desnecessários
def load_data():
    if not DATA_FILE_XLS.exists():
        st.warning("Nenhum arquivo de dados encontrado.")
        return None
    
    try:
        df = pd.read_excel(DATA_FILE_XLS)

    except Exception as error:
        st.error(f"Erro ao ler o arquivo: {str(error).lower()}")
        return None

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

    # retirar o BACG e '[]' AO LADO DE CADA OBJETO
    # exemplo: "BACG[OFICINA DE MOTORES]" -> "OFICINA DE MOTORES"
    if 'Objeto' in df.columns:
        df['Objeto'] = (
            df['Objeto']
            .astype(str)
            .str.replace(r'(?i)BACG\s*\[?\s*(.*?)\s*\]?', r'\1', regex=True)  
            .str.replace(r'[\[\]]', '', regex=True)
            .str.strip()
        )
    
    return df


df = load_data()
if df is None:
    st.warning("Arquivo de dados não encontrado ou inválido.")  
    st.stop()

try:
    st.sidebar.title("⚙️ Filtros do Sistema")
    st.sidebar.header("Menu")
    st.sidebar.caption("Use os filtros abaixo para refinar os dados exibidos no painel. Você pode selecionar uma ou mais opções em cada categoria, e ajustar o intervalo de dias em aberto para focar nos chamados mais críticos.")
    
    # Preparar opções para filtros
    lista_objetos = sorted(df['Objeto'].dropna().unique().tolist())
    objetos_selecionados = st.sidebar.multiselect("Oficina (Objeto):",
                                                  options=lista_objetos,
                                                  default=lista_objetos,
                                                  help='selecione a(s) oficina(s) desejada(s) para filtrar os chamados',
                                                  placeholder="escolha uma ou mais oficinas")

    lista_oms = sorted(df['OM'].dropna().unique().tolist())
    oms_selecionadas = st.sidebar.multiselect("Esquadrão Solicitante:", options=lista_oms,
                                            default=lista_oms,
                                            help='selecione a(s) OM(s) desejada(s) para filtrar os chamados',
                                            placeholder="escolha um ou mais esquadrões")

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
        st.metric("📦 Total de OS Abertas", len(df_filtrado))
        em_atendimento = len(df_filtrado[df_filtrado['Status'].str.lower() == 'atendimento']) if 'Status' in df_filtrado.columns else 0
        st.metric("⚡ Em Atendimento", em_atendimento)
    with col2:
        media_dias = df_filtrado['Dias em Aberto'].dropna().mean()
        st.metric("⏱️ Média de Tempo de Espera", f"{media_dias:.0f} dias" if not pd.isna(media_dias) else "0 dias")
    with col3:
        criticos = len(df_filtrado[df_filtrado['Dias em Aberto'] > 90])
        st.metric("🔴 OS Críticas (>90 dias)", criticos)
    with col4:
        # colocar os chamados com status 'A. AQUISIÇÃO'
        em_aquisicao = len(df_filtrado[df_filtrado['Status'].str.lower() == 'a. aquisição']) if 'Status' in df_filtrado.columns else 0
        st.metric("🛒 Em Aquisição", em_aquisicao)

    st.markdown("---")

    col_grafico1, col_grafico2 = st.columns(2)
    with col_grafico1:
        st.subheader("📋 Acúmulo por Oficina (Onde está o gargalo?)")
        grafico_objeto = df_filtrado['Objeto'].value_counts()
        st.bar_chart(grafico_objeto)
    with col_grafico2:
        st.subheader("🏢 Maiores Solicitantes (Quem mais demanda?)")
        grafico_om = df_filtrado['OM'].value_counts()
        st.bar_chart(grafico_om)

    st.markdown("---")

    # exibir a tabela de chamados geral
    st.subheader("🔍 Todos Chamados em lista")
    st.write("Use os filtros laterais para refinar a lista (por oficina, esquadrão ou dias em aberto)")
    st.write("Use a lupa para pesquisa textual (nome do militar solicitante, descrição do problema, etc)")
    # Define as colunas que queremos mostrar, na ordem desejada
    colunas_visao = ['Nº', 'Dias em Aberto', 'Objeto', 'OM', 'Solicitante', 'Status', 'Descrição do Problema']
    # Garantir que todas as colunas estejam presentes
    colunas_visao = [c for c in colunas_visao if c in df_filtrado.columns]
    df_visao = df_filtrado[colunas_visao].sort_values(by='Nº', ascending=False)

    st.dataframe(df_visao, use_container_width=True, hide_index=True)
    st.markdown("---")

    #exibir a tabela de chamados em aquisição
    st.subheader("🛒 Chamados em Aquisição")
    colunas_visao = ['Nº', 'Dias em Aberto', 'Objeto', 'OM', 'Solicitante', 'Status', 'Descrição do Problema']

    # exibir apenas os chamados com status 'A. AQUISIÇÃO' e com as colunas definidas
    df_aquisicao = df_filtrado[df_filtrado['Status'].str.lower() == 'a. aquisição'][colunas_visao].sort_values(by='Dias em Aberto', ascending=False)
    st.dataframe(df_aquisicao, use_container_width=True, hide_index=True)
    st.markdown("---")

    # exibir a tabela de chamados em atendimento
    st.subheader("⚡ Chamados em Atendimento")
    colunas_visao = ['Nº', 'Dias em Aberto', 'Objeto', 'OM', 'Solicitante', 'Status', 'Descrição do Problema']
    # exibir apenas os chamados com status 'ATEatus'].str.lower() == 'a. aquisição'][colunas_visao].sort_values(by='Dias em Aberto', ascending=False)
    st.dataframe(df_aquisicao, use_container_width=True, hide_index=True)
    st.markdown("---")

    # exibir a tabela de chamados em atendimento
    st.subheader("⚡ Chamados em Atendimento")
    colunas_visao = ['Nº', 'Dias em Aberto', 'Objeto', 'OM', 'Solicitante', 'Status', 'Descrição do Problema']
    # exibir apenas os chamados com status 'ATENDIMENTO' e com as colunas definidas
    df_atendimento = df_filtrado[df_filtrado['Status'].str.lower() == 'atendimento'][colunas_visao].sort_values(by='Dias em Aberto', ascending=False)
    st.dataframe(df_atendimento, use_container_width=True, hide_index=True)
    st.markdown("---")

    #configurar a sidebar para sair do sistema
    with st.sidebar:
        if st.button("SAIR", type='primary', use_container_width=True):
            st.switch_page("pages/inicio.py")

except Exception as e:
    st.error(f"Erro ao processar o arquivo de chamados: {e}")
    st.info("Verifique o formato do arquivo e os nomes das colunas esperadas (ex.: 'Ab.', 'Objeto', 'OM', 'Solicitante', 'Solucionador').")