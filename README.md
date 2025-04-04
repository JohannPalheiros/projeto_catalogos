# 📄 Projeto de Extração e Classificação de Conteúdo de PDFs

Este projeto tem como objetivo extrair informações de catálogos de peças em PDF, classificando os arquivos conforme o tipo de conteúdo e organizando os dados extraídos para fácil consulta e futura ingestão em sistemas.

---

## 🚀 Funcionalidades

- **Classificação de PDFs:**
  - `text_only`: PDF com texto selecionável.
  - `image_only`: PDF com imagens (necessita OCR).
  - `mixed`: PDF com texto selecionável e imagens.
  - `tables`: PDF contendo tabelas.

- **Extração de Conteúdo:**
  - Utiliza métodos diretos, OCR e extração mista para gerar arquivos `.txt` com o conteúdo de cada PDF.

- **Organização e Logs:**
  - Todos os eventos do processamento são registrados em `data/output/processing.log`.
  - Arquivos `.txt` são salvos em `data/output/text/<tipo>`, separados por tipo de classificação (`tables`, `mixed`, `image_only`, `text_only`).

---

## 📁 Estrutura do Projeto

```
├── data/                 # Arquivos de entrada, saída e intermediários
│   ├── input/            # PDFs pendentes e processados
│   ├── output/           # Textos extraídos, logs, imagens tratadas
│   └── interim/          # Arquivos intermediários
├── src/                  # Código-fonte principal
│   ├── classification/   # Lógica de classificação de PDFs
│   ├── extraction/       # Extração de texto e OCR
│   ├── processing/       # Pós-processamento
│   ├── api/              # Endpoints para consulta (se implementado)
│   └── utils/            # Funções auxiliares (logger, arquivos, etc.)
├── models/               # Modelos (OCR, ML, NER)
├── tests/                # Testes automatizados
├── requirements.txt      # Bibliotecas necessárias
├── config.yaml           # Configurações do pipeline
└── README.md             # Este arquivo :)
```

---

## 🧰 Requisitos

- **Python 3.x**
- **Poppler** – Necessário para converter PDFs em imagens.
- **Tesseract OCR** – Necessário para reconhecer texto em imagens (OCR).
- Instale também as dependências com `pip install -r requirements.txt`.

---

## ⚙️ Instalação do Poppler

O Poppler é essencial para converter PDF em imagem antes do OCR.

- **Linux / macOS:**
  ```bash
  sudo apt install poppler-utils        # Debian/Ubuntu
  brew install poppler                 # macOS
  ```

- **Windows:**
  O site oficial **não fornece binários para Windows**, use:
  👉 [https://github.com/oschwartz10612/poppler-windows/releases](https://github.com/oschwartz10612/poppler-windows/releases)

  Após extrair o `.zip`, adicione a pasta `Library\bin` ao `PATH`. Exemplo:
  ```
  C:\Ferramentas\poppler-xx\Library\bin
  ```

---

## 🧠 Instalação do Tesseract OCR

O Tesseract realiza a leitura de texto via OCR em PDFs com imagens.

- **Windows:**
  Baixe aqui: 👉 [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

  > 💡 Recomendado: marcar "Adicionar ao PATH" na instalação.

  Se não adicionar ao PATH, você pode definir a variável de ambiente `TESSERACT_PATH` com o caminho:
  ```
  C:\Users\SEU_USUARIO\AppData\Local\Tesseract-OCR\tesseract.exe
  ```

- **Linux:**
  ```bash
  sudo apt install tesseract-ocr
  ```

- **macOS:**
  ```bash
  brew install tesseract
  ```

---

## ✅ Verificação de Ambiente

Após instalar tudo, verifique no terminal se está ok:

```bash
tesseract --version
```

---

## ▶️ Como Executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o processamento em lote:
   ```bash
   python src/batch_processor.py
   ```

---

## 📬 Contato

Dúvidas, sugestões ou contribuições? Entre em contato:

- 📧 Email: [jpalheiros@gmail.com](mailto:jpalheiros@gmail.com)  
- 🧑‍💻 GitHub: [JohannPalheiros](https://github.com/JohannPalheiros)
