import sqlite3

def create_tables(conn):
    cursor = conn.cursor()
    # Books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            UNIQUE(title, author)
        )
    ''')
    # Highlights table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS highlights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            highlight_type TEXT,
            page INTEGER,
            location TEXT NOT NULL,
            date_added TEXT,
            quote TEXT NOT NULL,
            FOREIGN KEY(book_id) REFERENCES books(id),
            UNIQUE(book_id, location)
        )
    ''')
    # Tags (for future)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS highlight_tags (
            highlight_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY(highlight_id, tag_id),
            FOREIGN KEY(highlight_id) REFERENCES highlights(id),
            FOREIGN KEY(tag_id) REFERENCES tags(id)
        )
    ''')

    # Anchor table (for future)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS import_metadata (
                   key TEXT PRIMARY KEY,
                   value TEXT
                   )
    ''')
    conn.commit()

def get_last_import_date(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM import_metadata WHERE key = 'last_import_date'")
    row = cursor.fetchone()
    return row[0] if row else None

def set_last_import_date(conn, date_str):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO import_metadata (key, value) 
        VALUES ('last_import_date', ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
    """, (date_str,))
    conn.commit()


def get_books_with_stats(conn):
    from app.models import Book
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.id, b.title, b.author, COUNT(h.id) as highlight_count, MAX(h.date_added) as last_highlight_date
        FROM books b
        LEFT JOIN highlights h ON b.id = h.book_id
        GROUP BY b.id, b.title, b.author
        ORDER BY last_highlight_date DESC
    """)
    results = cursor.fetchall()
    
    books = []
    for row in results:
        book = Book(
            id=row[0],
            title=row[1],
            author=row[2],
            highlight_count=row[3],
            last_highlight_date=row[4]
        )
        books.append(book)
    
    return books

def get_highlights_for_book(conn, book_id):
    from app.models import Highlight
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.id, h.highlight_type, h.page, h.location, h.date_added, h.quote
        FROM highlights h
        WHERE h.book_id = ?
        ORDER BY h.date_added DESC
    """, (book_id,))
    results = cursor.fetchall()
    
    highlights = []
    for row in results:
        highlight = Highlight(
            id=row[0],
            book_id=book_id,
            highlight_type=row[1],
            page=row[2],
            location=row[3],
            date_added=row[4],
            quote=row[5]
        )
        highlights.append(highlight)
    
    return highlights

def get_book_by_id(conn, book_id):
    from app.models import Book
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author FROM books WHERE id = ?", (book_id,))
    row = cursor.fetchone()
    if row:
        return Book(id=row[0], title=row[1], author=row[2])
    return None

def search_highlights(conn, query):
    from app.models import Highlight, Book
    cursor = conn.cursor()
    like_query = f'%{query}%'
    cursor.execute("""
        SELECT h.id, h.highlight_type, h.page, h.location, h.date_added, h.quote, b.id, b.title, b.author
        FROM highlights h
        JOIN books b ON h.book_id = b.id
        WHERE h.quote LIKE ? OR b.title LIKE ? OR b.author LIKE ?
        ORDER BY h.date_added DESC
    """, (like_query, like_query, like_query))
    results = cursor.fetchall()
    
    search_results = []
    for row in results:
        highlight = Highlight(
            id=row[0],
            book_id=row[6],  # b.id
            highlight_type=row[1],
            page=row[2],
            location=row[3],
            date_added=row[4],
            quote=row[5]
        )
        book = Book(id=row[6], title=row[7], author=row[8])
        search_results.append((highlight, book))
    
    return search_results

def insert_book(conn, title, author):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM books WHERE title=? AND author=?", (title, author))
    book_row = cursor.fetchone()
    if book_row:
        return book_row[0]
    else:
        cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
        return cursor.lastrowid

def insert_highlight(conn, book_id, highlight_type, page, location, date_added, quote):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO highlights 
        (book_id, highlight_type, page, location, date_added, quote) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (book_id, highlight_type, page, location, date_added, quote))
    return cursor.lastrowid


if __name__ == '__main__':
    conn = sqlite3.connect('bookmarker.db')
    create_tables(conn)
    conn.close()
    