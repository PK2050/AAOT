# Customer Feedback Analyzer

A beginner-friendly local AI project that sends customer feedback to the
Mistral model through Ollama, validates its structured JSON response, and saves
the result to `feedback_result.json`.

No API key or `.env` file is required. Feedback stays on the computer because
the model runs locally.

## Project structure

```text
customer-feedback-analyzer/
|-- .gitignore
|-- README.md
|-- analyzer.py
`-- requirements.txt
```

After setup and the first run, `.venv/` and `feedback_result.json` also exist
locally but are also used by Git.

## Windows setup

Install Python 3.11 or newer from <https://www.python.org/downloads/windows/>
and Ollama from <https://ollama.com/download/windows>. Then open
PowerShell in this folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
ollama pull mistral

http://localhost:11434/ - check ollama is running
```

Verify the setup:

```powershell
python --version
ollama --version
ollama list
```

## Run interactively

```powershell
python analyzer.py
.\.venv\Scripts\python.exe analyzer.py
```

Then enter feedback when prompted.

## Run with feedback on the command line

```powershell
python analyzer.py "The app is easy to use, but it takes too long to load."
```

Choose another output file if desired:

```powershell
python analyzer.py "Checkout crashes every time." --output results\checkout.json
```

## Output shape

```json
{
  "feedback": "The app is easy to use, but it takes too long to load.",
  "sentiment": "mixed",
  "category": "performance",
  "priority": "medium",
  "issue": "The application takes too long to load.",
  "suggested_action": "Profile startup and reduce application load time."
}
```

The program asks Ollama to enforce a JSON schema and validates the response
again with Pydantic before saving it.

## Common errors

- **Cannot connect to Ollama:** start the Ollama application and try again.
- **Model not found:** run `ollama pull mistral`.
- **PowerShell blocks activation:** run the virtual environment's Python
  directly, for example `.\.venv\Scripts\python.exe analyzer.py`.
