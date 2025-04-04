import pytesseract
import cv2
import numpy as np
import time
import io
from PIL import Image
from pdf2image import convert_from_path
import fitz  # PyMuPDF
import hashlib
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_adaptive_block_size(width: int) -> int:
    block_size = width // 40
    if block_size % 2 == 0:
        block_size += 1
    return max(11, block_size)

def preprocess_image(image):
    try:
        start_time = time.time()
        image_np = np.array(image)
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        bilateral = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(bilateral)
        background_removed = cv2.medianBlur(enhanced, 3)
        block_size = get_adaptive_block_size(image_np.shape[1])
        thresh = cv2.adaptiveThreshold(
            background_removed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, block_size, 2
        )
        kernel_open = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel_open)
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
        return image

def extract_ocr_relevant_images(pdf_path: str, min_size: tuple = (400, 400), pages_to_sample: int = 3):
    relevant_images = []
    try:
        with fitz.open(pdf_path) as doc:
            for page_index in range(min(pages_to_sample, len(doc))):
                page = doc[page_index]
                images = page.get_images(full=True)
                for img_index, img_info in enumerate(images):
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    img = Image.open(io.BytesIO(image_bytes)).convert("L")
                    width, height = img.size
                    if width < min_size[0] or height < min_size[1]:
                        continue
                    img_np = np.array(img)
                    if np.mean(img_np) > 245 or np.mean(img_np) < 10:
                        continue
                    hash_digest = hashlib.md5(img_np.tobytes()).hexdigest()
                    relevant_images.append((img, hash_digest))
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {pdf_path}")
    except Exception as e:
        logger.error(f"Erro ao extrair imagens do PDF {pdf_path}: {str(e)}")
    return relevant_images

def has_text_in_images(pdf_path: str, pages_to_sample: int = 1) -> bool:
    try:
        start_time = time.time()
        relevant_images = extract_ocr_relevant_images(pdf_path, pages_to_sample=pages_to_sample)
        detected_texts = []
        min_text_length = 15

        for i, (img, img_hash) in enumerate(relevant_images):
            processed_img = preprocess_image(img)
            custom_config = r'--oem 3 --psm 6 -l por+eng'
            text = pytesseract.image_to_string(processed_img, config=custom_config).strip()
            if len(text) > min_text_length:
                detected_texts.append(text)
            logger.info(f"Imagem relevante {i+1}: Extraído {len(text)} caracteres.")

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

if __name__ == "__main__":
    import pytest
    pytest.main([
        "tests/test_text_analyzer.py",
        "--cov=src/classification/text_analyzer.py",
        "--cov-report=html:reports/coverage_text_analyzer",
        "--html=reports/test_report_text_analyzer.html",
        "--self-contained-html"
    ])
