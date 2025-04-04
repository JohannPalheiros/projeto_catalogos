import os

# Cria conteúdo de teste unitário para `has_selectable_text`
test_code = """
import pytest
from src.classification.text_analyzer import has_selectable_text

TEST_PDF_WITH_TEXT = "tests/data/pdf_com_texto_selecionavel.pdf"
TEST_PDF_WITHOUT_TEXT = "tests/data/pdf_sem_texto_selecionavel.pdf"
INVALID_PDF = "tests/data/inexistente.pdf"

def test_has_selectable_text_true():
    assert has_selectable_text(TEST_PDF_WITH_TEXT) is True

def test_has_selectable_text_false():
    assert has_selectable_text(TEST_PDF_WITHOUT_TEXT) is False

def test_has_selectable_text_invalid():
    with pytest.raises(FileNotFoundError):
        has_selectable_text(INVALID_PDF)
"""

# Garante que a pasta de testes existe
os.makedirs("tests", exist_ok=True)

# Escreve o conteúdo do teste no arquivo apropriado
test_path = "tests/test_text_analyzer.py"
with open(test_path, "w", encoding="utf-8") as f:
    f.write(test_code)

test_path
