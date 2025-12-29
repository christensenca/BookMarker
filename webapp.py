from flask import Flask, render_template, request
import sqlite3
import re
from database import get_books_with_stats, get_highlights_for_book, get_book_by_id, search_highlights
from config import DB_PATH

app = Flask(__name__)

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
        highlights_raw = search_highlights(conn, query)
        highlights = []
        for h in highlights_raw:
            highlighted_quote = highlight_text(h[5], query)
            highlighted_title = highlight_text(h[6], query)
            highlighted_author = highlight_text(h[7], query)
            highlights.append((h[0], h[1], h[2], h[3], h[4], highlighted_quote, highlighted_title, highlighted_author))
        selected_book = None
    elif selected_book_id:
        highlights = get_highlights_for_book(conn, selected_book_id)
        selected_book = get_book_by_id(conn, selected_book_id)
    else:
        highlights = []
        selected_book = None
    
    conn.close()
    return render_template('index.html', books=books, highlights=highlights, selected_book=selected_book, query=query)

if __name__ == '__main__':
    app.run(debug=True)