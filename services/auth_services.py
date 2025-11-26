import bcrypt
from config.db import criar_conexao

def autenticar_funcionario(login, senha_digitada):
    """
    Verifica se o login existe e se a senha bate com o hash armazenado.
    """
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        # Busca o hash da senha armazenada para aquele login
        sql = "SELECT senha FROM Usuarios WHERE login = %s"
        cursor.execute(sql, (login,))
        resultado = cursor.fetchone()
        
        if resultado:
            senha_hash_banco = resultado[0] # Isso vem do banco como String
            
            if bcrypt.checkpw(senha_digitada.encode('utf-8'), senha_hash_banco.encode('utf-8')):
                return True
        
        return False # Usuário não encontrado ou senha inválida

    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if con: con.close()