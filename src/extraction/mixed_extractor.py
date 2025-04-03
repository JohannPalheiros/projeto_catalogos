# src/extraction/mixed_extractor.py

import os
import re
from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

from src.classification.image_analyzer import preprocess_image
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def sanitize_filename(filename: str) -> str:
    """
    Sanitiza o nome do arquivo removendo espaços e caracteres especiais.
    """
    sanitized = re.sub(r'\s+', '_', filename)
    sanitized = re.sub(r'[^\w\-]', '', sanitized)
    return sanitized

def extract_text_mixed(
    pdf_path: str,
    output_dir: str,
    text_threshold: int = 15,
    ocr_language: str = 'por+eng',
    dpi: int = 300
) -> str:
    """
    Extrai texto de um PDF misto.
    
    Para cada página:
      - Tenta extrair o texto diretamente com PyMuPDF.
      - Se o texto extraído for menor que `text_threshold`, converte a página para imagem,
        aplica pré-processamento e executa OCR.
      
    Os textos de todas as páginas são combinados e salvos em um arquivo .txt.
    
    :param pdf_path: Caminho para o arquivo PDF.
    :param output_dir: Diretório onde o arquivo .txt será salvo.
    :param text_threshold: Limiar mínimo de caracteres para considerar a extração direta suficiente.
    :param ocr_language: Idiomas a serem utilizados pelo Tesseract (ex.: 'por+eng').
    :param dpi: Resolução para conversão da página em imagem.
    :return: Caminho para o arquivo .txt com o texto extraído ou None em caso de falha.
    """
    try:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        sanitized_filename = f"{sanitize_filename(Path(pdf_path).stem)}.txt"
        output_path = output_dir / sanitized_filename

        # Abre o PDF usando PyMuPDF
        doc = fitz.open(pdf_path)
        full_text = []

        for page in doc:
            # Extração direta com PyMuPDF
            page_text = page.get_text("text").strip()
            
            if len(page_text) < text_threshold:
                # Se o texto extraído for insuficiente, converte a página para imagem
                pix = page.get_pixmap(dpi=dpi)
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Aplica o pré-processamento da imagem
                processed_image = preprocess_image(image)
                
                # Configuração para OCR
                custom_config = r'--oem 3 --psm 6 -l ' + ocr_language
                ocr_text = pytesseract.image_to_string(processed_image, config=custom_config).strip()
                
                logger.info(
                    f"OCR aplicado na página {page.number + 1} de {pdf_path}. "
                    f"Texto extraído: {len(ocr_text)} caracteres."
                )
                page_text = ocr_text
            else:
                logger.info(
                    f"Extração direta aplicada na página {page.number + 1} de {pdf_path}. "
                    f"Texto extraído: {len(page_text)} caracteres."
                )
            
            full_text.append(page_text)
        
        combined_text = "\n".join(full_text).strip()
        
        if not combined_text:
            logger.warning(f"⚠️ Nenhum texto extraído de {pdf_path}.")
            return None
        
        with open(output_path, 'w', encoding='utf-8', errors='replace') as f:
            f.write(combined_text)
        logger.info(f"📂 Texto extraído salvo em {output_path}")
        return str(output_path)
    except Exception as e:
        logger.error(f"Erro ao extrair texto misto de {pdf_path}: {e}")
        return None
