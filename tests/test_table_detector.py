import pytest
from unittest.mock import patch, MagicMock
from src.classification.table_detector import has_tables_in_pdf

TEST_PDF_WITH_TABLES = "tests/data/pdf_com_tabelas.pdf"
TEST_PDF_NO_TABLES = "tests/data/pdf_sem_tabelas.pdf"
INVALID_PDF = "tests/data/inexistente.pdf"

@patch("src.classification.table_detector.pdfplumber.open")
def test_has_tables_returns_true(mock_open):
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_tables.return_value = [[["a", "b"], ["1", "2"]]]
    mock_pdf.pages = [mock_page, mock_page, mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = has_tables_in_pdf(TEST_PDF_WITH_TABLES)
    assert result is True

@patch("src.classification.table_detector.pdfplumber.open")
def test_has_tables_returns_false(mock_open):
    mock_pdf = MagicMock()
    mock_page = MagicMock()
    mock_page.extract_tables.return_value = []  # Sem tabelas
    mock_pdf.pages = [mock_page, mock_page]
    mock_open.return_value.__enter__.return_value = mock_pdf

    result = has_tables_in_pdf(TEST_PDF_NO_TABLES)
    assert result is False

def test_has_tables_invalid_file():
    result = has_tables_in_pdf(INVALID_PDF)
    assert result is False  # Espera fallback

@patch("src.classification.table_detector.pdfplumber.open", side_effect=Exception("Falha"))
def test_has_tables_exception_handling(mock_open):
    result = has_tables_in_pdf(TEST_PDF_WITH_TABLES)
    assert result is False
