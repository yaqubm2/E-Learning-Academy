"""Family-mode API. Local development only: no production authentication or isolation."""
import os
import secrets
import time
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from . import store

PARENT_PIN = os.getenv('ACADEMY_PARENT_PIN', '2468')
ADMIN_TOKENS: dict[str,float] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    store.initialize()
    yield

app = FastAPI(title='E-Learning Academy API', version='0.1.0', lifespan=lifespan)
# No permissive CORS: the Flet client uses a Python HTTP client.

class StudentIn(BaseModel):
    name: str = Field(min_length=1,max_length=50)
    grade: str
    avatar: str = Field(default='🌟', max_length=12)
    language: Literal['English','Urdu'] = 'English'
    @field_validator('name')
    @classmethod
    def trim_name(cls,value):
        value = value.strip()
        if not value: raise ValueError('Name is required')
        return value
    @field_validator('grade')
    @classmethod
    def valid_grade(cls,value):
        if value not in store.GRADES: raise ValueError('Unknown grade')
        return value

class Question(BaseModel):
    prompt: str = Field(min_length=1,max_length=350)
    choices: list[str] = Field(min_length=2,max_length=5)
    answer: int = Field(ge=0,le=4)
    @field_validator('choices')
    @classmethod
    def no_blank_choices(cls,value):
        if any(not c.strip() for c in value): raise ValueError('Choices cannot be blank')
        return value
    def model_post_init(self, _context):
        if self.answer >= len(self.choices): raise ValueError('Answer index out of range')

class LessonIn(BaseModel):
    grade: str
    subject: str
    title: str = Field(min_length=1,max_length=100)
    explanation: str = Field(min_length=1,max_length=2500)
    emoji: str = Field(default='📚',max_length=12)
    questions: list[Question] = Field(min_length=1,max_length=20)
    @field_validator('grade')
    @classmethod
    def grade_valid(cls,value):
        if value not in store.GRADES: raise ValueError('Unknown grade')
        return value
    @field_validator('subject')
    @classmethod
    def subject_valid(cls,value):
        if value not in store.SUBJECTS: raise ValueError('Unknown subject')
        return value

class AttemptIn(BaseModel):
    student_id: int
    lesson_id: int
    answers: list[int] = Field(max_length=20)

class PinIn(BaseModel):
    pin: str


def parent_only(authorization: str|None = Header(default=None)):
    token = authorization.removeprefix('Bearer ').strip() if authorization else ''
    if not token or ADMIN_TOKENS.get(token,0) < time.time():
        raise HTTPException(401,'Parent login required')

@app.get('/health')
def health():
    return {'status':'ok'}

@app.get('/catalog')
def catalog():
    return {'grades':store.GRADES,'subjects':store.SUBJECTS}

@app.get('/students')
def students():
    with store.connection() as con:
        return [dict(r) for r in con.execute('SELECT * FROM students ORDER BY id DESC')]

@app.post('/students',status_code=201)
def create_student(payload:StudentIn):
    with store.connection() as con:
        cursor = con.execute('INSERT INTO students(name,grade,avatar,language) VALUES (?,?,?,?)',
                 (payload.name,payload.grade,payload.avatar,payload.language))
        return {'id':cursor.lastrowid, **payload.model_dump()}

@app.get('/lessons')
def lessons(grade:str|None=None,subject:str|None=None):
    where,params = [],[]
    if grade: where.append('grade=?'); params.append(grade)
    if subject: where.append('subject=?'); params.append(subject)
    sql = 'SELECT * FROM lessons'
    if where: sql += ' WHERE ' + ' AND '.join(where)
    sql += ' ORDER BY id'
    with store.connection() as con:
        return [store.lesson_from_row(r) for r in con.execute(sql,params)]

@app.get('/lessons/{lesson_id}')
def lesson(lesson_id:int):
    with store.connection() as con:
        r = con.execute('SELECT * FROM lessons WHERE id=?',(lesson_id,)).fetchone()
        if not r: raise HTTPException(404,'Lesson not found')
        return store.lesson_from_row(r)

@app.post('/attempts',status_code=201)
def submit_attempt(payload:AttemptIn):
    with store.connection() as con:
        if not con.execute('SELECT id FROM students WHERE id=?',(payload.student_id,)).fetchone():
            raise HTTPException(404,'Student not found')
        row = con.execute('SELECT * FROM lessons WHERE id=?',(payload.lesson_id,)).fetchone()
        if not row: raise HTTPException(404,'Lesson not found')
        qs = store.lesson_from_row(row)['questions']
        if len(payload.answers) != len(qs):
            raise HTTPException(422,'One answer required for each question')
        if any(a<0 or a>=len(q['choices']) for a,q in zip(payload.answers,qs)):
            raise HTTPException(422,'Invalid answer choice')
        correct = sum(a==q['answer'] for a,q in zip(payload.answers,qs))
        con.execute('INSERT INTO attempts(student_id,lesson_id,correct,total) VALUES (?,?,?,?)',
                (payload.student_id,payload.lesson_id,correct,len(qs)))
        return {'correct':correct,'total':len(qs),'stars':round(3*correct/len(qs))}

@app.get('/progress/{student_id}')
def progress(student_id:int):
    with store.connection() as con:
        if not con.execute('SELECT id FROM students WHERE id=?',(student_id,)).fetchone():
            raise HTTPException(404,'Student not found')
        rows=con.execute('''SELECT l.id,l.title,l.subject,a.correct,a.total,a.created_at FROM attempts a
                            JOIN lessons l ON l.id=a.lesson_id WHERE a.student_id=? ORDER BY a.id DESC''',(student_id,))
        attempts=[dict(r) for r in rows]
        return {'attempts':attempts,'completed_lessons':len(set(a['id'] for a in attempts)),
                'total_attempts':len(attempts)}

@app.post('/parent/login')
def login(payload:PinIn):
    if not secrets.compare_digest(payload.pin,PARENT_PIN):
        raise HTTPException(401,'Incorrect parent PIN')
    token=secrets.token_urlsafe(32)
    ADMIN_TOKENS[token]=time.time()+3600
    return {'access_token':token,'expires_in':3600}

@app.post('/lessons',status_code=201,dependencies=[Depends(parent_only)])
def create_lesson(payload:LessonIn):
    import json
    with store.connection() as con:
        c=con.execute('''INSERT INTO lessons(grade,subject,title,explanation,emoji,questions)
                    VALUES (?,?,?,?,?,?)''',(payload.grade,payload.subject,payload.title,payload.explanation,
                    payload.emoji,json.dumps([q.model_dump() for q in payload.questions],ensure_ascii=False)))
        return {'id':c.lastrowid}

@app.put('/lessons/{lesson_id}',dependencies=[Depends(parent_only)])
def edit_lesson(lesson_id:int,payload:LessonIn):
    import json
    with store.connection() as con:
        c=con.execute('''UPDATE lessons SET grade=?,subject=?,title=?,explanation=?,emoji=?,questions=? WHERE id=?''',
        (payload.grade,payload.subject,payload.title,payload.explanation,payload.emoji,
         json.dumps([q.model_dump() for q in payload.questions],ensure_ascii=False),lesson_id))
        if not c.rowcount: raise HTTPException(404,'Lesson not found')
        return {'id':lesson_id}

@app.delete('/lessons/{lesson_id}',dependencies=[Depends(parent_only)])
def delete_lesson(lesson_id:int):
    with store.connection() as con:
        c=con.execute('DELETE FROM lessons WHERE id=?',(lesson_id,))
        if not c.rowcount: raise HTTPException(404,'Lesson not found')
        return {'deleted':True}
