import os
import logging
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
from src.classification.text_analyzer import has_selectable_text
from src.classification.image_analyzer import has_text_in_images, preprocess_image
import time

# Configuração do logger para garantir que grava no log principal
logging.basicConfig(
    filename="data/output/processing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

class PDFClassifier:
    
    def __init__(self, config):
        self.config = config
        self.last_analysis = {
            'file': None,
            'text_selectable': False,
            'image_has_text': False,
            'error': None,
            'enhanced_check': False
        }

    def classify(self, pdf_path: str) -> str:
        """
        Classifica o PDF em uma das categorias:
        - 'text_only': Contém apenas texto selecionável
        - 'image_only': Texto apenas em imagens (requer OCR)
        - 'mixed': Combinação de texto e imagens com texto
        - 'unprocessable': Não contém texto legível
        - 'error: [mensagem]': Erro no processamento
        """
        pdf_name = Path(pdf_path).name
        logger.info(f"📂 Iniciando classificação do PDF: {pdf_name}")

        self.last_analysis = {
            'file': pdf_name,
            'text_selectable': False,
            'image_has_text': False,
            'error': None,
            'enhanced_check': False
        }

        try:
            # Verificação de texto selecionável
            text_selectable = has_selectable_text(pdf_path)
            self.last_analysis['text_selectable'] = text_selectable
            logger.info(f"🔍 {pdf_name}: Texto selecionável detectado? {text_selectable}")

            # Verificação de texto em imagens
            image_has_text = has_text_in_images(
                pdf_path, 
                pages_to_sample=self.config.get('pages_to_sample', 1)
            )
            self.last_analysis['image_has_text'] = image_has_text
            logger.info(f"🖼 {pdf_name}: Texto encontrado em imagens? {image_has_text}")

            # Lógica de classificação primária
            if text_selectable and not image_has_text:
                logger.info(f"✅ {pdf_name} classificado como: text_only")
                return "text_only"
            elif not text_selectable and image_has_text:
                logger.info(f"✅ {pdf_name} classificado como: image_only")
                return "image_only"
            elif text_selectable and image_has_text:
                logger.info(f"✅ {pdf_name} classificado como: mixed")
                return "mixed"
            else:
                # Verificação secundária para imagens de baixa qualidade
                if self._enhanced_image_check(pdf_path):
                    logger.warning(f"⚠️ {pdf_name}: Texto encontrado via verificação aprimorada!")
                    return "image_only"

                logger.warning(f"❌ {pdf_name} classificado como: unprocessable (Sem texto detectável)")
                return "unprocessable"

        except Exception as e:
            error_msg = f"error: {str(e)}"
            self.last_analysis['error'] = error_msg
            logger.error(f"🚨 Erro ao classificar {pdf_name}: {str(e)}")
            return error_msg

    def _enhanced_image_check(self, pdf_path: str) -> bool:
        """Verificação especial para imagens de baixa qualidade"""
        pdf_name = Path(pdf_path).name
        logger.info(f"🔬 {pdf_name}: Iniciando verificação aprimorada para texto em imagens...")

        try:
            dpi = self.config.get('dpi', 300)
            pages_sample = min(3, self.config.get('pages_to_sample', 3))
            ocr_language = self.config.get('ocr_language', 'por+eng')
            
            images = convert_from_path(
                pdf_path, 
                first_page=1, 
                last_page=pages_sample,
                dpi=dpi
            )
            
            text_found = False
            for i, img in enumerate(images):
                logger.info(f"🖼 {pdf_name}: Processando página {i + 1} para OCR avançado...")
                
                processed_img = preprocess_image(img)
                
                # Configuração agressiva para texto difícil
                custom_config = r'--oem 3 --psm 11 -l ' + ocr_language
                text = pytesseract.image_to_string(processed_img, config=custom_config)
                
                if len(text.strip()) > self.config.get('min_text_length', 10):
                    text_found = True
                    logger.info(f"✅ {pdf_name}: Texto detectado na página {i + 1} durante verificação aprimorada")
                    break  # Se encontrar texto, já podemos parar
            
            self.last_analysis['enhanced_check'] = text_found
            return text_found
            
        except Exception as e:
            logger.error(f"🚨 {pdf_name}: Erro no enhanced check - {str(e)}")
            self.last_analysis['error'] = f"enhanced_error: {str(e)}"
            return False
