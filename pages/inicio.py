import streamlit as st
from pathlib import Path
from time import sleep

# configuração da página
st.set_page_config(
    layout='centered'
)

st.title("✈️ Bem-vindo ao Sistema de Apoio ao SAU da BACG 🛠️")
st.markdown("""
Esta ferramenta foi desenvolvida para otimizar o fluxo de gerenciamento de Ordens de Serviço do EIE da BACG.
- Utilize o menu lateral para alternar entre as visões estratégicas e operacionais.
- Certifique-se de atualizar o arquivo `.xls` exportado diretamente do sistema de chamados SAU para garantir que os dados estejam sempre atuais.
            
- Carregue a base de dados atualizada, no formato '.xls', a mesma pode ser exportada na lista de chamados do sistema SAU.
            
```© 2026 Sgt Wesley Souza. Todos os direitos reservados. | Sistema de Apoio ao SAU 🇧🇷```         
""")
# CRIAR UM UPLOADER DE ARQUIVOS

# criar o file uploader para arquivos .xlsx ou .csv
uploaded_file = st.file_uploader("Carregar arquivo de dados (.xlsx ou .csv)", type=["xls"])

if uploaded_file is not None:
    # garantir que o processamento ocorra apenas uma vez por arquivo carregado
    if st.session_state.get("last_uploaded_name") != uploaded_file.name:
        st.session_state["file_processed"] = False
        st.session_state["last_uploaded_name"] = uploaded_file.name

    if not st.session_state.get("file_processed", False):
        with st.spinner(f"Processando o arquivo {uploaded_file.name}..."):
            sleep(2)  # Simula um tempo de processamento
        st.session_state["file_processed"] = True

    if uploaded_file.name.endswith('.csv') or uploaded_file.name.endswith('.xls'):
        st.success("Arquivo carregado com sucesso!")
        if st.button("Iniciar Sistema", type="secondary"):
            # salvar o arquivo na pasta data
            data_path = Path("data/data_uploaded.xls")
            with open(data_path, "wb") as file:
                file.write(uploaded_file.getbuffer())

            # redirecionar para a página do painel gerencial
            st.switch_page("pages/painel_gerencial.py")
            
    else:
        st.error("Formato de arquivo inválido. Por favor, carregue um arquivo .xlsx ou .csv.")
        st.stop()

    


