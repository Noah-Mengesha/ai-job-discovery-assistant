import sqlite3
from pathlib import Path
DB = Path(__file__).with_name("job_finder.db")
def connect():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c
def init():
    with connect() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS facts(id INTEGER PRIMARY KEY, category TEXT, label TEXT, value TEXT, status TEXT DEFAULT 'verified');
        CREATE TABLE IF NOT EXISTS jobs(id INTEGER PRIMARY KEY, company TEXT, title TEXT, location TEXT, url TEXT, description TEXT, analysis TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS packages(id INTEGER PRIMARY KEY, job_id INTEGER, content TEXT, status TEXT DEFAULT 'pending', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS applications(id INTEGER PRIMARY KEY, job_id INTEGER, package_id INTEGER, status TEXT DEFAULT 'approved_for_handoff', notes TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        """)
