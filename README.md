# 🎬 YUUI Cinema Manager

Sistema de gerenciamento de cinema via linha de comando (CLI), desenvolvido em Python com integração a banco de dados PostgreSQL. O projeto permite o controle completo de filmes, sessões, clientes e venda de ingressos.

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

## 📋 Funcionalidades

### 🎥 Gestão de Filmes e Diretores
* Cadastro de filmes e diretores.
* Vínculo entre filmes e diretores.
* Listagem detalhada.
* Soft Delete (desativação) e exclusão permanente.

### 🏛️ Gestão de Salas e Sessões
* Cadastro de salas com capacidade e tipo (IMAX, 3D, etc.).
* Agendamento de sessões (validação de data e horário).
* Verificação de disponibilidade de sala.

### 👤 Gestão de Clientes
* Cadastro com validação de CPF (11 dígitos e apenas números).
* Soft Delete (inativar cliente sem perder histórico).
* Histórico de compras por cliente.

### 🎟️ Vendas e Bilheteria
* Definição de preços (Inteira/Meia) em tempo de execução.
* Mapa de assentos (Visualização de disponíveis/ocupados).
* Venda de ingressos com verificação de duplicidade de assento.
* Relatórios de ocupação por sessão.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Banco de Dados:** PostgreSQL
* **Bibliotecas:**
    * `psycopg2-binary` (Conector do banco de dados)
    * `python-dotenv` (Gerenciamento de variáveis de ambiente)
    * `datetime` (Manipulação de datas)

## 🚀 Como Rodar o Projeto

### Pré-requisitos
* Python 3 instalado.
* PostgreSQL instalado e rodando.
* Git instalado.

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone [https://github.com/seu-usuario/projeto-cinema.git](https://github.com/seu-usuario/projeto-cinema.git)
   cd projeto-cinema
