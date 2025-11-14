import psycopg2
import os
from dotenv import load_dotenv

load_dotenv() 

def criar_conexao():
    try:
        con = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        return con
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None