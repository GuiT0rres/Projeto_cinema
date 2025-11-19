from datetime import datetime
from services.filme_services import (
    inserir_filme, 
    listar_filmes, 
    deletar_filme,
    vincular_filme_diretor
)
from services.diretor_services import (
    inserir_diretor, 
    listar_diretores, 
    deletar_diretor,
    desativar_diretor,
    reativar_diretor
)
from services.sala_services import (
    inserir_sala, 
    listar_salas, 
    deletar_sala
)
from services.sessao_services import (
    inserir_sessao, 
    listar_sessoes, 
    deletar_sessao
)
from services.ingressos_services import (
    inserir_ingresso, 
    listar_ingressos, 
    listar_assentos_disponiveis,
    listar_assentos_ocupados,
    verificar_disponibilidade_sessao,
    deletar_ingresso
)
from services.cliente_services import (
    listar_clientes, 
    inserir_cliente, 
    desativar_cliente,
    reativar_cliente,
    deletar_cliente,
    deletar_cliente_e_ingressos_forcado
)
import getpass

PRECO_INTEIRA = 0.0
PRECO_MEIA = 0.0

USUARIO_FUNCIONARIO = "admin"
SENHA_FUNCIONARIO = "admin"


# ========================================
# FUNÇÕES DE SUBMENU (FILMES)
# ========================================

def mostrar_menu_filmes():
    print("\n" + "--- 🎬 GERENCIAR FILMES ---")
    print("1. Adicionar Filme")
    print("2. Listar Filmes (com diretores)")
    print("3. Deletar Filme")
    print("0. Voltar ao Menu Principal")
    print("="*50)

def menu_filmes():
    while True:
        mostrar_menu_filmes()
        opcao = input("Escolha uma opção: ")
        
        try:
            if opcao == '1':
                print("\n➕ ADICIONAR FILME")
                titulo = input("Título: ")
                genero = input("Gênero: ")
                ano = int(input("Ano: "))
                classificacao = int(input("Classificação: "))
                duracao = input("Duração (ex: 02:30): ")
                inserir_filme(titulo, genero, ano, classificacao, duracao)

            elif opcao == '2':
                print("\n📋 LISTA DE FILMES")
                filmes = listar_filmes() 
                if filmes:
                    for f in filmes:
                        diretores = f[6] if f[6] else "Nenhum diretor vinculado"
                        print(f"  [{f[0]}] {f[1]} ({f[3]}) - {f[2]} - {f[4]}+ - {f[5]}")
                        print(f"      ➡️  Diretor(es): {diretores}")
                else:
                    print("  Nenhum filme cadastrado.")

            elif opcao == '3':
                print("\n🗑️ DELETAR FILME")
                filmes = listar_filmes()
                if not filmes:
                    print("❌ Nenhum filme para deletar.")
                    continue
                
                print("\n📺 Filmes disponíveis:")
                for f in filmes:
                     print(f"  [{f[0]}] {f[1]}")
                id_filme = int(input("ID do Filme a deletar: "))
                deletar_filme(id_filme)
            
            elif opcao == '0':
                print("Voltando ao menu principal...")
                break
            
            else:
                print("\n❌ Opção inválida!")

        except ValueError:
            print("\n❌ ERRO: Valor inválido! Por favor, digite um número.")
            input("\nPressione Enter para continuar...")
        except KeyboardInterrupt:
            print("\nInterrupção manual detectada. Encerrando...")
            break 
        except Exception as e:
            print(f"\n❌ ERRO INESPERADO: {e}")
            input("\nPressione Enter para continuar...")

# ========================================
# FUNÇÕES DE SUBMENU (DIRETORES)
# ========================================

def mostrar_menu_diretores():
    print("\n" + "--- 🧑‍ GERENCIAR DIRETORES ---")
    print("1. Adicionar Diretor (e vincular filme)")
    print("2. Listar Diretores")
    print("3. Desativar Diretor")
    print("4. Reativar Diretor")
    print("5. Deletar Diretor")
    print("0. Voltar ao Menu Principal")
    print("="*50)

