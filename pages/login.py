# importações
import streamlit as st
from supabase import create_client, Client
import hashlib
from time import sleep

# verificando se foi estabelecida a conexão com o supabase (definida em app.py) e armazena no session_state.supabase para uso global
if not 'supabase' in st.session_state:
    st.error("Erro: Conexão com o banco de dados não estabelecida. Por favor, verifique as configurações do Supabase.")
elif 'supabase' in st.session_state:
    supabase = st.session_state.supabase # Acessa o cliente do Supabase armazenado no session_state


## função para hash de senha
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

## funções da página
# funções de validação do código
def validar_login(saram, password):
    # consultar o banco de dados para verificar se o SARAM existe e a senha corresponde
    try:
        if not saram or not password:
            return False
        senha_hashed = hash_password(password) # hash da senha fornecida para comparação
        query = supabase.table("usuarios").select("*").eq("saram", saram).execute()
        if query.data and query.data[0]['senha_hash'] == senha_hashed: 
            st.session_state.dados_militar = query.data[0] # Armazena os dados do militar no session_state
            st.session_state.logado = True # Define o estado de logado como True
            return True

    except:
        return False


def validar_cadastro(name, email, password, confirm_password, saram, confirm_saram, funcao, confirm_funcao, posto_graduacao, secao):
    ## vericações básicas de cadastro, como campos preenchidos e correspondência de senha/SARAM
    if not all([name, email, password, confirm_password, saram, confirm_saram, funcao, confirm_funcao, posto_graduacao]): # Verificação de campos vazios
        st.error("Por favor, preencha todos os campos.")
        return False
    if password != confirm_password: # Verificação de senha
        st.error("As senhas não coincidem.")
        return False
    if saram != confirm_saram: # Verificação de SARAM
        st.error("Os SARAMs não coincidem.")
        return False
    if len(saram) != 7 or not saram.isnumeric(): # 7440820 
        st.error("O SARAM deve conter exatamente 7 dígitos numéricos.")
        return False
    
    else: # se passou nas validações
        dados_militar = {
            "nome": name,
            "saram": saram,
            "email": email,
            "senha_hash": hash_password(password=password), # Armazena a senha como hash para segurança
            "funcao": funcao,
            "posto": posto_graduacao,
            "secao": secao
        }

        #gravar os dados no banco de dados (tabela "usuarios")
        try:
            supabase.table("usuarios").insert(dados_militar).execute()
        except:
            return False


    # se der tudo certo, retorna true para indicar cadastro bem-sucedido
    return True


##### INICIO DAS CONFIGURAÇÕES E LAYOUT DA PÁGINA #####

# estados da página
if 'logado' not in st.session_state:
    st.session_state.logado = False
if 'dados_militar' not in st.session_state:
    st.session_state.dados_militar = None


# configurações da página
st.set_page_config(
    layout="centered"
)

