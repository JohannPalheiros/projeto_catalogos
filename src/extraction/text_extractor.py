from pathlib import Path
import os
import re
import fitz  # PyMuPDF
import pdfplumber  # Extração avançada de texto
from PyPDF2 import PdfReader
from src.utils.logger import setup_logger

# Caminho do log
log_path = Path("data/output/processing.log")

# Configura o logger
logger = setup_logger(__name__, log_file=log_path)

def sanitize_filename(filename: str) -> str:
    """
    Sanitiza o nome do arquivo removendo espaços e caracteres especiais.
    Substitui espaços por underline e remove caracteres que não sejam alfanuméricos, underscore ou hífen.
    """
    sanitized = re.sub(r'\s+', '_', filename)
    sanitized = re.sub(r'[^\w\-]', '', sanitized)
    return sanitized

def extract_text_pypdf2(pdf_path: str) -> str:
    """Extrai texto usando PyPDF2. Retorna None se falhar."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            extracted_texts = [page.extract_text() or '' for page in reader.pages]
        full_text = "\n".join(extracted_texts).strip()
        return full_text if full_text else None
    except Exception as e:
        logger.warning(f"⚠️ PyPDF2 falhou ao extrair texto de {pdf_path}: {str(e)}")
        return None

def extract_text_pymupdf(pdf_path: str) -> str:
    """Extrai texto usando PyMuPDF (fitz). Retorna None se falhar."""
    try:
        doc = fitz.open(pdf_path)
        full_text = "\n".join([page.get_text("text") for page in doc]).strip()
        return full_text if full_text else None
    except Exception as e:
        logger.warning(f"⚠️ PyMuPDF falhou ao extrair texto de {pdf_path}: {str(e)}")
        return None

def extract_text_pdfplumber(pdf_path: str) -> str:
    """Extrai texto usando pdfplumber como último recurso."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            extracted_texts = [page.extract_text() or '' for page in pdf.pages]
        full_text = "\n".join(extracted_texts).strip()
        return full_text if full_text else None
    except Exception as e:
        logger.warning(f"⚠️ pdfplumber falhou ao extrair texto de {pdf_path}: {str(e)}")
        return None

def extract_and_save_text(pdf_path: str, output_dir: str) -> str:
    """
    Extrai texto de PDFs com conteúdo selecionável e salva em um arquivo .txt.
    
    Tenta extração utilizando diferentes métodos e usa um nome de arquivo sanitizado.
    
    :param pdf_path: Caminho do arquivo PDF a ser processado.
    :param output_dir: Diretório onde o arquivo .txt extraído será salvo.
    :return: Caminho para o arquivo .txt gerado ou None em caso de falha.
    """
    try:
        # Cria o diretório de saída, se não existir
        output_path_dir = Path(output_dir)
        output_path_dir.mkdir(parents=True, exist_ok=True)
        
        # Sanitiza o nome do arquivo para evitar problemas com espaços/caracteres especiais
        sanitized_filename = f"{sanitize_filename(Path(pdf_path).stem)}.txt"
        output_path = output_path_dir / sanitized_filename
        
        logger.info(f"🔍 Iniciando extração de texto para {pdf_path}...")
        print(f"📂 Tentando salvar em: {output_path}")
        
        # Tenta extrair o texto utilizando os diferentes extratores
        extractors = [extract_text_pypdf2, extract_text_pymupdf, extract_text_pdfplumber]
        full_text = None
        
        for extractor in extractors:
            full_text = extractor(pdf_path)
            if full_text:
                logger.info(f"✅ {extractor.__name__} extraiu {len(full_text)} caracteres de {pdf_path}")
                break
        
        if not full_text:
            logger.warning(f"⚠️ Nenhum texto extraído de {pdf_path}. Pode ser um PDF baseado em imagem.")
            return None
        
        if not full_text.strip():
            logger.warning(f"⚠️ Texto extraído de {pdf_path} está vazio. O arquivo pode estar corrompido ou o OCR falhou.")
            return None
        
        # Salva o texto extraído no arquivo de saída
        try:
            with open(output_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write(full_text)
            logger.info(f"📂 Texto extraído salvo em {output_path}")
            return str(output_path)
        except OSError as e:
            logger.error(f"❌ ERRO ao salvar o arquivo {output_path}: {e.strerror} (Código: {e.errno})")
            return None
    
    except Exception as e:
        logger.error(f"❌ Erro crítico ao processar {pdf_path}: {e}")
        return None
