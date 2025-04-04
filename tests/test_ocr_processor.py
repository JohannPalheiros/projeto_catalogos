import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from pathlib import Path
from src.extraction.ocr_processor import extract_text_from_images

DUMMY_PDF = "tests/data/fake.pdf"

@patch("src.extraction.ocr_processor.convert_from_path")
@patch("src.extraction.ocr_processor.pytesseract.image_to_string")
@patch("src.extraction.ocr_processor.preprocess_image")
@patch("pathlib.Path.mkdir")
def test_extract_text_success(mock_mkdir, mock_preprocess, mock_ocr, mock_convert):
    dummy_image = np.zeros((500, 500), dtype=np.uint8)
    mock_convert.return_value = [dummy_image]
    mock_preprocess.return_value = dummy_image
    mock_ocr.return_value = "Texto detectado"

    output_dir = "tests/output"
    result_path = extract_text_from_images(DUMMY_PDF, output_dir=output_dir)

    # Criamos a instância esperada para o arquivo de saída
    expected_output_path = Path(output_dir) / "fake.txt"

    assert result_path == str(expected_output_path)
    assert expected_output_path.exists(), "Arquivo de saída não foi criado"

    # Limpa após o teste (boa prática)
    expected_output_path.unlink()

@patch("src.extraction.ocr_processor.convert_from_path", side_effect=FileNotFoundError)
def test_extract_text_file_not_found(mock_convert):
    result = extract_text_from_images("tests/data/inexistente.pdf", output_dir="tests/output")
    assert result is None
