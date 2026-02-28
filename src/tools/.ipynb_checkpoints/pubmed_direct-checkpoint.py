import os
from pymed import PubMed
from dotenv import load_dotenv

load_dotenv()

pubmed = PubMed(
    tool=os.getenv("PUBMED_TOOL", "HealthcareAgent"),
    email=os.getenv("PUBMED_EMAIL", "user@example.com")
)

def search_pubmed(query: str, max_results=15):
    """Direct PubMed search - no CrewAI tools needed"""
    results = pubmed.query(query, max_results=max_results)
    articles = []
    for article in results:
        data = article.toDict()
        articles.append({
            'pmid': data.get('pubmed_id', 'N/A'),
            'title': data.get('title', 'No title'),
            'year': str(data.get('publication_date', ''))[:4],
            'journal': data.get('journal', 'N/A'),
            'abstract': str(data.get('abstract', ''))[:300]
        })
    return articles
