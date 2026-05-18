import streamlit as st
from pathlib import Path

st.title("🏠 Bem-vindo ao Sistema de Apoio ao SAU da BACG")
st.markdown("""
Esta ferramenta foi desenvolvida para otimizar o fluxo de gerenciamento de Ordens de Serviço do EIE da BACG.
- Utilize o menu lateral para alternar entre as visões estratégicas e operacionais.
- Certifique-se de atualizar o arquivo `.csv` na pasta raiz para alimentar os dados.
            
- Carregue a base de dados atualizada, no formato '.xls' exporta do sistema de chamado SAU.
""")

# CRIAR UM UPLOADER DE ARQUIVOS

# estilizar a caixa de upload
st.markdown("""
* INSIRA O ARQUIVO DE DADOS AQUI
            """)
uploaded_file = st.file_uploader("Carregar arquivo de dados (.xlsx ou .csv)", type=["xls"])

if uploaded_file is not None:
    # salvar o arquivo na pasta data
    data_path = Path("data/data_uploaded.xls")

    # mudar para a página de painel gerencial após upload/sucesso
    st.success("Arquivo carregado com sucesso!")
    st.switch_page("pages/painel_gerencial.py")

