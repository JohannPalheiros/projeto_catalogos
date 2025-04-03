import pdfplumber
import time
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def has_tables_in_pdf(pdf_path: str, pages_to_sample: int = 3) -> bool:
    """
    Verifica se há tabelas em um PDF analisando as primeiras páginas.
    
    Args:
        pdf_path (str): Caminho do arquivo PDF.
        pages_to_sample (int): Número de páginas a analisar.
    
    Returns:
        bool: True se tabelas forem detectadas, False caso contrário.
    """
    try:
        start_time = time.time()

        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            pages_to_sample = min(pages_to_sample, total_pages)

            detected_tables = 0  # Contador de tabelas válidas

            for i, page in enumerate(pdf.pages[:pages_to_sample]):
                tables = page.extract_tables()

                # Filtragem de tabelas pequenas ou irrelevantes
                filtered_tables = [
                    table for table in tables if len(table) > 1 and any(len(row) > 1 for row in table)
                ]

                if filtered_tables:
                    detected_tables += len(filtered_tables)
                    logger.info(f"Tabelas detectadas na página {i+1} do arquivo {pdf_path}.")

            end_time = time.time()
            
            if detected_tables > 0:
                logger.info(f"Tabelas confirmadas em {pdf_path}. Total: {detected_tables} tabelas. Tempo: {end_time - start_time:.2f}s")
                return True
            else:
                logger.warning(f"Nenhuma tabela encontrada em {pdf_path}. Tempo: {end_time - start_time:.2f}s")
                return False

    except Exception as e:
        logger.error(f"Erro ao detectar tabelas em {pdf_path}: {str(e)}")
        return False
