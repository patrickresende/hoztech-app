"""
Módulo da janela de processamento de PDFs.
Este módulo implementa a interface para processamento de PDFs.
"""

import os
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Callable, Any, Optional
import customtkinter as ctk
from tkinter import filedialog

# Módulos internos
from src.views.base_window import BaseWindow
from src.utils.pdf_processor import PDFProcessor
from src.models.employee import EmployeeDatabase

logger = logging.getLogger("pdf_processor_window")


class PDFProcessorWindow(BaseWindow):
    """Janela de processamento de PDFs."""
    
    def __init__(self, master, app):
        """
        Inicializa a janela de processamento de PDFs.
        
        Args:
            master: Widget pai
            app: Instância da aplicação principal
        """
        super().__init__(master, app, title="Processamento de PDFs")
        
        # Configurar frame de conteúdo
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(1, weight=1)
        
        # Variáveis de controle
        self.pdf_path = ctk.StringVar(value="")
        self.output_dir = ctk.StringVar(value="")
        self.year = ctk.StringVar(value=str(datetime.now().year))
        self.month = ctk.StringVar(value=str(datetime.now().month).zfill(2))
        self.use_proximity = ctk.BooleanVar(value=True)
        self.use_synonyms = ctk.BooleanVar(value=False)
        self.selected_db = ctk.StringVar(value="all_employee.txt")
        self.is_processing = False
        self.cancel_requested = False
        
        # Inicializar componentes
        self._create_left_panel()
        self._create_right_panel()
        
        # Carregar bancos de dados disponíveis
        self._load_databases()
    
    def _create_left_panel(self):
        """Cria o painel esquerdo com formulário de configuração."""
        left_panel = ctk.CTkFrame(self.content_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=0)
        
        # Configuração do panel
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_columnconfigure(1, weight=3)
        
        # Título
        title_label = ctk.CTkLabel(
            left_panel, 
            text="Configurações de Processamento", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 20))
        
        # PDF de entrada
        pdf_label = ctk.CTkLabel(left_panel, text="Arquivo PDF:")
        pdf_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        pdf_frame = ctk.CTkFrame(left_panel)
        pdf_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        pdf_frame.grid_columnconfigure(0, weight=1)
        
        pdf_entry = ctk.CTkEntry(pdf_frame, textvariable=self.pdf_path)
        pdf_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        pdf_button = ctk.CTkButton(
            pdf_frame, 
            text="Selecionar", 
            command=self._select_pdf,
            width=100
        )
        pdf_button.grid(row=0, column=1)
        
        # Diretório de saída
        output_label = ctk.CTkLabel(left_panel, text="Diretório de Saída:")
        output_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        output_frame = ctk.CTkFrame(left_panel)
        output_frame.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        output_frame.grid_columnconfigure(0, weight=1)
        
        output_entry = ctk.CTkEntry(output_frame, textvariable=self.output_dir)
        output_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        output_button = ctk.CTkButton(
            output_frame, 
            text="Selecionar", 
            command=self._select_output_dir,
            width=100
        )
        output_button.grid(row=0, column=1)
        
        # Ano e mês
        date_frame = ctk.CTkFrame(left_panel)
        date_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        year_label = ctk.CTkLabel(date_frame, text="Ano:")
        year_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        year_entry = ctk.CTkEntry(date_frame, textvariable=self.year, width=80)
        year_entry.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        month_label = ctk.CTkLabel(date_frame, text="Mês:")
        month_label.grid(row=0, column=2, sticky="w", padx=10, pady=5)
        
        month_entry = ctk.CTkEntry(date_frame, textvariable=self.month, width=80)
        month_entry.grid(row=0, column=3, sticky="w", padx=10, pady=5)
        
        # Seleção de banco de dados
        db_label = ctk.CTkLabel(left_panel, text="Banco de Dados:")
        db_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        
        db_frame = ctk.CTkFrame(left_panel)
        db_frame.grid(row=4, column=1, sticky="ew", padx=10, pady=5)
        db_frame.grid_columnconfigure(0, weight=1)
        
        self.db_combobox = ctk.CTkComboBox(
            db_frame, 
            values=["all_employee.txt"],
            variable=self.selected_db,
            width=200
        )
        self.db_combobox.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        db_new_button = ctk.CTkButton(
            db_frame, 
            text="Novo", 
            command=self._create_new_database,
            width=60
        )
        db_new_button.grid(row=0, column=1, padx=(0, 5))
        
        db_edit_button = ctk.CTkButton(
            db_frame, 
            text="Editar", 
            command=lambda: self.app.show_database_window(),
            width=60
        )
        db_edit_button.grid(row=0, column=2)
        
        # Opções de processamento
        options_frame = ctk.CTkFrame(left_panel)
        options_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        options_label = ctk.CTkLabel(
            options_frame, 
            text="Opções de Processamento", 
            font=ctk.CTkFont(weight="bold")
        )
        options_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        proximity_check = ctk.CTkCheckBox(
            options_frame, 
            text="Usar busca por proximidade", 
            variable=self.use_proximity
        )
        proximity_check.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        synonym_check = ctk.CTkCheckBox(
            options_frame, 
            text="Usar busca por sinônimos", 
            variable=self.use_synonyms
        )
        synonym_check.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # Botões de ação
        button_frame = ctk.CTkFrame(left_panel)
        button_frame.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=(20, 10))
        
        self.process_button = ctk.CTkButton(
            button_frame, 
            text="Iniciar Processamento", 
            command=self._start_processing
        )
        self.process_button.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        self.cancel_button = ctk.CTkButton(
            button_frame, 
            text="Cancelar", 
            command=self._cancel_processing,
            state="disabled"
        )
        self.cancel_button.pack(side="right", padx=10, pady=10, fill="x", expand=True)
    
    def _create_right_panel(self):
        """Cria o painel direito com logs e progresso."""
        right_panel = ctk.CTkFrame(self.content_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=0)
        
        # Configuração do panel
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            right_panel, 
            text="Progresso e Resultados", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 20))
        
        # Barra de progresso
        progress_frame = ctk.CTkFrame(right_panel)
        progress_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="0%")
        self.progress_label.grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10))
        self.progress_bar.set(0)
        
        # Área de log
        log_frame = ctk.CTkFrame(right_panel)
        log_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)
        
        log_label = ctk.CTkLabel(
            log_frame, 
            text="Log de Processamento", 
            font=ctk.CTkFont(weight="bold")
        )
        log_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.log_text = ctk.CTkTextbox(log_frame, height=300, wrap="word")
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Resultados do processamento
        results_frame = ctk.CTkFrame(right_panel)
        results_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        results_frame.grid_columnconfigure(0, weight=1)
        
        results_label = ctk.CTkLabel(
            results_frame, 
            text="Resultados", 
            font=ctk.CTkFont(weight="bold")
        )
        results_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Estatísticas de processamento
        self.stats_frame = ctk.CTkFrame(results_frame)
        self.stats_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Configuração inicial das estatísticas (serão atualizadas durante processamento)
        self._update_stats({
            "total_pages": 0,
            "identified_pages": 0,
            "unidentified_pages": 0,
            "employees_found": []
        })
    
    def _load_databases(self):
        """Carrega a lista de bancos de dados disponíveis."""
        # Banco de dados padrão sempre disponível
        databases = ["all_employee.txt"]
        
        # Adicionar bases de dados personalizadas das configurações
        custom_dbs = self.app.settings.get("paths", "custom_databases", [])
        for db in custom_dbs:
            if os.path.exists(db) and db not in databases:
                databases.append(db)
        
        # Atualizar combobox
        self.db_combobox.configure(values=databases)
        
        # Selecionar último banco de dados usado ou o padrão
        last_db = self.app.settings.get("processing", "last_database", "all_employee.txt")
        if last_db in databases:
            self.selected_db.set(last_db)
        else:
            self.selected_db.set(databases[0])
    
    def _select_pdf(self):
        """Abre diálogo para selecionar arquivo PDF."""
        last_dir = self.app.settings.get("paths", "last_pdf_dir", os.path.expanduser("~"))
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo PDF",
            filetypes=[("Arquivos PDF", "*.pdf")],
            initialdir=last_dir
        )
        
        if file_path:
            self.pdf_path.set(file_path)
            self.app.settings.update_last_pdf_dir(os.path.dirname(file_path))
            self._log_message(f"Arquivo selecionado: {file_path}")
    
    def _select_output_dir(self):
        """Abre diálogo para selecionar diretório de saída."""
        last_dir = self.app.settings.get("paths", "last_output_dir", os.path.expanduser("~"))
        dir_path = filedialog.askdirectory(
            title="Selecionar diretório de saída",
            initialdir=last_dir
        )
        
        if dir_path:
            self.output_dir.set(dir_path)
            self.app.settings.update_last_output_dir(dir_path)
            self._log_message(f"Diretório de saída selecionado: {dir_path}")
    
    def _create_new_database(self):
        """Abre diálogo para criar novo banco de dados."""
        # Esta função apenas redireciona para a janela de bancos de dados
        self.app.show_database_window()
    
    def _start_processing(self):
        """Inicia o processamento do PDF."""
        # Validar entradas
        if not self._validate_inputs():
            return
        
        # Atualizar interface para processamento
        self._set_processing_state(True)
        self._log_message("Iniciando processamento...")
        
        # Salvar configurações utilizadas
        self.app.settings.set("processing", "last_database", self.selected_db.get())
        self.app.settings.save()
        
        # Executar processamento em thread separada
        self.cancel_requested = False
        thread = threading.Thread(target=self._process_pdf)
        thread.daemon = True
        thread.start()
    
    def _process_pdf(self):
        """Executa o processamento do PDF em thread separada."""
        try:
            # Carregar banco de dados de funcionários
            employee_db = EmployeeDatabase(self.selected_db.get())
            employee_names = employee_db.get_employee_names()
            
            if not employee_names:
                self._log_message("Erro: Banco de dados de funcionários vazio!", is_error=True)
                self._set_processing_state(False)
                return
            
            # Criar instância do processador
            processor = PDFProcessor(
                output_dir=self.output_dir.get(),
                logs_dir=os.path.join(self.app.settings.get("paths", "logs_dir", "./logs"))
            )
            
            # Processar o PDF
            result = processor.process_pdf(
                pdf_path=self.pdf_path.get(),
                year=self.year.get(),
                month=self.month.get(),
                employee_names=employee_names,
                progress_callback=self._update_progress,
                cancel_callback=lambda: self.cancel_requested,
                use_synonyms=self.use_synonyms.get(),
                proximity_search=self.use_proximity.get()
            )
            
            # Atualizar resultados
            self._update_stats(result)
            
            if self.cancel_requested:
                self._log_message("Processamento cancelado pelo usuário.")
            else:
                self._log_message("Processamento concluído com sucesso!")
                
                message = (
                    f"Total de páginas: {result['total_pages']}\n"
                    f"Páginas identificadas: {result['identified_pages']}\n"
                    f"Páginas não identificadas: {result['unidentified_pages']}\n"
                    f"Funcionários encontrados: {len(result['employees_found'])}"
                )
                self._show_success_message("Processamento Concluído", message)
        
        except Exception as e:
            self._log_message(f"Erro durante o processamento: {str(e)}", is_error=True)
            logger.exception("Erro durante o processamento do PDF")
        
        finally:
            # Restaurar interface
            self._set_processing_state(False)
    
    def _update_progress(self, current, total):
        """
        Atualiza o progresso na interface.
        
        Args:
            current (int): Página atual
            total (int): Total de páginas
        """
        # Calcular porcentagem
        percentage = (current / total) if total > 0 else 0
        
        # Atualizar barra de progresso
        self.progress_bar.set(percentage)
        self.progress_label.configure(text=f"{int(percentage * 100)}%")
        
        # Atualizar log
        self._log_message(f"Processando página {current} de {total}...")
    
    def _update_stats(self, stats):
        """
        Atualiza as estatísticas na interface.
        
        Args:
            stats (dict): Estatísticas de processamento
        """
        # Limpar estatísticas anteriores
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Adicionar novas estatísticas
        ctk.CTkLabel(self.stats_frame, text="Total de páginas:").grid(
            row=0, column=0, sticky="w", padx=10, pady=2
        )
        ctk.CTkLabel(self.stats_frame, text=str(stats.get("total_pages", 0))).grid(
            row=0, column=1, sticky="w", padx=10, pady=2
        )
        
        ctk.CTkLabel(self.stats_frame, text="Páginas identificadas:").grid(
            row=1, column=0, sticky="w", padx=10, pady=2
        )
        ctk.CTkLabel(self.stats_frame, text=str(stats.get("identified_pages", 0))).grid(
            row=1, column=1, sticky="w", padx=10, pady=2
        )
        
        ctk.CTkLabel(self.stats_frame, text="Páginas não identificadas:").grid(
            row=2, column=0, sticky="w", padx=10, pady=2
        )
        ctk.CTkLabel(self.stats_frame, text=str(stats.get("unidentified_pages", 0))).grid(
            row=2, column=1, sticky="w", padx=10, pady=2
        )
        
        ctk.CTkLabel(self.stats_frame, text="Funcionários encontrados:").grid(
            row=3, column=0, sticky="w", padx=10, pady=2
        )
        ctk.CTkLabel(self.stats_frame, text=str(len(stats.get("employees_found", [])))).grid(
            row=3, column=1, sticky="w", padx=10, pady=2
        )
    
    def _log_message(self, message, is_error=False):
        """
        Adiciona uma mensagem ao log na interface.
        
        Args:
            message (str): Mensagem a ser adicionada
            is_error (bool): Se é uma mensagem de erro
        """
        # Adicionar timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # Adicionar ao log
        self.log_text.insert("end", log_entry)
        
        # Colorir mensagem de erro
        if is_error:
            # O CTkTextbox não suporta tags como o Tkinter nativo, então não podemos colorir o texto
            pass
        
        # Rolar para o final
        self.log_text.see("end")
        
        # Atualizar também a barra de status
        self.update_status(message, is_error)
    
    def _set_processing_state(self, is_processing):
        """
        Atualiza a interface para o estado de processamento.
        
        Args:
            is_processing (bool): Se está processando
        """
        self.is_processing = is_processing
        
        if is_processing:
            # Desabilitar campos e botões durante processamento
            self.process_button.configure(state="disabled")
            self.cancel_button.configure(state="normal")
            self.db_combobox.configure(state="disabled")
        else:
            # Habilitar campos e botões após processamento
            self.process_button.configure(state="normal")
            self.cancel_button.configure(state="disabled")
            self.db_combobox.configure(state="normal")
    
    def _cancel_processing(self):
        """Cancela o processamento em andamento."""
        if self.is_processing:
            self.cancel_requested = True
            self._log_message("Solicitação de cancelamento enviada. Aguardando finalização...")
            self.cancel_button.configure(state="disabled")
    
    def _validate_inputs(self):
        """
        Valida as entradas do usuário.
        
        Returns:
            bool: True se as entradas são válidas
        """
        # Validar PDF
        if not self.pdf_path.get():
            self._log_message("Erro: Selecione um arquivo PDF.", is_error=True)
            return False
        
        if not os.path.exists(self.pdf_path.get()):
            self._log_message(f"Erro: Arquivo não encontrado: {self.pdf_path.get()}", is_error=True)
            return False
        
        # Validar diretório de saída
        if not self.output_dir.get():
            self._log_message("Erro: Selecione um diretório de saída.", is_error=True)
            return False
        
        # Criar diretório se não existir
        try:
            os.makedirs(self.output_dir.get(), exist_ok=True)
        except Exception as e:
            self._log_message(f"Erro ao criar diretório de saída: {str(e)}", is_error=True)
            return False
        
        # Validar ano e mês
        try:
            year = int(self.year.get())
            month = int(self.month.get())
            
            if not (1900 <= year <= 2100):
                self._log_message("Erro: Ano inválido. Use um ano entre 1900 e 2100.", is_error=True)
                return False
            
            if not (1 <= month <= 12):
                self._log_message("Erro: Mês inválido. Use um mês entre 1 e 12.", is_error=True)
                return False
        except ValueError:
            self._log_message("Erro: Ano e mês devem ser números.", is_error=True)
            return False
        
        # Validar banco de dados
        if not os.path.exists(self.selected_db.get()):
            self._log_message(f"Erro: Banco de dados não encontrado: {self.selected_db.get()}", is_error=True)
            return False
        
        return True
    
    def _show_success_message(self, title, message):
        """
        Mostra uma mensagem de sucesso.
        
        Args:
            title (str): Título da mensagem
            message (str): Conteúdo da mensagem
        """
        # Usar método da classe pai para mostrar mensagem
        self.show_message(title, message) 