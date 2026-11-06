# Herbarium Twin Version 2

AI-assisted herbarium inventory system. Upload photos of herbarium storage boxes, and AI (Google Gemini) reads labels, packets, and handwritten notes to auto-fill metadata — collection area, material type, condition, taxonomic/geographic/collector clues, and more. Records are saved to a local database, and each box gets a printable QR code for physical labeling.

Version 2, Developed in November 2026. Key features include: .csv file export from interface, refinements to individual outputs, database clarification, prompt development, .json export files.

## Features

AI-assisted metadata from box photos via Gemini vision, editable fields, local SQLite database, auto-generated QR codes, ability to browse existing inventory.

## Requirements

- Python 3.10+
- A free [Google Gemini API key](https://aistudio.google.com/apikey)

## Setup

### 1. Clone the repo and enter the folder

```bash
git clone https://github.com/atchaya87/herbarium-twin
cd herbarium-twin
```

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Gemini API key

**Windows (PowerShell) — persists across sessions:**
```powershell
setx GEMINI_API_KEY "your-key-here"
```
> Close and reopen your terminal after running this — `setx` only applies to new terminal sessions.

**Linux / macOS — for the current session:**
```bash
export GEMINI_API_KEY="your-key-here"
```
> To make this permanent, add the line above to your `~/.bashrc` or `~/.zshrc`, then run `source ~/.bashrc`.

### 5. Run the app

```bash
streamlit run runnable.py
```

The app will open at `http://localhost:8501`.

## Project Structure

```
herbarium_twin/
├── runnable.py       # Streamlit app (UI, tabs, save logic)
├── ai_vision.py       # Gemini vision analysis
├── db.py               # SQLite database functions
├── qr_tools.py         # QR code generation
├── requirements.txt
└── README.md
```

## Notes & Known Limitations

- Re-uploading a different set of images under the **same** Unit ID will not automatically re-trigger AI analysis — only a Unit ID change does. If you swap photos, consider changing the Unit ID or manually clearing `st.session_state.ai_results`.
- If the AI response can't be parsed as valid JSON, fields fall back to "Unknown" and the raw response is placed in AI Summary — check "AI Confidence Notes" if results look off.
- On the Gemini free tier, submitted images/text may be used by Google to improve their models. Enable billing on your Google AI Studio account if this is a concern for sensitive collections.
- `herbarium_database.db`, `captured_images/`, and `qr_codes/` are local, generated at runtime, and excluded from version control via `.gitignore` — they are not included when you clone the repo. Make sure to upload local files to the Google Drive.

