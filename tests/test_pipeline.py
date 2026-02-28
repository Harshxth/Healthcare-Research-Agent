import pytest
from unittest.mock import patch, MagicMock


def test_pubmed_tool_returns_string():
    from src.tools.pubmed_tools import search_pubmed
    # Mock PubMed to avoid real API calls in tests
    with patch("src.tools.pubmed_tools.pubmed") as mock_pubmed:
        mock_article = MagicMock()
        mock_article.toDict.return_value = {
            "pubmed_id": "12345",
            "title": "Test Study on Readmissions",
            "abstract": "This is a test abstract.",
            "publication_date": "2023",
            "journal": "NEJM",
            "authors": [],
        }
        mock_pubmed.query.return_value = [mock_article]
        result = search_pubmed.run("hospital readmissions")
        assert "12345" in result
        assert "Test Study" in result


def test_report_builder_creates_file(tmp_path):
    from src.reporting.report_builder import build_report
    path = build_report(
        query="test query",
        crew_output="## Key Findings\n- Finding 1\n- Finding 2",
        output_dir=str(tmp_path),
    )
    assert path.endswith(".md")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
