import streamlit as st
from utils.router import login_redirect

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

# session_state para renderização de conteúdo dinâmico
if 'current_view' not in st.session_state:
    st.session_state.current_view = None
    

# ==========================================================
# RENDERIZAR CONTEUDO DE ATUALIZAR CHAMADOS
# ==========================================================
def renderizar_atualizar_chamados():
    st.subheader("Atualizar Chamados")
    st.markdown(
        """
        Para atualizar os chamados, siga os passos abaixo:
        1. Exporte a lista de chamados atualizada do sistema SAU no formato `.xls` ou `.xlsx`.
        2. Clique no botão "Carregar arquivo de dados" e selecione o arquivo exportado.
        3. Aguarde a mensagem de sucesso indicando que o arquivo foi carregado corretamente.
        
        **Observação:** Certifique-se de que o arquivo esteja formatado corretamente para garantir que os dados sejam processados sem erros.
        """,
        unsafe_allow_html=True,
    )

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

    
    st.sidebar.button("Despachar Chamados para Oficinas", use_container_width=True, 
                      on_click=lambda: setattr(st.session_state, 'current_view', 'despacho_chamados'))
    st.sidebar.button("Detalhamento de Chamados", use_container_width=True, 
                      on_click=lambda: setattr(st.session_state, 'current_view', 'detalhamento_chamados'))
    st.sidebar.button("Gerar Relatório", use_container_width=True, 
                      on_click=lambda: setattr(st.session_state, 'current_view', 'relatorios'))
    st.sidebar.button("Configurações", use_container_width=True, 
                      on_click=lambda: setattr(st.session_state, 'current_view', 'configuracoes'))

    st.sidebar.button("Atualizar Chamados", use_container_width=True, on_click=lambda: setattr(st.session_state, 'current_view', 'atualizar_chamados'))
    st.markdown(
        "<div style='text-align: right; color: red;'>"
        "última atualização do banco de dados em: 26/02/2024 14:30"
        "</div>"
        "<br>",
        unsafe_allow_html=True,
    )

    st.sidebar.button("Sair", use_container_width=True, type="primary", on_click= lambda: setattr(st.session_state, 'logado', False))

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
