import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import os
import shutil
import argparse
from typing import Dict
from concurrent.futures import ProcessPoolExecutor, as_completed
from src.classification.pdf_classifier import PDFClassifier
from src.utils.file_utils import move_file
from src.utils.logger import setup_logger
from src.extraction.text_extractor import extract_and_save_text
from src.extraction.ocr_processor import extract_text_from_images
from src.classification.table_detector import has_tables_in_pdf
from src.extraction.mixed_extractor import extract_text_mixed

poppler_path = Path("libs/poppler-24.08.0/Library/bin").resolve()
os.environ["PATH"] += os.pathsep + str(poppler_path)

config = {
    'pages_to_sample': 3,
    'min_text_length': 15,
    'ocr_language': 'por+eng',
    'dpi': 300,
    'enable_ocr': True,
    'quarantine_unprocessable': True,
    'enable_debug': True
}

logger = setup_logger(__name__)

def reset_test_environment():
    # 1. Limpar arquivos txt extraídos
    output_text_path = Path("data/output/text")
    if output_text_path.exists():
        for subdir in output_text_path.iterdir():
            if subdir.is_dir():
                for file in subdir.glob("*.txt"):
                    file.unlink()
    
    # 2. Mover arquivos de volta para pending
    processed_path = Path("data/input/processed")
    pending_path = Path("data/input/pending")
    for subdir in processed_path.glob("*"):
        if subdir.is_dir():
            for pdf_file in subdir.glob("*.pdf"):
                pending_path.mkdir(parents=True, exist_ok=True)
                shutil.move(str(pdf_file), str(pending_path / pdf_file.name))
    logger.info("🧹 Ambiente de teste resetado com sucesso!")

def processar_pdf(pdf_file_path: str, config: Dict) -> None:
    from time import sleep
    pdf_file = Path(pdf_file_path)
    filename = pdf_file.name
    try:
        classifier = PDFClassifier(config)
        pdf_type = classifier.classify(str(pdf_file))

        if has_tables_in_pdf(str(pdf_file)):
            logger.info(f"Tabela detectada em: {filename}")
            pdf_type = 'tables'

        text_output_base = Path("data/output/text")
        extraction_dir = text_output_base / pdf_type
        extraction_dir.mkdir(parents=True, exist_ok=True)

        txt_path = None
        if pdf_type == 'text_only':
            txt_path = extract_and_save_text(str(pdf_file), output_dir=str(extraction_dir))
        elif pdf_type == 'image_only':
            txt_path = extract_text_from_images(str(pdf_file), output_dir=str(extraction_dir))
        elif pdf_type == 'mixed':
            txt_path = extract_text_mixed(str(pdf_file), output_dir=str(extraction_dir))
        elif pdf_type == 'tables':
            txt_path = extract_and_save_text(str(pdf_file), output_dir=str(extraction_dir))
        else:
            logger.warning(f"⚠️ Tipo de PDF '{pdf_type}' não reconhecido: {filename}")

        if not txt_path:
            logger.warning(f"⚠️ Falha ao salvar texto extraído de {filename}")
            return

        logger.info(f"✅ Texto extraído salvo em: {txt_path}")

        output_base_path = Path("data/input/processed")
        if pdf_type == 'unprocessable' and config.get('quarantine_unprocessable', False):
            quarantine_dir = output_base_path / "quarantine"
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            move_file(str(pdf_file), str(quarantine_dir / filename))
            return

        destination_dir = output_base_path / pdf_type
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / filename
        move_file(str(pdf_file), str(destination))
        logger.info(f"📂 Arquivo {filename} classificado como {pdf_type} e movido para {destination}")

    except Exception as e:
        logger.error(f"❌ Falha crítica ao processar {filename}: {str(e)}")
        error_dir = Path("data/input/processed") / "errors"
        error_dir.mkdir(parents=True, exist_ok=True)
        move_file(str(pdf_file), str(error_dir / filename))

def process_batch(input_dir: str, output_base_dir: str, config: Dict):
    logger.info("Iniciando processamento em lote...")

    input_dir_path = Path(input_dir)
    if not input_dir_path.exists():
        logger.error(f"Diretório de entrada não encontrado: {input_dir}")
        return

    pdf_files = list(input_dir_path.glob("*.pdf"))
    if not pdf_files:
        logger.warning("Nenhum arquivo PDF encontrado para processar!")
        return

    pdf_files.sort(key=lambda x: x.stat().st_size, reverse=True)  # Ordena por tamanho (maior primeiro)

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(processar_pdf, str(pdf), config): pdf for pdf in pdf_files}
        total = len(futures)
        for i, future in enumerate(as_completed(futures), 1):
            try:
                future.result()
                print(f"✅ [{i}/{total}] Finalizado: {futures[future].name}")
            except Exception as e:
                print(f"❌ Erro ao processar {futures[future].name}: {e}")

    logger.info("✅ Processamento em lote concluído!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reseta ambiente de teste antes de executar")
    args = parser.parse_args()

    if args.reset:
        reset_test_environment()

    print("⭐ Script iniciado!")
    input_dir = "data/input/pending"
    output_dir = "data/input/processed"
    process_batch(input_dir=input_dir, output_base_dir=output_dir, config=config)
    print("✅ Processamento concluído!")
