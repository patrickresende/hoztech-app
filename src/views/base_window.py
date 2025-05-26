"""
Módulo com a classe base para todas as janelas.
Este módulo implementa funcionalidades comuns para todas as janelas.
"""

import os
import logging
from typing import Dict, List, Callable, Any, Optional
import customtkinter as ctk
from PIL import Image, ImageTk

logger = logging.getLogger("base_window")


class BaseWindow(ctk.CTkFrame):
    """Classe base para todas as janelas da aplicação."""
    
    def __init__(self, master, app, title=""):
        """
        Inicializa a janela base.
        
        Args:
            master: Widget pai (janela)
            app: Instância da aplicação principal
            title (str): Título da janela
        """
        super().__init__(master)
        self.app = app
        self.title = title
        
        # Configurar layout grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Cabeçalho
        self.grid_rowconfigure(1, weight=1)  # Conteúdo
        self.grid_rowconfigure(2, weight=0)  # Rodapé
        
        # Criar estrutura base
        self._create_header()
        self._create_content_frame()
        self._create_footer()
    
    def _create_header(self):
        """Cria o cabeçalho da janela."""
        self.header_frame = ctk.CTkFrame(self, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        # Botão de voltar
        self.back_button = ctk.CTkButton(
            self.header_frame,
            text="← Voltar",
            command=self.app.go_back_to_main,
            width=100
        )
        self.back_button.pack(side="left", padx=10, pady=10)
        
        # Título da janela
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text=self.title, 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(side="left", padx=10, pady=10)
    
    def _create_content_frame(self):
        """Cria o frame de conteúdo."""
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
    
    def _create_footer(self):
        """Cria o rodapé da janela."""
        self.footer_frame = ctk.CTkFrame(self, corner_radius=0)
        self.footer_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        
        # Status da aplicação
        self.status_label = ctk.CTkLabel(
            self.footer_frame, 
            text="Pronto", 
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
    
    def update_status(self, message, is_error=False):
        """
        Atualiza a mensagem de status no rodapé.
        
        Args:
            message (str): Mensagem de status
            is_error (bool): Se é uma mensagem de erro
        """
        self.status_label.configure(
            text=message,
            text_color="red" if is_error else None
        )
        self.update_idletasks()
    
    def show_message(self, title, message, error=False):
        """
        Exibe uma mensagem para o usuário.
        
        Args:
            title (str): Título da mensagem
            message (str): Conteúdo da mensagem
            error (bool): Se é uma mensagem de erro
        """
        if error:
            ctk.CTkMessageBox.show_error(title, message)
        else:
            ctk.CTkMessageBox.show_info(title, message)
    
    def create_scrollable_frame(self, master):
        """
        Cria um frame com barra de rolagem.
        
        Args:
            master: Widget pai
            
        Returns:
            tuple: (container_frame, scrollable_frame)
        """
        # Container para o frame com rolagem
        container = ctk.CTkFrame(master)
        
        # Canvas para implementar a rolagem
        canvas = ctk.CTkCanvas(container)
        scrollbar = ctk.CTkScrollbar(container, command=canvas.yview)
        scrollable_frame = ctk.CTkFrame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Empacotar widgets
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return container, scrollable_frame
    
    def create_table(self, master, columns, data=None):
        """
        Cria uma tabela simples.
        
        Args:
            master: Widget pai
            columns (list): Lista de colunas
            data (list): Lista de linhas (cada linha é uma lista)
            
        Returns:
            list: Lista de widgets da tabela
        """
        table_frame = ctk.CTkFrame(master)
        
        # Cabeçalho da tabela
        for i, col in enumerate(columns):
            header = ctk.CTkLabel(
                table_frame, 
                text=col, 
                font=ctk.CTkFont(weight="bold"),
                width=100
            )
            header.grid(row=0, column=i, sticky="ew", padx=5, pady=5)
        
        # Dados da tabela
        widgets = []
        if data:
            for row_idx, row in enumerate(data):
                row_widgets = []
                for col_idx, cell in enumerate(row):
                    cell_widget = ctk.CTkLabel(
                        table_frame, 
                        text=str(cell),
                        width=100
                    )
                    cell_widget.grid(
                        row=row_idx + 1, 
                        column=col_idx, 
                        sticky="ew", 
                        padx=5, 
                        pady=5
                    )
                    row_widgets.append(cell_widget)
                widgets.append(row_widgets)
        
        return table_frame, widgets
    
    def load_data(self):
        """
        Carrega dados para a janela.
        Deve ser implementado pelas classes filhas.
        """
        pass 