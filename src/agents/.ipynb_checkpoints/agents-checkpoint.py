import os
from crewai import Agent
from langchain_ollama import ChatOllama
from src.tools.pubmed_tools import search_pubmed, fetch_article_details

# Ollama LLM (no litellm needed)
ollama_llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    temperature=0.1,
)


def create_researcher() -> Agent:
    return Agent(
        role="Healthcare Literature Researcher",
        goal="Search PubMed for relevant and recent academic articles on the query. Use MeSH terms and filters.",
        backstory="Expert biomedical librarian with 15 years building PubMed strategies for systematic reviews.",
        tools=[search_pubmed, fetch_article_details],
        llm=ollama_llm,
        verbose=True,
        max_iter=4,
    )


def create_analyzer() -> Agent:
    return Agent(
        role="Clinical Evidence Analyzer",
        goal="Analyze articles: extract study design, population, interventions, outcomes, trends across studies.",
        backstory="Clinical epidemiologist who co-authored 50+ systematic reviews.",
        llm=ollama_llm,
        verbose=True,
    )


def create_validator() -> Agent:
    return Agent(
        role="Evidence Quality Validator",
        goal="Grade evidence (Level 1: RCT, Level 2: Cohort, Level 3: Case study). Flag biases, contradictions.",
        backstory="Biostatistician who peer-reviewed for NEJM, JAMA, Lancet.",
        llm=ollama_llm,
        verbose=True,
    )


def create_reporter() -> Agent:
    return Agent(
        role="Executive Healthcare Reporter",
        goal="Write Markdown executive report: Background, Findings, Evidence Quality, Implications, Limitations, Recommendations.",
        backstory="Medical writer for hospital executives and policymakers.",
        llm=ollama_llm,
        verbose=True,
    )
