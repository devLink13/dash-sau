# =================================================
# funções de acesso e manipulação do banco de dados
# =================================================

# importações necessárias
from datetime import datetime, timedelta, timezone

# função para inserir um novo usuário no sistema
def insert_new_user(supabase_client, table_name, user_data):
    '''
    Insere um novo usuário na tabela especificada do Supabase.
    user_data deve ser um dicionário contendo os campos necessários para a tabela, por exemplo:
    {
        "username": "johndoe",
        "email": "johndoe@example.com"
    }
    '''
    try:
        response = supabase_client.table(table_name).insert(user_data).execute().data
        return response[0] # retorna os dados do usuário inserido (primeiro item da lista de dados retornada pela resposta do Supabase)
    except:
        return False
    
# função para verificar a ultima data de atualização de uma tabela
def check_data_freshness(supabase_client, table_name, days = 1):
    '''
    Verifica a última data de atualização de uma tabela no Supabase e compara com a data atual.
    Se a diferença for maior que o número de dias especificado, retorna False e a data da última atualização. Caso contrário, retorna True e a data da última atualização.
    '''
    try:
        # buscar o registro mais recente baseado na data de inserção
        response = supabase_client.table(table_name).select("created_at").order("created_at", desc=True).limit(1).execute()

        if not response.data:
            return False, "Nenhum dado encontrado na tabela."
        
        last_update = datetime.fromisoformat(response.data[0]['created_at'].replace("Z", "+00:00")) # converter a string de data para um objeto datetime

        if datetime.now(timezone.utc) - last_update > timedelta(days=days):
            return False, last_update
        
        return True, last_update
    
    except Exception as e:
        return False, str(e)