def menu_diretores():
    while True:
        mostrar_menu_diretores()
        opcao = input("Escolha uma opção: ")

        try:
            if opcao == '1':
                print("\n➕ ADICIONAR DIRETOR")
                nome = input("Nome do diretor: ")
                nacionalidade = input("Nacionalidade: ")
                id_diretor_criado = inserir_diretor(nome, nacionalidade)
                
                if not id_diretor_criado:
                    continue 
                
                print(f"Diretor ID {id_diretor_criado} foi salvo.")
                vincular = input("Deseja vinculá-lo a um filme agora? (s/n): ")
                
                if vincular.lower() == 's':
                    filmes = listar_filmes()
                    if not filmes:
                        print("❌ Nenhum filme cadastrado para vincular.")
                        continue 

                    print("\n📺 Filmes disponíveis:")
                    for f in filmes: print(f"  [{f[0]}] {f[1]}")
                    id_filme = int(input("ID do Filme para vincular: "))
                    
                    if id_filme not in [f[0] for f in filmes]:
                        print("❌ ID de filme inválido!")
                        continue
                    vincular_filme_diretor(id_filme, id_diretor_criado)

            elif opcao == '2':
                print("\n📋 LISTA DE DIRETORES")
                
                ver_inativos = input("Deseja ver também os diretores inativos? (s/n): ").strip().lower()
                mostrar_tudo = (ver_inativos == 's')
                
                diretores = listar_diretores(incluir_inativos=mostrar_tudo) 
                
                if diretores:
                    print(f"\n--- Exibindo {'TODOS' if mostrar_tudo else 'ATIVOS'} ---")
                    for d in diretores:
                        status = "✅" if d[3] else "❌ INATIVO" 
                        print(f"  [{d[0]}] {d[1]} - {d[2]} (Status: {status})")
                else:
                    print("  Nenhum diretor cadastrado.")
            
            elif opcao == '3':
                print("\n👻 DESATIVAR DIRETOR")
                diretores = listar_diretores(incluir_inativos=False)
                if not diretores:
                    print("❌ Nenhum diretor ativo para desativar.")
                    continue
                
                print("\n👤 Diretores Ativos:")
                for d in diretores: print(f"  [{d[0]}] {d[1]} - {d[2]}")
                id_diretor = int(input("\nID do Diretor a desativar: "))
                desativar_diretor(id_diretor)

            elif opcao == '4':
                print("\n♻️ REATIVAR DIRETOR")
                diretores_todos = listar_diretores(incluir_inativos=True)
                diretores_inativos = [d for d in diretores_todos if d[3] is False]
                
                if not diretores_inativos:
                    print("❌ Nenhum diretor inativo para reativar.")
                    continue
                
                print("\n👤 Diretores Inativos:")
                for d in diretores_inativos: print(f"  [{d[0]}] {d[1]} - {d[2]}")
                id_diretor = int(input("\nID do Diretor a reativar: "))
                reativar_diretor(id_diretor)

            elif opcao == '5':
                print("\n🚨 DELETAR DIRETOR (PERMANENTE)")
                diretores = listar_diretores(incluir_inativos=True)
                if not diretores:
                    print("❌ Nenhum diretor para deletar.")
                    continue
                
                print("\n👤 Diretores (Ativos e Inativos):")
                for d in diretores: print(f"  [{d[0]}] {d[1]}")
                id_diretor = int(input("ID do Diretor a deletar: "))
                
                status = deletar_diretor(id_diretor, forcar=False)
                
                # Checa se o tipo é INT e se é maior que zero
                if type(status) is int and status > 0: 
                    print(f"❌ Não é possível deletar! Diretor possui {status} filme(s) vinculado(s).")
                    confirmacao = input("Deseja FORÇAR e remover os vínculos? (s/n): ")
                    
                    if confirmacao.lower() == 's':
                        deletar_diretor(id_diretor, forcar=True)
                        print(f"✅ Diretor ID {id_diretor} removido (vínculos removidos).")
                        input("\nPressione Enter para continuar...") 
                    else:
                        print("❌ Operação cancelada.")
                        input("\nPressione Enter para continuar...")
                
                # Sucesso sem vínculos (status é True)
                elif status is True: 
                    print(f"✅ Diretor ID {id_diretor} removido (Sem vínculos encontrados).")
                    input("\nPressione Enter para continuar...")

            elif opcao == '0':
                print("Voltando ao menu principal...")
                break
            
            else:
                print("\n❌ Opção inválida!")

        except ValueError:
            print("\n❌ ERRO: Valor inválido! Por favor, digite um número.")
            input("\nPressione Enter para continuar...")
        except KeyboardInterrupt:
            print("\nInterrupção manual detectada. Encerrando...")
            break 
        except Exception as e:
            print(f"\n❌ ERRO INESPERADO: {e}")
            input("\nPressione Enter para continuar...")

