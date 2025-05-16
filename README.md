# Azerbaijani Morphology Analyzer

This project provides two interfaces for Azerbaijani morphological analysis using Google Gemini LLM:
- **CLI Tool** (`cli.py`)
- **Web API & Modern Web UI** (`api.py` + `/static`)

All dependencies are managed with [`uv`](https://github.com/astral-sh/uv) (a fast Python package/dependency manager). **Do not use pip.**

---

## 🚀 Quick Start

### 1. Clone the repository
```sh
# Replace <repo_url> and <repo_dir> with your actual values
$ git clone <repo_url>
$ cd <repo_dir>
```

### 2. Set up your virtual environment and install dependencies
```sh
$ uv sync
```

### 3. Add or update packages (if needed)
```sh
$ uv add fastapi google-generativeai pydantic
```

### 4. Set your Gemini API key
You need a Google Gemini API key to use the analyzer.
```sh
$ set GEMINI_API_KEY=your-key-here   # Windows
$ export GEMINI_API_KEY=your-key-here # Linux/macOS
```

---

## 🖥️ CLI Usage (`cli.py`)
Analyze a list of Azerbaijani words from a text file.

### Prepare your input file
- Create a file named `words.txt` (or any `.txt` file)
- Put one Azerbaijani word per line

### Run the CLI
```sh
$ uv run cli.py
```

- The CLI will read from `words.txt` and output analysis to the console or a file (see `cli.py` for options).

---

## 🌐 Web API & UI (`api.py`)
Run a FastAPI server with:
- OpenAPI docs (Swagger UI) for API testing
- A beautiful web UI for interactive analysis

### Start the server
```sh
$ uv run fastapi dev
```

- The server will run at `http://localhost:8000/` by default.

### Use the Web UI
- Open [http://localhost:8000/](http://localhost:8000/) in your browser
- Enter your Gemini API key and words (single, batch, or upload a file)
- View and copy the results interactively

### Use the API directly
- Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation
- Endpoints:
  - `POST /analyze/single` – Analyze one word
  - `POST /analyze/batch` – Analyze a list of words
  - `POST /analyze/upload` – Analyze words from uploaded `.txt` file
  - All endpoints require an `api-key` header with your Gemini API key

---

## 📦 Dependency Management
- This project uses [`uv`](https://github.com/astral-sh/uv) for fast, modern Python dependency management
- **Never use `pip install`**; always use `uv sync` and `uv add`

---

## 🔑 Gemini API Key
- You must obtain a Gemini API key from Google and supply it via environment variable or directly in the web UI/API requests.
- **Never commit your API key to version control!**

---

## 🤝 Contributing & Extending
- PRs and issues welcome!
- Ideas: Add more languages, improve UI/UX, export to CoNLL-U, context-aware analysis, etc.

---

## 📝 License
MIT License. See `LICENSE` file.
