"""
Módulo de configurações da aplicação.
Este módulo gerencia as configurações persistentes da aplicação.
"""

import os
import json
import logging
from typing import Any, Dict, Optional
from pathlib import Path


class AppSettings:
    """Gerencia as configurações da aplicação."""
    
    def __init__(self, settings_file: str = "settings.json"):
        """
        Inicializa o gerenciador de configurações.
        
        Args:
            settings_file (str): Caminho para o arquivo de configurações
        """
        self.settings_file = Path(settings_file)
        self.logger = logging.getLogger("settings")
        
        # Garantir que o diretório do arquivo existe
        os.makedirs(self.settings_file.parent, exist_ok=True)
        
        # Carregar configurações existentes ou criar padrões
        self.settings = self._load()
        
        # Definir valores padrão se necessário
        self._set_defaults()
    
    def _load(self) -> Dict[str, Any]:
        """
        Carrega as configurações do arquivo.
        
        Returns:
            dict: Configurações carregadas
        """
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as file:
                    return json.load(file)
            else:
                self.logger.info(f"Arquivo de configurações não encontrado: {self.settings_file}")
                return {}
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
            return {}
    
    def save(self) -> bool:
        """
        Salva as configurações no arquivo.
        
        Returns:
            bool: True se as configurações foram salvas com sucesso
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as file:
                json.dump(self.settings, file, indent=4)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
            return False
    
    def _set_defaults(self) -> None:
        """Define valores padrão para configurações essenciais."""
        defaults = {
            "appearance": {
                "theme": "system",  # sistema, escuro, claro
                "font_size": "medium",  # pequeno, médio, grande
                "accent_color": "blue"  # azul, verde, roxo
            },
            "processing": {
                "ocr_threshold": 50,
                "fuzzy_match_threshold": 75,
                "backup_originals": True
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "use_tls": True,
                "auto_send": False,
                "include_disclaimer": True
            },
            "paths": {
                "last_pdf_dir": "",
                "last_output_dir": "",
                "custom_databases": []
            }
        }
        
        # Adicionar configurações padrão que não existem
        for section, options in defaults.items():
            if section not in self.settings:
                self.settings[section] = {}
            
            for key, value in options.items():
                if key not in self.settings[section]:
                    self.settings[section][key] = value
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Obtém uma configuração.
        
        Args:
            section (str): Seção da configuração
            key (str): Chave da configuração
            default (Any): Valor padrão se não existir
            
        Returns:
            Any: Valor da configuração
        """
        try:
            return self.settings.get(section, {}).get(key, default)
        except Exception:
            return default
    
    def set(self, section: str, key: str, value: Any) -> None:
        """
        Define uma configuração.
        
        Args:
            section (str): Seção da configuração
            key (str): Chave da configuração
            value (Any): Valor da configuração
        """
        if section not in self.settings:
            self.settings[section] = {}
        
        self.settings[section][key] = value
    
    def get_appearance(self) -> Dict[str, Any]:
        """
        Obtém as configurações de aparência.
        
        Returns:
            dict: Configurações de aparência
        """
        return self.settings.get("appearance", {})
    
    def get_processing(self) -> Dict[str, Any]:
        """
        Obtém as configurações de processamento.
        
        Returns:
            dict: Configurações de processamento
        """
        return self.settings.get("processing", {})
    
    def get_email(self) -> Dict[str, Any]:
        """
        Obtém as configurações de email.
        
        Returns:
            dict: Configurações de email
        """
        return self.settings.get("email", {})
    
    def get_paths(self) -> Dict[str, Any]:
        """
        Obtém as configurações de caminhos.
        
        Returns:
            dict: Configurações de caminhos
        """
        return self.settings.get("paths", {})
    
    def update_last_pdf_dir(self, path: str) -> None:
        """
        Atualiza o último diretório de PDF usado.
        
        Args:
            path (str): Caminho do diretório
        """
        self.set("paths", "last_pdf_dir", path)
    
    def update_last_output_dir(self, path: str) -> None:
        """
        Atualiza o último diretório de saída usado.
        
        Args:
            path (str): Caminho do diretório
        """
        self.set("paths", "last_output_dir", path)
    
    def add_custom_database(self, db_path: str) -> None:
        """
        Adiciona um caminho de base de dados personalizada.
        
        Args:
            db_path (str): Caminho da base de dados
        """
        custom_dbs = self.get("paths", "custom_databases", [])
        if db_path not in custom_dbs:
            custom_dbs.append(db_path)
            self.set("paths", "custom_databases", custom_dbs) 