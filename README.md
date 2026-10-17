---
title: BoloBharo
emoji: 🎙️
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
---

# 🎙️ BoloBharo: *bolo, form bharo*

**BoloBharo** is a voice-first Indian form-filling agent built on **Sarvam AI** and **Gradio**[cite: 1]. Users can upload any form image or PDF (or use the built-in 8-field sample form) and fill it out entirely by speaking in 10 Indian languages plus English[cite: 1].

## ✨ Features

* **Multilingual Voice Interface:** Supports Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Punjabi, Malayalam, Odia, and English (`en-IN`)[cite: 1].
* **Document Digitization (Sarvam Vision):** Upload a PDF, PNG, or JPG form to automatically extract up to 12 fillable fields and translate their labels into the chosen language[cite: 1].
* **Code-Mixed Speech Recognition (`saaras:v4`):** Transcribes spoken answers accurately even when users mix English and native languages[cite: 1].
* **Smart Extraction & Self-Correction (`sarvam-105b`):** Normalizes spoken dates (`DD/MM/YYYY`), phone numbers, and PIN codes into structured digits, writes names in both native and Roman scripts, asks clarifying follow-ups when uncertain, and lets users verbally correct previously filled fields[cite: 1].
* **Spoken Prompts & Read-Back (`bulbul:v3`):** Reads each question aloud and summarizes the entire completed form at the end for confirmation[cite: 1].
* **Export Ready:** View live progress in a table, print the formatted HTML summary, or download the structured JSON output[cite: 1].

## 🛠️ Tech Stack

* **Frontend / UI:** [Gradio](https://www.gradio.app/) (`>=4.44.0`)[cite: 1, 3]
* **AI Models (via [Sarvam AI SDK](https://dashboard.sarvam.ai/admin) `>=0.1.33`)[cite: 1, 2, 3]:**
  * **Document AI (`doc_ai`):** Form OCR & markdown extraction[cite: 1]
  * **Speech-to-Text:** `saaras:v4` (codemix mode)[cite: 1]
  * **LLM:** `sarvam-105b`[cite: 1]
  * **Text-to-Speech:** `bulbul:v3`[cite: 1, 2]
  * **Translation:** Sarvam Text Translate[cite: 1]

## 🚀 Quickstart (Run Locally)

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/bolobharo.git
cd bolobharo
```

### 2. Install dependencies
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set your Sarvam AI API Key
Get your API subscription key from the [Sarvam AI Dashboard](https://dashboard.sarvam.ai/admin) and set it as an environment variable (or paste it directly into the UI)[cite: 1, 2]:
```bash
export SARVAM_API_KEY="your_api_key_here"
```

### 4. (Optional) Generate Sample Audio Files
To test the app without a microphone, generate pre-recorded `.wav` answers in Hindi (`samples/hi-IN/`) and Tamil (`samples/ta-IN/`)[cite: 2]:
```bash
python make_samples.py
```

### 5. Launch the app
```bash
python app.py
```
Open **`[http://127.0.0.1:7860](http://127.0.0.1:7860)`** in your browser.

## 📂 Project Structure

* `app.py` — Main Gradio application and Sarvam AI workflow[cite: 1]
* `make_samples.py` — Script to generate mic-free demo WAV answers in Hindi and Tamil[cite: 2]
* `requirements.txt` — Python dependencies (`gradio`, `sarvamai`, `requests`)[cite: 3]
* `README.md` — Project documentation