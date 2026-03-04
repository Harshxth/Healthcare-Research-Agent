import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from crewai import Crew, Agent, Task
from src.tools.pubmed_direct import search_pubmed

load_dotenv()

# ---- CUSTOM QUERY HERE ----
query = sys.argv[1] if len(sys.argv) > 1 else "heart failure readmissions"
# ----------------------------

def main():
    print(f"🔍 Searching PubMed: {query}")
    articles = search_pubmed(query)
    print(f"Found {len(articles)} articles")

    researcher = Agent(
        role="Healthcare Researcher",
        goal="Review PubMed articles.",
        backstory="Medical research specialist.",
        llm="ollama/llama3.1:8b",
        verbose=True,
    )
    analyzer = Agent(
        role="Evidence Analyzer",
        goal="Extract insights from research.",
        backstory="Clinical research expert.",
        llm="ollama/llama3.1:8b",
        verbose=True,
    )
    validator = Agent(
        role="Evidence Validator",
        goal="Assess evidence quality.",
        backstory="Medical quality expert.",
        llm="ollama/llama3.1:8b",
        verbose=True,
    )
    reporter = Agent(
        role="Executive Reporter",
        goal="Write healthcare report.",
        backstory="Medical writer.",
        llm="ollama/llama3.1:8b",
        verbose=True,
    )

    task1 = Task(
        description=f"""Review {len(articles)} PubMed articles about '{query}':
{chr(10).join([f"- {a['title']} ({a['year']})" for a in articles[:8]])}""",
        expected_output="Research summary with key studies.",
        agent=researcher,
    )
    task2 = Task(
        description="Analyze clinical findings and trends.",
        expected_output="Structured analysis.",
        agent=analyzer,
        context=[task1],
    )
    task3 = Task(
        description="Grade evidence quality (Level 1-3).",
        expected_output="Quality assessment.",
        agent=validator,
        context=[task2],
    )
    task4 = Task(
        description="Write executive Markdown report.",
        expected_output="Complete report.",
        agent=reporter,
        context=[task1, task2, task3],
    )

    crew = Crew(
        agents=[researcher, analyzer, validator, reporter],
        tasks=[task1, task2, task3, task4],
        verbose=True
    )

    result = crew.kickoff()

    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = query.replace(" ", "_")[:30]
    report_path = f"reports/{safe_query}_{timestamp}.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Healthcare Research Report\n\n**Query:** {query}\n**Date:** {datetime.now()}\n\n{result}")

    print(f"\n Done! Report: {report_path}")

if __name__ == "__main__":
    main()
