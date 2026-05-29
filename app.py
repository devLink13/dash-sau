# importações
import streamlit as st
from supabase import create_client, Client

# conexão global ao supabase
if 'supabase' not in st.session_state:
    URL_BANCO = st.secrets['supabase']['url']
    KEY_BANCO = st.secrets['supabase']['key']
    supabase_cliente = create_client(URL_BANCO, KEY_BANCO)
    st.session_state.supabase = supabase_cliente # Armazena o cliente do Supabase no session_state para acesso global

# config global
st.set_page_config(
    page_title="Sistema de Apoio ao SAU",
    page_icon="✈️",
    
)

# declaração e mapeamento de página
pagina_login = st.Page(
    "pages/login.py",
    title="Login",
    icon="🔐",
    default=True    # tela que abre primeiro
)


pagina_gerencial = st.Page(
    "pages/painel_gerencial.py",
    title="Página Gerencial",
    icon="📊",
    default=False # Não abre esta página por padrão, pois queremos que o login seja a primeira tela que o usuário veja.
)


pagina_visao_comandante = st.Page(
    "pages/visao_comandante.py",
    title="Visão Comandante",
    icon="🧑‍✈️",
    default=False # Não abre esta página por padrão, pois queremos que o login seja a primeira
)

pagina_visao_chefia = st.Page(
    "pages/visao_chefia.py",
    title="Visão Chefia",
    icon="👔",
    default=False # Não abre esta página por padrão, pois queremos que o login seja a primeira tela que o usuário veja.
)

pagina_visao_encarregado = st.Page(
    "pages/visao_encarregado.py",
    title="Visão Encarregado",
    icon="🧑‍💼",
    default=False # Não abre esta página por padrão, pois queremos que o login seja a primeira tela que o usuário veja.
)

pagina_visao_tecnico = st.Page(
    "pages/visao_tecnico.py",
    title="Visão Técnico",
    icon="🧑‍🔧",
    default=False # Não abre esta página por padrão, pois queremos que o login seja a primeira tela que o usuário veja.
)

# 3. Criamos a navegação, mas ESCONDEMOS a barra lateral com position="hidden"
navegacao = st.navigation(
    [pagina_login, pagina_gerencial, pagina_visao_comandante, pagina_visao_chefia, pagina_visao_encarregado, pagina_visao_tecnico], 
    position="hidden" # <--- Esta linha esconde o menu lateral cinza do Streamlit
)

navegacao.run()
