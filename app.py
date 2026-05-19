# importações
import streamlit as st

# config global
st.set_page_config(
    page_title="Sistema de Apoio ao SAU",
    page_icon="✈️",
)

# declaração e mapeamento de página
pagina_inicio = st.Page(
    "pages/inicio.py",
    title="Página Inicial",
    icon="🏠",
    default=True # tela que abre primeiro
)

pagina_gerencial = st.Page(
    "pages/painel_gerencial.py",
    title="Página Gerencial",
    icon="📊"
)

pagina_operacional = st.Page(
    "pages/lista_operacional.py",
    title="Página Operacional",
    icon="⚙️"
)

# 3. Criamos a navegação, mas ESCONDEMOS a barra lateral com position="hidden"
navegacao = st.navigation(
    [pagina_inicio, pagina_gerencial, pagina_operacional], 
    position="hidden" # <--- Esta linha esconde o menu lateral cinza do Streamlit
)

navegacao.run()
