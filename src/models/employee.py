"""
Modelo de dados para funcionários.
Este módulo define a classe Employee para representar funcionários e suas operações.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
import re


@dataclass
class Employee:
    """Classe que representa um funcionário."""
    
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    department: str = ""
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validações após inicialização."""
        self.name = self.name.strip().upper()
        self.email = self.email.strip().lower()
        self.department = self.department.strip()
    
    @property
    def is_valid(self) -> bool:
        """Verifica se o funcionário é válido."""
        return bool(self.name) and self._is_valid_email()
    
    def _is_valid_email(self) -> bool:
        """Valida o formato do e-mail."""
        if not self.email:
            return True  # Email é opcional
        
        # Padrão básico de validação de email
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, self.email))
    
    def to_dict(self) -> Dict:
        """Converte o funcionário para um dicionário."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Employee':
        """Cria um funcionário a partir de um dicionário."""
        # Converter strings de data para objetos datetime
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            email=data.get("email", ""),
            department=data.get("department", ""),
            active=data.get("active", True),
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
        )


@dataclass
class Document:
    """Classe que representa um documento de funcionário."""
    
    id: Optional[int] = None
    employee_id: int = 0
    document_type: str = ""
    file_path: str = ""
    uploaded_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Converte o documento para um dicionário."""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "document_type": self.document_type,
            "file_path": self.file_path,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Document':
        """Cria um documento a partir de um dicionário."""
        # Converter string de data para objeto datetime
        uploaded_at = data.get("uploaded_at")
        if uploaded_at and isinstance(uploaded_at, str):
            uploaded_at = datetime.fromisoformat(uploaded_at)
        
        return cls(
            id=data.get("id"),
            employee_id=data.get("employee_id", 0),
            document_type=data.get("document_type", ""),
            file_path=data.get("file_path", ""),
            uploaded_at=uploaded_at or datetime.now()
        )


class EmployeeDatabase:
    """Gerencia a lista de funcionários e lê/escreve de/para arquivo."""
    
    def __init__(self, filename: str = "all_employee.txt"):
        """
        Inicializa o banco de dados de funcionários.
        
        Args:
            filename (str): Nome do arquivo com a lista de funcionários
        """
        self.filename = filename
        self.employees = []
        self.load_from_file()
    
    def load_from_file(self) -> None:
        """Carrega a lista de funcionários do arquivo."""
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            self.employees = []
            for line in lines:
                name = line.strip()
                if name:
                    self.employees.append(Employee(name=name))
                    
        except FileNotFoundError:
            self.employees = []
    
    def save_to_file(self) -> None:
        """Salva a lista de funcionários no arquivo."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                for employee in sorted(self.employees, key=lambda e: e.name):
                    file.write(f"{employee.name}\n")
        except Exception as e:
            raise IOError(f"Erro ao salvar arquivo de funcionários: {e}")
    
    def add_employee(self, employee: Employee) -> None:
        """
        Adiciona um funcionário à lista.
        
        Args:
            employee (Employee): O funcionário a ser adicionado
        """
        # Verificar se já existe um funcionário com o mesmo nome
        if any(e.name == employee.name for e in self.employees):
            return
        
        self.employees.append(employee)
        self.save_to_file()
    
    def remove_employee(self, name: str) -> bool:
        """
        Remove um funcionário da lista.
        
        Args:
            name (str): Nome do funcionário a ser removido
            
        Returns:
            bool: True se o funcionário foi removido
        """
        name = name.strip().upper()
        initial_count = len(self.employees)
        self.employees = [e for e in self.employees if e.name != name]
        
        if len(self.employees) < initial_count:
            self.save_to_file()
            return True
        return False
    
    def update_employee(self, old_name: str, new_employee: Employee) -> bool:
        """
        Atualiza um funcionário na lista.
        
        Args:
            old_name (str): Nome atual do funcionário
            new_employee (Employee): Novos dados do funcionário
            
        Returns:
            bool: True se o funcionário foi atualizado
        """
        old_name = old_name.strip().upper()
        for i, employee in enumerate(self.employees):
            if employee.name == old_name:
                self.employees[i] = new_employee
                self.save_to_file()
                return True
        return False
    
    def get_employee_names(self) -> List[str]:
        """
        Obtém a lista de nomes de funcionários.
        
        Returns:
            list: Lista de nomes de funcionários
        """
        return [e.name for e in self.employees]
    
    def get_employee_by_name(self, name: str) -> Optional[Employee]:
        """
        Obtém um funcionário pelo nome.
        
        Args:
            name (str): Nome do funcionário
            
        Returns:
            Employee: O funcionário encontrado ou None
        """
        name = name.strip().upper()
        for employee in self.employees:
            if employee.name == name:
                return employee
        return None 