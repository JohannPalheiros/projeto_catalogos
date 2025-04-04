import pytest
from unittest.mock import patch
from src.classification.pdf_classifier import PDFClassifier

DUMMY_PATH = "fake_path/test.pdf"
CONFIG = {
    "pages_to_sample": 2,
    "min_text_length": 15,
    "dpi": 200,
    "ocr_language": "por+eng"
}

@patch("src.classification.pdf_classifier.has_selectable_text")
@patch("src.classification.pdf_classifier.has_text_in_images")
def test_classify_text_only(mock_image_text, mock_selectable):
    mock_selectable.return_value = True
    mock_image_text.return_value = False
    classifier = PDFClassifier(CONFIG)
    result = classifier.classify(DUMMY_PATH)
    assert result == "text_only"

@patch("src.classification.pdf_classifier.has_selectable_text")
@patch("src.classification.pdf_classifier.has_text_in_images")
def test_classify_image_only(mock_image_text, mock_selectable):
    mock_selectable.return_value = False
    mock_image_text.return_value = True
    classifier = PDFClassifier(CONFIG)
    result = classifier.classify(DUMMY_PATH)
    assert result == "image_only"

@patch("src.classification.pdf_classifier.has_selectable_text")
@patch("src.classification.pdf_classifier.has_text_in_images")
def test_classify_mixed(mock_image_text, mock_selectable):
    mock_selectable.return_value = True
    mock_image_text.return_value = True
    classifier = PDFClassifier(CONFIG)
    result = classifier.classify(DUMMY_PATH)
    assert result == "mixed"

@patch("src.classification.pdf_classifier.has_selectable_text")
@patch("src.classification.pdf_classifier.has_text_in_images")
def test_classify_unprocessable_with_fallback(mock_image_text, mock_selectable):
    mock_selectable.return_value = False
    mock_image_text.return_value = True
    classifier = PDFClassifier(CONFIG)
    result = classifier.classify(DUMMY_PATH)
    assert result == "image_only"

@patch("src.classification.pdf_classifier.has_selectable_text")
@patch("src.classification.pdf_classifier.has_text_in_images")
def test_classify_fully_unprocessable(mock_image_text, mock_selectable):
    mock_selectable.return_value = False
    mock_image_text.return_value = False
    classifier = PDFClassifier(CONFIG)
    result = classifier.classify(DUMMY_PATH)
    assert result == "unprocessable"
