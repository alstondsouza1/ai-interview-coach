# AI Interview Coach

AI Interview Coach is a Streamlit web application that turns a student's
resume and a job description into a focused interview practice session. It is
designed for internships and entry-level software engineering roles.

The app works with an OpenAI-compatible API for personalized questions and
feedback. It also includes a local fallback mode, so the main workflow can be
demonstrated without an API key.

## Features

- Upload and extract text from a PDF resume
- Paste a target job description
- Detect common software engineering and teamwork skills
- Compare resume skills with job requirements
- Display matched skills, missing skills, and a match percentage
- Generate technical, behavioral, and situational questions
- Write and submit answers inside the app
- Receive a score, strengths, weaknesses, and improvement recommendations
- Load a sample student profile for a quick demonstration
- Use a responsive Streamlit interface on desktop or mobile
- Continue in local coaching mode if no AI provider is configured

## Project Structure

```text
ai-interview-coach/
├── app.py                         # Streamlit entry point
├── src/
│   ├── ai_client.py               # OpenAI-compatible API wrapper
│   ├── answer_evaluator.py        # AI and local answer scoring
│   ├── config.py                  # Environment configuration
│   ├── models.py                  # Shared data classes
│   ├── question_generator.py      # AI and local question generation
│   ├── resume_parser.py           # PDF validation and text extraction
│   ├── skill_analysis.py          # Skill detection and comparison
│   └── ui.py                      # Streamlit components and styling
├── sample_data/
│   ├── sample_job_description.txt
│   └── sample_resume.txt
├── tests/
├── .env.example
├── requirements.txt
└── requirements-dev.txt
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/alstondsouza1/ai-interview-coach.git
cd ai-interview-coach
```

### 2. Create a virtual environment

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

For development and tests:

```bash
pip install -r requirements-dev.txt
```

### 4. Configure the AI provider

Copy the example environment file:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Update `.env`:

```dotenv
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

`OPENAI_BASE_URL` and `OPENAI_MODEL` can be changed for another provider that
supports the OpenAI chat completions interface. Some providers do not support
JSON response mode. If a provider returns an error, the app explains the issue
and uses its local fallback for that request.

Do not commit `.env` or Streamlit secrets to Git.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL shown in the terminal, normally
`http://localhost:8501`.

## Using the App

1. Upload a text-based PDF resume.
2. Paste the complete job description.
3. Select **Analyze resume and build interview**.
4. Review strengths and missing requirements in **Resume match**.
5. Open **Practice interview** and answer each question.
6. Select **Get feedback** to receive a score and revision advice.

To explore the app without a PDF, select **Load sample student profile** in
the sidebar. The sample files are fictional and safe to edit.

## Local and AI Modes

### AI mode

When `OPENAI_API_KEY` is configured, the app sends relevant resume, job, and
answer text to the configured API provider. The model creates personalized
questions and detailed answer feedback.

### Local coaching mode

Without an API key, the app still:

- Extracts and compares skills
- Generates six practice questions
- Scores answers using detail, examples, ownership, and results
- Suggests a stronger answer structure

Local scores are simple coaching signals and should not be treated as hiring
predictions.

## Tests

Run the test suite:

```bash
pytest -q
```

The tests cover invalid uploads, skill aliases, skill-gap calculations,
question category balance, short-answer validation, and local answer scoring.

## Design Notes

- PDF files are limited to 5 MB and 10 pages.
- Scanned image-only PDFs require OCR before upload.
- Resume and prompt text is truncated before API requests to limit payload size.
- Skill matching uses a readable catalog in `src/skill_analysis.py`.
- AI output is validated before it is displayed.
- Provider failures automatically fall back to deterministic local behavior.
- The application does not store resumes in a database.

## Suggested Student Commit History

The repository is built in small commits that are easy to explain in a class,
portfolio review, or hackathon:

```text
chore: set up project structure and sample data
feat: parse resumes and compare job skills
feat: generate questions and evaluate answers
feat: build the Streamlit interview coaching interface
docs: add setup and usage guide
```

This keeps each commit focused on one understandable part of the project.

## Future Improvements

- Add OCR for scanned resumes
- Add speech recording and transcription
- Save practice history in a database
- Add charts for progress across multiple sessions
- Expand skill catalogs for data, cybersecurity, and product roles
- Add authentication before deploying for multiple users

## License

This project is available under the [MIT License](LICENSE).
