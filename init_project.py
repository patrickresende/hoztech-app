#!/usr/bin/env python3
"""
Script de inicialização do projeto Processador de Holerites.
Este script configura a estrutura inicial de diretórios e arquivos.
"""

import os
import sys
import logging
import shutil
from pathlib import Path
from datetime import datetime


def main():
    """Função principal para configuração do projeto."""
    print("=== Inicializando Processador de Holerites v1.2.0 ===")
    
    # Definir diretórios
    BASE_DIR = Path(__file__).resolve().parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    OUTPUT_DIR = BASE_DIR / "output"
    BACKUP_DIR = BASE_DIR / "backup"
    
    # Criar diretórios necessários
    print("Criando estrutura de diretórios...")
    for dir_path in [DATA_DIR, LOGS_DIR, OUTPUT_DIR, BACKUP_DIR]:
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {dir_path}")
        except Exception as e:
            print(f"  ✗ {dir_path} - Erro: {e}")
    
    # Configurar arquivo .env se não existir
    env_file = BASE_DIR / ".env"
    if not env_file.exists():
        print("Criando arquivo .env...")
        try:
            with open(env_file, "w", encoding="utf-8") as f:
                f.write("""# Configurações de e-mail
EMAIL_ADDRESS=seu-email@gmail.com
EMAIL_PASSWORD=sua-senha-de-app
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
USE_TLS=True
""")
            print(f"  ✓ {env_file}")
        except Exception as e:
            print(f"  ✗ {env_file} - Erro: {e}")
    
    # Configurar arquivo de log
    log_file = LOGS_DIR / "app.log"
    if not log_file.exists():
        print("Criando arquivo de log...")
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(f"{datetime.now()} - Aplicação inicializada\n")
            print(f"  ✓ {log_file}")
        except Exception as e:
            print(f"  ✗ {log_file} - Erro: {e}")
    
    # Verificar se temos o arquivo all_employee.txt e garantir que ele exista
    employee_file = BASE_DIR / "all_employee.txt"
    
    if employee_file.exists():
        print(f"Arquivo de funcionários encontrado: {employee_file}")
        
        # Fazer backup do arquivo para data
        backup_file = DATA_DIR / "all_employee.txt"
        try:
            shutil.copy2(employee_file, backup_file)
            print(f"  ✓ Backup criado em {backup_file}")
        except Exception as e:
            print(f"  ✗ Erro ao criar backup: {e}")
    else:
        print(f"Arquivo de funcionários não encontrado: {employee_file}")
        try:
            # Criar arquivo vazio
            with open(employee_file, "w", encoding="utf-8") as f:
                f.write("# Lista de funcionários - Um nome por linha\n")
            print(f"  ✓ Criado arquivo vazio {employee_file}")
        except Exception as e:
            print(f"  ✗ Erro ao criar arquivo: {e}")
    
    # Verificar dependências Python
    print("Verificando dependências Python...")
    try:
        import customtkinter
        import fitz  # PyMuPDF
        import pytesseract
        import PIL
        import rapidfuzz
        import dotenv
        import pydantic
        import sqlalchemy
        
        print("  ✓ Todas as dependências encontradas!")
    except ImportError as e:
        print(f"  ✗ Dependência faltando: {e}")
        print("    Execute 'pip install -r requirements.txt' para instalar todas as dependências.")
    
    # Verificar instalação do Tesseract
    print("Verificando Tesseract OCR...")
    try:
        import pytesseract
        path = pytesseract.get_tesseract_version()
        print(f"  ✓ Tesseract OCR encontrado (versão: {pytesseract.get_tesseract_version()})")
    except Exception:
        print("  ✗ Tesseract OCR não encontrado ou não configurado corretamente.")
        print("    Instale o Tesseract OCR e verifique se está no PATH do sistema.")
        print("    Visite: https://github.com/UB-Mannheim/tesseract/wiki")
    
    print("\nInicialização concluída! Execute a aplicação com:")
    print("python src/app.py")


if __name__ == "__main__":
    main() 