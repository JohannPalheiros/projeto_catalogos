# Projeto de Extração e Classificação de Conteúdo de PDFs

Este projeto extrai informações de catálogos de peças em PDF, classificando os arquivos conforme o tipo de conteúdo e permitindo a consulta dos dados extraídos.

## Funcionalidades

- **Classificação de PDFs:**
  - **text_only:** PDF com texto selecionável.
  - **image_only:** PDF com imagens (necessita OCR).
  - **mixed:** PDF com texto selecionável e imagens.
  - **tables:** PDF contendo tabelas.

- **Extração de Conteúdo:**
  - Utiliza métodos diretos, OCR e extração mista para converter PDFs em arquivos de texto.

- **Logs e Organização:**
  - Todas as operações são registradas em `data/output/processing.log`.
  - Os arquivos .txt são organizados em subpastas dentro de `data/output/text` de acordo com o tipo de extração.

## Estrutura do Projeto

├── data/ # Dados e arquivos utilizados no projeto
│ ├── input/ # PDFs recebidos (pendentes e processados)
│ ├── output/ # Resultados do processamento (textos, OCR, logs, etc.)
│ └── interim/ # Arquivos intermediários (imagens, arquivos temporários)
├── src/ # Código-fonte do projeto
│ ├── classification/ # Módulos para classificação de PDFs
│ ├── extraction/ # Módulos de extração (texto, OCR, misto)
│ ├── processing/ # Processamento e limpeza pós-extração
│ ├── api/ # API para consulta dos dados extraídos
│ └── utils/ # Funções utilitárias (logger, manipulação de arquivos, etc.)
├── models/ # Modelos de OCR, Machine Learning e NER (se aplicável)
├── tests/ # Testes unitários e de integração
├── requirements.txt # Dependências do projeto
├── config.yaml # Configurações globais
└── README.md # Documentação do projeto

## Requisitos

- **Python 3.x**
- **Dependências:** listadas em `requirements.txt`
- **Poppler:** Necessário para OCR. [Poppler](https://poppler.freedesktop.org/)

### Instalação do Poppler

- **Windows:**  
  Baixe e extraia o Poppler e adicione o diretório `bin` ao PATH.

- **Linux:**  
  ```sh
  sudo apt install poppler-utils

- **macOS:**  
  ```sh
  brew install poppler

### Como Executar:

1. Instale as dependências:
  ```sh
  pip install -r requirements.txt

2. Execute o processamento:
  ```sh
  python src/batch_processor.py

- **Contato**  
Para dúvidas ou sugestões, entre em contato:
Email: jpalheiros@gmail.com
GitHub: https://github.com/JohannPalheiros