# ========================================
# FUNÇÕES DE SUBMENU (FUNCIONÁRIO)
# ========================================

def mostrar_menu_funcionario():
    print("\n" + "="*50)
    print(" 💼 MENU FUNCIONÁRIO - Gerenciamento Central")
    print("="*50)
    print("1. Gerenciar Filmes")
    print("2. Gerenciar Diretores")
    print("3. Gerenciar Clientes")
    print("4. Gerenciar Salas e Sessões")
    print("5. Vendas e Consultas (Relatórios)")
    print("0. Voltar")
    print("="*50)

def menu_funcionario():
    while True:
        mostrar_menu_funcionario()
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            menu_filmes()
        elif opcao == '2':
            menu_diretores()
        elif opcao == '3':
            menu_clientes()
        elif opcao == '4':
            menu_salas_sessoes()
        elif opcao == '5':
            menu_vendas()
        elif opcao == '0':
            print("Retornando ao Menu Principal...")
            break
        else:
            print("\n❌ Opção inválida!")
            input("\nPressione Enter para tentar novamente...")

# ========================================
# FUNÇÕES DE SUBMENU (CONSUMIDOR)
# ========================================

def mostrar_menu_consumidor():
    print("\n" + "="*50)
    print(" 🍿 MENU CLIENTE - Compras e Consultas")
    print("="*50)
    print("1. Comprar Ingresso")
    print("2. Ver Programação (Sessões)")
    print("3. Ver Filmes em Cartaz")
    print("0. Voltar")
    print("="*50)

def menu_consumidor():
    while True:
        mostrar_menu_consumidor()
        opcao = input("Escolha uma opção: ")

        try:
            if opcao == '1':
                vender_ingresso_processo()

            elif opcao == '2':
                print("\n📋 LISTA DE SESSÕES")
                sessoes = listar_sessoes()
                if sessoes:
                    for s in sessoes:
                        print(f"  [{s[0]}] {s[1]} às {s[2]} - {s[5]} ({s[3]}) - Sala: {s[4]}")
                else:
                    print("  Nenhuma sessão cadastrada.")
                input("\nPressione Enter para continuar...")

            elif opcao == '3':
                print("\n📋 FILMES EM CARTAZ")
                filmes = listar_filmes() 
                if filmes:
                    for f in filmes:
                        diretores = f[6] if f[6] else "Nenhum diretor vinculado"
                        print(f"  [{f[0]}] {f[1]} ({f[3]}) - {f[2]} - {f[4]}+ - {f[5]}")
                        print(f"      ➡️  Diretor(es): {diretores}")
                else:
                    print("  Nenhum filme cadastrado.")
                input("\nPressione Enter para continuar...")

            elif opcao == '0':
                print("Retornando ao Menu Principal...")
                break

            else:
                print("\n❌ Opção inválida!")
                input("\nPressione Enter para tentar novamente...")

        except ValueError:
            print("\n❌ ERRO: Valor inválido! Por favor, digite um número.")
            input("\nPressione Enter para continuar...")
        except KeyboardInterrupt:
            print("\nInterrupção manual detectada. Encerrando...")
            break 
        except Exception as e:
            print(f"\n❌ ERRO INESPERADO: {e}")
            input("\nPressione Enter para continuar...")

# ========================================
# FUNÇÕES DE SUBMENU (CLIENTES)
# ========================================

def mostrar_menu_clientes():
    print("\n" + "--- 👤 GERENCIAR CLIENTES ---")
    print("1. Adicionar Cliente")
    print("2. Listar Clientes")
    print("3. Desativar Cliente")
    print("4. Reativar Cliente")
    print("5. Deletar Cliente (PERMANENTE)")
    print("0. Voltar ao Menu Principal")
    print("="*50)

