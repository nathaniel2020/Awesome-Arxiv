from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ArxivPaper(BaseModel):
    """Model representing an arXiv paper."""
    arxiv_id: str = Field(..., description="arXiv paper ID")
    title: str = Field(..., description="Paper title")
    authors: List[str] = Field(..., description="List of authors")
    abstract: str = Field(..., description="Paper abstract")
    categories: List[str] = Field(..., description="arXiv categories")
    published: datetime = Field(..., description="Publication date")
    updated: datetime = Field(..., description="Last update date")
    pdf_url: str = Field(..., description="URL to the PDF version")
    comment: Optional[str] = Field(None, description="Author comments")
    doi: Optional[str] = Field(None, description="DOI if available")
    journal_ref: Optional[str] = Field(None, description="Journal reference if available") 