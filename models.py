from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:
    title: str
    author: str
    id: Optional[int] = None

@dataclass
class Highlight:
    book_id: int
    highlight_type: str
    page: Optional[int]
    location: str
    date_added: Optional[str]
    quote: str
    id: Optional[int] = None

@dataclass
class Tag:
    name: str
    id: Optional[int] = None
    
@dataclass
class HighlightTag:
    highlight_id: int
    tag_id: int
    id: Optional[int] = None