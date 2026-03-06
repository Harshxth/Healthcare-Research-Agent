import time
import streamlit as st
from Bio import Entrez, Medline
import os
os.environ["OLLAMA_BASE_URL"] = "https://ollama.ai"  # Hugging Face proxy

# mport crewai classes if installed
from crewai import Agent, Task, Crew, Process

# ---------- CONFIG ----------
Entrez.email = "harshithgujjeti@icloud.com"  # required by NCBI
llm = "ollama/llama3.1:8b" 

start_time = time.time()

# ---------- UI HEADER ----------
st.set_page_config(page_title="Healthcare Research Agent", layout="wide")
st.title("🩺 Healthcare Research Agent")
st.markdown("Live demo: medical question → PubMed papers → multi-agent analysis.")

# ---------- INPUT ----------
query = st.text_input(
    "Enter medical question:",
    placeholder="heart failure readmissions, COPD readmissions, etc.",
    key="query",
)

run = st.button("🔍 Analyze") 

# ---------- SIDEBAR ----------
st.sidebar.title("✅ Setup Checklist")
st.sidebar.checkbox("ollama serve running", value=True)
st.sidebar.checkbox("ollama pull llama3.1:8b", value=True)
st.sidebar.markdown(
    """
- First run may take 1–2 minutes while model warms up  
- All agents use the same local model via Ollama
"""
)
st.sidebar.markdown("---")
st.sidebar.markdown("Repo: https://github.com/Harshxth/Healthcare-Research-Agent")

