"""SQLite persistence. All database access is parameterized; one connection per operation."""
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(os.getenv('ACADEMY_DB', str(Path(__file__).resolve().parent.parent / 'academy.sqlite3')))
GRADES = ['Preschool', 'Kindergarten'] + [f'Grade {x}' for x in range(1, 6)]
SUBJECTS = ['English', 'Mathematics', 'Urdu', 'Science', 'General Knowledge', 'Islamiyat', 'Computer']

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
    with connection() as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, grade TEXT NOT NULL, avatar TEXT NOT NULL DEFAULT '🌟',
            language TEXT NOT NULL DEFAULT 'English', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grade TEXT NOT NULL, subject TEXT NOT NULL,
            title TEXT NOT NULL, explanation TEXT NOT NULL,
            emoji TEXT NOT NULL DEFAULT '📚',
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
        if con.execute('SELECT COUNT(*) FROM lessons').fetchone()[0] == 0:
            for grade, subject, title, explanation, emoji, qs in SEED_LESSONS:
                con.execute('INSERT INTO lessons (grade,subject,title,explanation,emoji,questions) VALUES (?,?,?,?,?,?)',
                    (grade,subject,title,explanation,emoji,json.dumps(qs, ensure_ascii=False)))

def lesson_from_row(row):
    result = dict(row)
    result['questions'] = json.loads(result['questions'])
    return result

def q(prompt, choices, answer):
    return {'prompt': prompt, 'choices': choices, 'answer': answer}

SEED_LESSONS = [
 ('Preschool','English','A is for Apple','A is for Apple 🍎. Say the letter A and find the apple!', '🍎', [q('Which word starts with A?',['Apple','Ball','Cat'],0),q('Find the letter A',['C','A','B'],1)]),
 ('Preschool','Mathematics','Count the Stars','Count each star slowly: ⭐ ⭐ ⭐', '⭐', [q('How many stars? ⭐ ⭐ ⭐',['2','3','4'],1)]),
 ('Kindergarten','English','The Alphabet','We use letters to make words. A, B, and C are the first three letters.', '🔤', [q('Which comes after B?',['A','C','D'],1)]),
 ('Kindergarten','Mathematics','Shapes Around Us','A circle is round. A square has four equal sides.', '🔵', [q('Which shape is round?',['Circle','Triangle','Square'],0)]),
 ('Grade 1','Mathematics','Adding Apples','Adding means putting groups together. 🍎🍎 + 🍎 = 3 apples.', '🍏', [q('2 + 1 = ?',['2','3','4'],1),q('1 + 3 = ?',['3','4','5'],1)]),
 ('Grade 1','English','Nouns','A noun names a person, place, animal, or thing.', '📖', [q('Which is a noun?',['Run','Cat','Quickly'],1)]),
 ('Grade 2','Urdu','اردو حروف','اردو کے حروف سیکھیں: ا، ب، پ، ت۔', '🌙', [q('اردو کا پہلا حرف کون سا ہے؟',['ب','ا','پ'],1)]),
 ('Grade 2','Science','Living and Nonliving','Plants and animals are living things. Rocks and chairs are not living.', '🌱', [q('Which one grows?',['Stone','Plant','Cup'],1)]),
 ('Grade 3','General Knowledge','Our Planet Earth','Earth is the planet where we live. It has land and oceans.', '🌍', [q('Which planet is our home?',['Mars','Earth','Venus'],1)]),
 ('Grade 3','Computer','Computer Basics','A keyboard helps us type. A monitor displays pictures and words.', '💻', [q('Which device is used to type?',['Keyboard','Speaker','Monitor'],0)]),
 ('Grade 4','Islamiyat','Good Manners','Kindness, honesty and respect are important good manners.', '🤲', [q('Which is a good habit?',['Sharing','Bullying','Lying'],0)]),
 ('Grade 4','Mathematics','Multiplication','Multiplication is repeated addition: 3 × 4 = 3 + 3 + 3 + 3 = 12.', '✖️', [q('3 × 4 = ?',['7','12','14'],1)]),
 ('Grade 5','Science','The Solar System','Our solar system has the Sun and eight planets that orbit it.', '🪐', [q('How many planets orbit the Sun?',['7','8','9'],1)]),
 ('Grade 5','English','Adjectives','Adjectives describe nouns, such as bright, kind, or tall.', '✏️', [q('Which is an adjective?',['Blue','Jump','School'],0)])
]
