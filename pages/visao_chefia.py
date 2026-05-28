import streamlit as st
from utils.router import login_redirect
from time import sleep
import pandas as pd

# ==========================================================
# pagina de visão da chefia
# ==========================================================

# configura a página para layout wide
st.set_page_config(layout="wide")

# ==========================================================
# verificações de login
# ==========================================================
if 'logado' not in st.session_state or st.session_state.logado == False:
    st.session_state.clear() # limpa o session_state para evitar dados residuais
    login_redirect() # redireciona para a página de login se não estiver logado
    st.stop()  # Interrompe a execução do script

# verifica se o usuário tem permissão de acesso à visão da chefia
if 'logado' in st.session_state and st.session_state.dados_militar.get("funcao") not in ['Chefia', 'Direção', 'Outra']:
    login_redirect() # redireciona para a página de login se não tiver permissão de acesso
    st.stop()  # Interrompe a execução do script

# ==========================================================
# inicialização do states
# ==========================================================

# session_state para renderização de conteúdo dinâmico
if 'current_view' not in st.session_state:
    st.session_state.current_view = None

# criar um state para desabilitar alguns botões da sidebar caso não haja dados inseridos
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    

# ==========================================================
# RENDERIZAR CONTEUDO DE ATUALIZAR CHAMADOS
# ==========================================================
def renderizar_atualizar_chamados():
    

    top_container = st.container(border=True)
    with top_container:
        st.subheader("Atualizar Chamados ou Inserir chamados no Sistema", text_alignment='center')
        st.markdown("---")  # linha divisória
        st.markdown(
            """
            Para atualizar os chamados, siga os passos abaixo:
            1. Exporte a lista de chamados atualizada do sistema SAU no formato `.xls` ou `.xlsx`.
            2. Clique no botão "Carregar Planilha de Chamados" e selecione o arquivo exportado.
            3. Aguarde a mensagem de sucesso indicando que o arquivo foi carregado corretamente.
            
            **Observação:** Certifique-se de que o arquivo esteja formatado corretamente para garantir que os dados sejam processados sem erros.
            """,
            unsafe_allow_html=True,
        )
    
    main_container = st.container(border=False)
    with main_container:
        # dividir o container em duas colunas (30% e 70%)
        col_esquerda, col_direita = st.columns([3, 7])

        with col_esquerda:
            # =============================
            # container de upload de arquivo
            # =============================
            with st.container(border=True):
                st.markdown("### Carregar Planilha de Chamados")
                st.markdown('---')

                uploaded_file = st.file_uploader("Selecione o arquivo de dados (.xlsx ou .csv)", type=["xls", "xlsx", "csv"])
                if uploaded_file is not None:
                    with st.spinner(f"Processando o arquivo {uploaded_file.name}..."):
                        sleep(2)  # Simula um tempo de processamento

                        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(('.xls', '.xlsx')) else pd.read_csv(uploaded_file)


                        
                    st.toast(f"Arquivo {uploaded_file.name} carregado com sucesso!", icon="✅")

            # =============================
            # container que exibe insights prévios para conferência de dados integros
            # =============================
            if uploaded_file is not None: # só exibe se temos um arquivo carregado
                with st.container(border=True):
                    
                    # marca que temos dados carregados (habilita botões da sidebar)
                    st.session_state.data_loaded = True

                    st.markdown("### Insights Rápidos")
                    # infos básicas
                    n_rows, n_cols = df.shape
                    n_duplicados = int(df.duplicated().sum())
                    
                    # métricas
                    c1, c2, c3 = st.columns(3)
                    c1.metric("qtd chamados", f"{n_rows:,}")
                    c2.metric("Colunas (padrão é 16)", f"{n_cols:,}")
                    c3.metric("Duplicados", f"{n_duplicados:,}")

                    st.markdown("---")

                    # colunas com mais valores ausentes (top 10)
                    with st.expander("Colunas com mais valores ausentes"):
                        miss_by_col = df.isna().sum().sort_values(ascending=False)
                        st.bar_chart(miss_by_col.head(10))

                    # escolher uma coluna para inspeção rápida
                    cols = list(df.columns)
                    sel_col = st.selectbox("Selecionar coluna para inspeção rápida", options=cols)

                    if sel_col:
                        col_info, col_vals = st.columns([1, 2])
                        with col_info:
                            st.write("Nulos:", int(df[sel_col].isna().sum()))
                            st.write("Únicos:", int(df[sel_col].nunique(dropna=True)))
                        with col_vals:
                            st.write("Top valores")
                            st.table(df[sel_col].value_counts(dropna=True).head(6))

                
        with col_direita:
            if uploaded_file is not None: # só exibe se temos um arquivo carregado
                with st.container(border=True):
                    st.markdown("### Pré-visualização dos Dados")
                    st.markdown('---')

                    if uploaded_file is not None:
                        st.table(df.head(2))  # Exibe as primeiras 10 linhas do DataFrame como pré-visualização
                    else:
                        st.warning("Nenhum arquivo carregado. Carregue um arquivo para visualizar os dados aqui.")


        

