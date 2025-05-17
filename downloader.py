
from datetime import datetime, timedelta
from typing import List
import arxiv
from models import ArxivPaper


class ArxivDownloader:
    def __init__(self):
        pass
     

    def fetch_papers(self, date: datetime, categories: List[str]) -> List[ArxivPaper]:
        """
        Fetch papers from arXiv for a specific date and categories.
        
        Args:
            date: The date to fetch papers for
            categories: List of arXiv categories to fetch
            
        Returns:
            List of ArxivPaper objects
        """
        papers = []
        next_date = date + timedelta(days=2)
        
        for category in categories:
            query = f"cat:{category} AND submittedDate:[{date.strftime('%Y%m%d')} TO {next_date.strftime('%Y%m%d')}]"
            
            search = arxiv.Search(
                query=query,
                max_results=10000,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Ascending
            )
            
            for result in search.results():
                paper = ArxivPaper(
                    arxiv_id=result.entry_id.split('/')[-1],
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    categories=result.categories,
                    published=result.published,
                    updated=result.updated,
                    pdf_url=result.pdf_url,
                    comment=result.comment,
                    doi=result.doi,
                    journal_ref=result.journal_ref
                )
                papers.append(paper)        
        return papers


def main():
    """Main function to download and store papers."""
    # Example usage
    date = datetime(2023, 1, 1)
    categories = ["cs.AI", "cs.CL"]
    
    downloader = ArxivDownloader()
    try:
        papers = downloader.fetch_papers(date, categories)
    except Exception as e:
        papers = []
    finally:
        return papers


if __name__ == "__main__":
    main()