def menu_clientes():
    while True:
        mostrar_menu_clientes()
        opcao = input("Escolha uma opção: ")
        
        try:
            if opcao == '1':
                print("\n➕ ADICIONAR CLIENTE")
                nome = input("Nome: ")
                
                while True:
                    cpf = input("CPF (apenas 11 números): ")
                    
                    if not cpf.isdigit():
                        print("❌ ERRO: Digite apenas números.")
                        continue 
                        
                    if len(cpf) != 11:
                        print(f"❌ ERRO: O CPF deve ter 11 dígitos. Você digitou {len(cpf)}.")
                        continue 
                    
                    break
                
                email = input("Email: ")
                inserir_cliente(nome, cpf, email)
            
            elif opcao == '2':
                print("\n📋 LISTA DE CLIENTES")
                
                ver_inativos = input("Deseja ver também os clientes inativos? (s/n): ").strip().lower()
                
                mostrar_tudo = (ver_inativos == 's') 
                
                clientes = listar_clientes(incluir_inativos=mostrar_tudo)
                
                if clientes:
                    print(f"\n--- Exibindo {'TODOS' if mostrar_tudo else 'ATIVOS'} ---")
                    for c in clientes:
                        is_ativo = c[4]                     
                        status_icon = "✅" if is_ativo else "❌ INATIVO"
                        print(f"  [{c[0]}] {c[2]} - CPF: {c[1]} - {status_icon}")
                else:
                    print("  Nenhum cliente encontrado.")
            
            elif opcao == '3':
                print("\n👻 DESATIVAR CLIENTE")
                clientes = listar_clientes(incluir_inativos=False)
                if not clientes:
                    print("❌ Nenhum cliente ativo para desativar.")
                    continue
                
                print("\n👤 Clientes Ativos:")
                for c in clientes: print(f"  [{c[0]}] {c[2]} - CPF: {c[1]}")
                id_cliente = int(input("\nID do Cliente a desativar: "))
                desativar_cliente(id_cliente)

            elif opcao == '4':
                print("\n♻️ REATIVAR CLIENTE")
                clientes_todos = listar_clientes(incluir_inativos=True)
                clientes_inativos = [c for c in clientes_todos if c[4] is False]
                
                if not clientes_inativos:
                    print("❌ Nenhum cliente inativo para reativar.")
                    continue
                
                print("\n👤 Clientes Inativos:")
                for c in clientes_inativos: print(f"  [{c[0]}] {c[2]} - CPF: {c[1]}")
                id_cliente = int(input("\nID do Cliente a reativar: "))
                reativar_cliente(id_cliente)

            elif opcao == '5':
                print("\n🚨 DELETAR CLIENTE (PERMANENTE)")
                clientes = listar_clientes(incluir_inativos=True)
                if not clientes:
                    print("❌ Nenhum cliente para deletar.")
                    continue
                
                print("\n👤 Clientes:")
                for c in clientes: print(f"  [{c[0]}] {c[2]} - CPF: {c[1]}")
                id_cliente = int(input("ID do Cliente a deletar: "))
                
                # 1. Tenta deletar (Retorna INT count se bloqueado, ou True/False)
                status = deletar_cliente(id_cliente)
                
                # 2. Se status for um NÚMERO (Contagem de Ingressos)
                if type(status) is int and status > 0:
                    print(f"❌ Não é possível deletar! Cliente possui {status} ingresso(s) vinculado(s).")
                    confirmacao = input("Deseja FORÇAR a exclusão e CANCELAR os ingressos? (s/n): ")
                    
                    if confirmacao.lower() == 's':
                        # Chama a função forçada (que imprime a mensagem de sucesso)
                        deletar_cliente_e_ingressos_forcado(id_cliente)
                    else:
                        print("❌ Operação cancelada.")   
                
                # 3. Se status for True (Sucesso, 0 ingressos)
                elif status is True:
                    print(f"✅ Cliente ID {id_cliente} removido permanentemente.")
                
                # 4. Falha geral / ID não encontrado
                else:
                    print("❌ Falha na operação ou ID não encontrado.")

                input("\nPressione Enter para continuar...") 

            elif opcao == '0':
                print("Voltando ao menu principal...")
                break
            
            else:
                print("\n❌ Opção inválida!")

        except ValueError:
            print("\n❌ ERRO: Valor inválido! Por favor, digite um número.")
            input("\nPressione Enter para continuar...")
        except KeyboardInterrupt:
            print("\nInterrupção manual detectada. Encerrando...")
            break 
        except Exception as e:
            print(f"\n❌ ERRO INESPERADO: {e}")
            input("\nPressione Enter para continuar...")
            
