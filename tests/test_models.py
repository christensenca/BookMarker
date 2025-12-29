import pytest
from app.models import Book, Highlight, Tag, HighlightTag

def test_book_creation():
    book = Book(title="Test Title", author="Test Author", id=1)
    assert book.title == "Test Title"
    assert book.author == "Test Author"
    assert book.id == 1

def test_highlight_creation():
    highlight = Highlight(
        book_id=1,
        highlight_type="Highlight",
        page=10,
        location="100-102",
        date_added="2024-01-01T00:00:00",
        quote="Test quote",
        id=2
    )
    assert highlight.book_id == 1
    assert highlight.quote == "Test quote"

def test_tag_creation():
    tag = Tag(name="Test Tag", id=3)
    assert tag.name == "Test Tag"

def test_highlight_tag_creation():
    ht = HighlightTag(highlight_id=2, tag_id=3, id=4)
    assert ht.highlight_id == 2
    assert ht.tag_id == 3