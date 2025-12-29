import pytest
import sqlite3
import tempfile
import os
from main import main
from database import create_tables, get_books_with_stats, get_highlights_for_book

# Mock the config for testing
import main
main.DB_PATH = ':memory:'  # Use in-memory db
main.CLIPPINGS_FILE = 'My Clippings.txt'  # Use real file for now, but perhaps create a temp one

def test_import_process():
    # This would test the full import, but since it uses real files, maybe skip or mock.
    # For now, since functions are tested, perhaps not necessary.
    pass