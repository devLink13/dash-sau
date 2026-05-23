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


pagina_inicio = st.Page(
    "pages/inicio.py",
    title="Página Inicial",
    icon="🏠",
    default=False # Não abre esta página por padrão, pois queremos que o login seja a primeira tela que o usuário veja.
)

pagina_gerencial = st.Page(
    "pages/painel_gerencial.py",
    title="Página Gerencial",
    icon="📊",
    default=False # Não abre esta página por padrão, pois queremos que o login seja a primeira tela que o usuário veja.
)

pagina_operacional = st.Page(
    "pages/lista_operacional.py",
    title="Página Operacional",
    icon="⚙️",
    default=False # Não abre esta página por padrão, pois queremos que o login seja a primeira tela que o usuário veja.
)

# 3. Criamos a navegação, mas ESCONDEMOS a barra lateral com position="hidden"
navegacao = st.navigation(
    [pagina_login, pagina_inicio, pagina_gerencial, pagina_operacional], 
    position="hidden" # <--- Esta linha esconde o menu lateral cinza do Streamlit
)

navegacao.run()
