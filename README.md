# Interview Prep Studio

Interview Prep Studio is a private, local Streamlit application for students
and early-career job seekers preparing for software engineering interviews.
It turns a PDF resume and job description into a practical preparation
workspace without using an AI model or sending personal data to an API.

## What It Does

### Role-fit dashboard

- Detects the job's role family and seniority
- Finds technical and professional skills in the job post
- Compares job requirements with skills shown on the resume
- Highlights strengths to discuss and gaps to prepare
- Identifies themes such as testing, teamwork, ownership, and communication

### Resume Lab

- Checks for Education, Skills, Projects, and Experience sections
- Counts resume bullets, action-led bullets, and quantified bullets
- Calculates a transparent readiness score
- Recommends the highest-impact resume edits
- Shows the extracted resume text for verification

### Practice Room

- Builds 6 or 9 questions from a curated question bank
- Includes technical, behavioral, and situational questions
- Prioritizes questions related to detected skill gaps
- Filters questions by category
- Scores answers using an explainable rubric
- Shows strengths, weaknesses, and an ordered revision checklist

### Seven-Day Plan

- Creates a role-specific preparation schedule
- Prioritizes the first missing technical skill
- Includes project stories, behavioral practice, and a mock interview
- Tracks completed tasks in the browser session
- Exports the complete preparation report as Markdown

## No AI or API Keys

The application is fully deterministic:

- No OpenAI dependency
- No API key or `.env` file
- No network request for resume analysis or answer scoring
- No external storage or database
- No hidden model deciding the score

The uploaded resume is processed in the active Streamlit session. Scores are
preparation signals, not hiring predictions.

## Answer Scoring

Practice answers are scored from visible writing signals:

| Area | Weight | What the coach checks |
| --- | ---: | --- |
| Structure | 25% | Context, responsibility, action, and result |
| Specificity | 25% | Concrete examples, useful details, and numbers |
| Ownership | 20% | Clear individual actions and decisions |
| Impact | 20% | Outcomes, measurements, feedback, or lessons |
| Clarity | 10% | Useful length and readable sentence structure |

This rubric works best for improving answer structure. It does not verify
whether every technical statement is correct.

## Project Structure

```text
ai-interview-coach/
├── app.py
├── .streamlit/
│   └── config.toml              # Theme and upload settings
├── sample_data/
│   ├── sample_job_description.txt
│   └── sample_resume.txt
├── src/
│   ├── answer_evaluator.py      # Transparent answer rubric
│   ├── job_analysis.py          # Role and job-post analysis
│   ├── models.py                # Shared data classes
│   ├── preparation_plan.py      # Seven-day plan builder
│   ├── question_generator.py    # Curated question selection
│   ├── resume_analysis.py       # Resume readiness checks
│   ├── resume_parser.py         # PDF validation and extraction
│   ├── session_report.py        # Markdown export
│   ├── skill_analysis.py        # Skill extraction and comparison
│   └── ui.py                    # Streamlit interface and styling
├── tests/
├── requirements.txt
└── requirements-dev.txt
```

## Setup

### 1. Clone and enter the project

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

### 4. Start the application

```bash
streamlit run app.py
```

Open `http://localhost:8501` if the browser does not open automatically.

## Quick Demo

1. Select **Load example profile** in the sidebar.
2. Select **Build my preparation workspace**.
3. Review the **Overview** and **Resume Lab** tabs.
4. Write an answer in the **Practice Room** and score it.
5. Check tasks in the **7-Day Plan**.
6. Download the preparation report.

The included resume and job description are fictional sample data.

## Using Your Own Resume

1. Upload a text-based PDF resume under 5 MB.
2. Paste the complete job description, including preferred qualifications.
3. Choose two or three questions per category.
4. Build the workspace.

Scanned image-only PDFs are not supported because the project does not include
OCR. Export the resume from a document editor as a text-based PDF first.

## Development

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run the tests:

```bash
pytest -q
```

The suite covers:

- Empty and invalid PDF uploads
- Skill aliases and skill-gap calculations
- Balanced question selection
- Transparent answer scoring
- Resume structure and quantified bullet checks
- Job-family and internship detection
- Seven-day plan generation
- Markdown report export

## Commit History

The redesign was completed in focused, student-readable commits:

```text
refactor: replace AI services with local coaching
feat: add resume insights and preparation plans
feat: redesign the preparation workspace
test: cover exports and add app defaults
docs: document the private interview prep studio
```

Each commit represents one clear part of the application and can be explained
independently during a project review.

## Limitations

- Skill matching uses a curated software-role catalog.
- Keyword presence does not prove experience or proficiency.
- Answer scoring evaluates structure, not technical truth.
- Session progress is not saved after the Streamlit session ends.
- PDFs must contain extractable text.

## Possible Next Features

- Save multiple practice sessions locally
- Add a timer and full mock-interview mode
- Add more role families such as cybersecurity and product management
- Add optional speech recording without cloud processing
- Support DOCX resumes
- Add local charts showing score improvement over time

## License

This project is available under the [MIT License](LICENSE).
