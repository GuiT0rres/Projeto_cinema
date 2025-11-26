-- =====================================
-- SCRIPT DDL - Cinema
-- =====================================

DROP TABLE IF EXISTS Ingressos CASCADE;
DROP TABLE IF EXISTS Sessao CASCADE;
DROP TABLE IF EXISTS Assento CASCADE;
DROP TABLE IF EXISTS Filme_Diretor CASCADE;
DROP TABLE IF EXISTS Sala CASCADE;
DROP TABLE IF EXISTS Clientes CASCADE;
DROP TABLE IF EXISTS Diretor CASCADE;
DROP TABLE IF EXISTS Filme CASCADE;
drop table if exists exclusoes_log cascade;


-- ==============================
-- TABELA: Exclusões (Log)
-- ==============================
CREATE TABLE exclusoes_log (
    id_log SERIAL PRIMARY KEY,
    tabela_afetada VARCHAR(50) NOT NULL,
    id_registro_original INTEGER NOT NULL,
    dados_json JSONB NOT NULL,
    data_exclusao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    usuario_acao VARCHAR(50) DEFAULT 'system'
);

-- ==============================
-- 1. FUNÇÃO DE AUDITORIA UNIVERSAL (CORRIGIDA)
-- ==============================

CREATE OR REPLACE FUNCTION log_exclusao()
RETURNS TRIGGER AS $$
DECLARE
    registro_pk_id INTEGER;
    old_row_json JSONB; -- Variável para armazenar o registro OLD como JSON
BEGIN
    -- 1. Converte o registro OLD (linha sendo deletada) para JSONB
    old_row_json := to_jsonb(OLD);
    
    -- 2. Acessa o valor da chave primária (PK) usando o argumento (TG_ARGV[0]) no objeto JSONB
    -- O operador ->> retorna o valor como texto, que é então convertido para INTEGER.
    registro_pk_id := (old_row_json ->> TG_ARGV[0])::INTEGER;

    INSERT INTO exclusoes_log (
        tabela_afetada, 
        id_registro_original, 
        dados_json,
        usuario_acao
    )
    VALUES (
        TG_TABLE_NAME, 
        registro_pk_id,
        old_row_json, -- Agora usa a variável JSONB
        current_user
    );
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- ==============================
-- TABELA: Filme
-- ==============================
create table Filme (
    id_filme serial primary key,
    titulo VARCHAR(150) not null,
    genero VARCHAR(50) not null,
    ano int not null,
    classificacao int not null,
    duracao VARCHAR(10) not null
);
-- 2. TRIGGER NO FILME
CREATE TRIGGER trig_log_exclusao_filme
BEFORE DELETE ON Filme
FOR EACH ROW
EXECUTE FUNCTION log_exclusao('id_filme');

-- ==============================
-- TABELA: Diretor
-- ==============================
create table Diretor (
    id_diretor serial primary key,
    nome_diretor VARCHAR(50) not null,
    nacionalidade VARCHAR(50) not null,
    ativo BOOLEAN DEFAULT TRUE 
);
-- 3. TRIGGER NO DIRETOR
CREATE TRIGGER trig_log_exclusao_diretor
BEFORE DELETE ON Diretor
FOR EACH ROW
EXECUTE FUNCTION log_exclusao('id_diretor');

-- ==============================
-- TABELA: Filme_Diretor (Relacionamento N:N)
-- ==============================
create table Filme_Diretor (
    id_filme int references Filme(id_filme) ON DELETE CASCADE, -- Adicionado CASCADE para limpeza
    id_diretor int references Diretor(id_diretor) ON DELETE CASCADE, -- Adicionado CASCADE para limpeza
    primary key (id_filme, id_diretor)
);

-- ==============================
-- TABELA: Sala
-- ==============================
create table Sala (
    id_sala serial primary key,
    numero_sala int not null,
    capacidade int not null,
    tipo_sala VARCHAR(10)
);
-- 4. TRIGGER NA SALA
CREATE TRIGGER trig_log_exclusao_sala
BEFORE DELETE ON Sala
FOR EACH ROW
EXECUTE FUNCTION log_exclusao('id_sala');

-- ==============================
-- TABELA: Assento
-- ==============================
create table Assento (
    id_assento serial primary key,
    numero_assento VARCHAR(10) not null,
    id_sala int not null references Sala(id_sala),
    unique(numero_assento, id_sala)
);

-- ==============================
-- TABELA: Sessao
-- ==============================
create table Sessao(
    id_sessao serial primary key,
    data date not null,
    horario time not null,
    tipo_exibicao VARCHAR(20),
    id_filme int not null references Filme(id_filme),
    id_sala int not null references Sala(id_sala)
);
-- 5. TRIGGER NA SESSAO
CREATE TRIGGER trig_log_exclusao_sessao
BEFORE DELETE ON Sessao
FOR EACH ROW
EXECUTE FUNCTION log_exclusao('id_sessao');

-- ==============================
-- TABELA: Clientes
-- ==============================
create table Clientes (
    id_cliente serial primary key,
    CPF VARCHAR(11) not null unique,
    nome VARCHAR(50) not null,
    email VARCHAR(50) not null,
    ativo BOOLEAN default TRUE  
);
-- 6. TRIGGER NO CLIENTE (Original, ajustada para o novo método)
CREATE TRIGGER trig_log_exclusao_clientes
BEFORE DELETE ON Clientes
FOR EACH ROW
EXECUTE FUNCTION log_exclusao('id_cliente');


-- ==============================
-- TABELA: Ingressos
-- ==============================
create table Ingressos (
    id_ingresso serial primary key,
    preco NUMERIC(10, 2) not null,
    tipo_ingresso VARCHAR(10) not null,
    id_assento int not null references Assento(id_assento),
    id_sessao int not null references Sessao(id_sessao),
    id_cliente int not null references Clientes(id_cliente),
    unique(id_assento, id_sessao)
);

-- =====================================
-- FIM DO SCRIPT
-- =====================================