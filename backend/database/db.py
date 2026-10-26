"""
Database connection and utility functions for SQLite
"""
import sqlite3
import os
from contextlib import contextmanager
from backend.database.schema import SCHEMA_SQL

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "interview_tracker.db"))

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@contextmanager
def get_db():
    """Context manager for SQLite database connection with row dictionary factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize database tables according to schema."""
    with get_db() as conn:
        conn.executescript(SCHEMA_SQL)
    print(f"Database initialized successfully at {DB_PATH}")

if __name__ == "__main__":
    init_db()
