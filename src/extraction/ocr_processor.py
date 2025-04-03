import os
from pathlib import Path
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
from src.utils.logger import setup_logger

# Caminho do log
log_path = Path("data/output/processing.log")

# Configura o logger
logger = setup_logger(__name__, log_file=log_path)

# Caminho do Tesseract (ajuste conforme necessário)
tesseract_path = r'C:\Users\PROVER\AppData\Local\Tesseract-OCR\tesseract.exe'
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    logger.error(f"Tesseract não encontrado em {tesseract_path}")
    raise FileNotFoundError(
        f"Tesseract não encontrado! Instale em: https://github.com/UB-Mannheim/tesseract/wiki"
    )

# Configurações padrão do OCR
OCR_CONFIG = "--psm 6 -l por+eng"
MIN_TEXT_LENGTH = 10

def preprocess_image(image):
    """Melhora a imagem para OCR."""
    try:
        # Converte a imagem para escala de cinza
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)

        # Testa OCR com a imagem em escala de cinza antes de pré-processar
        raw_text = pytesseract.image_to_string(gray, config=OCR_CONFIG)
        if len(raw_text.strip()) > 20:
            return gray  # Se já funcionar bem, não é necessário mais processamento

        # Caso contrário, aplica melhoria na imagem
        denoised = cv2.fastNlMeansDenoising(gray, h=15)  # Redução de ruído mais suave
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        return thresh
    except Exception as e:
        logger.error(f"Erro no pré-processamento: {str(e)}")
        return image

def extract_text_from_images(pdf_path: str, output_dir: str) -> str:
    """Extrai texto de PDFs com imagens usando OCR."""
    try:
        # Garante que a pasta de saída existe
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
        
        # Cria o diretório para imagens de debug (uma única vez)
        debug_dir = output_dir_path / "debug_images"
        debug_dir.mkdir(exist_ok=True)
        
        # Converte o PDF para imagens com DPI configurado
        images = convert_from_path(pdf_path, dpi=300)
        if not images:
            logger.error(f"Falha na conversão de {pdf_path} para imagens. Verifique o Poppler.")
            return ""

        extracted_texts = []
        
        for i, img in enumerate(images):
            processed_img = preprocess_image(img)
            text = pytesseract.image_to_string(processed_img, config=OCR_CONFIG).strip()
            
            if len(text) < MIN_TEXT_LENGTH:
                logger.warning(
                    f"OCR extraiu pouco texto na página {i+1} de {pdf_path}. Pode haver problemas na imagem."
                )
            
            extracted_texts.append(text)
            
            # Salva a imagem processada para fins de debug
            debug_image_path = debug_dir / f"page_{i+1}_processed.jpg"
            cv2.imwrite(str(debug_image_path), processed_img)

        full_text = "\n".join(extracted_texts).strip()
        if not full_text:
            logger.error(f"Nenhum texto extraído de {pdf_path}. O PDF pode estar corrompido ou ilegível.")
            return ""

        # Salva o texto extraído em um arquivo .txt
        output_path = output_dir_path / f"{Path(pdf_path).stem}.txt"
        logger.info(f"Salvando texto extraído em {output_path}...")
        try:
            print(f"Salvando arquivo em: {output_path}")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)
            logger.info(f"✅ Texto extraído salvo: {output_path}")
        except PermissionError:
            logger.error(f"❌ Permissão negada ao tentar salvar {output_path}")
            return ""
        
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Erro no OCR: {str(e)}")
        return ""
