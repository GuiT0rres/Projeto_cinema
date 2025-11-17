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
    """Deleta uma sala APENAS se não houver sessões agendadas nela"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        
        #1. VERIFICAR SESSÕES
        cursor.execute("SELECT COUNT(*) FROM sessao WHERE id_sala = %s", (id_sala,))
        qtd_sessoes = cursor.fetchone()[0]
        
        if qtd_sessoes > 0:
            print(f"❌ Não é possível deletar a Sala ID {id_sala}.")
            print(f"   Ela está sendo usada em {qtd_sessoes} sessão(ões).")
            return False
        
        #2. Deletar os assentos
        cursor.execute("DELETE FROM assento WHERE id_sala = %s", (id_sala,))
        print(f"ℹ️  Assentos da Sala ID {id_sala} removidos...")
        
        #3: Deletar a sala
        cursor.execute("DELETE FROM sala WHERE id_sala = %s", (id_sala,))
        
        con.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Sala ID {id_sala} e seus assentos foram removidos!")
            return True
        else:
            print(f"ℹ️ Sala ID {id_sala} não encontrada.")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao deletar sala: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()