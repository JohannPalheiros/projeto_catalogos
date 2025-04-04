import os
import pytest
from src.classification.image_analyzer import extract_ocr_relevant_images, has_text_in_images

TEST_PDF_WITH_TEXT_IMAGES = "tests/data/pdf_com_texto_em_imagem.pdf"

# Função auxiliar para log amigável quando o arquivo não existir
def log_missing_file():
    print(f"\n📁 Arquivo de teste não encontrado: {TEST_PDF_WITH_TEXT_IMAGES}")
    print("🔧 Verifique se o PDF de teste está na pasta correta.")
    print("📂 Caminho esperado: tests/data/pdf_com_texto_em_imagem.pdf\n")

@pytest.mark.skipif(not os.path.exists(TEST_PDF_WITH_TEXT_IMAGES), reason="Arquivo de teste não encontrado.")
def test_extract_ocr_relevant_images():
    if not os.path.exists(TEST_PDF_WITH_TEXT_IMAGES):
        log_missing_file()
        pytest.skip("Arquivo de teste ausente.")
    images = extract_ocr_relevant_images(TEST_PDF_WITH_TEXT_IMAGES)
    assert isinstance(images, list)
    assert all(len(pair) == 2 for pair in images)

@pytest.mark.skipif(not os.path.exists(TEST_PDF_WITH_TEXT_IMAGES), reason="Arquivo de teste não encontrado.")
def test_has_text_in_images_positive():
    if not os.path.exists(TEST_PDF_WITH_TEXT_IMAGES):
        log_missing_file()
        pytest.skip("Arquivo de teste ausente.")
    result = has_text_in_images(TEST_PDF_WITH_TEXT_IMAGES, pages_to_sample=2)
    assert result is True

def test_has_text_in_images_negative():
    fake_path = "tests/data/inexistente.pdf"
    result = has_text_in_images(fake_path)
    assert result is False
