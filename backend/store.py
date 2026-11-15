"""SQLite schema, idempotent upgrades and starter content."""
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from .store_constants import GRADES, SUBJECTS

DB_PATH = Path(os.getenv('ACADEMY_DB', str(Path(__file__).resolve().parent.parent / 'academy.sqlite3')))

@contextmanager
def connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    try:
        yield con
        con.commit()
    finally:
        con.close()


def initialize():
    from .content import starter_lessons
    with connection() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS parents (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL, email TEXT NOT NULL UNIQUE COLLATE NOCASE,
          password_hash TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS students (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL, grade TEXT NOT NULL, avatar TEXT NOT NULL DEFAULT '🌟',
          language TEXT NOT NULL DEFAULT 'English',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS lessons (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          grade TEXT NOT NULL, subject TEXT NOT NULL, title TEXT NOT NULL,
          explanation TEXT NOT NULL, emoji TEXT NOT NULL DEFAULT '📚',
          questions TEXT NOT NULL DEFAULT '[]',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS attempts (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
          lesson_id INTEGER NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
          correct INTEGER NOT NULL, total INTEGER NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        cols = {row['name'] for row in con.execute('PRAGMA table_info(students)')}
        for name, sql in (
            ('parent_id','ALTER TABLE students ADD COLUMN parent_id INTEGER REFERENCES parents(id)'),
            ('username','ALTER TABLE students ADD COLUMN username TEXT'),
            ('pin_hash','ALTER TABLE students ADD COLUMN pin_hash TEXT'),
        ):
            if name not in cols:
                con.execute(sql)
        con.execute('CREATE UNIQUE INDEX IF NOT EXISTS ux_student_username ON students(username COLLATE NOCASE)')
        existing={(r['grade'],r['subject'],r['title']) for r in con.execute('SELECT grade,subject,title FROM lessons')}
        for grade, subject, title, description, emoji, questions in starter_lessons():
            if (grade,subject,title) not in existing:
                con.execute('''INSERT INTO lessons(grade,subject,title,explanation,emoji,questions)
                    VALUES(?,?,?,?,?,?)''',(grade,subject,title,description,emoji,
                                            json.dumps(questions,ensure_ascii=False)))


def lesson_from_row(row):
    item=dict(row)
    item['questions']=json.loads(item['questions'])
    return item


def student_from_row(row):
    return {k:row[k] for k in ('id','name','grade','avatar','language','username')}