# ========================================
# FUNÇÕES DE SUBMENU (SALAS E SESSÕES)
# ========================================

def mostrar_menu_salas_sessoes():
    print("\n" + "--- 🏛️ GERENCIAR SALAS E SESSÕES ---")
    print("1. Adicionar Sala")
    print("2. Listar Salas")
    print("3. Deletar Sala")
    print("4. Adicionar Sessão")
    print("5. Listar Sessões")
    print("6. Deletar Sessão")
    print("0. Voltar ao Menu Principal")
    print("="*50)

def menu_salas_sessoes():
    while True:
        mostrar_menu_salas_sessoes()
        opcao = input("Escolha uma opção: ")

        try:
            if opcao == '1':
                print("\n➕ ADICIONAR SALA")
                numero = int(input("Número da sala: "))
                capacidade = int(input("Capacidade: "))
                tipo = input("Tipo (IMAX/3D/Standard): ")
                inserir_sala(numero, capacidade, tipo)
            
            elif opcao == '2':
                print("\n📋 LISTA DE SALAS")
                salas = listar_salas()
                if salas:
                    for s in salas:
                        print(f"  [{s[0]}] Sala {s[1]} - Capacidade: {s[2]} - Tipo: {s[3]}")
                else:
                    print("Nenhuma sala cadastrada.")

            elif opcao == '3':
                print("\n🗑️ DELETAR SALA")
                salas = listar_salas()
                if not salas:
                    print("❌ Nenhuma sala para deletar.")
                    continue
                
                print("\n🏛️ Salas disponíveis:")
                for s in salas: print(f"  [{s[0]}] Sala {s[1]}")
                id_sala = int(input("ID da Sala a deletar: "))
                deletar_sala(id_sala)

            elif opcao == '4':
                print("\n➕ ADICIONAR SESSÃO")
                while True:
                    data = input("Data (AAAA-MM-DD): ")
                    try:
                        data_validada = datetime.strptime(data, "%Y-%m-%d")
                        if data_validada < datetime.now():
                             print("⚠️  Aviso: Essa data já passou!")
                             confirma = input("   Deseja continuar mesmo assim? (s/n): ")
                             if confirma.lower() != 's':
                                 continue
                        break 
                    except ValueError:
                        print("❌ Data inválida ou inexistente! Use o formato AAAA-MM-DD.")
                horario = input("Horário (HH:MM): ")
                tipo_exibicao = input("Tipo de exibição (2D/3D/IMAX): ")
                
                filmes = listar_filmes()
                if not filmes:
                    print("❌ Cadastre filmes primeiro!")
                    continue
                print("\n📺 Filmes disponíveis:")
                for f in filmes: print(f"  [{f[0]}] {f[1]}")
                id_filme = int(input("ID do Filme: "))
                
                salas = listar_salas()
                if not salas:
                    print("❌ Cadastre salas primeiro!")
                    continue
                print("\n🏛️ Salas disponíveis:")
                for s in salas: print(f"  [{s[0]}] Sala {s[1]}")
                id_sala = int(input("ID da Sala: "))
                
                inserir_sessao(data, horario, tipo_exibicao, id_filme, id_sala)

            elif opcao == '5':
                print("\n📋 LISTA DE SESSÕES")
                sessoes = listar_sessoes()
                if sessoes:
                    for s in sessoes:
                        print(f"  [{s[0]}] {s[1]} às {s[2]} - {s[5]} ({s[3]}) - Sala ID: {s[4]}")
                else:
                    print("  Nenhuma sessão cadastrada.")

            elif opcao == '6':
                print("\n🗑️ DELETAR SESSÃO")
                sessoes = listar_sessoes()
                if not sessoes:
                    print("❌ Nenhuma sessão para deletar.")
                    continue
                
                print("\n📺 Sessões disponíveis:")
                for s in sessoes:
                    print(f"  [{s[0]}] {s[1]} às {s[2]} - {s[5]} - Sala ID: {s[4]}")
                id_sessao = int(input("ID da Sessão a deletar: "))
                deletar_sessao(id_sessao)

            elif opcao == '0':
                print("Voltando ao menu principal...")
                break
            
            else:
                print("\n❌ Opção inválida!")

        except ValueError:
            print("\n❌ ERRO: Valor inválido! Por favor, digite um número.")
            input("\nPressione Enter para continuar...")
        except KeyboardInterrupt:
            print("\nInterrupção manual detectada. Encerrando...")
            break 
        except Exception as e:
            print(f"\n❌ ERRO INESPERADO: {e}")
            input("\nPressione Enter para continuar...")

