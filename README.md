# BookMarker

A web application for managing and searching Kindle highlights (clippings). Import your "My Clippings.txt" file and explore your reading highlights through a clean web interface.

## Features

### 📚 Book Management
- View all books with highlight counts and last highlight dates
- Browse highlights by book
- Automatic book deduplication on import

### 🔍 Search Functionality
- Search across highlight quotes, book titles, and authors
- Case-insensitive search with highlighting
- Real-time results

### 📥 Incremental Import
- Import highlights from Kindle's "My Clippings.txt"
- Only imports new highlights since last import
- Tracks import timestamps

### 🖥️ Web Interface
- Responsive design with sidebar navigation
- Clean, readable highlight display
- External CSS for easy customization

### 🧪 Testing
- Comprehensive test suite covering parser, database, and models
- 23+ tests with pytest
- In-memory databases for fast testing

## Project Structure

```
BookMarker/
├── app/                          # Flask web application
│   ├── __init__.py               # App initialization
│   ├── models.py                 # Data models (Book, Highlight, etc.)
│   ├── routes.py                 # Web routes and views
│   ├── static/css/style.css     # Stylesheets
│   └── templates/index.html      # HTML templates
├── config.py                     # Configuration settings
├── database.py                   # Database operations
├── main.py                       # CLI import script
├── parser.py                     # Kindle clippings parser
├── run.py                        # Web app entry point
├── requirements.txt              # Python dependencies
├── tests/                        # Test suite
│   ├── test_database.py
│   ├── test_models.py
│   ├── test_parser.py
│   └── test_main.py
└── README.md
```

## Installation

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd BookMarker
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure paths** (optional)
   - Edit `config.py` to change database path or clippings file location
   - Default: `bookmarker.db` and `My Clippings.txt`

## Usage

### Importing Highlights (CLI)

1. Place your "My Clippings.txt" file in the project root
2. Run the import script:
   ```bash
   python main.py
   ```
   - Parses and imports highlights
   - Skips already imported entries
   - Updates last import timestamp

### Running the Web App

1. Start the Flask development server:
   ```bash
   python run.py
   ```

2. Open your browser to `http://localhost:5001`

3. **Navigation:**
   - **Sidebar**: Click books to view their highlights
   - **Search**: Use the search box to find highlights across all content
   - **Clear**: Reset search to return to book list

### Running Tests

```bash
python -m pytest tests/
```

## Data Model

- **Books**: Title, author (unique constraint)
- **Highlights**: Quote text, location, page, date, type (Highlight/Note)
- **Import Metadata**: Tracks last import date for incremental updates

## Technical Details

- **Backend**: Python 3.12+, Flask, SQLite
- **Frontend**: HTML5, CSS3, Jinja2 templates
- **Database**: SQLite with foreign keys and constraints
- **Parsing**: Regex-based Kindle clippings parser
- **Testing**: pytest with in-memory databases

## Development

### Adding New Features
- **Web routes**: Add to `app/routes.py`
- **Database functions**: Add to `database.py`
- **Models**: Update `app/models.py`
- **Styles**: Modify `app/static/css/style.css`
- **Templates**: Edit `app/templates/index.html`

### Testing
- Add tests in `tests/` directory
- Use in-memory SQLite for database tests
- Run `pytest` to execute all tests

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Support

For issues or questions:
- Check the test suite: `python -m pytest tests/`
- Verify your "My Clippings.txt" format
- Ensure Python dependencies are installed

---

**Note**: This app is designed for personal use with Kindle highlights. Make sure your clippings file is from a Kindle device or app.</content>
<parameter name="filePath">/Users/cadechristensen/Source/BookMarker/README.md
