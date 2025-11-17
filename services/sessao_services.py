from config.db import criar_conexao

def inserir_sessao(data, horario, tipo_exibicao, id_filme, id_sala):
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        sql = """
            INSERT INTO sessao (data, horario, tipo_exibicao, id_filme, id_sala)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_sessao
        """
        cursor.execute(sql, (data, horario, tipo_exibicao, id_filme, id_sala))
        sessao_id = cursor.fetchone()[0]
        con.commit()
        print(f"✅ Sessão cadastrada com ID {sessao_id}!")
        return True
    except Exception as e:
        print(f"❌ Erro ao inserir sessão: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def listar_sessoes():
    """Lista todas as sessões cadastradas, incluindo o nome do filme"""
    con = criar_conexao()
    if not con:
        return []
    
    cursor = None
    try:
        cursor = con.cursor()
        sql = """
            SELECT 
                s.id_sessao, 
                s.data, 
                s.horario, 
                s.tipo_exibicao, 
                s.id_sala, 
                f.titulo,  -- Coluna nova (índice 5)
                s.id_filme -- Coluna antiga (agora índice 6)
            FROM sessao s
            INNER JOIN filme f ON s.id_filme = f.id_filme
            ORDER BY s.data, s.horario
        """
        # Inner join filme: Busca o título do filme vinculado a esta sessão (traduz o ID_filme).
        # ORDER BY: Organiza a lista cronologicamente (data primeiro, depois horário).
        cursor.execute(sql)
        sessoes = cursor.fetchall()
        return sessoes
    except Exception as e:
        print(f"❌ Erro ao listar sessões: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def deletar_sessao(id_sessao):
    """Deleta uma sessão APENAS se não houver ingressos vendidos"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        
        check_sql = "SELECT COUNT(id_ingresso) FROM ingressos WHERE id_sessao = %s"
        cursor.execute(check_sql, (id_sessao,))
        contagem_ingressos = cursor.fetchone()[0]
        
        if contagem_ingressos > 0:
            print(f"❌ ERRO: Você não pode deletar a Sessão ID {id_sessao} porque ela já possui {contagem_ingressos} ingresso(s) vendido(s).")
            return False
            
        delete_sql = "DELETE FROM sessao WHERE id_sessao = %s"
        cursor.execute(delete_sql, (id_sessao,))
        con.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Sessão ID {id_sessao} removida!")
            return True
        else:
            print(f"ℹ️ Sessão ID {id_sessao} não encontrada.")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao deletar sessão: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()