# ========================================
# FUNÇÃO PARA DEFINIR PREÇOS
# ========================================

def definir_precos():
    """
    Define os preços globais dos ingressos (Inteira e Meia).
    """
    global PRECO_INTEIRA, PRECO_MEIA
    
    print("\n⚙️ DEFINIR PREÇOS DOS INGRESSOS")
    print(f"   Preço ATUAL (Inteira): R$ {PRECO_INTEIRA:.2f}")
    print(f"   Preço ATUAL (Meia):    R$ {PRECO_MEIA:.2f}")
    
    try:
        novo_preco_inteira_str = input(f"\nNovo preço INTEIRA (Deixe em branco para manter R$ {PRECO_INTEIRA:.2f}): ")
        if novo_preco_inteira_str:
            PRECO_INTEIRA = float(novo_preco_inteira_str.replace(',', '.'))
        
        novo_preco_meia_str = input(f"Novo preço MEIA (Deixe em branco para manter R$ {PRECO_MEIA:.2f}): ")
        if novo_preco_meia_str:
            PRECO_MEIA = float(novo_preco_meia_str.replace(',', '.'))

        print(f"\n✅ Preços atualizados:")
        print(f"   Inteira: R$ {PRECO_INTEIRA:.2f}")
        print(f"   Meia:    R$ {PRECO_MEIA:.2f}")
        
    except ValueError:
            print("\n❌ ERRO: Valor inválido! Por favor, digite um número.")
            input("\nPressione Enter para continuar...")
    except KeyboardInterrupt:
        print("\nInterrupção manual detectada. Encerrando...")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        input("\nPressione Enter para continuar...")

# ========================================
# FUNÇÕES DO MENU DE VENDAS
# ========================================

def mostrar_menu_vendas():
    print("\n" + "--- 🎟️ VENDAS E CONSULTAS ---")
    print("1. Vender Ingresso")
    print("2. Listar Ingressos")
    print("3. Cancelar Ingresso (Deletar)")
    print("4. Ver Assentos Disponíveis (por Sessão)")
    print("5. Ver Mapa de Ocupação (por Sessão)")
    print("6. Definir Preços dos Ingressos")
    print("0. Voltar ao Menu Principal")
    print("="*50)

