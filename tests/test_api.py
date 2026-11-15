import os
os.environ['ACADEMY_DB'] = ':memory:' if False else '/tmp/academy_test_db.sqlite3'
os.environ['ACADEMY_PARENT_PIN'] = '9876'

import pytest
from fastapi.testclient import TestClient
from backend import store
from backend.main import app

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(store, 'DB_PATH', tmp_path/'test.sqlite3')
    with TestClient(app) as c:
        yield c

def test_catalog_and_seed_content(client):
    assert len(client.get('/catalog').json()['grades']) == 7
    assert len(client.get('/catalog').json()['subjects']) == 7
    assert len(client.get('/lessons').json()) >= 12

def test_student_quiz_and_progress(client):
    student = client.post('/students',json={'name':' Amina ','grade':'Grade 1','avatar':'🦋','language':'Urdu'})
    assert student.status_code == 201
    sid = student.json()['id']
    assert student.json()['name']=='Amina'
    lesson = client.get('/lessons?grade=Grade%201&subject=Mathematics').json()[0]
    answers=[q['answer'] for q in lesson['questions']]
    attempt=client.post('/attempts',json={'student_id':sid,'lesson_id':lesson['id'],'answers':answers})
    assert attempt.status_code == 201
    assert attempt.json()['correct']==len(answers)
    progress=client.get(f'/progress/{sid}').json()
    assert progress['completed_lessons']==1

def test_parent_can_create_and_edit_lesson(client):
    assert client.post('/lessons',json={}).status_code==401
    assert client.post('/parent/login',json={'pin':'bad'}).status_code==401
    token=client.post('/parent/login',json={'pin':'9876'}).json()['access_token']
    headers={'Authorization':'Bearer '+token}
    lesson={'grade':'Grade 5','subject':'Science','title':'New Discovery','explanation':'A new lesson.',
            'emoji':'🪐','questions':[{'prompt':'Question?','choices':['Yes','No'],'answer':0}]}
    created=client.post('/lessons',json=lesson,headers=headers)
    assert created.status_code==201
    lid=created.json()['id']
    lesson['title']='Edited Discovery'
    assert client.put(f'/lessons/{lid}',json=lesson,headers=headers).status_code==200
    assert client.get(f'/lessons/{lid}').json()['title']=='Edited Discovery'
    assert client.delete(f'/lessons/{lid}',headers=headers).status_code==200

def test_invalid_attempt_rejected(client):
    s=client.post('/students',json={'name':'H','grade':'Preschool'}).json()['id']
    l=client.get('/lessons?grade=Preschool').json()[0]
    assert client.post('/attempts',json={'student_id':s,'lesson_id':l['id'],'answers':[]}).status_code==422
    assert client.post('/students',json={'name':'','grade':'Preschool'}).status_code==422
