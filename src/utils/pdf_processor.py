"""
Módulo de processamento de PDFs.
Este módulo é responsável pela extração, identificação e separação de páginas de PDFs.
Implementa funcionalidades de OCR e reconhecimento de padrões para identificar funcionários.
"""

import os
import logging
import shutil
from pathlib import Path
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from rapidfuzz import process, fuzz
from datetime import datetime

# Configurações
OCR_THRESHOLD = 50  # Mínimo de texto para considerar o OCR necessário
FUZZY_MATCH_THRESHOLD = 75  # Limiar para considerar uma correspondência válida
MAX_FUZZY_CANDIDATES = 5  # Número máximo de candidatos para correspondência


class PDFProcessor:
    """Classe para processamento de PDFs de contracheques e outros documentos."""
    
    def __init__(self, output_dir="./output", logs_dir="./logs"):
        """
        Inicializa o processador de PDFs.
        
        Args:
            output_dir (str): Diretório para salvar os arquivos processados
            logs_dir (str): Diretório para salvar logs de processamento
        """
        # Garantir que os diretórios existam
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(logs_dir).mkdir(parents=True, exist_ok=True)
        
        self.output_dir = output_dir
        self.logs_dir = logs_dir
        self.logger = logging.getLogger("pdf_processor")
        
        # Configurar logger de nomes não identificados
        self.unmatched_log_path = os.path.join(logs_dir, "unmatched_names.log")
        
    def process_pdf(self, pdf_path, year, month, employee_names, 
                    progress_callback=None, cancel_callback=None, 
                    use_synonyms=False, proximity_search=False):
        """
        Processa um arquivo PDF, identificando e separando páginas por funcionário.
        
        Args:
            pdf_path (str): Caminho do arquivo PDF a ser processado
            year (str): Ano para nomenclatura dos arquivos
            month (str): Mês para nomenclatura dos arquivos
            employee_names (list): Lista de nomes de funcionários para identificação
            progress_callback (callable): Função para atualizar o progresso
            cancel_callback (callable): Função para verificar cancelamento
            use_synonyms (bool): Usar busca por sinônimos
            proximity_search (bool): Usar busca por proximidade
            
        Returns:
            dict: Estatísticas de processamento
        """
        if not os.path.exists(pdf_path):
            self.logger.error(f"Arquivo não encontrado: {pdf_path}")
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
        
        # Estatísticas de processamento
        stats = {
            "total_pages": 0,
            "identified_pages": 0,
            "unidentified_pages": 0,
            "employees_found": set(),
            "errors": []
        }
        
        try:
            # Abrir o documento PDF
            doc = fitz.open(pdf_path)
            stats["total_pages"] = len(doc)
            
            # Processar cada página
            for page_num, page in enumerate(doc):
                # Verificar cancelamento
                if cancel_callback and cancel_callback():
                    self.logger.info("Processamento cancelado pelo usuário")
                    break
                
                # Atualizar progresso
                if progress_callback:
                    progress_callback(page_num + 1, len(doc))
                
                # Extrair texto da página
                text = self._extract_text_from_page(page)
                
                # Se o texto for insuficiente, tentar OCR
                if len(text.strip()) < OCR_THRESHOLD:
                    self.logger.info(f"Texto insuficiente na página {page_num+1}, tentando OCR")
                    text = self._extract_text_with_ocr(page)
                
                # Identificar funcionário
                employee_name = self._identify_employee(
                    text, 
                    employee_names, 
                    use_synonyms=use_synonyms, 
                    proximity_search=proximity_search
                )
                
                # Processar resultado da identificação
                if employee_name and employee_name != "DESCONHECIDO":
                    stats["identified_pages"] += 1
                    stats["employees_found"].add(employee_name)
                    
                    # Salvar página para o funcionário
                    self._save_page_for_employee(doc, page_num, employee_name, year, month)
                else:
                    stats["unidentified_pages"] += 1
                    self._log_unmatched_page(page_num + 1, text)
            
            # Converter set para lista para serialização
            stats["employees_found"] = list(stats["employees_found"])
            
            self.logger.info(f"Processamento concluído: {stats['identified_pages']} páginas identificadas, "
                             f"{stats['unidentified_pages']} não identificadas")
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao processar PDF: {e}", exc_info=True)
            stats["errors"].append(str(e))
            raise
        finally:
            # Fechar o documento
            if 'doc' in locals():
                doc.close()
    
    def _extract_text_from_page(self, page):
        """
        Extrai texto de uma página de PDF.
        
        Args:
            page: Objeto de página do PyMuPDF
            
        Returns:
            str: Texto extraído
        """
        try:
            text = page.get_text("text")
            return text
        except Exception as e:
            self.logger.error(f"Erro ao extrair texto: {e}")
            return ""
    
    def _extract_text_with_ocr(self, page):
        """
        Extrai texto usando OCR de uma página de PDF.
        
        Args:
            page: Objeto de página do PyMuPDF
            
        Returns:
            str: Texto extraído via OCR
        """
        try:
            # Renderizar página como imagem
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # 2x para melhor qualidade
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Aplicar OCR
            text = pytesseract.image_to_string(img, lang="por")
            return text
        except Exception as e:
            self.logger.error(f"Erro ao realizar OCR: {e}")
            return ""
    
    def _identify_employee(self, text, employee_names, use_synonyms=False, proximity_search=False):
        """
        Identifica o funcionário com base no texto.
        
        Args:
            text (str): Texto extraído da página
            employee_names (list): Lista de nomes de funcionários
            use_synonyms (bool): Usar busca por sinônimos
            proximity_search (bool): Usar busca por proximidade
            
        Returns:
            str: Nome do funcionário identificado ou "DESCONHECIDO"
        """
        # Verificar correspondência exata primeiro
        for name in employee_names:
            if name.upper() in text.upper():
                self.logger.debug(f"Correspondência exata encontrada: {name}")
                return name
        
        # Se não encontrou correspondência exata, tentar fuzzy matching
        if proximity_search:
            matches = process.extract(
                text, 
                employee_names, 
                scorer=fuzz.token_set_ratio,  # Melhor para textos longos
                limit=MAX_FUZZY_CANDIDATES
            )
            
            # Verificar se há alguma correspondência com pontuação acima do limiar
            for match, score, _ in matches:
                if score >= FUZZY_MATCH_THRESHOLD:
                    self.logger.debug(f"Correspondência fuzzy encontrada: {match} (score: {score})")
                    return match
        
        # Se não encontrou correspondência, registrar e retornar desconhecido
        self.logger.warning(f"Nenhuma correspondência encontrada para o texto")
        return "DESCONHECIDO"
    
    def _save_page_for_employee(self, doc, page_num, employee_name, year, month):
        """
        Salva uma página para um funcionário específico.
        
        Args:
            doc: Documento PDF
            page_num (int): Número da página
            employee_name (str): Nome do funcionário
            year (str): Ano para nomenclatura
            month (str): Mês para nomenclatura
        """
        try:
            # Criar diretório para o funcionário se não existir
            employee_dir = os.path.join(self.output_dir, employee_name)
            Path(employee_dir).mkdir(parents=True, exist_ok=True)
            
            # Nome do arquivo de saída
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_filename = f"{employee_name} - Recibo - {month}-{year}_{timestamp}.pdf"
            output_path = os.path.join(employee_dir, output_filename)
            
            # Criar novo PDF com apenas esta página
            new_doc = fitz.open()
            new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            new_doc.save(output_path)
            new_doc.close()
            
            self.logger.info(f"Página salva para {employee_name}: {output_path}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar página para {employee_name}: {e}")
            raise
    
    def process_multi_page_document(self, doc, page_ranges, employee_name, year, month):
        """
        Processa um documento com múltiplas páginas para um mesmo funcionário.
        
        Args:
            doc: Documento PDF
            page_ranges (list): Lista de tuplas (início, fim) para as páginas
            employee_name (str): Nome do funcionário
            year (str): Ano para nomenclatura
            month (str): Mês para nomenclatura
            
        Returns:
            str: Caminho do arquivo salvo
        """
        try:
            # Criar diretório para o funcionário se não existir
            employee_dir = os.path.join(self.output_dir, employee_name)
            Path(employee_dir).mkdir(parents=True, exist_ok=True)
            
            # Nome do arquivo de saída
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            output_filename = f"{employee_name} - Recibo - {month}-{year}_{timestamp}.pdf"
            output_path = os.path.join(employee_dir, output_filename)
            
            # Criar novo PDF com as páginas especificadas
            new_doc = fitz.open()
            
            for start_page, end_page in page_ranges:
                # Garantir que os índices estão dentro dos limites
                start_page = max(0, start_page)
                end_page = min(len(doc) - 1, end_page)
                
                # Adicionar páginas ao novo documento
                new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)
            
            # Salvar o novo documento
            new_doc.save(output_path)
            new_doc.close()
            
            self.logger.info(f"Documento multi-página salvo para {employee_name}: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"Erro ao processar documento multi-página para {employee_name}: {e}")
            raise
    
    def _log_unmatched_page(self, page_num, text):
        """
        Registra informações sobre páginas não identificadas.
        
        Args:
            page_num (int): Número da página
            text (str): Texto extraído da página
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(self.unmatched_log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"=== Página não identificada ({timestamp}) ===\n")
                log_file.write(f"Número da página: {page_num}\n")
                log_file.write(f"Texto extraído:\n{text[:500]}...\n\n")
        except Exception as e:
            self.logger.error(f"Erro ao registrar página não identificada: {e}")
    
    def merge_pdfs(self, pdf_paths, output_path):
        """
        Combina múltiplos PDFs em um único arquivo.
        
        Args:
            pdf_paths (list): Lista de caminhos de PDFs a serem combinados
            output_path (str): Caminho para salvar o PDF combinado
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        try:
            # Criar diretório de saída se não existir
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Criar novo documento
            merged_doc = fitz.open()
            
            # Adicionar cada PDF
            for pdf_path in pdf_paths:
                if os.path.exists(pdf_path):
                    doc = fitz.open(pdf_path)
                    merged_doc.insert_pdf(doc)
                    doc.close()
                else:
                    self.logger.warning(f"Arquivo não encontrado: {pdf_path}")
            
            # Salvar o documento mesclado
            merged_doc.save(output_path)
            merged_doc.close()
            
            self.logger.info(f"PDFs mesclados com sucesso: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao mesclar PDFs: {e}")
            return False
    
    def secure_document(self, pdf_path, output_path, password):
        """
        Aplica criptografia a um documento PDF.
        
        Args:
            pdf_path (str): Caminho do PDF de entrada
            output_path (str): Caminho para salvar o PDF criptografado
            password (str): Senha para criptografia
            
        Returns:
            bool: True se a operação foi bem-sucedida
        """
        try:
            # Criar diretório de saída se não existir
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Abrir o documento
            doc = fitz.open(pdf_path)
            
            # Aplicar permissões e senha
            perm = int(
                fitz.PDF_PERM_PRINT |  # Permitir impressão
                fitz.PDF_PERM_COPY   # Permitir cópia de conteúdo
            )
            encrypt_meth = fitz.PDF_ENCRYPT_AES_256  # Método de criptografia AES 256
            
            # Definir senha e permissões
            doc.save(
                output_path,
                encryption=encrypt_meth,
                owner_pw=password,
                user_pw=password,
                permissions=perm
            )
            doc.close()
            
            self.logger.info(f"Documento criptografado com sucesso: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao criptografar documento: {e}")
            return False
    
    def backup_original(self, pdf_path, backup_dir="./backup"):
        """
        Faz backup do arquivo PDF original.
        
        Args:
            pdf_path (str): Caminho do PDF original
            backup_dir (str): Diretório para backup
            
        Returns:
            str: Caminho do arquivo de backup
        """
        try:
            # Garantir que o diretório existe
            Path(backup_dir).mkdir(parents=True, exist_ok=True)
            
            # Nome do arquivo com timestamp
            filename = os.path.basename(pdf_path)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_filename = f"{timestamp}_{filename}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Copiar arquivo
            shutil.copy2(pdf_path, backup_path)
            
            self.logger.info(f"Backup criado: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            return None 