def vender_ingresso_processo():
    """Contém a lógica completa para o processo de venda de um único ingresso."""
    try:
        print("\n🎟️ INICIAR VENDA DE INGRESSO")

        
        global PRECO_INTEIRA, PRECO_MEIA
        if PRECO_INTEIRA == 0.0 or PRECO_MEIA == 0.0:
            print("="*50)
            print("❌ ERRO: Os preços dos ingressos ainda não foram definidos!")
            print("   (Funcionário: Use a Opção 6 do menu de Vendas para definir os preços primeiro.)")
            return
        
        sessoes = listar_sessoes()
        if not sessoes:
            print("❌ Cadastre sessões primeiro!")
            return
        
        print("\n📺 Sessões disponíveis:")
        for s in sessoes:
            print(f"  [{s[0]}] {s[1]} às {s[2]} - {s[5]} ({s[3]}) - Sala ID: {s[4]}")
        
        id_sessao = int(input("\nID da Sessão: "))
        
        info = verificar_disponibilidade_sessao(id_sessao)
        if not info:
            print("❌ Sessão inválida ou sem capacidade definida.")
            return
        
        print(f"\n📊 Capacidade: {info[0]} | Vendidos: {info[1]} | Disponíveis: {info[2]}")
        
        assentos_disp = listar_assentos_disponiveis(id_sessao)
        if not assentos_disp:
            print("❌ Não há assentos disponíveis nesta sessão!")
            return
        
        print("\n💺 Assentos disponíveis:")
        for i, assento in enumerate(assentos_disp, 1):
            print(f"  [{assento[0]}] {assento[1]}", end="  ") 
            if i % 10 == 0: print()
        print()
        
        numero_assento_str = input("\nNúmero do Assento (ex: A5): ").strip().upper()
        
        id_assento = None
        for a in assentos_disp:
            if a[1].upper() == numero_assento_str:
                id_assento = a[0] 
                break
        
        if id_assento is None:
            print("❌ Esse número de assento não está disponível ou não existe!")
            return
        
        tipo_ingresso = input("\nTipo (Inteira/Meia): ").strip().lower()
        preco = 0.0

        if tipo_ingresso == 'inteira':
            preco = PRECO_INTEIRA
        elif tipo_ingresso == 'meia':
            preco = PRECO_MEIA
        else:
            print("❌ Tipo inválido! (Deve ser 'Inteira' ou 'Meia')")
            return
        
        print(f"   Preço definido: R$ {preco:.2f}")
        
        print("\n👤 DADOS DO CLIENTE")
        nome_cliente = input("Nome: ")
        
        while True:
            cpf_cliente = input("CPF (apenas 11 números): ")
            
            if not cpf_cliente.isdigit():
                print("❌ ERRO: Digite apenas números.")
                continue 
                
            if len(cpf_cliente) != 11:
                print(f"❌ ERRO: O CPF deve ter 11 dígitos. Você digitou {len(cpf_cliente)}.")
                continue 
            
            break
        
        email_cliente = input("Email: ")
        
        inserir_ingresso(preco, tipo_ingresso, id_assento, id_sessao, 
                       nome_cliente, cpf_cliente, email_cliente)

    except ValueError:
            print("\n❌ ERRO: Valor inválido! Por favor, digite um número.")
            input("\nPressione Enter para continuar...")
    except KeyboardInterrupt:
        print("\nInterrupção manual detectada. Encerrando...")
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        input("\nPressione Enter para continuar...")

