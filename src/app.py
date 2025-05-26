"""
Aplicação principal para processamento de holerites.
Este módulo implementa a interface gráfica usando CustomTkinter.
"""

import os
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any, Callable
import customtkinter as ctk
from customtkinter import filedialog
import tkinter as tk

# Configurar diretórios necessários
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "output"

# Garantir que os diretórios existam
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("app")

# Importar módulos internos
from src.views.main_window import MainWindow
from src.views.employee_window import EmployeeWindow
from src.views.pdf_processor_window import PDFProcessorWindow
from src.views.email_window import EmailWindow
from src.views.database_window import DatabaseWindow
from src.utils.settings import AppSettings

# Constantes da aplicação
APP_NAME = "Processador de Holerites"
APP_VERSION = "1.2.0"
APP_AUTHOR = "RH"


class Application:
    """Classe principal da aplicação."""
    
    def __init__(self):
        """Inicializa a aplicação."""
        
        # Configurar estilo do CustomTkinter
        ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
        
        # Carregar configurações
        self.settings = AppSettings(DATA_DIR / "settings.json")
        
        # Criar janela principal
        self.root = ctk.CTk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Criar ícone da aplicação (opcional)
        # self.root.iconbitmap("path/to/icon.ico")
        
        # Inicializar janelas
        self.main_window = None
        self.employee_window = None
        self.pdf_processor_window = None
        self.email_window = None
        self.database_window = None
        
        # Mostrar janela principal
        self._show_main_window()
        
        logger.info(f"Aplicação {APP_NAME} v{APP_VERSION} iniciada")
    
    def run(self):
        """Inicia o loop principal da aplicação."""
        self.root.mainloop()
    
    def _show_main_window(self):
        """Mostra a janela principal da aplicação."""
        if self.main_window is None:
            self.main_window = MainWindow(self.root, self)
            self.main_window.pack(fill="both", expand=True)
    
    def show_employee_window(self):
        """Mostra a janela de gerenciamento de funcionários."""
        self._hide_all_windows()
        if self.employee_window is None:
            self.employee_window = EmployeeWindow(self.root, self)
        self.employee_window.pack(fill="both", expand=True)
        self.employee_window.load_data()
    
    def show_pdf_processor_window(self):
        """Mostra a janela de processamento de PDFs."""
        self._hide_all_windows()
        if self.pdf_processor_window is None:
            self.pdf_processor_window = PDFProcessorWindow(self.root, self)
        self.pdf_processor_window.pack(fill="both", expand=True)
    
    def show_email_window(self):
        """Mostra a janela de envio de emails."""
        self._hide_all_windows()
        if self.email_window is None:
            self.email_window = EmailWindow(self.root, self)
        self.email_window.pack(fill="both", expand=True)
        self.email_window.load_data()
    
    def show_database_window(self):
        """Mostra a janela de gerenciamento de bases de dados."""
        self._hide_all_windows()
        if self.database_window is None:
            self.database_window = DatabaseWindow(self.root, self)
        self.database_window.pack(fill="both", expand=True)
        self.database_window.load_data()
    
    def _hide_all_windows(self):
        """Esconde todas as janelas da aplicação."""
        if self.main_window is not None:
            self.main_window.pack_forget()
        if self.employee_window is not None:
            self.employee_window.pack_forget()
        if self.pdf_processor_window is not None:
            self.pdf_processor_window.pack_forget()
        if self.email_window is not None:
            self.email_window.pack_forget()
        if self.database_window is not None:
            self.database_window.pack_forget()
    
    def go_back_to_main(self):
        """Volta para a janela principal."""
        self._hide_all_windows()
        self._show_main_window()
    
    def _on_close(self):
        """Manipula o evento de fechamento da aplicação."""
        # Salvar configurações
        self.settings.save()
        
        # Fechar a aplicação
        logger.info("Aplicação encerrada")
        self.root.destroy()


def setup_environment():
    """Configura o ambiente da aplicação."""
    # Garantir que os caminhos necessários estão no PATH do Python
    sys.path.insert(0, str(BASE_DIR))


if __name__ == "__main__":
    setup_environment()
    app = Application()
    app.run() 