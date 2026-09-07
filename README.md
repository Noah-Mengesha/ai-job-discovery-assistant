# ai-job-discovery-assistant
Local-first AI job search platform using Python, Streamlit, SQLite, and Ollama to discover, rank, and prepare tailored job applications.
# AI-Powered Job Discovery & Application Assistant

A local-first AI job search platform built to help candidates discover relevant opportunities, evaluate job fit, and prepare tailored application materials. The system combines public job board APIs, a local language model, and a human-in-the-loop review workflow to make the application process more organized and efficient.

## Overview

Searching for jobs across multiple company websites, reviewing qualifications, and tailoring application materials can be repetitive and time-consuming. This project brings those steps into one application while keeping the candidate in control of all final decisions and submissions.

The platform retrieves job postings, filters and stores relevant opportunities, uses AI to evaluate resume-to-job fit, and generates editable application drafts. It also tracks application progress and preserves a verified candidate profile to reduce unsupported or inaccurate AI-generated claims.

## Features

* **Automated Job Discovery:** Retrieves postings from public Greenhouse and Lever APIs, filters by job title and location, and stores deduplicated results.
* **AI Job Ranking:** Uses Ollama to generate 0–100 match scores and assess qualifications, experience, location, and sponsorship eligibility concerns.
* **Verified Candidate Profile:** Stores education, skills, experience, and project facts used to ground AI-generated content.
* **Application Package Generation:** Creates tailored resume content, cover letters, and suggested application answers for candidate review.
* **Human-in-the-Loop Approval:** Allows users to edit and approve application materials before opening the official application page.
* **Application Tracking:** Records application statuses, including applied, screening, interview, offer, and rejected.
* **Scheduled Discovery:** Supports recurring job searches while the local scheduler is running.

## Technology Stack

| Category             | Technologies                       |
| -------------------- | ---------------------------------- |
| Programming Language | Python                             |
| User Interface       | Streamlit                          |
| Database             | SQLite                             |
| Local AI             | Ollama, Llama 3.1                  |
| API Integration      | REST APIs, Requests                |
| Job Sources          | Greenhouse API, Lever API          |
| Data Processing      | JSON, HTML parsing, SQLite queries |

## How It Works

1. **Discover:** The application retrieves job postings from configured company career boards.
2. **Filter:** Job titles, locations, and seniority preferences are applied, and duplicate postings are removed.
3. **Rank:** Ollama compares job descriptions against verified candidate facts and produces structured match evaluations.
4. **Prepare:** The user selects a job and generates tailored application materials.
5. **Review:** The candidate edits and explicitly approves the application package.
6. **Apply:** The official application link is opened for the user to complete and submit.
7. **Track:** Application progress is recorded in the local database.

## Getting Started

### Prerequisites

* Python 3.11 or later
* Git
* Ollama
* A computer capable of running the selected local language model

### 1. Clone the repository

```bash
git clone https://github.com/Noah-Mengesha/ai-job-discovery-assistant.git
cd ai-job-discovery-assistant
```

Replace the repository URL if you choose a different name.

### 2. Create a virtual environment

On Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Install and configure Ollama

Install Ollama from its official website, then download the model:

```bash
ollama pull llama3.1:8b
```

Make sure Ollama is running before using the AI features.

### 4. Initialize the database

```bash
python seed.py
```

Before publishing this repository, replace any personal seed data with fictional example data. Users should enter their own verified profile information.

### 5. Start the application

```bash
streamlit run app.py
```

Open the local address displayed in the terminal, typically:

```text
http://localhost:8501
```

### 6. Configure job discovery

Open the Discovery page and add supported Greenhouse board identifiers or Lever site identifiers. Configure job title keywords, location preferences, and the search interval, then select **Search now**.

To run recurring discovery in a separate terminal:

```bash
python scheduler.py
```

The scheduler runs locally and stops when its process is closed or the computer shuts down.

## Project Structure

```text
auto_apply_job_finder/
├── app.py                 # Main Streamlit application
├── ai.py                  # Ollama integration
├── db.py                  # SQLite database initialization
├── seed.py                # Example profile data
├── discovery.py           # Job board API retrieval and filtering
├── discovery_page.py      # Discovery interface
├── ranking.py             # AI job evaluation and scoring
├── ranking_page.py        # Ranking interface
├── scheduler.py           # Recurring discovery worker
├── search_config.json     # Job search configuration
├── requirements.txt       # Python dependencies
└── README.md
```

## Current Limitations

* Match scores are AI-generated estimates, not hiring probabilities.
* Sponsorship and work authorization information must be verified with the employer and appropriate official sources.
* The system does not automatically submit applications or complete third-party application forms.
* Scheduled discovery requires the local worker to remain running.
* The SQLite database is local and is not configured for multi-user cloud hosting.
* AI-generated materials require human review before use.

## Planned Improvements

* Add a cloud-hosted deployment with persistent storage.
* Expand job source coverage through supported public APIs.
* Improve ranking with structured eligibility filters and evaluation benchmarks.
* Add document export for tailored application packages.
* Measure application preparation time against a manual workflow.
* Improve automated testing and deployment workflows.

## Privacy and Responsible Use

The application is designed to keep candidate information local and use verified facts when generating application materials. Personal databases, private resumes, credentials, and generated application packages should not be committed to a public repository.

The project uses public job board APIs and does not bypass authentication, scrape protected platforms, or submit applications without user approval.

## Author

**Noah Mengesha**
Computer Information Technology, Minnesota State University, Mankato

GitHub: https://github.com/Noah-Mengesha
LinkedIn: https://www.linkedin.com/in/noah-mengesha-63915b265/
