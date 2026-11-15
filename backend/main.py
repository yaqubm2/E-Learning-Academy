"""Role-scoped family API; local prototype, not a publicly deployable auth service."""
import hashlib
import hmac
import json
import re
import secrets
import sqlite3
import time
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field, field_validator
from . import store

# Server-memory sessions reset after backend restart. Use HTTPS and persistent
# session management, rate-limits, CSRF strategy etc. before public deployment.
SESSIONS = {}
SESSION_SECONDS = 8 * 3600

def hash_secret(secret):
    salt=secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac('sha256',secret.encode(),salt,260000)
    return f'{salt.hex()}:{digest.hex()}'

def verify_secret(secret, encoded):
    if not encoded: return False
    try:
        salt, digest = encoded.split(':')
        actual=hashlib.pbkdf2_hmac('sha256',secret.encode(),bytes.fromhex(salt),260000)
        return hmac.compare_digest(actual,bytes.fromhex(digest))
    except (ValueError,TypeError):
        return False

def issue_session(role, user_id):
    token=secrets.token_urlsafe(32)
    SESSIONS[token]=(role,user_id,time.time()+SESSION_SECONDS)
    return {'access_token':token,'role':role,'expires_in':SESSION_SECONDS}

def current_session(authorization: str|None=Header(default=None)):
    token=authorization.removeprefix('Bearer ').strip() if authorization else ''
    data=SESSIONS.get(token)
    if not data or data[2] < time.time():
        raise HTTPException(401,'Please log in')
    return data[:2]

def require_parent(session=Depends(current_session)):
    if session[0]!='parent': raise HTTPException(403,'Parent account required')
    return session[1]

def child_or_parent_access(student_id, session):
    role,uid=session
    with store.connection() as con:
        row=con.execute('SELECT parent_id FROM students WHERE id=?',(student_id,)).fetchone()
    if not row: raise HTTPException(404,'Child not found')
    if (role=='child' and uid!=student_id) or (role=='parent' and uid!=row['parent_id']):
        raise HTTPException(403,'Not authorized for this child')

@asynccontextmanager
async def lifespan(app:FastAPI):
    store.initialize()
    yield

app=FastAPI(title='E-Learning Academy API',version='0.2.0',lifespan=lifespan)

class ParentRegister(BaseModel):
    name:str=Field(min_length=2,max_length=70)
    email:str=Field(min_length=5,max_length=160)
    password:str=Field(min_length=10,max_length=128)
    @field_validator('email')
    @classmethod
    def valid_email(cls,v):
        v=v.strip().lower()
        if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',v): raise ValueError('Enter a valid email address')
        return v

class ParentLogin(BaseModel):
    email:str
    password:str

class ChildIn(BaseModel):
    name:str=Field(min_length=1,max_length=50)
    username:str=Field(min_length=3,max_length=30,pattern=r'^[A-Za-z0-9_]+$')
    pin:str=Field(min_length=4,max_length=8,pattern=r'^\d+$')
    grade:str
    avatar:str=Field(default='🌟',max_length=12)
    language:Literal['English','Urdu']='English'
    @field_validator('grade')
    @classmethod
    def validate_grade(cls,v):
        if v not in store.GRADES: raise ValueError('Unknown grade')
        return v
    @field_validator('name')
    @classmethod
    def trim(cls,v):
        if not v.strip(): raise ValueError('Name is required')
        return v.strip()

class ChildLogin(BaseModel):
    username:str
    pin:str

class ChildUpdate(BaseModel):
    name:str=Field(min_length=1,max_length=50)
    username:str=Field(min_length=3,max_length=30,pattern=r'^[A-Za-z0-9_]+$')
    pin:str|None=Field(default=None,min_length=4,max_length=8,pattern=r'^\d+$')
    grade:str
    avatar:str=Field(default='🌟',max_length=12)
    language:Literal['English','Urdu']='English'
    @field_validator('grade')
    @classmethod
    def validate_grade(cls,v):
        if v not in store.GRADES: raise ValueError('Unknown grade')
        return v

class Question(BaseModel):
    prompt:str=Field(min_length=1,max_length=350)
    choices:list[str]=Field(min_length=2,max_length=5)
    answer:int=Field(ge=0,le=4)
    @field_validator('choices')
    @classmethod
    def choices_nonblank(cls,v):
        if any(not x.strip() for x in v): raise ValueError('Answer choices cannot be empty')
        return v
    def model_post_init(self,_context):
        if self.answer>=len(self.choices): raise ValueError('Invalid correct answer')

