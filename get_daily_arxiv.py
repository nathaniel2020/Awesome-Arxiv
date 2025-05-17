'''

'''

from downloader import ArxivDownloader
from datetime import datetime, timedelta, date
import time


def get_daily_arxiv():
    """Main function to download and store papers."""
    today = date.today()
    yesterday = today - timedelta(days=2) # get yesterday papers
    categories = ["cs.AI", "cs.CL"]
    
    downloader = ArxivDownloader()
    try:
        papers = downloader.fetch_papers(yesterday, categories)
    except Exception as e:
        print('Error')
        papers = []
    finally:
        return papers

if __name__ == "__main__":
    papers = get_daily_arxiv()
    for paper in papers:
        # Convert Pydantic model to dict and remove _id if present
        paper_dict = paper.model_dump()
        print(paper_dict)
        break
