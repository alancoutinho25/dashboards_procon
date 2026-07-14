# ============================================================
# CONFIGURAÇÕES DO BANCO DE DADOS
# ============================================================

import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")
HOST = os.getenv("HOST")
PORTA = int(os.getenv("PORTA"))
BANCO = os.getenv("BANCO")