def menu_vendas():
    while True:
        mostrar_menu_vendas()
        opcao = input("Escolha uma opção: ")

        try:
            if opcao == '1':
                vender_ingresso_processo()

            elif opcao == '2':
                print("\n🎟️ LISTA DE INGRESSOS")
                ingressos = listar_ingressos()
                if ingressos:
                    for i in ingressos:
                        print(f"  [{i[0]}] {i[6]} - {i[4]} às {i[5]} - Assento: {i[3]} - {i[2]} - R$ {i[1]:.2f} - Cliente: {i[7]}")
                else:
                    print("Nenhum ingresso vendido.")
                input("\nPressione Enter para continuar...")
            
            elif opcao == '3':
                print("\n🚫 CANCELAR INGRESSSO")
                ingressos = listar_ingressos()
                if not ingressos:
                    print("❌ Nenhum ingresso para cancelar.")
                    continue
                
                print("\n🎟️ Ingressos Vendidos:")
                for i in ingressos:
                    print(f"  [{i[0]}] {i[6]} - {i[4]} às {i[5]} - Assento: {i[3]} - Cliente: {i[7]}")
                id_ingresso = int(input("ID do Ingresso a cancelar: "))
                deletar_ingresso(id_ingresso)
                input("\nPressione Enter para continuar...")
            
            elif opcao == '4':
                print("\n💺 VER ASSENTOS DISPONÍVEIS")
                
                sessoes = listar_sessoes()
                if not sessoes:
                    print("❌ Nenhuma sessão cadastrada!")
                    continue
                
                print("\n📺 Sessões:")
                for s in sessoes:
                    print(f"  [{s[0]}] {s[1]} às {s[2]} - {s[5]} - Sala ID: {s[4]}")
                id_sessao = int(input("\nID da Sessão: "))
                
                assentos = listar_assentos_disponiveis(id_sessao)
                if assentos:
                    print(f"\n✅ {len(assentos)} assentos disponíveis:")
                    for i, a in enumerate(assentos, 1):
                        print(f"  {a[1]}", end="  ")
                        if i % 15 == 0: print()
                else:
                    print("\n❌ Sessão esgotada!")
                
                input("\nPressione Enter para continuar...")
                
            elif opcao == '5':
                print("\n🗺️ MAPA DE OCUPAÇÃO")
                
                sessoes = listar_sessoes()
                if not sessoes:
                    print("❌ Nenhuma sessão cadastrada!")
                    continue
                
                print("\n📺 Sessões:")
                for s in sessoes:
                    print(f"  [{s[0]}] {s[1]} às {s[2]} - {s[5]} - Sala ID: {s[4]}")
                id_sessao = int(input("\nID da Sessão: "))
                
                info = verificar_disponibilidade_sessao(id_sessao)
                if not info:
                    print("❌ Sessão inválida ou sem capacidade definida.")
                    continue
                if info[0] == 0:
                    print("❌ Erro: Sala com capacidade 0.")
                    continue

                print(f"\n📊 ESTATÍSTICAS:")
                print(f"   Capacidade Total: {info[0]}")
                print(f"   Ingressos Vendidos: {info[1]}")
                print(f"   Assentos Disponíveis: {info[2]}")
                print(f"   Taxa de Ocupação: {(info[1]/info[0]*100):.1f}%")
                
                ocupados = listar_assentos_ocupados(id_sessao)
                if ocupados:
                    print(f"\n🔴 ASSENTOS OCUPADOS ({len(ocupados)}):")
                    for o in ocupados:
                        print(f"   {o[0]} - {o[1]} ({o[2]}) - R$ {o[3]:.2f}")
                
                disponiveis = listar_assentos_disponiveis(id_sessao)
                if disponiveis:
                    print(f"\n🟢 ASSENTOS DISPONÍVEIS ({len(disponiveis)}):")
                    for i, d in enumerate(disponiveis, 1):
                        print(f"  {d[1]}", end="  ")
                        if i % 15 == 0: print()

            elif opcao == '6':
                definir_precos()
                input("\nPressione Enter para continuar...")

            elif opcao == '0':
                print("Voltando ao menu principal...")
                break
            
            else:
                print("\n❌ Opção inválida!")
                input("\nPressione Enter para tentar novamente...")

        except ValueError:
            print("\n❌ ERRO: Valor inválido! Por favor, digite um número.")
            input("\nPressione Enter para continuar...")
        except KeyboardInterrupt:
            print("\nInterrupção manual detectada. Encerrando...")
            break 
        except Exception as e:
            print(f"\n❌ ERRO INESPERADO: {e}")
            input("\nPressione Enter para continuar...")

# ========================================
# MENU PRINCIPAL
# ========================================

def mostrar_menu_principal():
    print("\n" + "="*50)
    print(" 🎬 Gerenciar o YUUI Cinema - Acesso")
    print("="*50)
    print("1. Logar como Funcionário")
    print("2. Acessar como Cliente")
    print("0. Sair do Sistema")
    print("="*50)

def main():
    while True:
        mostrar_menu_principal()
        opcao = input("\nEscolha uma opção: ")

        if opcao == '1':
            print("\n🔒 ACESSO FUNCIONÁRIO")
            usuario = input("Usuário: ")
            senha = getpass.getpass("Senha: ")

            if usuario == USUARIO_FUNCIONARIO and senha == SENHA_FUNCIONARIO:
                print("✅ Acesso liberado!")
                menu_funcionario()
            else:
                print("❌ Usuário ou senha incorretos.")
                input("\nPressione Enter para voltar ao Menu Principal...")
        
        elif opcao == '2':
            menu_consumidor()
            
        elif opcao == '0':
            print("\n👋 Até logo!")
            break
        
        else:
            print("\n❌ Opção inválida!")
            input("\nPressione Enter para tentar novamente...")


if __name__ == "__main__":
    main()