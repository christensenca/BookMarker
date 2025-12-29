from flask import render_template, request
from app import app
import sqlite3
import re
from database import get_books_with_stats, get_highlights_for_book, get_book_by_id, search_highlights
from config import DB_PATH

def highlight_text(text, query):
    if not query:
        return text
    # Case-insensitive replace with <mark>
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f'<mark>{m.group()}</mark>', text)

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    books = get_books_with_stats(conn)
    query = request.args.get('q', '').strip()
    selected_book_id = request.args.get('book_id', type=int)
    
    if query:
        # Search mode
        search_results = search_highlights(conn, query)
        highlights = []
        for highlight, book in search_results:
            highlighted_quote = highlight_text(highlight.quote, query)
            highlighted_title = highlight_text(book.title, query)
            highlighted_author = highlight_text(book.author, query)
            highlights.append((highlight, book, highlighted_quote, highlighted_title, highlighted_author))
        selected_book = None
    elif selected_book_id:
        highlights = get_highlights_for_book(conn, selected_book_id)
        selected_book = get_book_by_id(conn, selected_book_id)
    else:
        highlights = []
        selected_book = None
    
    conn.close()
    return render_template('index.html', books=books, highlights=highlights, selected_book=selected_book, query=query)