# ==========================================================
# RENDERIZAR CONTEUDO DE DETALHAMENTO DE CHAMADOS
# ==========================================================
def renderizar_detalhamento_chamados():
    st.subheader("OS's Abertas por Oficinas", text_alignment='right')
    with st.container(border=True):
        # 4 colunas e duas linhas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Elétrica", "150", delta="5%")
            st.metric("Climatização", "20", delta="-5%")
            
        with col2:
            st.metric("Obras", "30", delta="-10%")
            st.metric("Matrículas Canceladas", "10", delta="-2%")
        with col3:
            st.metric("Hidráulica", "15", delta="3%")
            st.metric("Matrículas Rejeitadas", "5", delta="-1%")
        with col4:
            st.metric("Matrículas Concluídas", "120", delta="10%")
            st.metric("Matrículas Expiradas", "8", delta="-4%")

    # container principal da página que se dividirá em 2 colunas (70% e 30%)
    with st.container(border=True):
        col1, col2 = st.columns([7, 3])
        with col1:
            st.subheader("Gráfico de OS's Abertas por Oficinas")
            
        with col2:
            st.subheader("Gráfico de OS's Concluídas por Oficinas")

# =========================================================
# RENDERIZAR CONTEÚDO DE CONFIGURAÇÕES
# =========================================================
def renderizar_configuracoes():
    st.title("Configurações")
    st.markdown(
        """
        Aqui você pode configurar as preferências do sistema, como:
        - Notificações: Ativar ou desativar notificações por e-mail ou SMS.
        - Tema: Escolher entre tema claro ou escuro para a interface.
        - Idioma: Selecionar o idioma de exibição do sistema.
        - Gerenciamento de Usuários: Adicionar, remover ou editar usuários com acesso ao sistema.
        - Integrações: Configurar integrações com outros sistemas ou ferramentas utilizadas pela BACG.
        """)

# ==========================================================
# RENDERIZAR CONTEÚDO DE RELATÓRIOS
# ==========================================================
def renderizar_relatorios():
    st.title("Relatórios")
    st.markdown(
        """
        Aqui você pode gerar relatórios sobre o desempenho do sistema, como:
        - Relatório de Chamados: Visualizar estatísticas e métricas sobre os chamados atendidos.
        - Relatório de Usuários: Analisar o uso do sistema por diferentes usuários.
        - Relatório de Integrações: Verificar o status das integrações com outros sistemas.
        """
    )

# ==========================================================
# RENDERIZAR CONTEÚDO DE DESPACHO DE CHAMADOS
# ==========================================================
def renderizar_despacho_chamados():
    st.title("Despachar Chamados para Oficinas")
    st.markdown(
        """
        Aqui você pode despachar os chamados para as oficinas responsáveis, seguindo os passos abaixo:
        1. Selecione o chamado que deseja despachar.
        2. Escolha a oficina responsável pelo atendimento do chamado.
        3. Clique no botão "Despachar" para enviar o chamado para a oficina selecionada.
        
        **Observação:** Certifique-se de que as informações do chamado estejam completas e corretas antes de despachar para garantir um atendimento eficiente.
        """,
        unsafe_allow_html=True,
    )


