"""
Módulo de envio de e-mails.
Este módulo implementa funções para envio seguro de e-mails com anexos.
Inclui recursos para gerenciamento de templates e logs de envios.
"""

import os
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from pathlib import Path
import dotenv
from typing import List, Dict, Optional, Union


class EmailSender:
    """Classe para envio seguro de e-mails com anexos."""
    
    def __init__(self, config_file=".env", logs_dir="./logs"):
        """
        Inicializa o serviço de envio de e-mails.
        
        Args:
            config_file (str): Arquivo de configuração com credenciais
            logs_dir (str): Diretório para logs de envio
        """
        # Carregar configurações do arquivo .env
        dotenv.load_dotenv(config_file)
        
        # Garantir que o diretório de logs existe
        Path(logs_dir).mkdir(parents=True, exist_ok=True)
        
        # Configurar logger
        self.logger = logging.getLogger("email_sender")
        
        # Configurar log de emails enviados
        self.email_log_path = os.path.join(logs_dir, "email_sent.log")
        
        # Obter configurações do arquivo .env
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.email_address = os.getenv("EMAIL_ADDRESS", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.use_tls = os.getenv("USE_TLS", "True").lower() == "true"
        
        # Verificar configurações
        if not self.email_address or not self.email_password:
            self.logger.error("Credenciais de e-mail não configuradas")
    
    def send_email(self, 
                   recipients: List[str], 
                   subject: str, 
                   body: str, 
                   attachments: List[str] = None, 
                   cc: List[str] = None, 
                   bcc: List[str] = None, 
                   is_html: bool = False) -> bool:
        """
        Envia um e-mail para um ou mais destinatários.
        
        Args:
            recipients (list): Lista de endereços de e-mail dos destinatários
            subject (str): Assunto do e-mail
            body (str): Corpo do e-mail
            attachments (list): Lista de caminhos de arquivos para anexar
            cc (list): Lista de endereços em cópia
            bcc (list): Lista de endereços em cópia oculta
            is_html (bool): Se o corpo do e-mail está em formato HTML
            
        Returns:
            bool: True se o e-mail foi enviado com sucesso
        """
        if not recipients:
            self.logger.error("Nenhum destinatário especificado")
            return False
        
        if not self.email_address or not self.email_password:
            self.logger.error("Credenciais de e-mail não configuradas")
            return False
        
        try:
            # Criar mensagem
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Adicionar CC e BCC, se fornecidos
            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)
            
            # Adicionar corpo da mensagem
            content_type = "html" if is_html else "plain"
            msg.attach(MIMEText(body, content_type))
            
            # Adicionar anexos, se fornecidos
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        self._attach_file(msg, file_path)
                    else:
                        self.logger.warning(f"Anexo não encontrado: {file_path}")
            
            # Combinar todos os destinatários
            all_recipients = []
            all_recipients.extend(recipients)
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)
            
            # Conectar ao servidor SMTP e enviar e-mail
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=ssl.create_default_context())
                
                server.login(self.email_address, self.email_password)
                server.sendmail(self.email_address, all_recipients, msg.as_string())
            
            # Registrar envio
            self._log_email_sent(recipients, subject, attachments)
            
            self.logger.info(f"E-mail enviado com sucesso para {len(recipients)} destinatários")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar e-mail: {e}")
            return False
    
    def send_template_email(self, 
                           recipients: List[str], 
                           template_name: str, 
                           template_data: Dict, 
                           subject: str,
                           attachments: List[str] = None, 
                           cc: List[str] = None, 
                           bcc: List[str] = None) -> bool:
        """
        Envia um e-mail usando um template.
        
        Args:
            recipients (list): Lista de endereços de e-mail dos destinatários
            template_name (str): Nome do template a ser usado
            template_data (dict): Dados para preencher o template
            subject (str): Assunto do e-mail
            attachments (list): Lista de caminhos de arquivos para anexar
            cc (list): Lista de endereços em cópia
            bcc (list): Lista de endereços em cópia oculta
            
        Returns:
            bool: True se o e-mail foi enviado com sucesso
        """
        # Substituir por um sistema de templates mais robusto se necessário
        template_content = self._get_template_content(template_name)
        
        if not template_content:
            self.logger.error(f"Template não encontrado: {template_name}")
            return False
        
        # Substituir variáveis no template
        for key, value in template_data.items():
            placeholder = f"{{{{{key}}}}}"
            template_content = template_content.replace(placeholder, str(value))
        
        # Enviar e-mail com o template preenchido
        return self.send_email(
            recipients=recipients,
            subject=subject,
            body=template_content,
            attachments=attachments,
            cc=cc,
            bcc=bcc,
            is_html=True
        )
    
    def send_document_notification(self, 
                                  employee_email: str, 
                                  employee_name: str,
                                  document_type: str,
                                  document_path: str,
                                  reference_period: str = None) -> bool:
        """
        Envia uma notificação com um documento para um funcionário.
        
        Args:
            employee_email (str): E-mail do funcionário
            employee_name (str): Nome do funcionário
            document_type (str): Tipo de documento (ex: "Contracheque")
            document_path (str): Caminho para o documento
            reference_period (str): Período de referência (ex: "Janeiro/2023")
            
        Returns:
            bool: True se o e-mail foi enviado com sucesso
        """
        subject = f"{document_type} - {reference_period or 'Documento'}"
        
        # Construir corpo do e-mail
        body = f"""
        <html>
        <body>
        <p>Olá {employee_name},</p>
        <p>Segue em anexo seu {document_type.lower()}{' referente a ' + reference_period if reference_period else ''}.</p>
        <p>Este é um e-mail automático, por favor não responda.</p>
        <p>Em caso de dúvidas, entre em contato com o departamento de recursos humanos.</p>
        <br>
        <p><i>Este e-mail contém informações confidenciais e é destinado exclusivamente ao destinatário. 
        Se você recebeu este e-mail por engano, por favor, notifique o remetente e exclua-o imediatamente.</i></p>
        </body>
        </html>
        """
        
        return self.send_email(
            recipients=[employee_email],
            subject=subject,
            body=body,
            attachments=[document_path],
            is_html=True
        )
    
    def send_bulk_emails(self, 
                        email_data: List[Dict], 
                        template_name: str = None,
                        default_subject: str = "Documento") -> Dict:
        """
        Envia e-mails em massa para vários destinatários.
        
        Args:
            email_data (list): Lista de dicionários com dados de e-mail
                Cada item deve conter: 'email', 'name', 'attachments', etc.
            template_name (str): Nome do template a ser usado
            default_subject (str): Assunto padrão, caso não especificado nos dados
            
        Returns:
            dict: Estatísticas de envio (sucesso, falha, total)
        """
        stats = {
            "total": len(email_data),
            "success": 0,
            "failed": 0,
            "failed_addresses": []
        }
        
        for data in email_data:
            email = data.get("email")
            name = data.get("name", "")
            attachments = data.get("attachments", [])
            subject = data.get("subject", default_subject)
            
            if not email:
                stats["failed"] += 1
                continue
            
            success = False
            
            if template_name:
                # Usar template se fornecido
                success = self.send_template_email(
                    recipients=[email],
                    template_name=template_name,
                    template_data=data,
                    subject=subject,
                    attachments=attachments
                )
            else:
                # Construir e-mail simples
                body = f"""
                <html>
                <body>
                <p>Olá {name},</p>
                <p>Segue em anexo seu documento.</p>
                <p>Este é um e-mail automático, por favor não responda.</p>
                </body>
                </html>
                """
                
                success = self.send_email(
                    recipients=[email],
                    subject=subject,
                    body=body,
                    attachments=attachments,
                    is_html=True
                )
            
            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1
                stats["failed_addresses"].append(email)
        
        return stats
    
    def _attach_file(self, msg: MIMEMultipart, file_path: str) -> bool:
        """
        Anexa um arquivo à mensagem.
        
        Args:
            msg (MIMEMultipart): Mensagem à qual anexar o arquivo
            file_path (str): Caminho do arquivo a ser anexado
            
        Returns:
            bool: True se o arquivo foi anexado com sucesso
        """
        try:
            filename = os.path.basename(file_path)
            
            # Determinar tipo MIME com base na extensão
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext == '.pdf':
                # Anexar PDF
                with open(file_path, 'rb') as file:
                    part = MIMEApplication(file.read(), Name=filename)
                part['Content-Disposition'] = f'attachment; filename="{filename}"'
            else:
                # Anexar outros tipos de arquivo
                with open(file_path, 'rb') as file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
            
            # Adicionar parte à mensagem
            msg.attach(part)
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao anexar arquivo {file_path}: {e}")
            return False
    
    def _log_email_sent(self, recipients: List[str], subject: str, attachments: List[str] = None) -> None:
        """
        Registra o envio de um e-mail no log.
        
        Args:
            recipients (list): Lista de destinatários
            subject (str): Assunto do e-mail
            attachments (list): Lista de anexos
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(self.email_log_path, "a", encoding="utf-8") as log_file:
                log_file.write(f"=== E-mail enviado em {timestamp} ===\n")
                log_file.write(f"De: {self.email_address}\n")
                log_file.write(f"Para: {', '.join(recipients)}\n")
                log_file.write(f"Assunto: {subject}\n")
                
                if attachments:
                    log_file.write(f"Anexos: {', '.join([os.path.basename(a) for a in attachments])}\n")
                
                log_file.write("\n")
        except Exception as e:
            self.logger.error(f"Erro ao registrar envio de e-mail: {e}")
    
    def _get_template_content(self, template_name: str) -> Optional[str]:
        """
        Obtém o conteúdo de um template de e-mail.
        
        Args:
            template_name (str): Nome do template
            
        Returns:
            str: Conteúdo do template ou None se não encontrado
        """
        # Implementação básica, substituir por sistema de templates mais robusto se necessário
        templates = {
            "notification": """
            <html>
            <body>
            <p>Olá {{name}},</p>
            <p>{{message}}</p>
            <p>Atenciosamente,<br>Recursos Humanos</p>
            </body>
            </html>
            """,
            
            "payslip": """
            <html>
            <body>
            <p>Olá {{name}},</p>
            <p>Segue em anexo seu contracheque referente a {{period}}.</p>
            <p>Em caso de dúvidas, entre em contato com o departamento de recursos humanos.</p>
            <br>
            <p><i>Este e-mail contém informações confidenciais e é destinado exclusivamente ao destinatário.</i></p>
            </body>
            </html>
            """
        }
        
        return templates.get(template_name) 