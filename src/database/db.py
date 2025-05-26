"""
Módulo de gerenciamento de banco de dados.
Este módulo implementa a conexão e operações com banco de dados SQLite.
Responsável por armazenar e gerenciar informações dos funcionários.
"""

import os
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

class DatabaseManager:
    """Gerencia conexões e operações de banco de dados."""
    
    def __init__(self, db_name="employees.db", db_folder="./data"):
        """
        Inicializa o gerenciador de banco de dados.
        
        Args:
            db_name (str): Nome do arquivo de banco de dados
            db_folder (str): Pasta onde o banco de dados será armazenado
        """
        # Garantir que o diretório existe
        Path(db_folder).mkdir(parents=True, exist_ok=True)
        
        self.db_path = os.path.join(db_folder, db_name)
        self.connection = None
        self.cursor = None
        self.logger = logging.getLogger("db_manager")
        
        # Inicializar o banco de dados
        self._initialize_db()
        
    def _initialize_db(self):
        """Inicializa o banco de dados e cria tabelas se não existirem."""
        try:
            self.connect()
            
            # Criar tabela de funcionários
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                department TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
            ''')
            
            # Criar tabela para armazenar bases de dados customizadas
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS custom_databases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active BOOLEAN DEFAULT 1
            )
            ''')
            
            # Criar tabela para documentos de funcionários
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employee_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                document_type TEXT,
                file_path TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
            ''')
            
            # Criar tabela para registros de logs
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                description TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_info TEXT
            )
            ''')
            
            self.connection.commit()
            self.logger.info("Banco de dados inicializado com sucesso")
            
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao inicializar o banco de dados: {e}")
        finally:
            self.disconnect()
    
    def connect(self):
        """Estabelece conexão com o banco de dados."""
        if not self.connection:
            try:
                self.connection = sqlite3.connect(self.db_path)
                self.cursor = self.connection.cursor()
                self.logger.debug(f"Conectado ao banco de dados: {self.db_path}")
            except sqlite3.Error as e:
                self.logger.error(f"Erro ao conectar ao banco de dados: {e}")
                raise
    
    def disconnect(self):
        """Fecha a conexão com o banco de dados."""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                self.cursor = None
                self.logger.debug("Desconectado do banco de dados")
            except sqlite3.Error as e:
                self.logger.error(f"Erro ao desconectar do banco de dados: {e}")
    
    def execute_query(self, query, params=None):
        """
        Executa uma query SQL.
        
        Args:
            query (str): Query SQL a ser executada
            params (tuple): Parâmetros para a query
            
        Returns:
            Resultado da query
        """
        result = None
        try:
            self.connect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            result = self.cursor.fetchall()
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao executar query: {e}")
            self.connection.rollback()
            raise
        finally:
            self.disconnect()
        return result
    
    def add_employee(self, name, email=None, department=None):
        """
        Adiciona um novo funcionário ao banco de dados.
        
        Args:
            name (str): Nome do funcionário
            email (str): Email do funcionário
            department (str): Departamento do funcionário
            
        Returns:
            int: ID do funcionário adicionado
        """
        try:
            self.connect()
            query = """
            INSERT INTO employees (name, email, department)
            VALUES (?, ?, ?)
            """
            self.cursor.execute(query, (name, email, department))
            self.connection.commit()
            employee_id = self.cursor.lastrowid
            
            # Registrar atividade
            self._log_activity("add_employee", f"Funcionário adicionado: {name}")
            
            return employee_id
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao adicionar funcionário: {e}")
            self.connection.rollback()
            raise
        finally:
            self.disconnect()
    
    def update_employee(self, employee_id, name=None, email=None, department=None):
        """
        Atualiza informações de um funcionário.
        
        Args:
            employee_id (int): ID do funcionário
            name (str): Novo nome do funcionário
            email (str): Novo email do funcionário
            department (str): Novo departamento do funcionário
            
        Returns:
            bool: True se atualizado com sucesso
        """
        try:
            self.connect()
            
            # Criar partes da query dinamicamente
            update_parts = []
            params = []
            
            if name:
                update_parts.append("name = ?")
                params.append(name)
            if email:
                update_parts.append("email = ?")
                params.append(email)
            if department:
                update_parts.append("department = ?")
                params.append(department)
                
            # Adicionar timestamp de atualização
            update_parts.append("updated_at = ?")
            params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # Adicionar ID ao final
            params.append(employee_id)
            
            if update_parts:
                query = f"""
                UPDATE employees 
                SET {', '.join(update_parts)}
                WHERE id = ?
                """
                self.cursor.execute(query, params)
                self.connection.commit()
                
                # Registrar atividade
                self._log_activity("update_employee", f"Funcionário atualizado: ID {employee_id}")
                
                return True
            return False
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao atualizar funcionário: {e}")
            self.connection.rollback()
            raise
        finally:
            self.disconnect()
    
    def delete_employee(self, employee_id):
        """
        Remove um funcionário do banco de dados (soft delete).
        
        Args:
            employee_id (int): ID do funcionário
            
        Returns:
            bool: True se removido com sucesso
        """
        try:
            self.connect()
            query = """
            UPDATE employees
            SET active = 0, updated_at = ?
            WHERE id = ?
            """
            self.cursor.execute(query, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), employee_id))
            self.connection.commit()
            
            # Registrar atividade
            self._log_activity("delete_employee", f"Funcionário desativado: ID {employee_id}")
            
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao remover funcionário: {e}")
            self.connection.rollback()
            raise
        finally:
            self.disconnect()
    
    def get_employee(self, employee_id):
        """
        Obtém informações de um funcionário.
        
        Args:
            employee_id (int): ID do funcionário
            
        Returns:
            dict: Informações do funcionário
        """
        try:
            self.connect()
            query = """
            SELECT id, name, email, department, created_at, updated_at
            FROM employees
            WHERE id = ? AND active = 1
            """
            self.cursor.execute(query, (employee_id,))
            employee = self.cursor.fetchone()
            
            if employee:
                return {
                    "id": employee[0],
                    "name": employee[1],
                    "email": employee[2],
                    "department": employee[3],
                    "created_at": employee[4],
                    "updated_at": employee[5]
                }
            return None
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao obter funcionário: {e}")
            raise
        finally:
            self.disconnect()
    
    def get_all_employees(self):
        """
        Obtém todos os funcionários ativos.
        
        Returns:
            list: Lista de funcionários
        """
        try:
            self.connect()
            query = """
            SELECT id, name, email, department
            FROM employees
            WHERE active = 1
            ORDER BY name
            """
            self.cursor.execute(query)
            employees = self.cursor.fetchall()
            
            result = []
            for emp in employees:
                result.append({
                    "id": emp[0],
                    "name": emp[1],
                    "email": emp[2],
                    "department": emp[3]
                })
            return result
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao obter lista de funcionários: {e}")
            raise
        finally:
            self.disconnect()
    
    def add_document(self, employee_id, document_type, file_path):
        """
        Adiciona um documento para um funcionário.
        
        Args:
            employee_id (int): ID do funcionário
            document_type (str): Tipo de documento
            file_path (str): Caminho do arquivo
            
        Returns:
            int: ID do documento adicionado
        """
        try:
            self.connect()
            query = """
            INSERT INTO employee_documents (employee_id, document_type, file_path)
            VALUES (?, ?, ?)
            """
            self.cursor.execute(query, (employee_id, document_type, file_path))
            self.connection.commit()
            document_id = self.cursor.lastrowid
            
            # Registrar atividade
            self._log_activity("add_document", f"Documento adicionado para funcionário ID {employee_id}")
            
            return document_id
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao adicionar documento: {e}")
            self.connection.rollback()
            raise
        finally:
            self.disconnect()
    
    def get_employee_documents(self, employee_id):
        """
        Obtém documentos de um funcionário.
        
        Args:
            employee_id (int): ID do funcionário
            
        Returns:
            list: Lista de documentos
        """
        try:
            self.connect()
            query = """
            SELECT id, document_type, file_path, uploaded_at
            FROM employee_documents
            WHERE employee_id = ?
            ORDER BY uploaded_at DESC
            """
            self.cursor.execute(query, (employee_id,))
            documents = self.cursor.fetchall()
            
            result = []
            for doc in documents:
                result.append({
                    "id": doc[0],
                    "document_type": doc[1],
                    "file_path": doc[2],
                    "uploaded_at": doc[3]
                })
            return result
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao obter documentos do funcionário: {e}")
            raise
        finally:
            self.disconnect()
    
    def create_custom_database(self, name, description=None):
        """
        Cria uma base de dados personalizada.
        
        Args:
            name (str): Nome da base de dados
            description (str): Descrição da base de dados
            
        Returns:
            int: ID da base de dados criada
        """
        try:
            self.connect()
            query = """
            INSERT INTO custom_databases (name, description)
            VALUES (?, ?)
            """
            self.cursor.execute(query, (name, description))
            self.connection.commit()
            db_id = self.cursor.lastrowid
            
            # Criar tabela para esta base de dados
            table_name = f"custom_db_{db_id}"
            self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_term TEXT NOT NULL,
                replacement TEXT,
                description TEXT,
                active BOOLEAN DEFAULT 1
            )
            ''')
            self.connection.commit()
            
            # Registrar atividade
            self._log_activity("create_database", f"Base de dados personalizada criada: {name}")
            
            return db_id
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao criar base de dados personalizada: {e}")
            self.connection.rollback()
            raise
        finally:
            self.disconnect()
    
    def get_custom_databases(self):
        """
        Obtém todas as bases de dados personalizadas.
        
        Returns:
            list: Lista de bases de dados
        """
        try:
            self.connect()
            query = """
            SELECT id, name, description, created_at
            FROM custom_databases
            WHERE active = 1
            ORDER BY name
            """
            self.cursor.execute(query)
            databases = self.cursor.fetchall()
            
            result = []
            for db in databases:
                result.append({
                    "id": db[0],
                    "name": db[1],
                    "description": db[2],
                    "created_at": db[3]
                })
            return result
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao obter bases de dados personalizadas: {e}")
            raise
        finally:
            self.disconnect()
    
    def add_custom_db_entry(self, db_id, search_term, replacement=None, description=None):
        """
        Adiciona uma entrada em uma base de dados personalizada.
        
        Args:
            db_id (int): ID da base de dados
            search_term (str): Termo de busca
            replacement (str): Termo de substituição
            description (str): Descrição adicional
            
        Returns:
            int: ID da entrada adicionada
        """
        try:
            self.connect()
            table_name = f"custom_db_{db_id}"
            query = f"""
            INSERT INTO {table_name} (search_term, replacement, description)
            VALUES (?, ?, ?)
            """
            self.cursor.execute(query, (search_term, replacement, description))
            self.connection.commit()
            entry_id = self.cursor.lastrowid
            
            # Registrar atividade
            self._log_activity("add_db_entry", f"Entrada adicionada à base de dados ID {db_id}")
            
            return entry_id
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao adicionar entrada na base de dados: {e}")
            self.connection.rollback()
            raise
        finally:
            self.disconnect()
    
    def get_custom_db_entries(self, db_id):
        """
        Obtém todas as entradas de uma base de dados personalizada.
        
        Args:
            db_id (int): ID da base de dados
            
        Returns:
            list: Lista de entradas
        """
        try:
            self.connect()
            table_name = f"custom_db_{db_id}"
            query = f"""
            SELECT id, search_term, replacement, description
            FROM {table_name}
            WHERE active = 1
            ORDER BY search_term
            """
            self.cursor.execute(query)
            entries = self.cursor.fetchall()
            
            result = []
            for entry in entries:
                result.append({
                    "id": entry[0],
                    "search_term": entry[1],
                    "replacement": entry[2],
                    "description": entry[3]
                })
            return result
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao obter entradas da base de dados: {e}")
            raise
        finally:
            self.disconnect()
    
    def _log_activity(self, action, description, user_info=None):
        """
        Registra uma atividade no log.
        
        Args:
            action (str): Ação realizada
            description (str): Descrição da ação
            user_info (str): Informações do usuário
        """
        try:
            query = """
            INSERT INTO activity_logs (action, description, user_info)
            VALUES (?, ?, ?)
            """
            self.cursor.execute(query, (action, description, user_info))
            self.connection.commit()
        except sqlite3.Error as e:
            self.logger.error(f"Erro ao registrar atividade: {e}")
            # Não causar falha na operação principal 