# ==========================================================
# RENDERIZAR CONTEÚDO PADRÃO DE BOAS VINDAS
# ==========================================================
def renderizar_conteudo_padrao():
    
    st.title("✈️ Bem-vindo ao Sistema de Apoio ao SAU da BACG 🛠️")
    st.markdown("""
        Esta ferramenta foi desenvolvida para otimizar o fluxo de gerenciamento de Ordens de Serviço do EIE da BACG.
        - Utilize o menu lateral para alternar entre as visões estratégicas e operacionais.
        - Certifique-se de atualizar o arquivo `.xls` exportado diretamente do sistema de chamados SAU para garantir que os dados estejam sempre atuais.
                    
        - Carregue a base de dados atualizada, no formato '.xls', a mesma pode ser exportada na lista de chamados do sistema SAU.
        ```© 2026 Sgt LINK. Todos os direitos reservados. | Sistema de Apoio ao SAU 🇧🇷```
    """, unsafe_allow_html=True)


# ==========================================================
# RENDERIZAR A BARRA LATERAL COM AVATAR E NOME DO USUÁRIO
# ==========================================================
with st.sidebar:
    
    # bloco com avatar redondo e nome/posto
    posto = st.session_state.dados_militar.get("posto", "Posto Desconecido")
    nome = st.session_state.dados_militar.get("nome_guerra", "Usuário")

    # gerar iniciais a partir do nome (até 2 letras)
    iniciais = "".join([parte[0] for parte in nome.split()][:2]).upper()

    # ======================================
    # bloco com avatar redondo e nome/posto
    # ======================================
    st.markdown(
        f"""
        <div style="display:flex;flex-direction:column;align-items:center;padding:10px 0;">
            <div style="
                width:80px;height:80px;border-radius:50%;
                background:#2B6CB0;color:#fff;
                display:flex;align-items:center;justify-content:center;
                font-size:28px;font-weight:700;
                box-shadow:0 2px 6px rgba(0,0,0,0.15);
            ">
                {iniciais}
            </div>
            <div style="margin-top:8px;text-align:center;font-weight:600;color:#fff;">
                {posto}
            </div>
            <div style="font-size:13px;color:#fff;text-align:center;">
                {nome}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")  # linha divisória

    st.sidebar.button("Atualizar/Inserir Chamados", use_container_width=True, on_click=lambda: setattr(st.session_state, 'current_view', 'atualizar_chamados'))

    st.sidebar.button("Despachar Chamados para Oficinas", use_container_width=True, 
                      on_click=lambda: setattr(st.session_state, 'current_view', 'despacho_chamados'), disabled = True if not st.session_state.data_loaded else False)
    st.sidebar.button("Detalhamento de Chamados", use_container_width=True, 
                      on_click=lambda: setattr(st.session_state, 'current_view', 'detalhamento_chamados'), disabled = True if not st.session_state.data_loaded else False)
    st.sidebar.button("Gerar Relatório", use_container_width=True, 
                      on_click=lambda: setattr(st.session_state, 'current_view', 'relatorios'), disabled = True if not st.session_state.data_loaded else False)
    st.sidebar.button("Configurações", use_container_width=True, 
                      on_click=lambda: setattr(st.session_state, 'current_view', 'configuracoes'))

    
    st.markdown(
        "<div style='text-align: right; color: red;'>"
        "última atualização do banco de dados em: 26/02/2024 14:30"
        "</div>"
        "<br>",
        unsafe_allow_html=True,
    )

    st.sidebar.button("Sair", use_container_width=True, type="primary", on_click= lambda: setattr(st.session_state, 'logado', False))



# ==========================================================
# renderização de conteúdo dinâmico
# ==========================================================
if st.session_state.current_view is None:
    renderizar_conteudo_padrao()
elif st.session_state.current_view == "detalhamento_chamados":
    renderizar_detalhamento_chamados()
elif st.session_state.current_view == "configuracoes":
    renderizar_configuracoes()
elif st.session_state.current_view == "relatorios":
    renderizar_relatorios()
elif st.session_state.current_view == "despacho_chamados":
    renderizar_despacho_chamados()
elif st.session_state.current_view == "atualizar_chamados":
    renderizar_atualizar_chamados()
