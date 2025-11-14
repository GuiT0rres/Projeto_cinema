from config.db import criar_conexao

def inserir_filme(titulo, genero, ano, classificacao, duracao):
    """Cadastra um novo filme"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        sql = """
            INSERT INTO filme (titulo, genero, ano, classificacao, duracao)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_filme
        """
        cursor.execute(sql, (titulo, genero, ano, classificacao, duracao))
        filme_id = cursor.fetchone()[0]
        con.commit()
        print(f"✅ Filme '{titulo}' cadastrado com ID {filme_id}!")
        return True
    except Exception as e:
        print(f"❌ Erro ao inserir filme: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def listar_filmes():
    """Lista todos os filmes cadastrados e seus diretores"""
    con = criar_conexao()
    if not con:
        return []
    
    try:
        cursor = con.cursor()
        # SQL une as 3 tabelas e agrupa os diretores em uma string
        sql = """
            SELECT 
                f.id_filme, 
                f.titulo, 
                f.genero, 
                f.ano, 
                f.classificacao, 
                f.duracao,
                STRING_AGG(d.nome_diretor, ', ') AS diretores
            FROM filme f
            LEFT JOIN filme_diretor fd ON f.id_filme = fd.id_filme
            LEFT JOIN diretor d ON fd.id_diretor = d.id_diretor
            GROUP BY f.id_filme
            ORDER BY f.id_filme
        """
        cursor.execute(sql)
        filmes = cursor.fetchall()
        return filmes
    except Exception as e:
        print(f"❌ Erro ao listar filmes: {e}")
        return []
    finally:
        cursor.close()
        con.close()


def atualizar_filme(id_filme, titulo=None, genero=None, ano=None, classificacao=None, duracao=None):
    """Atualiza dados de um filme"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        updates = []
        params = []
        
        if titulo:
            updates.append("titulo = %s")
            params.append(titulo)
        if genero:
            updates.append("genero = %s")
            params.append(genero)
        if ano:
            updates.append("ano = %s")
            params.append(ano)
        if classificacao:
            updates.append("classificacao = %s")
            params.append(classificacao)
        if duracao:
            updates.append("duracao = %s")
            params.append(duracao)
        
        if updates:
            params.append(id_filme)
            sql = f"UPDATE filme SET {', '.join(updates)} WHERE id_filme = %s"
            cursor.execute(sql, params)
            con.commit()
            print(f"✅ Filme ID {id_filme} atualizado!")
            return True
        else:
            print("⚠️ Nenhum dado para atualizar!")
            return False
    except Exception as e:
        print(f"❌ Erro ao atualizar filme: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def deletar_filme(id_filme):
    """Remove um filme, APENAS se não estiver vinculado a sessões ou diretores"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        
        # 1. Verificar se está vinculado a uma sessão
        cursor.execute("SELECT COUNT(*) FROM sessao WHERE id_filme = %s", (id_filme,))
        qtd_sessoes = cursor.fetchone()[0]
        if qtd_sessoes > 0:
            print(f"❌ Não é possível deletar! Filme está em {qtd_sessoes} sessão(ões).")
            return False
            
        # 2. Verificar se está vinculado a um diretor
        cursor.execute("SELECT COUNT(*) FROM filme_diretor WHERE id_filme = %s", (id_filme,))
        qtd_diretores = cursor.fetchone()[0]
        if qtd_diretores > 0:
            print(f"❌ Não é possível deletar! Filme está vinculado a {qtd_diretores} diretor(es).")
            return False

        # 3. Se passou em ambos, pode deletar
        cursor.execute("DELETE FROM filme WHERE id_filme = %s", (id_filme,))
        con.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Filme ID {id_filme} removido!")
            return True
        else:
            print(f"ℹ️ Filme ID {id_filme} não encontrado.")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao deletar filme: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def vincular_filme_diretor(id_filme, id_diretor):
    """Vincula um diretor a um filme na tabela filme_diretor"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        sql = "INSERT INTO filme_diretor (id_filme, id_diretor) VALUES (%s, %s)"
        cursor.execute(sql, (id_filme, id_diretor))
        con.commit()
        print("✅ Diretor vinculado ao filme com sucesso!")
        return True
    except Exception as e:
        # Pega a violação de chave única (filme/diretor já vinculado)
        if "unique_violation" in str(e): 
             print("❌ Erro: Esse diretor já está vinculado a esse filme.")
        else:
             print(f"❌ Erro ao vincular diretor: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()