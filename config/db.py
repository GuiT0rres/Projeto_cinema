import psycopg2 
import os #Para utilizar juntamente ao dotenv afim de ler o arquivo .env
from dotenv import load_dotenv # Para ler oq está guardado no arquivo .env

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