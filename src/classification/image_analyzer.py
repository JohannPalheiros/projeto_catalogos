import pytesseract
import cv2
import numpy as np
import time
from pdf2image import convert_from_path
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_adaptive_block_size(width: int) -> int:
    """
    Calcula um tamanho de bloco para a binarização adaptativa,
    garantindo que seja um número ímpar e não menor que 11.
    """
    block_size = width // 40
    if block_size % 2 == 0:
        block_size += 1
    return max(11, block_size)

def preprocess_image(image):
    """
    Melhora a qualidade da imagem para OCR.
    
    Etapas:
      - Conversão para escala de cinza
      - Filtro bilateral para suavização preservando bordas
      - Equalização adaptativa (CLAHE) para melhorar o contraste
      - Remoção de padrões repetitivos no fundo com mediana
      - Binarização adaptativa com bloco de tamanho dinâmico
      - Abertura morfológica para eliminar pequenos ruídos
      - Correção de inclinação (Deskewing) utilizando Transformada de Hough
    """
    try:
        start_time = time.time()

        # Converte a imagem para array e para escala de cinza
        image_np = np.array(image)
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

        # Suavização preservando bordas
        bilateral = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

        # Equalização adaptativa para melhorar o contraste
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(bilateral)

        # Remoção de padrões repetitivos no fundo (opcional)
        background_removed = cv2.medianBlur(enhanced, 3)

        # Binarização adaptativa com tamanho de bloco dinâmico
        block_size = get_adaptive_block_size(image_np.shape[1])
        thresh = cv2.adaptiveThreshold(
            background_removed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, block_size, 2
        )

        # Abertura morfológica para remoção de ruídos pequenos
        kernel_open = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_open)

        # Correção de inclinação (deskewing) utilizando Transformada de Hough
        edges = cv2.Canny(morph, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=30, maxLineGap=5)

        if lines is not None:
            angles = []
            for line in lines:
                for x1, y1, x2, y2 in line:
                    angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                    angles.append(angle)
            median_angle = np.median(angles)
            (h, w) = morph.shape
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
            morph = cv2.warpAffine(morph, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        end_time = time.time()
        logger.info(f"Pré-processamento concluído em {end_time - start_time:.2f}s")
        return morph

    except Exception as e:
        logger.error(f"Erro no pré-processamento da imagem: {str(e)}")
        return image  # Retorna a imagem original em caso de falha

def has_text_in_images(pdf_path: str, pages_to_sample: int = 1) -> bool:
    """
    Verifica se há texto em imagens dentro do PDF.
    
    - Aplica pré-processamento avançado antes do OCR.
    - Utiliza Tesseract com configurações otimizadas para imagens de baixa qualidade.
    - Registra logs detalhados do processo.
    
    :param pdf_path: Caminho para o arquivo PDF.
    :param pages_to_sample: Número de páginas a serem amostradas.
    :return: True se texto for detectado; False caso contrário.
    """
    try:
        start_time = time.time()
        images = convert_from_path(pdf_path, first_page=1, last_page=pages_to_sample)
        detected_texts = []
        min_text_length = 15  # Limiar mínimo para considerar que o OCR encontrou texto

        for i, img in enumerate(images):
            processed_img = preprocess_image(img)
            
            # Configuração otimizada para OCR
            custom_config = r'--oem 3 --psm 6 -l por+eng'
            text = pytesseract.image_to_string(processed_img, config=custom_config).strip()

            if len(text) > min_text_length:
                detected_texts.append(text)

            logger.info(f"Página {i+1}: Extraído {len(text)} caracteres.")

        end_time = time.time()
        if detected_texts:
            logger.info(f"Texto detectado em {pdf_path}. Tempo total: {end_time - start_time:.2f}s")
            return True
        else:
            logger.warning(f"Nenhum texto encontrado em {pdf_path}. Tempo total: {end_time - start_time:.2f}s")
            return False

    except Exception as e:
        logger.error(f"Erro no OCR do arquivo {pdf_path}: {str(e)}")
        return False
