from config.db import criar_conexao

def inserir_cliente(nome, cpf, email):
    """Cadastra um novo cliente ou reativa um inativo"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        
        cursor.execute("SELECT id_cliente, ativo FROM clientes WHERE CPF = %s", (cpf,))
        resultado = cursor.fetchone()
        
        if resultado:
            id_cliente_existente, cliente_esta_ativo = resultado[0], resultado[1]
            
            if not cliente_esta_ativo:
                print(f"ℹ️  Cliente com CPF {cpf} está inativo.")
                reativar = input("   Deseja reativar? (s/n): ")
                
                if reativar.lower() == 's':
                    cursor.execute(
                        "UPDATE clientes SET ativo = TRUE, nome = %s, email = %s WHERE id_cliente = %s",
                        (nome, email, id_cliente_existente)
                    )
                    con.commit()
                    print(f"✅ Cliente reativado e atualizado (ID: {id_cliente_existente})!")
                    return True
                else:
                    print("❌ Operação cancelada!")
                    return False
            else:
                print("❌ CPF já cadastrado!")
                return False
        
        sql = """
            INSERT INTO clientes (CPF, nome, email, ativo)
            VALUES (%s, %s, %s, TRUE)
            RETURNING id_cliente
        """
        cursor.execute(sql, (cpf, nome, email))
        cliente_id = cursor.fetchone()[0]
        con.commit()
        print(f"✅ Cliente '{nome}' cadastrado com ID {cliente_id}!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir cliente: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def listar_clientes(incluir_inativos=False):
    """
    Lista todos os clientes cadastrados
    
    Args:
        incluir_inativos: Se True, lista também clientes desativados
    """
    con = criar_conexao()
    if not con:
        return []
    
    try:
        cursor = con.cursor()
        
        if not incluir_inativos:
            cursor.execute("SELECT * FROM clientes WHERE ativo = TRUE ORDER BY id_cliente")
        else:
            cursor.execute("SELECT * FROM clientes ORDER BY id_cliente")
        
        clientes = cursor.fetchall()
        return clientes
    except Exception as e:
        print(f"❌ Erro ao listar clientes: {e}")
        return []
    finally:
        cursor.close()
        con.close()


def buscar_cliente(id_cliente):
    """Busca um cliente específico por ID"""
    con = criar_conexao()
    if not con:
        return None
    
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id_cliente = %s", (id_cliente,))
        cliente = cursor.fetchone()
        return cliente
    except Exception as e:
        print(f"❌ Erro ao buscar cliente: {e}")
        return None
    finally:
        cursor.close()
        con.close()


def buscar_cliente_por_cpf(cpf):
    """Busca um cliente pelo CPF"""
    con = criar_conexao()
    if not con:
        return None
    
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM clientes WHERE CPF = %s", (cpf,))
        cliente = cursor.fetchone()
        return cliente
    except Exception as e:
        print(f"❌ Erro ao buscar cliente: {e}")
        return None
    finally:
        cursor.close()
        con.close()


def atualizar_cliente(id_cliente, nome=None, email=None):
    """Atualiza dados de um cliente (não atualiza CPF)"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        updates = []
        params = []
        
        if nome:
            updates.append("nome = %s")
            params.append(nome)
        if email:
            updates.append("email = %s")
            params.append(email)
        
        if updates:
            params.append(id_cliente)
            sql = f"UPDATE clientes SET {', '.join(updates)} WHERE id_cliente = %s"
            cursor.execute(sql, params)
            con.commit()
            print(f"✅ Cliente ID {id_cliente} atualizado!")
            return True
        else:
            print("⚠️ Nenhum dado para atualizar!")
            return False
    except Exception as e:
        print(f"❌ Erro ao atualizar cliente: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def deletar_cliente(id_cliente, forcar=False):
    """
    Remove um cliente
    
    Args:
        id_cliente: ID do cliente a ser removido
        forcar: Se True, remove os ingressos antes de deletar o cliente
               Se False, apenas verifica e impede a exclusão
    """
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM ingressos WHERE id_cliente = %s", 
            (id_cliente,)
        )
        qtd_ingressos = cursor.fetchone()[0]
        
        if qtd_ingressos > 0:
            if forcar:
                # Opção 1: Deletar ingressos em cascata
                print(f"⚠️  Cliente possui {qtd_ingressos} ingresso(s).")
                confirmacao = input("   Deseja deletar os ingressos também? (s/n): ")
                
                if confirmacao.lower() == 's':
                    cursor.execute("DELETE FROM ingressos WHERE id_cliente = %s", (id_cliente,))
                    print(f"   ✅ {qtd_ingressos} ingresso(s) deletado(s)")
                else:
                    print("   ❌ Operação cancelada!")
                    return False
            else:
                # Opção 2: Apenas avisar e impedir
                print(f"❌ Não é possível deletar!")
                print(f"   Cliente possui {qtd_ingressos} ingresso(s) vinculado(s).")
                print(f"   Use deletar_cliente(id, forcar=True) para forçar a exclusão.")
                return False
        
        cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
        con.commit()
        print(f"✅ Cliente ID {id_cliente} removido!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao deletar cliente: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def desativar_cliente(id_cliente):
    """
    Soft Delete - Marca o cliente como inativo ao invés de deletar
    """
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        
        cursor.execute("UPDATE clientes SET ativo = FALSE WHERE id_cliente = %s", (id_cliente,))
        con.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Cliente ID {id_cliente} desativado!")
            return True
        else:
            print(f"ℹ️ Cliente ID {id_cliente} não encontrado.")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao desativar cliente: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def reativar_cliente(id_cliente):
    """Reativa um cliente desativado"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        cursor.execute("UPDATE clientes SET ativo = TRUE WHERE id_cliente = %s", (id_cliente,))
        con.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Cliente ID {id_cliente} reativado!")
            return True
        else:
            print(f"ℹ️ Cliente ID {id_cliente} não encontrado.")
            return False
        
    except Exception as e:
        print(f"❌ Erro ao reativar cliente: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def listar_clientes_com_ingressos():
    """Lista clientes e quantos ingressos cada um comprou"""
    con = criar_conexao()
    if not con:
        return []
    
    try:
        cursor = con.cursor()
        sql = """
            SELECT 
                c.id_cliente,
                c.nome,
                c.CPF,
                c.email,
                c.ativo, 
                COUNT(i.id_ingresso) as total_ingressos
            FROM clientes c
            LEFT JOIN ingressos i ON c.id_cliente = i.id_cliente
            GROUP BY c.id_cliente, c.nome, c.CPF, c.email, c.ativo
            ORDER BY total_ingressos DESC
        """
        cursor.execute(sql)
        clientes = cursor.fetchall()
        return clientes
    except Exception as e:
        print(f"❌ Erro ao listar clientes com ingressos: {e}")
        return []
    finally:
        cursor.close()
        con.close()