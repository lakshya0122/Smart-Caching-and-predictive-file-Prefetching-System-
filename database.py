"""
database.py - DBMS part of the project.

Stores file metadata and the access log (the history of which files were opened)
in a SQLite database. The predictor reads this history to learn user habits.
"""
import sqlite3
from pathlib import Path
from datetime import datetime

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "predictive_fs.db"


def now_text():
    return datetime.now().isoformat(timespec="seconds")


class Store:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS files (
                path TEXT PRIMARY KEY,
                size_bytes INTEGER NOT NULL,
                allocation_method TEXT NOT NULL,
                blocks TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT NOT NULL,
                accessed_at TEXT NOT NULL,
                sequence_no INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def save_file(self, path, size, method, blocks, created):
        self.conn.execute("""
            INSERT INTO files(path, size_bytes, allocation_method, blocks, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET size_bytes=excluded.size_bytes,
              allocation_method=excluded.allocation_method, blocks=excluded.blocks
        """, (path, size, method, ",".join(map(str, blocks)), created))
        self.conn.commit()

    def log_access(self, path):
        seq = self.conn.execute(
            "SELECT COALESCE(MAX(sequence_no), 0) + 1 FROM access_logs"
        ).fetchone()[0]
        self.conn.execute(
            "INSERT INTO access_logs(path, accessed_at, sequence_no) VALUES (?, ?, ?)",
            (path, now_text(), seq)
        )
        self.conn.commit()

    def sequence(self):
        return [r[0] for r in self.conn.execute(
            "SELECT path FROM access_logs ORDER BY sequence_no"
        ).fetchall()]

    def logs(self, limit=100):
        return self.conn.execute(
            "SELECT sequence_no, path, accessed_at FROM access_logs "
            "ORDER BY sequence_no DESC LIMIT ?", (limit,)
        ).fetchall()

    def metadata(self):
        return self.conn.execute(
            "SELECT path, size_bytes, allocation_method, blocks, created_at "
            "FROM files ORDER BY path"
        ).fetchall()

    def close(self):
        self.conn.close()
