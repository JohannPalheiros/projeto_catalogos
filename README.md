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
- Instale também as dependências com:
  ```bash
  pip install -r requirements.txt
  ```

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

  Após extrair o `.zip` em um diretório da sua preferência, adicione o seguinte caminho ao `PATH` do sistema:
  ```
  C:\Ferramentas\poppler-xx\Library\bin
  ```

---

## 🧠 Instalação do Tesseract OCR

O Tesseract realiza a leitura de texto via OCR em PDFs com imagens.

- **Windows:**
  Baixe aqui: 👉 [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

  > 💡 Recomendado: marcar "Adicionar ao PATH" durante a instalação.

  Caso contrário, defina a variável de ambiente `TESSERACT_PATH` apontando para o executável:
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

## 🔍 Verificação de Ambiente

Após instalar tudo, verifique se está funcionando:

```bash
python -m pip show pytesseract
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
```

---

## ▶️ Como Executar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Coloque os arquivos PDF que deseja processar em:
   ```
   data/input/pending
   ```

3. Execute o processamento em lote:
   ```bash
   python src/batch_processor.py
   ```

---

## 🧹 Funcionamento Interno (Visão Geral)

1. **Classificação**:
   - Verifica se o PDF contém texto, imagens ou tabelas.
2. **Extração**:
   - Usa a melhor abordagem: texto direto, OCR ou mista.
3. **Organização**:
   - Move os arquivos para `data/input/processed/<tipo>`
   - Salva o texto em `data/output/text/<tipo>`
   - Registra logs detalhados em `data/output/processing.log`

---

## ❓ FAQ / Possíveis Erros Comuns

### 1. **Erro: `Tesseract não encontrado!`**
- **Causa:** O Tesseract OCR não está instalado ou não foi adicionado ao `PATH`.
- **Solução:**
  - Instale o Tesseract: [Link para Windows](https://github.com/UB-Mannheim/tesseract/wiki)
  - Ou defina a variável de ambiente `TESSERACT_PATH` com o caminho completo:
    ```
    C:\Users\SEU_USUARIO\AppData\Local\Tesseract-OCR\tesseract.exe
    ```

### 2. **Erro: `PDF não convertido em imagens`**
- **Causa:** O Poppler não está instalado corretamente ou o executável `pdftoppm` não está no `PATH`.
- **Solução:**
  - Use: [https://github.com/oschwartz10612/poppler-windows/releases](https://github.com/oschwartz10612/poppler-windows/releases)
  - Adicione ao PATH:
    ```
    C:\Ferramentas\poppler-xx\Library\bin
    ```

### 3. **Erro: `PermissionError` ao salvar arquivos**
- **Causa:** Um arquivo está aberto ou sendo usado.
- **Solução:** Feche o PDF ou arquivo `.txt` antes de rodar o script.

### 4. **Nenhum texto é extraído**
- **Causa:** PDF corrompido ou imagens sem OCR.
- **Solução:** Verifique se `enable_ocr` está ativado. O log informará se o arquivo foi movido para `quarantine`.

### 5. **Quero reiniciar os testes**
- **Resposta:** Esvazie a pasta `data/output/text/` e mova os arquivos de `data/input/processed/` de volta para `data/input/pending/`
  - Alternativamente, use a flag `--reset` se for implementada.

### 6. **Posso mudar o número de processos paralelos?**
- **Sim!** Por padrão, usamos todos os núcleos da máquina. Para limitar (em PCs mais fracos), edite o parâmetro `max_workers` em `batch_processor.py`.

---

## 📨 Contato

Dúvidas, sugestões ou contribuições? Entre em contato:

- 📧 Email: [jpalheiros@gmail.com](mailto:jpalheiros@gmail.com)  
- 🤝 GitHub: [JohannPalheiros](https://github.com/JohannPalheiros)
- 💼 LinkedIn: [linkedin.com/in/johannpalheiros](https://www.linkedin.com/in/johannpalheiros/)