# debug_classifier.py
from src.classification.pdf_classifier import PDFClassifier
from src.utils.logger import setup_logger
import logging

setup_logger(__name__)
logger = logging.getLogger(__name__)

def debug_single_file(file_path: str):
    """Testa classificação com debug detalhado"""
    config = {
        'pages_to_sample': 3,
        'min_text_length': 10,
        'dpi': 300
    }
    
    classifier = PDFClassifier(config)
    
    print(f"\n🔍 Iniciando análise detalhada de: {file_path}")
    result = classifier.classify(file_path)
    analysis = classifier.get_last_analysis()
    
    print("\n📊 Resultado:")
    print(f"Tipo detectado: {result}")
    print("\n🔧 Análise técnica:")
    for key, value in analysis.items():
        print(f"- {key}: {value}")
    
    print("\n💡 Dicas:")
    if result == "unprocessable":
        print("• Tente aumentar o 'dpi' para 400 ou mais")
        print("• Ajuste 'min_text_length' no config")
        print("• Verifique a imagem pré-processada em data/debug_images/")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        debug_single_file(sys.argv[1])
    else:
        print("Uso: python debug_classifier.py caminho/do/arquivo.pdf")