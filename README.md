# 🛡️ Private Document QA Assistant

![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker)
![License](https://img.shields.io/badge/license-MIT-green)
![Privacy](https://img.shields.io/badge/privacy-100%25%20local-informational)
![LLM](https://img.shields.io/badge/LLM-phi--2-red)
![Build](https://img.shields.io/badge/build-passing-brightgreen)

A **fully local**, **privacy-compliant** AI-powered assistant that allows users to upload `.txt`, `.pdf`, or `.docx` files and ask natural language questions about their content. Built for use in **schools, nonprofits, and internal enterprise environments** with no internet dependency.

Powered by:
- 🧠 **MiniLM** for embeddings  
- 📚 **FAISS** for semantic search  
- 🤖 **phi-2** via `llama-cpp-python` for offline inference  
- 🎙️ Optional TTS with Piper for spoken answers  
- 🔒 No data leaves your device — 100% offline capability

---

## ✅ Features

- 🚀 **FastAPI Backend** for modular and secure APIs  
- 🧾 Upload and index `.txt`, `.pdf`, `.docx` documents  
- 🧠 Semantic Embedding using `sentence-transformers/paraphrase-MiniLM-L3-v2`  
- 🔍 Local vector search via **FAISS**  
- 🤖 Answer generation with **phi-2** (quantized `.gguf` format)  
- 🗣️ Voice response using **Piper TTS** (optional)  
- 🖥️ Interactive **Gradio UI** with 3 tabs:
  - Upload & Index
  - Ask Questions
  - Policy Review Agent  
- 📊 Excel reports generated for policy analysis via Pandas  
- 🐳 Fully Dockerized  
- 🔐 Works entirely offline — no external APIs or cloud dependencies  

---

## 🗂️ Project Structure

```
private-doc-qa/
├── app/
│   ├── api/                   # API logic
│   ├── core/                  # Embedding, FAISS, LLM interface
│   ├── agent/                 # Policy review logic
│   ├── utils/                 # File reader, text chunker
├── models/                   # LLM models and TTS
├── vector_store/             # FAISS index files
├── reports/                  # Excel reports from policy agent
├── ui.py                     # Gradio interface
├── Dockerfile                # Docker setup
├── requirements.txt
├── README.md
```

---

## 🚀 How to Run Locally

### Prerequisites

- Python 3.10+
- pip
- ffmpeg
- [Optional] Docker Desktop (Mac/Windows/Linux)

---

### ⚙️ Setup (Non-Docker)

```bash
git clone https://github.com/VinayMattapalli/PRIVATE-DOCUMENT-QA.git
cd PRIVATE-DOCUMENT-QA
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python ui.py
```

Access at: [http://127.0.0.1:7860](http://127.0.0.1:7860)

---

### 🐳 Docker Run (Recommended)

```bash
docker build -t private-doc-qa .
docker run -p 7860:7860 private-doc-qa
```

---

## 🔊 Piper TTS (Optional)

To enable voice responses, download the Piper model:
- `en_US-danny-low.onnx`
- `en_US-danny-low.onnx.json`

Place them in:  
```bash
models/tts/
```

---

## 📄 Supported Document Formats

- `.txt`  
- `.pdf`  
- `.docx`  

---

## 🛡️ Privacy & Security

✅ **No GPT, no cloud API**  
✅ **Local-only execution**  
✅ **Works without internet access**  
✅ **Safe for internal, confidential use cases**

---

## 👨‍💻 Author

**Vinay Mattapalli**  
🔗 [GitHub](https://github.com/VinayMattapalli)  
🔐 AI Developer | Privacy-first LLM Solutions

---
