import threading
import time
import webbrowser

from waitress import serve

from src.app import app
from src.database import init_db


def start_server():
    init_db()

    serve(
        app,
        host="127.0.0.1",
        port=5001
    )


thread = threading.Thread(
    target=start_server,
    daemon=True
)

thread.start()

time.sleep(2)

webbrowser.open("http://127.0.0.1:5001")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass