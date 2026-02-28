import os
from datetime import datetime
from dotenv import load_dotenv
from crewai import Crew, Agent, Task

load_dotenv()

def main():
    query =  "breast cancer screening guidelines 2026"
    
    # Direct PubMed (already working!)
    from src.tools.pubmed_direct import search_pubmed
    print(" Searching PubMed...")
    articles = search_pubmed(query)
    print(f"Found {len(articles)} articles")
    
    for i, article in enumerate(articles[:3], 1):
        print(f"{i}. {article['title']} ({article['year']})")
    
    # 4 Agents - STRING model name (no ChatOllama object)
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
    
    # Tasks WITH expected_output
    task1 = Task(
        description=f"""Review these {len(articles)} PubMed articles:

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
    
    print("\n 4‑Agent System Running...\n")
    crew = Crew(
        agents=[researcher, analyzer, validator, reporter],
        tasks=[task1, task2, task3, task4],
        verbose=True
    )
    
    result = crew.kickoff()
    
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"reports/report_{timestamp}.md"
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# Healthcare Research Agent\n\n**Query:** {query}\n**Generated:** {datetime.now()}\n\n```\n{result}\n```")
    
    print(f"\n PROJECT COMPLETE!")
    print(f" Report: {report_path}")

if __name__ == "__main__":
    main()
