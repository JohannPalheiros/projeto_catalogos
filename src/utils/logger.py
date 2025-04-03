import logging
from pathlib import Path
import sys

# Adiciona um nível customizado "SUCCESS"
logging.addLevelName(25, "SUCCESS")
def success(self, message, *args, **kwargs):
    if self.isEnabledFor(25):
        self._log(25, message, args, kwargs)
logging.Logger.success = success

def setup_logger(name: str, log_file: str = "data/output/processing.log") -> logging.Logger:
    """
    Configura um logger com saída para console e arquivo.
    
    Args:
        name: Nome do logger (geralmente __name__)
        log_file: Caminho do arquivo de log (criará pastas automaticamente)
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Cria diretório se não existir
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Formato padrão
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Handler para console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Handler para arquivo (append)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Remove handlers antigos para evitar duplicação
    if logger.hasHandlers():
        logger.handlers.clear()
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Impede propagação para loggers pais
    logger.propagate = False
    
    return logger
