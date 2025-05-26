"""
Módulo da janela principal da aplicação.
Este módulo implementa a tela inicial com acesso às principais funcionalidades.
"""

import os
import logging
from typing import Dict, List, Callable, Any, Optional
import customtkinter as ctk
from PIL import Image, ImageTk

logger = logging.getLogger("main_window")


class MainWindow(ctk.CTkFrame):
    """Janela principal da aplicação."""
    
    def __init__(self, master, app):
        """
        Inicializa a janela principal.
        
        Args:
            master: Widget pai (janela)
            app: Instância da aplicação principal
        """
        super().__init__(master)
        self.app = app
        
        # Configurar layout grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Título não expande
        self.grid_rowconfigure(1, weight=1)  # Conteúdo expande
        self.grid_rowconfigure(2, weight=0)  # Rodapé não expande
        
        # Criar widgets
        self._create_header()
        self._create_content()
        self._create_footer()
    
    def _create_header(self):
        """Cria o cabeçalho da janela."""
        header_frame = ctk.CTkFrame(self, corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Processador de Holerites", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
    
    def _create_content(self):
        """Cria o conteúdo principal da janela."""
        content_frame = ctk.CTkFrame(self)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        # Configurar layout grid para o conteúdo
        content_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="column")
        content_frame.grid_rowconfigure((0, 1), weight=1, uniform="row")
        
        # Função para criar um card
        def create_card(row, col, title, description, icon_path=None, command=None):
            card = ctk.CTkFrame(content_frame)
            card.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            
            card.grid_columnconfigure(0, weight=1)
            card.grid_rowconfigure(0, weight=0)  # Título
            card.grid_rowconfigure(1, weight=1)  # Descrição
            card.grid_rowconfigure(2, weight=0)  # Botão
            
            # Título do card
            title_label = ctk.CTkLabel(
                card, 
                text=title, 
                font=ctk.CTkFont(size=18, weight="bold")
            )
            title_label.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
            
            # Descrição do card
            desc_label = ctk.CTkLabel(
                card, 
                text=description, 
                font=ctk.CTkFont(size=14),
                wraplength=250
            )
            desc_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
            
            # Botão do card
            button = ctk.CTkButton(card, text="Abrir", command=command)
            button.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
            
            # Tornar todo o card clicável
            card.bind("<Button-1>", lambda event: command() if command else None)
            title_label.bind("<Button-1>", lambda event: command() if command else None)
            desc_label.bind("<Button-1>", lambda event: command() if command else None)
        
        # Criar cards para cada funcionalidade
        create_card(
            0, 0,
            "Processamento de PDFs",
            "Processar arquivos PDF de holerites, identificar funcionários e separar páginas.",
            command=self.app.show_pdf_processor_window
        )
        
        create_card(
            0, 1,
            "Gerenciar Funcionários",
            "Cadastrar, editar e remover funcionários, bem como gerenciar seus documentos.",
            command=self.app.show_employee_window
        )
        
        create_card(
            0, 2,
            "Envio de E-mails",
            "Enviar documentos por e-mail para os funcionários, com templates personalizados.",
            command=self.app.show_email_window
        )
        
        create_card(
            1, 0,
            "Bancos de Dados",
            "Gerenciar bancos de dados personalizados para diferentes tipos de documentos.",
            command=self.app.show_database_window
        )
        
        create_card(
            1, 1,
            "Relatórios",
            "Gerar relatórios de processamento e envio de documentos.",
            command=lambda: logger.info("Função de relatórios ainda não implementada")
        )
        
        create_card(
            1, 2,
            "Configurações",
            "Configurar opções da aplicação, aparência e preferências de processamento.",
            command=lambda: logger.info("Função de configurações ainda não implementada")
        )
    
    def _create_footer(self):
        """Cria o rodapé da janela."""
        footer_frame = ctk.CTkFrame(self, corner_radius=0)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        
        # Versão da aplicação
        version_label = ctk.CTkLabel(
            footer_frame, 
            text="Versão 1.2.0", 
            font=ctk.CTkFont(size=12)
        )
        version_label.pack(side="right", padx=10, pady=5)
        
        # Informações adicionais
        info_label = ctk.CTkLabel(
            footer_frame, 
            text="LGPD/GDPR Compliant", 
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(side="left", padx=10, pady=5) 