class LessonIn(BaseModel):
    grade:str
    subject:str
    title:str=Field(min_length=1,max_length=100)
    explanation:str=Field(min_length=1,max_length=2500)
    emoji:str=Field(default='📚',max_length=12)
    questions:list[Question]=Field(min_length=1,max_length=30)
    @field_validator('grade')
    @classmethod
    def valid_grade(cls,v):
        if v not in store.GRADES: raise ValueError('Invalid grade')
        return v
    @field_validator('subject')
    @classmethod
    def valid_subject(cls,v):
        if v not in store.SUBJECTS: raise ValueError('Invalid subject')
        return v

class AttemptIn(BaseModel):
    lesson_id:int
    answers:list[int]=Field(min_length=1,max_length=30)

@app.get('/health')
def health(): return {'status':'ok'}

@app.get('/catalog')
def catalog(): return {'grades':store.GRADES,'subjects':store.SUBJECTS}

@app.post('/auth/parent/register',status_code=201)
def register_parent(data:ParentRegister):
    with store.connection() as con:
        try:
            first_parent=con.execute('SELECT COUNT(*) FROM parents').fetchone()[0]==0
            cur=con.execute('INSERT INTO parents(name,email,password_hash) VALUES (?,?,?)',
                            (data.name.strip(),data.email,hash_secret(data.password)))
            uid=cur.lastrowid
            # Existing v0.1 children become visible to first parent, but must
            # be given login usernames and PINs in the parent dashboard.
            if first_parent:
                con.execute('UPDATE students SET parent_id=? WHERE parent_id IS NULL',(uid,))
        except sqlite3.IntegrityError:
            raise HTTPException(409,'Email already registered')
    return issue_session('parent',uid)

@app.post('/auth/parent/login')
def login_parent(data:ParentLogin):
    with store.connection() as con:
        row=con.execute('SELECT id,password_hash FROM parents WHERE email=? COLLATE NOCASE',
                        (data.email.strip(),)).fetchone()
    if not row or not verify_secret(data.password,row['password_hash']):
        raise HTTPException(401,'Incorrect email or password')
    return issue_session('parent',row['id'])

@app.post('/auth/child/login')
def login_child(data:ChildLogin):
    with store.connection() as con:
        row=con.execute('SELECT id,pin_hash FROM students WHERE username=? COLLATE NOCASE',
                        (data.username.strip(),)).fetchone()
    if not row or not verify_secret(data.pin,row['pin_hash']):
        raise HTTPException(401,'Incorrect child username or PIN')
    return issue_session('child',row['id'])

@app.get('/auth/me')
def whoami(session=Depends(current_session)):
    role,uid=session
    with store.connection() as con:
        if role=='parent':
            row=con.execute('SELECT id,name,email FROM parents WHERE id=?',(uid,)).fetchone()
        else:
            row=con.execute('SELECT * FROM students WHERE id=?',(uid,)).fetchone()
    if not row: raise HTTPException(401,'Account no longer exists')
    return {'role':role,'account':dict(row) if role=='parent' else store.student_from_row(row)}

@app.post('/auth/logout')
def logout(authorization:str|None=Header(default=None)):
    token=authorization.removeprefix('Bearer ').strip() if authorization else ''
    SESSIONS.pop(token,None)
    return {'ok':True}

@app.get('/children')
def children(parent_id=Depends(require_parent)):
    with store.connection() as con:
        return [store.student_from_row(r) for r in con.execute('SELECT * FROM students WHERE parent_id=? ORDER BY id',(parent_id,))]

@app.post('/children',status_code=201)
def create_child(data:ChildIn,parent_id=Depends(require_parent)):
    with store.connection() as con:
        try:
            c=con.execute('''INSERT INTO students(name,username,pin_hash,grade,avatar,language,parent_id)
                VALUES(?,?,?,?,?,?,?)''',(data.name,data.username,hash_secret(data.pin),data.grade,
                                          data.avatar,data.language,parent_id))
        except sqlite3.IntegrityError:
            raise HTTPException(409,'Child username already taken')
    return {'id':c.lastrowid,**data.model_dump(exclude={'pin'})}

