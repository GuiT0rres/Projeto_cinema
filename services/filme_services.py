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
        #String_AGG Junta todos os diretores do mesmo filme em uma única linha
        #Left join pega o filme, vê se tem vínculo na tabela filme_diretor 
        #e então vai na tabela diretor pegar o nome do diretor

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
    """Deleta um filme, seus vínculos (diretores/sessões) e ingressos relacionados."""
    con = criar_conexao()
    if not con:
        return False

    cursor = None
    try:
        cursor = con.cursor()

        # Encontra as sessões ligadas ao filme para deletar os ingressos primeiro
        cursor.execute("SELECT id_sessao FROM sessao WHERE id_filme = %s", (id_filme,))
        sessoes_ids = [row[0] for row in cursor.fetchall()]

        if sessoes_ids:
            # Constrói placeholders (%s) dinamicamente para a lista de IDs
            sessoes_placeholders = ', '.join(['%s'] * len(sessoes_ids))
            
            # 1. Deletar INGRESSOS que dependem dessas sessões
            cursor.execute(f"DELETE FROM ingressos WHERE id_sessao IN ({sessoes_placeholders})", sessoes_ids)
            print(f"ℹ️ {cursor.rowcount} ingresso(s) cancelado(s) devido à exclusão do filme.")

        # 2. Deletar vínculos de diretores (filme_diretor)
        cursor.execute("DELETE FROM filme_diretor WHERE id_filme = %s", (id_filme,))
        print(f"ℹ️ {cursor.rowcount} vínculo(s) de diretor removido(s).")
        
        # 3. Deletar as sessões
        cursor.execute("DELETE FROM sessao WHERE id_filme = %s", (id_filme,))
        print(f"ℹ️ {cursor.rowcount} sessão(ões) dependente(s) removida(s).")
        
        # 4. Deletar o filme
        cursor.execute("DELETE FROM filme WHERE id_filme = %s", (id_filme,))
        
        if cursor.rowcount > 0:
            con.commit()
            print(f"✅ Filme ID {id_filme} deletado permanentemente.")
            return True
        else:
            print(f"❌ Filme ID {id_filme} não encontrado.")
            return False

    except Exception as e:
        print(f"❌ Erro ao deletar filme: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if con: con.close()


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