# =========================================================
# ÁREA DE LOGIN E CADASTRO(SÓ EXIBIDA SE NÃO ESTIVER LOGADO)
# =========================================================
if not st.session_state.logado: # Se o usuário não estiver logado, exibe a área de login e cadastro

    st.title("🛡️ Portal de Acesso - Seção SAU")

    #criar abas de acesso ao sistema
    tab_login, tab_cadastro = st.tabs(["🔐 Entrar no Sistema", "📝 Cadastrar Novo Usuário"])

    #trabalhando na aba de login
    with tab_login:
        st.subheader("Bem-vindo de volta! Faça login para acessar o sistema.")
        
        #form para campos de user e senha
        with st.form("form_login", clear_on_submit= True):
            saram = st.text_input("SARAM", placeholder="Digite seu SARAM")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            submit_login = st.form_submit_button("Entrar")

            if submit_login:
                if validar_login(saram, password): # se retornar true, o login é bem-sucedido
                    st.toast("Login automático realizado após cadastro bem-sucedido. Redirecionando para a página inicial...")
                    st.switch_page("pages/inicio.py") # Redireciona para a página inicial após login bem-sucedido
                else: # se retornar false, mostra mensagem de erro
                    st.error("SARAM ou senha incorretos. Por favor, tente novamente.")
    #trabalhando na aba de cadastro
    with tab_cadastro:
        st.subheader("Crie uma nova conta para acessar o sistema.")

        st.caption("Aviso: A falsidade, omissão ou inexatidão nas informações prestadas neste formulário "
        "constitui transgressão disciplinar, conforme o Art. 10, itens 67 e 68 do Regulamento "
        "Disciplinar da Aeronáutica (RDAER), sem prejuízo da imediata instauração de Inquérito "
        "Policial-Militar caso a conduta configure crime militar (como falsidade ideológica).")

        # lista de postos (fora do form para permitir rerun imediato / uso de session_state)
        postos_graduacoes = [
            'Soldado de 2° Classe', 'Soldado de 1° Classe', 'Cabo',
            '3º Sargento', '2º Sargento', '1º Sargento', 'Suboficial',
            'Aspirante', '2º Tenente', '1º Tenente', 'Capitão', 'Major',
            'Tenente-Coronel', 'Coronel', 'Brigadeiro do Ar',
            'Major-Brigadeiro do Ar', 'Tenente-Brigadeiro do Ar'
        ]

        # aplica reset solicitado ANTES de instanciar o widget
        if st.session_state.get("reset_posto_graduacao"):
            st.session_state["posto_graduacao"] = None  # ou False, se preferir
            del st.session_state["reset_posto_graduacao"]

        if "posto_graduacao" not in st.session_state:
            st.session_state["posto_graduacao"] = postos_graduacoes[0]

        # selectbox fora do form (grava em session_state e causa rerun)
        posto_graduacao_cadastro = st.selectbox("Posto/Graduação", postos_graduacoes, key="posto_graduacao")

        # form de cadastro — lê o posto atual de session_state para definir funções
        with st.form("form_cadastro",
                    clear_on_submit=True,
                    enter_to_submit=False
                    ):

            columns = st.columns(2)
            with columns[0]:
                username_cadastro = st.text_input("Nome Completo", placeholder="Digite seu nome completo")
                password_cadastro = st.text_input("Senha", type="password", placeholder="Digite sua senha")
                saram_cadastro = st.text_input("SARAM", placeholder="Digite seu SARAM, sem espaços ou traços")
            with columns[1]:
                email_cadastro = st.text_input("Email", placeholder="Digite seu email")
                confirm_password_cadastro = st.text_input("Confirmar Senha", type="password", placeholder="Confirme sua senha")
                confirm_saram_cadastro = st.text_input("Confirmar SARAM", placeholder="Confirme seu SARAM, sem espaços ou traços")

            # pega o posto atual da session_state (atualizado pelo selectbox) para definir as opções de função
            posto_atual = st.session_state.get("posto_graduacao", posto_graduacao_cadastro)

            # condição para o campo de função, baseado no posto selecionado
            if posto_atual in ['Soldado de 2° Classe', 'Soldado de 1° Classe', 'Cabo']:
                funcoes = ['Auxiliar']
            elif posto_atual in ['3º Sargento', '2º Sargento', '1º Sargento', 'Suboficial']:
                funcoes = ['Técnico', 'Encarregado']
            elif posto_atual in ['Aspirante', '2º Tenente', '1º Tenente', 'Capitão', 'Major', 'Tenente-Coronel', 'Coronel']:
                funcoes = ['Chefia', 'Comando', 'Direção', 'Outra']
            else:  # para postos mais altos como Brigadeiros
                funcoes = ['Comandante de Organização Militar']
            funcao_cadastro = st.selectbox("Função", funcoes)

            # condição para seção, baseado no posto selecionado
            lista_secao = ['Climatização', 'Elétrica', 'Hidráulica', 'Pintura', 'Serralheria', 'Marcenaria', 'Obras', 'Engenharia']

            # aplicado à chefias
            if posto_atual in ['Aspirante','2º Tenente', '1º Tenente', 'Capitão', 'Major', 'Tenente-Coronel', 'Coronel']:
                lista_secao = ['Chefia da SSG', 'Direção do EIE', 'Comando do EIE']
                secao_cadastro = st.selectbox("Seção", lista_secao)
            

            else: # para demais postos, mantém a lista completa
                secao_cadastro = st.selectbox("Seção", lista_secao)

            #enviar cadastro
            submit_cadastro = st.form_submit_button("Cadastrar")
            if submit_cadastro:
                if validar_cadastro(name=username_cadastro, email=email_cadastro, password=password_cadastro, confirm_password=confirm_password_cadastro, saram=saram_cadastro, confirm_saram=confirm_saram_cadastro, funcao=funcao_cadastro, confirm_funcao=funcao_cadastro, posto_graduacao=posto_atual, secao=secao_cadastro):
                    st.success("Cadastro realizado com sucesso!")
                    st.session_state.dados_militar = {
                        "nome": username_cadastro,
                        "saram": saram_cadastro,
                        "email": email_cadastro,
                        "funcao": funcao_cadastro,
                        "posto_graduacao": posto_atual,
                        "secao": secao_cadastro
                    }
                    st.session_state.logado = True # Define o estado de logado como True após cadastro bem-sucedido
                    st.session_state["reset_posto_graduacao"] = True
                    st.switch_page('pages/inicio.py') # Redireciona para a página inicial após cadastro bem-sucedido

                else:
                    st.error("Ocorreu um erro no cadastro. Verifique os dados e tente novamente.")
                    st.session_state.clear() # Limpa o session_state para evitar dados inconsistentes após erro de cadastro
                    sleep(4) # Aguarda 4 segundos antes de reiniciar
                    st.rerun() # Rerun para resetar os campos e o estado da página após erro de cadastro


# =========================================================
# SE O USUÁRIO ESTIVER LOGADO, EXIBE A PÁGINA INICIAL (REDIRECIONA PARA OUTRA PÁGINA)
# =========================================================
if st.session_state.logado: # Se o usuário estiver logado, exibe a página inicial
    st.switch_page("pages/inicio.py")