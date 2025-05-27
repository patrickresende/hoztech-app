<<<<<<< HEAD
# Processador de Holerites

Uma aplicação para processamento de holerites e outros documentos PDF, com recursos de identificação automatizada de funcionários, extração de informações e envio de e-mails.

## Descrição

O Processador de Holerites é uma ferramenta desenvolvida em Python que permite automatizar o processo de separação e envio de holerites para funcionários. A aplicação identifica automaticamente os nomes dos funcionários em um PDF consolidado, separa cada página em arquivos individuais e permite o envio seguro por e-mail.

## Principais Funcionalidades

- **Interface gráfica moderna e intuitiva** com CustomTkinter
- **Processamento automatizado de PDFs** com identificação de funcionários
- **Reconhecimento inteligente de nomes** usando correspondência fuzzy e similaridade de texto
- **Múltiplos bancos de dados** para diferentes tipos de documentos
- **Gestão de funcionários** com CRUD completo
- **Envio seguro de e-mails** com anexos seguindo normas de privacidade
- **Logs detalhados** para auditoria e acompanhamento
- **Segurança e conformidade** com LGPD/GDPR

## Novas Funcionalidades

### Versão 1.2.0
- Refatoração completa do código para melhor organização e manutenção
- Interface gráfica moderna com CustomTkinter
- Sistema de banco de dados SQLite para armazenar informações de funcionários
- Módulo de envio de e-mails melhorado com suporte a templates e segurança SSL/TLS
- Gerenciamento de múltiplos bancos de dados de funcionários
- Identificação de texto avançada com busca por proximidade e sinônimos
- Reconhecimento inteligente para documentos multipágina
- Logs detalhados e tratamento de erros
- Segurança e privacidade de dados seguindo LGPD/GDPR

## Requisitos

- Python 3.10+
- Bibliotecas Python (instaladas automaticamente via requirements.txt):
  - CustomTkinter
  - PyMuPDF (para processamento de PDFs)
  - RapidFuzz (para correspondência de texto)
  - pytesseract (para OCR)
  - pillow (para processamento de imagens)
  - python-dotenv (para configurações seguras)
  - pydantic (para validação de dados)
  - SQLAlchemy (para operações de banco de dados)

- Tesseract OCR instalado no sistema (para reconhecimento de texto)

## Instalação

1. Clone o repositório:
```
git clone https://github.com/seu-usuario/processador-holerites.git
cd processador-holerites
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente para envio de e-mails:
Crie um arquivo `.env` na raiz do projeto com:
```
EMAIL_ADDRESS=seu-email@gmail.com
EMAIL_PASSWORD=sua-senha-de-app
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
USE_TLS=True
```

4. Execute a aplicação:
```
python src/app.py
```

## Uso

1. Na tela inicial, escolha entre as diversas funcionalidades disponíveis
2. Para processar holerites:
   - Selecione o arquivo PDF que contém os holerites
   - Escolha o diretório de saída
   - Informe o ano e mês de referência
   - Selecione o banco de dados de funcionários
   - Configure as opções de processamento (busca por proximidade, sinônimos)
   - Clique em "Iniciar Processamento"

3. Para enviar documentos por e-mail:
   - Navegue até a seção de Envio de E-mails
   - Selecione os funcionários e documentos
   - Configure as opções de envio
   - Envie os e-mails de forma segura

## Segurança e Privacidade

A aplicação foi desenvolvida seguindo as melhores práticas de segurança e privacidade, em conformidade com a LGPD (Lei Geral de Proteção de Dados) e GDPR (Regulamento Geral de Proteção de Dados):

- Armazenamento seguro de credenciais sensíveis
- Logs anônimos para atividades de processamento
- Criptografia de dados sensíveis
- Acesso controlado a informações pessoais
- Proteção contra vazamento de dados

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.