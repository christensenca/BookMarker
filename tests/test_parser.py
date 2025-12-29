import pytest
from parser import parse_book_author, parse_highlight_info, parse_quote, parse_clippings
import datetime

def test_parse_book_author_with_author():
    line = "Churchill (Roberts, Andrew)"
    book, author = parse_book_author(line)
    assert book == "Churchill"
    assert author == "Roberts, Andrew"

def test_parse_book_author_without_author():
    line = "Some Book Title"
    book, author = parse_book_author(line)
    assert book == "Some Book Title"
    assert author == ""

def test_parse_highlight_info():
    line = "- Your Highlight on page 285 | Location 6982-6984 | Added on Sunday, November 10, 2024 11:21:35 AM"
    highlight_type, page, location, date_added = parse_highlight_info(line)
    assert highlight_type == "Highlight"
    assert page == 285
    assert location == "6982-6984"
    assert date_added == datetime.datetime(2024, 11, 10, 11, 21, 35).isoformat()

def test_parse_highlight_info_no_page():
    line = "- Your Note | Location 1234-1235 | Added on Monday, January 1, 2024 12:00:00 PM"
    highlight_type, page, location, date_added = parse_highlight_info(line)
    assert highlight_type == "Note"
    assert page is None
    assert location == "1234-1235"
    assert date_added == datetime.datetime(2024, 1, 1, 12, 0, 0).isoformat()

def test_parse_quote():
    lines = ["This is a quote.", "It spans multiple lines."]
    quote = parse_quote(lines)
    assert quote == "This is a quote. It spans multiple lines."

def test_parse_clippings_single_entry():
    text = """Churchill (Roberts, Andrew)
- Your Highlight on page 285 | Location 6982-6984 | Added on Sunday, November 10, 2024 11:21:35 AM

Churchill asked him to sit down, apologized, offered him a drink and thereafter behaved better, prompting Wood to remark truthfully: 'He hates doormats.' It was the beginning of what was to prove one of the most important political relationships of Churchill's life.
=========="""
    parsed = parse_clippings(text)
    assert len(parsed) == 1
    book, highlight = parsed[0]
    assert book.title == "Churchill"
    assert book.author == "Roberts, Andrew"
    assert highlight.highlight_type == "Highlight"
    assert highlight.page == 285
    assert highlight.location == "6982-6984"
    assert highlight.date_added == datetime.datetime(2024, 11, 10, 11, 21, 35).isoformat()
    assert "Churchill asked him to sit down" in highlight.quote

def test_parse_clippings_multiple_entries():
    text = """Churchill (Roberts, Andrew)
- Your Highlight on page 285 | Location 6982-6984 | Added on Sunday, November 10, 2024 11:21:35 AM

First quote.
==========
Never Split the Difference (Voss, Chris)
- Your Highlight on page 12 | Location 199-203 | Added on Sunday, November 10, 2024 12:50:53 PM

Second quote.
=========="""
    parsed = parse_clippings(text)
    assert len(parsed) == 2
    book1, highlight1 = parsed[0]
    book2, highlight2 = parsed[1]
    assert book1.title == "Churchill"
    assert book2.title == "Never Split the Difference"