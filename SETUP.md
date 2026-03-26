# LLM Firewall Setup and Execution Guide

This guide provides step-by-step instructions on how to set up, install dependencies, and run the LLM Firewall project.

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- **Python 3.8 or higher**: [Download Python](https://www.python.org/downloads/)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **Groq API Key**: You need an API key from [Groq](https://console.groq.com/) to use the LLM features.

## Step 1: Clone the Repository

Open your terminal or command prompt and run:
```bash
git clone https://github.com/Dhanyasree-02/LLM-Firewall-.git
cd LLM-Firewall-
```

## Step 2: Set Up a Virtual Environment (Recommended)

It is highly recommended to use a virtual environment to manage dependencies:

### Windows:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Required Dependencies

Install the necessary Python packages using `pip`:
```bash
pip install -r requirements.txt
```

The core dependencies include:
- `fastapi` & `uvicorn`: For the backend API.
- `streamlit`: For the frontend dashboard.
- `groq`: For LLM integration.
- `transformers` & `torch`: For the classification model (BART MNLI).

## Step 4: Configure Environment Variables

You need to set your Groq API key as an environment variable.

### Windows (PowerShell):
```powershell
$env:GROQ_API_KEY="your_api_key_here"
```

### macOS/Linux (Bash):
```bash
export GROQ_API_KEY="your_api_key_here"
```

## Step 5: Run the Application

The application consists of a backend and a frontend. You need to run both.

### 1. Start the Backend API:
In one terminal window, run:
```bash
python -m uvicorn api:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### 2. Start the Frontend Dashboard:
Open a **new** terminal window (keeping the backend running) and run:
```bash
streamlit run app.py
```
The dashboard will open in your default web browser (usually at `http://localhost:8501`).

## How it Works
1. **Input**: Enter a prompt in the Streamlit UI.
2. **Classification**: The prompt is sent to the FastAPI backend, where it is classified into categories (e.g., Safe, Jailbreak, Toxic, PII Leak).
3. **Firewall**: If the prompt is deemed "Unsafe", it is blocked.
4. **LLM Response**: If the prompt is "Safe", it is forwarded to the Groq LLM to generate a response.
