from config.db import criar_conexao

def inserir_sala(numero, capacidade, tipo):
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        
        #1. Inserir a Sala
        sql_sala = """
            INSERT INTO sala (numero_sala, capacidade, tipo_sala)
            VALUES (%s, %s, %s)
            RETURNING id_sala
        """
        cursor.execute(sql_sala, (numero, capacidade, tipo))
        sala_id = cursor.fetchone()[0]
        print(f"✅ Sala {numero} cadastrada com ID {sala_id}! Populando assentos...")

        #2. Popular os Assentos
        assentos_para_criar = []
        for i in range(1, capacidade + 1):
            numero_assento = f"A{i}" 
            assentos_para_criar.append((numero_assento, sala_id))

        sql_assentos = "INSERT INTO assento (numero_assento, id_sala) VALUES (%s, %s)"
        cursor.executemany(sql_assentos, assentos_para_criar)
        
        #3. Commit da Transação
        con.commit() # Salva a sala E os assentos juntos
        
        print(f"✅ {len(assentos_para_criar)} assentos criados para a Sala {numero}.")
        return True
    
    except Exception as e:
        print(f"❌ Erro ao inserir sala e assentos: {e}")
        if con:
            con.rollback()
        return False
    
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def listar_salas():
    con = criar_conexao()
    if not con:
        return []
    
    cursor = None
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM sala ORDER BY id_sala")
        salas = cursor.fetchall()
        return salas
    except Exception as e:
        print(f"❌ Erro ao listar salas: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def deletar_sala(id_sala):
    """Deleta uma sala, removendo assentos vinculados e verificando se há sessões ativas nela."""
    con = criar_conexao()
    if not con:
        return False

    cursor = None
    try:
        cursor = con.cursor()
        
        # 1. VERIFICAÇÃO PRINCIPAL: Checa se há SESSÕES vinculadas (Prioridade máxima de bloqueio)
        cursor.execute("SELECT COUNT(*) FROM sessao WHERE id_sala = %s", (id_sala,))
        qtd_sessoes = cursor.fetchone()[0]
        
        if qtd_sessoes > 0:
            print(f"❌ Sala ID {id_sala} não pode ser deletada. Possui {qtd_sessoes} sessão(ões) vinculada(s).")
            print("   Deletar as sessões primeiro para liberar a sala.")
            return False
            
        # 2. CASCADE MANUAL: Deletar ASSENTOS vinculados (Resolve a Foreign Key de 'assento')
        cursor.execute("DELETE FROM assento WHERE id_sala = %s", (id_sala,))
        print(f"ℹ️ {cursor.rowcount} assento(s) removido(s) da sala.")

        # 3. Deletar a sala
        cursor.execute("DELETE FROM sala WHERE id_sala = %s", (id_sala,))
        
        if cursor.rowcount > 0:
            con.commit()
            print(f"✅ Sala ID {id_sala} deletada permanentemente.")
            return True
        else:
            print(f"❌ Sala ID {id_sala} não encontrada.")
            return False

    except Exception as e:
        print(f"❌ Erro ao deletar sala: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor: cursor.close()
        if con: con.close()