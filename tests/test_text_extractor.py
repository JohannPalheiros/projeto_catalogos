import pytest
from unittest.mock import patch, MagicMock
from src.extraction.text_extractor import extract_and_save_text

DUMMY_PDF = "tests/data/fake.pdf"


@patch("builtins.open", new_callable=MagicMock)
@patch("pathlib.Path.mkdir")
@patch("src.extraction.text_extractor.extract_text_pdfplumber")
@patch("src.extraction.text_extractor.extract_text_pymupdf")
@patch("src.extraction.text_extractor.extract_text_pypdf2")
def test_extract_text_success(mock_pypdf2, mock_pymupdf, mock_pdfplumber, mock_mkdir, mock_open):
    # Simula falha nos dois primeiros extratores
    mock_pypdf2.return_value = None
    mock_pymupdf.return_value = None
    mock_pdfplumber.return_value = "Texto extraído com sucesso"

    # Corrige o problema de __name__
    mock_pypdf2.__name__ = "extract_text_pypdf2"
    mock_pymupdf.__name__ = "extract_text_pymupdf"
    mock_pdfplumber.__name__ = "extract_text_pdfplumber"

    result = extract_and_save_text(DUMMY_PDF, output_dir="tests/output")

    assert result is not None
    assert mock_open.called


@patch("src.extraction.text_extractor.extract_text_pdfplumber", return_value=None)
@patch("src.extraction.text_extractor.extract_text_pymupdf", return_value=None)
@patch("src.extraction.text_extractor.extract_text_pypdf2", return_value=None)
def test_extract_text_file_not_found(mock_pypdf2, mock_pymupdf, mock_pdfplumber):
    result = extract_and_save_text("tests/data/inexistente.pdf", output_dir="tests/output")
    assert result is None


@patch("src.extraction.text_extractor.extract_text_pypdf2", side_effect=Exception("Falha inesperada"))
def test_extract_text_with_exception(mock_pypdf2):
    result = extract_and_save_text(DUMMY_PDF, output_dir="tests/output")
    assert result is None
