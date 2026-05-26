# =================================================
# funções de acesso e manipulação do banco de dados
# =================================================

# função para inserir um novo usuário no sistema
def insert_new_user(supabase_client, table_name, user_data):
    try:
        response = supabase_client.table(table_name).insert(user_data).execute().data
        return response[0] # retorna os dados do usuário inserido (primeiro item da lista de dados retornada pela resposta do Supabase)
    except:
        return False