import fitz  # PyMuPDF
import PyPDF2
from typing import Literal
from src.utils.logger import setup_logger
from src.classification.text_analyzer import has_selectable_text
from src.classification.image_analyzer import has_text_in_images
from src.classification.table_detector import has_tables_in_pdf

logger = setup_logger(__name__)

PDFType = Literal['text_only', 'image_only', 'mixed', 'tables', 'unprocessable']

class PDFClassifier:
    def __init__(self, config: dict):
        self.config = config
        self.last_analysis = {
            'file': None,
            'text_selectable': False,
            'image_has_text': False,
            'error': None,
            'enhanced_check': False
        }

    def classify(self, pdf_path: str) -> PDFType:
        pdf_name = pdf_path.split("/")[-1]
        logger.info(f"📂 Iniciando classificação do PDF: {pdf_name}")

        self.last_analysis = {
            'file': pdf_name,
            'text_selectable': False,
            'image_has_text': False,
            'error': None,
            'enhanced_check': False
        }

        try:
            has_text = has_selectable_text(pdf_path, threshold=self.config.get("text_threshold", 0.7))
            has_image = has_text_in_images(pdf_path, sample_pages=self.config.get("pages_to_sample", 3))

            self.last_analysis['text_selectable'] = has_text
            self.last_analysis['image_has_text'] = has_image

            logger.info(f"🔎 Verificação combinada - Texto selecionável: {has_text}, Texto em imagens: {has_image}")

            if has_text and has_image:
                logger.info(f"✅ {pdf_name} classificado como: mixed")
                return "mixed"
            elif has_text:
                logger.info(f"✅ {pdf_name} classificado como: text_only")
                return "text_only"
            elif has_image:
                logger.info(f"✅ {pdf_name} classificado como: image_only")
                return "image_only"
            else:
                logger.warning(f"❌ {pdf_name} classificado como: unprocessable (sem texto detectável)")
                return "unprocessable"

        except Exception as e:
            error_msg = f"error: {str(e)}"
            self.last_analysis['error'] = error_msg
            logger.error(f"🚨 Erro ao classificar {pdf_name}: {str(e)}")
            return "unprocessable"
