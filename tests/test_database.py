import pytest
import sqlite3
from database import (
    create_tables, get_last_import_date, set_last_import_date,
    get_books_with_stats, get_highlights_for_book, get_book_by_id, search_highlights,
    insert_book, insert_highlight, get_all_tags, get_tag_by_id, insert_tag, update_tag, delete_tag,
    get_tags_for_highlight, add_tag_to_highlight, remove_tag_from_highlight, get_highlights_for_book_with_tags
)

@pytest.fixture
def conn():
    conn = sqlite3.connect(':memory:')
    create_tables(conn)
    yield conn
    conn.close()

def test_create_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    expected_tables = ['books', 'highlights', 'tags', 'highlight_tags', 'import_metadata']
    for table in expected_tables:
        assert table in tables

def test_get_set_last_import_date(conn):
    # Initially None
    assert get_last_import_date(conn) is None
    
    # Set a date
    date_str = "2024-11-10T11:21:35"
    set_last_import_date(conn, date_str)
    assert get_last_import_date(conn) == date_str
    
    # Update
    new_date = "2024-12-01T00:00:00"
    set_last_import_date(conn, new_date)
    assert get_last_import_date(conn) == new_date

def test_get_books_with_stats_empty(conn):
    books = get_books_with_stats(conn)
    assert books == []

def test_get_books_with_stats_with_data(conn):
    cursor = conn.cursor()
    # Insert a book
    cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", ("Test Book", "Test Author"))
    book_id = cursor.lastrowid
    
    # Insert highlights
    cursor.execute("""
        INSERT INTO highlights (book_id, highlight_type, page, location, date_added, quote)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (book_id, "Highlight", 10, "100-102", "2024-11-10T11:21:35", "Test quote"))
    
    cursor.execute("""
        INSERT INTO highlights (book_id, highlight_type, page, location, date_added, quote)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (book_id, "Note", None, "200-201", "2024-11-11T12:00:00", "Another quote"))
    
    conn.commit()
    
    books = get_books_with_stats(conn)
    assert len(books) == 1
    book = books[0]
    assert book.id == book_id  # id
    assert book.title == "Test Book"  # title
    assert book.author == "Test Author"  # author
    assert book.highlight_count == 2  # highlight_count
    assert book.last_highlight_date == "2024-11-11T12:00:00"  # last_highlight_date

def test_get_highlights_for_book(conn):
    cursor = conn.cursor()
    # Insert book
    cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", ("Book", "Author"))
    book_id = cursor.lastrowid
    
    # Insert highlights
    cursor.execute("""
        INSERT INTO highlights (book_id, highlight_type, page, location, date_added, quote)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (book_id, "Highlight", 5, "50-52", "2024-01-01T00:00:00", "First"))
    cursor.execute("""
        INSERT INTO highlights (book_id, highlight_type, page, location, date_added, quote)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (book_id, "Note", 10, "100-101", "2024-01-02T00:00:00", "Second"))
    conn.commit()
    
    highlights = get_highlights_for_book(conn, book_id)
    assert len(highlights) == 2
    # Should be ordered by date_added DESC
    assert highlights[0].quote == "Second"  # quote
    assert highlights[1].quote == "First"

def test_get_book_by_id(conn):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", ("Title", "Author"))
    book_id = cursor.lastrowid
    conn.commit()
    
    book = get_book_by_id(conn, book_id)
    assert book.id == book_id
    assert book.title == "Title"
    assert book.author == "Author"
    
    # Non-existent
    assert get_book_by_id(conn, 999) is None

