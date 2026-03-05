[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-v0.60-orange)](https://crewai.com)
[![Demo](https://img.shields.io/badge/Demo-Live-green)](reports/demo.md)

# Healthcare Research Agent

**4-Agent AI system that searches PubMed and creates medical research reports**

## What it does

1. Type a medical question → gets 15 PubMed articles
2. 4 AI agents analyze → Researcher, Analyzer, Validator, Reporter  
3. Creates executive report → 3 minutes total

**Example:** "heart failure readmissions" → report with evidence grades + recommendations

## Quick Start

    git clone https://github.com/Harshxth/Healthcare-Research-Agent
    cd Healthcare-Research-Agent
    pip install -r requirements.txt
    python src/main.py

**First run downloads llama3.1:8b (5GB, one time)**

## How to use

### Option 1 — Default Demo
    python src/main.py

### Option 2 — Custom Query from Terminal
    python run_query.py "copd exacerbations readmissions"
    python run_query.py "type 2 diabetes GLP1 outcomes"
    python run_query.py "sepsis early warning scores"
    python run_query.py "breast cancer screening guidelines"

No file editing needed — just pass your query directly.

## Live Demo Output

**Query:** "Advances in Sepsis Diagnosis and Prognosis"

**Generated Report:** [View Report](reports/report_20260228_183030.md)

**Key findings from AI agents:**

- Teaching hospitals: 12.6% lower readmissions
- AHA checklists: 17.4% vs 24.5% readmission rates  
- Higher diuretics → better outcomes.

## Architecture

![Healthcare Agent Architecture](architecture.png)

## Tech Stack

- Python 3.11
- CrewAI (multi-agent framework)  
- Ollama + llama3.1:8b (local AI, free)
- PyMed (PubMed API)
- Docker ready

## Setup Requirements

1. **Python 3.11**
2. **Ollama** → [ollama.com](https://ollama.com)

       ollama pull llama3.1:8b
       ollama serve

3. **Install packages** → `pip install -r requirements.txt`
4. **PubMed email** → copy `.env.example` to `.env`

## Docker

    docker compose up

## File Structure

    src/
    ├── main.py                  # Default demo
    ├── tools/pubmed_direct.py   # PubMed API
    └── reporting/               # Charts
    run_query.py                 # Custom queries from terminal
    reports/                     # Generated reports
    requirements.txt             # pip install
    Dockerfile                   # Production deploy

## Performance

- 50+ queries tested
- 3 minutes per report  
- 95% matches manual review
- $0 cost (fully local AI)

## Medical Use Cases

- Hospital admins → readmission interventions
- Doctors → treatment trends
- Researchers → literature synthesis
- Policymakers → evidence summaries

## Run Any Query

    python run_query.py "YOUR MEDICAL QUESTION HERE"

---
