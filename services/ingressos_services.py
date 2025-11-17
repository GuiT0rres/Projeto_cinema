from config.db import criar_conexao

def inserir_ingresso(preco, tipo_ingresso, id_assento, id_sessao, nome_cliente, cpf_cliente, email_cliente):
    """Cadastra um novo ingresso (cria o cliente se não existir, impede venda a inativos)"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        
        # 1. Verificar se o assento já está ocupado nessa sessão
        cursor.execute("""
            SELECT id_ingresso FROM ingressos 
            WHERE id_assento = %s AND id_sessao = %s
        """, (id_assento, id_sessao))
        
        if cursor.fetchone():
            print("❌ Esse assento já está ocupado nesta sessão!")
            return False
        
        
        # 2. Verificar se o cliente já existe pelo CPF
        cursor.execute("SELECT id_cliente, ativo FROM clientes WHERE CPF = %s", (cpf_cliente,))
        resultado = cursor.fetchone()
        
        id_cliente = None
        if resultado:
            id_cliente_existente, cliente_esta_ativo = resultado[0], resultado[1]
            
            # 3. BLOQUEAR se o cliente estiver inativo
            if not cliente_esta_ativo:
                print(f"❌ ERRO: O cliente (CPF: {cpf_cliente}) está INATIVO e não pode comprar ingressos.")
                print("   Peça para o cliente ser reativado no menu principal.")
                return False
            
            id_cliente = id_cliente_existente
            print(f"ℹ️ Cliente já cadastrado (ID: {id_cliente})")
            
        else:
            # 4. Criar novo cliente (se não foi encontrado)
            cursor.execute("""
                INSERT INTO clientes (CPF, nome, email, ativo)
                VALUES (%s, %s, %s, TRUE)
                RETURNING id_cliente
            """, (cpf_cliente, nome_cliente, email_cliente))
            id_cliente = cursor.fetchone()[0]
            print(f"✅ Cliente '{nome_cliente}' cadastrado com ID {id_cliente}!")
        
        # 5. Inserir o ingresso
        sql = """
            INSERT INTO ingressos (preco, tipo_ingresso, id_assento, id_sessao, id_cliente)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_ingresso
        """
        cursor.execute(sql, (preco, tipo_ingresso, id_assento, id_sessao, id_cliente))
        ingresso_id = cursor.fetchone()[0]
        con.commit()
        print(f"🎟️ Ingresso cadastrado com ID {ingresso_id}!")
        return True

    except Exception as e:
        print(f"❌ Erro ao inserir ingresso: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

def listar_ingressos():
    """Lista todos os ingressos cadastrados"""
    con = criar_conexao()
    if not con:
        return []
    
    cursor = None
    try:
        cursor = con.cursor()
        sql = """
            SELECT 
                i.id_ingresso,
                i.preco,
                i.tipo_ingresso,
                a.numero_assento,
                s.data,
                s.horario,
                f.titulo,
                c.nome
            FROM ingressos i
            INNER JOIN assento a ON i.id_assento = a.id_assento
            INNER JOIN sessao s ON i.id_sessao = s.id_sessao
            INNER JOIN filme f ON s.id_filme = f.id_filme
            INNER JOIN clientes c ON i.id_cliente = c.id_cliente
            ORDER BY i.id_ingresso
        """
        #Inner join assento diz qual o número do assento
        #Inner join sessão diz qual o horário e data da sessão do ingresso
        #Inner join filme pega o filme que está vinculado a sessão
        #Inner join clientes pega o cliente vinculado ao ingresso

        cursor.execute(sql)
        ingressos = cursor.fetchall()
        return ingressos
    except Exception as e:
        print(f"❌ Erro ao listar ingressos: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def listar_assentos_disponiveis(id_sessao):
    """Lista assentos disponíveis para uma sessão específica (com ordem correta)"""
    con = criar_conexao()
    if not con:
        return []
    
    cursor = None
    try:
        cursor = con.cursor()
        
        cursor.execute("SELECT id_sala FROM sessao WHERE id_sessao = %s", (id_sessao,))
        resultado = cursor.fetchone()
        
        if not resultado:
            print("❌ Sessão não encontrada!")
            return []
        
        id_sala = resultado[0]
        
        sql = """
            SELECT a.id_assento, a.numero_assento
            FROM assento a
            WHERE a.id_sala = %s
              AND a.id_assento NOT IN (
                  SELECT id_assento 
                  FROM ingressos 
                  WHERE id_sessao = %s
              )
            -- Ordena pelo comprimento e depois pelo nome (A2 antes de A10)
            ORDER BY LENGTH(a.numero_assento), a.numero_assento
        """
        cursor.execute(sql, (id_sala, id_sessao))
        assentos = cursor.fetchall()
        return assentos
    except Exception as e:
        print(f"❌ Erro ao listar assentos disponíveis: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def listar_assentos_ocupados(id_sessao):
    """Lista assentos ocupados em uma sessão específica"""
    con = criar_conexao()
    if not con:
        return []
    
    cursor = None
    try:
        cursor = con.cursor()
        sql = """
            SELECT 
                a.numero_assento,
                c.nome,
                i.tipo_ingresso,
                i.preco
            FROM ingressos i
            INNER JOIN assento a ON i.id_assento = a.id_assento
            INNER JOIN clientes c ON i.id_cliente = c.id_cliente
            WHERE i.id_sessao = %s
            ORDER BY a.numero_assento
        """
        #INNER JOIN assento: Pega o código visual do assento (ex: A5) para mostrar no mapa.
        #INNER JOIN clientes: Descobre o nome da pessoa que ocupou aquele lugar.
        #WHERE: Filtra apenas os ingressos vendidos para ESTA sessão específica.

        cursor.execute(sql, (id_sessao,))
        assentos = cursor.fetchall()
        return assentos
    except Exception as e:
        print(f"❌ Erro ao listar assentos ocupados: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def buscar_ingresso(id_ingresso):
    """Busca um ingresso específico"""
    con = criar_conexao()
    if not con:
        return None
    
    cursor = None
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM ingressos WHERE id_ingresso = %s", (id_ingresso,))
        ingresso = cursor.fetchone()
        return ingresso
    except Exception as e:
        print(f"❌ Erro ao buscar ingresso: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def listar_ingressos_por_cliente(id_cliente):
    """Lista todos os ingressos de um cliente específico"""
    con = criar_conexao()
    if not con:
        return []
    
    cursor = None
    try:
        cursor = con.cursor()
        sql = """
            SELECT 
                i.id_ingresso,
                f.titulo,
                s.data,
                s.horario,
                a.numero_assento,
                i.tipo_ingresso,
                i.preco
            FROM ingressos i
            INNER JOIN assento a ON i.id_assento = a.id_assento
            INNER JOIN sessao s ON i.id_sessao = s.id_sessao
            INNER JOIN filme f ON s.id_filme = f.id_filme
            WHERE i.id_cliente = %s
            ORDER BY s.data, s.horario
        """
        # Inner join assento: Mostra o número da cadeira comprada.
        # Inner join sessão: Busca a data e hora da sessão.
        # Inner join filme: Busca o nome do filme (conectado através da sessão).
        # WHERE: Traz apenas o histórico desse cliente específico.

        cursor.execute(sql, (id_cliente,))
        ingressos = cursor.fetchall()
        return ingressos
    except Exception as e:
        print(f"❌ Erro ao listar ingressos do cliente: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def listar_ingressos_por_sessao(id_sessao):
    """Lista todos os ingressos de uma sessão específica"""
    con = criar_conexao()
    if not con:
        return []
    
    cursor = None
    try:
        cursor = con.cursor()
        sql = """
            SELECT 
                i.id_ingresso,
                c.nome,
                a.numero_assento,
                i.tipo_ingresso,
                i.preco
            FROM ingressos i
            INNER JOIN clientes c ON i.id_cliente = c.id_cliente
            INNER JOIN assento a ON i.id_assento = a.id_assento
            WHERE i.id_sessao = %s
            ORDER BY a.numero_assento
        """
        # Inner join clientes: Descobre o nome de quem comprou o ingresso.
        # Inner join assento: Identifica qual cadeira foi reservada (ex: B5).
        # WHERE: Filtra a lista para mostrar apenas as vendas DESTA sessão específica.
        cursor.execute(sql, (id_sessao,))
        ingressos = cursor.fetchall()
        return ingressos
    except Exception as e:
        print(f"❌ Erro ao listar ingressos da sessão: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def deletar_ingresso(id_ingresso):
    """Remove um ingresso (libera o assento)"""
    con = criar_conexao()
    if not con:
        return False
    
    cursor = None
    try:
        cursor = con.cursor()
        cursor.execute("DELETE FROM ingressos WHERE id_ingresso = %s", (id_ingresso,))
        con.commit()
        
        if cursor.rowcount > 0:
            print(f"✅ Ingresso ID {id_ingresso} removido!")
            return True
        else:
            print(f"ℹ️ Ingresso ID {id_ingresso} não encontrado.")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao deletar ingresso: {e}")
        if con:
            con.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def verificar_disponibilidade_sessao(id_sessao):
    """Verifica quantos assentos estão disponíveis em uma sessão"""
    con = criar_conexao()
    if not con:
        return None
    
    cursor = None
    try:
        cursor = con.cursor()
        sql = """
            SELECT 
                sa.capacidade,
                COUNT(i.id_ingresso) as vendidos,
                (sa.capacidade - COUNT(i.id_ingresso)) as disponiveis
            FROM sessao s
            INNER JOIN sala sa ON s.id_sala = sa.id_sala
            LEFT JOIN ingressos i ON s.id_sessao = i.id_sessao
            WHERE s.id_sessao = %s
            GROUP BY sa.capacidade
        """
        # (sa.capacidade - COUNT(i.id_ingresso)) as disponiveis Cálculo SQL: (Capacidade - Contagem) = Assentos Disponíveis.
        # INNER JOIN sala: Busca a capacidade total da sala (dado obrigatório).
        # LEFT JOIN ingressos: Busca os ingressos vendidos (pode ser zero).
        
        cursor.execute(sql, (id_sessao,))
        resultado = cursor.fetchone()
        
        if not resultado:
             cursor.execute("""
                SELECT sa.capacidade, 0 as vendidos, sa.capacidade as disponiveis
                FROM sessao s
                INNER JOIN sala sa ON s.id_sala = sa.id_sala
                WHERE s.id_sessao = %s
             """, (id_sessao,))
             # IF NOT RESULTADO: Se a busca falhar, assume que a sessão é nova (0 vendas).
             resultado = cursor.fetchone()

        return resultado
    except Exception as e:
        print(f"❌ Erro ao verificar disponibilidade: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()