def test_search_highlights(conn):
    cursor = conn.cursor()
    # Insert book
    cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", ("Search Book", "Search Author"))
    book_id = cursor.lastrowid
    
    # Insert highlight
    cursor.execute("""
        INSERT INTO highlights (book_id, highlight_type, page, location, date_added, quote)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (book_id, "Highlight", 1, "1-2", "2024-01-01T00:00:00", "This is a searchable quote"))
    conn.commit()
    
    # Search in quote
    results = search_highlights(conn, "searchable")
    assert len(results) == 1
    highlight, book = results[0]
    assert highlight.quote == "This is a searchable quote"  # quote
    assert book.title == "Search Book"  # title
    assert book.author == "Search Author"  # author
    
    # Search in title
    results = search_highlights(conn, "Book")
    assert len(results) == 1
    
    # No match
    results = search_highlights(conn, "nonexistent")
    assert results == []

def test_insert_book_new(conn):
    book_id = insert_book(conn, "New Book", "New Author")
    assert book_id is not None
    # Check it was inserted
    book = get_book_by_id(conn, book_id)
    assert book.id == book_id
    assert book.title == "New Book"
    assert book.author == "New Author"

def test_insert_book_existing(conn):
    # Insert first time
    book_id1 = insert_book(conn, "Existing Book", "Existing Author")
    # Insert again
    book_id2 = insert_book(conn, "Existing Book", "Existing Author")
    assert book_id1 == book_id2

def test_insert_highlight(conn):
    book_id = insert_book(conn, "Book for Highlight", "Author")
    highlight_id = insert_highlight(conn, book_id, "Highlight", 5, "10-12", "2024-01-01T00:00:00", "Quote text")
    assert highlight_id is not None
    
    # Check highlights
    highlights = get_highlights_for_book(conn, book_id)
    assert len(highlights) == 1
    assert highlights[0].highlight_type == "Highlight"  # type
    assert highlights[0].quote == "Quote text"  # quote

def test_insert_highlight_duplicate(conn):
    book_id = insert_book(conn, "Book Dup", "Author Dup")
    # Insert first
    insert_highlight(conn, book_id, "Highlight", 5, "10-12", "2024-01-01T00:00:00", "Quote")
    # Insert duplicate (same book_id and location)
    highlight_id2 = insert_highlight(conn, book_id, "Highlight", 5, "10-12", "2024-01-01T00:00:00", "Quote")
    # Should be ignored, so still one
    highlights = get_highlights_for_book(conn, book_id)
    assert len(highlights) == 1

def test_get_all_tags_empty(conn):
    tags = get_all_tags(conn)
    assert tags == []

def test_insert_tag(conn):
    tag_id = insert_tag(conn, "Test Tag")
    assert tag_id is not None
    
    tags = get_all_tags(conn)
    assert len(tags) == 1
    assert tags[0].name == "Test Tag"

def test_insert_tag_duplicate(conn):
    insert_tag(conn, "Duplicate Tag")
    tag_id2 = insert_tag(conn, "Duplicate Tag")
    assert tag_id2 is None  # Should fail due to unique constraint
    
    tags = get_all_tags(conn)
    assert len(tags) == 1

def test_get_tag_by_id(conn):
    tag_id = insert_tag(conn, "Find Me")
    tag = get_tag_by_id(conn, tag_id)
    assert tag is not None
    assert tag.name == "Find Me"
    
    # Non-existent
    tag_none = get_tag_by_id(conn, 999)
    assert tag_none is None

def test_update_tag(conn):
    tag_id = insert_tag(conn, "Old Name")
    success = update_tag(conn, tag_id, "New Name")
    assert success
    
    tag = get_tag_by_id(conn, tag_id)
    assert tag.name == "New Name"

def test_update_tag_duplicate_name(conn):
    insert_tag(conn, "Existing")
    tag_id2 = insert_tag(conn, "Another")
    success = update_tag(conn, tag_id2, "Existing")  # Try to rename to existing
    assert not success
    
    tag = get_tag_by_id(conn, tag_id2)
    assert tag.name == "Another"  # Should remain unchanged

def test_delete_tag(conn):
    tag_id = insert_tag(conn, "To Delete")
    tags_before = get_all_tags(conn)
    assert len(tags_before) == 1
    
    success = delete_tag(conn, tag_id)
    assert success
    
    tags_after = get_all_tags(conn)
    assert len(tags_after) == 0
    
    # Delete non-existent
    success2 = delete_tag(conn, 999)
    assert not success2

def test_add_tag_to_highlight(conn):
    # Create highlight
    book_id = insert_book(conn, "Book", "Author")
    highlight_id = insert_highlight(conn, book_id, "Highlight", 1, "1-2", "2024-01-01", "Quote")
    tag_id = insert_tag(conn, "Test Tag")
    
    success = add_tag_to_highlight(conn, highlight_id, tag_id)
    assert success
    
    tags = get_tags_for_highlight(conn, highlight_id)
    assert len(tags) == 1
    assert tags[0].name == "Test Tag"

def test_add_tag_to_highlight_duplicate(conn):
    book_id = insert_book(conn, "Book2", "Author2")
    highlight_id = insert_highlight(conn, book_id, "Highlight", 1, "1-2", "2024-01-01", "Quote")
    tag_id = insert_tag(conn, "Dup Tag")
    
    add_tag_to_highlight(conn, highlight_id, tag_id)
    success2 = add_tag_to_highlight(conn, highlight_id, tag_id)  # Duplicate
    assert not success2  # Should fail
    
    tags = get_tags_for_highlight(conn, highlight_id)
    assert len(tags) == 1

def test_remove_tag_from_highlight(conn):
    book_id = insert_book(conn, "Book3", "Author3")
    highlight_id = insert_highlight(conn, book_id, "Highlight", 1, "1-2", "2024-01-01", "Quote")
    tag_id = insert_tag(conn, "Remove Tag")
    
    add_tag_to_highlight(conn, highlight_id, tag_id)
    tags_before = get_tags_for_highlight(conn, highlight_id)
    assert len(tags_before) == 1
    
    success = remove_tag_from_highlight(conn, highlight_id, tag_id)
    assert success
    
    tags_after = get_tags_for_highlight(conn, highlight_id)
    assert len(tags_after) == 0

def test_get_highlights_for_book_with_tags(conn):
    book_id = insert_book(conn, "Book4", "Author4")
    highlight_id1 = insert_highlight(conn, book_id, "Highlight", 1, "1-2", "2024-01-01", "Quote1")
    highlight_id2 = insert_highlight(conn, book_id, "Note", 2, "3-4", "2024-01-02", "Quote2")
    
    tag_id1 = insert_tag(conn, "Tag1")
    tag_id2 = insert_tag(conn, "Tag2")
    
    add_tag_to_highlight(conn, highlight_id1, tag_id1)
    add_tag_to_highlight(conn, highlight_id1, tag_id2)
    add_tag_to_highlight(conn, highlight_id2, tag_id1)
    
    highlights = get_highlights_for_book_with_tags(conn, book_id)
    assert len(highlights) == 2
    
    # Check tags
    h1 = next(h for h in highlights if h.id == highlight_id1)
    assert len(h1.tags) == 2
    tag_names = [t.name for t in h1.tags]
    assert "Tag1" in tag_names
    assert "Tag2" in tag_names
    
    h2 = next(h for h in highlights if h.id == highlight_id2)
    assert len(h2.tags) == 1
    assert h2.tags[0].name == "Tag1"