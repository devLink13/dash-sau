# ====================================
# funções de segurança para os scripts
# ====================================

import hashlib

# função para hash de senha usando SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# função para validar o login do usuário, verificando o SARAM e a senha fornecidos
def validar_login(saram, password_hashed, supabase_client, table_name):
    # consultar o banco de dados para verificar se o SARAM existe e a senha corresponde
    try:
        if not saram or not password_hashed:
            return False
    
        query = supabase_client.table(table_name).select("*").eq("saram", saram).execute()
        if query.data and query.data[0]['senha_hash'] == password_hashed:
            dados_militar = query.data[0] # Armazena os dados do militar encontrado para uso posterior
            return dados_militar # Retorna os dados do militar encontrado (pode ser usado para outros propósitos, como exibir o nome do usuário na interface)

    except:
        return False

# função para validar o cadastro
def validar_cadastro(user_data):
    # extrair os dados do formulário
    name = user_data.get("name")
    email = user_data.get("email")
    password = user_data.get("password")
    confirm_password = user_data.get("confirm_password")
    saram = user_data.get("saram")
    confirm_saram = user_data.get("confirm_saram")
    funcao = user_data.get("funcao")
    confirm_funcao = user_data.get("confirm_funcao")
    posto_graduacao = user_data.get("posto_graduacao")
    secao = user_data.get("secao")
    nome_guerra = user_data.get("nome_guerra")

    ## vericações básicas de cadastro, como campos preenchidos e correspondência de senha/SARAM
    if not all([name, email, password, confirm_password, saram, confirm_saram, funcao, confirm_funcao, posto_graduacao, secao, nome_guerra]): # Verificação de campos vazios
        error = "Por favor, preencha todos os campos."
        return False, error
    if password != confirm_password: # Verificação de senha
        error = "As senhas não coincidem."
        return False, error
    if saram != confirm_saram: # Verificação de SARAM
        error = "Os SARAMs não coincidem."
        return False, error
    if len(saram) != 7 or not saram.isnumeric(): # 7440820
        error = "O SARAM deve conter exatamente 7 dígitos numéricos."
        return False, error
    
    
    else: # se passou nas validações
        dados_militar = {
            "nome": name,
            "saram": saram,
            "email": email,
            "senha_hash": hash_password(password=password), # Armazena a senha como hash para segurança
            "funcao": funcao,
            "posto": posto_graduacao,
            "secao": secao,
            "nome_guerra": nome_guerra
        }

        return True, dados_militar
    
