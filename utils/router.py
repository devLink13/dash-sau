# ============================================================  
# funções de roteamento para navegação entre páginas streamlit
# ============================================================

import streamlit as st

# função para redirecionar para a página a qual tem permissão de acesso após o login
def login_redirect():
    
    try:
        if not st.session_state.logado:
            st.session_state.clear() # Limpa o session_state para evitar dados residuais
            st.switch_page("pages/login.py") # Redireciona para a página de login se o usuário não estiver logado
            st.stop()

        credentials = {
            "nome_guerra": st.session_state.dados_militar["nome_guerra"],
            "posto": st.session_state.dados_militar["posto"],
            "funcao": st.session_state.dados_militar["funcao"],
            "secao": st.session_state.dados_militar["secao"],
        }

        if credentials["funcao"] == 'Comando':
            st.switch_page("pages/visao_comandante.py") # Redireciona para a página do comandante
            st.stop()
        elif credentials["funcao"] == "Encarregado":
            st.switch_page("pages/visao_encarregado.py") # Redireciona para a página do encarregado
            st.stop()
        elif credentials["funcao"] in ['Auxiliar', 'Técnico']:
            st.switch_page("pages/visao_tecnico.py") # Redireciona para a página do auxiliar ou técnico
            st.stop()
        elif credentials['funcao'] in ['Chefia', 'Direção', 'Outra']:
            st.switch_page("pages/visao_chefia.py") # Redireciona para a página da chefia
            st.stop()

    except Exception as e:
        st.error(f"Ocorreu um erro ao redirecionar: {e}")
        st.switch_page("pages/login.py") # Redireciona para a página de login em caso de erro
        st.stop()

