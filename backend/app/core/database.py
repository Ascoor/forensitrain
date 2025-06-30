"""Simple SQLite connection helper."""
import sqlite3
from .config import settings


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection using configured database URL."""
    return sqlite3.connect(settings.database_url)
