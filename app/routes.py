from flask import render_template, request, jsonify
from app import app
import sqlite3
import re
from database import get_books_with_stats, get_highlights_for_book, get_book_by_id, search_highlights, get_all_tags, get_tag_by_id, insert_tag, update_tag, delete_tag, get_highlights_for_book_with_tags, add_tag_to_highlight, remove_tag_from_highlight, get_tags_for_highlight
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
            # Add tags
            highlight.tags = get_tags_for_highlight(conn, highlight.id)
            highlights.append((highlight, book, highlighted_quote, highlighted_title, highlighted_author))
        selected_book = None
    elif selected_book_id:
        highlights = get_highlights_for_book_with_tags(conn, selected_book_id)
        selected_book = get_book_by_id(conn, selected_book_id)
    else:
        highlights = []
        selected_book = None
    
    all_tags = get_all_tags(conn)
    conn.close()
    return render_template('index.html', books=books, highlights=highlights, selected_book=selected_book, query=query, all_tags=all_tags)

@app.route('/add_tag_to_highlight', methods=['POST'])
def add_tag_to_highlight_route():
    highlight_id = request.form.get('highlight_id', type=int)
    tag_id = request.form.get('tag_id', type=int)
    if highlight_id and tag_id:
        conn = sqlite3.connect(DB_PATH)
        add_tag_to_highlight(conn, highlight_id, tag_id)
        conn.close()
    return '', 204

@app.route('/remove_tag_from_highlight', methods=['POST'])
def remove_tag_from_highlight_route():
    highlight_id = request.form.get('highlight_id', type=int)
    tag_id = request.form.get('tag_id', type=int)
    if highlight_id and tag_id:
        conn = sqlite3.connect(DB_PATH)
        remove_tag_from_highlight(conn, highlight_id, tag_id)
        conn.close()
    return '', 204

@app.route('/get_tags_for_highlight')
def get_tags_for_highlight_route():
    highlight_id = request.args.get('highlight_id', type=int)
    if highlight_id:
        conn = sqlite3.connect(DB_PATH)
        tags = get_tags_for_highlight(conn, highlight_id)
        conn.close()
        return jsonify([{'id': t.id, 'name': t.name} for t in tags])
    return jsonify([])

@app.route('/update_highlight_tags', methods=['POST'])
def update_highlight_tags():
    data = request.get_json()
    highlight_id = data.get('highlight_id')
    tag_ids = data.get('tag_ids', [])
    if highlight_id:
        conn = sqlite3.connect(DB_PATH)
        # Remove all current tags
        cursor = conn.cursor()
        cursor.execute("DELETE FROM highlight_tags WHERE highlight_id = ?", (highlight_id,))
        # Add new tags
        for tag_id in tag_ids:
            add_tag_to_highlight(conn, highlight_id, tag_id)
        conn.close()
    return '', 204

@app.route('/tags', methods=['GET', 'POST'])
def tags():
    conn = sqlite3.connect(DB_PATH)
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name', '').strip()
            if name:
                insert_tag(conn, name)
        elif action == 'update':
            tag_id = request.form.get('tag_id', type=int)
            name = request.form.get('name', '').strip()
            if tag_id and name:
                update_tag(conn, tag_id, name)
        elif action == 'delete':
            tag_id = request.form.get('tag_id', type=int)
            if tag_id:
                delete_tag(conn, tag_id)
    
    tags_list = get_all_tags(conn)
    conn.close()
    return render_template('tags.html', tags=tags_list)