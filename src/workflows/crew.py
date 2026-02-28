from crewai import Crew, Task, Process
from src.agents.agents import (
    create_researcher, create_analyzer,
    create_validator, create_reporter
)


def build_healthcare_crew(query: str) -> Crew:
    researcher = create_researcher()
    analyzer = create_analyzer()
    validator = create_validator()
    reporter = create_reporter()

    task_research = Task(
        description=(
            f"Search PubMed for articles on: '{query}'. "
            "Use multiple search queries with relevant MeSH terms. "
            "Retrieve at least 10 articles. Return titles, PMIDs, journals, years, and abstracts."
        ),
        expected_output=(
            "A numbered list of articles with PMID, title, journal, year, and a 2-3 sentence abstract summary."
        ),
        agent=researcher,
    )

    task_analyze = Task(
        description=(
            "Using the articles from the researcher, analyze each one. "
            "Extract: study design, sample size, interventions, primary outcomes, "
            "and key numeric results. Then synthesize cross-study trends."
        ),
        expected_output=(
            "A structured analysis with per-study breakdowns and a cross-study synthesis section "
            "identifying key trends, metrics, and patterns."
        ),
        agent=analyzer,
        context=[task_research],
    )

    task_validate = Task(
        description=(
            "Review the analyzer's output. For each study, assign an evidence level "
            "(Level 1: RCT/Meta-analysis, Level 2: Cohort, Level 3: Case study/Opinion). "
            "Flag any contradictions or methodological weaknesses. "
            "Assign an overall confidence score (0-100%) to the synthesis."
        ),
        expected_output=(
            "A validated evidence table with evidence levels, quality flags, and an overall "
            "confidence score with justification."
        ),
        agent=validator,
        context=[task_analyze],
    )

    task_report = Task(
        description=(
            "Write a professional executive report in Markdown based on all prior agent outputs. "
            "Structure: ## Background, ## Methods, ## Key Findings (with bullet points and numbers), "
            "## Evidence Quality, ## Clinical Implications, ## Limitations, ## Recommendations, ## References. "
            "Be concise but complete. Suitable for a hospital executive or clinical director."
        ),
        expected_output=(
            "A complete, well-formatted Markdown executive report with all sections filled in, "
            "including inline PMID references."
        ),
        agent=reporter,
        context=[task_research, task_analyze, task_validate],
    )

    crew = Crew(
        agents=[researcher, analyzer, validator, reporter],
        tasks=[task_research, task_analyze, task_validate, task_report],
        process=Process.sequential,
        verbose=True,
    )

    return crew
