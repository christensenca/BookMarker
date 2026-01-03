from flask import Flask
import sqlite3
from database import create_tables
from config import DB_PATH

app = Flask(__name__)

# Initialize database
conn = sqlite3.connect(DB_PATH)
create_tables(conn)
conn.close()