@app.put('/children/{child_id}')
def update_child(child_id:int,data:ChildUpdate,parent_id=Depends(require_parent)):
    with store.connection() as con:
        row=con.execute('SELECT parent_id FROM students WHERE id=?',(child_id,)).fetchone()
        if not row: raise HTTPException(404,'Child not found')
        if row['parent_id']!=parent_id: raise HTTPException(403,'Not your child account')
        try:
            con.execute('''UPDATE students SET name=?, username=?, grade=?, avatar=?, language=?,
                pin_hash=COALESCE(?,pin_hash) WHERE id=?''',(data.name.strip(),data.username,
                data.grade,data.avatar,data.language,hash_secret(data.pin) if data.pin else None,child_id))
        except sqlite3.IntegrityError:
            raise HTTPException(409,'Child username already taken')
    return {'id':child_id}

@app.get('/lessons')
def lessons(grade:str|None=None,subject:str|None=None,session=Depends(current_session)):
    where,params=[],[]
    if grade: where.append('grade=?'); params.append(grade)
    if subject: where.append('subject=?'); params.append(subject)
    sql='SELECT * FROM lessons'
    if where: sql+=' WHERE '+' AND '.join(where)
    with store.connection() as con:
        return [store.lesson_from_row(r) for r in con.execute(sql+' ORDER BY id',params)]

@app.get('/lessons/{lesson_id}')
def lesson(lesson_id:int,session=Depends(current_session)):
    with store.connection() as con:
        row=con.execute('SELECT * FROM lessons WHERE id=?',(lesson_id,)).fetchone()
    if not row: raise HTTPException(404,'Lesson not found')
    return store.lesson_from_row(row)

@app.post('/attempts',status_code=201)
def submit_attempt(data:AttemptIn,session=Depends(current_session)):
    if session[0]!='child': raise HTTPException(403,'Log in as a child to complete quizzes')
    student_id=session[1]
    with store.connection() as con:
        row=con.execute('SELECT * FROM lessons WHERE id=?',(data.lesson_id,)).fetchone()
        if not row: raise HTTPException(404,'Lesson not found')
        questions=store.lesson_from_row(row)['questions']
        if len(data.answers)!=len(questions): raise HTTPException(422,'Please answer all questions')
        if any(answer<0 or answer>=len(q['choices']) for answer,q in zip(data.answers,questions)):
            raise HTTPException(422,'Invalid choice')
        count=sum(answer==q['answer'] for answer,q in zip(data.answers,questions))
        con.execute('INSERT INTO attempts(student_id,lesson_id,correct,total) VALUES (?,?,?,?)',
                    (student_id,data.lesson_id,count,len(questions)))
    return {'correct':count,'total':len(questions),'stars':round(3*count/len(questions))}

@app.get('/progress/{student_id}')
def progress(student_id:int,session=Depends(current_session)):
    child_or_parent_access(student_id,session)
    with store.connection() as con:
        rows=con.execute('''SELECT l.id,l.title,l.subject,a.correct,a.total,a.created_at
               FROM attempts a JOIN lessons l ON l.id=a.lesson_id
               WHERE a.student_id=? ORDER BY a.id DESC''',(student_id,))
        attempts=[dict(r) for r in rows]
    return {'attempts':attempts,'completed_lessons':len(set(x['id'] for x in attempts)),
            'total_attempts':len(attempts),'total_stars':sum(round(3*x['correct']/x['total']) for x in attempts)}

@app.post('/lessons',status_code=201)
def create_lesson(data:LessonIn,parent_id=Depends(require_parent)):
    with store.connection() as con:
        c=con.execute('''INSERT INTO lessons(grade,subject,title,explanation,emoji,questions)
                VALUES(?,?,?,?,?,?)''',(data.grade,data.subject,data.title,data.explanation,data.emoji,
                                      json.dumps([q.model_dump() for q in data.questions],ensure_ascii=False)))
    return {'id':c.lastrowid}

@app.put('/lessons/{lesson_id}')
def edit_lesson(lesson_id:int,data:LessonIn,parent_id=Depends(require_parent)):
    with store.connection() as con:
        cur=con.execute('''UPDATE lessons SET grade=?,subject=?,title=?,explanation=?,emoji=?,questions=? WHERE id=?''',
                        (data.grade,data.subject,data.title,data.explanation,data.emoji,
                         json.dumps([q.model_dump() for q in data.questions],ensure_ascii=False),lesson_id))
        if not cur.rowcount: raise HTTPException(404,'Lesson not found')
    return {'id':lesson_id}

@app.delete('/lessons/{lesson_id}')
def delete_lesson(lesson_id:int,parent_id=Depends(require_parent)):
    with store.connection() as con:
        cur=con.execute('DELETE FROM lessons WHERE id=?',(lesson_id,))
        if not cur.rowcount: raise HTTPException(404,'Lesson not found')
    return {'deleted':True}
