import sqlite3
import re
import sys
import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedEntry:
    book: str
    author: str
    highlight_type: str
    page: Optional[int] 
    location: str
    date_added: Optional[str]
    quote: str

def parse_book_author(line):
    """Parse book title and author from the first line."""
    book_author = line.replace('\ufeff', '').strip()
    match = re.match(r'^(.*)\s*\((.*?)\)\s*$', book_author)
    book = match.group(1).strip() if match else book_author
    author = match.group(2).strip() if match else ''
    return book, author

def parse_highlight_info(line):
    """Parse highlight type, page, location, and date from the second line."""
    highlight_line = line.lstrip('* ').lstrip('- ').strip()
    type_match = re.match(r'Your (\w+)', highlight_line)
    highlight_type = type_match.group(1) if type_match else 'Unknown'
    
    page_match = re.search(r'on page (\d+)', highlight_line)
    page = int(page_match.group(1)) if page_match else None
    
    loc_match = re.search(r'Location (\d+-\d+)', highlight_line)
    location = loc_match.group(1) if loc_match else None
    
    date_match = re.search(r'Added on (.+)$', highlight_line)
    date_added_str = date_match.group(1).strip() if date_match else None
    date_added = datetime.datetime.strptime(date_added_str, '%A, %B %d, %Y %I:%M:%S %p').isoformat() if date_added_str else None
    
    return highlight_type, page, location, date_added

def parse_quote(quote_lines):
    """Parse the quote from the remaining lines."""
    return ' '.join([ql.strip() for ql in quote_lines]).strip()

def parse_clippings(text):
    parsed = []
    entries = re.split(r'==========\n?', text)
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        lines = [line for line in entry.split('\n') if line.strip()]
        if len(lines) < 3:
            continue
        
        # Book and author
        book, author = parse_book_author(lines[0])
        
        # Highlight info
        highlight_type, page, location, date_added = parse_highlight_info(lines[1])
        
        # Quote
        quote = parse_quote(lines[2:])
        
        if book and location and quote:  # Required fields
            parsed.append(
                ParsedEntry(
                    book=book,
                    author=author,
                    highlight_type=highlight_type,
                    page=page,
                    location=location,
                    date_added=date_added,
                    quote=quote
                )
            )
    return parsed



if __name__ == '__main__':

    clippings_file = 'My Clippings.txt'
    with open(clippings_file, 'r', encoding='utf-8-sig') as f:
        text = f.read()

    highlights = parse_clippings(text)

    # output the parsed highlights to csv
    import csv
    with open('parsed_clippings.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['book', 'author', 'highlight_type', 'page', 'location', 'date_added', 'quote']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for h in highlights:
            writer.writerow({
                'book': h.book,
                'author': h.author,
                'highlight_type': h.highlight_type,
                'page': h.page,
                'location': h.location,
                'date_added': h.date_added,
                'quote': h.quote
            })
