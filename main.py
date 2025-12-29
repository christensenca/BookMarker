import sys
from database import create_tables, get_last_import_date, set_last_import_date, insert_book, insert_highlight
from parser import parse_clippings
from app.models import Book, Highlight
from config import DB_PATH, CLIPPINGS_FILE
import sqlite3
import datetime


def main():
    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)

    last_import_date = get_last_import_date(conn)
    print(f"Last import date: {last_import_date}")

    with open(CLIPPINGS_FILE, 'r', encoding='utf-8-sig') as f:
        text = f.read()

    parsed_entries = parse_clippings(text)
    if last_import_date:
        parsed_entries = [e for e in parsed_entries if not e.date_added or e.date_added > last_import_date]
    print(f"Parsed {len(parsed_entries)} entries.")

    for entry in parsed_entries:
        # Insert or get book
        book_id = insert_book(conn, entry.book, entry.author)

        # Insert highlight
        insert_highlight(conn, book_id, entry.highlight_type, entry.page, entry.location, entry.date_added, entry.quote)

    conn.commit()

    # Update last import date
    now_iso = datetime.datetime.now().isoformat()
    set_last_import_date(conn, now_iso)
    print(f"Import completed at {now_iso}")

    conn.close()

if __name__ == '__main__':
    main()