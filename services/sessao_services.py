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
            sa.numero_sala, 
            f.titulo,  
            s.id_filme
        FROM sessao s
        INNER JOIN filme f ON s.id_filme = f.id_filme
        INNER JOIN sala sa ON s.id_sala = sa.id_sala
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
    """Deleta uma sessão e todos os ingressos vendidos para ela."""
    con = criar_conexao()
    if not con:
        return False

    cursor = None
    try:
        cursor = con.cursor()

        # 1. Deletar ingressos dependentes (ingressos)
        cursor.execute("DELETE FROM ingressos WHERE id_sessao = %s", (id_sessao,))
        print(f"ℹ️ {cursor.rowcount} ingresso(s) cancelado(s).")
        
        # 2. Deletar a sessão
        cursor.execute("DELETE FROM sessao WHERE id_sessao = %s", (id_sessao,))
        
        if cursor.rowcount > 0:
            con.commit()
            print(f"✅ Sessão ID {id_sessao} deletada permanentemente.")
            return True
        else:
            print(f"❌ Sessão ID {id_sessao} não encontrada.")
            return False

    except Exception as e:
        print(f"❌ Erro ao deletar sessão: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if con: con.close()

def atualizar_sessao(id_sessao, data=None, horario=None, tipo_exibicao=None, id_filme=None, id_sala=None):
    """Atualiza dados de uma sessão."""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        updates = []
        params = []
        
        if data: updates.append("data = %s"); params.append(data)
        if horario: updates.append("horario = %s"); params.append(horario)
        if tipo_exibicao: updates.append("tipo_exibicao = %s"); params.append(tipo_exibicao)
        if id_filme: updates.append("id_filme = %s"); params.append(id_filme)
        if id_sala: updates.append("id_sala = %s"); params.append(id_sala)
        
        if updates:
            params.append(id_sessao)
            sql = f"UPDATE sessao SET {', '.join(updates)} WHERE id_sessao = %s"
            cursor.execute(sql, params)
            con.commit()
            print(f"✅ Sessão ID {id_sessao} atualizada!")
            return True
        else:
            print("⚠️ Nenhum dado para atualizar!")
            return False
    except Exception as e:
        print(f"❌ Erro ao atualizar sessão: {e}")
        if con: con.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if con: con.close()