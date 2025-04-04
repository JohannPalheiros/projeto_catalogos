import subprocess
import webbrowser
from pathlib import Path
import shutil
import os
import pytest  # Necessário para chamadas diretas

REPORT_DIR = Path("reports")
COV_HTML_DIR = Path("htmlcov")

REPORT_FILE = REPORT_DIR / "test_report.html"
COV_INDEX_FILE = COV_HTML_DIR / "index.html"


def clean_reports():
    if REPORT_DIR.exists():
        shutil.rmtree(REPORT_DIR)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if COV_HTML_DIR.exists():
        shutil.rmtree(COV_HTML_DIR)
    COV_HTML_DIR.mkdir(parents=True, exist_ok=True)


def run_tests():
    print("🚀 Executando testes gerais com cobertura...")

    result = subprocess.run([
        "pytest",
        "--tb=short",
        "--maxfail=1",
        "--html", str(REPORT_FILE),
        "--self-contained-html",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term",
        "tests"
    ])

    if result.returncode == 0:
        print("✅ Todos os testes passaram!")
    else:
        print("⚠️ Alguns testes falharam.")

    # Execuções isoladas com cobertura dedicada

    print("\n📌 Executando teste isolado: PDFClassifier")
    pytest.main([
        "tests/test_pdf_classifier.py",
        "--cov=src/classification/pdf_classifier.py",
        "--cov-report=html:reports/coverage_pdf_classifier",
        "--html=reports/test_report_pdf_classifier.html",
        "--self-contained-html"
    ])

    print("\n📌 Executando teste isolado: TableDetector")
    pytest.main([
        "tests/test_table_detector.py",
        "--cov=src/classification/table_detector.py",
        "--cov-report=html:reports/coverage_table_detector",
        "--html=reports/test_report_table_detector.html",
        "--self-contained-html"
    ])

    print("\n📌 Executando teste isolado: OCRProcessor")
    pytest.main([
        "tests/test_ocr_processor.py",
        "--cov=src/extraction/ocr_processor.py",
        "--cov-report=html:reports/coverage_ocr_processor",
        "--html=reports/test_report_ocr_processor.html",
        "--self-contained-html"
    ])

    print("\n📌 Executando teste isolado: TextExtractor")
    pytest.main([
        "tests/test_text_extractor.py",
        "--cov=src/extraction/text_extractor.py",
        "--cov-report=html:reports/coverage_text_extractor",
        "--html=reports/test_report_text_extractor.html",
        "--self-contained-html"
    ])

    # Abre os relatórios no navegador
    if REPORT_FILE.exists():
        print(f"📄 Abrindo relatório: {REPORT_FILE}")
        webbrowser.open(REPORT_FILE.resolve().as_uri())
    if COV_INDEX_FILE.exists():
        print(f"📊 Abrindo cobertura: {COV_INDEX_FILE}")
        webbrowser.open(COV_INDEX_FILE.resolve().as_uri())


if __name__ == "__main__":
    clean_reports()
    run_tests()
