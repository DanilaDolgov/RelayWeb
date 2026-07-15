from waitress import serve

from src.app import app
from src.database import init_db

if __name__ == "__main__":
    init_db()

    serve(
        app,
        host="127.0.0.1",
        port=5001
    )