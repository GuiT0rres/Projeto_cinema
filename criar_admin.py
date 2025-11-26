import bcrypt
from config.db import criar_conexao

def cadastrar_admin_inicial():
    con = criar_conexao()
    if not con:
        return

    login = "admin"
    senha_plana = "admin"
    nome = "Administrador Supremo"

    # 1. Gerar o Hash
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha_plana.encode('utf-8'), salt)
    
    # Converte de bytes para string para salvar no banco
    senha_hash_str = senha_hash.decode('utf-8')

    try:
        cursor = con.cursor()
        
        # Limpa usuários antigos para não dar erro de duplicidade
        cursor.execute("DELETE FROM Usuarios WHERE login = %s", (login,))
        
        # Insere o novo com a senha criptografada
        sql = "INSERT INTO Usuarios (login, senha, nome) VALUES (%s, %s, %s)"
        cursor.execute(sql, (login, senha_hash_str, nome))
        
        con.commit()
        print("✅ Usuário ADMIN recriado com senha HASH com sucesso!")
        print(f"🔑 Login: {login}")
        print(f"🔑 Senha: {senha_plana}")
        print(f"🔒 Hash salvo no banco: {senha_hash_str}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    cadastrar_admin_inicial()