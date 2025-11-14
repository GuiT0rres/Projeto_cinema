from config.db import criar_conexao

def inserir_diretor(nome, nacionalidade):
    """
    Cadastra um novo diretor ou reativa um inativo.
    Retorna o ID do diretor (novo ou reativado) em caso de sucesso.
    Retorna None em caso de falha ou cancelamento.
    """
    con = criar_conexao()
    if not con:
        return None 
    
    cursor = None
    try:
        cursor = con.cursor()
        
        cursor.execute(
            "SELECT id_diretor, ativo FROM diretor WHERE nome_diretor = %s", 
            (nome,)
        )
        resultado = cursor.fetchone()
        
        if resultado:
            id_diretor_existente, diretor_esta_ativo = resultado[0], resultado[1]
            
            if not diretor_esta_ativo:
                print(f"ℹ️  Diretor '{nome}' está inativo.")
                reativar = input("   Deseja reativar? (s/n): ")
                
                if reativar.lower() == 's':
                    cursor.execute(
                        "UPDATE diretor SET ativo = TRUE, nacionalidade = %s WHERE id_diretor = %s",
                        (nacionalidade, id_diretor_existente)
                    )
                    con.commit()
                    print(f"✅ Diretor reativado e atualizado (ID: {id_diretor_existente})!")
                    return id_diretor_existente
                else:
                    print("❌ Operação cancelada!")
                    return None
            else:
                print("❌ Diretor com esse nome já está cadastrado!")
                return None
        
        sql = """
            INSERT INTO diretor (nome_diretor, nacionalidade, ativo)
            VALUES (%s, %s, TRUE)
            RETURNING id_diretor
        """
        cursor.execute(sql, (nome, nacionalidade))
        diretor_id = cursor.fetchone()[0]
        con.commit()
        print(f"✅ Diretor '{nome}' cadastrado com ID {diretor_id}!")
        return diretor_id
        
    except Exception as e:
        print(f"❌ Erro ao inserir diretor: {e}")
        if con:
            con.rollback()
        return None
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()
            
def listar_diretores(incluir_inativos=False):
    """
    Lista todos os diretores cadastrados
    
    Args:
        incluir_inativos: Se True, lista também diretores desativados
    """
    con = criar_conexao()
    if not con:
        return []
    
    try:
        cursor = con.cursor()
        
        if not incluir_inativos:
            cursor.execute("SELECT * FROM diretor WHERE ativo = TRUE ORDER BY id_diretor")
        else:
            cursor.execute("SELECT * FROM diretor ORDER BY id_diretor")
        
        diretores = cursor.fetchall()
        return diretores
    except Exception as e:
        print(f"❌ Erro ao listar diretores: {e}")
        return []
    finally:
        cursor.close()
        con.close()


def buscar_diretor(id_diretor):
    """Busca um diretor específico por ID"""
    con = criar_conexao()
    if not con:
        return None
    
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM diretor WHERE id_diretor = %s", (id_diretor,))
        diretor = cursor.fetchone()
        return diretor
    except Exception as e:
        print(f"❌ Erro ao buscar diretor: {e}")
        return None
    finally:
        cursor.close()
        con.close()


def atualizar_diretor(id_diretor, nome=None, nacionalidade=None):
    """Atualiza dados de um diretor"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        updates = []
        params = []
        
        if nome:
            updates.append("nome_diretor = %s")
            params.append(nome)
        if nacionalidade:
            updates.append("nacionalidade = %s")
            params.append(nacionalidade)
        
        if updates:
            params.append(id_diretor)
            sql = f"UPDATE diretor SET {', '.join(updates)} WHERE id_diretor = %s"
            cursor.execute(sql, params)
            con.commit()
            print(f"✅ Diretor ID {id_diretor} atualizado!")
            return True
        else:
            print("⚠️ Nenhum dado para atualizar!")
            return False
    except Exception as e:
        print(f"❌ Erro ao atualizar diretor: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def deletar_diretor(id_diretor, forcar=False):
    """
    Remove um diretor
    
    Args:
        id_diretor: ID do diretor a ser removido
        forcar: Se True, remove os vínculos com filmes antes de deletar
               Se False, apenas verifica e impede a exclusão
    """
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM filme_diretor WHERE id_diretor = %s", 
            (id_diretor,)
        )
        qtd_filmes = cursor.fetchone()[0]
        
        if qtd_filmes > 0:
            if forcar:
                print(f"⚠️  Diretor possui {qtd_filmes} filme(s) vinculado(s).")
                confirmacao = input("   Deseja remover os vínculos e deletar? (s/n): ")
                
                if confirmacao.lower() == 's':
                    cursor.execute("DELETE FROM filme_diretor WHERE id_diretor = %s", (id_diretor,))
                    print(f"   ✅ {qtd_filmes} vínculo(s) removido(s)")
                else:
                    print("   ❌ Operação cancelada!")
                    return False
            else:
                print(f"❌ Não é possível deletar!")
                print(f"   Diretor possui {qtd_filmes} filme(s) vinculado(s).")
                print(f"   Use deletar_diretor(id, forcar=True) para forçar a exclusão.")
                print(f"   Ou use desativar_diretor(id) para soft delete.")
                return False
        
        cursor.execute("DELETE FROM diretor WHERE id_diretor = %s", (id_diretor,))
        con.commit()
        print(f"✅ Diretor ID {id_diretor} removido!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao deletar diretor: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def desativar_diretor(id_diretor):
    """
    Soft Delete - Marca o diretor como inativo ao invés de deletar
    """
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        
        cursor.execute("UPDATE diretor SET ativo = FALSE WHERE id_diretor = %s", (id_diretor,))
        con.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Diretor ID {id_diretor} desativado!")
            return True
        else:
            print(f"ℹ️ Diretor ID {id_diretor} não encontrado.")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao desativar diretor: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def reativar_diretor(id_diretor):
    """Reativa um diretor desativado"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        cursor.execute("UPDATE diretor SET ativo = TRUE WHERE id_diretor = %s", (id_diretor,))
        con.commit()

        if cursor.rowcount > 0:
            print(f"✅ Diretor ID {id_diretor} reativado!")
            return True
        else:
            print(f"ℹ️ Diretor ID {id_diretor} não encontrado.")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao reativar diretor: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def listar_diretores_com_filmes():
    """Lista diretores ATIVOS e quantos filmes cada um dirigiu"""
    con = criar_conexao()
    if not con:
        return []
    
    try:
        cursor = con.cursor()
        sql = """
            SELECT 
                d.id_diretor,
                d.nome_diretor,
                d.nacionalidade,
                d.ativo,
                COUNT(fd.id_filme) as total_filmes
            FROM diretor d
            LEFT JOIN filme_diretor fd ON d.id_diretor = fd.id_diretor
            WHERE d.ativo = TRUE
            GROUP BY d.id_diretor, d.nome_diretor, d.nacionalidade, d.ativo
            ORDER BY total_filmes DESC
        """
        cursor.execute(sql)
        diretores = cursor.fetchall()
        return diretores
    except Exception as e:
        print(f"❌ Erro ao listar diretores com filmes: {e}")
        return []
    finally:
        cursor.close()
        con.close()