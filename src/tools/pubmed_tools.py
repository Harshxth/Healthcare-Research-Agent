import os
from pymed import PubMed
from crewai.tools import tool

pubmed = PubMed(
    tool=os.getenv("PUBMED_TOOL", "HealthcareResearchAgent"),
    email=os.getenv("PUBMED_EMAIL", "researcher@example.com")
)

@tool("Search PubMed")
def search_pubmed(query: str) -> str:
    try:
        max_results = int(os.getenv("MAX_PUBMED_RESULTS", 15))
        results = pubmed.query(query, max_results=max_results)
        articles = []
        for article in results:
            article_dict = article.toDict()
            articles.append({
                "pmid": article_dict.get("pubmed_id", "N/A"),
                "title": article_dict.get("title", "No title"),
                "abstract": str(article_dict.get("abstract", "No abstract"))[:500],
                "year": str(article_dict.get("publication_date", "N/A"))[:4],
                "journal": article_dict.get("journal", "N/A"),
                "authors": [str(a) for a in article_dict.get("authors", [])][:3],
            })
        if not articles:
            return "No articles found for this query."
        output = f"Found {len(articles)} articles:\n\n"
        for i, a in enumerate(articles, 1):
            output += f"{i}. [{a['pmid']}] {a['title']} ({a['year']}, {a['journal']})\n"
            output += f"   Abstract: {a['abstract'][:200]}...\n\n"
        return output
    except Exception as e:
        return f"PubMed search error: {str(e)}"


@tool("Fetch PubMed Article Details")
def fetch_article_details(pmids: str) -> str:
    try:
        pmid_list = [p.strip() for p in pmids.split(",")]
        details = []
        for pmid in pmid_list[:10]:
            results = list(pubmed.query(f"{pmid}[uid]", max_results=1))
            if results:
                a = results[0].toDict()
                details.append(
                    f"PMID: {pmid}\n"
                    f"Title: {a.get('title', 'N/A')}\n"
                    f"Journal: {a.get('journal', 'N/A')}\n"
                    f"Year: {str(a.get('publication_date', 'N/A'))[:4]}\n"
                    f"Abstract: {str(a.get('abstract', 'N/A'))[:600]}\n"
                    f"Keywords: {', '.join(str(k) for k in a.get('keywords', []))}\n"
                )
        return "\n---\n".join(details) if details else "No details found."
    except Exception as e:
        return f"Fetch error: {str(e)}"
