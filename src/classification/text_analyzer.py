import PyPDF2

def has_selectable_text(pdf_path: str, threshold: float = 0.7) -> bool:
    """Verifica se o PDF contém texto selecionável"""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text_pages = 0
        for page in reader.pages[:3]:  # Amostra as 3 primeiras páginas
            if page.extract_text():
                text_pages += 1
        return (text_pages / len(reader.pages[:3])) >= threshold