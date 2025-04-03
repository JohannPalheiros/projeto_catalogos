import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import os
from typing import Dict
from src.classification.pdf_classifier import PDFClassifier
from src.utils.file_utils import move_file
from src.utils.logger import setup_logger
from src.extraction.text_extractor import extract_and_save_text
from src.extraction.ocr_processor import extract_text_from_images
# Importa o detector de tabelas
from src.classification.table_detector import has_tables_in_pdf  

# Importa o extrator para PDFs mistos
from src.extraction.mixed_extractor import extract_text_mixed

# Define o caminho do Poppler manualmente
poppler_path = Path("libs/poppler-24.08.0/Library/bin").resolve()
os.environ["PATH"] += os.pathsep + str(poppler_path)

config = {
    'pages_to_sample': 3,
    'min_text_length': 15,
    'ocr_language': 'por+eng',
    'dpi': 300,
    'enable_ocr': True,  # Habilita processamento OCR
    'quarantine_unprocessable': True,  # Move arquivos não processáveis
    'enable_debug': True  # Habilita modo debug
}

logger = setup_logger(__name__)

def process_batch(input_dir: str, output_base_dir: str, config: Dict):
    """Processa todos os PDFs no diretório de entrada, extrai o texto e os classifica."""
    logger.info("Iniciando processamento em lote...")
    
    input_dir_path = Path(input_dir)
    if not input_dir_path.exists():
        logger.error(f"Diretório de entrada não encontrado: {input_dir}")
        return

    output_base_path = Path(output_base_dir)
    output_base_path.mkdir(parents=True, exist_ok=True)

    # Diretório base para armazenar os arquivos .txt extraídos, organizados por tipo
    text_output_base = Path("data/output/text")
    text_output_base.mkdir(parents=True, exist_ok=True)
    
    classifier = PDFClassifier(config)
    pdf_files = list(input_dir_path.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("Nenhum arquivo PDF encontrado para processar!")
        return

    for pdf_file in pdf_files:
        try:
            filename = pdf_file.name
            logger.debug(f"Processando arquivo: {filename}")
            pdf_type = classifier.classify(str(pdf_file))
            
            # Verifica se há tabelas para ajustar a classificação, mas ainda tenta extrair o texto
            if has_tables_in_pdf(str(pdf_file)):
                logger.info(f"Tabela detectada em: {filename}")
                pdf_type = 'tables'
            
            txt_path = None
            # Cria a subpasta de saída de texto de acordo com o tipo
            extraction_dir = text_output_base / pdf_type
            extraction_dir.mkdir(parents=True, exist_ok=True)
            
            # Extrai texto para todos os tipos (exceto se o PDF for considerado totalmente "unprocessable")
            if pdf_type == 'text_only':
                txt_path = extract_and_save_text(str(pdf_file), output_dir=str(extraction_dir))
            elif pdf_type == 'image_only':
                txt_path = extract_text_from_images(str(pdf_file), output_dir=str(extraction_dir))
            elif pdf_type == 'mixed':
                txt_path = extract_text_mixed(str(pdf_file), output_dir=str(extraction_dir))
            elif pdf_type == 'tables':
                txt_path = extract_and_save_text(str(pdf_file), output_dir=str(extraction_dir))
            else:
                logger.warning(f"⚠️ Tipo de PDF '{pdf_type}' não reconhecido para extração: {filename}")
            
            if not txt_path:
                logger.warning(f"⚠️ Falha ao salvar texto extraído de {filename}")
                continue  # Pula para o próximo PDF se a extração falhar
            
            logger.info(f"✅ Texto extraído salvo em: {txt_path}")
            
            # Se o PDF for classificado como 'unprocessable', movemos para quarentena
            if pdf_type == 'unprocessable':
                logger.warning(f"Arquivo não processável: {filename}")
                if config.get('quarantine_unprocessable', False):
                    quarantine_dir = output_base_path / "quarantine"
                    quarantine_dir.mkdir(parents=True, exist_ok=True)
                    move_file(str(pdf_file), str(quarantine_dir / filename))
                    continue
            
            # Define o diretório de destino para o arquivo PDF processado com base na classificação
            destination_dir = output_base_path / pdf_type
            destination_dir.mkdir(parents=True, exist_ok=True)
            destination = destination_dir / filename
            move_file(str(pdf_file), str(destination))
            logger.info(f"📂 Arquivo {filename} classificado como {pdf_type} e movido para {destination}")
    
        except Exception as e:
            logger.error(f"❌ Falha crítica ao processar {pdf_file.name}: {str(e)}")
            error_dir = output_base_path / "errors"
            error_dir.mkdir(parents=True, exist_ok=True)
            move_file(str(pdf_file), str(error_dir / pdf_file.name))
            continue

    logger.info("✅ Processamento em lote concluído!")

if __name__ == "__main__":
    print("⭐ Script iniciado!")
    input_dir = "data/input/pending"
    output_dir = "data/input/processed"
    process_batch(input_dir=input_dir, output_base_dir=output_dir, config=config)
    print("✅ Processamento concluído!")