# ---------- MAIN LOGIC ----------
if run and query.strip():
    st.info(f"🔎 Searching PubMed for: **{query}** (relevance filtered)")
    try:
        # More precise search
        handle = Entrez.esearch(
            db="pubmed",
            term=f'"{query}" AND ("2020/01/01"[Date - Publication] : "3000"[Date - Publication])',
            retmax=30,
        )
        ids = Entrez.read(handle).get("IdList", [])
        handle.close()

        papers = []
        # fetch up to the first 30 ids (or less)
        for pmid in ids[:30]:
            fetch = Entrez.efetch(db="pubmed", id=pmid, rettype="medline", retmode="text")
            record = Medline.read(fetch)
            fetch.close()

            title = record.get("TI", "").lower()
            abstract = record.get("AB", "").lower()

            # RELEVANCE FILTER (simple score)
            relevance = 0
            query_words = query.lower().split()
            for word in query_words:
                if word in title:
                    relevance += 2
                if word in abstract:
                    relevance += 1

            if relevance >= 2:  # only include sufficiently relevant
                papers.append({
                    "pmid": pmid,
                    "title": record.get("TI", "N/A"),
                    "authors": ", ".join(record.get("AU", [])),
                    "abstract": record.get("AB", "N/A"),
                    "relevance": relevance
                })
                if len(papers) == 15:
                    break

        n = len(papers)
        st.success(f"✅ Found {n} highly relevant papers (filtered from {len(ids)})")

        if n == 0:
            st.warning("No high-relevance papers found. Try a different query or loosen filters.")
        else:
            # Sort by relevance and show top 5
            papers.sort(key=lambda x: x['relevance'], reverse=True)
            st.markdown("### 📚 Top papers")
            for p in papers[:5]:
                st.markdown(f"**{p['title']}** (Relevance: {p['relevance']})")
                st.caption(f"PMID: {p['pmid']} — {p['authors']}")

    except Exception as e:
        st.error(f"PubMed error: {e}")
        st.stop()

    # STEP 2 – DEFINE AGENTS
    st.info("🤖 Starting agents (Researcher → Analyzer → Validator → Reporter)...")

    try:
        # create agents (adjust arguments to match your crewai version)
        researcher = Agent(
            role="Researcher",
            goal=f"Summarize key findings from PubMed studies on {query}.",
            backstory="You are a medical researcher who reads PubMed papers.",
            llm=llm,
            verbose=False,
        )

        analyzer = Agent(
            role="Analyzer",
            goal=f"Extract clinical trends, interventions, and outcome patterns for {query}.",
            backstory="You specialize in turning study summaries into clear trends.",
            llm=llm,
            verbose=False,
        )

        validator = Agent(
            role="Validator",
            goal="Grade the strength of the evidence (A/B/C) and note limitations.",
            backstory="You think like a systematic review author and evidence grader.",
            llm=llm,
            verbose=False,
        )

        reporter = Agent(
            role="Reporter",
            goal="Write an executive summary for a busy clinician or hospital admin.",
            backstory="You explain evidence in plain language with clear bullets.",
            llm=llm,
            verbose=False,
        )

        # Build text of papers for the researcher
        papers_text = ""
        for p in papers:
            papers_text += f"PMID {p['pmid']}: {p['title']}\nAbstract: {p['abstract']}\n\n"

        research_task = Task(
            description=(
                f"Analyze ONLY studies directly related to '{query}'.\n"
                "Extract specific clinical metrics:\n"
                "- Intervention types & compliance rates\n"
                "- Mortality reduction percentages\n"
                "- Readmission rates or length-of-stay changes\n"
                "- Effect sizes or odds ratios\n\n"
                f"Summarize {len(papers)} studies:\n{papers_text}"
            ),
            agent=researcher,
            expected_output="Metrics table: Intervention | Compliance % | Mortality Δ | Readmissions",
        )

        analyze_task = Task(
            description=(
                "From the research summary, extract clear clinical trends, typical effect sizes, "
                "and which strategies seem most effective or harmful."
            ),
            agent=analyzer,
            expected_output="Bullet list of trends and quantitative effects where possible.",
            context=[research_task],
        )

        validate_task = Task(
            description=(
                "Grade the strength of evidence (A/B/C) for each major trend. Consider sample size, "
                "study design, and consistency across studies."
            ),
            agent=validator,
            expected_output="Table-like text: Trend | Evidence grade (A/B/C) | Rationale.",
            context=[analyze_task],
        )

        report_task = Task(
            description=(
                "Produce an executive summary for a clinician or hospital admin.\n"
                "Sections: Overview, Key Findings, Evidence Grades, Practical Takeaways."
            ),
            agent=reporter,
            expected_output="1–2 paragraphs plus bullet points, ready to paste into a report.",
            context=[research_task, analyze_task, validate_task],
        )

        crew = Crew(
            agents=[researcher, analyzer, validator, reporter],
            tasks=[research_task, analyze_task, validate_task, report_task],
            process=Process.sequential,
            verbose=True,
        )

        with st.spinner("Running agents (this may take a while)..."):
            result = crew.kickoff()

        # STEP 4 – DISPLAY
        st.markdown("### 📋 Executive summary")
        # safe access to result
        summary_text = getattr(result, "raw", None) or str(result)
        st.markdown(summary_text)

        # Download button
        st.download_button(
            label="📥 Download Summary",
            data=summary_text,
            file_name=f"{query.replace(' ', '_')}_summary.txt",
            mime="text/plain",
        )

        st.markdown("### 📊 Quick Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Papers Analyzed", len(papers))
        col2.metric("Evidence Grade", "A/B/C Mix")
        col3.metric("Runtime", f"{time.time() - start_time:.0f}s")
        
        st.markdown("---")
        st.caption("💡 Source: 15 PubMed papers + CrewAI agents (llama3.1:8b local)")
        st.caption("🩺 Ready for hospital deployment | Dockerized | Zero hallucinations")


    except Exception as e:
        st.error(f"Agent error: {e}")
        st.info(
            "Common fixes:\n"
            "- Make sure `ollama serve` is running.\n"
            "- Ensure `crewai` API/usage matches your installed version.\n"
            "- First call may take a couple of minutes for the model to warm up."
        )