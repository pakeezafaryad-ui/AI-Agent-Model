# AI Research Agent

A beginner-friendly research app built with Python, CrewAI, Groq, DuckDuckGo search, and Streamlit. Enter a topic and receive a Markdown report with a source list.

## Features

- One CrewAI agent
- Groq model: `openai/gpt-oss-120b`
- DuckDuckGo web search
- Streamlit interface
- Markdown report download
- Basic error messages for common API and search problems

> **Important:** Search results and AI-generated reports can be incomplete or inaccurate. Verify important claims by opening the source links. DuckDuckGo search availability and rate limits can change.

## Requirements

- Windows, macOS, or Linux
- Python 3.11 or 3.12 recommended
- A Groq API key
- Internet access

## 1. Create and activate a virtual environment

Open a terminal in this folder.

### Windows Command Prompt

```bat
py -3.12 -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
```

If you have Python 3.11 rather than 3.12, use `py -3.11 -m venv .venv`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

## 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

If installation fails, copy the complete error from the terminal and review the installed Python version. Do not randomly upgrade individual packages; dependency compatibility matters.

## 3. Configure your Groq API key

1. Create or sign in to your Groq account and obtain an API key from the Groq developer console.
2. Copy `.env.example` to a new file named `.env`.
3. Replace `your_groq_api_key_here` with your actual key.

Your `.env` file should look like this:

```text
GROQ_API_KEY=your_actual_key_goes_here
```

Do not include quotation marks unless required by your environment, and never commit `.env` to GitHub. If a key is exposed, revoke it and create a new one.

## 4. Run the app locally

From the project folder, with the virtual environment active:

```bash
python -m streamlit run app.py
```

Streamlit should open the app in your browser. If it does not, open the local URL printed in the terminal (usually `http://localhost:8501`).

## 5. Deploy to Streamlit Community Cloud

1. Create a GitHub repository and upload the project files.
2. Make sure `.env` is **not** in the repository.
3. Open Streamlit Community Cloud and create a new app from your repository.
4. Select the correct branch and set the main file path to `app.py`.
5. In the app's settings, open **Secrets** and add:

```toml
GROQ_API_KEY = "your_actual_key_goes_here"
```

6. Save the secret and deploy/reboot the app.

Streamlit makes secrets available to the app. This project reads `GROQ_API_KEY` from the environment, so if your deployment environment does not expose Streamlit secrets as environment variables, update `research_agent.py` to read `st.secrets["GROQ_API_KEY"]` in the Streamlit runtime. Never place a real key in source code.

## Project structure

```text
ai_research_agent/
├── app.py
├── research_agent.py
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md
```

## Troubleshooting

- **`python` not found:** Install Python from https://www.python.org/downloads/windows/ and enable “Add Python to PATH” in the installer.
- **`GROQ_API_KEY is missing`:** Check your local `.env` file or your Streamlit Cloud Secrets.
- **401 / invalid key:** Check the key and revoke/replace it if exposed.
- **429 / rate limit:** Wait before trying again.
- **Search failure:** Check your internet connection. DuckDuckGo's unofficial search endpoints can change or temporarily block requests.
- **Package conflict:** Create a fresh virtual environment and reinstall from `requirements.txt`. Save the full error message before changing versions.

## Notes

This starter project uses version ranges to allow compatible package updates. For reproducible deployments, test the installation and then pin the exact versions that work in your environment. The current Groq model availability and CrewAI integration should be checked against their official documentation before deployment.
