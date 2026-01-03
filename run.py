from app import app
from app import routes
import threading
import webbrowser
import time

def open_browser():
    time.sleep(2)  # Wait for server to start
    webbrowser.open('http://localhost:5001')

if __name__ == '__main__':
    # Start browser in a separate thread
    threading.Thread(target=open_browser).start()
    app.run(host='127.0.0.1', port=5001, debug=False)